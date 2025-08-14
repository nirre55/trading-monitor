"""
Configuration du monitoring des bougies et indicateurs
"""

# Configuration principale
SYMBOL = "BTCUSDT"          # Symbole à monitorer
TIMEFRAME = "1m"            # Timeframe (1m, 3m, 5m, 15m, 30m, 1h, etc.)

# Périodes RSI à calculer
RSI_PERIODS = [14, 21]

# Configuration WebSocket
WEBSOCKET_URL = "wss://stream.binance.com:9443/ws/"

# Nombre de bougies historiques pour démarrage
INITIAL_KLINES_LIMIT = 100

# Configuration affichage
DISPLAY_CONFIG = {
    'SHOW_TIMESTAMP': True,
    'SHOW_PRICES': True,
    'SHOW_RSI_VALUES': True,
    'USE_COLORS': True,
    'COMPACT_MODE': False,
    'CLEAR_CONSOLE': False,  # Nettoyer console à chaque update
}

# Configuration des couleurs console
COLORS = {
    'GREEN': '\033[92m',     # Bougie verte
    'RED': '\033[91m',       # Bougie rouge
    'YELLOW': '\033[93m',    # Doji
    'CYAN': '\033[96m',      # Headers
    'WHITE': '\033[97m',     # Normal
    'RESET': '\033[0m',      # Reset couleur
    'BOLD': '\033[1m'        # Gras
}

# Symboles d'affichage
SYMBOLS = {
    'GREEN_CANDLE': '🟢',
    'RED_CANDLE': '🔴', 
    'DOJI_CANDLE': '🟡',
    'HA_INDICATOR': '📊',
    'RSI_INDICATOR': '📈',
    'SEPARATOR': '─' * 50
}

# Configuration logging
LOG_CONFIG = {
    'ENABLE_FILE_LOG': False,
    'LOG_FILENAME': 'monitor.log',
    'LOG_LEVEL': 'INFO'
}