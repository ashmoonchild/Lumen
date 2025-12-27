from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # On essaie de récupérer la clé sous deux noms possibles par sécurité
            api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("GEMINI_API_KEY")
            
            if not api_key:
                self.send_final_response("✨ *Lumen is sleeping* (Missing API Key in Vercel)")
                return

            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            query = urllib.parse.parse_qs(post_data).get('query', [''])[0].strip() or "Hello"

            url = "https://api.groq.com/openai/v1/chat/completions"
            
            payload = {
                "model": "llama3-8b-8192", 
                "messages": [
                    {"role": "system", "content": "You are Lumen at Aurora Birth Center. Warm, max 2 sentences. Mention Mama Allpa, Really Needy, LoveMomma. Tell them to click the front desk for info."},
                    {"role": "user", "content": query}
                ]
            }

            # Envoi avec l'en-tête Bearer formaté strictement
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), method='POST')
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', f'Bearer {api_key.strip()}')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                res_json = json.loads(response.read().decode('utf-8'))
                answer = res_json['choices'][0]['message']['content'].strip()
                self.send_final_response(answer.replace('\n', ' '))

        except urllib.error.HTTPError as e:
            # Si Groq renvoie encore 403, on affiche un indice
            self.send_final_response(f"✨ *Lumen flickers* (Groq Access Denied: {e.code})")
        except Exception as e:
            self.send_final_response(f"✨ *Lumen is dazed* ({str(e)[:20]})")

    def do_GET(self): self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
