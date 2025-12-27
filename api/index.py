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

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            
            # Refined prompt: We tell her to be EXTREMELY concise so she doesn't get cut off.
            prompt = (
                "You are Lumen, a fairy guide at the Aurora Birth Center. "
                "Speak in English. Be warm, magical, and very brief (under 150 characters). "
                f"Answer this: {query}"
            )

            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "maxOutputTokens": 200, # Small enough to fit in any SL string
                    "temperature": 0.8
                }
            }

            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})

            with urllib.request.urlopen(req, timeout=15) as response:
                res = json.loads(response.read().decode('utf-8'))
                answer = res['candidates'][0]['content']['parts'][0]['text'].strip()
                # We remove any newlines that might break the SL chat
                answer = answer.replace('\n', ' ')
                self.send_final_response(answer)

        except Exception as e:
            self.send_final_response("✨ *Lumen sparkles* ✨ I am here to guide you.")

    def do_GET(self): self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
