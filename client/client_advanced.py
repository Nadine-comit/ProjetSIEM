"""
Client SIEM avancé - Envoie différents types de logs pour tester le système
"""
import requests
import psutil
import socket
import time
import random
from datetime import datetime
import platform

SERVER_URL = "http://localhost:5000/logs"  # Modifier selon votre configuration

def collect_system_log():
    """Collecte les métriques système"""
    return {
        "host": socket.gethostname(),
        "os": platform.system() + " " + platform.release(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("C:\\").percent if platform.system() == "Windows" else psutil.disk_usage("/").percent,
        "timestamp": datetime.now().isoformat()
    }

def generate_connection_log():
    """Génère un log de connexion simulé"""
    return {
        "host": socket.gethostname(),
        "log_type": "connection",
        "severity": "info",
        "message": f"Connexion établie depuis {random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "source_ip": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "port": random.randint(1024, 65535)
        }
    }

def generate_error_log():
    """Génère un log d'erreur simulé"""
    error_messages = [
        "Échec d'authentification",
        "Erreur de connexion à la base de données",
        "Timeout sur la requête",
        "Erreur de permission",
        "Service indisponible"
    ]
    
    return {
        "host": socket.gethostname(),
        "log_type": "error",
        "severity": random.choice(["error", "warning", "critical"]),
        "message": random.choice(error_messages),
        "timestamp": datetime.now().isoformat(),
        "data": {
            "error_code": random.randint(100, 599),
            "component": random.choice(["database", "api", "auth", "network"])
        }
    }

def send_log(log):
    """Envoie le log au serveur"""
    try:
        response = requests.post(SERVER_URL, json=log, timeout=5)
        if response.status_code == 200:
            print(f"[OK] Log envoyé - Type: {log.get('log_type', 'system')}, Sévérité: {log.get('severity', 'info')}")
        else:
            print(f"[ERREUR SERVEUR] Code : {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"[ERREUR CONNEXION] Impossible de se connecter au serveur {SERVER_URL}")
    except Exception as e:
        print(f"[ERREUR] {e}")

if __name__ == "__main__":
    print("📡 Client SIEM avancé démarré")
    print(f"🌐 Serveur: {SERVER_URL}")
    print("📊 Envoi de logs toutes les 5 secondes...")
    print("-" * 50)
    
    cycle = 0
    while True:
        cycle += 1
        
        # Envoyer un log système toutes les itérations
        system_log = collect_system_log()
        send_log(system_log)
        time.sleep(2)
        
        # Envoyer un log de connexion toutes les 3 itérations
        if cycle % 3 == 0:
            connection_log = generate_connection_log()
            send_log(connection_log)
            time.sleep(2)
        
        # Envoyer un log d'erreur toutes les 5 itérations (pour tester la détection)
        if cycle % 5 == 0:
            error_log = generate_error_log()
            send_log(error_log)
            time.sleep(2)
        
        # Pause avant le prochain cycle
        time.sleep(1)

