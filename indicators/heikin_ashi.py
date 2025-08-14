"""
Calculs des bougies Heikin Ashi
"""
import pandas as pd
import numpy as np

class HeikinAshi:
    """Calculateur des bougies Heikin Ashi"""
    
    @staticmethod
    def compute(df):
        """
        Calcule les valeurs Heikin Ashi pour un DataFrame
        
        Args:
            df: DataFrame avec colonnes 'open', 'high', 'low', 'close'
            
        Returns:
            DataFrame avec colonnes HA_open, HA_high, HA_low, HA_close
        """
        if df.empty:
            return df.copy()
        
        ha_df = df.copy()
        
        # HA Close = moyenne des 4 prix
        ha_df['HA_close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
        
        # HA Open - calculé séquentiellement
        ha_open = []
        
        # Premier HA Open = moyenne open et close
        first_ha_open = (df['open'].iloc[0] + df['close'].iloc[0]) / 2
        ha_open.append(first_ha_open)
        
        # HA Open suivants = moyenne du HA Open précédent et HA Close précédent
        for i in range(1, len(df)):
            prev_ha_open = ha_open[i - 1]
            prev_ha_close = ha_df['HA_close'].iloc[i - 1]
            current_ha_open = (prev_ha_open + prev_ha_close) / 2
            ha_open.append(current_ha_open)
        
        ha_df['HA_open'] = ha_open
        
        # HA High = maximum entre HA_open, HA_close et high original
        ha_df['HA_high'] = ha_df[['HA_open', 'HA_close', 'high']].max(axis=1)
        
        # HA Low = minimum entre HA_open, HA_close et low original
        ha_df['HA_low'] = ha_df[['HA_open', 'HA_close', 'low']].min(axis=1)
        
        return ha_df
    
    @staticmethod
    def get_candle_color(ha_open, ha_close):
        """
        Détermine la couleur d'une bougie Heikin Ashi
        
        Args:
            ha_open: Prix d'ouverture HA
            ha_close: Prix de clôture HA
            
        Returns:
            str: 'green', 'red', ou 'doji'
        """
        if ha_close > ha_open:
            return "green"
        elif ha_close < ha_open:
            return "red"
        else:
            return "doji"
    
    @staticmethod
    def get_latest_ha_candle(ha_df):
        """
        Retourne les données de la dernière bougie HA
        
        Args:
            ha_df: DataFrame avec colonnes HA calculées
            
        Returns:
            dict: Données de la dernière bougie HA
        """
        if ha_df.empty:
            return None
        
        latest = ha_df.iloc[-1]
        
        return {
            'open': latest['HA_open'],
            'high': latest['HA_high'],
            'low': latest['HA_low'],
            'close': latest['HA_close'],
            'color': HeikinAshi.get_candle_color(latest['HA_open'], latest['HA_close'])
        }
    
    @staticmethod
    def get_close_series(ha_df):
        """
        Retourne la série des prix de clôture HA
        
        Args:
            ha_df: DataFrame avec colonnes HA
            
        Returns:
            Series: Prix de clôture HA
        """
        if 'HA_close' not in ha_df.columns:
            return pd.Series()
        return ha_df['HA_close'].copy()