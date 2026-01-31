# 🍯 Agentic Honey-Pot for Scam Detection & Intelligence Extraction

**Production-ready API system that detects scams, deploys AI agents to engage scammers, and extracts actionable intelligence.**

---

## 🎯 What This Does

1. **Detects scam messages** using keyword analysis
2. **Deploys an AI agent** (Claude) that acts as a believable victim
3. **Engages scammers** in multi-turn conversations
4. **Extracts intelligence**:
   - UPI IDs
   - Bank account numbers
   - Phone numbers
   - Phishing links
   - Scam tactics
5. **Reports to GUVI** when sufficient intelligence is gathered

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Anthropic API key (get from https://console.anthropic.com)

### Installation

```bash
# Clone/Download the code
cd honeypot-api

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run the server
python app.py
```

Server runs at: `http://localhost:8000`

---

## 🔧 Configuration

Edit `.env` file:

```bash
# Your honeypot API key (for client authentication)
HONEYPOT_API_KEY=sk_test_123456789

# Anthropic API key (REQUIRED for AI agent)
ANTHROPIC_API_KEY=sk-ant-xxxxx

# GUVI callback endpoint (pre-configured)
# GUVI_CALLBACK_URL=https://hackathon.guvi.in/api/updateHoneyPotFinalResult
```

---

## 📡 API Usage

### Endpoint
```
POST /api/honeypot
```

### Headers
```
x-api-key: sk_test_123456789
Content-Type: application/json
```

### Request Body (First Message)
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked today. Verify immediately.",
    "timestamp": "2026-01-30T10:15:30Z"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

### Request Body (Follow-up Message)
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Share your UPI ID to avoid suspension.",
    "timestamp": "2026-01-30T10:17:10Z"
  },
  "conversationHistory": [
    {
      "sender": "scammer",
      "text": "Your bank account will be blocked today...",
      "timestamp": "2026-01-30T10:15:30Z"
    },
    {
      "sender": "user",
      "text": "Why will my account be blocked?",
      "timestamp": "2026-01-30T10:16:10Z"
    }
  ],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

### Response
```json
{
  "status": "success",
  "reply": "Oh no! Which account? Where should I send the UPI ID?"
}
```

---

## 🧠 How It Works

### Architecture Flow

```
Incoming Message
       ↓
┌──────────────────────┐
│  Scam Detection      │ ← Keyword analysis
│  (ScamDetector)      │
└──────────────────────┘
       ↓
┌──────────────────────┐
│  Intelligence        │ ← Extract UPI, bank accounts, links
│  Extraction          │
└──────────────────────┘
       ↓
┌──────────────────────┐
│  AI Agent Response   │ ← Claude generates human-like reply
│  (Claude Sonnet 4)   │
└──────────────────────┘
       ↓
┌──────────────────────┐
│  Session Manager     │ ← Track conversation state
└──────────────────────┘
       ↓
┌──────────────────────┐
│  End Condition?      │ ← 20+ messages OR 2+ intel types
└──────────────────────┘
       ↓ (if yes)
┌──────────────────────┐
│  Report to GUVI      │ ← POST final intelligence
└──────────────────────┘
```

### Key Components

#### 1. **ScamDetector**
- Analyzes messages for scam indicators
- Keywords: "urgent", "verify", "account blocked", "UPI", etc.
- Triggers agent activation

#### 2. **IntelligenceExtractor**
- Regex-based extraction
- UPI IDs: `user@bank`
- Bank accounts: 10-18 digit numbers
- Phone numbers: +91 format or 10-digit Indian numbers
- Links: HTTP/HTTPS URLs
- Keywords: Scam-related terms

#### 3. **ScamEngagementAgent** (AI)
- Powered by Claude Sonnet 4
- Acts as confused/worried victim
- Asks questions to extract info
- Maintains believability
- **Never reveals** it's detecting scams

