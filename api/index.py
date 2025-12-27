from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            query = urllib.parse.parse_qs(post_data).get('query', [''])[0].strip() or "Bonjour"
            api_key = os.environ.get("GEMINI_API_KEY", "").strip()
            
            # On utilise l'URL v1 avec le modèle flash (le plus standard)
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            payload = {"contents": [{"parts": [{"text": query}]}]}
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})

            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode('utf-8'))
                self.send_msg(res['candidates'][0]['content']['parts'][0]['text'])

        except urllib.error.HTTPError as e:
            # ICI : On récupère la VRAIE raison du 403
            raw_error = e.read().decode('utf-8')
            try:
                reason = json.loads(raw_error)['error']['message']
            except:
                reason = raw_error[:100]
            self.send_msg(f"Google 403: {reason}")
        except Exception as e:
            self.send_msg(f"Erreur : {str(e)}")

    def do_GET(self): self.do_POST()
    def send_msg(self, m):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(m.encode('utf-8'))
