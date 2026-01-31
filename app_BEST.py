"""
Agentic Honey-Pot for Scam Detection & Intelligence Extraction
FastAPI Application - Production Ready
"""

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import uvicorn
import anthropic
import requests
from enum import Enum
import re
import json

# ============================================================================
# CONFIGURATION
# ============================================================================

API_KEY = os.getenv("HONEYPOT_API_KEY", "sk_test_123456789")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

# Debug: Print API key status
if ANTHROPIC_API_KEY:
    print(f"✅ Anthropic API Key loaded: {ANTHROPIC_API_KEY[:20]}...")
else:
    print("⚠️  WARNING: ANTHROPIC_API_KEY not set - using fallback responses")

# Session storage (in production, use Redis/Database)
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
    """Extract structured intelligence from conversation"""
    
    @staticmethod
    def extract_upi_ids(text: str) -> List[str]:
        """Extract UPI IDs (format: user@bank)"""
        pattern = r'\b[\w\.-]+@[\w]+\b'
        return list(set(re.findall(pattern, text, re.IGNORECASE)))
    
    @staticmethod
    def extract_bank_accounts(text: str) -> List[str]:
        """Extract bank account numbers (10-18 digits)"""
        pattern = r'\b\d{10,18}\b'
        accounts = re.findall(pattern, text)
        # Filter out phone numbers (typically 10 digits starting with 6-9)
        bank_accounts = [acc for acc in accounts if len(acc) > 10 or not acc.startswith(('6', '7', '8', '9'))]
        return list(set(bank_accounts))
    
    @staticmethod
    def extract_phone_numbers(text: str) -> List[str]:
        """Extract phone numbers (Indian format)"""
        patterns = [
            r'\+91[\s-]?\d{10}',  # +91 format
            r'\b[6-9]\d{9}\b',     # 10 digit starting with 6-9
        ]
        numbers = []
        for pattern in patterns:
            numbers.extend(re.findall(pattern, text))
        return list(set(numbers))
    
    @staticmethod
    def extract_links(text: str) -> List[str]:
        """Extract URLs"""
        pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return list(set(re.findall(pattern, text, re.IGNORECASE)))
    
    @staticmethod
    def extract_suspicious_keywords(text: str) -> List[str]:
        """Extract scam-related keywords"""
        keywords = [
            'urgent', 'immediately', 'verify', 'suspend', 'blocked', 'expire',
            'account', 'bank', 'kyc', 'pan', 'aadhar', 'otp', 'password',
            'prize', 'winner', 'congratulations', 'claim', 'reward',
            'arrest', 'legal', 'court', 'police', 'tax', 'fine',
            'click here', 'update now', 'confirm', 'validate'
        ]
        text_lower = text.lower()
        found = [kw for kw in keywords if kw in text_lower]
        return list(set(found))
    
    @classmethod
    def extract_all(cls, conversation: List[Message]) -> ExtractedIntelligence:
        """Extract all intelligence from conversation"""
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
    """Detect scam intent from message"""
    
    SCAM_INDICATORS = [
        'account blocked', 'verify immediately', 'suspend', 'kyc update',
        'prize winner', 'claim reward', 'urgent action', 'otp',
        'bank details', 'upi id', 'arrest warrant', 'legal notice',
        'tax pending', 'refund', 'click here', 'link', 'password',
        'congratulations', 'lottery', 'won', 'expire'
    ]
    
    @classmethod
    def is_scam(cls, message: str) -> bool:
        """Simple keyword-based scam detection"""
        message_lower = message.lower()
        
        # Check for scam indicators
        indicator_count = sum(1 for indicator in cls.SCAM_INDICATORS if indicator in message_lower)
        
        # Check for urgency + financial request combination
        has_urgency = any(word in message_lower for word in ['urgent', 'immediately', 'now', 'today'])
        has_financial = any(word in message_lower for word in ['account', 'bank', 'upi', 'pay', 'transfer'])
        
        return indicator_count >= 2 or (has_urgency and has_financial)

# ============================================================================
# AI AGENT (ANTHROPIC CLAUDE)
# ============================================================================

