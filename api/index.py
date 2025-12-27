from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 1. Lecture des données
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = urllib.parse.parse_qs(post_data)
            query = data.get('query', [''])[0]

            # 2. Clé API
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                self.send_response_and_msg("Erreur : Clé API manquante dans Vercel.")
                return

            # 3. URL Gemini (Version v1beta avec gemini-pro pour compatibilité maximale)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
            
            prompt = f"Tu es Lumen, fée guide de l'Aurora Birth Center. Réponds courtement : {query}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            body = json.dumps(payload).encode('utf-8')

            # 4. Requête
            req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'}, method='POST')
            
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                if "candidates" in res_data:
                    answer = res_data['candidates'][0]['content']['parts'][0]['text']
                    self.send_response_and_msg(answer)
                else:
                    self.send_response_and_msg("Lumen est pensive... (Réponse vide)")

        except urllib.error.HTTPError as e:
            # Détail de l'erreur HTTP pour nous aider
            error_body = e.read().decode('utf-8')
            self.send_response_and_msg(f"Erreur Google {e.code}: {e.reason}")
        except Exception as e:
            self.send_response_and_msg(f"Erreur Python : {str(e)}")

    def do_GET(self):
        self.do_POST()

    def send_response_and_msg(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
