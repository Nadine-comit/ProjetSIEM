# Guide de démarrage rapide - SIEM

## ✅ SQLite est bien configuré !

La base de données SQLite sera créée automatiquement dans `serveur/siem_logs.db` au premier démarrage.

## 🚀 Démarrage en 3 étapes

### 1. Installer les dépendances

**Serveur:**
```bash
cd serveur
pip install -r requirements.txt
```

**Client:**
```bash
cd client
pip install -r requirements.txt
```

### 2. Démarrer le serveur

```bash
# Option 1: Depuis la racine du projet
python start_server.py

# Option 2: Depuis le dossier serveur
cd serveur
python app.py
```

Le serveur sera accessible sur `http://localhost:5000`

### 3. Démarrer un client

Dans un **nouveau terminal**:

```bash
cd client
python client_advanced.py
```

## 📊 Vérifier que tout fonctionne

### Vérifier la santé du serveur
```bash
curl http://localhost:5000/health
```

### Voir les statistiques
```bash
curl http://localhost:5000/stats
```

### Voir les alertes
```bash
curl http://localhost:5000/alerts
```

### Voir les logs récents
```bash
curl http://localhost:5000/logs?minutes=60&limit=10
```

## 🔍 Tester la détection d'anomalies

Le client avancé génère automatiquement:
- Des logs système toutes les 5 secondes
- Des logs de connexion toutes les 15 secondes
- Des logs d'erreur toutes les 25 secondes

Après quelques minutes, vous devriez voir des alertes apparaître dans `/alerts` si les seuils sont dépassés.

## ⚙️ Ajuster les seuils

Modifiez `serveur/config.py` pour ajuster:
- `ERROR_THRESHOLD`: Nombre d'erreurs pour alerter (défaut: 10)
- `ABNORMAL_CONNECTION_THRESHOLD`: Nombre de connexions suspectes (défaut: 5)
- `HIGH_CPU_THRESHOLD`: Seuil CPU en % (défaut: 90)

## 📝 Exemple de log envoyé

```json
{
  "host": "DESKTOP-ABC123",
  "timestamp": "2024-01-15T10:30:00",
  "log_type": "system",
  "severity": "info",
  "message": "System metrics - CPU: 45.2%, Memory: 62.1%, Disk: 78.5%",
  "data": {
    "cpu_percent": 45.2,
    "memory_percent": 62.1,
    "disk_percent": 78.5,
    "os": "Windows 10"
  }
}
```

## 🐛 Problèmes courants

**Le client ne se connecte pas:**
- Vérifiez que le serveur est démarré
- Modifiez `SERVER_URL` dans le fichier client (ligne 8)

**Pas d'alertes générées:**
- Les seuils peuvent être trop élevés
- Attendez quelques minutes pour que les logs s'accumulent
- Déclenchez une analyse manuelle: `curl -X POST http://localhost:5000/analyze`

