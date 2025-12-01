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
            "Content-Type": "application/json",
           "HTTP-Referer": "http://localhost:8000",  # Required for OpenRouter
            "X-Title": "Sentiment Chatbot"  # Optional, for rankings
        }
        # Using meta-llama/llama-3.3-70b-instruct:free (verified working)
        self.model = "meta-llama/llama-3.3-70b-instruct:free"
    
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
        prompt = f"""You are a sentiment analysis expert. Analyze the sentiment of this text.

Text: "{text}"

Respond with ONLY this JSON format, no other text:
{{"sentiment": "positive", "score": 0.8, "explanation": "brief explanation"}}

Rules:
- sentiment: must be exactly "positive", "negative", or "neutral"
- score: number from 0.0 (very negative) to 1.0 (very positive), 0.5 is neutral
- explanation: one short sentence"""

        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self.chat(messages)
            
            # Try multiple JSON extraction methods
            import json
            import re
            
            # Method 1: Find JSON object in response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                try:
                    result = json.loads(json_str)
                    sentiment = result.get("sentiment", "neutral").lower()
                    # Ensure sentiment is valid
                    if sentiment not in ["positive", "negative", "neutral"]:
                        sentiment = "neutral"
                    
                    return {
                        "sentiment": sentiment,
                        "score": float(result.get("score", 0.5)),
                        "explanation": result.get("explanation", "")
                    }
                except json.JSONDecodeError:
                    pass
            
            # Method 2: Regex extraction as fallback
            sentiment_match = re.search(r'"sentiment"\s*:\s*"(\w+)"', response, re.IGNORECASE)
            score_match = re.search(r'"score"\s*:\s*([\d.]+)', response)
            
            sentiment = "neutral"
            score = 0.5
            
            if sentiment_match:
                sent = sentiment_match.group(1).lower()
                if sent in ["positive", "negative", "neutral"]:
                    sentiment = sent
            
            if score_match:
                try:
                    score = float(score_match.group(1))
                    score = max(0.0, min(1.0, score))  # Clamp between 0 and 1
                except ValueError:
                    score = 0.5
            
            # If no sentiment found, infer from score
            if sentiment == "neutral" and score != 0.5:
                if score > 0.6:
                    sentiment = "positive"
                elif score < 0.4:
                    sentiment = "negative"
            
            return {
                "sentiment": sentiment,
                "score": score,
                "explanation": "Analyzed from response"
            }
        
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            print(f"Response was: {response if 'response' in locals() else 'No response'}")
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
            f"{msg['role'].upper()}: {msg['content']}" 
            for msg in messages if msg['role'] == 'user'
        ])
        
        prompt = f"""You are a sentiment analysis expert. Analyze the OVERALL emotional tone of this conversation based on ALL user messages.

User messages:
{conversation_text}

Respond with ONLY this JSON format, no other text:
{{"sentiment": "positive", "score": 0.7, "summary": "brief overall summary"}}

Rules:
- sentiment: must be exactly "positive", "negative", or "neutral"
- score: 0.0 (very negative) to 1.0 (very positive), 0.5 is neutral
- summary: one sentence describing the emotional trajectory"""

        request_messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self.chat(request_messages)
            
            # Try multiple JSON extraction methods
            import json
            import re
            
            # Method 1: Direct JSON parsing
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                try:
                    result = json.loads(json_str)
                    sentiment = result.get("sentiment", "neutral").lower()
                    if sentiment not in ["positive", "negative", "neutral"]:
                        sentiment = "neutral"
                    
                    return {
                        "sentiment": sentiment,
                        "score": float(result.get("score", 0.5)),
                        "summary": result.get("summary", "Overall conversation analysis")
                    }
                except json.JSONDecodeError:
                    pass
            
            # Method 2: Regex extraction
            sentiment_match = re.search(r'"sentiment"\s*:\s*"(\w+)"', response, re.IGNORECASE)
            score_match = re.search(r'"score"\s*:\s*([\d.]+)', response)
            summary_match = re.search(r'"summary"\s*:\s*"([^"]+)"', response)
            
            sentiment = "neutral"
            score = 0.5
            summary = "Conversation analyzed"
            
            if sentiment_match:
                sent = sentiment_match.group(1).lower()
                if sent in ["positive", "negative", "neutral"]:
                    sentiment = sent
            
            if score_match:
                try:
                    score = float(score_match.group(1))
                    score = max(0.0, min(1.0, score))
                except ValueError:
                    pass
            
            if summary_match:
                summary = summary_match.group(1)
            
            # Infer sentiment from score if needed
            if sentiment == "neutral" and score != 0.5:
                if score > 0.6:
                    sentiment = "positive"
                elif score < 0.4:
                    sentiment = "negative"
            
            return {
                "sentiment": sentiment,
                "score": score,
                "summary": summary
            }
        
        except Exception as e:
            print(f"Error analyzing conversation sentiment: {e}")
            print(f"Response was: {response if 'response' in locals() else 'No response'}")
            return {"sentiment": "neutral", "score": 0.5, "summary": "Error in analysis"}
