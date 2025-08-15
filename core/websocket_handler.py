"""
Gestionnaire WebSocket pour recevoir les données en temps réel
"""
import websocket
import json
import threading
import time
import config
from datetime import datetime, timedelta

class WebSocketHandler:
    """Gestionnaire des connexions WebSocket Binance"""
    
    def __init__(self, symbol, timeframe, on_kline_callback):
        """
        Initialise le gestionnaire WebSocket
        
        Args:
            symbol: Symbole à écouter
            timeframe: Timeframe des bougies
            on_kline_callback: Fonction appelée à chaque nouvelle donnée
        """
        self.symbol = symbol.lower()
        self.timeframe = timeframe
        self.on_kline_callback = on_kline_callback
        self.ws = None
        self.is_running = False
        self.ws_thread = None
        
        # Gestion des reconnexions depuis la configuration
        reconnect_config = getattr(config, 'RECONNECTION_CONFIG', {})
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = reconnect_config.get('MAX_ATTEMPTS', 10)
        self.reconnect_delay = reconnect_config.get('DELAY_SECONDS', 5)
        self.last_message_time = None
        self.connection_timeout = reconnect_config.get('TIMEOUT_SECONDS', 60)
        self.should_reconnect = reconnect_config.get('ENABLED', True)
    
    def create_websocket_url(self):
        """Crée l'URL WebSocket pour le stream de klines"""
        stream_name = f"{self.symbol}@kline_{self.timeframe}"
        return f"{config.WEBSOCKET_URL}{stream_name}"
    
    def on_message(self, ws, message):
        """Callback appelé à la réception d'un message"""
        try:
            # Marquer que la connexion est active
            self.last_message_time = datetime.now()
            self.is_connected = True
            self.reconnect_attempts = 0  # Reset le compteur si message reçu
            
            data = json.loads(message)
            if 'k' in data:
                kline_data = data['k']
                self.on_kline_callback(kline_data)
        except json.JSONDecodeError as e:
            print(f"❌ Erreur décodage JSON: {e}")
        except Exception as e:
            print(f"❌ Erreur traitement message: {e}")
    
    def on_error(self, ws, error):
        """Callback appelé en cas d'erreur"""
        print(f"❌ Erreur WebSocket: {error}")
        self.is_connected = False
        
        # Déclencher une reconnexion si l'erreur est grave
        if self.should_reconnect and self.reconnect_attempts < self.max_reconnect_attempts:
            print(f"🔄 Tentative de reconnexion dans {self.reconnect_delay} secondes...")
            threading.Timer(self.reconnect_delay, self._attempt_reconnect).start()
    
    def on_close(self, ws, close_status_code, close_msg):
        """Callback appelé à la fermeture"""
        print(f"🔌 Connexion WebSocket fermée (code: {close_status_code})")
        self.is_running = False
        self.is_connected = False
        
        # Tentative de reconnexion si pas un arrêt volontaire
        if self.should_reconnect and self.reconnect_attempts < self.max_reconnect_attempts:
            print(f"🔄 Reconnexion automatique dans {self.reconnect_delay} secondes...")
            threading.Timer(self.reconnect_delay, self._attempt_reconnect).start()
    
    def on_open(self, ws):
        """Callback appelé à l'ouverture"""
        print(f"🔌 Connexion WebSocket ouverte pour {self.symbol.upper()} {self.timeframe}")
        self.is_running = True
        self.is_connected = True
        self.last_message_time = datetime.now()
        self.reconnect_attempts = 0
    
    def start(self):
        """Démarre la connexion WebSocket"""
        url = self.create_websocket_url()
        print(f"🔗 Connexion à: {url}")
        
        self.ws = websocket.WebSocketApp(
            url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        
        # Démarrer dans un thread séparé
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()
    
    def stop(self):
        """Arrête la connexion WebSocket"""
        print("🛑 Arrêt WebSocket...")
        self.is_running = False
        
        if self.ws:
            self.ws.close()
        
        if self.ws_thread and self.ws_thread.is_alive():
            self.ws_thread.join(timeout=5)
    
    def wait_for_connection(self, timeout=10):
        """Attend que la connexion soit établie"""
        start_time = time.time()
        while not self.is_running and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        return self.is_running
    
    def _attempt_reconnect(self):
        """Tente une reconnexion"""
        if not self.should_reconnect:
            return
            
        self.reconnect_attempts += 1
        print(f"🔄 Tentative de reconnexion #{self.reconnect_attempts}/{self.max_reconnect_attempts}")
        
        try:
            # Fermer l'ancienne connexion si elle existe
            if self.ws:
                self.ws.close()
            
            # Attendre un peu avant de reconnecter
            time.sleep(1)
            
            # Redémarrer la connexion
            self.start()
            
        except Exception as e:
            print(f"❌ Échec de reconnexion: {e}")
            
            # Si on n'a pas atteint le maximum, programmer une nouvelle tentative
            if self.reconnect_attempts < self.max_reconnect_attempts:
                delay = min(self.reconnect_delay * self.reconnect_attempts, 60)  # Max 60s
                print(f"🔄 Nouvelle tentative dans {delay} secondes...")
                threading.Timer(delay, self._attempt_reconnect).start()
            else:
                print(f"❌ Échec définitif après {self.max_reconnect_attempts} tentatives")
                self.should_reconnect = False
    
    def check_connection_health(self):
        """Vérifie l'état de santé de la connexion"""
        if not self.is_connected or not self.last_message_time:
            return False
        
        # Vérifier si on a reçu un message récemment
        time_since_last_message = datetime.now() - self.last_message_time
        
        if time_since_last_message.total_seconds() > self.connection_timeout:
            print(f"⚠️ Aucun message depuis {time_since_last_message.total_seconds():.0f}s - Connexion potentiellement perdue")
            self.is_connected = False
            
            # Déclencher une reconnexion
            if self.should_reconnect:
                print("🔄 Déclenchement d'une reconnexion préventive...")
                threading.Timer(1, self._attempt_reconnect).start()
            
            return False
        
        return True
    
    def start_health_monitor(self):
        """Démarre le monitoring de santé de la connexion"""
        def monitor():
            while self.should_reconnect:
                time.sleep(30)  # Vérifier toutes les 30 secondes
                if self.is_running:
                    self.check_connection_health()
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def get_connection_status(self):
        """Retourne le statut détaillé de la connexion"""
        status = {
            'is_running': self.is_running,
            'is_connected': self.is_connected,
            'reconnect_attempts': self.reconnect_attempts,
            'last_message_time': self.last_message_time,
            'should_reconnect': self.should_reconnect
        }
        
        if self.last_message_time:
            time_since_last = datetime.now() - self.last_message_time
            status['seconds_since_last_message'] = time_since_last.total_seconds()
        
        return status