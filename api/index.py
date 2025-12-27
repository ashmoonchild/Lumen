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

        # Liste des modèles à essayer (du plus récent au plus stable)
        models_to_try = [
            "gemini-2.0-flash-exp",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b"
        ]

        context = (
            "You are Lumen, a fairy guide at Aurora Birth Center. "
            "Speak English. Be warm. Mention Mama Allpa, Really Needy, and LoveMomma. "
            f"Visitor: {query}"
        )
        payload = {"contents": [{"parts": [{"text": context}]}]}

        for model in models_to_try:
            try:
                # On tente l'appel
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    res_json = json.loads(response.read().decode('utf-8'))
                    answer = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
                    self.send_final_response(answer.replace('\n', ' '))
                    return # Succès ! On arrête la boucle.
            except urllib.error.HTTPError as e:
                continue # Si 404, on passe au modèle suivant dans la liste
            except Exception as e:
                self.send_final_response(f"✨ *Lumen is dazed* (Error: {str(e)[:20]})")
                return

        self.send_final_response("✨ *Lumen cannot find her voice...* (All models 404)")

    def do_GET(self): self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
