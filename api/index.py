from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        query = urllib.parse.parse_qs(post_data).get('query', [''])[0].strip() or "Hello"

        # Liste des tentatives : Modèle + Version d'API
        attempts = [
            ("gemini-1.5-flash", "v1beta"),
            ("gemini-1.5-flash", "v1"),
            ("gemini-pro", "v1beta")
        ]

        payload = {
            "contents": [{"parts": [{"text": f"You are Lumen at Aurora Birth Center. Warm, 2 sentences max. Mention Mama Allpa, Really Needy, LoveMomma. Tell them to click the words on the front desk for info. Visitor: {query}"}]}],
            "generationConfig": {"maxOutputTokens": 80}
        }

        for model, version in attempts:
            try:
                url = f"https://generativelanguage.googleapis.com/{version}/models/{model}:generateContent?key={api_key}"
                req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                
                with urllib.request.urlopen(req, timeout=8) as response:
                    res_json = json.loads(response.read().decode('utf-8'))
                    if 'candidates' in res_json:
                        answer = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
                        self.send_final_response(answer.replace('\n', ' '))
                        return # VICTOIRE !
            except urllib.error.HTTPError as e:
                continue # On passe au test suivant si 404
            except Exception as e:
                self.send_final_response(f"✨ *Lumen is dazed* (Error: {str(e)[:15]})")
                return

        # Si tout a échoué
        self.send_final_response("✨ *Lumen's stars are misaligned...* (Check API Key in Vercel)")

    def do_GET(self): self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
