// Global state
let currentConversationId = null;

// DOM elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const newConversationBtn = document.getElementById('newConversationBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const currentSentiment = document.getElementById('currentSentiment');
const overallSentiment = document.getElementById('overallSentiment');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    createNewConversation();

    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    newConversationBtn.addEventListener('click', createNewConversation);
    analyzeBtn.addEventListener('click', analyzeConversation);
});

// Create new conversation
async function createNewConversation() {
    try {
        const response = await fetch('/api/conversation/new', {
            method: 'POST'
        });
        const data = await response.json();
        currentConversationId = data.conversation_id;

        // Clear chat
        chatMessages.innerHTML = '';

        // Reset sentiment displays
        updateCurrentSentiment('neutral', 0.5, 'Send a message to see sentiment');
        updateOverallSentiment('neutral', null, 'Click "Analyze Conversation" below');

        addSystemMessage('New conversation started! How are you feeling today?');
    } catch (error) {
        console.error('Error creating conversation:', error);
        alert('Failed to create new conversation');
    }
}

// Send message
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || !currentConversationId) return;

    // Disable input
    messageInput.disabled = true;
    sendBtn.disabled = true;

    // Add user message to UI
    addMessage('user', message);
    messageInput.value = '';

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                conversation_id: currentConversationId,
                message: message
            })
        });

        const data = await response.json();

        // Update current sentiment (Tier 2)
        updateCurrentSentiment(
            data.sentiment,
            data.sentiment_score,
            data.explanation
        );

        // Update user message with sentiment
        updateMessageSentiment(data.sentiment, data.sentiment_score);

        // Add bot response
        addMessage('assistant', data.response);

    } catch (error) {
        console.error('Error sending message:', error);
        addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
    } finally {
        // Re-enable input
        messageInput.disabled = false;
        sendBtn.disabled = false;
        messageInput.focus();
    }
}

// Analyze conversation sentiment (Tier 1)
async function analyzeConversation() {
    if (!currentConversationId) return;

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = 'Analyzing...';

    try {
        const response = await fetch(`/api/sentiment/${currentConversationId}`, {
            method: 'POST'
        });

        const data = await response.json();

        // Update overall sentiment display
        updateOverallSentiment(
            data.overall_sentiment,
            data.overall_score,
            data.summary
        );

        addSystemMessage(`Conversation analyzed! Overall sentiment: ${data.overall_sentiment.toUpperCase()} (${data.message_count} messages)`);

    } catch (error) {
        console.error('Error analyzing conversation:', error);
        alert('Failed to analyze conversation');
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = 'Analyze Conversation';
    }
}

// UI helper functions
function addMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const headerDiv = document.createElement('div');
    headerDiv.className = 'message-header';

    const roleSpan = document.createElement('span');
    roleSpan.className = 'message-role';
    roleSpan.textContent = role === 'user' ? '👤 You' : '🤖 Bot';
    headerDiv.appendChild(roleSpan);

    // Add sentiment indicator for user messages (will be updated)
    if (role === 'user') {
        const sentimentSpan = document.createElement('span');
        sentimentSpan.className = 'message-sentiment neutral';
        sentimentSpan.id = 'latest-sentiment';
        headerDiv.appendChild(sentimentSpan);
    }

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;

    messageDiv.appendChild(headerDiv);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addSystemMessage(content) {
    const messageDiv = document.createElement('div');
    messageDiv.style.textAlign = 'center';
    messageDiv.style.padding = '10px';
    messageDiv.style.color = '#666';
    messageDiv.style.fontSize = '13px';
    messageDiv.style.fontStyle = 'italic';
    messageDiv.textContent = content;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function updateMessageSentiment(sentiment, score) {
    const latestSentiment = document.getElementById('latest-sentiment');
    if (latestSentiment) {
        latestSentiment.className = `message-sentiment ${sentiment}`;
        latestSentiment.textContent = `${sentiment} (${score.toFixed(2)})`;
        latestSentiment.id = ''; // Remove ID so next message gets it
    }
}

function updateCurrentSentiment(sentiment, score, explanation) {
    currentSentiment.innerHTML = `
        <div class="sentiment-badge ${sentiment}">${sentiment.charAt(0).toUpperCase() + sentiment.slice(1)}</div>
        <div class="sentiment-score">Score: ${score !== null ? score.toFixed(2) : '-'}</div>
        <div class="sentiment-explanation">${explanation}</div>
    `;
}

function updateOverallSentiment(sentiment, score, summary) {
    const displaySentiment = score === null ? 'Not analyzed' : sentiment.charAt(0).toUpperCase() + sentiment.slice(1);
    overallSentiment.innerHTML = `
        <div class="sentiment-badge ${sentiment}">${displaySentiment}</div>
        <div class="sentiment-score">Score: ${score !== null ? score.toFixed(2) : '-'}</div>
        <div class="sentiment-explanation">${summary}</div>
    `;
}
