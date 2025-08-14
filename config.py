# Configuration principale
SYMBOL = "BTCUSDT"  # Symbole à monitorer
TIMEFRAME = "1m"  # Timeframe (1m, 3m, 5m, 15m, 30m, 1h, etc.)

# Périodes RSI à calculer
RSI_PERIODS = [14, 21]

# NOUVEAU: Configuration EMA sur timeframe supérieur
EMA_HIGHER_TIMEFRAME = {
    "ENABLED": True,  # Activer/désactiver les EMA timeframe supérieur
    "PERIODS": [20, 50, 200],  # Périodes EMA à calculer
    "CUSTOM_TIMEFRAME": "15m",  # Forcer un timeframe spécifique (None = auto) ou mettre "1h", "4h", etc.
    "AUTO_SUGGESTIONS": {  # Suggestions automatiques de timeframes
        "1m": "5m",
        "5m": "15m",
        "15m": "1h",
        "1h": "4h",
        "4h": "1d",
    },
}

# Configuration WebSocket
WEBSOCKET_URL = "wss://stream.binance.com:9443/ws/"

# Nombre de bougies historiques pour démarrage
INITIAL_KLINES_LIMIT = 500

# Configuration affichage
DISPLAY_CONFIG = {
    "SHOW_TIMESTAMP": True,
    "SHOW_PRICES": True,
    "SHOW_RSI_VALUES": True,
    "USE_COLORS": True,
    "COMPACT_MODE": False,
    "CLEAR_CONSOLE": False,  # Nettoyer console à chaque update
}

# Configuration des couleurs console
COLORS = {
    "GREEN": "\033[92m",  # Bougie verte
    "RED": "\033[91m",  # Bougie rouge
    "YELLOW": "\033[93m",  # Doji
    "CYAN": "\033[96m",  # Headers
    "WHITE": "\033[97m",  # Normal
    "RESET": "\033[0m",  # Reset couleur
    "BOLD": "\033[1m",  # Gras
}

# Symboles d'affichage
SYMBOLS = {
    "GREEN_CANDLE": "🟢",
    "RED_CANDLE": "🔴",
    "DOJI_CANDLE": "🟡",
    "HA_INDICATOR": "📊",
    "RSI_INDICATOR": "📈",
    "SEPARATOR": "─" * 50,
}

# Configuration logging
LOG_CONFIG = {
    "ENABLE_FILE_LOG": False,
    "LOG_FILENAME": "monitor.log",
    "LOG_LEVEL": "INFO",
}
