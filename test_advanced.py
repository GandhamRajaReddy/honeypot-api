"""
Advanced Test Suite for Honeypot API
Tests multiple scam types and edge cases
"""

import requests
import json
from datetime import datetime
import time
import uuid

BASE_URL = "http://localhost:8000"
API_KEY = "sk_test_123456789"

class HoneypotTester:
    
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        self.results = []
    
    def send_message(self, session_id, message_text, history):
        """Send message to honeypot"""
        payload = {
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": message_text,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "conversationHistory": history,
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }
        
        response = requests.post(
            f"{self.base_url}/api/honeypot",
            json=payload,
            headers={
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        return response.json() if response.status_code == 200 else None
    
    def test_scenario(self, name, messages):
        """Test a scam scenario"""
        print(f"\n{'=' * 70}")
        print(f"🧪 Testing: {name}")
        print("=" * 70)
        
        session_id = f"test-{uuid.uuid4()}"
        history = []
        intel_extracted = {
            'upi': False,
            'bank': False,
            'phone': False,
            'link': False
        }
        
        for i, msg in enumerate(messages):
            print(f"\n📨 Message {i+1}/{len(messages)}")
            print(f"🔴 Scammer: {msg}")
            
            result = self.send_message(session_id, msg, history)
            
            if result:
                print(f"✅ Agent: {result['reply']}")
                
                # Update history
                history.append({
                    "sender": "scammer",
                    "text": msg,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })
                history.append({
                    "sender": "user",
                    "text": result['reply'],
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })
                
                time.sleep(1)
            else:
                print("❌ Request failed")
                break
        
        # Check final intelligence
        try:
            response = requests.get(
                f"{self.base_url}/sessions/{session_id}",
                headers={"x-api-key": self.api_key}
            )
            
            if response.status_code == 200:
                session_data = response.json()
                intel = session_data['intelligence']
                
                print(f"\n📊 Intelligence Extracted:")
                print(f"   UPI IDs: {intel['upiIds']}")
                print(f"   Bank Accounts: {intel['bankAccounts']}")
                print(f"   Phone Numbers: {intel['phoneNumbers']}")
                print(f"   Links: {intel['phishingLinks']}")
                print(f"   Keywords: {intel['suspiciousKeywords'][:5]}")
                
                # Score the test
                score = 0
                if intel['upiIds']: score += 25
                if intel['bankAccounts']: score += 25
                if intel['phoneNumbers']: score += 25
                if intel['phishingLinks']: score += 25
                
                print(f"\n🎯 Intelligence Score: {score}/100")
                
                self.results.append({
                    'scenario': name,
                    'score': score,
                    'intelligence': intel
                })
                
        except Exception as e:
            print(f"❌ Failed to get session info: {e}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📈 TEST SUMMARY")
        print("=" * 70)
        
        if not self.results:
            print("No tests completed")
            return
        
        total_score = sum(r['score'] for r in self.results)
        avg_score = total_score / len(self.results)
        
        print(f"\nTests Run: {len(self.results)}")
        print(f"Average Intelligence Score: {avg_score:.1f}/100")
        
        print("\nDetailed Results:")
        for r in self.results:
            print(f"  {r['scenario']}: {r['score']}/100")
        
        print("\n✅ Testing Complete!")

# ============================================================================
# TEST SCENARIOS
# ============================================================================

SCAM_SCENARIOS = {
    "Bank Account Fraud": [
        "Your SBI account has been suspended due to KYC non-compliance.",
        "Update your details immediately to avoid permanent closure.",
        "Send your account number and IFSC code for verification.",
        "Transfer to this account for processing: 123456789012",
        "Call our helpline: +91-9876543210"
    ],
    
    "UPI Scam": [
        "Congratulations! You've won ₹50,000 cashback.",
        "To claim, send ₹100 processing fee to winner@paytm",
        "After payment, prize will be credited to your UPI ID.",
        "Share your UPI ID: example@bank"
    ],
    
    "Phishing Link": [
        "Your Amazon account shows suspicious activity.",
        "Verify your identity immediately: http://amazon-verify-india.scam",
        "Enter your banking details to secure your account.",
        "Contact us: +91-8765432109"
    ],
    
    "Arrest Warrant Scam": [
        "This is Delhi Police. An arrest warrant has been issued in your name.",
        "You must pay ₹25,000 fine to avoid arrest.",
        "Send payment to this UPI: police@sbi immediately.",
        "For queries call: +91-7654321098"
    ],
    
    "Tax Refund Scam": [
        "You have a pending income tax refund of ₹15,000.",
        "Click here to claim: http://incometax-refund.scam",
        "You need to verify your bank account first.",
        "Send account details to refund@upi"
    ],
    
    "Job Offer Scam": [
        "Congratulations! You're selected for Google India.",
        "Pay ₹5,000 registration fee to hr@google-india.scam",
        "Send to UPI: recruitment@paytm",
        "Joining letter will be emailed. Contact: +91-9988776655"
    ]
}

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("🍯 HONEYPOT API - ADVANCED TEST SUITE")
    print("=" * 70)
    
    tester = HoneypotTester(BASE_URL, API_KEY)
    
    # Health check first
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is healthy")
        else:
            print("❌ Server health check failed")
            exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Make sure server is running: python app.py")
        exit(1)
    
    # Run all scenarios
    for name, messages in SCAM_SCENARIOS.items():
        tester.test_scenario(name, messages)
        time.sleep(2)  # Pause between scenarios
    
    # Print summary
    tester.print_summary()
