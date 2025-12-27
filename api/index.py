from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 1. Récupération de la clé API
            api_key = os.environ.get("GEMINI_API_KEY", "").strip()
            
            # 2. Récupération de la question
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            query = urllib.parse.parse_qs(post_data).get('query', [''])[0].strip() or "Bonjour"

            # 3. URL avec le modèle 2.5 FLASH (Standard pour fin 2025)
            # On utilise v1beta qui est le canal recommandé pour les modèles 2.x et 3.x
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": f"Tu es Lumen, fée guide de l'Aurora Birth Center. Réponds courtement : {query}"}]
                }],
                "generationConfig": {
                    "maxOutputTokens": 150,
                    "temperature": 0.7
                }
            }

            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                res_json = json.loads(response.read().decode('utf-8'))
                # Extraction de la réponse
                if 'candidates' in res_json and res_json['candidates']:
                    answer = res_json['candidates'][0]['content']['parts'][0]['text']
                    self.send_final_response(answer)
                else:
                    self.send_final_response("Lumen est un peu distraite, réessaie !")

        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8')
            self.send_final_response(f"Erreur Google {e.code}: Modèle 2.5 non trouvé.")
        except Exception as e:
            self.send_final_response(f"Erreur technique : {str(e)}")

    def do_GET(self):
        self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
