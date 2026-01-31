# 🚀 Deployment Guide - Honeypot API

Complete guide to deploy your Honeypot API to production.

---

## 📋 Pre-Deployment Checklist

- [ ] Anthropic API key obtained
- [ ] Code tested locally
- [ ] Environment variables configured
- [ ] Docker tested
- [ ] Domain/subdomain ready (optional)

---

## 🐳 Option 1: Docker Deployment

### Quick Deploy

```bash
# 1. Clone/download code
cd honeypot-api

# 2. Create .env file
cat > .env << EOF
HONEYPOT_API_KEY=sk_test_123456789
ANTHROPIC_API_KEY=your_actual_api_key_here
EOF

# 3. Build and run
docker-compose up -d

# 4. Check logs
docker-compose logs -f

# 5. Test
curl http://localhost:8000/health
```

### Manual Docker

```bash
# Build
docker build -t honeypot-api .

# Run
docker run -d \
  -p 8000:8000 \
  -e ANTHROPIC_API_KEY=sk-ant-xxxxx \
  -e HONEYPOT_API_KEY=sk_test_123456789 \
  --name honeypot \
  --restart unless-stopped \
  honeypot-api

# View logs
docker logs -f honeypot

# Stop
docker stop honeypot

# Remove
docker rm honeypot
```

---

## ☁️ Option 2: Cloud Platform Deployment

### A. AWS EC2

```bash
# 1. Launch EC2 instance (t3.small recommended)
# OS: Ubuntu 22.04

# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu

# 4. Clone code
git clone your-repo-url
cd honeypot-api

# 5. Configure
nano .env
# Add ANTHROPIC_API_KEY

# 6. Deploy
docker-compose up -d

# 7. Configure security group
# Allow inbound: Port 8000 (or 443 if using HTTPS)
```

**Access**: `http://YOUR_EC2_IP:8000`

---

### B. Google Cloud Run

```bash
# 1. Install gcloud CLI

# 2. Build and push to Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT/honeypot-api

# 3. Deploy to Cloud Run
gcloud run deploy honeypot-api \
  --image gcr.io/YOUR_PROJECT/honeypot-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ANTHROPIC_API_KEY=sk-ant-xxxxx,HONEYPOT_API_KEY=sk_test_123456789

# 4. Get URL
gcloud run services describe honeypot-api --region us-central1
```

**Access**: `https://honeypot-api-xxxxx.run.app`

---

### C. DigitalOcean Droplet

```bash
# 1. Create droplet (Basic $12/month - 2GB RAM)

# 2. SSH into droplet
ssh root@your-droplet-ip

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 4. Deploy
cd /opt
git clone your-repo-url honeypot-api
cd honeypot-api

# Configure
cat > .env << EOF
ANTHROPIC_API_KEY=sk-ant-xxxxx
HONEYPOT_API_KEY=sk_test_123456789
EOF

# Run
docker-compose up -d

# 5. Configure firewall
ufw allow 8000/tcp
ufw enable
```

**Access**: `http://YOUR_DROPLET_IP:8000`

---

### D. Heroku

```bash
# 1. Install Heroku CLI

# 2. Login
heroku login

# 3. Create app
heroku create honeypot-api-yourname

# 4. Set environment variables
heroku config:set ANTHROPIC_API_KEY=sk-ant-xxxxx
heroku config:set HONEYPOT_API_KEY=sk_test_123456789

# 5. Create Procfile
echo "web: uvicorn app:app --host 0.0.0.0 --port \$PORT" > Procfile

# 6. Deploy
git init
git add .
git commit -m "Initial deployment"
heroku git:remote -a honeypot-api-yourname
git push heroku main
```

**Access**: `https://honeypot-api-yourname.herokuapp.com`

---

### E. Render.com (Easiest!)

1. **Create account** at https://render.com
2. **New Web Service**
3. **Connect GitHub repo** (or upload code)
4. **Configure**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app:app --host 0.0.0.0 --port 10000`
5. **Add Environment Variables**:
   - `ANTHROPIC_API_KEY`
   - `HONEYPOT_API_KEY`
6. **Deploy** (automatic)

**Access**: `https://honeypot-api.onrender.com`

---

## 🔒 HTTPS Setup (Production)

### Option A: Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/honeypot
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/honeypot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Install SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### Option B: Caddy (Automatic HTTPS)

