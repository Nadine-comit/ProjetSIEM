#!/usr/bin/env python
"""
Script de démarrage du serveur SIEM
Utilisation: python start_server.py
"""
import sys
import os

# Changer vers le répertoire serveur
os.chdir(os.path.join(os.path.dirname(__file__), 'serveur'))

# Importer et exécuter le serveur
if __name__ == '__main__':
    from app import app
    from config import SERVER_HOST, SERVER_PORT, DEBUG, ANALYSIS_INTERVAL
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("🚀 DÉMARRAGE DU SERVEUR SIEM")
    logger.info("=" * 60)
    logger.info(f"📡 Serveur: http://{SERVER_HOST}:{SERVER_PORT}")
    logger.info(f"📊 Base de données: siem_logs.db")
    logger.info(f"🔍 Analyse automatique: {ANALYSIS_INTERVAL}s")
    logger.info("=" * 60)
    
    try:
        app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG, threaded=True)
    except KeyboardInterrupt:
        logger.info("\n⏹️  Arrêt du serveur...")
        sys.exit(0)

