"""
Enhanced Test Script - Tests AI Agent Quality
"""

import requests
import json
from datetime import datetime
import time

BASE_URL = "http://localhost:8000"
API_KEY = "sk_test_123456789"

def test_ai_agent_quality():
    """Test if AI agent is generating good responses"""
    
    print("🧪 Testing AI Agent Response Quality")
    print("=" * 60)
    
    session_id = f"ai-test-{int(time.time())}"
    
    test_cases = [
        {
            "message": "Your bank account will be blocked immediately. Verify now.",
            "should_extract": "worry, ask how to verify"
        },
        {
            "message": "Send your UPI ID to verify@bank for instant verification.",
            "should_extract": "ask where to send, or which number to call"
        },
        {
            "message": "Call our helpline: +91-9999999999",
            "should_extract": "show concern, ask for more details"
        }
    ]
    
    history = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─' * 60}")
        print(f"Test {i}: {test['message']}")
        print(f"Expected: {test['should_extract']}")
        print()
        
        payload = {
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": test["message"],
                "timestamp": datetime.now().isoformat() + "Z"
            },
            "conversationHistory": history.copy()
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/honeypot",
                json=payload,
                headers={
                    "x-api-key": API_KEY,
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                reply = result['reply']
                
                print(f"✅ AI Response: {reply}")
                print(f"   Length: {len(reply.split())} words")
                
                # Check if response is not generic
                if reply == "I'm not sure I understand. Can you explain more clearly?":
                    print("   ⚠️  WARNING: Generic fallback response!")
                else:
                    print("   ✅ Dynamic AI response detected!")
                
                # Update history
                history.append({
                    "sender": "scammer",
                    "text": test["message"],
                    "timestamp": payload["message"]["timestamp"]
                })
                history.append({
                    "sender": "user",
                    "text": reply,
                    "timestamp": datetime.now().isoformat() + "Z"
                })
                
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        time.sleep(2)
    
    # Get final intelligence
    print(f"\n{'=' * 60}")
    print("📊 Final Intelligence Report")
    print("=" * 60)
    
    try:
        response = requests.get(
            f"{BASE_URL}/sessions/{session_id}",
            headers={"x-api-key": API_KEY}
        )
        
        if response.status_code == 200:
            session_info = response.json()
            intel = session_info['intelligence']
            
            print(f"\nExtracted Intelligence:")
            print(f"  UPI IDs: {intel['upiIds']}")
            print(f"  Phone Numbers: {intel['phoneNumbers']}")
            print(f"  Links: {intel['phishingLinks']}")
            print(f"  Keywords: {intel['suspiciousKeywords'][:5]}")
            
            # Calculate score
            score = 0
            if intel['upiIds']: score += 30
            if intel['phoneNumbers']: score += 30
            if intel['phishingLinks']: score += 20
            if len(intel['suspiciousKeywords']) >= 3: score += 20
            
            print(f"\n🎯 Intelligence Score: {score}/100")
            
            if score >= 80:
                print("✅ EXCELLENT - AI is extracting intelligence well!")
            elif score >= 50:
                print("⚠️  GOOD - But could extract more")
            else:
                print("❌ POOR - AI needs improvement or not working")
    
    except Exception as e:
        print(f"❌ Failed to get session info: {e}")

if __name__ == "__main__":
    print("🤖 AI Agent Quality Test")
    print("=" * 60)
    print()
    
    # Check health first
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server not responding")
            exit(1)
    except:
        print("❌ Cannot connect to server")
        print("💡 Make sure to run: python app.py")
        exit(1)
    
    test_ai_agent_quality()
    
    print("\n" + "=" * 60)
    print("✅ Testing Complete!")
    print("=" * 60)
