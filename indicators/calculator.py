"""
Orchestrateur principal des calculs d'indicateurs
"""
import pandas as pd
import numpy as np
from .heikin_ashi import HeikinAshi
from .rsi import RSI
import config

class IndicatorCalculator:
    """Orchestrateur des calculs d'indicateurs techniques"""
    
    def __init__(self):
        """Initialise le calculateur"""
        self.ha_calculator = HeikinAshi()
        self.rsi_calculator = RSI()
    
    def calculate_all_indicators(self, df):
        """
        Calcule tous les indicateurs pour le DataFrame
        
        Args:
            df: DataFrame avec données OHLC
            
        Returns:
            dict: Résultats de tous les calculs
        """
        if df.empty:
            return {
                'normal_candle': None,
                'ha_candle': None,
                'normal_rsi': {},
                'ha_rsi': {},
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
        
        return {
            'normal_candle': normal_candle,
            'ha_candle': ha_candle,
            'normal_rsi': normal_rsi_latest,
            'ha_rsi': ha_rsi_latest,
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