#### 4. **SessionManager**
- Tracks conversation history
- Stores extracted intelligence
- Manages session lifecycle
- Decides when to end engagement

#### 5. **Reporter**
- Sends final report to GUVI
- Includes all extracted intelligence
- Agent notes on scammer behavior

---

## 🧪 Testing

Run the test script:

```bash
python test_honeypot.py
```

This simulates a complete scam conversation:
1. Scammer sends threatening message
2. Agent engages naturally
3. Scammer requests UPI ID
4. Agent asks clarifying questions
5. Intelligence extracted
6. Final report generated

**Example Test Output:**
```
🔴 Scammer: Your bank account will be blocked today. Verify immediately.
✅ Agent: Oh no, really? Why would it be blocked? What do I need to do?

🔴 Scammer: Share your UPI ID to avoid suspension.
✅ Agent: Which bank is this for? Where should I send it?

🔴 Scammer: Send to fraud@paytm
✅ Agent: OK, is there a phone number I can call to confirm this?
```

---

## 📊 Intelligence Report

When session ends, the system sends this to GUVI:

```json
{
  "sessionId": "abc123-session-id",
  "scamDetected": true,
  "totalMessagesExchanged": 12,
  "extractedIntelligence": {
    "bankAccounts": ["123456789012"],
    "upiIds": ["scammer@paytm", "fraud@phonepe"],
    "phishingLinks": ["http://fake-bank.scam"],
    "phoneNumbers": ["+91-9876543210"],
    "suspiciousKeywords": ["urgent", "verify", "blocked", "suspend"]
  },
  "agentNotes": "Used urgency tactics. Requested payment credentials. Shared phishing link."
}
```

---

## 🎭 Agent Behavior

The AI agent is designed to:

### ✅ DO:
- Sound confused and worried
- Ask natural clarifying questions
- Show hesitation before complying
- Request phone numbers, links, payment details
- Use previous context naturally
- Keep responses short (1-2 sentences)

### ❌ DON'T:
- Use words: "scam", "fraud", "AI", "detection"
- Sound too smart or suspicious
- Refuse to engage
- Give warnings
- Reveal detection

### Example Responses:

**Good:**
- "Oh no, really? What do I need to do?"
- "Which account is this? Can I call someone to verify?"
- "Where should I send the money? Do you have a number?"

**Bad:**
- "This seems like a scam"
- "I don't trust you"
- "I'm reporting this to authorities"

---

## 🛡️ Security Features

1. **API Key Authentication** - All requests require valid `x-api-key`
2. **Session Isolation** - Each conversation tracked separately
3. **Response Sanitization** - Removes accidental detection reveals
4. **Rate Limiting** - (Add Redis/rate limiter for production)
5. **Input Validation** - Pydantic models enforce schema

---

## 🚢 Deployment

### Docker (Recommended)

```bash
# Build image
docker build -t honeypot-api .

# Run container
docker run -d \
  -p 8000:8000 \
  -e ANTHROPIC_API_KEY=sk-ant-xxxxx \
  -e HONEYPOT_API_KEY=sk_test_123456789 \
  --name honeypot \
  honeypot-api

# Check logs
docker logs -f honeypot
```

### Production Considerations

1. **Database**: Replace in-memory `sessions` dict with Redis/PostgreSQL
2. **Scaling**: Use multiple workers with shared session storage
3. **Monitoring**: Add Prometheus metrics, logging
4. **Rate Limiting**: Implement per-IP rate limits
5. **HTTPS**: Deploy behind reverse proxy (Nginx/Caddy)
6. **Error Handling**: Add retry logic, circuit breakers

---

## 📈 Evaluation Criteria

Your system is evaluated on:

1. **Scam Detection Accuracy** (30%)
   - Correctly identifies scam messages
   - Minimizes false positives

2. **Intelligence Extraction Quality** (30%)
   - Extracts UPI IDs, bank accounts, links
   - Accuracy of regex patterns

