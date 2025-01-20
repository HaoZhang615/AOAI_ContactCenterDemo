from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey
from ..config import settings
from datetime import datetime
import uuid

class CosmosService:
    def __init__(self):
        self.client = CosmosClient(
            settings.COSMOSDB_ENDPOINT,
            settings.COSMOSDB_KEY
        )
        self.database = self.client.get_database_client(settings.COSMOSDB_DATABASE)
        self.container = self.database.get_container_client(settings.COSMOSDB_CONTAINER)

    async def save_conversation(self, user_id: str, conversation_id: str, message: str, response: str):
        try:
            await self.container.upsert_item({
                'id': conversation_id or str(uuid.uuid4()),
                'userId': user_id,
                'message': message,
                'response': response,
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            raise Exception(f"Error saving to CosmosDB: {str(e)}")

    async def get_conversation_history(self, user_id: str):
        query = f"SELECT * FROM c WHERE c.userId = '{user_id}' ORDER BY c.timestamp DESC"
        try:
            items = []
            async for item in self.container.query_items(query, enable_cross_partition_query=True):
                items.append(item)
            return items
        except Exception as e:
            raise Exception(f"Error fetching from CosmosDB: {str(e)}")
