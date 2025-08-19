# Configuration principale
SYMBOL = "BTCUSDC"  # Symbole à monitorer (Futures: BTCUSDT, ETHUSDT, etc.)
TIMEFRAME = "5m"  # Timeframe (1m, 3m, 5m, 15m, 30m, 1h, etc.)

# Périodes RSI à calculer
RSI_PERIODS = [3, 5, 14, 21]

# NOUVEAU: Configuration EMA sur timeframe supérieur
EMA_HIGHER_TIMEFRAME = {
    "ENABLED": True,  # Activer/désactiver les EMA timeframe supérieur
    "PERIODS": [20, 50, 200],  # Périodes EMA à calculer
    "CUSTOM_TIMEFRAME": "1h",  # Forcer un timeframe spécifique (None = auto) ou mettre "1h", "4h", etc.
    "SAFETY_MARGIN": 50,  # Marge de sécurité en nombre de bougies (calcul dynamique)
    "AUTO_SUGGESTIONS": {  # Suggestions automatiques de timeframes
        "1m": "5m",
        "5m": "15m",
        "15m": "1h",
        "1h": "4h",
        "4h": "1d",
    },
}

# Configuration WebSocket - FUTURES USDⓈ-M
WEBSOCKET_URL = "wss://fstream.binance.com/ws/"

# Configuration de reconnexion automatique
RECONNECTION_CONFIG = {
    "ENABLED": True,  # Activer/désactiver la reconnexion automatique
    "MAX_ATTEMPTS": 10,  # Nombre maximum de tentatives de reconnexion
    "DELAY_SECONDS": 30,  # Délai entre les tentatives (en secondes)
    "TIMEOUT_SECONDS": 3600,  # Timeout pour considérer la connexion comme perdue
}

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

# Configuration ATR (Average True Range)
ATR_CONFIG = {
    "ENABLED": True,  # Activer/désactiver les calculs ATR
    "PERIODS": [14, 21],  # Périodes ATR à calculer
}

# Configuration analyse Volume
VOLUME_CONFIG = {
    "ENABLED": True,  # Activer/désactiver l'analyse de volume
    "LOOKBACK_PERIODS": [5, 10, 20],  # Périodes d'analyse des X dernières bougies
    "COMPARISON_PERIOD": 20,  # Période pour comparer avec moyenne historique
}

# Configuration détection de signaux de trading
SIGNAL_CONFIG = {
    "ENABLED": True,  # Activer/désactiver la détection de signaux
    "RSI_OVERSOLD": 30,  # Seuil RSI de survente pour signaux LONG
    "RSI_OVERBOUGHT": 70,  # Seuil RSI de surachat pour signaux SHORT
    "RSI_PERIOD": 5,  # Période RSI à utiliser pour les signaux
    "LOG_SIGNALS": True,  # Enregistrer les signaux dans des fichiers JSON
    "EMA_CURRENT_PERIOD": 50,  # Période EMA pour timeframe current
    "EMA_HIGHER_TIMEFRAME_PERIOD": 200,  # Période EMA pour timeframe supérieur
    "VOLUME_COMPARISON_PERIODS": 20,  # Périodes pour comparaison volume vs moyenne
}

# Symboles d'affichage
SYMBOLS = {
    "GREEN_CANDLE": "🟢",
    "RED_CANDLE": "🔴",
    "DOJI_CANDLE": "🟡",
    "HA_INDICATOR": "📊",
    "RSI_INDICATOR": "📈",
    "ATR_INDICATOR": "🌊",
    "VOLUME_INDICATOR": "📊",
    "SIGNAL_LONG": "🚀",
    "SIGNAL_SHORT": "📉",
    "SIGNAL_WAITING": "⏳",
    "SIGNAL_ALERT": "🚨",
    "SEPARATOR": "─" * 50,
}

# Configuration logging
LOG_CONFIG = {
    "ENABLE_FILE_LOG": False,
    "LOG_FILENAME": "monitor.log",
    "LOG_LEVEL": "INFO",
}