class ScamEngagementAgent:
    """AI Agent that engages scammers to extract intelligence"""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate_response(
        self,
        current_message: str,
        conversation_history: List[Message],
        extracted_intelligence: ExtractedIntelligence
    ) -> str:
        """Generate human-like response to engage scammer"""
        
        # Build conversation context
        history_text = self._build_history(conversation_history)
        intelligence_summary = self._summarize_intelligence(extracted_intelligence)
        
        # System prompt for the agent
        system_prompt = """You are acting as a confused potential scam victim. Your goal is to extract information from the scammer WITHOUT revealing you know it's a scam.

PERSONA:
- You are a normal person, not tech-savvy
- Confused, worried, cautious
- Want to comply but hesitant
- Ask natural questions

EXTRACTION STRATEGY:
When scammer mentions payment → Ask "Which account should I use?" or "Where do I send it?"
When scammer threatens → Show worry: "Oh no! How can I fix this?"
When scammer shares contact → Ask for clarification: "What number should I call?" or "Can you send the link again?"
When stuck → Act confused: "I don't understand, can you explain differently?"

KEY RULES:
1. Keep responses VERY short (10-15 words max)
2. NEVER use these words: scam, fraud, fake, suspicious, AI, bot, detection
3. Sound like a real worried person
4. Always try to get them to reveal: UPI IDs, bank accounts, phone numbers, or links
5. Show emotion: worry, confusion, fear

EXAMPLES:
Bad: "This seems suspicious. I don't trust this."
Good: "I'm worried. Can you give me your office number to verify?"

Bad: "I need more information about your organization."
Good: "Which bank is this? Where do I send the money?"

Bad: "I understand. Let me process this request."
Good: "Wait, I'm confused. What exactly do I need to do?"
"""

        user_prompt = f"""The scammer just said: "{current_message}"

Previous conversation:
{history_text}

What we've extracted so far:
{intelligence_summary}

Respond naturally as a worried victim. Your response should:
- Be under 15 words
- Ask a question that makes them reveal MORE information (UPI, phone, account, link)
- Sound confused or worried
- NOT sound suspicious or too smart

If they asked for UPI/account → Ask where to send it
If they threatened you → Show worry and ask for help  
If they gave contact info → Ask for clarification
If information is missing → Ask for specifics

Respond now with ONLY your reply (no explanations):"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=100,
                temperature=0.9,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            reply = response.content[0].text.strip()
            
            # Remove quotes if AI added them
            if reply.startswith('"') and reply.endswith('"'):
                reply = reply[1:-1]
            if reply.startswith("'") and reply.endswith("'"):
                reply = reply[1:-1]
            
            # Sanitize reply (remove any accidental reveals)
            reply = self._sanitize_reply(reply)
            
            print(f"🤖 AI Generated: {reply}")
            return reply
            
        except Exception as e:
            print(f"❌ AI Error: {e}")
            # Fallback response if AI fails
            fallback_responses = [
                "Oh no! What exactly do I need to do?",
                "I'm worried. Can you give me more details?",
                "Where should I send this information?",
                "Is there a phone number I can call to verify this?"
            ]
            import random
            return random.choice(fallback_responses)
    
    def _build_history(self, history: List[Message]) -> str:
        """Build conversation history as text"""
        if not history:
            return "(This is the first message)"
        
        lines = []
        for msg in history[-6:]:  # Last 6 messages for context
            role = "Scammer" if msg.sender == Sender.SCAMMER else "You"
            lines.append(f"{role}: {msg.text}")
        return "\n".join(lines)
    
    def _summarize_intelligence(self, intel: ExtractedIntelligence) -> str:
        """Summarize extracted intelligence"""
        parts = []
        if intel.upiIds:
            parts.append(f"UPI IDs: {', '.join(intel.upiIds)}")
        if intel.bankAccounts:
            parts.append(f"Bank Accounts: {', '.join(intel.bankAccounts)}")
        if intel.phoneNumbers:
            parts.append(f"Phone Numbers: {', '.join(intel.phoneNumbers)}")
        if intel.phishingLinks:
            parts.append(f"Links: {', '.join(intel.phishingLinks)}")
        
        return "\n".join(parts) if parts else "(No intelligence extracted yet)"
    
    def _sanitize_reply(self, reply: str) -> str:
        """Remove any accidental scam-revealing words"""
        forbidden = ['scam', 'fraud', 'ai', 'detect', 'honeypot', 'system', 'agent']
        reply_lower = reply.lower()
        
        for word in forbidden:
            if word in reply_lower:
                # Replace with safe fallback
                return "I'm a bit confused. Can you help me understand what I need to do?"
        
        return reply

# ============================================================================
# SESSION MANAGER
# ============================================================================

class SessionManager:
    """Manage conversation sessions"""
    
    @staticmethod
    def get_session(session_id: str) -> Dict[str, Any]:
        """Get or create session"""
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
        """Add message to session"""
        session = SessionManager.get_session(session_id)
        session["messages"].append(message)
    
    @staticmethod
    def should_end_session(session_id: str) -> bool:
        """Decide if session should end and report"""
        session = SessionManager.get_session(session_id)
        
        # End conditions
        message_count = len(session["messages"])
        intel = session["intelligence"]
        
        # End if:
        # - 20+ messages exchanged
        # - OR significant intelligence extracted (2+ different types)
        # - OR scammer stopped responding (implemented externally)
        
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
    """Report final intelligence to GUVI"""
    
    @staticmethod
    def send_final_report(session_id: str):
        """Send final report to GUVI endpoint"""
        session = SessionManager.get_session(session_id)
        
        # Generate agent notes
        intel = session["intelligence"]
        notes_parts = []
        
        if intel.suspiciousKeywords:
            notes_parts.append(f"Used tactics: {', '.join(intel.suspiciousKeywords[:5])}")
        if intel.phishingLinks:
            notes_parts.append(f"Shared {len(intel.phishingLinks)} phishing links")
        if intel.upiIds or intel.bankAccounts:
            notes_parts.append("Requested payment credentials")
        
        agent_notes = ". ".join(notes_parts) if notes_parts else "Scammer engaged, limited intelligence extracted"
        
        # Build report
        report = FinalReport(
            sessionId=session_id,
            scamDetected=session["scam_detected"],
            totalMessagesExchanged=len(session["messages"]),
            extractedIntelligence=intel,
            agentNotes=agent_notes
        )
        
        # Send to GUVI
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
                print(f"❌ Failed to send report: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending report: {e}")
            return False

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Agentic Honey-Pot API",
    description="Scam Detection & Intelligence Extraction System",
    version="1.0.0"
)

# Initialize AI Agent
agent = ScamEngagementAgent(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

@app.post("/api/honeypot", response_model=HoneypotResponse)
async def honeypot_endpoint(
    request: HoneypotRequest,
    x_api_key: str = Header(None)
):
    """Main honeypot endpoint"""
    
    # Validate API Key
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Get or create session
    session = SessionManager.get_session(request.sessionId)
    
    # Add incoming message to history
    SessionManager.add_message(request.sessionId, request.message)
    
    # Build full conversation (history + current)
    full_conversation = request.conversationHistory + [request.message]
    
    # STEP 1: Detect scam intent
    if not session["scam_detected"]:
        is_scam = ScamDetector.is_scam(request.message.text)
        if is_scam:
            session["scam_detected"] = True
            session["agent_active"] = True
            print(f"🚨 Scam detected in session {request.sessionId}")
    
    # STEP 2: Extract intelligence
    session["intelligence"] = IntelligenceExtractor.extract_all(full_conversation)
    
    # STEP 3: Generate AI response
    if session["agent_active"] and agent:
        reply_text = agent.generate_response(
            current_message=request.message.text,
            conversation_history=full_conversation,
            extracted_intelligence=session["intelligence"]
        )
    else:
        # Fallback if agent not active or API key missing
        reply_text = "I'm not sure I understand. Can you explain?"
    
    # Add agent's reply to session
    agent_message = Message(
        sender=Sender.USER,
        text=reply_text,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )
    SessionManager.add_message(request.sessionId, agent_message)
    
    # STEP 4: Check if session should end
    if SessionManager.should_end_session(request.sessionId):
        print(f"📊 Ending session {request.sessionId} - sending final report")
        Reporter.send_final_report(request.sessionId)
    
    return HoneypotResponse(
        status="success",
        reply=reply_text
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "honeypot-api",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/sessions/{session_id}")
async def get_session_info(session_id: str, x_api_key: str = Header(None)):
    """Get session information (for debugging)"""
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

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("🍯 Starting Honeypot API Server...")
    print(f"📍 API Key: {API_KEY[:10]}...")
    print(f"🤖 AI Agent: {'Enabled' if agent else 'Disabled (set ANTHROPIC_API_KEY)'}")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )