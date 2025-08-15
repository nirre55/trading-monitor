"""
Calculs de l'EMA (Exponential Moving Average)
"""
import pandas as pd
import numpy as np

class EMA:
    """Calculateur EMA avec support multi-timeframes"""
    
    @staticmethod
    def calculate(price_series, period, adjust=False):
        """
        Calcule l'EMA pour une série de prix
        
        Args:
            price_series: Série des prix (Series pandas)
            period: Période de l'EMA
            adjust: Utiliser l'ajustement pandas (False par défaut)
            
        Returns:
            Series: Valeurs EMA
        """
        if len(price_series) < period:
            # Pas assez de données - retourner série avec NaN
            return pd.Series([np.nan] * len(price_series), index=price_series.index)
        
        # Calculer EMA avec pandas
        ema = price_series.ewm(span=period, adjust=adjust).mean()
        return ema
    
    @staticmethod
    def calculate_multiple(price_series, periods, adjust=False):
        """
        Calcule l'EMA pour plusieurs périodes
        
        Args:
            price_series: Série des prix
            periods: Liste des périodes (ex: [20, 50, 200])
            adjust: Utiliser l'ajustement pandas
            
        Returns:
            dict: {f'EMA_{period}': Series} pour chaque période
        """
        ema_results = {}
        
        for period in periods:
            ema_values = EMA.calculate(price_series, period, adjust)
            ema_results[f'EMA_{period}'] = ema_values
        
        return ema_results
    
    @staticmethod
    def get_latest_values(ema_dict):
        """
        Extrait les dernières valeurs EMA
        
        Args:
            ema_dict: Dictionnaire des EMA calculées
            
        Returns:
            dict: {period: dernière_valeur} ou {period: None} si NaN
        """
        latest_values = {}
        
        for ema_name, ema_series in ema_dict.items():
            if ema_series.empty:
                latest_values[ema_name] = None
            else:
                latest_value = ema_series.iloc[-1]
                latest_values[ema_name] = latest_value if not np.isnan(latest_value) else None
        
        return latest_values
    
    @staticmethod
    def classify_price_vs_ema(current_price, ema_value):
        """
        Classe la position du prix par rapport à l'EMA
        
        Args:
            current_price: Prix actuel
            ema_value: Valeur EMA
            
        Returns:
            str: 'above', 'below', ou 'N/A'
        """
        if current_price is None or ema_value is None or np.isnan(ema_value):
            return 'N/A'
        
        if current_price > ema_value:
            return 'above'
        elif current_price < ema_value:
            return 'below'
        else:
            return 'equal'
    
    @staticmethod
    def get_ema_trend(ema_series, lookback=3):
        """
        Détermine la tendance de l'EMA
        
        Args:
            ema_series: Série EMA
            lookback: Nombre de périodes pour analyser la tendance
            
        Returns:
            str: 'rising', 'falling', 'sideways', ou 'N/A'
        """
        if len(ema_series) < lookback + 1:
            return 'N/A'
        
        # Prendre les dernières valeurs
        recent_values = ema_series.tail(lookback + 1)
        
        # Vérifier si toutes les valeurs sont valides
        if recent_values.isna().any():
            return 'N/A'
        
        # Comparer première et dernière valeur
        first_value = recent_values.iloc[0]
        last_value = recent_values.iloc[-1]
        
        # Calculer le pourcentage de changement
        change_percent = ((last_value - first_value) / first_value) * 100
        
        # Seuils pour déterminer la tendance
        rising_threshold = 0.05  # 0.05%
        falling_threshold = -0.05  # -0.05%
        
        if change_percent > rising_threshold:
            return 'rising'
        elif change_percent < falling_threshold:
            return 'falling'
        else:
            return 'sideways'