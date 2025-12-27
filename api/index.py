from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            api_key = os.environ.get("GEMINI_API_KEY", "").strip()
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = urllib.parse.parse_qs(post_data)
            query = params.get('query', [''])[0].strip() or "Hello"

            # On utilise le point d'accès v1beta avec le modèle 1.5-flash
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            context = (
                "You are Lumen, the celestial fairy guide of Aurora Birth Center. English only. "
                "Mention Mama Allpa, Really Needy, and LoveMomma if asked about systems. "
                "Be warm and brief (2-3 sentences max). "
                f"Visitor: {query}"
            )

            payload = {
                "contents": [{"parts": [{"text": context}]}]
            }

            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode('utf-8'), 
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            # Augmentation du timeout à 15 secondes pour éviter les coupures Vercel
            with urllib.request.urlopen(req, timeout=15) as response:
                res_data = response.read().decode('utf-8')
                res_json = json.loads(res_data)
                
                # Extraction sécurisée de la réponse
                if 'candidates' in res_json and res_json['candidates']:
                    candidate = res_json['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        answer = candidate['content']['parts'][0]['text'].strip()
                        answer = answer.replace('\n', ' ')
                        self.send_final_response(answer)
                    else:
                        self.send_final_response("✨ *Lumen hums softly, lost in thought...* (No text content)")
                else:
                    self.send_final_response("✨ *The stars are quiet...* (No candidates)")

        except Exception as e:
            # On affiche un message d'erreur plus utile pour le débug
            error_str = str(e)
            self.send_final_response(f"✨ *Lumen's light flickers...* (Error: {error_str[:30]})")

    def do_GET(self):
        self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
