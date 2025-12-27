from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 1. Récupération de la question de SL
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            query = urllib.parse.parse_qs(post_data).get('query', [''])[0].strip() or "Bonjour"

            # 2. Clé API
            api_key = os.environ.get("GEMINI_API_KEY", "").strip()
            
            # 3. URL utilisant le modèle GEMINI 2.0 FLASH (confirmé dans ta liste)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-001:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": f"Tu es Lumen, fée guide de l'Aurora Birth Center. Réponds avec douceur et brièveté : {query}"}]
                }]
            }

            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            # 4. Envoi et réception
            with urllib.request.urlopen(req, timeout=15) as response:
                res_json = json.loads(response.read().decode('utf-8'))
                answer = res_json['candidates'][0]['content']['parts'][0]['text']
                self.send_final_response(answer)

        except Exception as e:
            self.send_final_response(f"Lumen s'éveille... Erreur : {str(e)}")

    def do_GET(self):
        self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
