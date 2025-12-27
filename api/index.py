from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 1. Configuration de l'API
            api_key = os.environ.get("GEMINI_API_KEY", "").strip()
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = urllib.parse.parse_qs(post_data)
            query = params.get('query', [''])[0].strip() or "Hello"

            # Utilisation du modèle 1.5-Flash (stable et rapide)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            # 2. Définition de la personnalité riche de Lumen
            context = (
                "You are Lumen, the celestial fairy guide of the Aurora Birth Center. "
                "Your essence is made of starlight and compassion. You guide future parents with poetic grace. "
                "\n\nIMPORTANT KNOWLEDGE: "
                "We provide support and specialized services for users of: "
                "- Mama Allpa "
                "- Really Needy "
                "- LoveMomma "
                "If someone asks about services or birth systems, mention these three specifically. "
                "\n\nINSTRUCTIONS: "
                "1. Always speak in English. "
                "2. Be warm, ethereal, and encouraging. "
                "3. Remind people to say your name 'Lumen' if they want to talk to you. "
                "4. Keep responses under 3-4 sentences to fit the chat bubble. "
                "5. Use magical emojis (✨, 🌿, 🌸, 🌙). "
                f"\n\nVisitor says: {query}"
            )

            payload = {
                "contents": [{"parts": [{"text": context}]}],
                "generationConfig": {
                    "maxOutputTokens": 250,
                    "temperature": 0.85 # Un peu plus haut pour plus de poésie
                }
            }

            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode('utf-8'), 
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req, timeout=15) as response:
                res_json = json.loads(response.read().decode('utf-8'))
                if 'candidates' in res_json:
                    answer = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
                    # Nettoyage des retours à la ligne pour le chat SL
                    answer = answer.replace('\n', ' ')
                    self.send_final_response(answer)
                else:
                    self.send_final_response("✨ *Lumen hums a soft melody, waiting for your words.* ✨")

        except Exception as e:
            self.send_final_response("✨ *The stars are flickering...* Please call my name again, dear one.")

    def do_GET(self):
        self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
