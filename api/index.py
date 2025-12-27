from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            query = urllib.parse.parse_qs(post_data).get('query', [''])[0].strip() or "Hello"

            url = "https://openrouter.ai/api/v1/chat/completions"
            
            payload = {
                "model": "meta-llama/llama-3.1-8b-instruct:free",
                "messages": [
                    {"role": "system", "content": "You are Lumen, a fairy guide at Aurora Birth Center. Warm, 2 sentences max. Mention Mama Allpa, Really Needy, LoveMomma. Tell them to click the front desk for info."},
                    {"role": "user", "content": query}
                ]
            }

            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), method='POST')
            req.add_header('Authorization', f'Bearer {api_key}')
            req.add_header('Content-Type', 'application/json')
            # OpenRouter demande souvent ces deux en-têtes
            req.add_header('HTTP-Referer', 'http://localhost:3000') 
            req.add_header('X-Title', 'Lumen AI')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                res_json = json.loads(response.read().decode('utf-8'))
                answer = res_json['choices'][0]['message']['content'].strip()
                self.send_final_response(answer.replace('\n', ' '))

        except Exception as e:
            # On affiche l'erreur brute pour ne plus rien rater
            self.send_final_response(f"✨ *Lumen flickers* (Error: {str(e)[:20]})")

    def do_GET(self): self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
