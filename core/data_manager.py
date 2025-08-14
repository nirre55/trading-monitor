"""
Gestionnaire des données OHLC et mise à jour du DataFrame
"""
import pandas as pd
from datetime import datetime
import config
from .binance_client import BinanceClient

class DataManager:
    """Gestionnaire des données de bougies"""
    
    def __init__(self):
        """Initialise le gestionnaire de données"""
        self.df = pd.DataFrame()
        self.binance_client = BinanceClient()
        self.last_candle_time = None
    
    def initialize_historical_data(self, symbol, timeframe, limit=None):
        """
        Charge les données historiques initiales
        
        Args:
            symbol: Symbole à charger
            timeframe: Timeframe des bougies
            limit: Nombre de bougies (défaut depuis config)
            
        Returns:
            bool: True si succès
        """
        if limit is None:
            limit = config.INITIAL_KLINES_LIMIT
        
        print(f"📥 Chargement données historiques {symbol} {timeframe}...")
        
        historical_data = self.binance_client.get_historical_klines(
            symbol, timeframe, limit
        )
        
        if historical_data is None or historical_data.empty:
            print("❌ Impossible de charger les données historiques")
            return False
        
        self.df = historical_data
        print(f"✅ {len(self.df)} bougies historiques chargées")
        return True
    
    def update_with_kline(self, kline_data):
        """
        Met à jour le DataFrame avec une nouvelle bougie
        
        Args:
            kline_data: Données brutes WebSocket
            
        Returns:
            bool: True si bougie fermée (nouvelle donnée disponible)
        """
        if self.df.empty:
            print("⚠️ DataFrame non initialisé")
            return False
        
        # Formater les données
        formatted_data = self.binance_client.format_kline_data(kline_data)
        
        # Ne traiter que les bougies fermées
        if not formatted_data['is_closed']:
            return False
        
        # Éviter les doublons
        if self.last_candle_time == formatted_data['open_time']:
            return False
        
        self.last_candle_time = formatted_data['open_time']
        
        # Préparer nouvelle ligne
        new_row = {
            'open_time': formatted_data['open_time'],
            'close_time': formatted_data['close_time'],
            'open': formatted_data['open'],
            'high': formatted_data['high'],
            'low': formatted_data['low'],
            'close': formatted_data['close'],
            'volume': formatted_data['volume']
        }
        
        # Ajouter ou mettre à jour
        if self.df.empty:
            self.df = pd.DataFrame([new_row])
        else:
            last_open_time = self.df.iloc[-1]['open_time']
            if formatted_data['open_time'] > last_open_time:
                # Nouvelle bougie
                new_index = len(self.df)
                for col, value in new_row.items():
                    self.df.loc[new_index, col] = value
                
                # Limiter la taille du DataFrame
                if len(self.df) > config.INITIAL_KLINES_LIMIT:
                    self.df = self.df.tail(config.INITIAL_KLINES_LIMIT).reset_index(drop=True)
            else:
                # Mise à jour bougie existante
                last_index = self.df.index[-1]
                for col, value in new_row.items():
                    self.df.loc[last_index, col] = value
        
        return True
    
    def get_latest_candle(self):
        """
        Retourne les données de la dernière bougie
        
        Returns:
            dict: Données OHLC de la dernière bougie
        """
        if self.df.empty:
            return None
        
        latest = self.df.iloc[-1]
        return {
            'open_time': latest['open_time'],
            'open': latest['open'],
            'high': latest['high'],
            'low': latest['low'],
            'close': latest['close'],
            'volume': latest['volume']
        }
    
    def get_dataframe(self):
        """Retourne une copie du DataFrame complet"""
        return self.df.copy()
    
    def get_close_series(self):
        """Retourne la série des prix de clôture"""
        if self.df.empty:
            return pd.Series()
        return self.df['close'].copy()
    
    def has_enough_data(self, min_periods):
        """
        Vérifie si on a assez de données pour les calculs
        
        Args:
            min_periods: Nombre minimum de périodes requises
            
        Returns:
            bool: True si assez de données
        """
        return len(self.df) >= min_periods