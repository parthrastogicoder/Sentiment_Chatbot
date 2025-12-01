# Sentiment Chatbot

A conversational AI chatbot with real-time sentiment analysis capabilities, featuring both **statement-level** (Tier 2) and **conversation-level** (Tier 1) sentiment evaluation.

![Chatbot Demo](https://img.shields.io/badge/Status-Complete-success) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)

## 🚀 Features

### ✅ Tier 1 - Conversation-Level Sentiment Analysis (Mandatory)
- **Full conversation history tracking** in SQLite database
- **Overall sentiment analysis** performed on complete conversation
- Clear indication of **emotional direction** throughout the entire exchange
- Sentiment summary with score and explanation

### ✅ Tier 2 - Statement-Level Sentiment Analysis (Additional Credit)
- **Real-time sentiment evaluation** for every user message
- Individual sentiment displayed with each message (positive/negative/neutral)
- Sentiment score (0.0 to 1.0) for each statement
- Visual sentiment indicators in chat interface

## 📁 Project Structure

```
Liaplus_Assignment/
├── app.py                  # FastAPI application with REST endpoints
├── database.py             # SQLite database models and operations
├── openrouter_client.py    # OpenRouter API integration
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (gitignored)
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── README.md               # This file
└── static/
    ├── index.html          # Main web interface
    ├── style.css           # Styling with modern aesthetics
    └── app.js              # Frontend JavaScript logic
```

## 🛠️ Technologies Used

### Backend
- **FastAPI** - Modern, high-performance Python web framework
  - Auto-generated API documentation (Swagger UI)
  - Async support for better performance
  - Type hints with Pydantic models
  
- **SQLite** - Lightweight relational database
  - Two tables: `conversations` and `messages`
  - Stores sentiment data for both individual messages and overall conversations
  - No separate database server required

- **OpenRouter API** - LLM provider
  - Model: `meta-llama/llama-3.1-8b-instruct:free`
  - Handles both chat responses and sentiment analysis
  - Cost-effective with free tier access

### Frontend
- **Vanilla HTML/CSS/JavaScript** - No frameworks, minimal and fast
  - Modern gradient backgrounds and glassmorphism effects
  - Responsive design (mobile-friendly)
  - Smooth animations and transitions
  - Real-time sentiment visualization

## 🧠 Sentiment Analysis Logic

### Statement-Level Analysis (Tier 2)
Each user message is analyzed individually using the following approach:

1. **LLM-Based Analysis**: The message is sent to OpenRouter's LLM with a structured prompt
2. **JSON Response**: LLM returns sentiment classification, score, and explanation
3. **Classification**: 
   - `positive` - Score > 0.6
   - `negative` - Score < 0.4
   - `neutral` - Score between 0.4-0.6
4. **Storage**: Sentiment and score stored with each message in the database
5. **Display**: Shown immediately in the chat UI with color-coded badges

### Conversation-Level Analysis (Tier 1)
Overall conversation sentiment is calculated when user clicks "Analyze Conversation":

1. **Aggregate Analysis**: All user messages are sent together to the LLM
2. **Holistic Evaluation**: LLM considers:
   - Emotional trajectory throughout conversation
   - Dominant sentiment patterns
   - Context and progression of emotions
3. **Summary Generation**: LLM provides overall sentiment, score, and narrative summary
4. **Persistence**: Results saved to `conversations` table
5. **Display**: Shown in sentiment panel with detailed summary

### Why LLM-Based Sentiment Analysis?
- **Contextual Understanding**: Captures nuance, sarcasm, and complex emotions
- **Accuracy**: Better than simple keyword-based approaches
- **Consistency**: Same model for chat and sentiment ensures coherent analysis
- **Scalability**: OpenRouter handles the computational complexity

## ⚙️ How to Run

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/parthrastogicoder/Sentiment_Chatbot.git
cd Sentiment_Chatbot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your OpenRouter API key
# OPENROUTER_API_KEY=your_api_key_here
```

4. **Run the application**
```bash
uvicorn app:app --reload
```

5. **Open in browser**
```
http://localhost:8000
```

The application will automatically:
- Create the SQLite database (`chatbot.db`)
- Initialize the required tables
- Serve the web interface

### Alternative: Run on custom port
```bash
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

## 📡 API Endpoints

The FastAPI application provides the following REST endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve main HTML page |
| `/api/conversation/new` | POST | Create new conversation |
| `/api/chat` | POST | Send message, get response + sentiment |
| `/api/conversation/{id}` | GET | Get full conversation history |
| `/api/sentiment/{id}` | POST | Analyze overall conversation sentiment |

**Interactive API Documentation**: Visit `http://localhost:8000/docs` when running.

## 🎨 User Interface

### Chat Interface
- Clean, modern design with gradient backgrounds
- User messages on the left (purple gradient)
- Bot responses on the right (white background)
- Real-time sentiment badges on user messages

### Sentiment Panel
- **Current Message**: Shows sentiment of the last user message (Tier 2)
- **Overall Conversation**: Displays conversation-level analysis (Tier 1)
- **Analyze Button**: Triggers Tier 1 analysis on demand
- Color-coded sentiment badges:
  - 🟢 Green gradient - Positive
  - 🔴 Red gradient - Negative
  - ⚪ Gray gradient - Neutral

## ✅ Implementation Status

### Tier 1 - Conversation-Level Sentiment ✅ COMPLETE
- [x] Full conversation history maintained
- [x] Sentiment analysis for entire conversation
- [x] Clear emotional direction indication
- [x] Stored in database with summary

### Tier 2 - Statement-Level Sentiment ✅ COMPLETE
- [x] Individual message sentiment evaluation
- [x] Real-time sentiment display
- [x] Sentiment score for each message
- [x] Visual indicators in UI

## 🗄️ Database Schema

### conversations
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| created_at | TIMESTAMP | Creation time |
| overall_sentiment | TEXT | positive/negative/neutral |
| sentiment_score | REAL | 0.0 to 1.0 |

### messages
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| conversation_id | INTEGER | Foreign key to conversations |
| role | TEXT | 'user' or 'assistant' |
| content | TEXT | Message text |
| sentiment | TEXT | Statement-level sentiment (Tier 2) |
| sentiment_score | REAL | Statement-level score (Tier 2) |
| created_at | TIMESTAMP | Creation time |

## 🔐 Environment Variables

Create a `.env` file with:
```
OPENROUTER_API_KEY=your_api_key_here
```

**Security Note**: The `.env` file is gitignored to prevent accidental exposure of API keys.

## 🧪 Testing

### Manual Testing Steps
1. Start the application
2. Open browser to http://localhost:8000
3. Send multiple messages with varying sentiments
4. Observe real-time sentiment badges (Tier 2)
5. Click "Analyze Conversation" button
6. Verify overall sentiment matches conversation tone (Tier 1)
7. Start new conversation to test persistence

### Example Test Scenarios
- **Positive conversation**: "I'm so happy today!", "This is amazing!"
- **Negative conversation**: "I'm frustrated", "This is disappointing"
- **Mixed conversation**: Start negative, end positive
- **Neutral conversation**: "What time is it?", "Tell me about Python"

## 📝 Development Notes

### Design Decisions
- **FastAPI over Flask**: Better performance, async support, auto-docs
- **LLM-based sentiment**: More accurate than rule-based approaches
- **SQLite**: Simple, serverless, perfect for this use case
- **Minimal UI**: Focus on functionality over complexity

### Future Enhancements
- User authentication and multiple user support
- Export conversation history
- Advanced sentiment visualizations (charts/graphs)
- Multi-language support
- Fine-tuned sentiment model

## 📄 License

This project is provided as-is for educational purposes.

## 👤 Author

Parth Rastogi

## 🔗 Repository

https://github.com/parthrastogicoder/Sentiment_Chatbot

---

**Built with ❤️ for LiaPlus Assignment**
