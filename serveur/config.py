"""
Configuration du serveur SIEM
"""
import os

# Configuration du serveur
SERVER_HOST = os.getenv('SIEM_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('SIEM_PORT', 5000))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Configuration de la base de données
DATABASE_PATH = os.getenv('DATABASE_PATH', 'siem_logs.db')

# Configuration de l'analyse
# Seuil pour détecter une répétition d'erreurs (nombre d'erreurs dans une fenêtre de temps)
ERROR_THRESHOLD = int(os.getenv('ERROR_THRESHOLD', 10))
ERROR_TIME_WINDOW = int(os.getenv('ERROR_TIME_WINDOW', 60))  # secondes

# Seuil pour détecter des connexions anormales
ABNORMAL_CONNECTION_THRESHOLD = int(os.getenv('ABNORMAL_CONNECTION_THRESHOLD', 5))
CONNECTION_TIME_WINDOW = int(os.getenv('CONNECTION_TIME_WINDOW', 300))  # secondes

# Seuil pour détecter des ressources système anormales
HIGH_CPU_THRESHOLD = float(os.getenv('HIGH_CPU_THRESHOLD', 90.0))
HIGH_MEMORY_THRESHOLD = float(os.getenv('HIGH_MEMORY_THRESHOLD', 90.0))
HIGH_DISK_THRESHOLD = float(os.getenv('HIGH_DISK_THRESHOLD', 90.0))

# Intervalle d'analyse (secondes)
ANALYSIS_INTERVAL = int(os.getenv('ANALYSIS_INTERVAL', 30))

