import os
import requests
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.model = "meta-llama/llama-3.1-8b-instruct:free"  # Free model
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Send chat messages and get response
        
        Args:
            messages: List of message dicts with 'role' and 'content'
        
        Returns:
            Assistant's response text
        """
        payload = {
            "model": self.model,
            "messages": messages
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
        
        except requests.exceptions.RequestException as e:
            print(f"Error calling OpenRouter API: {e}")
            return "I'm sorry, I encountered an error processing your request."
    
    def analyze_sentiment(self, text: str) -> Dict[str, any]:
        """
        Analyze sentiment of a single message
        
        Returns:
            Dict with 'sentiment' (positive/negative/neutral) and 'score' (0-1)
        """
        prompt = f"""Analyze the sentiment of the following text and respond ONLY with a JSON object in this exact format:
{{"sentiment": "positive/negative/neutral", "score": 0.0-1.0, "explanation": "brief explanation"}}

Text: "{text}"

Remember: 
- sentiment must be exactly one of: positive, negative, or neutral
- score is 0.0 (very negative) to 1.0 (very positive), with 0.5 being neutral
- Keep explanation brief (one sentence)"""

        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self.chat(messages)
            # Extract JSON from response
            import json
            # Try to find JSON in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                result = json.loads(json_str)
                return {
                    "sentiment": result.get("sentiment", "neutral"),
                    "score": float(result.get("score", 0.5)),
                    "explanation": result.get("explanation", "")
                }
            else:
                # Fallback
                return {"sentiment": "neutral", "score": 0.5, "explanation": "Could not parse sentiment"}
        
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {"sentiment": "neutral", "score": 0.5, "explanation": "Error in analysis"}
    
    def analyze_conversation_sentiment(self, messages: List[Dict]) -> Dict[str, any]:
        """
        Analyze sentiment of entire conversation
        
        Args:
            messages: List of message dicts with 'role' and 'content'
        
        Returns:
            Dict with overall 'sentiment' and 'score'
        """
        # Build conversation text
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in messages if msg['role'] == 'user'
        ])
        
        prompt = f"""Analyze the OVERALL sentiment of this entire conversation based on the user's messages. Consider the emotional trajectory throughout the conversation.

Respond ONLY with a JSON object in this exact format:
{{"sentiment": "positive/negative/neutral", "score": 0.0-1.0, "summary": "brief summary of emotional direction"}}

Conversation:
{conversation_text}

Remember:
- sentiment must be exactly one of: positive, negative, or neutral
- score is 0.0 (very negative) to 1.0 (very positive), with 0.5 being neutral
- summary should describe the overall emotional direction (one sentence)"""

        request_messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self.chat(request_messages)
            # Extract JSON from response
            import json
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                result = json.loads(json_str)
                return {
                    "sentiment": result.get("sentiment", "neutral"),
                    "score": float(result.get("score", 0.5)),
                    "summary": result.get("summary", "")
                }
            else:
                return {"sentiment": "neutral", "score": 0.5, "summary": "Could not parse sentiment"}
        
        except Exception as e:
            print(f"Error analyzing conversation sentiment: {e}")
            return {"sentiment": "neutral", "score": 0.5, "summary": "Error in analysis"}
