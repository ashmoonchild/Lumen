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

        # Liste des modèles (On garde ta liste qui fonctionne)
        models_to_try = ["gemini-2.0-flash-exp", "gemini-1.5-flash"]

        # Prompt ultra-directif pour limiter la longueur
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
            "generationConfig": {
                "maxOutputTokens": 80,  # Limite technique absolue
                "temperature": 0.7
            }
        }

        for model in models_to_try:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    res_json = json.loads(response.read().decode('utf-8'))
                    answer = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
                    # On s'assure qu'il n'y a pas de sauts de ligne
                    self.send_final_response(answer.replace('\n', ' '))
                    return 
            except:
                continue 

        self.send_final_response("✨ *Lumen is tired...* (All models failed)")

    def do_GET(self): self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
