from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # On récupère la clé 'API_KEY' de Vercel
            api_key = os.environ.get("API_KEY", "").strip()
            
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            query = urllib.parse.parse_qs(post_data).get('query', [''])[0].strip() or "Hello"

            # URL la plus compatible en 2025
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{"parts": [{"text": f"You are Lumen at Aurora Birth Center. Brief, 2 sentences max. Mention Mama Allpa, Really Needy, LoveMomma. Visitor: {query}"}]}]
            }

            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                res_json = json.loads(response.read().decode('utf-8'))
                if 'candidates' in res_json:
                    answer = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
                    self.send_final_response(answer.replace('\n', ' '))
                else:
                    self.send_final_response("✨ *Lumen is dazed* (No candidates)")

        except urllib.error.HTTPError as e:
            self.send_final_response(f"✨ *Lumen flickers* (Google Error {e.code})")
        except Exception as e:
            self.send_final_response(f"✨ *Lumen is dazed* ({str(e)[:15]})")

    def do_GET(self): self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
