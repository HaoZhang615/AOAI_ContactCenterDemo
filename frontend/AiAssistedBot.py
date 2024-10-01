import streamlit as st
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from openai import AzureOpenAI
import random
import json
import uuid
from datetime import datetime
from utils import create_cosmosdb_client

# Set the title of the app
st.title("AI Assisted Live Chat with Forwarded Customer Conversation")

# Azure Open AI Configuration
api_base = st.session_state.AOAI_API_BASE # your endpoint should look like the following https://YOUR_RESOURCE_NAME.openai.azure.com/
api_key = st.session_state.AOAI_API_KEY
api_version = st.session_state.AOAI_API_VERSION
gpt4o_mini = st.session_state.AOAI_GPT4O_MINI_MODEL

session_customer_id = st.session_state.customer_id

client = AzureOpenAI(
    api_key=api_key,  
    api_version=api_version,
    azure_endpoint = api_base,
)

# CosmosDB Configuration
cosmos_endpoint = st.session_state.COSMOS_ENDPOINT
cosmos_key = st.session_state.COSMOS_KEY
#cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)
cosmos_client = create_cosmosdb_client(use_cosmos_key=False)
database_name = st.session_state.COSMOS_DATABASE
database = cosmos_client.create_database_if_not_exists(id=database_name)  
customer_container_name = "Customer"
purchase_container_name = "Purchases"
ai_conversations_container_name = "AI_Conversations"
human_conversations_container_name = "Human_Conversations"
human_conversation_container = database.create_container_if_not_exists(  
    id=human_conversations_container_name,   
    partition_key=PartitionKey(path="/customer_id"),  
    offer_throughput=400  
) 

def get_customer_info(customer_id):
    # Get the database and container
    database = cosmos_client.get_database_client(database_name)
    container = database.get_container_client(customer_container_name)

    try:
        # Query the container for the customer information
        query = f"SELECT * FROM c WHERE c.customer_id = '{customer_id}'"
        items = list(container.query_items(query, enable_cross_partition_query=True))
        
        if items:
            return items[0]
        else:
            return None
    except exceptions.CosmosResourceNotFoundError:
        return None

def get_previous_purchases(customer_id):
    database = cosmos_client.get_database_client(database_name)
    container = database.get_container_client(purchase_container_name)

    try:
        query = f"SELECT * FROM c WHERE c.customer_id = '{customer_id}'"
        items = list(container.query_items(query, enable_cross_partition_query=True))
        return items
    except exceptions.CosmosResourceNotFoundError:
        return []
    
def display_customer_info(customer_info):
    if customer_info:
        left, right = st.columns(2)
        with left:
            st.write(f"**Customer ID:** {customer_info['customer_id']}")
            st.write(f"**Name:** {customer_info['first_name']} {customer_info['last_name']}")
            st.write(f"**Email:** {customer_info['email']}")
        with right:
            st.write(f"**Phone Number:** {customer_info['phone_number']}")
            st.write("**Address:**")
            st.write(f"{customer_info['address']['street']}, "
                     f"{customer_info['address']['city']}, "
                     f"{customer_info['address']['postal_code']}, "
                     f"{customer_info['address']['country']}")
    else:
        st.write("Customer information not found.")

def display_product_details(product_details):
    for key, value in product_details.items():
        st.write(f"**{key.replace('_', ' ').capitalize()}:** {value}")

def display_previous_purchases(purchases):
    if purchases:
        cols = st.columns(len(purchases))
        for idx, purchase in enumerate(purchases):
            with cols[idx]:
                st.write(f"**Order Number:** {purchase['order_number']}")
                st.write("**Product Details:**")
                display_product_details(purchase['product_details'])
                st.write(f"**Quantity:** {purchase['quantity']}")
                st.write(f"**Total Price:** ${purchase['total_price']:.2f}")
                st.write(f"**Purchase Date:** {purchase['purchasing_date']}")
                st.write(f"**Delivered Date:** {purchase['delivered_date']}")
                st.write("---")
    else:
        st.write("No previous purchases found.")

def get_prior_conversation(customer_id):
    client = CosmosClient(cosmos_endpoint, cosmos_key)
    database = client.get_database_client(database_name)
    container = database.get_container_client(ai_conversations_container_name)

    try:
        query = f"SELECT * FROM c WHERE c.customer_id = '{customer_id}' ORDER BY c._ts DESC"
        items = list(container.query_items(query, enable_cross_partition_query=True, max_item_count=1))
        if items:
            return items[0]
        else:
            return None
    except exceptions.CosmosResourceNotFoundError:
        return None

