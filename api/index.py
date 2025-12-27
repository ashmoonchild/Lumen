from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 1. Récupération des données
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = urllib.parse.parse_qs(post_data)
            query = data.get('query', [''])[0]

            # 2. Clé API
            api_key = os.environ.get("GEMINI_API_KEY")
            
            # 3. URL ULTRA-STRICTE (v1 avec gemini-1.5-flash)
            # Note: pas de 'models/' en trop, pas de faute de frappe
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{"parts": [{"text": f"Tu es Lumen, fée guide. Réponds courtement : {query}"}]}]
            }
            
            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode('utf-8'), 
                headers={'Content-Type': 'application/json'}, 
                method='POST'
            )

            # 4. Envoi
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                if "candidates" in res_data:
                    answer = res_data['candidates'][0]['content']['parts'][0]['text']
                    self.send_response_and_msg(answer)
                else:
                    self.send_response_and_msg("✨ Lumen est pensive, réessaie dans un instant...")

        except urllib.error.HTTPError as e:
            # Diagnostic précis pour le 404
            error_msg = e.read().decode('utf-8')
            self.send_response_and_msg(f"Erreur Google {e.code}: Accès refusé ou modèle invalide.")
        except Exception as e:
            self.send_response_and_msg(f"Souci technique : {str(e)}")

    def do_GET(self):
        self.do_POST()

    def send_response_and_msg(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
