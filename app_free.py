"""
Honeypot API - FREE VERSION (FIXED)
Rule-based intelligence extraction - No API key needed
Production ready for hackathon
"""

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import uvicorn
import requests
from enum import Enum
import re
import random

# ============================================================================
# CONFIGURATION
# ============================================================================

API_KEY = os.getenv("HONEYPOT_API_KEY", "sk_test_123456789")
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

print("🍯 FREE VERSION - Rule-Based Intelligence Extraction")
print("💰 No API costs - Works immediately")

sessions: Dict[str, Dict[str, Any]] = {}

# ============================================================================
# MODELS
# ============================================================================

class Sender(str, Enum):
    SCAMMER = "scammer"
    USER = "user"

class Message(BaseModel):
    sender: Sender
    text: str
    timestamp: str

class Metadata(BaseModel):
    channel: Optional[str] = "SMS"
    language: Optional[str] = "English"
    locale: Optional[str] = "IN"

class HoneypotRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message] = Field(default_factory=list)
    metadata: Optional[Metadata] = None

class HoneypotResponse(BaseModel):
    status: str
    reply: str

class ExtractedIntelligence(BaseModel):
    bankAccounts: List[str] = Field(default_factory=list)
    upiIds: List[str] = Field(default_factory=list)
    phishingLinks: List[str] = Field(default_factory=list)
    phoneNumbers: List[str] = Field(default_factory=list)
    suspiciousKeywords: List[str] = Field(default_factory=list)

class FinalReport(BaseModel):
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: ExtractedIntelligence
    agentNotes: str

# ============================================================================
# INTELLIGENCE EXTRACTOR
# ============================================================================

class IntelligenceExtractor:
    @staticmethod
    def extract_upi_ids(text: str) -> List[str]:
        pattern = r'\b[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\b'
        upis = re.findall(pattern, text, re.IGNORECASE)
        return list(set([u for u in upis if not u.endswith(('.com', '.org', '.net'))]))
    
    @staticmethod
    def extract_bank_accounts(text: str) -> List[str]:
        pattern = r'\b\d{10,18}\b'
        accounts = re.findall(pattern, text)
        bank_accounts = []
        for acc in accounts:
            if len(acc) == 10 and acc[0] in '6789':
                context = text[max(0, text.find(acc) - 40):text.find(acc) + 40].lower()
                if any(w in context for w in ['account', 'ifsc', 'transfer']):
                    bank_accounts.append(acc)
            elif len(acc) > 10:
                bank_accounts.append(acc)
        return list(set(bank_accounts))
    
    @staticmethod
    def extract_phone_numbers(text: str) -> List[str]:
        patterns = [r'\+91[\s-]?\d{10}', r'\b[6-9]\d{9}\b']
        numbers = []
        for pattern in patterns:
            numbers.extend(re.findall(pattern, text))
        return list(set(numbers))
    
    @staticmethod
    def extract_links(text: str) -> List[str]:
        pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return list(set(re.findall(pattern, text, re.IGNORECASE)))
    
    @staticmethod
    def extract_suspicious_keywords(text: str) -> List[str]:
        keywords = [
            'urgent', 'immediately', 'verify', 'suspend', 'blocked', 'expire',
            'account', 'bank', 'kyc', 'pan', 'aadhar', 'otp', 'password',
            'prize', 'winner', 'congratulations', 'claim', 'reward',
            'arrest', 'legal', 'court', 'police', 'tax', 'fine'
        ]
        text_lower = text.lower()
        return list(set([kw for kw in keywords if kw in text_lower]))
    
    @classmethod
    def extract_all(cls, conversation: List[Message]) -> ExtractedIntelligence:
        full_text = " ".join([msg.text for msg in conversation])
        return ExtractedIntelligence(
            bankAccounts=cls.extract_bank_accounts(full_text),
            upiIds=cls.extract_upi_ids(full_text),
            phishingLinks=cls.extract_links(full_text),
            phoneNumbers=cls.extract_phone_numbers(full_text),
            suspiciousKeywords=cls.extract_suspicious_keywords(full_text)
        )

# ============================================================================
# SCAM DETECTOR
# ============================================================================

