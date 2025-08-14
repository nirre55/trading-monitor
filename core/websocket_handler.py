"""
Gestionnaire WebSocket pour recevoir les données en temps réel
"""
import websocket
import json
import threading
import time
import config

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
    
    def create_websocket_url(self):
        """Crée l'URL WebSocket pour le stream de klines"""
        stream_name = f"{self.symbol}@kline_{self.timeframe}"
        return f"{config.WEBSOCKET_URL}{stream_name}"
    
    def on_message(self, ws, message):
        """Callback appelé à la réception d'un message"""
        try:
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
    
    def on_close(self, ws, close_status_code, close_msg):
        """Callback appelé à la fermeture"""
        print(f"🔌 Connexion WebSocket fermée (code: {close_status_code})")
        self.is_running = False
    
    def on_open(self, ws):
        """Callback appelé à l'ouverture"""
        print(f"🔌 Connexion WebSocket ouverte pour {self.symbol.upper()} {self.timeframe}")
        self.is_running = True
    
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