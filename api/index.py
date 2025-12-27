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
            params = urllib.parse.parse_qs(post_data)
            query = params.get('query', [''])[0].strip()

            if not query: query = "Bonjour"

            api_key = os.environ.get("GEMINI_API_KEY", "").strip()
            
            # Changement vers la version v1 (Stable) au lieu de v1beta
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": f"Tu es Lumen, fée de l'Aurora Center. Réponds courtement : {query}"}]
                }]
            }

            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=15) as response:
                res_json = json.loads(response.read().decode('utf-8'))
                answer = res_json['candidates'][0]['content']['parts'][0]['text']
                self.send_final_response(answer)

        except urllib.error.HTTPError as e:
            error_data = e.read().decode('utf-8')
            self.send_final_response(f"Erreur Google {e.code}: Modèle ou version incompatible.")
        except Exception as e:
            self.send_final_response(f"Erreur : {str(e)}")

    def do_GET(self):
        self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
