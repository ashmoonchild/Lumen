from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # On récupère la clé
            api_key = os.environ.get("GROQ_API_KEY", "").strip()
            
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            query = urllib.parse.parse_qs(post_data).get('query', [''])[0].strip() or "Hello"

            # Utilisation de Mixtral, souvent plus stable sur les nouveaux comptes
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {
                "model": "mixtral-8x7b-32768",
                "messages": [
                    {"role": "system", "content": "You are Lumen, a fairy guide at Aurora Birth Center. Warm, 2 sentences max. Mention Mama Allpa, Really Needy, LoveMomma."},
                    {"role": "user", "content": query}
                ]
            }

            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), method='POST')
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', f'Bearer {api_key}')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                res_json = json.loads(response.read().decode('utf-8'))
                answer = res_json['choices'][0]['message']['content']
                self.send_final_response(answer.replace('\n', ' '))

        except urllib.error.HTTPError as e:
            # Si ça échoue, on affiche la raison précise pour corriger
            err_msg = e.read().decode('utf-8')
            self.send_final_response(f"✨ *Lumen flickers* (Log: {err_msg[15:40]})")
        except Exception as e:
            self.send_final_response(f"✨ *Lumen is dazed* ({str(e)[:20]})")

    def do_GET(self): self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
