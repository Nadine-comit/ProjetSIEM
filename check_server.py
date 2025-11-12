"""Vérification rapide du serveur"""
import requests
import time

print("Attente du démarrage du serveur (3 secondes)...")
time.sleep(3)

try:
    response = requests.get("http://localhost:5000/health", timeout=5)
    if response.status_code == 200:
        print("✅ SERVEUR EN LIGNE !")
        print(f"   Réponse: {response.json()}")
    else:
        print(f"❌ Serveur répond avec code: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("❌ Serveur non accessible")
    print("   Vérifiez que le serveur est démarré")
except Exception as e:
    print(f"❌ Erreur: {e}")

