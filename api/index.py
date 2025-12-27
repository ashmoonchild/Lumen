from http.server import BaseHTTPRequestHandler
import urllib.parse
import json
import os
import requests

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        # 1. Récupération de la question (query)
        data = urllib.parse.parse_qs(post_data)
        query = data.get('query', [''])[0]
        
        # 2. Vérification de la Clé API
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            self.send_response(200)
            self.end_headers()
            self.wfile.write("Erreur : Clé GEMINI_API_KEY manquante dans Vercel.".encode('utf-8'))
            return

        # 3. Appel à Gemini 1.5 Flash (Version STABLE v1)
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        
        # Instruction système intégrée au prompt
        system_prompt = "Tu es Lumen, une fée lumineuse et bienveillante de l'Aurora Birth Center. Réponds de façon magique et courte (max 2 phrases)."
        
        payload = {
            "contents": [{
                "parts": [{"text": f"{system_prompt}\n\nUtilisateur: {query}"}]
            }]
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            res_json = response.json()
            
            # Gestion des erreurs renvoyées par Google
            if "error" in res_json:
                msg_err = res_json["error"].get("message", "Erreur Google inconnue")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(f"Erreur Google : {msg_err}".encode('utf-8'))
                return

            # Extraction du texte de la réponse
            if "candidates" in res_json and res_json['candidates'][0]['content']['parts']:
                answer = res_json['candidates'][0]['content']['parts'][0]['text']
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(answer.encode('utf-8'))
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write("Lumen reste silencieuse... (
