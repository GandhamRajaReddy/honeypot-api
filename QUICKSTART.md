# 🚀 QUICK START - Get Running in 5 Minutes

## Prerequisites
- Python 3.11+ installed
- Anthropic API key (get free at https://console.anthropic.com)

---

## 🏃 Run Locally (Fastest)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Anthropic API key
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# 3. Run server
python app.py
```

**Server running at**: http://localhost:8000

---

## 🐳 Run with Docker (Recommended)

```bash
# 1. Edit .env file and add your Anthropic API key
nano .env

# 2. Build and run
docker-compose up -d

# 3. Check logs
docker-compose logs -f
```

**Server running at**: http://localhost:8000

---

## ✅ Verify It's Working

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

**Expected output:**
```json
{
  "status": "healthy",
  "service": "honeypot-api",
  "timestamp": "2026-01-30T..."
}
```

### Test 2: Run Test Suite
```bash
python test_honeypot.py
```

**Expected output:**
```
🧪 Honeypot API Test Suite
✅ Health check passed
🔴 Scammer Message 1: Your bank account will be blocked...
✅ Agent Response: Oh no! Why would it be blocked?
...
```

---

## 🎯 Quick Integration

### Python Example

```python
import requests

def send_scam_message(message_text):
    response = requests.post(
        "http://localhost:8000/api/honeypot",
        headers={
            "x-api-key": "sk_test_123456789",
            "Content-Type": "application/json"
        },
        json={
            "sessionId": "test-session-1",
            "message": {
                "sender": "scammer",
                "text": message_text,
                "timestamp": "2026-01-30T10:00:00Z"
            },
            "conversationHistory": []
        }
    )
    return response.json()

# Test it
result = send_scam_message("Your bank account will be blocked. Verify now.")
print(result['reply'])
# Output: "Oh no! Why would it be blocked? What do I need to do?"
```

### cURL Example

```bash
curl -X POST http://localhost:8000/api/honeypot \
  -H "x-api-key: sk_test_123456789" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-123",
    "message": {
      "sender": "scammer",
      "text": "Your account will be suspended. Share UPI ID.",
      "timestamp": "2026-01-30T10:00:00Z"
    },
    "conversationHistory": []
  }'
```

---

## 🛠️ Configuration

### Required: Anthropic API Key

1. **Get free key**: https://console.anthropic.com
2. **Set in .env**:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
   ```
3. **Or export**:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-xxxxx"
   ```

### Optional: Custom API Key

Change in `.env`:
```bash
HONEYPOT_API_KEY=your_custom_key_here
```

---

## 📊 View Session Intelligence

```bash
curl -H "x-api-key: sk_test_123456789" \
  http://localhost:8000/sessions/test-123
```

**Response:**
```json
{
  "sessionId": "test-123",
  "messageCount": 6,
  "scamDetected": true,
  "agentActive": true,
  "intelligence": {
    "upiIds": ["scammer@paytm"],
    "phoneNumbers": ["+91-9876543210"],
    "phishingLinks": ["http://fake-bank.scam"],
    "suspiciousKeywords": ["urgent", "verify", "blocked"]
  }
}
```

---

## 🐛 Troubleshooting

### Issue: "Connection refused"
**Fix**: Make sure server is running
```bash
python app.py
```

### Issue: "401 Unauthorized"
**Fix**: Check API key in request header
```bash
-H "x-api-key: sk_test_123456789"
```

### Issue: "Agent not responding naturally"
**Fix**: Make sure ANTHROPIC_API_KEY is set correctly
```bash
echo $ANTHROPIC_API_KEY
```

---

## 📁 File Structure

```
honeypot-api/
├── app.py              # Main application (START HERE)
├── requirements.txt    # Dependencies
├── .env                # Configuration
├── Dockerfile          # Container setup
├── docker-compose.yml  # Easy deployment
├── test_honeypot.py    # Basic tests
├── test_advanced.py    # Advanced tests
├── README.md           # Full documentation
├── DEPLOYMENT.md       # Cloud deployment guide
└── ARCHITECTURE.md     # Technical details
```

---

## ⚡ What Happens Next?

1. **Message arrives** → Scam detection runs
2. **Scam detected** → AI agent activates
3. **Agent engages** → Extracts UPI, bank accounts, links, phones
4. **Intelligence gathered** → Sends final report to GUVI
5. **Evaluation complete** → You get scored!

---

## 🎯 Next Steps

1. ✅ Get server running (above)
2. 📖 Read [README.md](README.md) for full details
3. ☁️ Deploy to cloud with [DEPLOYMENT.md](DEPLOYMENT.md)
4. 🏗️ Understand system with [ARCHITECTURE.md](ARCHITECTURE.md)
5. 🧪 Run advanced tests: `python test_advanced.py`

---

## 📞 Need Help?

1. **Check logs**: `docker logs -f honeypot` or console output
2. **Test health**: `curl http://localhost:8000/health`
3. **Review docs**: See README.md

---

**You're ready to detect scams and extract intelligence! 🍯🔍**
