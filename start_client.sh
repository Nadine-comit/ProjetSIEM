#!/bin/bash

echo "========================================"
echo "  DÉMARRAGE DU CLIENT SIEM"
echo "========================================"
echo ""

# Aller dans le dossier client
cd client || exit 1

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 n'est pas installé"
    echo "   Installez-le avec: sudo apt-get install python3 python3-pip"
    exit 1
fi

# Vérifier si les dépendances sont installées
if ! python3 -c "import requests" 2>/dev/null; then
    echo "📦 Installation des dépendances..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Erreur lors de l'installation des dépendances"
        exit 1
    fi
fi

echo ""
echo "📡 Démarrage du client..."
echo "   Le client enverra des logs au serveur"
echo "   Assurez-vous que le serveur est démarré sur http://localhost:5000"
echo "   Appuyez sur Ctrl+C pour arrêter"
echo ""
echo "========================================"
echo ""

# Démarrer le client
python3 client_advanced.py

