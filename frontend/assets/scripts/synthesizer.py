import os
import json
import uuid
import random
import time
from openai import AzureOpenAI
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.identity import DefaultAzureCredential
from datetime import datetime

# Constants for synthesis
SENTIMENTS_LIST = ['positive', 'negative', 'neutral', 'mixed', 'content', 'upset', 'angry', 'frustrated', 'happy', 'disappointed', 'confused']
TOPICS_LIST = ['churn', 'assistance', 'support', 'information', 'billing', 'payment', 'account', 'service', 'Quality', 'Sustainability']
AGENT_LIST = ['adam','betrace','curie','davinci','emil', 'fred']
FIRST_NAME_LIST = ['Alex','Brian','Chloe','David','Emma','Fiona','George','Hannah','Ian','Julia','Kevin','Lucy','Michael',
    'Nicole','Oliver','Paula','Quinn','Rachel','Samuel','Tara','Ursula','Victor','Wendy','Xander','Yvonne','Zachary']
LAST_NAME_LIST = ["Anderson", "Brown", "Clark", "Davis", "Evans", "Foster", "Garcia", "Harris", "Ingram", "Johnson", "King", 
                  "Lewis", "Martin", "Nelson", "Owens", "Parker", "Quinn", "Robinson", "Smith", "Taylor", "Underwood", 
                  "Vargas", "Wilson", "Xavier", "Young", "Zimmerman"]

class DataSynthesizer:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.setup_azure_clients()
        self.setup_cosmos_containers()

    def setup_azure_clients(self):
        self.aoai_client = AzureOpenAI(
            api_key=os.getenv("AOAI_API_KEY"),
            api_version=os.getenv("AOAI_API_VERSION"),
            azure_endpoint=os.getenv("AOAI_API_BASE")
        )
        
        self.cosmos_client = CosmosClient(
            os.getenv("COSMOS_ENDPOINT"), 
            DefaultAzureCredential()
        )
        self.database = self.cosmos_client.get_database_client(os.getenv("COSMOS_DATABASE"))

    def setup_cosmos_containers(self):
        self.containers = {
            'customer': self.database.get_container_client("Customer"),
            'product': self.database.get_container_client("Product"),
            'purchases': self.database.get_container_client("Purchases"),
            'human_conversations': self.database.get_container_client("Human_Conversations")
        }

    def create_document(self, prompt, temperature=0.9, max_tokens=2000):
        response = self.aoai_client.chat.completions.create(
            model=os.getenv("AOAI_GPT4O_MINI_MODEL"),
            messages=[
                {"role": "system", "content": "You are a helpful assistant who helps people"},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content

    def save_json_files_to_cosmos_db(self, directory, container):
        for filename in os.listdir(directory):
            if not filename.endswith('.json'):
                continue
                
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            partition_key_path = container.read()['partitionKey']['paths'][0].strip('/')
            partition_key_value = data.get(partition_key_path)
            
            if partition_key_value:
                try:
                    container.upsert_item(body=data)
                    print(f"Document {filename} has been successfully created in Azure Cosmos DB!")
                except Exception as e:
                    print(f"Error uploading {filename}: {str(e)}")

    def synthesize_everything(self, company_name, num_customers, num_products, num_conversations):
        # Create required directories
        for dir_name in ['Cosmos_Customer', 'Cosmos_Product', 'Cosmos_Purchases', 'Cosmos_HumanConversations']:
            os.makedirs(os.path.join(self.base_dir, dir_name), exist_ok=True)

        # Generate and save product list
        products_data = self.create_product_and_url_list(company_name, num_products)
        products_dir = os.path.join(self.base_dir, 'Products_and_Urls_List')
        os.makedirs(products_dir, exist_ok=True)
        with open(os.path.join(products_dir, f'{company_name}_products_and_urls.json'), 'w', encoding='utf-8') as f:
            json.dump(products_data, f, ensure_ascii=False, indent=4)

        # Generate all data types
        self.synthesize_customer_profiles(num_customers)
        self.synthesize_product_profiles(company_name)
        self.synthesize_purchases()
        self.synthesize_human_conversations(num_conversations, company_name)

        # Upload all data to Cosmos DB
        for folder, container in [
            ('Cosmos_Customer', self.containers['customer']),
            ('Cosmos_Product', self.containers['product']),
            ('Cosmos_Purchases', self.containers['purchases']),
            ('Cosmos_HumanConversations', self.containers['human_conversations'])
        ]:
            self.save_json_files_to_cosmos_db(os.path.join(self.base_dir, folder), container)

    # Implementation of other methods (create_product_and_url_list, synthesize_customer_profiles, etc.)
    # Copy these methods from the notebook, adjusting them to use class attributes and methods
    # ...

def run_synthesis(company_name, num_customers, num_products, num_conversations):
    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
    synthesizer = DataSynthesizer(base_dir)
    synthesizer.synthesize_everything(company_name, num_customers, num_products, num_conversations)
