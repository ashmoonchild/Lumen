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

            # Utilisation du modèle 1.5 Flash (le plus compatible)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            context = (
            "SYSTEM: You are Lumen, a magical fairy guide at Aurora Birth Center. "
            "STRICT RULES: Answer in ENGLISH only. Maximum 2 short sentences. "
            "INFO: We support Mama Allpa, Really Needy, and LoveMomma. "
            "IMPORTANT: If someone needs more details or is looking for documents, "
            "tell them to click on the words on the front desk. "
            "Be ethereal, warm, and brief. ✨"
            f"\n\nVisitor: {query}"
            )

            payload = {
                "contents": [{"parts": [{"text": context}]}],
                "generationConfig": {"maxOutputTokens": 80, "temperature": 0.7}
            }

            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
            
            with urllib.request.urlopen(req, timeout=10) as response:
                res_json = json.loads(response.read().decode('utf-8'))
                answer = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
                self.send_final_response(answer.replace('\n', ' '))

        except urllib.error.HTTPError as e:
            # On affiche le code d'erreur Google (400, 403, 429...)
            self.send_final_response(f"✨ *Lumen's light flickers* (Google Error {e.code})")
        except Exception as e:
            self.send_final_response(f"✨ *Lumen is dazed* (Error: {str(e)[:20]})")

    def do_GET(self): self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
