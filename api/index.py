from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
import requests
import os

# If you are using OpenAI, make sure you added OPENAI_API_KEY to Vercel Environment Variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        # Parse the 'query=' from the LSL script
        params = parse_qs(post_data)
        user_message = params.get('query', [''])[0]

        if not user_message:
            self.send_final_response("I heard nothing...")
            return

        try:
            # This is where we call the AI (Example using OpenAI)
            # If you are using a different AI, replace this section
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": user_message}],
                    "max_tokens": 100
                },
                timeout=10 # Second Life will time out if this is too long
            )
            
            data = response.json()
            ai_text = data['choices'][0]['message']['content'].strip()
            self.send_final_response(ai_text)

        except Exception as e:
            self.send_final_response(f"Error: {str(e)}")

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        # This allows Second Life to read the response clearly
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
