"""
Module d'analyse et de corrélation d'événements réseau
Détecte les répétitions d'erreurs et les connexions anormales
"""
import logging
from datetime import datetime
from typing import Dict, List
from collections import defaultdict
from database import DatabaseManager
from config import (
    ERROR_THRESHOLD,
    ERROR_TIME_WINDOW,
    ABNORMAL_CONNECTION_THRESHOLD,
    CONNECTION_TIME_WINDOW,
    HIGH_CPU_THRESHOLD,
    HIGH_MEMORY_THRESHOLD,
    HIGH_DISK_THRESHOLD
)

logger = logging.getLogger(__name__)

class SIEMAnalyzer:
    """Analyseur SIEM pour détecter les anomalies et comportements suspects"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.alert_history = defaultdict(list)  # Historique des alertes par host
    
    def analyze_errors(self) -> List[Dict]:
        """
        Analyse les répétitions d'erreurs
        
        Returns:
            Liste des alertes générées
        """
        alerts = []
        
        try:
            # Récupérer les logs d'erreur récents
            error_logs = self.db.get_error_logs(minutes=ERROR_TIME_WINDOW // 60)
            
            # Grouper les erreurs par host
            errors_by_host = defaultdict(list)
            for log in error_logs:
                host = log.get('host', 'unknown')
                errors_by_host[host].append(log)
            
            # Analyser chaque host
            for host, errors in errors_by_host.items():
                error_count = len(errors)
                
                if error_count >= ERROR_THRESHOLD:
                    # Vérifier si on n'a pas déjà alerté récemment pour ce host
                    if not self._has_recent_alert(host, 'error_repetition', minutes=5):
                        alert = {
                            'type': 'error_repetition',
                            'severity': 'high',
                            'message': f"Répétition d'erreurs détectée sur {host}: {error_count} erreurs dans les {ERROR_TIME_WINDOW} dernières secondes",
                            'host': host,
                            'details': {
                                'error_count': error_count,
                                'time_window_seconds': ERROR_TIME_WINDOW,
                                'errors': errors[:10]  # Limiter à 10 erreurs pour les détails
                            }
                        }
                        alerts.append(alert)
                        logger.warning(f"⚠️ Alerte: {alert['message']}")
        
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des erreurs: {str(e)}")
        
        return alerts
    
    def analyze_connections(self) -> List[Dict]:
        """
        Analyse les connexions anormales
        
        Returns:
            Liste des alertes générées
        """
        alerts = []
        
        try:
            # Récupérer les logs de connexion récents
            connection_logs = self.db.get_connection_logs(minutes=CONNECTION_TIME_WINDOW // 60)
            
            # Grouper les connexions par host
            connections_by_host = defaultdict(list)
            for log in connection_logs:
                host = log.get('host', 'unknown')
                connections_by_host[host].append(log)
            
            # Analyser chaque host
            for host, connections in connections_by_host.items():
                connection_count = len(connections)
                
                if connection_count >= ABNORMAL_CONNECTION_THRESHOLD:
                    # Vérifier si on n'a pas déjà alerté récemment
                    if not self._has_recent_alert(host, 'abnormal_connections', minutes=5):
                        # Analyser les patterns de connexion
                        unique_sources = set()
                        for conn in connections:
                            data = conn.get('data', {})
                            if isinstance(data, str):
                                import json
                                try:
                                    data = json.loads(data)
                                except:
                                    data = {}
                            source = data.get('source_ip', 'unknown')
                            unique_sources.add(source)
                        
                        alert = {
                            'type': 'abnormal_connections',
                            'severity': 'medium',
                            'message': f"Connexions anormales détectées sur {host}: {connection_count} connexions depuis {len(unique_sources)} source(s) dans les {CONNECTION_TIME_WINDOW} dernières secondes",
                            'host': host,
                            'details': {
                                'connection_count': connection_count,
                                'unique_sources': len(unique_sources),
                                'time_window_seconds': CONNECTION_TIME_WINDOW,
                                'connections': connections[:10]
                            }
                        }
                        alerts.append(alert)
                        logger.warning(f"⚠️ Alerte: {alert['message']}")
        
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des connexions: {str(e)}")
        
        return alerts
    
    def analyze_system_resources(self) -> List[Dict]:
        """
        Analyse les ressources système pour détecter des anomalies
        
        Returns:
            Liste des alertes générées
        """
        alerts = []
        
        try:
            # Récupérer les logs système récents
            system_logs = self.db.get_recent_logs(minutes=5)
            
            # Grouper par host et analyser les métriques
            hosts_metrics = defaultdict(lambda: {'cpu': [], 'memory': [], 'disk': []})
            
            for log in system_logs:
                if log.get('log_type') == 'system':
                    host = log.get('host', 'unknown')
                    data = log.get('data', {})
                    
                    if isinstance(data, str):
                        import json
                        try:
                            data = json.loads(data)
                        except:
                            data = {}
                    
                    if 'cpu_percent' in data:
                        hosts_metrics[host]['cpu'].append(data['cpu_percent'])
                    if 'memory_percent' in data:
                        hosts_metrics[host]['memory'].append(data['memory_percent'])
                    if 'disk_percent' in data:
                        hosts_metrics[host]['disk'].append(data['disk_percent'])
            
            # Analyser chaque host
            for host, metrics in hosts_metrics.items():
                # CPU élevé
                if metrics['cpu']:
                    avg_cpu = sum(metrics['cpu']) / len(metrics['cpu'])
                    max_cpu = max(metrics['cpu'])
                    
                    if max_cpu >= HIGH_CPU_THRESHOLD:
                        if not self._has_recent_alert(host, 'high_cpu', minutes=10):
                            alert = {
                                'type': 'high_cpu',
                                'severity': 'warning' if avg_cpu < HIGH_CPU_THRESHOLD else 'high',
                                'message': f"CPU élevé sur {host}: {max_cpu:.1f}% (moyenne: {avg_cpu:.1f}%)",
                                'host': host,
                                'details': {
                                    'max_cpu': max_cpu,
                                    'avg_cpu': avg_cpu,
                                    'threshold': HIGH_CPU_THRESHOLD
                                }
                            }
                            alerts.append(alert)
                            logger.warning(f"⚠️ Alerte: {alert['message']}")
                
                # Mémoire élevée
                if metrics['memory']:
                    avg_memory = sum(metrics['memory']) / len(metrics['memory'])
                    max_memory = max(metrics['memory'])
                    
                    if max_memory >= HIGH_MEMORY_THRESHOLD:
                        if not self._has_recent_alert(host, 'high_memory', minutes=10):
                            alert = {
                                'type': 'high_memory',
                                'severity': 'warning' if avg_memory < HIGH_MEMORY_THRESHOLD else 'high',
                                'message': f"Mémoire élevée sur {host}: {max_memory:.1f}% (moyenne: {avg_memory:.1f}%)",
                                'host': host,
                                'details': {
                                    'max_memory': max_memory,
                                    'avg_memory': avg_memory,
                                    'threshold': HIGH_MEMORY_THRESHOLD
                                }
                            }
                            alerts.append(alert)
                            logger.warning(f"⚠️ Alerte: {alert['message']}")
                
                # Disque élevé
                if metrics['disk']:
                    avg_disk = sum(metrics['disk']) / len(metrics['disk'])
                    max_disk = max(metrics['disk'])
                    
                    if max_disk >= HIGH_DISK_THRESHOLD:
                        if not self._has_recent_alert(host, 'high_disk', minutes=10):
                            alert = {
                                'type': 'high_disk',
                                'severity': 'warning' if avg_disk < HIGH_DISK_THRESHOLD else 'high',
                                'message': f"Disque presque plein sur {host}: {max_disk:.1f}% (moyenne: {avg_disk:.1f}%)",
                                'host': host,
                                'details': {
                                    'max_disk': max_disk,
                                    'avg_disk': avg_disk,
                                    'threshold': HIGH_DISK_THRESHOLD
                                }
                            }
                            alerts.append(alert)
                            logger.warning(f"⚠️ Alerte: {alert['message']}")
        
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des ressources système: {str(e)}")
        
        return alerts
    
    def analyze_correlated_events(self) -> List[Dict]:
        """
        Analyse les événements corrélés (plusieurs types d'anomalies simultanées)
        
        Returns:
            Liste des alertes générées
        """
        alerts = []
        
        try:
            # Récupérer les logs récents
            recent_logs = self.db.get_recent_logs(minutes=5)
            
            # Grouper par host
            hosts_events = defaultdict(lambda: {
                'errors': 0,
                'warnings': 0,
                'high_cpu': False,
                'high_memory': False,
                'connections': 0
            })
            
            for log in recent_logs:
                host = log.get('host', 'unknown')
                severity = log.get('severity', 'info')
                log_type = log.get('log_type', 'system')
                
                if severity == 'error' or severity == 'critical':
                    hosts_events[host]['errors'] += 1
                elif severity == 'warning':
                    hosts_events[host]['warnings'] += 1
                
                if log_type == 'connection':
                    hosts_events[host]['connections'] += 1
                
                # Vérifier les ressources
                data = log.get('data', {})
                if isinstance(data, str):
                    import json
                    try:
                        data = json.loads(data)
                    except:
                        data = {}
                
                if data.get('cpu_percent', 0) > HIGH_CPU_THRESHOLD:
                    hosts_events[host]['high_cpu'] = True
                if data.get('memory_percent', 0) > HIGH_MEMORY_THRESHOLD:
                    hosts_events[host]['high_memory'] = True
            
            # Détecter les corrélations suspectes
            for host, events in hosts_events.items():
                suspicious_score = 0
                issues = []
                
                if events['errors'] > 5:
                    suspicious_score += 2
                    issues.append(f"{events['errors']} erreurs")
                
                if events['warnings'] > 10:
                    suspicious_score += 1
                    issues.append(f"{events['warnings']} avertissements")
                
                if events['high_cpu']:
                    suspicious_score += 1
                    issues.append("CPU élevé")
                
                if events['high_memory']:
                    suspicious_score += 1
                    issues.append("Mémoire élevée")
                
                if events['connections'] > 10:
                    suspicious_score += 1
                    issues.append(f"{events['connections']} connexions")
                
                # Si le score est élevé, générer une alerte
                if suspicious_score >= 3:
                    if not self._has_recent_alert(host, 'correlated_events', minutes=10):
                        alert = {
                            'type': 'correlated_events',
                            'severity': 'critical' if suspicious_score >= 4 else 'high',
                            'message': f"Événements corrélés suspects sur {host}: {', '.join(issues)}",
                            'host': host,
                            'details': {
                                'suspicious_score': suspicious_score,
                                'events': events
                            }
                        }
                        alerts.append(alert)
                        logger.critical(f"🚨 Alerte critique: {alert['message']}")
        
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des événements corrélés: {str(e)}")
        
        return alerts
    
    def _has_recent_alert(self, host: str, alert_type: str, minutes: int = 5) -> bool:
        """
        Vérifie si une alerte similaire a été générée récemment
        
        Args:
            host: Nom du host
            alert_type: Type d'alerte
            minutes: Fenêtre de temps en minutes
            
        Returns:
            True si une alerte récente existe
        """
        key = f"{host}_{alert_type}"
        now = datetime.now()
        
        # Nettoyer l'historique ancien
        self.alert_history[key] = [
            timestamp for timestamp in self.alert_history[key]
            if (now - timestamp).total_seconds() < minutes * 60
        ]
        
        return len(self.alert_history[key]) > 0
    
    def run_analysis(self) -> List[Dict]:
        """
        Exécute toutes les analyses et retourne toutes les alertes
        
        Returns:
            Liste de toutes les alertes générées
        """
        all_alerts = []
        
        logger.info("🔍 Démarrage de l'analyse SIEM...")
        
        # Analyser les erreurs
        alerts = self.analyze_errors()
        all_alerts.extend(alerts)
        
        # Analyser les connexions
        alerts = self.analyze_connections()
        all_alerts.extend(alerts)
        
        # Analyser les ressources système
        alerts = self.analyze_system_resources()
        all_alerts.extend(alerts)
        
        # Analyser les événements corrélés
        alerts = self.analyze_correlated_events()
        all_alerts.extend(alerts)
        
        logger.info(f"✅ Analyse terminée: {len(all_alerts)} alerte(s) générée(s)")
        
        return all_alerts