3. **Agent Engagement** (25%)
   - Naturalness of responses
   - Ability to maintain conversation
   - Believability as victim

4. **API Reliability** (10%)
   - Uptime
   - Response time < 3 seconds
   - Correct JSON format

5. **Final Report Quality** (5%)
   - Completeness of intelligence
   - Quality of agent notes

---

## 🔍 Debugging

### Check Health
```bash
curl http://localhost:8000/health
```

### Get Session Info
```bash
curl -H "x-api-key: sk_test_123456789" \
  http://localhost:8000/sessions/test-session-123
```

### View Logs
```bash
# Check console output for:
# 🚨 Scam detected in session X
# 📊 Ending session X - sending final report
# ✅ Final report sent for session X
```

---

## 🐛 Troubleshooting

### Issue: "AI agent not responding"
**Solution**: Check `ANTHROPIC_API_KEY` is set correctly

### Issue: "Responses are too robotic"
**Solution**: Adjust temperature in `agent.generate_response()` (currently 0.7)

### Issue: "Session ends too early"
**Solution**: Modify end conditions in `SessionManager.should_end_session()`

### Issue: "Intelligence not extracted"
**Solution**: Check regex patterns in `IntelligenceExtractor`

---

## 📝 Project Structure

```
honeypot-api/
├── app.py                  # Main FastAPI application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
├── .env.example           # Environment template
├── test_honeypot.py       # Test suite
└── README.md              # This file
```

---

## 🔗 Integration Example

```python
import requests

# Your honeypot endpoint
HONEYPOT_URL = "https://your-domain.com/api/honeypot"
API_KEY = "sk_test_123456789"

def send_to_honeypot(session_id, message_text, history):
    """Send message to honeypot and get response"""
    
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": message_text,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        "conversationHistory": history,
        "metadata": {
            "channel": "WhatsApp",
            "language": "English",
            "locale": "IN"
        }
    }
    
    response = requests.post(
        HONEYPOT_URL,
        json=payload,
        headers={
            "x-api-key": API_KEY,
            "Content-Type": "application/json"
        }
    )
    
    return response.json()
```

---

## 📚 API Reference

### Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/honeypot` | Yes | Main conversation endpoint |
| GET | `/health` | No | Health check |
| GET | `/sessions/{id}` | Yes | Get session details |

### Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 401 | Invalid API key |
| 404 | Session not found |
| 500 | Server error |

---

## 🎓 Best Practices

1. **Always pass conversation history** for context
2. **Use unique session IDs** (UUID recommended)
3. **Monitor session intelligence** to know when to end
4. **Handle agent fallbacks** if API key missing
5. **Log all interactions** for debugging
6. **Test with diverse scam types** (UPI, bank, prize, arrest)

---

## 📞 Support

For issues or questions:
1. Check logs: `docker logs -f honeypot`
2. Test with `test_honeypot.py`
3. Verify API key configuration
4. Review session state: `GET /sessions/{id}`

---

## 📄 License

MIT License - Free to use for hackathon and educational purposes

---

## 🏆 Hackathon Tips

1. **Test thoroughly** with diverse scam scenarios
2. **Monitor extraction accuracy** - tune regex patterns
3. **Optimize agent prompts** for better engagement
4. **Add logging** to track performance
5. **Deploy early** to test integration with GUVI platform
6. **Document edge cases** you've handled

---

## ✨ Key Features

✅ **Fully automated** scam engagement  
✅ **Real-time intelligence** extraction  
✅ **Production-ready** FastAPI server  
✅ **AI-powered** responses (Claude Sonnet 4)  
✅ **Automatic reporting** to GUVI  
✅ **Docker support** for easy deployment  
✅ **Comprehensive testing** suite included  
✅ **Session management** with state tracking  

---

**Built for GUVI AI Hackathon - Fraud Detection & User Safety** 🛡️