def summarize_conversation(messages):
    system_message = """
"You are a helpful customer service representative who is good at looking at a prior customer-agent conversation and 
provide a key-points based summary with the key-points being: 'Issue Reported', 'Already provided help', 'user expectation as next' and 'converstaion language'."""
    prompt = "Summarize the following conversation:\n\n"
    for message in messages:
        prompt += f"{message['role'].capitalize()}: {message['content']}\n"
    completion = client.chat.completions.create(
    model=gpt4o_mini,
    temperature=0.0,
    max_tokens=300,
    messages=[
        {
            "role": "system",
            "content": system_message,
        },
        {
            "role": "user",
            "content": prompt,
        }
    ],
)
    return completion.choices[0].message.content

def display_prior_conversation_summary(summary):
    st.write(f"{summary}")

def generate_recommended_reply(customer_id):
    system_message = """
You are a senior customer service agent who is good at giving next-turn reply to keep an engaging conversation and solving customer's problem. 
You got forwarded an existing customer service conversation done by another junior agent with extra provided context of customer information and previous purchases.
This is a live chat so do expect a quick response from the customer, do not reply like the customer is offline. You will initiate the conversation with the customer.
The existing conversation:\n\n"""
    prior_conversation = get_prior_conversation(customer_id)
    for message in prior_conversation['messages']:
        system_message += f"{message['role'].capitalize()}: {message['content']}\n"
    customer_info = get_customer_info(customer_id)
    customer_info_str = json.dumps(customer_info, indent=4)
    system_message += f"Customer Information:\n{customer_info_str}"
    previous_purchases = get_previous_purchases(customer_id)
    previous_purchases_str = json.dumps(previous_purchases, indent=4)
    system_message += f"Previous Purchases the customer made:\n{previous_purchases_str}"
    messages=[
        {
            "role": "system",
            "content": system_message,
        }
        ]
    if "new_messages" in st.session_state:
        messages.extend(st.session_state.new_messages)
    completion = client.chat.completions.create(
    model=gpt4o_mini,
    temperature=0.5,
    max_tokens=800,
    messages=messages,
)
    return completion.choices[0].message.content

def human_chat(customer_id):
    system_message = """you are in a role playing game simulating what a real-life human would say in a customer service conversation. 
            The user simulates what a friendly customer service agent would say and you will pretend to be a real-world grumpy user seeking for help. 
            You will finish the conversation within 3 turns, either happily accepting the provided help or leaving the conversation with a negative sentiment.
            """
    prior_conversation = get_prior_conversation(customer_id)
    for message in prior_conversation['messages']:
        system_message += f"{message['role'].capitalize()}: {message['content']}\n"
    customer_info = get_customer_info(customer_id)
    customer_info_str = json.dumps(customer_info, indent=4)
    system_message += f"Customer Information:\n{customer_info_str}"
    previous_purchases = get_previous_purchases(customer_id)
    previous_purchases_str = json.dumps(previous_purchases, indent=4)
    system_message += f"Previous Purchases the customer made:\n{previous_purchases_str}"
    messages=[
        {
            "role": "system",
            "content": system_message,
        }
        ]
    if "new_messages" in st.session_state:
        messages.extend(st.session_state.new_messages)
    completion = client.chat.completions.create(
    model=gpt4o_mini,
    temperature=0.5,
    max_tokens=800,
    messages=messages,
)
    return completion.choices[0].message.content

def save_chat(session_id, customer_id, messages):  
    document_id = f"chat_{session_id}"  # Create a document ID that is consistent throughout the session  
    container = human_conversation_container
    try:  
        # Attempt to read the existing document  
        item = container.read_item(item=document_id, partition_key=customer_id)
        item['messages'] = messages  # Update the messages  
        container.replace_item(item=item, body=item)  
    except exceptions.CosmosResourceNotFoundError:  
        # If the document does not exist, create a new one  
        container.create_item({  
            'id': document_id,  
            'session_id': session_id,  
            'customer_id': customer_id,
            'messages': messages  
        })

def analyse_chat_messages(messages):
    system_message = """
"You are a helpful customer service representative who is good at looking at customer-agent conversation about Nestle product and 
provide a entity recognition on the conversation's topic, the related product of the conversation and the sentiment of the conversation.
The available values for the entity recognition are:
sentiment = ['positive', 'negative', 'neutral', 'mixed', 'content', 'upset', 'angry', 'frustrated', 'happy', 'disappointed', 'confused']
topic = ['churn', 'assistance', 'support', 'information', 'billing', 'payment', 'account', 'service', 'delivery', 'damages', 'Quality', 'brand image', 'Nutrition information', 'Health Issues', 'Sustainability']
product = ['Nespresso Coffee Machine', 'Nespresso Coffee Capsule', 'Kitkat', 'Purina Pro Plan', 'Maggi Soy Sauce', 'Gerber Goodstart gentle pro']
Output a JSON object with the key "topic", "product" and "sentiment". """
    prompt = "analyse the following conversation:\n\n"
    for message in messages:
        prompt += f"{message['role'].capitalize()}: {message['content']}\n"
    completion = client.chat.completions.create(
    model=gpt4o_mini,
    temperature=0.0,
    max_tokens=300,
    messages=[
        {
            "role": "system",
            "content": system_message,
        },
        {
            "role": "user",
            "content": prompt,
        }
    ],
    response_format = { "type": "json_object" }
)
    return completion.choices[0].message.content
