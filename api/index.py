from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            query = urllib.parse.parse_qs(post_data).get('query', [''])[0]
            api_key = os.environ.get("GEMINI_API_KEY")

            # Liste des URLs à tester par ordre de priorité
            urls = [
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}",
                f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}",
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
            ]

            last_error = ""
            for url in urls:
                try:
                    payload = {"contents": [{"parts": [{"text": f"Réponds comme une fée : {query}"}]}]}
                    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
                    with urllib.request.urlopen(req, timeout=10) as response:
                        res_data = json.loads(response.read().decode('utf-8'))
                        answer = res_data['candidates'][0]['content']['parts'][0]['text']
                        self.send_response_and_msg(answer)
                        return # Succès ! On sort de la boucle.
                except urllib.error.HTTPError as e:
                    last_error = f"{e.code} sur {url.split('/')[5]}" # On garde l'erreur pour info
                    continue # On tente l'URL suivante
            
            self.send_response_and_msg(f"Aucun modèle n'a répondu. Dernière erreur : {last_error}")

        except Exception as e:
            self.send_response_and_msg(f"Erreur système : {str(e)}")

    def do_GET(self):
        self.do_POST()

    def send_response_and_msg(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
