"""
Gestionnaire d'affichage console
"""
import os
from datetime import datetime
from .formatter import DataFormatter
import config

class ConsoleDisplay:
    """Gestionnaire de l'affichage dans la console"""
    
    def __init__(self):
        """Initialise l'affichage console"""
        self.formatter = DataFormatter()
        self.last_display_time = None
    
    def clear_console(self):
        """Nettoie la console si configuré"""
        if config.DISPLAY_CONFIG['CLEAR_CONSOLE']:
            os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self, symbol, timeframe):
        """
        Affiche l'en-tête du monitoring
        
        Args:
            symbol: Symbole surveillé
            timeframe: Timeframe des bougies
        """
        cyan = self.formatter.get_color_code('cyan')
        bold = self.formatter.get_color_code('bold')
        reset = self.formatter.get_color_code('reset')
        
        if config.DISPLAY_CONFIG['USE_COLORS']:
            title = f"{cyan}{bold}=== MONITORING {symbol} - {timeframe.upper()} ==={reset}"
        else:
            title = f"=== MONITORING {symbol} - {timeframe.upper()} ==="
        
        print(title)
        print(config.SYMBOLS['SEPARATOR'])
    
    def display_indicators(self, indicators_data):
        """
        Affiche tous les indicateurs calculés
        
        Args:
            indicators_data: Données des indicateurs calculés
        """
        if not indicators_data['has_data']:
            message = indicators_data.get('message', 'Données insuffisantes')
            print(f"⚠️ {message}")
            return
        
        # Timestamp si configuré
        if config.DISPLAY_CONFIG['SHOW_TIMESTAMP']:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"⏰ Mise à jour: {timestamp}")
            print()
        
        # Affichage des bougies
        self._display_candles(indicators_data)
        
        # Affichage des RSI
        if config.DISPLAY_CONFIG['SHOW_RSI_VALUES']:
            self._display_rsi_values(indicators_data)
        
        print(config.SYMBOLS['SEPARATOR'])
        print()
    
    def _display_candles(self, indicators_data):
        """Affiche les données des bougies"""
        normal_candle = indicators_data['normal_candle']
        ha_candle = indicators_data['ha_candle']
        
        # Bougie normale
        if normal_candle:
            if config.DISPLAY_CONFIG['COMPACT_MODE']:
                self._display_candle_compact(normal_candle, "Normal")
            else:
                candle_lines = self.formatter.format_candle_data(normal_candle, "Normal")
                for line in candle_lines:
                    print(line)
        
        print()
        
        # Bougie Heikin Ashi
        if ha_candle:
            if config.DISPLAY_CONFIG['COMPACT_MODE']:
                self._display_candle_compact(ha_candle, "Heikin Ashi")
            else:
                candle_lines = self.formatter.format_candle_data(ha_candle, "Heikin Ashi")
                for line in candle_lines:
                    print(line)
    
    def _display_candle_compact(self, candle_data, candle_type):
        """Affichage compact d'une bougie"""
        symbol = self.formatter.get_candle_symbol(candle_data['color'])
        color = candle_data['color'].upper()
        close_price = self.formatter.format_price(candle_data['close'], 2)
        
        color_code = self.formatter.get_color_code(candle_data['color'])
        reset_code = self.formatter.get_color_code('reset')
        
        if config.DISPLAY_CONFIG['USE_COLORS']:
            print(f"{symbol} {candle_type}: {color_code}{color}{reset_code} @ {close_price}")
        else:
            print(f"{symbol} {candle_type}: {color} @ {close_price}")
    
    def _display_rsi_values(self, indicators_data):
        """Affiche les valeurs RSI"""
        normal_rsi = indicators_data['normal_rsi']
        ha_rsi = indicators_data['ha_rsi']
        
        print()
        
        # RSI sur bougies normales
        if normal_rsi:
            rsi_symbol = config.SYMBOLS['RSI_INDICATOR']
            print(f"{rsi_symbol} RSI Bougies Normales:")
            
            normal_classifications = self._get_rsi_classifications(normal_rsi)
            
            for rsi_name, rsi_value in normal_rsi.items():
                classification = normal_classifications.get(rsi_name, 'neutral')
                formatted_rsi = self.formatter.format_rsi_with_level(
                    rsi_name, rsi_value, classification
                )
                print(f"  {formatted_rsi}")
        
        print()
        
        # RSI sur bougies Heikin Ashi
        if ha_rsi:
            ha_symbol = config.SYMBOLS['HA_INDICATOR']
            print(f"{ha_symbol} RSI Heikin Ashi:")
            
            ha_classifications = self._get_rsi_classifications(ha_rsi)
            
            for rsi_name, rsi_value in ha_rsi.items():
                classification = ha_classifications.get(rsi_name, 'neutral')
                formatted_rsi = self.formatter.format_rsi_with_level(
                    rsi_name, rsi_value, classification
                )
                print(f"  {formatted_rsi}")
    
    def _get_rsi_classifications(self, rsi_values):
        """Obtient les classifications RSI"""
        # Import absolu pour éviter les erreurs de relative import
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from indicators.rsi import RSI
        
        classifications = {}
        for rsi_name, rsi_value in rsi_values.items():
            classifications[rsi_name] = RSI.classify_rsi_level(rsi_value)
        
        return classifications
    
    def display_startup_info(self, symbol, timeframe):
        """
        Affiche les informations de démarrage
        
        Args:
            symbol: Symbole surveillé
            timeframe: Timeframe
        """
        self.clear_console()
        
        cyan = self.formatter.get_color_code('cyan')
        bold = self.formatter.get_color_code('bold')
        reset = self.formatter.get_color_code('reset')
        
        if config.DISPLAY_CONFIG['USE_COLORS']:
            title = f"{cyan}{bold}🚀 DÉMARRAGE MONITORING BOUGIES{reset}"
        else:
            title = "🚀 DÉMARRAGE MONITORING BOUGIES"
        
        print(title)
        print("=" * 50)
        print(f"📊 Symbole: {symbol}")
        print(f"⏱️ Timeframe: {timeframe}")
        print(f"📈 Périodes RSI: {config.RSI_PERIODS}")
        print(f"📥 Données historiques: {config.INITIAL_KLINES_LIMIT} bougies")
        print()
        
        print("Fonctionnalités:")
        print("✅ Bougies normales (OHLC)")
        print("✅ Bougies Heikin Ashi")
        print("✅ RSI sur bougies normales")
        print("✅ RSI sur bougies Heikin Ashi")
        print("✅ Affichage couleurs des bougies")
        print()
        
        print("Légende des couleurs:")
        green = self.formatter.get_color_code('green')
        red = self.formatter.get_color_code('red')
        yellow = self.formatter.get_color_code('yellow')
        
        if config.DISPLAY_CONFIG['USE_COLORS']:
            print(f"🟢 {green}VERT{reset}: Bougie haussière (Close > Open)")
            print(f"🔴 {red}ROUGE{reset}: Bougie baissière (Close < Open)")
            print(f"🟡 {yellow}JAUNE{reset}: Doji (Close = Open)")
        else:
            print("🟢 VERT: Bougie haussière (Close > Open)")
            print("🔴 ROUGE: Bougie baissière (Close < Open)")
            print("🟡 JAUNE: Doji (Close = Open)")
        
        print()
        print("Appuyez sur Ctrl+C pour arrêter")
        print("=" * 50)
        print()
    
    def display_error(self, message):
        """Affiche un message d'erreur"""
        red = self.formatter.get_color_code('red')
        reset = self.formatter.get_color_code('reset')
        
        if config.DISPLAY_CONFIG['USE_COLORS']:
            print(f"{red}❌ {message}{reset}")
        else:
            print(f"❌ {message}")
    
    def display_success(self, message):
        """Affiche un message de succès"""
        green = self.formatter.get_color_code('green')
        reset = self.formatter.get_color_code('reset')
        
        if config.DISPLAY_CONFIG['USE_COLORS']:
            print(f"{green}✅ {message}{reset}")
        else:
            print(f"✅ {message}")
    
    def display_info(self, message):
        """Affiche un message d'information"""
        cyan = self.formatter.get_color_code('cyan')
        reset = self.formatter.get_color_code('reset')
        
        if config.DISPLAY_CONFIG['USE_COLORS']:
            print(f"{cyan}ℹ️ {message}{reset}")
        else:
            print(f"ℹ️ {message}")