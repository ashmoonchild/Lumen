from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Récupération de la clé API configurée dans Vercel
            api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
            
            # Lecture de la question envoyée par Second Life
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            query = urllib.parse.parse_qs(post_data).get('query', [''])[0].strip() or "Hello"

            # Configuration de l'appel OpenRouter
            url = "https://openrouter.ai/api/v1/chat/completions"
            
            payload = {
                "model": "mistralai/mistral-7b-instruct:free",
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are Lumen, a fairy guide at Aurora Birth Center. Warm, poetic, 2 sentences max. Mention Mama Allpa, Really Needy, and LoveMomma. Tell visitors to click the front desk for info."
                    },
                    {
                        "role": "user", 
                        "content": query
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 100
            }

            # Encodage de la requête
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, method='POST')
            
            # Ajout des en-têtes obligatoires pour OpenRouter
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', f'Bearer {api_key}')
            req.add_header('HTTP-Referer', 'https://vercel.com') # Obligatoire pour OpenRouter
            req.add_header('X-Title', 'Lumen Aurora Guide')     # Identifie votre application

            # Exécution de la requête
            with urllib.request.urlopen(req, timeout=15) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)
                
                # Extraction de la réponse de l'IA
                if 'choices' in res_json and len(res_json['choices']) > 0:
                    answer = res_json['choices'][0]['message']['content'].strip()
                else:
                    answer = "✨ *Lumen sparkles softly* Welcome! Please click the front desk for more information."

                self.send_final_response(answer.replace('\n', ' '))

        except urllib.error.HTTPError as e:
            # En cas d'erreur API (400, 401, 403, etc.)
            self.send_final_response(f"✨ *Lumen flickers* (OpenRouter Error {e.code})")
        except Exception as e:
            # En cas d'erreur de code ou de connexion
            self.send_final_response(f"✨ *Lumen is dazed* (Check Vercel Logs)")

    def do_GET(self):
        self.do_POST()

    def send_final_response(self,
