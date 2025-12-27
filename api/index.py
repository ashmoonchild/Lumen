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
            query = urllib.parse.parse_qs(post_data).get('query', [''])[0].strip() or "Hello"

            # Changement de modèle vers 'gemini-pro' et version stable 'v1'
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
            
            payload = {
                "contents": [{"parts": [{"text": f"You are Lumen, a fairy guide at Aurora Birth Center. Answer in English, max 2 short sentences. Mention Mama Allpa, Really Needy, and LoveMomma. Tell them to click the words on the front desk for info. Visitor: {query}"}]}]
            }

            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
            
            with urllib.request.urlopen(req, timeout=12) as response:
                res_json = json.loads(response.read().decode('utf-8'))
                if 'candidates' in res_json:
                    answer = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
                    self.send_final_response(answer.replace('\n', ' '))
                else:
                    self.send_final_response("✨ *Lumen is dreaming of stars...* (No response)")

        except urllib.error.HTTPError as e:
            # On affiche l'erreur pour voir si le 404 disparaît enfin
            self.send_final_response(f"✨ *Lumen flickers* (Status: {e.code})")
        except Exception as e:
            self.send_final_response(f"✨ *Lumen is dazed* (Error: {str(e)[:20]})")

    def do_GET(self): self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
