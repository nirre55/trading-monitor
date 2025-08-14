
import pandas as pd
import numpy as np
from .heikin_ashi import HeikinAshi
from .rsi import RSI
from .ema import EMA
import config
import sys
import os

# Ajouter core au path pour import
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'core'))
from timeframe_manager import TimeframeManager

class IndicatorCalculator:
    """Orchestrateur des calculs d'indicateurs techniques"""
    
    def __init__(self):
        """Initialise le calculateur"""
        self.ha_calculator = HeikinAshi()
        self.rsi_calculator = RSI()
        self.ema_calculator = EMA()
        self.timeframe_manager = TimeframeManager()
        
        # Configuration EMA timeframe supérieur
        self.ema_enabled = getattr(config, 'EMA_HIGHER_TIMEFRAME', {}).get('ENABLED', False)
        if self.ema_enabled:
            self.higher_timeframe = None  # Sera calculé dynamiquement
            self.ema_periods = getattr(config, 'EMA_HIGHER_TIMEFRAME', {}).get('PERIODS', [20, 50])
            print(f"✅ EMA timeframe supérieur activé - Périodes: {self.ema_periods}")
    
    def _ensure_higher_timeframe_data(self, symbol, base_timeframe, current_candle_time):
        """S'assure que les données du timeframe supérieur sont disponibles"""
        if not self.ema_enabled:
            return None
        
        # Déterminer le timeframe supérieur si pas encore fait
        if not self.higher_timeframe:
            if hasattr(config, 'EMA_HIGHER_TIMEFRAME') and config.EMA_HIGHER_TIMEFRAME.get('CUSTOM_TIMEFRAME'):
                self.higher_timeframe = config.EMA_HIGHER_TIMEFRAME['CUSTOM_TIMEFRAME']
            else:
                self.higher_timeframe = self.timeframe_manager.get_suggested_higher_timeframe(base_timeframe)
            
            print(f"📊 Timeframe supérieur déterminé: {self.higher_timeframe} (base: {base_timeframe})")
        
        # Mettre à jour les données si nécessaire
        self.timeframe_manager.update_higher_timeframe_if_needed(
            symbol, 
            self.higher_timeframe, 
            current_candle_time
        )
        
        return self.higher_timeframe
    
    def calculate_all_indicators(self, df, symbol=None, base_timeframe=None):
        """
        Calcule tous les indicateurs pour le DataFrame
        
        Args:
            df: DataFrame avec données OHLC
            symbol: Symbole pour les données multi-timeframes (optionnel)
            base_timeframe: Timeframe de base pour calculer le timeframe supérieur (optionnel)
            
        Returns:
            dict: Résultats de tous les calculs
        """
        if df.empty:
            return {
                'normal_candle': None,
                'ha_candle': None,
                'normal_rsi': {},
                'ha_rsi': {},
                'higher_tf_ema': {},
                'has_data': False
            }
        
        # Vérifier qu'on a assez de données
        max_period = max(config.RSI_PERIODS) if config.RSI_PERIODS else 14
        min_data_needed = max_period + 5  # Marge de sécurité
        
        if len(df) < min_data_needed:
            return {
                'normal_candle': None,
                'ha_candle': None,
                'normal_rsi': {},
                'ha_rsi': {},
                'higher_tf_ema': {},
                'has_data': False,
                'message': f'Pas assez de données: {len(df)}/{min_data_needed}'
            }
        
        # 1. Calculer Heikin Ashi
        ha_df = self.ha_calculator.compute(df)
        
        # 2. Extraire les données de la dernière bougie normale
        normal_candle = self._get_normal_candle_data(df)
        
        # 3. Extraire les données de la dernière bougie HA
        ha_candle = self.ha_calculator.get_latest_ha_candle(ha_df)
        
        # 4. Calculer RSI sur bougies normales
        normal_close_series = df['close']
        normal_rsi_dict = self.rsi_calculator.calculate_multiple(
            normal_close_series, config.RSI_PERIODS
        )
        normal_rsi_latest = self.rsi_calculator.get_latest_values(normal_rsi_dict)
        
        # 5. Calculer RSI sur bougies HA
        ha_close_series = self.ha_calculator.get_close_series(ha_df)
        ha_rsi_dict = self.rsi_calculator.calculate_multiple(
            ha_close_series, config.RSI_PERIODS
        )
        ha_rsi_latest = self.rsi_calculator.get_latest_values(ha_rsi_dict)
        
        # 6. NOUVEAU: Calculer EMA sur timeframe supérieur
        higher_tf_ema = {}
        if self.ema_enabled and symbol and base_timeframe and normal_candle:
            try:
                higher_tf_ema = self._calculate_higher_timeframe_ema(
                    symbol, 
                    base_timeframe, 
                    normal_candle['open_time']
                )
            except Exception as e:
                print(f"⚠️ Erreur calcul EMA timeframe supérieur: {e}")
                higher_tf_ema = {}
        
        return {
            'normal_candle': normal_candle,
            'ha_candle': ha_candle,
            'normal_rsi': normal_rsi_latest,
            'ha_rsi': ha_rsi_latest,
            'higher_tf_ema': higher_tf_ema,
            'has_data': True,
            'data_points': len(df)
        }
    
    def _get_normal_candle_data(self, df):
        """
        Extrait les données de la dernière bougie normale
        
        Args:
            df: DataFrame avec données OHLC
            
        Returns:
            dict: Données de la bougie normale
        """
        if df.empty:
            return None
        
        latest = df.iloc[-1]
        
        # Déterminer la couleur
        if latest['close'] > latest['open']:
            color = "green"
        elif latest['close'] < latest['open']:
            color = "red"
        else:
            color = "doji"
        
        return {
            'open': latest['open'],
            'high': latest['high'],
            'low': latest['low'],
            'close': latest['close'],
            'color': color,
            'open_time': latest['open_time'] if 'open_time' in latest else None
        }
    
    def get_rsi_classifications(self, rsi_values, oversold=30, overbought=70):
        """
        Classe tous les RSI selon leurs niveaux
        
        Args:
            rsi_values: Dict des valeurs RSI
            oversold: Seuil de survente
            overbought: Seuil de surachat
            
        Returns:
            dict: Classifications pour chaque RSI
        """
        classifications = {}
        
        for rsi_name, rsi_value in rsi_values.items():
            classifications[rsi_name] = self.rsi_calculator.classify_rsi_level(
                rsi_value, oversold, overbought
            )
        
        return classifications
    
    def _calculate_higher_timeframe_ema(self, symbol, base_timeframe, current_candle_time):
        """
        Calcule les EMA sur le timeframe supérieur
        
        Args:
            symbol: Symbole
            base_timeframe: Timeframe de base
            current_candle_time: Timestamp de la bougie actuelle
            
        Returns:
            dict: Résultats EMA avec informations détaillées
        """
        # S'assurer que les données sont disponibles
        higher_tf = self._ensure_higher_timeframe_data(symbol, base_timeframe, current_candle_time)
        
        if not higher_tf:
            return {}
        
        # Récupérer la série de prix du timeframe supérieur
        close_series = self.timeframe_manager.get_timeframe_close_series(symbol, higher_tf)
        
        if close_series.empty:
            return {}
        
        # Calculer les EMA
        ema_dict = self.ema_calculator.calculate_multiple(close_series, self.ema_periods)
        ema_latest = self.ema_calculator.get_latest_values(ema_dict)
        
        # Récupérer la bougie correspondante du timeframe supérieur
        current_higher_candle = self.timeframe_manager.get_current_higher_timeframe_candle(
            symbol, higher_tf, current_candle_time
        )
        
        # Ajouter des informations contextuelles
        result = {
            'values': ema_latest,
            'timeframe': higher_tf,
            'current_candle': current_higher_candle,
            'price_vs_ema': {},
            'ema_trends': {}
        }
        
        # Analyser position prix vs EMA
        if current_higher_candle:
            current_price = current_higher_candle['close']
            for ema_name, ema_value in ema_latest.items():
                if ema_value is not None:
                    result['price_vs_ema'][ema_name] = self.ema_calculator.classify_price_vs_ema(
                        current_price, ema_value
                    )
        
        # Analyser tendances EMA
        for ema_name, ema_series in ema_dict.items():
            if not ema_series.empty:
                result['ema_trends'][ema_name] = self.ema_calculator.get_ema_trend(ema_series, 3)
        
        return result
    
    def get_ema_classifications(self, ema_data):
        """
        Classe les EMA selon leur position et tendance
        
        Args:
            ema_data: Données EMA du timeframe supérieur
            
        Returns:
            dict: Classifications détaillées
        """
        if not ema_data or 'values' not in ema_data:
            return {}
        
        classifications = {}
        
        for ema_name, ema_value in ema_data['values'].items():
            if ema_value is None:
                classifications[ema_name] = 'N/A'
                continue
            
            # Combiner position prix et tendance
            price_position = ema_data.get('price_vs_ema', {}).get(ema_name, 'N/A')
            trend = ema_data.get('ema_trends', {}).get(ema_name, 'N/A')
            
            if price_position == 'above' and trend == 'rising':
                classifications[ema_name] = 'bullish'
            elif price_position == 'below' and trend == 'falling':
                classifications[ema_name] = 'bearish'
            elif price_position == 'above' and trend == 'falling':
                classifications[ema_name] = 'resistance'
            elif price_position == 'below' and trend == 'rising':
                classifications[ema_name] = 'support'
            else:
                classifications[ema_name] = 'neutral'
        
        return classifications