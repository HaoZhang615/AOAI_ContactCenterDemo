from openai import AzureOpenAI
import random
import time
import os
import json
import uuid
from azure.cosmos import CosmosClient, exceptions
from dotenv import load_dotenv
# load the environment variables
load_dotenv()

# configurations
api_base = os.getenv("AOAI_API_BASE") # your endpoint should look like the following https://YOUR_RESOURCE_NAME.openai.azure.com/
api_key = os.getenv("AOAI_API_KEY")
gpt4omini = os.getenv("GPT4o_MINI_MODEL_NAME")
api_version = "2024-02-01" # this might change in the future 2023-12-01-preview 2024-02-15-preview

client = AzureOpenAI(
    api_key=api_key,  
    api_version=api_version,
    azure_endpoint = api_base,
)

# function: generate random combination of sentiment, topic and product for AOAI to synthesize converstation content.
def randomized_prompt_elements(sentiments_list, topics_list, products_list, agend_list, customer_list):
    # Randomly draw an element from the supplied lists for the sentiment, topic, and product 
    random_sentiment = random.choice(sentiments_list)
    random_topic = random.choice(topics_list)
    random_product = random.choice(products_list)
    random_agent =random.choice(agend_list)
    random_customer = random.choice(customer_list)
    
    # Return the randomized element string 
    return random_sentiment, random_topic, random_product, random_agent, random_customer


def create_document(document_creation_prompt, temperature=0.7, max_tokens=2000):
    # Submit the answer from the QA Bot to the AOAI model for summariation
    messages=[
        {
            "role": "system",
            "content": "you are a helpful assistant who helps people",
        },
        {
            "role": "user",
            "content": document_creation_prompt,
        }
        ]
    openai_output = client.chat.completions.create(
      model=gpt4omini,
      messages=messages,
      temperature= temperature,
      max_tokens= max_tokens,
      response_format = { "type": "json_object" }
      )
    
    generated_document = openai_output.choices[0].message.content

    return openai_output,generated_document

# function: create dynamic document name based on the randomized combination of sentiment, topic and product. 
def create_document_name(i, random_sentiment, random_topic, random_product, total_tokens, completion_tokens):
    # Create a name for the document based on the randomly selected sentiment, topic, and product
    document_name = f'{i}_{total_tokens}_{completion_tokens}_{random_sentiment}_{random_topic}_{random_product}_document.json'
    return document_name

# Funtion: generate synthetic conversations between customer and agent for the Call Center Demo and save them as JSON files in the local folder synthesized_documents

def synthesize_conversations(number_of_files):
    # declare the 3 lists with allowed values
    sentiments_list = ['positive', 'negative', 'neutral', 'mixed', 'content', 'upset', 'angry', 'frustrated', 'happy', 'disappointed', 'confused']
    topics_list = ['churn', 'assistance', 'support', 'information', 'billing', 'payment', 'account', 'service', 'Quality', 'Sustainability']
    products_list = ['Xbox', 'LinkedIn', 'GitHub', 'Microsoft Office', 'Microsoft Dynamics', 'Microsoft Azure', 'Microsoft Surface']
    agent_list = ['adam','betrace','curie','davinci','emil', 'fred']
    customer_list = ['Alex','Brian','Chloe','David','Emma','Fiona','George','Hannah','Ian','Julia','Kevin','Lucy','Michael',
        'Nicole','Oliver','Paula','Quinn','Rachel','Samuel','Tara','Ursula','Victor','Wendy','Xander','Yvonne','Zachary']

    for i in range(number_of_files):# the range number decides how many files/synthetic conversations should be generated in a randomized manner. 
        # parameterized prompt generation
        random_sentiment, random_topic, random_product, random_agent, random_customer = randomized_prompt_elements(sentiments_list, topics_list, products_list, agent_list, customer_list)
        document_creation_prompt = f"""CREATE a JSON document with the key: "customer_id", "messages", "agent_id".
        The "messages" is JSON array containing multi-turn chat conversation representing an exchange between a customer service 
        agent for the company Microsoft and their customer. The sentiment of the customer must be {random_sentiment} and 
        the topic of the conversation betweem the agent and customer should center around {random_topic}. The customer must be asking about the product {random_product}.
        The agent handling this conversation is named {random_agent}. The name of the customer is {random_customer}. 
        At the beginning of the converstion, the agent thanks the customer for calling, tells the customer his/her name and asks what the name of the customer is.
        The document should have at least 5 back and forth exchanges between the customer and the agent and the length MUST NOT EXCEED 800 words.
        The "customer_id" should be a number between 1 and 26. The "agent_id" should be a number between 1 and 6. The customer_id and agent_id should be randomly assigned.
        Do not use markdown to format the json object.
        If you encounter double quotes in any text, use backslach escaping method to ensure the validaty of the JSON output. 
        Example below:
        {{
        "customer_id": 1,
        "messages": [
            {{
                "role": "assistant",
                "content": "Hi Jennifer, this is Alex from the customer service team. I see that your Essenza Mini coffee machine is giving you trouble. I can assist you further with this. Would you prefer to go through some troubleshooting steps together, or should I provide you with the contact details for our customer support to arrange a repair or replacement?"
            }},
            {{
                "role": "user",
                "content": "Look, I don't have time for troubleshooting steps. Just tell me how I can get this thing fixed or replaced."
            }},
            {{
                "role": "assistant",
                "content": "I understand, Jennifer. Since your Essenza Mini is still under the 2-year warranty, we can arrange a repair or replacement for you. I'll need to gather a few details to proceed. \n\nCould you please confirm the following:\n1. The serial number of your coffee machine.\n2. A brief description of the issue you're experiencing.\n\nOnce I have this information, I'll expedite the process for you."
            }},
            {{
                "role": "user",
                "content": "Fine, the serial number is 12345ABC. The machine won’t turn on at all, no matter what I do. Now, can we get this sorted quickly?"
            }},
            {{
                "role": "assistant",
                "content": "Thank you for providing the details, Jennifer. I'll get this sorted for you right away. \n\nI'll initiate the repair/replacement process and our customer support team will contact you shortly to arrange the next steps. You should receive an email with further instructions within the next 24 hours.\n\nIn the meantime, if there's anything else you need or any other questions you have, feel free to let me know. We're here to help!"
            }},
            {{
                "role": "user",
                "content": "Alright, I'll keep an eye out for that email. Just make sure it gets done quickly. Thanks."
            }},
            {{
                "role": "assistant",
                "content": "Absolutely, Jennifer. "
            }},
            {{
                "role": "user",
                "content": "Yeah, yeah. We'll see."
            }}
        ],
        "agent_id": 8}}
    """

        openai_output, generated_document = create_document(document_creation_prompt)

        total_tokens, completion_tokens = openai_output.usage.total_tokens, openai_output.usage.completion_tokens
        document_name = create_document_name(i, random_sentiment, random_topic, random_product, total_tokens, completion_tokens)

        # save the JSON document to the local folder synthesized_documents
        with open(f'synthesized_documents/{document_name}', 'w', encoding='utf-8') as f:
            f.write(generated_document)
        print(f"Document {document_name} has been successfully created!")
        time.sleep(5) # sleep for 5 second to avoid rate limiting

