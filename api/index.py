from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 1. Clé API
            api_key = os.environ.get("GEMINI_API_KEY", "").strip()
            
            # 2. Données SL
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            query = urllib.parse.parse_qs(post_data).get('query', [''])[0].strip() or "Hello"

            # 3. URL ciblée sur le modèle présent dans votre liste (v1beta / gemini-2.0-flash-001)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-001:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": f"You are Lumen, a magical fairy guide at the Aurora Birth Center. Be brief and warm in English: {query}"}]
                }]
            }

            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                res_json = json.loads(response.read().decode('utf-8'))
                if 'candidates' in res_json:
                    answer = res_json['candidates'][0]['content']['parts'][0]['text']
                    self.send_final_response(answer.strip())
                else:
                    self.send_final_response("I am searching for my magic dust... try again!")

        except urllib.error.HTTPError as e:
            # On affiche l'erreur pour comprendre si le 404 persiste
            self.send_final_response(f"Lumen Error {e.code}: Model mismatch.")
        except Exception as e:
            self.send_final_response(f"Lumen Error: {str(e)[:30]}")

    def do_GET(self): self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
