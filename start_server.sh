#!/bin/bash

echo "========================================"
echo "  DÉMARRAGE DU SERVEUR SIEM"
echo "========================================"
echo ""

# Aller dans le dossier serveur
cd serveur || exit 1

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 n'est pas installé"
    echo "   Installez-le avec: sudo apt-get install python3 python3-pip"
    exit 1
fi

# Vérifier si Flask est installé
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installation des dépendances..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Erreur lors de l'installation des dépendances"
        exit 1
    fi
fi

echo ""
echo "🚀 Démarrage du serveur..."
echo "   Le serveur sera accessible sur http://localhost:5000"
echo "   Appuyez sur Ctrl+C pour arrêter"
echo ""
echo "========================================"
echo ""

# Démarrer le serveur
python3 app.py

