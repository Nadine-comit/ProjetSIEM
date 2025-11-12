"""
Script de test pour vérifier que le système SIEM fonctionne
"""
import requests
import time
import json

SERVER_URL = "http://localhost:5000"

def test_health():
    """Test de santé du serveur"""
    print("🔍 Test de santé du serveur...")
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Serveur en ligne !")
            print(f"   Réponse: {response.json()}")
            return True
        else:
            print(f"❌ Serveur répond avec le code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("   Assurez-vous que le serveur est démarré sur http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_stats():
    """Test des statistiques"""
    print("\n📊 Test des statistiques...")
    try:
        response = requests.get(f"{SERVER_URL}/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            print("✅ Statistiques récupérées:")
            print(f"   - Logs (dernière heure): {stats.get('total_logs_last_hour', 0)}")
            print(f"   - Alertes: {stats.get('total_alerts', 0)}")
            print(f"   - Hosts: {list(stats.get('by_host', {}).keys())}")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_logs():
    """Test de récupération des logs"""
    print("\n📝 Test de récupération des logs...")
    try:
        response = requests.get(f"{SERVER_URL}/logs?minutes=5&limit=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            logs = data.get('logs', [])
            print(f"✅ {len(logs)} log(s) récupéré(s)")
            if logs:
                print(f"   Dernier log: {logs[0].get('host')} - {logs[0].get('log_type')}")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_alerts():
    """Test de récupération des alertes"""
    print("\n🚨 Test de récupération des alertes...")
    try:
        response = requests.get(f"{SERVER_URL}/alerts?limit=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            alerts = data.get('alerts', [])
            print(f"✅ {len(alerts)} alerte(s) trouvée(s)")
            if alerts:
                for alert in alerts[:3]:
                    print(f"   - {alert.get('alert_type')}: {alert.get('message')}")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_analysis():
    """Test d'analyse manuelle"""
    print("\n🔍 Test d'analyse manuelle...")
    try:
        response = requests.post(f"{SERVER_URL}/analyze", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analyse terminée: {data.get('alerts_count', 0)} alerte(s) générée(s)")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print("=" * 60)
    print("  TEST DU SYSTÈME SIEM")
    print("=" * 60)
    print()
    
    # Tests
    results = []
    results.append(("Santé du serveur", test_health()))
    time.sleep(1)
    results.append(("Statistiques", test_stats()))
    time.sleep(1)
    results.append(("Récupération des logs", test_logs()))
    time.sleep(1)
    results.append(("Récupération des alertes", test_alerts()))
    time.sleep(1)
    results.append(("Analyse manuelle", test_analysis()))
    
    # Résumé
    print("\n" + "=" * 60)
    print("  RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ OK" if result else "❌ ÉCHEC"
        print(f"{status} - {test_name}")
    
    success_count = sum(1 for _, result in results if result)
    print(f"\nRésultat: {success_count}/{len(results)} tests réussis")
    
    if success_count == len(results):
        print("\n🎉 Tous les tests sont passés ! Le système fonctionne correctement.")
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifiez que le serveur est démarré.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrompu par l'utilisateur.")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")

