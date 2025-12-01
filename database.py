import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json

class Database:
    def __init__(self, db_path: str = "chatbot.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                overall_sentiment TEXT,
                sentiment_score REAL
            )
        """)
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                sentiment TEXT,
                sentiment_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_conversation(self) -> int:
        """Create a new conversation and return its ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO conversations DEFAULT VALUES")
        conversation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return conversation_id
    
    def add_message(self, conversation_id: int, role: str, content: str, 
                    sentiment: Optional[str] = None, sentiment_score: Optional[float] = None):
        """Add a message to a conversation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (conversation_id, role, content, sentiment, sentiment_score)
            VALUES (?, ?, ?, ?, ?)
        """, (conversation_id, role, content, sentiment, sentiment_score))
        conn.commit()
        conn.close()
    
    def get_conversation_messages(self, conversation_id: int) -> List[Dict]:
        """Get all messages in a conversation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, role, content, sentiment, sentiment_score, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
        """, (conversation_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "id": row["id"],
                "role": row["role"],
                "content": row["content"],
                "sentiment": row["sentiment"],
                "sentiment_score": row["sentiment_score"],
                "created_at": row["created_at"]
            })
        
        conn.close()
        return messages
    
    def update_conversation_sentiment(self, conversation_id: int, 
                                     sentiment: str, sentiment_score: float):
        """Update overall conversation sentiment"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE conversations
            SET overall_sentiment = ?, sentiment_score = ?
            WHERE id = ?
        """, (sentiment, sentiment_score, conversation_id))
        conn.commit()
        conn.close()
    
    def get_conversation(self, conversation_id: int) -> Optional[Dict]:
        """Get conversation details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, created_at, overall_sentiment, sentiment_score
            FROM conversations
            WHERE id = ?
        """, (conversation_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row["id"],
                "created_at": row["created_at"],
                "overall_sentiment": row["overall_sentiment"],
                "sentiment_score": row["sentiment_score"]
            }
        return None
