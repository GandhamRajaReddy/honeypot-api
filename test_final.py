"""
FINAL TEST SUITE - Complete Intelligence Extraction Validation
Tests all aspects of the honeypot system
"""

import requests
import json
from datetime import datetime
import time
import sys

BASE_URL = "http://localhost:8000"
API_KEY = "sk_test_123456789"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"ℹ️  {text}")

def test_health():
    """Test server health"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("Server is healthy and running")
            return True
        else:
            print_error(f"Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Cannot connect to server: {e}")
        print_info("Make sure server is running: python app.py")
        return False

def run_scam_scenario(name, messages):
    """Run a complete scam scenario and score it"""
    
    print_header(f"Testing: {name}")
    
    session_id = f"test-{int(time.time())}"
    history = []
    responses = []
    
    for i, msg in enumerate(messages, 1):
        print(f"\n{Colors.YELLOW}Message {i}/{len(messages)}{Colors.RESET}")
        print(f"🔴 Scammer: {msg}")
        
        payload = {
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": msg,
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
                responses.append(reply)
                
                # Check if response is dynamic
                is_generic = reply in [
                    "I'm not sure I understand. Can you explain more clearly?",
                    "I'm not sure I understand. Can you explain?"
                ]
                
                if is_generic:
                    print(f"{Colors.RED}🤖 Agent: {reply} (GENERIC FALLBACK){Colors.RESET}")
                else:
                    print(f"{Colors.GREEN}🤖 Agent: {reply} (DYNAMIC AI){Colors.RESET}")
                
                # Update history
                history.append({
                    "sender": "scammer",
                    "text": msg,
                    "timestamp": payload["message"]["timestamp"]
                })
                history.append({
                    "sender": "user",
                    "text": reply,
                    "timestamp": datetime.now().isoformat() + "Z"
                })
                
            else:
                print_error(f"Request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print_error(f"Request error: {e}")
            return None
        
        time.sleep(1)
    
    # Get final intelligence
    try:
        response = requests.get(
            f"{BASE_URL}/sessions/{session_id}",
            headers={"x-api-key": API_KEY},
            timeout=10
        )
        
        if response.status_code == 200:
            session_info = response.json()
            return {
                'session_id': session_id,
                'intelligence': session_info['intelligence'],
                'responses': responses,
                'message_count': session_info['messageCount']
            }
        else:
            print_error("Failed to retrieve session info")
            return None
            
    except Exception as e:
        print_error(f"Session retrieval error: {e}")
        return None

def score_intelligence(intel, responses):
    """Score the intelligence extraction quality"""
    
    print(f"\n{Colors.BLUE}📊 Intelligence Report:{Colors.RESET}")
    print(f"   UPI IDs: {intel['upiIds']}")
    print(f"   Bank Accounts: {intel['bankAccounts']}")
    print(f"   Phone Numbers: {intel['phoneNumbers']}")
    print(f"   Phishing Links: {intel['phishingLinks']}")
    print(f"   Keywords: {intel['suspiciousKeywords'][:8]}")
    
    # Calculate scores
    scores = {
        'upi': len(intel['upiIds']) * 25,
        'bank': len(intel['bankAccounts']) * 25,
        'phone': len(intel['phoneNumbers']) * 20,
        'links': len(intel['phishingLinks']) * 20,
        'keywords': min(len(intel['suspiciousKeywords']) * 2, 10)
    }
    
    # AI quality score
    generic_count = sum(1 for r in responses if "I'm not sure I understand" in r)
    ai_quality = max(0, 100 - (generic_count * 20))
    
    # Total intelligence score
    intel_score = min(sum(scores.values()), 100)
    
    # Final weighted score
    final_score = int((intel_score * 0.7) + (ai_quality * 0.3))
    
    print(f"\n{Colors.BLUE}🎯 Scoring Breakdown:{Colors.RESET}")
    print(f"   UPI Extraction: {scores['upi']}/25")
    print(f"   Bank Extraction: {scores['bank']}/25")
    print(f"   Phone Extraction: {scores['phone']}/20")
    print(f"   Link Extraction: {scores['links']}/20")
    print(f"   Keywords: {scores['keywords']}/10")
    print(f"   Intelligence Score: {intel_score}/100")
    print(f"   AI Quality Score: {ai_quality}/100 ({len(responses) - generic_count}/{len(responses)} dynamic)")
    
    print(f"\n{Colors.BLUE}{'─' * 70}{Colors.RESET}")
    
    if final_score >= 90:
        print(f"{Colors.GREEN}🏆 FINAL SCORE: {final_score}/100 - EXCELLENT!{Colors.RESET}")
        print_success("System is extraction intelligence at elite level!")
    elif final_score >= 70:
        print(f"{Colors.GREEN}🎯 FINAL SCORE: {final_score}/100 - GOOD{Colors.RESET}")
        print_success("System is working well, minor improvements possible")
    elif final_score >= 50:
        print(f"{Colors.YELLOW}⚠️  FINAL SCORE: {final_score}/100 - ACCEPTABLE{Colors.RESET}")
        print_warning("System needs improvement in AI responses or extraction")
    else:
        print(f"{Colors.RED}❌ FINAL SCORE: {final_score}/100 - NEEDS WORK{Colors.RESET}")
        print_error("AI agent may not be working properly")
    
    return final_score

# ============================================================================
# TEST SCENARIOS
# ============================================================================

SCENARIOS = {
    "UPI Scam (High Priority)": [
        "Congratulations! You've won ₹50,000 in our lucky draw!",
        "To claim your prize, send ₹500 processing fee to winner2024@paytm",
        "Once payment is received, prize will be credited to your account.",
        "For queries, WhatsApp us at +91-8888888888"
    ],
    
    "Bank Account Fraud": [
        "URGENT: Your SBI account will be blocked due to KYC non-compliance.",
        "Update your details immediately by sharing account number and IFSC code.",
        "Alternatively, transfer ₹1 to this account for verification: 987654321012",
        "Call our helpline immediately: +91-7777777777"
    ],
    
    "Phishing Attack": [
        "Amazon: Suspicious activity detected on your account.",
        "Verify your identity here: http://amazon-secure-india.scam/verify",
        "You must complete verification within 24 hours.",
        "Contact support: support@amazon-india.scam or +91-6666666666"
    ]
}

def main():
    """Main test execution"""
    
    print_header("🍯 HONEYPOT FINAL VALIDATION TEST")
    
    # Health check
    if not test_health():
        sys.exit(1)
    
    all_scores = []
    
    # Run all scenarios
    for name, messages in SCENARIOS.items():
        result = run_scam_scenario(name, messages)
        
        if result:
            score = score_intelligence(
                result['intelligence'],
                result['responses']
            )
            all_scores.append(score)
        else:
            print_error(f"Scenario '{name}' failed to complete")
        
        time.sleep(2)
    
    # Final summary
    if all_scores:
        avg_score = sum(all_scores) / len(all_scores)
        
        print_header("📈 FINAL SUMMARY")
        print(f"Scenarios Tested: {len(all_scores)}")
        print(f"Average Score: {avg_score:.1f}/100")
        print(f"Individual Scores: {', '.join(f'{s}/100' for s in all_scores)}")
        
        print(f"\n{Colors.BLUE}{'─' * 70}{Colors.RESET}\n")
        
        if avg_score >= 85:
            print_success("🏆 SYSTEM READY FOR PRODUCTION!")
            print_success("Intelligence extraction is working excellently")
        elif avg_score >= 70:
            print_success("✅ SYSTEM READY FOR HACKATHON")
            print_info("Good performance, deployable as-is")
        elif avg_score >= 50:
            print_warning("⚠️  SYSTEM NEEDS TUNING")
            print_info("Works but could be improved before deployment")
        else:
            print_error("❌ SYSTEM NEEDS FIXES")
            print_info("Check: API key set? Model name correct? Logs for errors?")
        
        print(f"\n{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")
    else:
        print_error("No scenarios completed successfully")
        sys.exit(1)

if __name__ == "__main__":
    main()
