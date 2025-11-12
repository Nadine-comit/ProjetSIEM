# 🚀 Guide de démarrage local - SIEM

## ✅ Oui, SQLite est bien configuré !

La base de données SQLite (`siem_logs.db`) sera créée automatiquement dans le dossier `serveur/` au premier démarrage.

## 📋 Étapes pour tester en local

### Étape 1 : Installer les dépendances

**Terminal 1 - Serveur:**
```bash
cd serveur
pip install -r requirements.txt
```

**Terminal 2 - Client:**
```bash
cd client
pip install -r requirements.txt
```

### Étape 2 : Démarrer le serveur

**Terminal 1:**
```bash
# Depuis la racine du projet
python start_server.py

# OU depuis le dossier serveur
cd serveur
python app.py
```

Vous devriez voir :
```
🚀 Serveur SIEM démarré sur 0.0.0.0:5000
📊 Base de données: siem_logs.db
🔍 Analyse automatique activée (intervalle: 30s)
```

### Étape 3 : Démarrer le client (dans un NOUVEAU terminal)

**Terminal 2:**
```bash
cd client
python client_advanced.py
```

Le client enverra des logs toutes les 5 secondes.

## 🔍 Vérifier que ça fonctionne

### 1. Vérifier la santé du serveur
Ouvrez votre navigateur ou utilisez curl :
```
http://localhost:5000/health
```

### 2. Voir les statistiques
```
http://localhost:5000/stats
```

### 3. Voir les logs reçus
```
http://localhost:5000/logs?minutes=5&limit=10
```

### 4. Voir les alertes générées
```
http://localhost:5000/alerts
```

## 📊 Base de données SQLite

La base de données est créée automatiquement dans : `serveur/siem_logs.db`

### Voir le contenu avec SQLite

**Windows:**
```bash
cd serveur
sqlite3 siem_logs.db
```

**Linux/Mac:**
```bash
cd serveur
sqlite3 siem_logs.db
```

**Commandes SQLite utiles:**
```sql
-- Voir les tables
.tables

-- Voir les 10 derniers logs
SELECT * FROM logs ORDER BY timestamp DESC LIMIT 10;

-- Compter les logs
SELECT COUNT(*) FROM logs;

-- Voir les alertes
SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 10;

-- Quitter
.quit
```

## 🧪 Test rapide avec curl (Windows PowerShell)

```powershell
# Vérifier la santé
Invoke-WebRequest -Uri http://localhost:5000/health

# Voir les stats
Invoke-WebRequest -Uri http://localhost:5000/stats | Select-Object -ExpandProperty Content

# Voir les alertes
Invoke-WebRequest -Uri http://localhost:5000/alerts | Select-Object -ExpandProperty Content
```

## 🐛 Problèmes courants

### Le client ne se connecte pas
- Vérifiez que le serveur est bien démarré
- Vérifiez que l'URL dans `client/client_advanced.py` est `http://localhost:5000/logs`
- Vérifiez qu'aucun autre programme n'utilise le port 5000

### Port 5000 déjà utilisé
Modifiez le port dans `serveur/config.py` :
```python
SERVER_PORT = 5001  # ou un autre port
```

Et mettez à jour l'URL dans le client :
```python
SERVER_URL = "http://localhost:5001/logs"
```

### Pas d'alertes générées
- Attendez 1-2 minutes pour que les logs s'accumulent
- Les seuils peuvent être trop élevés (modifiez dans `serveur/config.py`)
- Déclenchez une analyse manuelle : `POST http://localhost:5000/analyze`

## 📁 Structure des données SQLite

### Table `logs`
- `id` : Identifiant unique
- `host` : Nom de la machine
- `timestamp` : Date/heure du log
- `log_type` : Type (system, connection, error, security)
- `severity` : Sévérité (info, warning, error, critical)
- `message` : Message du log
- `data` : Données JSON supplémentaires
- `created_at` : Date de création dans la base

### Table `alerts`
- `id` : Identifiant unique
- `alert_type` : Type d'alerte
- `severity` : Sévérité (low, medium, high, critical)
- `message` : Message de l'alerte
- `host` : Host concerné
- `details` : Détails JSON
- `timestamp` : Date de création
- `acknowledged` : Si l'alerte a été acquittée (0 ou 1)

## 🎯 Exemple de test complet

1. **Démarrer le serveur** → Terminal 1
2. **Démarrer le client** → Terminal 2
3. **Attendre 2-3 minutes**
4. **Vérifier les alertes** → `http://localhost:5000/alerts`
5. **Voir les logs** → `http://localhost:5000/logs?limit=20`

Vous devriez voir des logs et potentiellement des alertes si les seuils sont dépassés !