def analyse_chat_messages(messages):
    system_message = """
"You are a helpful customer service representative who is good at looking at customer-agent conversation about Microsoft product and 
provide a entity recognition on the conversation's topic, the related product of the conversation and the sentiment of the conversation. 
Output a JSON object with the key "topic", "product" and "sentiment". """
    prompt = "analyse the following conversation:\n\n"
    for message in messages:
        prompt += f"{message['role'].capitalize()}: {message['content']}\n"
    completion = client.chat.completions.create(
    model=gpt4omini,
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

# add a extra key "session_id" to each JSON file using the uuid.uuid4() function
def add_additional_keys_to_json_files():
    # get the list of all files in the folder synthesized_documents
    files = os.listdir('synthesized_documents')
    for file in files:
        with open(f'synthesized_documents/{file}', 'r', encoding='utf-8') as f:
            item = json.load(f)
            item["session_id"] = str(uuid.uuid4())
            # call the analyse_chat_messages function to get the entity recognition and sentiment analysis results
            # analysis_results = json.loads(analyse_chat_messages(item['messages']))
            # item['topic'] = analysis_results['topic']
            # item['product'] = analysis_results['product']
            # item['sentiment'] = analysis_results['sentiment']
        with open(f'synthesized_documents/{file}', 'w', encoding='utf-8') as f:
            json.dump(item, f, indent=4)
        time.sleep(2) # sleep for 5 second to avoid rate limiting
    print("Session ID has been successfully added to all JSON files!")
# function to save the JSON files to Azure Cosmos DB

# Azure Cosmos DB connection details
cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
cosmos_key = os.getenv("COSMOS_KEY")
cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)
database_name = os.getenv("COSMOS_DATABASE")
database = cosmos_client.create_database_if_not_exists(id=database_name)
customer_container_name = "Customer"
purchase_container_name = "Purchases"
ai_conversations_container_name = "AI_Conversations"
human_conversations_container_name = "Human_Conversations"

def save_json_files_to_cosmos_db():
    container = database.get_container_client(human_conversations_container_name)
    # get the list of all files in the folder synthesized_documents
    files = os.listdir('synthesized_documents')
    for file in files:
        with open(f'synthesized_documents/{file}', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # add a document_id field to the JSON file as f"chat_{session_id}"
            data["id"] = f"chat_{data['session_id']}"
            # save the JSON file to Azure Cosmos DB
            try:
                container.create_item(body=data)
            except exceptions.CosmosHttpResponseError as e:
                print(f"An error occurred: {e}")
            print(f"Document {file} has been successfully saved to Azure Cosmos DB!")

# Function to update the JSON files based on the file name: example: chat_1_800_800_positive_churn_Nespresso Coffee Machine_document.json
# update the "sentiment" key to "positive", "topic" key to "churn" and "product" key to "Nespresso Coffee Machine"
def update_JSON_files():
    # get the list of all files in the folder synthesized_documents
    files = os.listdir('synthesized_documents')
    for file in files:
        with open(f'synthesized_documents/{file}', 'r', encoding='utf-8') as f:
            item = json.load(f)
            # get the sentiment, topic and product from the file name
            sentiment, topic, product = file.split('_')[3], file.split('_')[4], file.split('_')[5]
            item['sentiment'] = sentiment
            item['topic'] = topic
            item['product'] = product
        with open(f'synthesized_documents/{file}', 'w', encoding='utf-8') as f:
            json.dump(item, f, indent=4)

    print("Sentiment, topic and product have been successfully updated in all JSON files!")




synthesize_conversations(51)
add_additional_keys_to_json_files()
update_JSON_files()
save_json_files_to_cosmos_db()

