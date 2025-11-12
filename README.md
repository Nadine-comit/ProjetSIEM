# Projet SIEM - Journalisation et corrélation d'événements réseau

Système SIEM simplifié en Python pour centraliser les logs d'un réseau et détecter les comportements suspects.

## 🎯 Fonctionnalités

- **Serveur centralisé** : Réception des logs de plusieurs clients via API REST
- **Stockage SQLite** : Base de données pour stocker tous les logs
- **Analyse automatique** : Détection en temps réel des anomalies
- **Détection d'erreurs répétées** : Alerte si trop d'erreurs dans une fenêtre de temps
- **Détection de connexions anormales** : Identification des patterns suspects
- **Surveillance des ressources** : Alertes sur CPU, mémoire et disque élevés
- **Corrélation d'événements** : Détection de patterns complexes

## 📋 Prérequis

- Python 3.7+
- pip

## 🚀 Installation

### Windows

**Option 1 : Scripts batch (double-clic)**
- `start_server.bat` → Démarre le serveur
- `start_client.bat` → Démarre le client

**Option 2 : Ligne de commande**

Serveur :
```bash
cd serveur
pip install -r requirements.txt
python app.py
```

Client :
```bash
cd client
pip install -r requirements.txt
python client_advanced.py
```

### Linux/Ubuntu

**Option 1 : Scripts shell (recommandé)**
```bash
chmod +x start_server.sh start_client.sh
./start_server.sh  # Terminal 1
./start_client.sh   # Terminal 2
```

**Option 2 : Installation manuelle**

Serveur :
```bash
cd serveur
pip3 install -r requirements.txt
python3 app.py
```

Client :
```bash
cd client
pip3 install -r requirements.txt
python3 client_advanced.py
```

Voir `INSTALL_UBUNTU.md` pour plus de détails sur Ubuntu.

### Installation avec environnement virtuel (recommandé)

**Serveur:**
```bash
cd serveur
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app.py
```

**Client:**
```bash
cd client
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
pip install -r requirements.txt
python client_advanced.py
```

## 🏃 Utilisation

### Démarrer le serveur

```bash
cd serveur
python app.py
```

Le serveur démarre sur `http://0.0.0.0:5000` par défaut.

### Démarrer un client

#### Client simple (métriques système uniquement)
```bash
cd client
python env_log.py
```

#### Client avancé (test avec différents types de logs)
```bash
cd client
python client_advanced.py
```

**Important** : Modifier l'URL du serveur dans les fichiers client si nécessaire :
- `env_log.py` : Ligne 8, variable `SERVER_URL`
- `client_advanced.py` : Ligne 8, variable `SERVER_URL`

## 📡 API Endpoints

### Recevoir des logs
```
POST /logs
Content-Type: application/json

{
  "host": "nom_du_host",
  "timestamp": "2024-01-01T12:00:00",
  "log_type": "system|connection|error|security",
  "severity": "info|warning|error|critical",
  "message": "Description du log",
  "data": { ... }
}
```

### Récupérer les logs
```
GET /logs?minutes=60&host=nom_host&limit=100
```

### Récupérer les alertes
```
GET /alerts?limit=50&acknowledged=false
```

### Statistiques
```
GET /stats
```

### Déclencher une analyse manuelle
```
POST /analyze
```

### Vérification de santé
```
GET /health
```

## ⚙️ Configuration

Les paramètres peuvent être modifiés dans `serveur/config.py` :

- `ERROR_THRESHOLD` : Nombre d'erreurs pour déclencher une alerte (défaut: 10)
- `ERROR_TIME_WINDOW` : Fenêtre de temps en secondes (défaut: 60)
- `ABNORMAL_CONNECTION_THRESHOLD` : Nombre de connexions suspectes (défaut: 5)
- `CONNECTION_TIME_WINDOW` : Fenêtre de temps pour les connexions (défaut: 300)
- `HIGH_CPU_THRESHOLD` : Seuil CPU en pourcentage (défaut: 90%)
- `HIGH_MEMORY_THRESHOLD` : Seuil mémoire en pourcentage (défaut: 90%)
- `HIGH_DISK_THRESHOLD` : Seuil disque en pourcentage (défaut: 90%)
- `ANALYSIS_INTERVAL` : Intervalle d'analyse en secondes (défaut: 30)

## 🔍 Types d'alertes détectées

1. **Répétition d'erreurs** : Trop d'erreurs sur un host dans une fenêtre de temps
2. **Connexions anormales** : Nombre élevé de connexions depuis différentes sources
3. **Ressources système élevées** : CPU, mémoire ou disque au-dessus des seuils
4. **Événements corrélés** : Plusieurs types d'anomalies simultanées (alerte critique)

## 📊 Base de données

La base de données SQLite (`siem_logs.db`) contient deux tables :

- **logs** : Tous les logs reçus
- **alerts** : Toutes les alertes générées

Vous pouvez interroger la base directement avec SQLite :
```bash
sqlite3 serveur/siem_logs.db
```

## 🧪 Test du système

1. Démarrer le serveur
2. Démarrer le client avancé dans un autre terminal
3. Observer les logs du serveur pour voir les alertes générées
4. Consulter les alertes via l'API : `GET http://localhost:5000/alerts`

## 📝 Structure du projet

```
ProjetSIEM/
├── serveur/
│   ├── app.py              # Serveur Flask principal
│   ├── database.py         # Gestion de la base SQLite
│   ├── analyse.py          # Module d'analyse et détection
│   ├── alerts.py           # Gestionnaire d'alertes
│   ├── config.py           # Configuration
│   ├── requirements.txt    # Dépendances serveur
│   └── siem_logs.db       # Base de données (créée automatiquement)
├── client/
│   ├── env_log.py          # Client simple
│   ├── client_advanced.py  # Client avancé pour tests
│   └── requirements.txt    # Dépendances client
├── start_server.sh         # Script de démarrage serveur (Linux/Ubuntu)
├── start_client.sh         # Script de démarrage client (Linux/Ubuntu)
├── start_server.bat        # Script de démarrage serveur (Windows)
├── start_client.bat        # Script de démarrage client (Windows)
├── test_system.py          # Script de test du système
├── .gitignore              # Fichiers à ignorer par Git
├── README.md               # Documentation principale
├── QUICKSTART.md           # Guide de démarrage rapide
├── DEMARRAGE_LOCAL.md      # Guide de démarrage local
└── INSTALL_UBUNTU.md       # Guide d'installation Ubuntu
```

## 🔒 Sécurité

⚠️ **Note** : Ce projet est conçu pour un environnement de test/développement. Pour la production, considérez :
- Authentification des clients
- Chiffrement des communications (HTTPS)
- Validation stricte des entrées
- Gestion des permissions

## 📚 Compétences démontrées

- SIEM simplifié
- Traitement de logs en temps réel
- Détection corrélée d'événements
- Analyse de patterns
- Stockage et requêtage de données
- API REST
- Architecture client-serveur

## 🐛 Dépannage

**Le client ne peut pas se connecter au serveur**
- Vérifier que le serveur est démarré
- Vérifier l'URL dans le fichier client
- Vérifier le firewall

**Aucune alerte n'est générée**
- Vérifier que les seuils dans `config.py` sont appropriés
- Vérifier que les logs sont bien reçus via `/stats`
- Déclencher une analyse manuelle via `/analyze`

## 📄 Licence

Projet éducatif - Fin d'année
