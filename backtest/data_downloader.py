#!/usr/bin/env python3
"""
Module de téléchargement de données historiques depuis Binance
Sauvegarde les données en format CSV pour le backtest
"""

import requests
import pandas as pd
import os
from datetime import datetime, timedelta
import time
from typing import Optional, List, Dict, Union, Any
import sys

class BinanceDataDownloader:
    """Téléchargeur de données historiques Binance"""
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3/klines"
        self.data_dir = "backtest/data"
        
        # S'assurer que le dossier existe
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Limites API Binance
        self.max_limit = 1000  # Max klines par requête
        self.request_delay = 0.1  # Délai entre requêtes (100ms)
        
    def get_klines(self, symbol: str, interval: str, start_time: int, end_time: int, limit: int = 1000) -> List[List]:
        """
        Récupère les klines depuis l'API Binance
        
        Args:
            symbol: Symbole (ex: BTCUSDC)
            interval: Intervalle (1m, 5m, 15m, 1h, etc.)
            start_time: Timestamp de début en milliseconds
            end_time: Timestamp de fin en milliseconds
            limit: Nombre max de klines (max 1000)
            
        Returns:
            Liste des klines
        """
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': start_time,
            'endTime': end_time,
            'limit': min(limit, self.max_limit)
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur API Binance: {e}")
            return []
    
    def download_historical_data(
        self, 
        symbol: str, 
        interval: str, 
        days_back: int = 30,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> str:
        """
        Télécharge les données historiques et sauvegarde en CSV
        
        Args:
            symbol: Symbole à télécharger
            interval: Intervalle des bougies
            days_back: Nombre de jours en arrière (si pas de dates spécifiées)
            start_date: Date de début au format YYYY-MM-DD
            end_date: Date de fin au format YYYY-MM-DD
            
        Returns:
            Chemin vers le fichier CSV créé
        """
        print(f"Téléchargement des données {symbol} - {interval}")
        
        # Calculer les timestamps
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=days_back)
        
        start_timestamp = int(start_dt.timestamp() * 1000)
        end_timestamp = int(end_dt.timestamp() * 1000)
        
        print(f"Période: {start_dt.strftime('%Y-%m-%d')} à {end_dt.strftime('%Y-%m-%d')}")
        
        # Télécharger les données par chunks
        all_klines = []
        current_start = start_timestamp
        
        while current_start < end_timestamp:
            print(f"Téléchargement... {datetime.fromtimestamp(current_start/1000).strftime('%Y-%m-%d %H:%M')}", end=" ")
            
            klines = self.get_klines(
                symbol=symbol,
                interval=interval,
                start_time=current_start,
                end_time=end_timestamp,
                limit=self.max_limit
            )
            
            if not klines:
                print("❌")
                break
                
            print(f"✓ ({len(klines)} bougies)")
            all_klines.extend(klines)
            
            # Préparer pour la prochaine requête
            if len(klines) < self.max_limit:
                break
                
            # Le timestamp de la dernière bougie + 1ms
            current_start = klines[-1][6] + 1
            
            # Respecter les limites API
            time.sleep(self.request_delay)
        
        if not all_klines:
            raise Exception("Aucune donnée téléchargée")
        
        # Convertir en DataFrame
        df = self._klines_to_dataframe(all_klines)
        
        # Sauvegarder en CSV
        filename = f"{symbol}_{interval}_{start_dt.strftime('%Y%m%d')}_{end_dt.strftime('%Y%m%d')}.csv"
        filepath = os.path.join(self.data_dir, filename)
        
        df.to_csv(filepath, index=False)
        
        print(f"✅ Données sauvegardées: {filepath}")
        print(f"📊 Total: {len(df)} bougies")
        print(f"📅 Première bougie: {df['timestamp'].iloc[0]}")
        print(f"📅 Dernière bougie: {df['timestamp'].iloc[-1]}")
        
        return filepath
    
    def _klines_to_dataframe(self, klines: List[List]) -> pd.DataFrame:
        """
        Convertit les klines Binance en DataFrame pandas
        
        Args:
            klines: Liste des klines de l'API Binance
            
        Returns:
            DataFrame avec colonnes standardisées
        """
        columns = [
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ]
        
        df = pd.DataFrame(klines, columns=columns)
        
        # Conversion des types
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'quote_asset_volume',
                          'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']
        
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Conversion des timestamps
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
        
        # Créer une colonne timestamp standardisée
        df['timestamp'] = df['open_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Supprimer les colonnes non nécessaires pour le backtest
        columns_to_keep = ['timestamp', 'open_time', 'open', 'high', 'low', 'close', 'volume']
        df = df[columns_to_keep]
        
        # Supprimer les doublons et trier
        df = df.drop_duplicates(subset=['open_time']).sort_values('open_time').reset_index(drop=True)
        
        return df
    
    def list_available_data(self) -> List[Dict[str, Union[str, float]]]:
        """
        Liste les fichiers de données disponibles
        
        Returns:
            Liste des fichiers avec leurs informations
        """
        files = []
        
        if not os.path.exists(self.data_dir):
            return files
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.csv'):
                filepath = os.path.join(self.data_dir, filename)
                parsed_info = self._parse_filename(filename)
                
                # Créer un nouveau dictionnaire avec les types mixtes
                file_info: Dict[str, Union[str, float]] = {
                    'filename': parsed_info['filename'],
                    'symbol': parsed_info['symbol'],
                    'interval': parsed_info['interval'],
                    'start_date': parsed_info['start_date'],
                    'end_date': parsed_info['end_date'],
                    'filepath': filepath,
                    'size_mb': os.path.getsize(filepath) / (1024 * 1024)
                }
                files.append(file_info)
        
        return sorted(files, key=lambda x: x['filename'])
    
    def _parse_filename(self, filename: str) -> Dict[str, str]:
        """
        Parse le nom de fichier pour extraire les informations
        
        Args:
            filename: Nom du fichier (ex: BTCUSDC_5m_20250101_20250119.csv)
            
        Returns:
            Dictionnaire avec les informations extraites
        """
        try:
            # Retirer l'extension
            name = filename.replace('.csv', '')
            parts = name.split('_')
            
            if len(parts) >= 4:
                return {
                    'filename': filename,
                    'symbol': parts[0],
                    'interval': parts[1],
                    'start_date': parts[2],
                    'end_date': parts[3]
                }
            else:
                return {'filename': filename, 'symbol': 'Unknown', 'interval': 'Unknown', 
                       'start_date': 'Unknown', 'end_date': 'Unknown'}
        except:
            return {'filename': filename, 'symbol': 'Unknown', 'interval': 'Unknown', 
                   'start_date': 'Unknown', 'end_date': 'Unknown'}

def main():
    """Interface en ligne de commande pour télécharger des données"""
    if len(sys.argv) < 3:
        print("Usage: python data_downloader.py SYMBOL INTERVAL [DAYS_BACK]")
        print("Exemple: python data_downloader.py BTCUSDC 5m 30")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    interval = sys.argv[2].lower()
    days_back = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    
    downloader = BinanceDataDownloader()
    
    try:
        filepath = downloader.download_historical_data(symbol, interval, days_back)
        print(f"\n🎉 Téléchargement terminé: {filepath}")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()