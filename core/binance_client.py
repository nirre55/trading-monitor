"""
Client pour récupérer les données historiques de Binance
"""
import requests
import pandas as pd
from datetime import datetime
import config

class BinanceClient:
    """Client pour interaction avec l'API publique Binance"""
    
    def __init__(self):
        self.base_url = "https://fapi.binance.com"  # API Futures USDⓈ-M
    
    def get_historical_klines(self, symbol, interval, limit=100):
        """
        Récupère les données historiques de bougies
        
        Args:
            symbol: Symbole trading (ex: BTCUSDT)
            interval: Intervalle (1m, 5m, 1h, etc.)
            limit: Nombre de bougies
            
        Returns:
            DataFrame avec colonnes: open_time, open, high, low, close, volume
        """
        try:
            endpoint = f"{self.base_url}/fapi/v1/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit + 1  # +1 pour avoir la bougie en cours
            }
            
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Convertir en DataFrame
            df = pd.DataFrame(data, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Convertir les types
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            # Convertir les timestamps
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            
            # Garder seulement les colonnes nécessaires
            df = df[['open_time', 'close_time', 'open', 'high', 'low', 'close', 'volume']]
            
            # Supprimer la dernière bougie (en cours)
            df = df[:-1].copy()
            
            print(f"✅ Récupéré {len(df)} bougies historiques pour {symbol}")
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {e}")
            return None
        except Exception as e:
            print(f"❌ Erreur traitement données: {e}")
            return None
    
    def format_kline_data(self, kline_data):
        """
        Formate les données WebSocket en format standardisé
        
        Args:
            kline_data: Données brutes WebSocket
            
        Returns:
            Dict avec format standardisé
        """
        return {
            'open_time': pd.to_datetime(kline_data['t'], unit='ms'),
            'close_time': pd.to_datetime(kline_data['T'], unit='ms'),
            'open': float(kline_data['o']),
            'high': float(kline_data['h']),
            'low': float(kline_data['l']),
            'close': float(kline_data['c']),
            'volume': float(kline_data['v']),
            'is_closed': kline_data['x']  # True si bougie fermée
        }