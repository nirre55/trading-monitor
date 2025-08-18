"""
Analyses du Volume
"""
import pandas as pd
import numpy as np

class Volume:
    """Analyseur de volume avec moyennes et tendances"""
    
    @staticmethod
    def calculate_volume_moving_average(volume_series, period):
        """
        Calcule la moyenne mobile du volume
        
        Args:
            volume_series: Série des volumes
            period: Période de la moyenne
            
        Returns:
            Series: Moyenne mobile du volume
        """
        if len(volume_series) < period:
            return pd.Series([np.nan] * len(volume_series), index=volume_series.index)
        
        return volume_series.rolling(window=period).mean()
    
    @staticmethod
    def calculate_volume_ema(volume_series, period):
        """
        Calcule l'EMA du volume (pour cohérence avec les autres indicateurs)
        
        Args:
            volume_series: Série des volumes
            period: Période de l'EMA
            
        Returns:
            Series: EMA du volume
        """
        if len(volume_series) < period:
            return pd.Series([np.nan] * len(volume_series), index=volume_series.index)
        
        return volume_series.ewm(alpha=1/period, adjust=False).mean()
    
    @staticmethod
    def analyze_recent_volume(df, lookback_periods):
        """
        Analyse le volume sur les X dernières bougies
        
        Args:
            df: DataFrame avec colonnes volume, close, open
            lookback_periods: Nombre de bougies à analyser
            
        Returns:
            dict: Analyse complète du volume récent
        """
        if df.empty or len(df) < lookback_periods:
            return {
                'has_data': False,
                'message': f'Pas assez de données: {len(df)}/{lookback_periods}'
            }
        
        # Prendre les dernières bougies
        recent_df = df.tail(lookback_periods).copy()
        
        # Statistiques de base
        total_volume = recent_df['volume'].sum()
        avg_volume = recent_df['volume'].mean()
        max_volume = recent_df['volume'].max()
        min_volume = recent_df['volume'].min()
        
        # Volume par type de bougie (verte/rouge)
        recent_df['candle_type'] = np.where(
            recent_df['close'] > recent_df['open'], 'green', 
            np.where(recent_df['close'] < recent_df['open'], 'red', 'doji')
        )
        
        green_volume = recent_df[recent_df['candle_type'] == 'green']['volume'].sum()
        red_volume = recent_df[recent_df['candle_type'] == 'red']['volume'].sum()
        doji_volume = recent_df[recent_df['candle_type'] == 'doji']['volume'].sum()
        
        # Tendance du volume
        volume_trend = Volume._get_volume_trend(recent_df['volume'])
        
        # Volume ratio (haussier vs baissier)
        volume_ratio = Volume._calculate_volume_ratio(green_volume, red_volume)
        
        # Bougies à volume exceptionnel
        high_volume_candles = Volume._find_high_volume_candles(recent_df)
        
        return {
            'has_data': True,
            'lookback_periods': lookback_periods,
            'total_volume': total_volume,
            'avg_volume': avg_volume,
            'max_volume': max_volume,
            'min_volume': min_volume,
            'green_volume': green_volume,
            'red_volume': red_volume,
            'doji_volume': doji_volume,
            'volume_trend': volume_trend,
            'volume_ratio': volume_ratio,
            'high_volume_candles': high_volume_candles,
            'latest_volume': recent_df['volume'].iloc[-1],
            'latest_candle_type': recent_df['candle_type'].iloc[-1]
        }
    
    @staticmethod
    def compare_with_average(current_volume, volume_series, comparison_period=20):
        """
        Compare le volume actuel avec la moyenne historique
        
        Args:
            current_volume: Volume de la bougie actuelle
            volume_series: Série complète des volumes
            comparison_period: Période pour calculer la moyenne de comparaison
            
        Returns:
            dict: Comparaison avec moyennes
        """
        if len(volume_series) < comparison_period:
            return {
                'has_data': False,
                'message': f'Pas assez de données historiques: {len(volume_series)}/{comparison_period}'
            }
        
        # Calculer les moyennes de référence
        recent_avg = volume_series.tail(comparison_period).mean()
        overall_avg = volume_series.mean()
        
        # Calculer les ratios
        ratio_vs_recent = current_volume / recent_avg if recent_avg > 0 else 0
        ratio_vs_overall = current_volume / overall_avg if overall_avg > 0 else 0
        
        # Classification du volume
        volume_level = Volume._classify_volume_level(ratio_vs_recent)
        
        return {
            'has_data': True,
            'current_volume': current_volume,
            'recent_avg': recent_avg,
            'overall_avg': overall_avg,
            'ratio_vs_recent': ratio_vs_recent,
            'ratio_vs_overall': ratio_vs_overall,
            'volume_level': volume_level,
            'comparison_period': comparison_period
        }
    
    @staticmethod
    def _get_volume_trend(volume_series, lookback=5):
        """Détermine la tendance du volume"""
        if len(volume_series) < lookback:
            return 'N/A'
        
        # Comparer début et fin de période
        first_half = volume_series.iloc[:len(volume_series)//2].mean()
        second_half = volume_series.iloc[len(volume_series)//2:].mean()
        
        change_percent = ((second_half - first_half) / first_half) * 100 if first_half > 0 else 0
        
        if change_percent > 10:
            return 'increasing'
        elif change_percent < -10:
            return 'decreasing'
        else:
            return 'stable'
    
    @staticmethod
    def _calculate_volume_ratio(green_volume, red_volume):
        """Calcule le ratio volume haussier/baissier"""
        total_directional = green_volume + red_volume
        
        if total_directional == 0:
            return {
                'green_ratio': 0,
                'red_ratio': 0,
                'dominance': 'neutral'
            }
        
        green_ratio = (green_volume / total_directional) * 100
        red_ratio = (red_volume / total_directional) * 100
        
        # Déterminer la dominance
        if green_ratio > 60:
            dominance = 'bullish'
        elif red_ratio > 60:
            dominance = 'bearish'
        else:
            dominance = 'neutral'
        
        return {
            'green_ratio': green_ratio,
            'red_ratio': red_ratio,
            'dominance': dominance
        }
    
    @staticmethod
    def _find_high_volume_candles(df, threshold_multiplier=1.5):
        """Trouve les bougies à volume exceptionnel"""
        avg_volume = df['volume'].mean()
        threshold = avg_volume * threshold_multiplier
        
        high_volume_mask = df['volume'] > threshold
        high_volume_candles = df[high_volume_mask].copy()
        
        if not high_volume_candles.empty:
            high_volume_candles['volume_ratio'] = high_volume_candles['volume'] / avg_volume
            return {
                'count': len(high_volume_candles),
                'max_ratio': high_volume_candles['volume_ratio'].max(),
                'candle_types': high_volume_candles['candle_type'].value_counts().to_dict()
            }
        else:
            return {
                'count': 0,
                'max_ratio': 1.0,
                'candle_types': {}
            }
    
    @staticmethod
    def _classify_volume_level(ratio):
        """Classifie le niveau de volume"""
        if ratio >= 2.0:
            return 'very_high'
        elif ratio >= 1.5:
            return 'high'
        elif ratio >= 1.2:
            return 'above_average'
        elif ratio >= 0.8:
            return 'normal'
        elif ratio >= 0.5:
            return 'below_average'
        else:
            return 'very_low'
    
    @staticmethod
    def calculate_multiple_volume_analysis(df, lookback_periods_list, comparison_period=20):
        """
        Analyse le volume pour plusieurs périodes de lookback
        
        Args:
            df: DataFrame OHLC avec volume
            lookback_periods_list: Liste des périodes à analyser (ex: [5, 10, 20])
            comparison_period: Période pour comparaison historique
            
        Returns:
            dict: Analyses pour chaque période
        """
        results = {}
        
        for period in lookback_periods_list:
            analysis = Volume.analyze_recent_volume(df, period)
            results[f'volume_{period}'] = analysis
        
        # Ajouter la comparaison avec moyenne si on a des données
        if not df.empty and 'volume' in df.columns:
            latest_volume = df['volume'].iloc[-1]
            comparison = Volume.compare_with_average(
                latest_volume, df['volume'], comparison_period
            )
            results['volume_comparison'] = comparison
        
        return results