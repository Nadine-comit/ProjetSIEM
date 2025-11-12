"""
Serveur SIEM - Point d'entrée pour recevoir les logs des clients
"""
from flask import Flask, request, jsonify
from datetime import datetime
import logging
from database import DatabaseManager
from alerts import AlertManager
from config import DATABASE_PATH, ANALYSIS_INTERVAL

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation de la base de données
db = DatabaseManager(DATABASE_PATH)

# Initialisation du gestionnaire d'alertes
alert_manager = AlertManager(db)
alert_manager.start()

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de vérification de santé du serveur"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/logs', methods=['POST'])
def receive_log():
    """
    Endpoint pour recevoir les logs des clients
    
    Format attendu:
    {
        "host": "nom_du_host",
        "timestamp": "2024-01-01T12:00:00",
        "log_type": "system|connection|error|security",
        "severity": "info|warning|error|critical",
        "message": "Description du log",
        "data": { ... }
    }
    """
    try:
        log_data = request.get_json()
        
        if not log_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validation des champs requis
        if 'host' not in log_data:
            log_data['host'] = request.remote_addr or 'unknown'
        
        if 'timestamp' not in log_data:
            log_data['timestamp'] = datetime.now().isoformat()
        
        # Déterminer le type de log si non spécifié
        if 'log_type' not in log_data:
            # Analyser les données pour déterminer le type
            if 'cpu_percent' in log_data or 'memory_percent' in log_data:
                log_data['log_type'] = 'system'
            elif 'connection' in str(log_data.get('message', '')).lower():
                log_data['log_type'] = 'connection'
            else:
                log_data['log_type'] = 'system'
        
        # Déterminer la sévérité si non spécifiée
        if 'severity' not in log_data:
            # Analyser les métriques système pour déterminer la sévérité
            cpu = log_data.get('cpu_percent', 0)
            memory = log_data.get('memory_percent', 0)
            disk = log_data.get('disk_percent', 0)
            
            if cpu > 90 or memory > 90 or disk > 90:
                log_data['severity'] = 'critical'
            elif cpu > 70 or memory > 70 or disk > 70:
                log_data['severity'] = 'warning'
            else:
                log_data['severity'] = 'info'
        
        # Créer le message si non présent
        if 'message' not in log_data:
            if log_data['log_type'] == 'system':
                log_data['message'] = f"System metrics - CPU: {log_data.get('cpu_percent', 0)}%, Memory: {log_data.get('memory_percent', 0)}%, Disk: {log_data.get('disk_percent', 0)}%"
            else:
                log_data['message'] = 'Log entry'
        
        # Extraire les données supplémentaires
        data_fields = ['cpu_percent', 'memory_percent', 'disk_percent', 'os', 'ip', 'port']
        log_data['data'] = {k: v for k, v in log_data.items() if k in data_fields}
        
        # Insérer le log dans la base de données
        log_id = db.insert_log(log_data)
        
        logger.info(f"Log reçu de {log_data['host']} - Type: {log_data['log_type']}, Sévérité: {log_data['severity']}")
        
        return jsonify({
            'status': 'success',
            'log_id': log_id,
            'message': 'Log received and stored'
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la réception du log: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    """
    Endpoint pour récupérer les logs
    
    Paramètres de requête:
    - minutes: Nombre de minutes à remonter (défaut: 60)
    - host: Filtrer par host (optionnel)
    - limit: Nombre maximum de logs (défaut: 100)
    """
    try:
        minutes = int(request.args.get('minutes', 60))
        host = request.args.get('host', None)
        limit = int(request.args.get('limit', 100))
        
        logs = db.get_recent_logs(minutes=minutes, host=host)
        
        # Limiter le nombre de résultats
        logs = logs[:limit]
        
        return jsonify({
            'status': 'success',
            'count': len(logs),
            'logs': logs
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des logs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/alerts', methods=['GET'])
def get_alerts():
    """
    Endpoint pour récupérer les alertes
    
    Paramètres de requête:
    - limit: Nombre maximum d'alertes (défaut: 50)
    - acknowledged: Inclure les alertes acquittées (défaut: false)
    """
    try:
        limit = int(request.args.get('limit', 50))
        acknowledged = request.args.get('acknowledged', 'false').lower() == 'true'
        
        alerts = db.get_recent_alerts(limit=limit, acknowledged=acknowledged)
        
        return jsonify({
            'status': 'success',
            'count': len(alerts),
            'alerts': alerts
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des alertes: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Endpoint pour récupérer les statistiques du système"""
    try:
        # Récupérer les statistiques récentes
        recent_logs = db.get_recent_logs(minutes=60)
        recent_alerts = db.get_recent_alerts(limit=100, acknowledged=False)
        
        # Compter par type
        log_types = {}
        severities = {}
        hosts = {}
        
        for log in recent_logs:
            log_type = log.get('log_type', 'unknown')
            severity = log.get('severity', 'unknown')
            host = log.get('host', 'unknown')
            
            log_types[log_type] = log_types.get(log_type, 0) + 1
            severities[severity] = severities.get(severity, 0) + 1
            hosts[host] = hosts.get(host, 0) + 1
        
        # Compter les alertes par sévérité
        alert_severities = {}
        for alert in recent_alerts:
            severity = alert.get('severity', 'unknown')
            alert_severities[severity] = alert_severities.get(severity, 0) + 1
        
        return jsonify({
            'status': 'success',
            'stats': {
                'total_logs_last_hour': len(recent_logs),
                'total_alerts': len(recent_alerts),
                'by_type': log_types,
                'by_severity': severities,
                'by_host': hosts,
                'alerts_by_severity': alert_severities
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def trigger_analysis():
    """Endpoint pour déclencher une analyse manuelle"""
    try:
        alerts = alert_manager.trigger_manual_analysis()
        
        return jsonify({
            'status': 'success',
            'message': f'Analyse terminée: {len(alerts)} alerte(s) générée(s)',
            'alerts_count': len(alerts)
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse manuelle: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    from config import SERVER_HOST, SERVER_PORT, DEBUG
    
    logger.info(f"🚀 Serveur SIEM démarré sur {SERVER_HOST}:{SERVER_PORT}")
    logger.info(f"📊 Base de données: {DATABASE_PATH}")
    logger.info(f"🔍 Analyse automatique activée (intervalle: {ANALYSIS_INTERVAL}s)")
    
    try:
        # Démarrer le serveur Flask
        app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG, threaded=True)
    except KeyboardInterrupt:
        logger.info("Arrêt du serveur...")
        alert_manager.stop()

