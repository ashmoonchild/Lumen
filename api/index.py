from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            query = urllib.parse.parse_qs(post_data).get('query', [''])[0].strip() or "Bonjour"

            api_key = os.environ.get("GEMINI_API_KEY", "").strip()
            
            # Utilisation de la version v1 (la plus stable pour les droits d'accès)
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{"parts": [{"text": f"Réponds très brièvement : {query}"}]}],
                "safetySettings": [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}
                ]
            }

            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                res = json.loads(response.read().decode('utf-8'))
                answer = res['candidates'][0]['content']['parts'][0]['text']
                self.send_msg(answer)

        except urllib.error.HTTPError as e:
            msg = e.read().decode('utf-8')
            self.send_msg(f"Erreur 403 : Vérifie les restrictions de ta clé sur AI Studio.")
        except Exception as e:
            self.send_msg(f"Erreur : {str(e)}")

    def do_GET(self): self.do_POST()
    def send_msg(self, m):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(m.encode('utf-8'))
