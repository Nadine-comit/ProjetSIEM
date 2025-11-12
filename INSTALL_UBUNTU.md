# Installation et démarrage sur Ubuntu

## 📋 Prérequis

```bash
# Mettre à jour le système
sudo apt-get update

# Installer Python3 et pip
sudo apt-get install -y python3 python3-pip python3-venv
```

## 🚀 Démarrage rapide

### Option 1 : Scripts automatiques (recommandé)

**Terminal 1 - Serveur:**
```bash
./start_server.sh
```

**Terminal 2 - Client:**
```bash
./start_client.sh
```

Si les scripts ne sont pas exécutables :
```bash
chmod +x start_server.sh start_client.sh
```

### Option 2 : Installation manuelle

**1. Installer les dépendances du serveur:**
```bash
cd serveur
pip3 install -r requirements.txt
python3 app.py
```

**2. Installer les dépendances du client (dans un autre terminal):**
```bash
cd client
pip3 install -r requirements.txt
python3 client_advanced.py
```

## 🔧 Utilisation avec environnement virtuel (recommandé)

### Serveur

```bash
cd serveur
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Client

```bash
cd client
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python client_advanced.py
```

## 🌐 Configuration réseau

Si vous voulez accéder au serveur depuis d'autres machines sur le réseau :

1. Modifiez `serveur/config.py` :
```python
SERVER_HOST = '0.0.0.0'  # Écoute sur toutes les interfaces
```

2. Trouvez l'IP de votre machine :
```bash
hostname -I
# ou
ip addr show
```

3. Modifiez l'URL dans le client :
```python
SERVER_URL = "http://VOTRE_IP:5000/logs"
```

## 🔥 Configuration du firewall (si nécessaire)

```bash
# Autoriser le port 5000
sudo ufw allow 5000/tcp
sudo ufw reload
```

## ✅ Vérification

Une fois le serveur démarré, testez avec :

```bash
# Vérifier la santé
curl http://localhost:5000/health

# Voir les statistiques
curl http://localhost:5000/stats

# Voir les alertes
curl http://localhost:5000/alerts
```

## 🐛 Dépannage

### Port 5000 déjà utilisé

```bash
# Trouver le processus qui utilise le port
sudo lsof -i :5000

# Ou
sudo netstat -tulpn | grep 5000

# Tuer le processus si nécessaire
sudo kill -9 <PID>
```

### Erreur de permissions

```bash
# Rendre les scripts exécutables
chmod +x start_server.sh start_client.sh
```

### Module non trouvé

```bash
# Réinstaller les dépendances
pip3 install --upgrade -r requirements.txt
```

## 📊 Service systemd (démarrage automatique)

Pour démarrer le serveur automatiquement au boot, créez un service :

```bash
sudo nano /etc/systemd/system/siem-server.service
```

Contenu :
```ini
[Unit]
Description=SIEM Server
After=network.target

[Service]
Type=simple
User=votre_utilisateur
WorkingDirectory=/chemin/vers/ProjetSIEM/serveur
ExecStart=/usr/bin/python3 /chemin/vers/ProjetSIEM/serveur/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Activer le service :
```bash
sudo systemctl daemon-reload
sudo systemctl enable siem-server
sudo systemctl start siem-server
sudo systemctl status siem-server
```

