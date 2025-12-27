from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            api_key = os.environ.get("GEMINI_API_KEY", "").strip()
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = urllib.parse.parse_qs(post_data)
            query = params.get('query', [''])[0].strip() or "Hello"

            # Using the 2.5 Flash model which worked!
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            
            # Setting up her English personality
            prompt = (
                "You are Lumen, a luminous and benevolent fairy guide at the Aurora Birth Center in Second Life. "
                "Your role is to welcome future parents with grace, warmth, and a touch of magic. "
                "Always respond in English. Keep your answers poetic, kind, and no longer than 3 sentences. "
                "Use magical emojis like ✨, 🌸, or 🌿. "
                f"The visitor says: {query}"
            )

            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "maxOutputTokens": 200,
                    "temperature": 0.8
                }
            }

            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode('utf-8'), 
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req, timeout=15) as response:
                res = json.loads(response.read().decode('utf-8'))
                answer = res['candidates'][0]['content']['parts'][0]['text']
                self.send_final_response(answer)

        except Exception as e:
            # Fallback message in English
            self.send_final_response("✨ *Lumen sparkles softly* ✨ I am listening, dear soul. Please, tell me again.")

    def do_GET(self): self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
