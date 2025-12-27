from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # REMPLACEZ CECI PAR VOTRE CLÉ GROQ (gsk_...)
            api_key = "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"
            
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            query = urllib.parse.parse_qs(post_data).get('query', [''])[0].strip() or "Hello"

            url = "https://api.groq.com/openai/v1/chat/completions"
            
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "You are Lumen, a fairy guide at Aurora Birth Center. Warm, poetic, max 2 sentences. Mention Mama Allpa, Really Needy, LoveMomma. Tell them to click the front desk for info."},
                    {"role": "user", "content": query}
                ],
                "max_tokens": 80
            }

            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), 
                                         headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}, 
                                         method='POST')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                res_json = json.loads(response.read().decode('utf-8'))
                answer = res_json['choices'][0]['message']['content'].strip()
                self.send_final_response(answer.replace('\n', ' '))

        except Exception as e:
            self.send_final_response(f"✨ *Lumen is dazed* (Error: {str(e)[:20]})")

    def do_GET(self): self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
