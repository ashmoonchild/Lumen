from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Récupération de la clé OpenRouter
            api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
            
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            query = urllib.parse.parse_qs(post_data).get('query', [''])[0].strip() or "Hello"

            # URL stricte pour OpenRouter
            url = "https://openrouter.ai/api/v1/chat/completions"
            
            # Utilisation d'un modèle ultra-stable (Llama 3.1 8B)
            payload = {
                "model": "meta-llama/llama-3.1-8b-instruct:free",
                "messages": [
                    {"role": "system", "content": "You are Lumen at Aurora Birth Center. Warm, 2 sentences max. Mention Mama Allpa, Really Needy, LoveMomma."},
                    {"role": "user", "content": query}
                ]
            }

            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, method='POST')
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', f'Bearer {api_key}')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)
                answer = res_json['choices'][0]['message']['content'].strip()
                self.send_final_response(answer.replace('\n', ' '))

        except urllib.error.HTTPError as e:
            # Si erreur, on affiche le début de la réponse pour diagnostiquer
            self.send_final_response(f"✨ *Lumen flickers* (OpenRouter {e.code})")
        except Exception as e:
            self.send_final_response(f"✨ *Lumen is dazed* (Check Vercel Logs)")

    def do_GET(self): self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
