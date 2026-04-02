import json
import re
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CONFIG ---
API_KEY = "2cfc534356bc4ab887db200e14b12d1a.OPI0nAAq3i-yPlEd2i_hYtnF"
API_URL = "https://ollama.com/api/chat"
MODEL_NAME = "gemma3:4b" 

# EXPANDED DATASET FOR TESTING
emails = [
    {"id": 1, "sender": "investor@venture.com", "subject": "URGENT: Funding Meeting", "body": "Can you meet today at 4 PM to discuss the Series A round? We are ready to move forward."},
    {"id": 2, "sender": "no-reply@spam-center.com", "subject": "You won a iPhone!", "body": "Click here to claim your prize immediately. Limited time offer for selected users."},
    {"id": 3, "sender": "colleague@work.com", "subject": "Lunch?", "body": "Hey, do you want to grab pizza for lunch later? Let me know by 12."},
    {"id": 4, "sender": "support@github.com", "subject": "[Security] New Login Detected", "body": "A new login was detected on your account from a Chrome browser in London, UK. If this was not you, please reset your password."},
    {"id": 5, "sender": "hr@google.com", "subject": "Job Interview Update", "body": "We would like to invite you for a second round of interviews for the Senior AI Engineer position. Are you free next Tuesday?"},
    {"id": 6, "sender": "newsletter@travel-deals.com", "subject": "Last Minute Flights to Bali!", "body": "Unbelievable prices for next weekend! Book now and save 70% on all tropical destinations."},
    {"id": 7, "sender": "client-success@SaaS.com", "subject": "RE: Feedback on API", "body": "Thanks for the feedback! We noticed the latency issue you mentioned and have pushed a fix to the dev branch. Can you test it?"},
    {"id": 8, "sender": "mom@family.com", "subject": "Sunday Dinner", "body": "Hi honey, don't forget we're having dinner at 6 PM this Sunday. Grandma is coming too!"},
    {"id": 9, "sender": "billing@netflix-secure.com", "subject": "Payment Declined", "body": "Your subscription has been suspended due to a payment error. Update your credit card details now to avoid service interruption."},
    {"id": 10, "sender": "dev-team@internal.com", "subject": "CRITICAL: Database Migration", "body": "We are starting the migration in 20 minutes. All write access will be blocked. Stop all local sync scripts now."}
]

@app.route('/emails', methods=['GET'])
def get_emails():
    return jsonify(emails)

@app.route('/process/<int:email_id>', methods=['POST'])
def process_email(email_id):
    email = next((e for e in emails if e["id"] == email_id), None)
    if not email:
        return jsonify({"error": "Email not found"}), 404
    
    prompt = (
        f"Analyze this email: '{email['body']}'. "
        "Return ONLY a JSON object with keys: 'category' (urgent, spam, or normal), "
        "'reason', and 'reply'. No other conversation."
    )

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "format": "json"
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code != 200:
            return jsonify({"category": "error", "reason": f"Status {response.status_code}"}), 500

        result = response.json()
        raw_content = result.get("message", {}).get("content", "")
        
        match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if match:
            ai_data = json.loads(match.group(0))
            return jsonify({**email, **ai_data})
        else:
            return jsonify({**email, "category": "error", "reason": "AI non-JSON"}), 500

    except Exception as e:
        return jsonify({"category": "error", "reason": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)