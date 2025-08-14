"""
Formatage des données pour l'affichage
"""
import numpy as np
from datetime import datetime
import config

class DataFormatter:
    """Formateur des données pour affichage"""
    
    @staticmethod
    def format_price(price, decimals=6):
        """
        Formate un prix avec le nombre de décimales approprié
        
        Args:
            price: Prix à formater
            decimals: Nombre de décimales
            
        Returns:
            str: Prix formaté
        """
        if price is None or np.isnan(price):
            return "N/A"
        
        return f"{float(price):.{decimals}f}"
    
    @staticmethod
    def format_rsi(rsi_value, decimals=2):
        """
        Formate une valeur RSI
        
        Args:
            rsi_value: Valeur RSI
            decimals: Nombre de décimales
            
        Returns:
            str: RSI formaté
        """
        if rsi_value is None or np.isnan(rsi_value):
            return "N/A"
        
        return f"{float(rsi_value):.{decimals}f}"
    
    @staticmethod
    def format_timestamp(timestamp):
        """
        Formate un timestamp pour affichage
        
        Args:
            timestamp: Timestamp pandas ou datetime
            
        Returns:
            str: Timestamp formaté
        """
        if timestamp is None:
            return "N/A"
        
        try:
            if hasattr(timestamp, 'strftime'):
                return timestamp.strftime("%Y-%m-%d %H:%M:%S")
            else:
                return str(timestamp)
        except:
            return "N/A"
    
    @staticmethod
    def get_candle_symbol(color):
        """
        Retourne le symbole correspondant à la couleur de bougie
        
        Args:
            color: Couleur de la bougie ('green', 'red', 'doji')
            
        Returns:
            str: Symbole emoji
        """
        symbol_map = {
            'green': config.SYMBOLS['GREEN_CANDLE'],
            'red': config.SYMBOLS['RED_CANDLE'],
            'doji': config.SYMBOLS['DOJI_CANDLE']
        }
        
        return symbol_map.get(color, '⚪')
    
    @staticmethod
    def get_color_code(color):
        """
        Retourne le code couleur ANSI
        
        Args:
            color: Nom de la couleur
            
        Returns:
            str: Code couleur ANSI
        """
        if not config.DISPLAY_CONFIG['USE_COLORS']:
            return ''
        
        color_map = {
            'green': config.COLORS['GREEN'],
            'red': config.COLORS['RED'],
            'doji': config.COLORS['YELLOW'],
            'neutral': config.COLORS['WHITE'],
            'cyan': config.COLORS['CYAN'],
            'bold': config.COLORS['BOLD'],
            'reset': config.COLORS['RESET']
        }
        
        return color_map.get(color, '')
    
    @staticmethod
    def format_rsi_with_level(rsi_name, rsi_value, classification):
        """
        Formate un RSI avec indication de niveau
        
        Args:
            rsi_name: Nom du RSI (ex: RSI_14)
            rsi_value: Valeur du RSI
            classification: Classification du niveau
            
        Returns:
            str: RSI formaté avec couleur et niveau
        """
        formatted_value = DataFormatter.format_rsi(rsi_value)
        
        # Couleur selon le niveau
        if classification == 'oversold':
            color = DataFormatter.get_color_code('green')
            level_indicator = " (Survente)"
        elif classification == 'overbought':
            color = DataFormatter.get_color_code('red')
            level_indicator = " (Surachat)"
        else:
            color = DataFormatter.get_color_code('neutral')
            level_indicator = ""
        
        reset_color = DataFormatter.get_color_code('reset')
        
        if config.DISPLAY_CONFIG['USE_COLORS']:
            return f"{rsi_name}: {color}{formatted_value}{level_indicator}{reset_color}"
        else:
            return f"{rsi_name}: {formatted_value}{level_indicator}"
    
    @staticmethod
    def format_candle_data(candle_data, candle_type="Normal"):
        """
        Formate les données complètes d'une bougie
        
        Args:
            candle_data: Données de la bougie
            candle_type: Type de bougie ("Normal" ou "Heikin Ashi")
            
        Returns:
            list: Lignes formatées pour affichage
        """
        if candle_data is None:
            return [f"{candle_type}: Données non disponibles"]
        
        lines = []
        color = candle_data['color']
        symbol = DataFormatter.get_candle_symbol(color)
        color_code = DataFormatter.get_color_code(color)
        reset_code = DataFormatter.get_color_code('reset')
        
        # Titre avec symbole et couleur
        if config.DISPLAY_CONFIG['USE_COLORS']:
            title = f"{symbol} {candle_type}: {color_code}{color.upper()}{reset_code}"
        else:
            title = f"{symbol} {candle_type}: {color.upper()}"
        
        lines.append(title)
        
        if config.DISPLAY_CONFIG['SHOW_PRICES']:
            lines.append(f"  Open:  {DataFormatter.format_price(candle_data['open'])}")
            lines.append(f"  High:  {DataFormatter.format_price(candle_data['high'])}")
            lines.append(f"  Low:   {DataFormatter.format_price(candle_data['low'])}")
            lines.append(f"  Close: {DataFormatter.format_price(candle_data['close'])}")
        
        return lines