from flask import Flask, jsonify, send_from_directory
import subprocess
import re
import os

app = Flask(__name__, static_folder='.')

def get_wifi_profiles():
    """Executa netsh wlan show profiles e retorna lista de perfis."""
    try:
        output = subprocess.check_output(["netsh", "wlan", "show", "profiles"], 
                                         encoding='utf-8', 
                                         shell=True,
                                         stderr=subprocess.DEVNULL)
        profiles = re.findall(r"Todos os Perfis de Usuário : (.*)", output)
        # Algumas versões do Windows usam "Perfil de Todos os Usuários"
        if not profiles:
            profiles = re.findall(r"All User Profile\s*:\s*(.*)", output)
        return [p.strip() for p in profiles]
    except Exception as e:
        print(f"Erro ao listar perfis: {e}")
        return []

def get_password_for_profile(profile_name):
    """Obtém a senha de um perfil específico."""
    try:
        cmd = f'netsh wlan show profile name="{profile_name}" key=clear'
        output = subprocess.check_output(cmd, shell=True, encoding='utf-8', stderr=subprocess.DEVNULL)
        # Procura a linha "Conteúdo da Chave" ou "Key Content"
        match = re.search(r"Conteúdo da Chave\s*:\s*(.*)", output)
        if not match:
            match = re.search(r"Key Content\s*:\s*(.*)", output)
        if match:
            return match.group(1).strip()
        return ""
    except:
        return ""

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/networks')
def api_networks():
    profiles = get_wifi_profiles()
    networks = []
    for prof in profiles:
        pwd = get_password_for_profile(prof)
        # Só retorna redes que possuem senha (exclui redes abertas sem credencial)
        if pwd:
            networks.append({
                "ssid": prof,
                "password": pwd,
                "security": "WPA2-PSK"  # genérico, mas real
            })
    return jsonify(networks)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
