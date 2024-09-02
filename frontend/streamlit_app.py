import papermill as pm
import streamlit as st
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize the session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login function
def login():
    if st.button("Log in"):
        st.session_state.logged_in = True
        st.rerun()

# Logout function
def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()

# Define pages
login_page = st.Page(login, title="Customer Contact Center Demo", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

self_service_page = st.Page("SelfServiceBot.py", title="Self Service Chatbot", icon="🧊")
ai_assisted_page = st.Page("AiAssistedBot.py", title="AI Assisted Chatbot", icon="🧊")

# Set the page configuration
st.set_page_config(page_title="Customer Contact Center Demo", page_icon="🧊", layout="wide")

# initiate the session state for all secrets
env_vars = {
    'AOAI_API_BASE': "AOAI_API_BASE",
    'AOAI_API_KEY': "AOAI_API_KEY",
    'AOAI_API_VERSION': "AOAI_API_VERSION",
    'AOAI_GPT4O_MINI_MODEL': "AOAI_GPT4O_MINI_MODEL",
    'AOAI_TTS_MODEL_NAME': "AOAI_TTS_MODEL_NAME",
    'AOAI_WHISPER_MODEL_NAME': "AOAI_WHISPER_MODEL_NAME",
    'BING_CUSTOM_SEARCH_API_ENDPOINT': "BING_CUSTOM_SEARCH_API_ENDPOINT",
    'BING_CUSTOM_SEARCH_API_KEY': "BING_CUSTOM_SEARCH_API_KEY",
    'BING_CUSTOM_CONFIG_ID': "BING_CUSTOM_CONFIG_ID",
    'BING_SEARCH_API_ENDPOINT': "BING_SEARCH_API_ENDPOINT",
    'BING_SEARCH_API_KEY': "BING_SEARCH_API_KEY",
    'COSMOS_ENDPOINT': "COSMOS_ENDPOINT",
    'COSMOS_KEY': "COSMOS_KEY",
    'COSMOS_DATABASE': "COSMOS_DATABASE"
}
for var, env in env_vars.items():
    if var not in st.session_state:
        st.session_state[var] = os.getenv(env)

# Show customer sign-in dropdown
if not st.session_state.logged_in:
    st.title("Azure OpenAI powered Contact Center")
    # get current customer profiles
    customer_folder_path = os.path.join(os.path.dirname(__file__), 'assets', 'Cosmos_Customer')
    customer_names = []
    customer_id_map = {}

    for file_name in os.listdir(customer_folder_path):
        if file_name.endswith('.json'):
            json_file_path = os.path.join(customer_folder_path, file_name)
            with open(json_file_path, 'r') as file:
                customer_data = json.load(file)
                # Construct the full name
                full_name = f"{customer_data['first_name']} {customer_data['last_name']}"
                customer_names.append(full_name)
                # Map the full name to the customer_id
                customer_id_map[full_name] = customer_data['customer_id']
    # Display the customer sign-in dropdown
    with st.container():
        st.markdown('<div class="fixed-dropdown">', unsafe_allow_html=True)
        Customer_Name = st.selectbox("Sign in as:", customer_names, index=0)
        st.markdown('</div>', unsafe_allow_html=True)
    # Assign customer_id based on the selected name
    st.session_state.customer_id = customer_id_map.get(Customer_Name)

    # Navigation based on login state
if st.session_state.logged_in:
    pg = st.navigation([self_service_page, ai_assisted_page])
else:
    pg = st.navigation([login_page])
pg.run()

if st.session_state.logged_in == False:

    # # Layout with one column for logo and radio buttons
    # col1, col2 = st.columns([5, 1])

    # with col1:
    #     # Mapping company names to logo filenames
    #     companies = ["Azure", "Dynamics", "GitHub", "LinkedIn", "Office", "Hardware"]
    #     logo_mapping = {
    #         "Azure": "Azure.png",
    #         "Dynamics": "Dynamics.png",
    #         "GitHub": "GitHub.png",
    #         "LinkedIn": "LinkedIn.png",
    #         "Office": "Office.png",
    #         "Hardware": "Hardware.png",
    #     }
    #     company = st.radio("Select a product:", companies, horizontal=True)

    # with col2:
    #     # Set a fixed height container for the logo
    #     logo_filename = logo_mapping.get(company)
    #     if logo_filename:
    #         # Get the current directory of the script
    #         base_dir = os.path.dirname(os.path.abspath(__file__))
    #         logo_path = os.path.join(base_dir, f"logos/{logo_filename}")
    #         # Display the image inside the fixed height container
    #         st.image(logo_path, width=300)

    products_folder_path = os.path.join(os.path.dirname(__file__), 'assets', 'Products_and_Urls_List')
    for file_name in os.listdir(products_folder_path):
        if file_name.endswith('.json'):
            json_file_path = os.path.join(products_folder_path, file_name)
            break
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    st.session_state.products = data['products']
    st.session_state.urls = data['urls']
    # set target_company variable to the first word of the filename separated by underscore and add it to the session state
    st.session_state.target_company = file_name.split('_')[0]

    # count number of files in the Cosmos_Customer folder, Cosmos_Product folder, Cosmos_Purchase folder, Cosmos_HumanConversations folder
    customer_folder_path = os.path.join(os.path.dirname(__file__), 'assets', 'Cosmos_Customer')
    customer_count = len([name for name in os.listdir(customer_folder_path) if name.endswith('.json')])
    product_folder_path = os.path.join(os.path.dirname(__file__), 'assets', 'Cosmos_Product')
    product_count = len([name for name in os.listdir(product_folder_path) if name.endswith('.json')])
    purchase_folder_path = os.path.join(os.path.dirname(__file__), 'assets', 'Cosmos_Purchases')
    purchase_count = len([name for name in os.listdir(purchase_folder_path) if name.endswith('.json')])
    human_conversation_folder_path = os.path.join(os.path.dirname(__file__), 'assets', 'Cosmos_HumanConversations')
    human_conversation_count = len([name for name in os.listdir(human_conversation_folder_path) if name.endswith('.json')])
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        st.write("The synthesized products are:")
        for product in st.session_state.products:
            st.markdown(f"- **{product}**",)
    with col2:
        st.write("The Bing Search is grounded by:")
        for url in st.session_state.urls:
            st.markdown(f"- **{url}**")
    with col3:
        st.write(f"Current Company for synthesization: **{st.session_state.target_company}**")
        st.write(f"Number of customers synthesized: **{customer_count}**")
        st.write(f"Number of products synthesized: **{product_count}**")
        st.write(f"Number of purchases synthesized: **{purchase_count}**")
        st.write(f"Number of human conversations synthesized: **{human_conversation_count}**")
        # add seperator line
        st.markdown("---")
        col4, col5 = st.columns([3, 1])
        with col4:
            st.write("Enter the new company name for synthesization:")
            st.write("")
            st.write("Enter the number of customers to synthesize:")
            st.write("")
            st.write("Enter the number of products to synthesize:")
            st.write("")
            st.write("Enter the number of human conversations to synthesize:")
        with col5:
            new_company = st.text_input("new company", key="new_company", label_visibility = "collapsed")  
            number_customer = st.text_input("number customer", key="number_customer", label_visibility = "collapsed")
            number_product = st.text_input("number product", key="number_product", label_visibility = "collapsed")
            number_human_conversation = st.text_input("number human conversation", key="number_human_conversation", label_visibility = "collapsed")
            # execute the synthesization process by clicking the button and call the notebook assets/scripts/SynthesizeEverything.ipynb
            notebook_path = os.path.join(os.path.dirname(__file__), 'assets', 'scripts', 'SynthesizeEverything.ipynb')
            output_path = os.path.join(os.path.dirname(__file__), 'assets', 'scripts', 'SynthesizeEverything_output.ipynb')
            if st.button("Synthesize"):
                params = {
                    # convert new_company to int
                    "company_name": new_company,
                    "number_of_customers": int(number_customer),
                    "number_of_product": int(number_product),
                    "number_of_human_conversations": int(number_human_conversation)
                }
                print(f"Parameters: {params}")
                pm.execute_notebook(        
                    notebook_path,  # Input notebook path
                    output_path,    # Output notebook path
                    parameters=params  # Parameters to pass to the notebook
                    )
