from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            api_key = os.environ.get("HUGGINGFACE_TOKEN", "").strip()
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            query = urllib.parse.parse_qs(post_data).get('query', [''])[0].strip() or "Hello"

            # Passage sur un modèle Llama-3 ultra-disponible
            url = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
            
            payload = {
                "inputs": f"You are Lumen, a fairy guide at Aurora Birth Center. Warm, 2 sentences max. Mention Mama Allpa, Really Needy, LoveMomma. Visitor: {query}",
                "parameters": {"max_new_tokens": 100, "return_full_text": False}
            }

            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), method='POST')
            req.add_header('Authorization', f'Bearer {api_key}')
            req.add_header('Content-Type', 'application/json')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                res_json = json.loads(response.read().decode('utf-8'))
                
                # Gestion de la réponse qui peut être une liste ou un dictionnaire
                if isinstance(res_json, list):
                    answer = res_json[0].get('generated_text', '').strip()
                else:
                    answer = res_json.get('generated_text', '').strip()
                
                # Si la réponse est vide, message de secours
                if not answer:
                    answer = "Welcome to Aurora! I am Lumen. Please click the front desk for info."
                
                self.send_final_response(answer.replace('\n', ' '))

        except urllib.error.HTTPError as e:
            # On affiche le code d'erreur exact pour comprendre
            self.send_final_response(f"✨ *Lumen flickers* (Error {e.code})")
        except Exception as e:
            self.send_final_response(f"✨ *Lumen is dazed* ({str(e)[:15]})")

    def do_GET(self): self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
