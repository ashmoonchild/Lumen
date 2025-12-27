from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 1. Vérification de la clé
            api_key = os.environ.get("GEMINI_API_KEY", "").strip()
            if not api_key:
                self.send_msg("Erreur : Clé API manquante dans Vercel.")
                return

            # 2. Récupération de la question
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            query = urllib.parse.parse_qs(post_data).get('query', [''])[0].strip() or "Bonjour"

            # 3. URL en v1beta (indispensable selon ton erreur)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": f"Tu es Lumen, réponds courtement : {query}"}]
                }]
            }

            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                res = json.loads(response.read().decode('utf-8'))
                answer = res['candidates'][0]['content']['parts'][0]['text']
                self.send_msg(answer)

        except urllib.error.HTTPError as e:
            err_msg = e.read().decode('utf-8')
            self.send_msg(f"Erreur Google : {e.code}")
        except Exception as e:
            self.send_msg(f"Erreur : {str(e)}")

    def do_GET(self): self.do_POST()
    def send_msg(self, m):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(m.encode('utf-8'))
