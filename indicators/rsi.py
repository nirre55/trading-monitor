"""
Calculs du RSI (Relative Strength Index)
"""
import pandas as pd
import numpy as np

class RSI:
    """Calculateur RSI avec méthode EMA"""
    
    @staticmethod
    def calculate(price_series, period):
        """
        Calcule le RSI pour une série de prix
        
        Args:
            price_series: Série des prix (Series pandas)
            period: Période du RSI
            
        Returns:
            Series: Valeurs RSI
        """
        if len(price_series) < period + 1:
            # Pas assez de données
            return pd.Series([np.nan] * len(price_series), index=price_series.index)
        
        # Calculer les variations de prix
        delta = price_series.diff()
        
        # Séparer les gains et pertes
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        
        # Calculer les moyennes avec EMA (comme dans le projet original)
        avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
        
        # Calculer RS et RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_multiple(price_series, periods):
        """
        Calcule le RSI pour plusieurs périodes
        
        Args:
            price_series: Série des prix
            periods: Liste des périodes (ex: [14, 21])
            
        Returns:
            dict: {f'RSI_{period}': Series} pour chaque période
        """
        rsi_results = {}
        
        for period in periods:
            rsi_values = RSI.calculate(price_series, period)
            rsi_results[f'RSI_{period}'] = rsi_values
        
        return rsi_results
    
    @staticmethod
    def get_latest_values(rsi_dict):
        """
        Extrait les dernières valeurs RSI
        
        Args:
            rsi_dict: Dictionnaire des RSI calculés
            
        Returns:
            dict: {period: dernière_valeur} ou {period: None} si NaN
        """
        latest_values = {}
        
        for rsi_name, rsi_series in rsi_dict.items():
            if rsi_series.empty:
                latest_values[rsi_name] = None
            else:
                latest_value = rsi_series.iloc[-1]
                latest_values[rsi_name] = latest_value if not np.isnan(latest_value) else None
        
        return latest_values
    
    @staticmethod
    def classify_rsi_level(rsi_value, oversold=30, overbought=70):
        """
        Classe le niveau RSI
        
        Args:
            rsi_value: Valeur RSI
            oversold: Seuil de survente
            overbought: Seuil de surachat
            
        Returns:
            str: 'oversold', 'overbought', 'neutral', ou 'N/A'
        """
        if rsi_value is None or np.isnan(rsi_value):
            return 'N/A'
        
        if rsi_value <= oversold:
            return 'oversold'
        elif rsi_value >= overbought:
            return 'overbought'
        else:
            return 'neutral'