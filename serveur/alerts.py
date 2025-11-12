"""
Système de gestion des alertes SIEM
"""
import logging
import threading
import time
from datetime import datetime
from database import DatabaseManager
from analyse import SIEMAnalyzer
from config import ANALYSIS_INTERVAL

logger = logging.getLogger(__name__)

class AlertManager:
    """Gestionnaire d'alertes qui exécute l'analyse périodiquement"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.analyzer = SIEMAnalyzer(db)
        self.running = False
        self.thread = None
    
    def start(self):
        """Démarre le gestionnaire d'alertes en arrière-plan"""
        if self.running:
            logger.warning("Le gestionnaire d'alertes est déjà en cours d'exécution")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info(f"🚨 Gestionnaire d'alertes démarré (intervalle: {ANALYSIS_INTERVAL}s)")
    
    def stop(self):
        """Arrête le gestionnaire d'alertes"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Gestionnaire d'alertes arrêté")
    
    def _run_loop(self):
        """Boucle principale d'analyse"""
        while self.running:
            try:
                # Exécuter l'analyse
                alerts = self.analyzer.run_analysis()
                
                # Enregistrer les alertes dans la base de données
                for alert in alerts:
                    self.db.insert_alert(
                        alert_type=alert['type'],
                        severity=alert['severity'],
                        message=alert['message'],
                        host=alert.get('host'),
                        details=alert.get('details')
                    )
                
                # Attendre avant la prochaine analyse
                time.sleep(ANALYSIS_INTERVAL)
                
            except Exception as e:
                logger.error(f"Erreur dans la boucle d'analyse: {str(e)}")
                time.sleep(ANALYSIS_INTERVAL)
    
    def trigger_manual_analysis(self):
        """Déclenche une analyse manuelle"""
        try:
            alerts = self.analyzer.run_analysis()
            
            for alert in alerts:
                self.db.insert_alert(
                    alert_type=alert['type'],
                    severity=alert['severity'],
                    message=alert['message'],
                    host=alert.get('host'),
                    details=alert.get('details')
                )
            
            return alerts
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse manuelle: {str(e)}")
            return []

