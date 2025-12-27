from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 1. Récupération de la question
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            query = urllib.parse.parse_qs(post_data).get('query', [''])[0]
            
            # 2. Clé API (on enlève les espaces invisibles s'il y en a)
            api_key = os.environ.get("GEMINI_API_KEY", "").strip()
            
            # 3. URL simplifiée au maximum (Modèle Flash 1.5)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{"parts": [{"text": f"Tu es Lumen, réponds courtement : {query}"}]}]
            }

            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode('utf-8'), 
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                # Extraction sécurisée de la réponse
                if 'candidates' in res_data and res_data['candidates']:
                    answer = res_data['candidates'][0]['content']['parts'][0]['text']
                    self.send_response_and_msg(answer)
                else:
                    self.send_response_and_msg("✨ Lumen réfléchit... réessaie !")

        except urllib.error.HTTPError as e:
            error_text = e.read().decode('utf-8')
            # On affiche un résumé de l'erreur Google pour comprendre le 404
            self.send_response_and_msg(f"Google Error {e.code}: Vérifie si l'API est activée.")
        except Exception as e:
            self.send_response_and_msg(f"Erreur : {str(e)}")

    def do_GET(self):
        self.do_POST()

    def send_response_and_msg(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
