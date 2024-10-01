import os
from azure.cosmos import CosmosClient
from azure.identity import ClientSecretCredential
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_cosmosdb_client(use_cosmos_key):
    endpoint = os.getenv('COSMOS_ENDPOINT')
    cosmos_key = os.getenv('COSMOS_KEY')
    app_registration_info = {
        'tenant_id': os.getenv('AZURE_TENANT_ID'),
        'client_id': os.getenv('AZURE_CLIENT_ID'),
        'client_secret': os.getenv('AZURE_CLIENT_SECRET')
    }
    
    if use_cosmos_key:
        if not cosmos_key:
            raise ValueError("Cosmos DB key must be provided when use_cosmos_key is True")
        client = CosmosClient(endpoint, cosmos_key)
    else:
        if not app_registration_info:
            raise ValueError("App registration information must be provided when use_cosmos_key is False")
        
        tenant_id = app_registration_info.get('tenant_id')
        client_id = app_registration_info.get('client_id')
        client_secret = app_registration_info.get('client_secret')
        
        if not tenant_id or not client_id or not client_secret:
            raise ValueError("Tenant ID, Client ID, and Client Secret must be provided for app registration")
        
        credential = ClientSecretCredential(tenant_id, client_id, client_secret)
        client = CosmosClient(endpoint, credential)
    
    return client

def main():
    # Example usage
    use_cosmos_key = False  # Change this based on your authentication method

    try:
        client = create_cosmosdb_client(use_cosmos_key)
        print("Cosmos DB client created successfully.")
    except Exception as e:
        print(f"Failed to create Cosmos DB client: {e}")

if __name__ == "__main__":
    main()