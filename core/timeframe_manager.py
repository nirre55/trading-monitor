"""
Gestionnaire pour les données multi-timeframes
Permet de récupérer et synchroniser des données de différents timeframes
"""
import pandas as pd
from datetime import datetime, timedelta
from .binance_client import BinanceClient
from typing import Dict, Optional, Union, Any
import config

class TimeframeManager:
    """Gestionnaire des données multi-timeframes"""
    
    def __init__(self):
        """Initialise le gestionnaire"""
        self.binance_client = BinanceClient()
        self.timeframe_data = {}  # Cache des données par timeframe
        # Récupérer la marge de sécurité depuis la config ou utiliser 50 par défaut
        self.safety_margin = self._get_safety_margin_from_config()
        self.timeframe_hierarchy = {
            '1m': 1,
            '3m': 3,
            '5m': 5,
            '15m': 15,
            '30m': 30,
            '1h': 60,
            '2h': 120,
            '4h': 240,
            '6h': 360,
            '8h': 480,
            '12h': 720,
            '1d': 1440,
            '3d': 4320,
            '1w': 10080,
            '1M': 43200  # Approximation 30 jours
        }
    
    def get_higher_timeframe(self, base_timeframe, multiplier=4):
        """
        Détermine un timeframe supérieur basé sur le timeframe de base
        
        Args:
            base_timeframe: Timeframe de base (ex: '1m')
            multiplier: Multiplicateur pour calculer le timeframe supérieur
            
        Returns:
            str: Timeframe supérieur (ex: '5m' si base='1m' et multiplier=5)
        """
        if base_timeframe not in self.timeframe_hierarchy:
            return None
        
        base_minutes = self.timeframe_hierarchy[base_timeframe]
        target_minutes = base_minutes * multiplier
        
        # Trouver le timeframe le plus proche
        best_match = None
        min_diff = float('inf')
        
        for tf, minutes in self.timeframe_hierarchy.items():
            if minutes >= target_minutes:
                diff = abs(minutes - target_minutes)
                if diff < min_diff:
                    min_diff = diff
                    best_match = tf
        
        return best_match or '1h'  # Fallback sur 1h
    
    def get_suggested_higher_timeframe(self, base_timeframe):
        """
        Retourne un timeframe supérieur suggéré selon des règles prédéfinies
        
        Args:
            base_timeframe: Timeframe de base
            
        Returns:
            str: Timeframe supérieur suggéré
        """
        suggestions = {
            '1m': '5m',
            '3m': '15m',
            '5m': '30m',
            '15m': '1h',
            '30m': '4h',
            '1h': '4h',
            '2h': '12h',
            '4h': '1d',
            '6h': '1d',
            '8h': '1d',
            '12h': '1d',
            '1d': '1w',
            '3d': '1w',
            '1w': '1M'
        }
        
        return suggestions.get(base_timeframe, '1h')
    
    def load_timeframe_data(self, symbol, timeframe, limit=100):
        """
        Charge les données pour un timeframe spécifique
        
        Args:
            symbol: Symbole à charger
            timeframe: Timeframe des données
            limit: Nombre de bougies
            
        Returns:
            DataFrame ou None si erreur
        """
        print(f"📥 Chargement données {symbol} {timeframe} ({limit} bougies)...")
        
        df = self.binance_client.get_historical_klines(symbol, timeframe, limit)
        
        if df is not None and not df.empty:
            # Stocker dans le cache
            cache_key = f"{symbol}_{timeframe}"
            self.timeframe_data[cache_key] = df
            print(f"✅ Données {timeframe} chargées: {len(df)} bougies")
            return df
        else:
            print(f"❌ Échec chargement données {timeframe}")
            return None
    
    def get_current_higher_timeframe_candle(self, symbol, higher_timeframe, base_candle_time):
        """
        Récupère la dernière bougie fermée du timeframe supérieur avant ou au moment donné
        
        Args:
            symbol: Symbole
            higher_timeframe: Timeframe supérieur
            base_candle_time: Timestamp de la bougie de base
            
        Returns:
            dict: Données de la dernière bougie fermée ou None
        """
        cache_key = f"{symbol}_{higher_timeframe}"
        
        # Vérifier si on a les données en cache
        if cache_key not in self.timeframe_data:
            # Charger les données si pas en cache avec calcul dynamique
            required_candles = self.calculate_required_candles(higher_timeframe)
            self.load_timeframe_data(symbol, higher_timeframe, required_candles)
        
        if cache_key not in self.timeframe_data:
            return None
        
        df = self.timeframe_data[cache_key]
        if df.empty:
            return None
        
        # Trier par timestamp pour être sûr de l'ordre
        df_sorted = df.sort_values('close_time')
        
        # Trouver la dernière bougie fermée avant ou au moment donné
        # Une bougie est fermée si son close_time <= base_candle_time
        closed_candles = df_sorted[df_sorted['close_time'] <= base_candle_time]
        
        if not closed_candles.empty:
            # Prendre la dernière bougie fermée
            latest_closed = closed_candles.iloc[-1]
            return {
                'open_time': latest_closed['open_time'],
                'close_time': latest_closed['close_time'],
                'open': latest_closed['open'],
                'high': latest_closed['high'],
                'low': latest_closed['low'],
                'close': latest_closed['close'],
                'volume': latest_closed['volume']
            }
        else:
            # Aucune bougie fermée trouvée, prendre la première disponible
            # (cas où base_candle_time est antérieur à toutes les données)
            first_candle = df_sorted.iloc[0]
            return {
                'open_time': first_candle['open_time'],
                'close_time': first_candle['close_time'],
                'open': first_candle['open'],
                'high': first_candle['high'],
                'low': first_candle['low'],
                'close': first_candle['close'],
                'volume': first_candle['volume']
            }
    
    def get_timeframe_close_series(self, symbol, timeframe):
        """
        Retourne la série des prix de clôture pour un timeframe
        
        Args:
            symbol: Symbole
            timeframe: Timeframe
            
        Returns:
            Series: Prix de clôture ou série vide
        """
        cache_key = f"{symbol}_{timeframe}"
        
        if cache_key in self.timeframe_data:
            df = self.timeframe_data[cache_key]
            return df['close'].copy()
        else:
            return pd.Series()
    
    def update_higher_timeframe_if_needed(self, symbol, higher_timeframe, base_candle_time):
        """
        Met à jour les données du timeframe supérieur si nécessaire
        
        Args:
            symbol: Symbole
            higher_timeframe: Timeframe supérieur
            base_candle_time: Timestamp de référence
            
        Returns:
            bool: True si mis à jour
        """
        cache_key = f"{symbol}_{higher_timeframe}"
        
        # Vérifier si on a besoin de mettre à jour
        if cache_key not in self.timeframe_data:
            # Pas de données, charger avec calcul dynamique
            required_candles = self.calculate_required_candles(higher_timeframe)
            return self.load_timeframe_data(symbol, higher_timeframe, required_candles) is not None
        
        df = self.timeframe_data[cache_key]
        if df.empty:
            return False
        
        # Vérifier si les données sont assez récentes
        latest_close_time = df.iloc[-1]['close_time']
        
        # Si la dernière bougie est trop ancienne, recharger
        time_diff = base_candle_time - latest_close_time
        
        # Recharger si plus d'1 période du timeframe supérieur (plus strict)
        higher_tf_minutes = self.timeframe_hierarchy.get(higher_timeframe, 60)
        reload_threshold = timedelta(minutes=higher_tf_minutes)
        
        if time_diff > reload_threshold:
            print(f"🔄 Mise à jour données {higher_timeframe} (dernière: {latest_close_time}, actuel: {base_candle_time})")
            required_candles = self.calculate_required_candles(higher_timeframe)
            return self.load_timeframe_data(symbol, higher_timeframe, required_candles) is not None
        
        return True
    
    def get_cached_timeframes(self):
        """Retourne la liste des timeframes en cache"""
        return list(self.timeframe_data.keys())
    
    def clear_cache(self, symbol=None, timeframe=None):
        """
        Nettoie le cache
        
        Args:
            symbol: Symbole spécifique (optionnel)
            timeframe: Timeframe spécifique (optionnel)
        """
        if symbol and timeframe:
            cache_key = f"{symbol}_{timeframe}"
            if cache_key in self.timeframe_data:
                del self.timeframe_data[cache_key]
        elif symbol:
            # Nettoyer toutes les données du symbole
            keys_to_delete = [k for k in self.timeframe_data.keys() if k.startswith(f"{symbol}_")]
            for key in keys_to_delete:
                del self.timeframe_data[key]
        else:
            # Nettoyer tout le cache
            self.timeframe_data.clear()
        
        print(f"🧹 Cache nettoyé {'pour ' + symbol if symbol else 'complètement'}")
    
    def get_timeframe_minutes(self, timeframe):
        """Retourne le nombre de minutes pour un timeframe"""
        return self.timeframe_hierarchy.get(timeframe, 60)
    
    def calculate_required_candles(self, timeframe=None):
        """
        Calcule dynamiquement le nombre de bougies nécessaires
        en fonction des périodes EMA configurées
        
        Args:
            timeframe: Timeframe spécifique (optionnel)
            
        Returns:
            int: Nombre de bougies à charger
        """
        # Récupérer les périodes EMA configurées
        ema_periods = []
        if hasattr(config, 'EMA_HIGHER_TIMEFRAME') and config.EMA_HIGHER_TIMEFRAME.get('ENABLED', False):
            ema_periods = config.EMA_HIGHER_TIMEFRAME.get('PERIODS', [])
        
        # Récupérer aussi les périodes RSI pour comparaison
        rsi_periods = getattr(config, 'RSI_PERIODS', [])
        
        # Trouver la période maximale
        all_periods = ema_periods + rsi_periods
        max_period = max(all_periods) if all_periods else 50
        
        # Calculer le nombre de bougies nécessaires avec marge de sécurité
        required_candles = max_period + self.safety_margin
        
        # Minimum absolu
        min_candles = 100
        required_candles = max(required_candles, min_candles)
        
        print(f"📊 Calcul dynamique pour {timeframe or 'timeframe supérieur'}:")
        print(f"   - Périodes EMA: {ema_periods}")
        print(f"   - Périodes RSI: {rsi_periods}")
        print(f"   - Période max: {max_period}")
        print(f"   - Marge sécurité: {self.safety_margin}")
        print(f"   - Bougies à charger: {required_candles}")
        
        return required_candles
    
    def set_safety_margin(self, margin):
        """
        Configure la marge de sécurité
        
        Args:
            margin: Nombre de bougies de marge
        """
        self.safety_margin = max(10, margin)  # Minimum 10
        print(f"🔧 Marge de sécurité configurée: {self.safety_margin} bougies")
    
    def _get_safety_margin_from_config(self):
        """
        Récupère la marge de sécurité depuis la configuration
        
        Returns:
            int: Marge de sécurité configurée ou 50 par défaut
        """
        if hasattr(config, 'EMA_HIGHER_TIMEFRAME') and isinstance(config.EMA_HIGHER_TIMEFRAME, dict):
            margin = config.EMA_HIGHER_TIMEFRAME.get('SAFETY_MARGIN', 50)
            return max(10, margin)  # Minimum 10
        return 50  # Valeur par défaut