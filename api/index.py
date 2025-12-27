from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 1. Récupération sécurisée des données
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            # Analyse des paramètres envoyés par SL
            params = urllib.parse.parse_qs(post_data)
            raw_query = params.get('query', [''])[0]
            
            # Nettoyage des caractères spéciaux pour éviter l'erreur 400
            query = raw_query.strip().replace('"', '\\"').replace('\n', ' ')

            if not query or query == "":
                query = "Dis bonjour !"

            # 2. Clé API
            api_key = os.environ.get("GEMINI_API_KEY", "").strip()
            
            # 3. URL et Payload (Format Gemini 1.5 Strict)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": f"Tu es Lumen, fée de l'Aurora Center. Réponds courtement : {query}"}]
                    }
                ]
            }

            data_encoded = json.dumps(payload).encode('utf-8')
            
            # 4. Requête avec Headers complets
            req = urllib.request.Request(
                url, 
                data=data_encoded,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Vercel-Python-Handler'
                },
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=15) as response:
                res_json = json.loads(response.read().decode('utf-8'))
                
                # Extraction avec vérification de structure
                if 'candidates' in res_json and res_json['candidates']:
                    text_response = res_json['candidates'][0]['content']['parts'][0]['text']
                    self.send_final_response(text_response)
                else:
                    self.send_final_response("✨ Lumen est pensive, réessaie !")

        except urllib.error.HTTPError as e:
            error_data = e.read().decode('utf-8')
            # Si c'est encore une erreur 400, on affiche le détail technique pour déboguer
            self.send_final_response(f"Détail 400: {error_data[:100]}")
        except Exception as e:
            self.send_final_response(f"Erreur système: {str(e)}")

    def do_GET(self):
        self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
