from http.server import BaseHTTPRequestHandler
import urllib.parse
import json
import os
import requests

# --- CONFIGURATION ---
# L'instruction système qui définit la personnalité de Lumen
SYSTEM_INSTRUCTION = "Tu es Lumen, une petite fée lumineuse et bienveillante qui guide les futurs parents à l'Aurora Birth Center. Tu parles avec douceur, utilise des émojis d'étoiles et de nature, et tu connais tout sur la naissance respectée."

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.process_request()

    def do_POST(self):
        self.process_request()

    def process_request(self):
        # 1. Extraction de la question (query)
        query = ""
        
        # Essayer de récupérer via l'URL (GET)
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        if 'query' in query_params:
            query = query_params['query'][0]
        
        # Essayer de récupérer via le corps de la requête (POST)
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                # Gère le format JSON ou le format formulaire
                if self.headers.get('Content-Type') == 'application/json':
                    data = json.loads(post_data)
                    query = data.get('query', query)
                else:
                    data = urllib.parse.parse_qs(post_data)
                    if 'query' in data:
                        query = data['query'][0]
            except:
                pass

        if not query:
            self.send_response(400)
            self.end_headers()
            self.wfile.write("Erreur: Parametre query manquant".encode())
            return

        # 2. Appel à l'API Gemini (ou autre service AI)
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            self.send_response(500)
            self.end_headers()
            self.wfile.write("Erreur: Cle API manquante sur Vercel".encode())
            return

        # Construction du prompt avec l'instruction système
        prompt = f"{SYSTEM_INSTRUCTION}\n\nUtilisateur: {query}\nLumen:"
        
        url_ai = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        try:
            response = requests.post(url_ai, json=payload)
            response_data = response.json()
            
            # Extraction de la réponse texte
            answer = response_data['candidates'][0]['content']['parts'][0]['text']
            
            # 3. Envoi de la réponse à Second Life
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(answer.encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Erreur interne: {str(e)}".encode())