def persist_chat_messages(session_id, customer_id):
    # if the first message is from the assistant, update the data in Cosmos DB of the current session to swap the role of the user and the assistant . 
    # Then add the agent_id to the document.
    # finally, use Azure OpenAI to do entity recognition and sentiment analysis on the messages and save the results to Cosmos DB.
    container = human_conversation_container
    document_id = f"chat_{session_id}"
    item = container.read_item(item=document_id, partition_key=customer_id)
    # if the first message is from the assistant, iterate through messages and swap the role
    if item['messages'][0]['role'] == 'user':
        for message in item['messages']:
            if message['role'] == 'user':
                message['role'] = 'assistant'
            elif message['role'] == 'assistant':
                message['role'] = 'user'
    # Add agent_id to the document
    if 'agent_id' not in item:
        item['agent_id'] = random.randint(1, 9)
    # call the analyse_chat_messages function to get the entity recognition and sentiment analysis results
    analysis_results = json.loads(analyse_chat_messages(item['messages']))
    item['topic'] = analysis_results['topic']
    item['product'] = analysis_results['product']
    item['sentiment'] = analysis_results['sentiment']
    # Update the document with the modified messages
    container.replace_item(item=item, body=item)



# Initialize session state attributes  
if "new_messages" not in st.session_state:  
    st.session_state.new_messages = []  
    st.session_state.session_id = str(uuid.uuid4())  # Unique session ID  

# Define the layout with columns
left_col, right_col = st.columns([1, 1])

# Add components to the left column
with left_col:
    st.subheader("Customer Information")

    customer_info = get_customer_info(session_customer_id)
    display_customer_info(customer_info)

    st.subheader("Previous Purchases")
    purchases = get_previous_purchases(session_customer_id)
    display_previous_purchases(purchases)

    st.subheader("Recommended Reply")

    assisted_prompt = None
    # Add the button next to the "Recommended Reply" label
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write("")
    with col2:
        regenerate_button = st.button("Regenerate")
    with col3:
        submit_button = st.button("Submit Reply")

    recommended_reply = generate_recommended_reply(session_customer_id)

    if regenerate_button:
        recommended_reply = generate_recommended_reply(session_customer_id)

    recommended_reply_box = st.text_area(":sunglasses:", value = recommended_reply, height=300, label_visibility = "collapsed")


    # Save the content of the recommended reply to a variable when the button is clicked
    if submit_button:
        assisted_prompt = recommended_reply_box

# Add components to the right column
with right_col:
    st.subheader("Summary of Prior Conversation")
    conversation = get_prior_conversation(session_customer_id)
    if conversation:
        summary = summarize_conversation(conversation['messages'])
        display_prior_conversation_summary(summary)
    else:
        st.write("No prior conversation found.")

    st.subheader("Live Chat")
    # Function to save chat to Cosmos DB  

    # Generate a timestamp of 5 seconds fron now
    timestamp = datetime.now().timestamp() + 10

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write("")
    with col2:
        persist_button = st.button("Persist Chat")
    with col3:
        st.page_link(f"https://msit.powerbi.com/groups/me/reports/1fa677a4-784b-4450-a18a-5629a2296a9c/4ecaa42da7599db93aff?experience=power-bi", label="Post Call Analytics", icon="🌎")

    if persist_button:
        persist_chat_messages(st.session_state.session_id, session_customer_id)
  
    # create a container with fixed height and scroll bar for conversation history
    conversation_container = st.container(height = 600, border=False)
    # Handle new message  
    if text_prompt := st.chat_input("type your request here..."):
        prompt = text_prompt
    elif assisted_prompt:
        prompt = assisted_prompt
    else:
        prompt = None

    with conversation_container:
        if prompt:
            st.session_state.new_messages.append({"role": "user", "content": prompt})
            # Display the conversation history
            for message in st.session_state.new_messages:
                if message["role"] != "system":  
                    with st.chat_message(message["role"]):  
                        st.markdown(message["content"]) 
            with st.chat_message("assistant"):  
                result= human_chat(session_customer_id)
                st.markdown(result)
            st.session_state.new_messages.append({"role": "assistant", "content": result}) 
            save_chat(st.session_state.session_id, session_customer_id, st.session_state.new_messages)  # Save the session
            recommended_reply = generate_recommended_reply(session_customer_id)
        else:
            # Display the conversation history
            for message in st.session_state.new_messages:
                if message["role"] != "system":  
                    with st.chat_message(message["role"]):  
                        st.markdown(message["content"])

