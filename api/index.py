from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # GARDER VOTRE CLÉ ICI POUR CE TEST FINAL
            api_key = "AIzaSyC_fIBiH41gVsgol1JcjUe-6y2qm07p0KU" 
            
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            query = urllib.parse.parse_qs(post_data).get('query', [''])[0].strip() or "Hello"

            # TENTATIVE SUR LA VERSION STABLE V1 AVEC LE MODÈLE PRO
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
            
            payload = {
                "contents": [{"parts": [{"text": f"You are Lumen at Aurora Birth Center. Be brief. Visitor: {query}"}]}]
            }

            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                res_json = json.loads(response.read().decode('utf-8'))
                answer = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
                self.send_final_response(answer.replace('\n', ' '))

        except urllib.error.HTTPError as e:
            # On affiche l'erreur et l'URL pour comprendre
            self.send_final_response(f"✨ *Lumen flickers* (V1-PRO Error {e.code})")
        except Exception as e:
            self.send_final_response(f"✨ *Lumen is dazed* ({str(e)[:20]})")

    def do_GET(self): self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