class ScamDetector:
    SCAM_INDICATORS = [
        'account blocked', 'verify immediately', 'suspend', 'kyc update',
        'prize winner', 'claim reward', 'urgent action', 'otp',
        'bank details', 'upi id', 'arrest warrant', 'legal notice',
        'tax pending', 'refund', 'click here', 'password'
    ]
    
    @classmethod
    def is_scam(cls, message: str) -> bool:
        message_lower = message.lower()
        indicator_count = sum(1 for ind in cls.SCAM_INDICATORS if ind in message_lower)
        has_urgency = any(w in message_lower for w in ['urgent', 'immediately', 'now', 'today'])
        has_financial = any(w in message_lower for w in ['account', 'bank', 'upi', 'pay', 'transfer'])
        return indicator_count >= 2 or (has_urgency and has_financial)

# ============================================================================
# SMART AGENT (Context-Aware Responses)
# ============================================================================

class SmartAgent:
    """Context-aware response generator - no API needed"""
    
    def generate_response(self, message: str, history: List[Message], intel: ExtractedIntelligence) -> str:
        """Generate smart contextual response"""
        
        msg_lower = message.lower()
        prev_responses = [m.text for m in history if m.sender == Sender.USER]
        
        # Determine context and generate appropriate responses
        responses = []
        
        # UPI/Payment mentioned
        if 'upi' in msg_lower or '@' in message:
            responses = [
                "Which UPI ID should I use? Can I call you first?",
                "What's the exact UPI? Do you have a verification number?",
                "Is there a customer service number to confirm this?",
                "Which account exactly? Can you send official details?"
            ]
        
        # Account blocking/suspension
        elif any(w in msg_lower for w in ['block', 'suspend', 'deactivate', 'freeze']):
            responses = [
                "Which bank account? What's your helpline number?",
                "Why is this happening? How can I verify this is real?",
                "What do I need to do? Which bank department is this?",
                "Can I call your office? What's the official number?"
            ]
        
        # Link/Website
        elif 'http' in message or 'link' in msg_lower or 'click' in msg_lower:
            responses = [
                "Is this the official website? Can you give me your phone number?",
                "I'm not sure about clicking links. What's your contact number?",
                "Can I call instead? What's your official helpline?",
                "Is there another way to verify? Phone number?"
            ]
        
        # Phone/Call mentioned
        elif 'call' in msg_lower or 'phone' in msg_lower or 'whatsapp' in msg_lower:
            responses = [
                "What number should I call? Is this the official line?",
                "Can you confirm this is your real number? Which department?",
                "Is this the bank's main number or a direct line?",
                "What's your employee ID? Which branch are you from?"
            ]
        
        # Payment request
        elif any(w in msg_lower for w in ['pay', 'send', 'transfer', 'deposit', 'fee']):
            responses = [
                "Where exactly should I send it? What's the account number?",
                "Which account? Can you give me IFSC code?",
                "What's the official account? Can I verify this first?",
                "Is there a reference number? What's your contact info?"
            ]
        
        # Prize/Winner
        elif any(w in msg_lower for w in ['prize', 'won', 'winner', 'congratulations']):
            responses = [
                "Really? How do I claim this? What's your office number?",
                "Which company is this? Can I call to verify?",
                "What do I need to do? Is there a verification number?",
                "Can you send official details? What's your contact?"
            ]
        
        # Generic smart responses
        else:
            responses = [
                "I'm confused. What exactly should I do? Who should I contact?",
                "Can you explain more clearly? What's your phone number?",
                "Which organization is this? How can I verify you?",
                "What's the first step? Can you give me contact details?"
            ]
        
        # Filter out already used responses
        available = [r for r in responses if r not in prev_responses]
        
        if available:
            reply = random.choice(available)
        else:
            reply = "I need help understanding this. What's your contact number?"
        
        print(f"💡 Smart Response: {reply}")
        return reply

# ============================================================================
# SESSION MANAGER
# ============================================================================

