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
                self.send_response_and_msg("Erreur : Clé GEMINI_API_KEY manquante.")
                return

            # 3. URL Gemini (On utilise gemini-1.5-pro qui est très stable)
            # Changement de l'URL pour forcer la version stable
            base_url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent"
            full_url = f"{base_url}?key={api_key}"
            
            payload = {
                "contents": [{"parts": [{"text": f"Réponds comme une fée : {query}"}]}]
            }
            
            req = urllib.request.Request(
                full_url, 
                data=json.dumps(payload).encode('utf-8'), 
                headers={'Content-Type': 'application/json'}, 
                method='POST'
            )

            # 4. Exécution
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                answer = res_data['candidates'][0]['content']['parts'][0]['text']
                self.send_response_and_msg(answer)

        except urllib.error.HTTPError as e:
            # Si Google renvoie 404, on affiche la raison technique
            error_body = e.read().decode('utf-8')
            self.send_response_and_msg(f"Erreur Google {e.code}: Vérifiez le nom du modèle ou la région de la clé.")
        except Exception as e:
            self.send_response_and_msg(f"Lumen a un souci : {str(e)}")

    def do_GET(self):
        self.do_POST()

    def send_response_and_msg(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
