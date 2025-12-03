from flask import Flask, jsonify, send_file, send_from_directory
from flask_cors import CORS
from ftplib import FTP
import os
import re
from datetime import datetime
import threading
import time

app = Flask(__name__)
CORS(app)

# Configuração
FTP_CONFIG = {
    'mendanha': {
        'host': '82.180.153.43',
        'user': 'u109222483.CorInea',
        'password': 'Inea$123Qwe!!',
        'path': '/',
        'pattern': r'MDN-.*\.png$'
    }
}

CACHE_DIR = '/var/www/radar-nowcast/cache'
os.makedirs(f'{CACHE_DIR}/mendanha', exist_ok=True)

# Status da sincronização
sync_status = {
    'last_sync': None,
    'files_count': 0,
    'status': 'idle'
}

def sync_ftp_mendanha():
    """Sincroniza imagens do FTP do Mendanha"""
    global sync_status
    config = FTP_CONFIG['mendanha']
    
    try:
        sync_status['status'] = 'syncing'
        print(f"[FTP] Conectando a {config['host']}...")
        
        ftp = FTP(config['host'], timeout=30)
        ftp.login(config['user'], config['password'])
        ftp.cwd(config['path'])
        
        # Listar arquivos
        files = []
        ftp.retrlines('NLST', files.append)
        
        # Filtrar apenas PNGs do Mendanha
        png_files = [f for f in files if re.match(config['pattern'], f)]
        png_files = sorted(png_files, reverse=True)[:30]  # Últimos 30
        
        print(f"[FTP] Encontrados {len(png_files)} arquivos")
        
        # Baixar arquivos novos
        downloaded = 0
        for filename in png_files:
            local_path = f'{CACHE_DIR}/mendanha/{filename}'
            if not os.path.exists(local_path):
                with open(local_path, 'wb') as f:
                    ftp.retrbinary(f'RETR {filename}', f.write)
                downloaded += 1
                print(f"[FTP] Baixado: {filename}")
        
        ftp.quit()
        
        # Limpar arquivos antigos (manter apenas últimos 30)
        local_files = sorted(os.listdir(f'{CACHE_DIR}/mendanha'), reverse=True)
        for old_file in local_files[30:]:
            os.remove(f'{CACHE_DIR}/mendanha/{old_file}')
        
        sync_status['last_sync'] = datetime.now().isoformat()
        sync_status['files_count'] = len(png_files)
        sync_status['status'] = 'ok'
        print(f"[FTP] Sincronização concluída. {downloaded} novos arquivos.")
        
    except Exception as e:
        sync_status['status'] = f'error: {str(e)}'
        print(f"[FTP] Erro: {e}")

def sync_loop():
    """Loop de sincronização a cada 2 minutos"""
    while True:
        sync_ftp_mendanha()
        time.sleep(120)

# Iniciar thread de sincronização
sync_thread = threading.Thread(target=sync_loop, daemon=True)
sync_thread.start()

# ============ ROTAS ============

@app.route('/')
def index():
    return send_file('/var/www/radar-nowcast/index.html')

@app.route('/api/status')
def get_status():
    return jsonify(sync_status)

@app.route('/api/frames/<radar>')
def get_frames(radar):
    radar_dir = f'{CACHE_DIR}/{radar}'
    if not os.path.exists(radar_dir):
        return jsonify({'frames': [], 'count': 0})
    
    files = sorted([f for f in os.listdir(radar_dir) if f.endswith('.png')], reverse=True)
    return jsonify({
        'radar': radar,
        'frames': files[:20],
        'count': len(files)
    })

@app.route('/api/frame/<radar>/<filename>')
def get_frame(radar, filename):
    return send_from_directory(f'{CACHE_DIR}/{radar}', filename)

@app.route('/api/sync/<radar>')
def manual_sync(radar):
    if radar == 'mendanha':
        threading.Thread(target=sync_ftp_mendanha).start()
        return jsonify({'message': 'Sincronização iniciada'})
    return jsonify({'error': 'Radar não configurado'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