class SessionManager:
    @staticmethod
    def get_session(session_id: str) -> Dict[str, Any]:
        if session_id not in sessions:
            sessions[session_id] = {
                "messages": [],
                "scam_detected": False,
                "intelligence": ExtractedIntelligence(),
                "agent_active": False,
                "started_at": datetime.utcnow().isoformat()
            }
        return sessions[session_id]
    
    @staticmethod
    def add_message(session_id: str, message: Message):
        session = SessionManager.get_session(session_id)
        session["messages"].append(message)
    
    @staticmethod
    def should_end_session(session_id: str) -> bool:
        session = SessionManager.get_session(session_id)
        message_count = len(session["messages"])
        intel = session["intelligence"]
        intel_types = sum([
            len(intel.upiIds) > 0,
            len(intel.bankAccounts) > 0,
            len(intel.phoneNumbers) > 0,
            len(intel.phishingLinks) > 0
        ])
        return message_count >= 20 or intel_types >= 2

# ============================================================================
# REPORTER
# ============================================================================

class Reporter:
    @staticmethod
    def send_final_report(session_id: str):
        session = SessionManager.get_session(session_id)
        intel = session["intelligence"]
        notes_parts = []
        
        if intel.suspiciousKeywords:
            notes_parts.append(f"Tactics: {', '.join(intel.suspiciousKeywords[:5])}")
        if intel.phishingLinks:
            notes_parts.append(f"Shared {len(intel.phishingLinks)} phishing links")
        if intel.upiIds or intel.bankAccounts:
            notes_parts.append("Requested payment credentials")
        
        agent_notes = ". ".join(notes_parts) if notes_parts else "Scammer engaged, intelligence extracted"
        
        report = FinalReport(
            sessionId=session_id,
            scamDetected=session["scam_detected"],
            totalMessagesExchanged=len(session["messages"]),
            extractedIntelligence=intel,
            agentNotes=agent_notes
        )
        
        try:
            response = requests.post(
                GUVI_CALLBACK_URL,
                json=report.dict(),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ Final report sent for session {session_id}")
                return True
            else:
                print(f"❌ Report failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Report error: {e}")
            return False

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Honeypot API - FREE",
    description="Smart Rule-Based Scam Detection - No API Key Required",
    version="1.0.0"
)

agent = SmartAgent()

@app.post("/api/honeypot", response_model=HoneypotResponse)
async def honeypot_endpoint(request: HoneypotRequest, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    session = SessionManager.get_session(request.sessionId)
    SessionManager.add_message(request.sessionId, request.message)
    full_conversation = request.conversationHistory + [request.message]
    
    # Detect scam
    if not session["scam_detected"]:
        if ScamDetector.is_scam(request.message.text):
            session["scam_detected"] = True
            session["agent_active"] = True
            print(f"🚨 Scam detected: {request.sessionId}")
    
    # Extract intelligence
    session["intelligence"] = IntelligenceExtractor.extract_all(full_conversation)
    
    # Generate response
    if session["agent_active"]:
        reply_text = agent.generate_response(request.message.text, full_conversation, session["intelligence"])
    else:
        reply_text = "I'm not sure what you mean. Can you explain?"
    
    # Add reply
    agent_message = Message(
        sender=Sender.USER,
        text=reply_text,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )
    SessionManager.add_message(request.sessionId, agent_message)
    
    # Check if should end
    if SessionManager.should_end_session(request.sessionId):
        print(f"📊 Ending session {request.sessionId}")
        Reporter.send_final_report(request.sessionId)
    
    return HoneypotResponse(status="success", reply=reply_text)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "honeypot-free",
        "mode": "smart-rules",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/sessions/{session_id}")
async def get_session_info(session_id: str, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return {
        "sessionId": session_id,
        "messageCount": len(session["messages"]),
        "scamDetected": session["scam_detected"],
        "agentActive": session["agent_active"],
        "intelligence": session["intelligence"].dict(),
        "startedAt": session["started_at"]
    }

if __name__ == "__main__":
    print("🍯 Starting FREE Honeypot API...")
    print(f"📍 API Key: {API_KEY[:10]}...")
    print("💡 Smart rule-based responses - No API costs")
    
    uvicorn.run("app_free:app", host="0.0.0.0", port=8000, reload=True)
