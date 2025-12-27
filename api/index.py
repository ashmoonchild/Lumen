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

        # On teste les 3 combinaisons de noms que Google utilise actuellement
        endpoints = [
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
            "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent",
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        ]

        payload = {
            "contents": [{"parts": [{"text": f"You are Lumen at Aurora Birth Center. Warm, 2 sentences. Visitor: {query}"}]}]
        }

        for url in endpoints:
            try:
                full_url = f"{url}?key={api_key}"
                req = urllib.request.Request(full_url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
                
                with urllib.request.urlopen(req, timeout=8) as response:
                    res_json = json.loads(response.read().decode('utf-8'))
                    answer = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
                    self.send_final_response(answer.replace('\n', ' '))
                    return
            except urllib.error.HTTPError:
                continue # On ignore le 404 et on teste l'URL suivante
            except Exception as e:
                self.send_final_response(f"✨ *Lumen is dazed* (Error: {str(e)[:15]})")
                return

        self.send_final_response("✨ *Lumen's signal is lost...* (Please check the API Key project in Google AI Studio)")

    def do_GET(self): self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
