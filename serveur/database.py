"""
Gestion de la base de données SQLite pour stocker les logs
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import threading

class DatabaseManager:
    """Gestionnaire de base de données pour les logs SIEM"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialise les tables de la base de données"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Table principale des logs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    host TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    log_type TEXT NOT NULL,
                    severity TEXT,
                    message TEXT,
                    data TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des alertes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    host TEXT,
                    details TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    acknowledged INTEGER DEFAULT 0
                )
            ''')
            
            # Index pour améliorer les performances
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_host ON logs(host)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_log_type ON logs(log_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_severity ON logs(severity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alert_timestamp ON alerts(timestamp)')
            
            conn.commit()
            conn.close()
    
    def insert_log(self, log_data: Dict) -> int:
        """
        Insère un log dans la base de données
        
        Args:
            log_data: Dictionnaire contenant les données du log
            
        Returns:
            ID du log inséré
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Déterminer le type de log et la sévérité
            log_type = log_data.get('log_type', 'system')
            severity = log_data.get('severity', 'info')
            
            # Convertir les données supplémentaires en JSON
            data_json = json.dumps(log_data.get('data', {}))
            
            cursor.execute('''
                INSERT INTO logs (host, timestamp, log_type, severity, message, data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                log_data.get('host', 'unknown'),
                log_data.get('timestamp', datetime.now().isoformat()),
                log_type,
                severity,
                log_data.get('message', ''),
                data_json
            ))
            
            log_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return log_id
    
    def get_recent_logs(self, minutes: int = 60, host: Optional[str] = None) -> List[Dict]:
        """
        Récupère les logs récents
        
        Args:
            minutes: Nombre de minutes à remonter
            host: Filtrer par host (optionnel)
            
        Returns:
            Liste des logs
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = '''
                SELECT * FROM logs 
                WHERE datetime(timestamp) >= datetime('now', '-' || ? || ' minutes')
            '''
            params = [minutes]
            
            if host:
                query += ' AND host = ?'
                params.append(host)
            
            query += ' ORDER BY timestamp DESC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
    
    def get_error_logs(self, minutes: int = 60, host: Optional[str] = None) -> List[Dict]:
        """
        Récupère les logs d'erreur récents
        
        Args:
            minutes: Nombre de minutes à remonter
            host: Filtrer par host (optionnel)
            
        Returns:
            Liste des logs d'erreur
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = '''
                SELECT * FROM logs 
                WHERE datetime(timestamp) >= datetime('now', '-' || ? || ' minutes')
                AND severity IN ('error', 'critical', 'warning')
            '''
            params = [minutes]
            
            if host:
                query += ' AND host = ?'
                params.append(host)
            
            query += ' ORDER BY timestamp DESC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
    
    def get_connection_logs(self, minutes: int = 60, host: Optional[str] = None) -> List[Dict]:
        """
        Récupère les logs de connexion récents
        
        Args:
            minutes: Nombre de minutes à remonter
            host: Filtrer par host (optionnel)
            
        Returns:
            Liste des logs de connexion
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = '''
                SELECT * FROM logs 
                WHERE datetime(timestamp) >= datetime('now', '-' || ? || ' minutes')
                AND log_type = 'connection'
            '''
            params = [minutes]
            
            if host:
                query += ' AND host = ?'
                params.append(host)
            
            query += ' ORDER BY timestamp DESC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
    
    def count_logs_by_host(self, minutes: int, host: str) -> int:
        """
        Compte le nombre de logs d'un host dans une fenêtre de temps
        
        Args:
            minutes: Nombre de minutes à remonter
            host: Nom du host
            
        Returns:
            Nombre de logs
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM logs 
                WHERE datetime(timestamp) >= datetime('now', '-' || ? || ' minutes')
                AND host = ?
            ''', (minutes, host))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
    
    def insert_alert(self, alert_type: str, severity: str, message: str, 
                     host: Optional[str] = None, details: Optional[Dict] = None) -> int:
        """
        Insère une alerte dans la base de données
        
        Args:
            alert_type: Type d'alerte
            severity: Sévérité (low, medium, high, critical)
            message: Message de l'alerte
            host: Host concerné (optionnel)
            details: Détails supplémentaires (optionnel)
            
        Returns:
            ID de l'alerte insérée
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            details_json = json.dumps(details) if details else None
            
            cursor.execute('''
                INSERT INTO alerts (alert_type, severity, message, host, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (alert_type, severity, message, host, details_json))
            
            alert_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return alert_id
    
    def get_recent_alerts(self, limit: int = 50, acknowledged: bool = False) -> List[Dict]:
        """
        Récupère les alertes récentes
        
        Args:
            limit: Nombre maximum d'alertes à récupérer
            acknowledged: Inclure les alertes acquittées
            
        Returns:
            Liste des alertes
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = 'SELECT * FROM alerts WHERE acknowledged = ? ORDER BY timestamp DESC LIMIT ?'
            cursor.execute(query, (1 if acknowledged else 0, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]