```bash
# Install Caddy
curl https://getcaddy.com | bash -s personal

# Create Caddyfile
cat > Caddyfile << EOF
yourdomain.com {
    reverse_proxy localhost:8000
}
EOF

# Run
caddy run
```

---

## 📊 Monitoring & Logging

### Basic Logging

```bash
# View live logs
docker logs -f honeypot

# Save logs to file
docker logs honeypot > honeypot.log 2>&1
```

### Production Logging

Add to `app.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('honeypot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# In endpoints:
logger.info(f"Session {session_id}: Scam detected")
logger.warning(f"Invalid API key attempt from {request.client.host}")
```

---

## 🔥 Performance Optimization

### 1. Use Production Server

Replace `uvicorn.run()` with Gunicorn:

```bash
# Install
pip install gunicorn

# Run
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 2. Add Redis for Session Storage

```python
import redis
import json

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

class SessionManager:
    @staticmethod
    def get_session(session_id: str):
        data = redis_client.get(f"session:{session_id}")
        if data:
            return json.loads(data)
        # Create new session...
    
    @staticmethod
    def save_session(session_id: str, data: dict):
        redis_client.setex(
            f"session:{session_id}",
            3600,  # 1 hour TTL
            json.dumps(data)
        )
```

### 3. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/honeypot")
@limiter.limit("60/minute")  # 60 requests per minute
async def honeypot_endpoint(...):
    ...
```

---

## 🧪 Production Testing

```bash
# Load test with Apache Bench
ab -n 100 -c 10 -H "x-api-key: sk_test_123456789" \
  -p payload.json -T application/json \
  http://your-domain.com/api/honeypot

# Monitor response times
while true; do
  curl -w "@curl-format.txt" -o /dev/null -s \
    -H "x-api-key: sk_test_123456789" \
    http://your-domain.com/health
  sleep 1
done
```

---

## 🔧 Troubleshooting Production Issues

### Issue: High Response Time

**Solution**:
- Add Redis for session caching
- Use Gunicorn with multiple workers
- Enable response caching for repeated queries

### Issue: Memory Leaks

**Solution**:
```python
# Add session cleanup
import threading

def cleanup_old_sessions():
    while True:
        # Remove sessions older than 1 hour
        current_time = time.time()
        to_remove = [
            sid for sid, data in sessions.items()
            if current_time - data.get('last_activity', 0) > 3600
        ]
        for sid in to_remove:
            del sessions[sid]
        time.sleep(600)  # Every 10 minutes

threading.Thread(target=cleanup_old_sessions, daemon=True).start()
```

### Issue: API Key Exposed

**Solution**:
- Rotate immediately
- Use environment variables only
- Never commit .env to git
- Add .env to .gitignore

---

## 📈 Scaling Strategy

### Horizontal Scaling

```bash
# Docker Swarm
docker swarm init
docker service create \
  --name honeypot \
  --replicas 3 \
  --publish 8000:8000 \
  -e ANTHROPIC_API_KEY=sk-ant-xxxxx \
  honeypot-api

# Kubernetes
kubectl create deployment honeypot --image=honeypot-api
kubectl scale deployment honeypot --replicas=3
kubectl expose deployment honeypot --port=8000 --type=LoadBalancer
```

### Load Balancing

```nginx
upstream honeypot_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    location / {
        proxy_pass http://honeypot_backend;
    }
}
```

---

## 💰 Cost Estimation

| Platform | Monthly Cost | Notes |
|----------|--------------|-------|
| DigitalOcean | $12 | 2GB droplet |
| AWS EC2 | $15-30 | t3.small |
| Google Cloud Run | $5-15 | Pay per use |
| Render.com | $7-25 | Starter plan |
| Heroku | $25 | Hobby dyno |

**Plus**: Anthropic API costs (~$0.003 per request)

---

## 🎯 Post-Deployment Checklist

- [ ] Health endpoint responding
- [ ] API key authentication working
- [ ] Test scam detection
- [ ] Intelligence extraction verified
- [ ] GUVI callback configured
- [ ] HTTPS enabled (production)
- [ ] Monitoring setup
- [ ] Logs configured
- [ ] Backups enabled
- [ ] Documentation updated

---

## 📞 Support Resources

- **Server logs**: `docker logs -f honeypot`
- **Health check**: `curl http://your-domain/health`
- **Session debug**: `curl -H "x-api-key: KEY" http://your-domain/sessions/ID`

---

**🚀 You're ready for production!**
