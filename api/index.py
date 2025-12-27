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

            # CHANGEMENT : Utilisation de la version 'v1' au lieu de 'v1beta'
            # C'est l'URL la plus stable pour Gemini 1.5 Flash
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            context = (
                "You are Lumen, the celestial fairy guide of the Aurora Birth Center. "
                "Always speak in English with a warm and poetic tone. "
                "We support Mama Allpa, Really Needy, and LoveMomma birth systems. "
                "Tell visitors to say your name 'Lumen' to talk to you. "
                "Keep answers very brief (max 3 sentences). ✨"
                f"\n\nVisitor: {query}"
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

            with urllib.request.urlopen(req, timeout=15) as response:
                res_data = response.read().decode('utf-8')
                res_json = json.loads(res_data)
                
                if 'candidates' in res_json and res_json['candidates']:
                    answer = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
                    answer = answer.replace('\n', ' ')
                    self.send_final_response(answer)
                else:
                    self.send_final_response("✨ *Lumen sparkles silently...*")

        except urllib.error.HTTPError as e:
            # Si ça renvoie encore une erreur, on affiche le code exact
            self.send_final_response(f"✨ *Lumen's light flickers...* (Status: {e.code})")
        except Exception as e:
            self.send_final_response(f"✨ *Lumen is resting...* (Error: {str(e)[:20]})")

    def do_GET(self):
        self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
