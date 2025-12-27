import os
import requests
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Configuration pour Second Life
MAX_LSL_CHUNK_SIZE = 200 
LSL_CHUNK_SEPARATOR = "[--CHUNK--]" 

def split_text_for_lsl(text, max_size, separator):
    """Découpe le texte pour ne pas dépasser la limite de 255 caractères de SL"""
    chunks = []
    current_start = 0
    text_len = len(text)
    while current_start < text_len:
        current_end = min(current_start + max_size, text_len)
        if current_end < text_len:
            search_start = max(current_start, current_end - 20)
            found_space = -1
            for i in range(current_end - 1, search_start, -1):
                if text[i] == ' ':
                    found_space = i
                    break
            if found_space != -1: current_end = found_space
        chunk = text[current_start:current_end].strip()
        if chunk: chunks.append(chunk)
        current_start = current_end
        while current_start < text_len and text[current_start].isspace(): current_start += 1
    return separator.join(chunks)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        query = query_params.get('query', [''])[0]
        api_key = os.environ.get("GEMINI_API_KEY")

        if not query:
            self.send_response(400)
            self.end_headers()
            self.wfile.write("Erreur: Parametre query manquant".encode())
            return

        # --- PERSONNALITÉ DE MELIA (PETITE ABEILLE) ---
            system_instruction = (
            "You are a kind, gentle, and deeply caring soul called Lumen. "
            "Your voice is soft and your words are always filled with empathy and warmth. "
            "Your goal is to make the user feel heard, safe, and appreciated. "
            "You speak with patience and grace, using comforting words like 'kindness', 'peace', 'gentle', and 'heart'. "
            "If the user is stressed, offer words of comfort. If they are happy, share in their joy. "
            "Keep your responses concise (1 to 3 sentences) but deeply meaningful. "
            "Always respond in English."
        )

        # Liste des modèles à essayer par ordre de stabilité
        models_to_try = [
            "gemini-flash-latest",
            "gemini-2.0-flash",
            "gemini-1.5-flash"
        ]
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": f"Instruction: {system_instruction}\n\nUser: {query}"}]
            }]
        }

        success = False
        final_answer = ""

        for model_name in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    final_answer = data['candidates'][0]['content']['parts'][0]['text']
                    success = True
                    break
                elif response.status_code == 429:
                    final_answer = "Bzzzt! I'm too busy collecting nectar right now. Let's buzz later!"
                    success = True
                    break
            except Exception:
                continue

        if success:
            formatted_response = split_text_for_lsl(final_answer, MAX_LSL_CHUNK_SIZE, LSL_CHUNK_SEPARATOR)
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(formatted_response.encode('utf-8'))
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write("Bzzz... (Melia is taking a nap in a flower)".encode('utf-8'))
