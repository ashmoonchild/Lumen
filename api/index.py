from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 1. Récupération et nettoyage de la question
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = urllib.parse.parse_qs(post_data)
            query = params.get('query', [''])[0].strip()

            if not query:
                query = "Dis bonjour"

            # 2. Clé API
            api_key = os.environ.get("GEMINI_API_KEY", "").strip()
            
            # 3. URL Gemini 1.5 Flash (Version la plus stable)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            # 4. Structure JSON ultra-précise
            payload = {
                "contents": [
                    {
                        "parts": [{"text": f"Tu es Lumen, une fée guide bienveillante. Réponds courtement en français : {query}"}]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": 100,
                    "temperature": 0.7
                }
            }

            body = json.dumps(payload).encode('utf-8')
            
            req = urllib.request.Request(
                url, 
                data=body, 
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                
                # Extraction sécurisée
                if 'candidates' in res_data and len(res_data['candidates']) > 0:
                    answer = res_data['candidates'][0]['content']['parts'][0]['text']
                    self.send_response_and_msg(answer)
                else:
                    self.send_response_and_msg("✨ Lumen cherche ses mots... réessaie !")

        except urllib.error.HTTPError as e:
            err_res = e.read().decode('utf-8')
            # Si c'est encore une erreur 400, on affiche un bout du message de Google
            self.send_response_and_msg(f"Erreur Google {e.code}: {e.reason}")
        except Exception as e:
            self.send_response_and_msg(f"Erreur technique : {str(e)}")

    def do_GET(self):
        self.do_POST()

    def send_response_and_msg(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
