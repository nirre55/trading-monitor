#!/usr/bin/env python3
"""
Script principal de monitoring des bougies et indicateurs
Affiche en temps réel:
- Couleur des bougies normales
- Couleur des bougies Heikin Ashi  
- RSI sur bougies normales
- RSI sur bougies Heikin Ashi
"""

import sys
import os
import signal
import time
from datetime import datetime

# Ajouter le répertoire racine au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports des modules du projet avec chemins absolus
import config
from core.data_manager import DataManager
from core.websocket_handler import WebSocketHandler
from indicators.calculator import IndicatorCalculator
from display.console import ConsoleDisplay

class CandleMonitor:
    """Moniteur principal des bougies et indicateurs"""
    
    def __init__(self):
        """Initialise le moniteur"""
        self.data_manager = DataManager()
        self.calculator = IndicatorCalculator()
        self.display = ConsoleDisplay()
        self.ws_handler = None
        self.running = True
        
        # Configuration du signal d'arrêt
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Gestionnaire pour arrêt propre"""
        print("\n")
        self.display.display_info("Arrêt du monitoring en cours...")
        self.running = False
        if self.ws_handler:
            self.ws_handler.stop()
        sys.exit(0)
    
    def on_kline_update(self, kline_data):
        """
        Callback appelé à chaque mise à jour de bougie
        
        Args:
            kline_data: Données brutes WebSocket
        """
        try:
            # Mettre à jour les données
            is_new_candle = self.data_manager.update_with_kline(kline_data)
            
            if is_new_candle:
                # Nouvelle bougie fermée - calculer et afficher
                self.calculate_and_display()
                
        except Exception as e:
            self.display.display_error(f"Erreur traitement bougie: {e}")
            import traceback
            traceback.print_exc()
    
    def calculate_and_display(self):
        """Calcule tous les indicateurs et affiche les résultats"""
        try:
            # Récupérer le DataFrame complet
            df = self.data_manager.get_dataframe()
            
            if df.empty:
                return
            
            # Calculer tous les indicateurs
            indicators_data = self.calculator.calculate_all_indicators(df)
            
            # Afficher les résultats
            if not config.DISPLAY_CONFIG['COMPACT_MODE']:
                self.display.clear_console()
                self.display.display_header(config.SYMBOL, config.TIMEFRAME)
            
            self.display.display_indicators(indicators_data)
            
        except Exception as e:
            self.display.display_error(f"Erreur calcul indicateurs: {e}")
            import traceback
            traceback.print_exc()
    
    def initialize_data(self):
        """Initialise les données historiques"""
        self.display.display_info("Chargement des données historiques...")
        
        success = self.data_manager.initialize_historical_data(
            config.SYMBOL, 
            config.TIMEFRAME,
            config.INITIAL_KLINES_LIMIT
        )
        
        if not success:
            self.display.display_error("Impossible de charger les données historiques")
            return False
        
        self.display.display_success("Données historiques chargées")
        return True
    
    def start_websocket(self):
        """Démarre la connexion WebSocket"""
        self.display.display_info("Démarrage de la connexion WebSocket...")
        
        self.ws_handler = WebSocketHandler(
            config.SYMBOL,
            config.TIMEFRAME, 
            self.on_kline_update
        )
        
        self.ws_handler.start()
        
        # Attendre la connexion
        if not self.ws_handler.wait_for_connection():
            self.display.display_error("Impossible de se connecter au WebSocket")
            return False
        
        self.display.display_success("WebSocket connecté")
        return True
    
    def run(self):
        """Lance le monitoring complet"""
        try:
            # Affichage des informations de démarrage
            self.display.display_startup_info(config.SYMBOL, config.TIMEFRAME)
            
            # Initialisation des données
            if not self.initialize_data():
                return
            
            # Calcul et affichage initial
            self.display.display_info("Calcul des indicateurs initiaux...")
            self.calculate_and_display()
            
            # Démarrage WebSocket
            if not self.start_websocket():
                return
            
            self.display.display_success("Monitoring démarré avec succès!")
            self.display.display_info("En attente de nouvelles bougies...")
            print()
            
            # Boucle principale
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.signal_handler(None, None)
        except Exception as e:
            self.display.display_error(f"Erreur inattendue: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

def main():
    """Point d'entrée principal"""
    try:
        print("🚀 Démarrage du monitoring de bougies...")
        
        # Vérification de la configuration
        if not hasattr(config, 'SYMBOL') or not config.SYMBOL:
            print("❌ Configuration incomplète: SYMBOL requis dans config.py")
            sys.exit(1)
        
        if not hasattr(config, 'TIMEFRAME') or not config.TIMEFRAME:
            print("❌ Configuration incomplète: TIMEFRAME requis dans config.py")
            sys.exit(1)
        
        if not hasattr(config, 'RSI_PERIODS') or not config.RSI_PERIODS:
            print("❌ Configuration incomplète: RSI_PERIODS requis dans config.py")
            sys.exit(1)
        
        # Créer et lancer le moniteur
        monitor = CandleMonitor()
        monitor.run()
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("Assurez-vous d'avoir installé les dépendances avec: pip install -r requirements.txt")
        print("Et vérifiez que tous les fichiers sont présents dans la bonne structure")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("👋 Monitoring arrêté")

if __name__ == "__main__":
    main()