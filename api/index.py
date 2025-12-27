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
        
        # 2. Vérification Clé API
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            self.send_response(200)
            self.end_headers()
            self.wfile.write("Erreur : La clé GEMINI_API_KEY est manquante dans Vercel.".encode('utf-8'))
            return

        # 3. Appel à Gemini 1.5 Flash
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": f"Tu es Lumen, fée guide de l'Aurora Birth Center. Réponds courtement : {query}"}]
            }]
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            res_json = response.json()
            
            # Debug: Si Google renvoie une erreur
            if "error" in res_json:
                msg_err = res_json["error"].get("message", "Erreur inconnue Google")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(f"Erreur Google : {msg_err}".encode('utf-8'))
                return

            # Extraction de la réponse
            answer = res_json['candidates'][0]['content']['parts'][0]['text']
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(answer.encode('utf-8'))
                
        except Exception as e:
            self.send_response(200) # On envoie 200 pour que le texte s'affiche dans SL
            self.end_headers()
            self.wfile.write(f"Erreur Python : {str(e)}".encode('utf-8'))

    def do_GET(self):
        self.do_POST() # Redirige vers POST pour que le navigateur puisse aussi tester
