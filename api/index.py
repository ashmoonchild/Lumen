from http.server import BaseHTTPRequestHandler
import urllib.parse
import json
import os
import requests

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        # 1. Récupération de la query
        data = urllib.parse.parse_qs(post_data)
        query = data.get('query', [''])[0]
        
        if not query:
            self.send_error_msg(400, "Message vide ou mal forme.")
            return

        # 2. Appel Gemini
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            self.send_error_msg(500, "Cle API introuvable sur Vercel.")
            return

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": f"Tu es Lumen, fée guide de l'Aurora Birth Center. Réponds courtement : {query}"}]}]
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            res_json = response.json()
            
            # Vérification de la structure de réponse
            if "candidates" in res_json:
                answer = res_json['candidates'][0]['content']['parts'][0]['text']
                self.send_success(answer)
            else:
                # Si Gemini renvoie une erreur (quota, clé invalide, etc.)
                error_info = res_json.get("error", {}).get("message", "Erreur structurelle Gemini")
                self.send_error_msg(500, f"Gemini API: {error_info}")
                
        except Exception as e:
            self.send_error_msg(500, f"Erreur Python: {str(e)}")

    def send_success(self, msg):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(msg.encode('utf-8'))

    def send_error_msg(self, code, txt):
        self.send_response(code)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(f"Désolée, {txt}".encode('utf-8'))

    def do_GET(self): # Redirige le GET vers le POST pour simplifier les tests
        self.send_error_msg(200, "Le serveur est en ligne. Envoie un message depuis Second Life !")
