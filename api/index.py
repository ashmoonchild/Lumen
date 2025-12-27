from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Assure-toi que cette clé est EXACTEMENT celle de console.groq.com
            # Elle doit commencer par gsk_...
            api_key = "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".strip()
            
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            query = urllib.parse.parse_qs(post_data).get('query', [''])[0].strip() or "Hello"

            url = "https://api.groq.com/openai/v1/chat/completions"
            
            payload = {
                "model": "llama-3.3-7b-versatile", # Modèle plus récent et très stable
                "messages": [
                    {"role": "system", "content": "You are Lumen, a fairy guide at Aurora Birth Center. Warm, max 2 sentences. Mention Mama Allpa, Really Needy, LoveMomma. Tell them to click the front desk for info."},
                    {"role": "user", "content": query}
                ],
                "max_tokens": 100
            }

            # Envoi de la requête
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), method='POST')
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', f'Bearer {api_key}')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = response.read().decode('utf-8')
                res_json = json.loads(res_data)
                answer = res_json['choices'][0]['message']['content'].strip()
                self.send_final_response(answer.replace('\n', ' '))

        except urllib.error.HTTPError as e:
            self.send_final_response(f"✨ *Lumen flickers* (Groq Error {e.code})")
        except Exception as e:
            self.send_final_response(f"✨ *Lumen is dazed* ({str(e)[:20]})")

    def do_GET(self): self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
