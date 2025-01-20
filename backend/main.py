from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import asyncio
from openai import AsyncAzureOpenAI
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Request body model
class ChatInput(BaseModel):
    content: str  
class ChatResponse(BaseModel):
    content: str


# Replace with your Azure OpenAI endpoint and key
AZURE_OPENAI_ENDPOINT = os.getenv("AOAI_API_BASE")
AZURE_OPENAI_KEY = os.getenv("AOAI_API_KEY")
GPT_4O_MINI = os.getenv("AOAI_GPT4O_MINI_MODEL")
API_VERSION = os.getenv("AOAI_API_VERSION")

# Initialize AsyncAzureOpenAI client
async def get_openai_client():
    return AsyncAzureOpenAI(
        api_key=AZURE_OPENAI_KEY,
        api_version=API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(user_input: ChatInput):
    """
    Endpoint to interact with Azure OpenAI GPT model.
    """
    system_message = f"""You are a helpful assistant."""
    messages=[{"role": "system", "content": system_message}]
    messages.append({"role": "user", "content": user_input.content})
    try:
        client = await get_openai_client()
        response = await client.chat.completions.create(
            model=GPT_4O_MINI,  # Replace with your model deployment name
            messages=messages
        )

        # Extract and return the assistant's reply
        assistant_reply = response.choices[0].message.content
        return ChatResponse(content=assistant_reply)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the app with your preferred ASGI server (e.g., uvicorn)
# Example: `uvicorn main:app --reload`
