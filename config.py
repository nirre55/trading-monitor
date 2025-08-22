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
    # Configuration multi-RSI avec seuils différents par période
    "RSI_THRESHOLDS": {
        5: {"OVERSOLD": 10, "OVERBOUGHT": 90},  # RSI 5: plus sensible
        14: {"OVERSOLD": 20, "OVERBOUGHT": 80},  # RSI 14: standard
        21: {"OVERSOLD": 30, "OVERBOUGHT": 70},  # RSI 21: moins sensible
    },
    "RSI_SIGNAL_MODE": "ALL",  # "ANY" = au moins 1 RSI déclenche, "ALL" = tous les RSI doivent déclencher
    # Ancienne config (gardée pour compatibilité)
    "RSI_OVERSOLD": 30,  # DEPRECATED - utilisé comme fallback
    "RSI_OVERBOUGHT": 70,  # DEPRECATED - utilisé comme fallback
    "RSI_PERIOD": 21,  # DEPRECATED - utilisé comme fallback
    "LOG_SIGNALS": True,  # Enregistrer les signaux dans des fichiers JSON
    "EMA_CURRENT_PERIOD": 500,  # Période EMA pour timeframe current
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

# Configuration backtest
BACKTEST_CONFIG = {
    "ENABLED": True,  # Activer/désactiver les paramètres de backtest
    "RISK_PER_TRADE": 0.005,  # Risque par trade (0.02 = 2% du capital)
    # Méthode de calcul SL/TP: "ATR" ou "SWING_LEVELS"
    "SL_METHOD": "SWING_LEVELS",  # "ATR" ou "SWING_LEVELS"
    # Configuration ATR (si SL_METHOD = "ATR")
    "STOP_LOSS_ATR_MULTIPLIER": 1.0,  # SL = 1 x ATR
    "TAKE_PROFIT_ATR_MULTIPLIER": 1.0,  # TP = 1 x ATR
    "ATR_PERIOD_FOR_STOPS": 14,  # Période ATR à utiliser pour SL/TP (doit être dans ATR_CONFIG.PERIODS)
    # Configuration Swing Levels (si SL_METHOD = "SWING_LEVELS")
    "SWING_LOOKBACK_CANDLES": 5,  # Nombre de bougies précédentes à analyser
    "SWING_OFFSET_PCT": 0.01,  # Offset en % (0.1 = 0.1%)
    "SWING_TP_RATIO": 2.0,  # Multiplicateur pour TP (ex: 2 = TP à 2x la distance SL)
    # Configuration Take Profit : "RATIO" (basé sur SL), "FIXED_PCT" (% du prix d'entrée)
    "TP_METHOD": "FIXED_PCT",  # "RATIO" ou "FIXED_PCT"
    "FIXED_TP_PCT": 0.2,  # TP fixe en % (1.5 = 1.5% du prix d'entrée)
    # Paramètres communs
    "MIN_RISK_REWARD_RATIO": 0.05,  # Ratio risque/récompense minimum pour prendre un trade
    "MAX_POSITION_SIZE_PCT": 0.95,  # Taille de position maximale (95% du capital)
    "USE_TRAILING_STOP": False,  # Utiliser un trailing stop basé sur ATR
    "TRAILING_STOP_ATR_MULTIPLIER": 1.5,  # Multiplicateur ATR pour trailing stop
}
