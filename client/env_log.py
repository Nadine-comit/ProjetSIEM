import requests
import psutil
import socket
import time
from datetime import datetime
import platform  # ✅ ajout important

SERVER_URL = "http://192.168.123.100:5000/logs"  # change localhost par l'IP du serveur Ubuntu si besoin

def collect_logs():
    """Collecte les informations de la machine client"""
    log = {
        "host": socket.gethostname(),
        "os": platform.system() + " " + platform.release(),  # ✅ correction ici
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("C:\\").percent,  # ✅ pour Windows
        "timestamp": datetime.now().isoformat()
    }
    return log

def send_log(log):  # ✅ renommé "send_log" au lieu de "sen_log"
    """Envoie le log au serveur"""
    try:
        response = requests.post(SERVER_URL, json=log)
        if response.status_code == 200:
            print(f"[OK] Log envoyé : {log}")
        else:
            print(f"[ERREUR SERVEUR] Code : {response.status_code}")
    except Exception as e:
        print(f"[ERREUR CONNEXION] {e}")

if __name__ == "__main__":
    print("📡 Client SIEM démarré, envoi toutes les 10 secondes...")
    while True:
        log = collect_logs()
        send_log(log)
        time.sleep(10)
