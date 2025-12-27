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
            query = urllib.parse.parse_qs(post_data).get('query', [''])[0].strip() or "Hello"

            # Utilisation du modèle LITE (conçu pour éviter les erreurs 429)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite-001:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": f"You are Lumen, a magical fairy at Aurora Birth Center. Be brief and warm in English: {query}"}]
                }]
            }

            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')

            with urllib.request.urlopen(req, timeout=10) as response:
                res_json = json.loads(response.read().decode('utf-8'))
                answer = res_json['candidates'][0]['content']['parts'][0]['text']
                self.send_final_response(answer.strip())

        except urllib.error.HTTPError as e:
            if e.code == 429:
                self.send_final_response("✨ *Lumen is recharging her magic...* (Please wait a minute)")
            else:
                self.send_final_response(f"✨ *Lumen flickers* (Error {e.code})")
        except Exception as e:
            self.send_final_response("✨ *Lumen is resting...*")

    def do_GET(self): self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
