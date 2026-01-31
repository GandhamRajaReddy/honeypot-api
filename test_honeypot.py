"""
Test script for Honeypot API
Simulates scam conversation flow
"""

import requests
import json
from datetime import datetime
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "sk_test_123456789"

def test_scam_conversation():
    """Simulate a scam conversation"""
    
    session_id = f"test-session-{int(time.time())}"
    
    print("🍯 Testing Honeypot API")
    print(f"📍 Session ID: {session_id}")
    print("=" * 60)
    
    # Scam message sequence
    scam_messages = [
        {
            "message": "Your bank account will be blocked today. Verify immediately.",
            "expected": "scam_detected"
        },
        {
            "message": "Share your UPI ID to avoid account suspension.",
            "expected": "extract_upi"
        },
        {
            "message": "Send to fraud@paytm for verification.",
            "expected": "extract_upi"
        },
        {
            "message": "Also share your account number and IFSC code.",
            "expected": "extract_bank"
        },
        {
            "message": "Call this number immediately: +91-9876543210",
            "expected": "extract_phone"
        },
        {
            "message": "Click here to verify: http://fake-bank-verify.scam",
            "expected": "extract_link"
        }
    ]
    
    conversation_history = []
    
    for i, scam_msg in enumerate(scam_messages):
        print(f"\n{'─' * 60}")
        print(f"🔴 Scammer Message {i+1}: {scam_msg['message']}")
        
        # Build request
        payload = {
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": scam_msg["message"],
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "conversationHistory": conversation_history.copy(),
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }
        
        # Send request
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
                print(f"✅ Agent Response: {result['reply']}")
                
                # Add both messages to history
                conversation_history.append({
                    "sender": "scammer",
                    "text": scam_msg["message"],
                    "timestamp": payload["message"]["timestamp"]
                })
                
                conversation_history.append({
                    "sender": "user",
                    "text": result['reply'],
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })
                
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                break
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            break
        
        time.sleep(1)  # Simulate realistic timing
    
    # Get final session info
    print(f"\n{'=' * 60}")
    print("📊 Final Session Report")
    print("=" * 60)
    
    try:
        response = requests.get(
            f"{BASE_URL}/sessions/{session_id}",
            headers={"x-api-key": API_KEY}
        )
        
        if response.status_code == 200:
            session_info = response.json()
            print(json.dumps(session_info, indent=2))
        else:
            print(f"❌ Could not retrieve session info")
            
    except Exception as e:
        print(f"❌ Failed to get session info: {e}")

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

if __name__ == "__main__":
    print("🧪 Honeypot API Test Suite")
    print("=" * 60)
    
    # Test 1: Health check
    print("\nTest 1: Health Check")
    print("-" * 60)
    test_health()
    
    # Test 2: Scam conversation
    print("\n\nTest 2: Scam Conversation Simulation")
    print("-" * 60)
    test_scam_conversation()
    
    print("\n" + "=" * 60)
    print("✅ Testing complete!")
