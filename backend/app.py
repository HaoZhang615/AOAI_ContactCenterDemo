from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import chat, history

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(history.router)

@app.get("/")
async def root():
    return {"message": "Contact Center Demo API"}
