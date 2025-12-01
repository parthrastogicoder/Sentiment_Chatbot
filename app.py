from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn

from database import Database
from openrouter_client import OpenRouterClient

app = FastAPI(title="Sentiment Chatbot API")

# Initialize database and OpenRouter client
db = Database()
openrouter = OpenRouterClient()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models
class ChatRequest(BaseModel):
    conversation_id: int
    message: str

class ChatResponse(BaseModel):
    response: str
    sentiment: str
    sentiment_score: float
    explanation: str

class ConversationResponse(BaseModel):
    id: int
    messages: List[Dict]
    overall_sentiment: Optional[str] = None
    overall_score: Optional[float] = None

class SentimentAnalysisResponse(BaseModel):
    conversation_id: int
    overall_sentiment: str
    overall_score: float
    summary: str
    message_count: int

@app.get("/")
async def root():
    """Serve the main HTML page"""
    return FileResponse("static/index.html")

@app.post("/api/conversation/new")
async def create_conversation():
    """Create a new conversation"""
    conversation_id = db.create_conversation()
    return {"conversation_id": conversation_id}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message and get response with sentiment analysis (Tier 2)
    """
    # Get conversation history
    messages = db.get_conversation_messages(request.conversation_id)
    
    # Build message list for OpenRouter
    chat_messages = []
    for msg in messages:
        chat_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Add new user message
    chat_messages.append({
        "role": "user",
        "content": request.message
    })
    
    # Analyze sentiment of user message (Tier 2)
    sentiment_result = openrouter.analyze_sentiment(request.message)
    
    # Save user message with sentiment
    db.add_message(
        conversation_id=request.conversation_id,
        role="user",
        content=request.message,
        sentiment=sentiment_result["sentiment"],
        sentiment_score=sentiment_result["score"]
    )
    
    # Get chatbot response
    bot_response = openrouter.chat(chat_messages)
    
    # Save bot response (no sentiment for bot messages)
    db.add_message(
        conversation_id=request.conversation_id,
        role="assistant",
        content=bot_response
    )
    
    return ChatResponse(
        response=bot_response,
        sentiment=sentiment_result["sentiment"],
        sentiment_score=sentiment_result["score"],
        explanation=sentiment_result.get("explanation", "")
    )

@app.get("/api/conversation/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: int):
    """Get full conversation history"""
    conversation = db.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.get_conversation_messages(conversation_id)
    
    return ConversationResponse(
        id=conversation["id"],
        messages=messages,
        overall_sentiment=conversation["overall_sentiment"],
        overall_score=conversation["sentiment_score"]
    )

@app.post("/api/sentiment/{conversation_id}", response_model=SentimentAnalysisResponse)
async def analyze_conversation_sentiment(conversation_id: int):
    """
    Generate conversation-level sentiment analysis (Tier 1)
    """
    # Get all messages
    messages = db.get_conversation_messages(conversation_id)
    
    if not messages:
        raise HTTPException(status_code=404, detail="Conversation not found or empty")
    
    # Analyze overall conversation sentiment
    sentiment_result = openrouter.analyze_conversation_sentiment(messages)
    
    # Update conversation with overall sentiment
    db.update_conversation_sentiment(
        conversation_id=conversation_id,
        sentiment=sentiment_result["sentiment"],
        sentiment_score=sentiment_result["score"]
    )
    
    # Count user messages
    user_message_count = sum(1 for msg in messages if msg["role"] == "user")
    
    return SentimentAnalysisResponse(
        conversation_id=conversation_id,
        overall_sentiment=sentiment_result["sentiment"],
        overall_score=sentiment_result["score"],
        summary=sentiment_result.get("summary", ""),
        message_count=user_message_count
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
