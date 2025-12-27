from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            api_key = os.environ.get("HUGGINGFACE_TOKEN", "").strip()
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            query = urllib.parse.parse_qs(post_data).get('query', [''])[0].strip() or "Hello"

            # Utilisation de Llama 3.2 (le modèle le plus récent et disponible)
            url = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct"
            
            payload = {
                "inputs": f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are Lumen, a fairy guide at Aurora Birth Center. Warm, 2 sentences max. Mention Mama Allpa, Really Needy, LoveMomma. Tell them to click the front desk for info.<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{query}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
                "parameters": {"max_new_tokens": 100, "return_full_text": False}
            }

            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), method='POST')
            req.add_header('Authorization', f'Bearer {api_key}')
            req.add_header('Content-Type', 'application/json')
            
            with urllib.request.urlopen(req, timeout=20) as response:
                res_json = json.loads(response.read().decode('utf-8'))
                
                if isinstance(res_json, list) and len(res_json) > 0:
                    answer = res_json[0].get('generated_text', '').strip()
                elif 'error' in res_json:
                    answer = f"✨ *Lumen is warming up her wings...* (Try again in 20s)"
                else:
                    answer = "Welcome to Aurora! I'm Lumen. Click the front desk for info!"
                
                self.send_final_response(answer.replace('\n', ' '))

        except urllib.error.HTTPError as e:
            self.send_final_response(f"✨ *Lumen flickers* (Gate {e.code})")
        except Exception as e:
            self.send_final_response(f"✨ *Lumen is dazed* (Restarting...)")

    def do_GET(self): self.do_POST()

    def send_final_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
