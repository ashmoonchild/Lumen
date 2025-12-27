from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 1. Récupération de la clé
            api_key = os.environ.get("GEMINI_API_KEY", "").strip()
            
            # 2. Données de Second Life
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = urllib.parse.parse_qs(post_data)
            query = params.get('query', [''])[0].strip() or "Hello"

            # 3. URL Gemini 1.5 Flash (le plus stable en fin 2025 pour les scripts simples)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            # 4. Payload ultra-simplifié (pour éviter les erreurs de structure)
            payload = {
                "contents": [
                    {
                        "parts": [{"text": f"You are Lumen, a fairy at Aurora Birth Center. Answer in English, very briefly: {query}"}]
                    }
                ]
            }

            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            # 5. Tentative d'appel
            with urllib.request.urlopen(req, timeout=10) as response:
                res_json = json.loads(response.read().decode('utf-8'))
                
                # Vérification de la présence de la réponse
                if 'candidates' in res_json and len(res_json['candidates']) > 0:
                    answer = res_json['candidates'][0]['content']['parts'][0]['text']
                    self.send_final_response(answer)
                else:
                    self.send_final_response("Empty response from Google.")

        except urllib.error.HTTPError as e:
            # Affiche l'erreur Google réelle (ex: 400, 429, 500)
            self.send_final_response(f"Google HTTP Error: {e.code}")
        except Exception as e:
            # Affiche l'erreur Python réelle
            self.send_final_response(f"Python Error: {str(e)[:50]}")

    def do_GET(self):
        self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
