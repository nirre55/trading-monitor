"""
Calculs de l'ATR (Average True Range)
"""
import pandas as pd
import numpy as np

class ATR:
    """Calculateur ATR avec méthode EMA"""
    
    @staticmethod
    def calculate_true_range(df):
        """
        Calcule le True Range pour chaque bougie
        
        Args:
            df: DataFrame avec colonnes high, low, close
            
        Returns:
            Series: Valeurs True Range
        """
        if df.empty or len(df) < 2:
            return pd.Series([np.nan] * len(df), index=df.index)
        
        # True Range = max(high-low, abs(high-prev_close), abs(low-prev_close))
        high_low = df['high'] - df['low']
        high_close_prev = abs(df['high'] - df['close'].shift(1))
        low_close_prev = abs(df['low'] - df['close'].shift(1))
        
        true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
        
        return true_range
    
    @staticmethod
    def calculate(df, period):
        """
        Calcule l'ATR pour un DataFrame OHLC
        
        Args:
            df: DataFrame avec colonnes high, low, close
            period: Période de l'ATR
            
        Returns:
            Series: Valeurs ATR
        """
        if df.empty or len(df) < period + 1:
            return pd.Series([np.nan] * len(df), index=df.index)
        
        # Calculer le True Range
        true_range = ATR.calculate_true_range(df)
        
        # Calculer l'ATR avec EMA (comme les autres indicateurs du projet)
        atr = true_range.ewm(alpha=1/period, adjust=False).mean()
        
        return atr
    
    @staticmethod
    def calculate_multiple(df, periods):
        """
        Calcule l'ATR pour plusieurs périodes
        
        Args:
            df: DataFrame OHLC
            periods: Liste des périodes (ex: [14, 21])
            
        Returns:
            dict: {f'ATR_{period}': Series} pour chaque période
        """
        atr_results = {}
        
        for period in periods:
            atr_values = ATR.calculate(df, period)
            atr_results[f'ATR_{period}'] = atr_values
        
        return atr_results
    
    @staticmethod
    def get_latest_values(atr_dict):
        """
        Extrait les dernières valeurs ATR
        
        Args:
            atr_dict: Dictionnaire des ATR calculés
            
        Returns:
            dict: {period: dernière_valeur} ou {period: None} si NaN
        """
        latest_values = {}
        
        for atr_name, atr_series in atr_dict.items():
            if atr_series.empty:
                latest_values[atr_name] = None
            else:
                latest_value = atr_series.iloc[-1]
                latest_values[atr_name] = latest_value if not np.isnan(latest_value) else None
        
        return latest_values
    
    @staticmethod
    def classify_volatility(atr_value, atr_series, lookback=20):
        """
        Classe le niveau de volatilité basé sur l'ATR
        
        Args:
            atr_value: Valeur ATR actuelle
            atr_series: Série ATR pour comparaison
            lookback: Nombre de périodes pour calculer les percentiles
            
        Returns:
            str: 'low', 'normal', 'high', 'extreme', ou 'N/A'
        """
        if atr_value is None or np.isnan(atr_value) or atr_series.empty:
            return 'N/A'
        
        if len(atr_series) < lookback:
            return 'N/A'
        
        # Prendre les dernières valeurs pour calculer les percentiles
        recent_atr = atr_series.tail(lookback).dropna()
        
        if len(recent_atr) < lookback // 2:
            return 'N/A'
        
        # Calculer les percentiles
        p25 = recent_atr.quantile(0.25)
        p75 = recent_atr.quantile(0.75)
        p90 = recent_atr.quantile(0.90)
        
        # Classifier la volatilité
        if atr_value >= p90:
            return 'extreme'
        elif atr_value >= p75:
            return 'high'
        elif atr_value <= p25:
            return 'low'
        else:
            return 'normal'
    
    @staticmethod
    def get_atr_trend(atr_series, lookback=5):
        """
        Détermine la tendance de l'ATR (volatilité)
        
        Args:
            atr_series: Série ATR
            lookback: Nombre de périodes pour analyser la tendance
            
        Returns:
            str: 'increasing', 'decreasing', 'stable', ou 'N/A'
        """
        if len(atr_series) < lookback + 1:
            return 'N/A'
        
        # Prendre les dernières valeurs
        recent_values = atr_series.tail(lookback + 1).dropna()
        
        if len(recent_values) < lookback + 1:
            return 'N/A'
        
        # Comparer première et dernière valeur
        first_value = recent_values.iloc[0]
        last_value = recent_values.iloc[-1]
        
        # Calculer le pourcentage de changement
        change_percent = ((last_value - first_value) / first_value) * 100
        
        # Seuils pour déterminer la tendance
        increasing_threshold = 5.0  # 5%
        decreasing_threshold = -5.0  # -5%
        
        if change_percent > increasing_threshold:
            return 'increasing'
        elif change_percent < decreasing_threshold:
            return 'decreasing'
        else:
            return 'stable'