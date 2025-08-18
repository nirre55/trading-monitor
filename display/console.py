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
        
        if config.DISPLAY_CONFIG.get('USE_COLORS', False):
            title = f"{cyan}{bold}=== MONITORING {symbol} - {timeframe.upper()} ==={reset}"
        else:
            title = f"=== MONITORING {symbol} - {timeframe.upper()} ==="
        
        print(title)
        print(config.SYMBOLS['SEPARATOR'])
    
    def display_indicators(self, indicators_data, connection_status=None):
        """
        Affiche tous les indicateurs calculés
        
        Args:
            indicators_data: Données des indicateurs calculés
            connection_status: Statut de la connexion WebSocket (optionnel)
        """
        if not indicators_data['has_data']:
            message = indicators_data.get('message', 'Données insuffisantes') if indicators_data else 'Données insuffisantes'
            print(f"⚠️ {message}")
            return
        
        # Timestamp et statut de connexion si configuré
        if config.DISPLAY_CONFIG['SHOW_TIMESTAMP']:
            timestamp = datetime.now().strftime("%H:%M:%S")
            status_text = ""
            
            if connection_status:
                if connection_status.get('is_connected', False):
                    since_last = connection_status.get('seconds_since_last_message', 0)
                    if since_last < 30:
                        status_text = " 🟢 Connecté"
                    else:
                        status_text = f" 🟡 Dernière donnée il y a {since_last:.0f}s"
                else:
                    attempts = connection_status.get('reconnect_attempts', 0)
                    if attempts > 0:
                        status_text = f" 🔄 Reconnexion (#{attempts})"
                    else:
                        status_text = " 🔴 Déconnecté"
            
            print(f"⏰ Mise à jour: {timestamp}{status_text}")
            print()
        
        # Affichage des bougies
        self._display_candles(indicators_data)
        
        # Affichage des RSI
        if config.DISPLAY_CONFIG['SHOW_RSI_VALUES']:
            self._display_rsi_values(indicators_data)
        
        # Affichage EMA timeframe supérieur
        if indicators_data.get('higher_tf_ema') and indicators_data['higher_tf_ema']:
            self._display_higher_timeframe_ema(indicators_data['higher_tf_ema'])
        
        # NOUVEAU: Affichage ATR
        if indicators_data.get('atr_data') and indicators_data['atr_data']:
            self._display_atr_data(indicators_data['atr_data'])
        
        # NOUVEAU: Affichage Volume
        if indicators_data.get('volume_data') and indicators_data['volume_data']:
            self._display_volume_data(indicators_data['volume_data'])
        
        # NOUVEAU: Affichage Signaux de Trading
        if indicators_data.get('signal_analysis') and indicators_data['signal_analysis']:
            self._display_signal_analysis(indicators_data['signal_analysis'])
        
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
        
        if config.DISPLAY_CONFIG.get('USE_COLORS', False):
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
                classification = normal_classifications.get(rsi_name, 'neutral') if normal_classifications else 'neutral'
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
                classification = ha_classifications.get(rsi_name, 'neutral') if ha_classifications else 'neutral'
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
        
    def _display_higher_timeframe_ema(self, ema_data):
        """Affiche les EMA du timeframe supérieur"""
        print()
        
        # Vérification de sécurité pour éviter les erreurs Pylance
        if not ema_data or not isinstance(ema_data, dict):
            print("⚠️ Données EMA non disponibles")
            return
        
        timeframe = ema_data.get('timeframe', 'N/A') if ema_data else 'N/A'
        ema_values = ema_data.get('values', {}) if ema_data else {}
        price_vs_ema = ema_data.get('price_vs_ema', {}) if ema_data else {}
        ema_trends = ema_data.get('ema_trends', {}) if ema_data else {}
        current_candle = ema_data.get('current_candle')
        
        # Vérifications supplémentaires
        if not isinstance(ema_values, dict):
            ema_values = {}
        if not isinstance(price_vs_ema, dict):
            price_vs_ema = {}
        if not isinstance(ema_trends, dict):
            ema_trends = {}
        
        # Titre avec timeframe
        ema_symbol = "📊"
        print(f"{ema_symbol} EMA Timeframe Supérieur ({timeframe.upper()}):")
        
        if current_candle and isinstance(current_candle, dict):
            current_price = current_candle.get('close')
            candle_time = current_candle.get('open_time')
            
            if current_price is not None:
                formatted_time = self.formatter.format_timestamp(candle_time) if candle_time else 'N/A'
                print(f"  📈 Prix actuel {timeframe}: {self.formatter.format_price(current_price, 2)} ({formatted_time})")
        
        print()
        
        # Afficher chaque EMA avec ses détails
        for ema_name, ema_value in ema_values.items():
            if ema_value is None:
                print(f"  {ema_name}: N/A")
                continue
            
            # Valeur EMA formatée
            formatted_value = self.formatter.format_price(ema_value, 2)
            
            # Position prix vs EMA
            position = price_vs_ema.get(ema_name, 'N/A') if price_vs_ema else 'N/A'
            position_symbol = {
                'above': '⬆️',
                'below': '⬇️',
                'equal': '➡️',
                'N/A': '❓'
            }.get(position, '❓')
            
            # Tendance EMA
            trend = ema_trends.get(ema_name, 'N/A') if ema_trends else 'N/A'
            trend_symbol = {
                'rising': '📈',
                'falling': '📉',
                'sideways': '➡️',
                'N/A': '❓'
            }.get(trend, '❓')
            
            # Couleur selon la classification
            classification = self._get_ema_classification(position, trend)
            color_code = self._get_ema_color_code(classification)
            reset_code = self.formatter.get_color_code('reset')
            
            # Affichage complet
            if config.DISPLAY_CONFIG.get('USE_COLORS', False):
                print(f"  {ema_name}: {color_code}{formatted_value}{reset_code} {position_symbol} {trend_symbol} ({classification})")
            else:
                print(f"  {ema_name}: {formatted_value} {position_symbol} {trend_symbol} ({classification})")
    
    def _get_ema_classification(self, position, trend):
        """Détermine la classification EMA avec vérifications de sécurité"""
        # Vérifications de type pour éviter les erreurs
        if not isinstance(position, str):
            position = 'N/A'
        if not isinstance(trend, str):
            trend = 'N/A'
            
        if position == 'above' and trend == 'rising':
            return 'Haussier'
        elif position == 'below' and trend == 'falling':
            return 'Baissier'
        elif position == 'above' and trend == 'falling':
            return 'Résistance'
        elif position == 'below' and trend == 'rising':
            return 'Support'
        elif trend == 'sideways':
            return 'Neutre'
        else:
            return 'N/A'
    
    def _get_ema_color_code(self, classification):
        """Retourne la couleur selon la classification EMA avec vérifications"""
        # Vérification de sécurité pour DISPLAY_CONFIG
        if not hasattr(config, 'DISPLAY_CONFIG') or not isinstance(config.DISPLAY_CONFIG, dict):
            return ''
            
        if not config.DISPLAY_CONFIG.get('USE_COLORS', False):
            return ''
        
        # Vérification que classification est une string
        if not isinstance(classification, str):
            classification = 'N/A'
        
        color_map = {
            'Haussier': self.formatter.get_color_code('green'),
            'Baissier': self.formatter.get_color_code('red'),
            'Résistance': self.formatter.get_color_code('red'),
            'Support': self.formatter.get_color_code('green'),
            'Neutre': self.formatter.get_color_code('neutral'),
            'N/A': self.formatter.get_color_code('neutral')
        }
        
        return color_map.get(classification, '')
    
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
        
        if config.DISPLAY_CONFIG.get('USE_COLORS', False):
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
        
        # Afficher les nouveaux indicateurs si activés
        if hasattr(config, 'EMA_HIGHER_TIMEFRAME') and config.EMA_HIGHER_TIMEFRAME.get('ENABLED', False):
            print("✅ EMA timeframe supérieur")
        
        atr_config = getattr(config, 'ATR_CONFIG', {})
        if atr_config.get('ENABLED', False):
            atr_periods = atr_config.get('PERIODS', [])
            print(f"✅ ATR (Volatilité) - Périodes: {atr_periods}")
        
        volume_config = getattr(config, 'VOLUME_CONFIG', {})
        if volume_config.get('ENABLED', False):
            volume_periods = volume_config.get('LOOKBACK_PERIODS', [])
            print(f"✅ Analyse Volume - Périodes: {volume_periods}")
        
        signal_config = getattr(config, 'SIGNAL_CONFIG', {})
        if signal_config.get('ENABLED', False):
            rsi_levels = f"{signal_config.get('RSI_OVERSOLD', 30)}/{signal_config.get('RSI_OVERBOUGHT', 70)}"
            print(f"✅ Détection Signaux - RSI: {rsi_levels}")
        print()
        
        print("Légende des couleurs:")
        green = self.formatter.get_color_code('green')
        red = self.formatter.get_color_code('red')
        yellow = self.formatter.get_color_code('yellow')
        
        if config.DISPLAY_CONFIG.get('USE_COLORS', False):
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
        
        if config.DISPLAY_CONFIG.get('USE_COLORS', False):
            print(f"{red}❌ {message}{reset}")
        else:
            print(f"❌ {message}")
    
    def display_success(self, message):
        """Affiche un message de succès"""
        green = self.formatter.get_color_code('green')
        reset = self.formatter.get_color_code('reset')
        
        if config.DISPLAY_CONFIG.get('USE_COLORS', False):
            print(f"{green}✅ {message}{reset}")
        else:
            print(f"✅ {message}")
    
    def display_info(self, message):
        """Affiche un message d'information"""
        cyan = self.formatter.get_color_code('cyan')
        reset = self.formatter.get_color_code('reset')
        
        if config.DISPLAY_CONFIG.get('USE_COLORS', False):
            print(f"{cyan}ℹ️ {message}{reset}")
        else:
            print(f"ℹ️ {message}")
    
    def _display_atr_data(self, atr_data):
        """Affiche les données ATR"""
        print()
        
        atr_symbol = "🌊"
        print(f"{atr_symbol} ATR (Average True Range):")
        
        values = atr_data.get('values', {})
        analysis = atr_data.get('analysis', {})
        
        for atr_name, atr_value in values.items():
            if atr_value is None:
                print(f"  {atr_name}: N/A")
                continue
            
            # Formater la valeur ATR
            formatted_value = self.formatter.format_price(atr_value, 4)
            
            # Récupérer l'analyse si disponible
            atr_analysis = analysis.get(atr_name, {})
            volatility_level = atr_analysis.get('volatility_level', 'N/A')
            trend = atr_analysis.get('trend', 'N/A')
            
            # Symboles pour la volatilité
            volatility_symbols = {
                'low': '🟢',
                'normal': '🟡', 
                'high': '🟠',
                'extreme': '🔴',
                'N/A': '❓'
            }
            
            # Symboles pour la tendance
            trend_symbols = {
                'increasing': '📈',
                'decreasing': '📉',
                'stable': '➡️',
                'N/A': '❓'
            }
            
            volatility_symbol = volatility_symbols.get(volatility_level, '❓')
            trend_symbol = trend_symbols.get(trend, '❓')
            
            # Couleur selon le niveau de volatilité
            color_code = self._get_volatility_color_code(volatility_level)
            reset_code = self.formatter.get_color_code('reset')
            
            # Affichage complet
            if config.DISPLAY_CONFIG.get('USE_COLORS', False):
                print(f"  {atr_name}: {color_code}{formatted_value}{reset_code} {volatility_symbol} {trend_symbol} ({volatility_level.replace('_', ' ').title()})")
            else:
                print(f"  {atr_name}: {formatted_value} {volatility_symbol} {trend_symbol} ({volatility_level.replace('_', ' ').title()})")
    
    def _display_volume_data(self, volume_data):
        """Affiche les données d'analyse du volume"""
        print()
        
        volume_symbol = "📊"
        print(f"{volume_symbol} Analyse Volume:")
        
        # Afficher la comparaison avec la moyenne si disponible
        comparison = volume_data.get('volume_comparison', {})
        if comparison.get('has_data', False):
            current_vol = comparison.get('current_volume', 0)
            ratio_recent = comparison.get('ratio_vs_recent', 1)
            volume_level = comparison.get('volume_level', 'normal')
            
            formatted_volume = self.formatter.format_number(current_vol, 0)
            
            # Couleur selon le niveau de volume
            color_code = self._get_volume_level_color_code(volume_level)
            reset_code = self.formatter.get_color_code('reset')
            
            # Symbole selon le niveau
            level_symbols = {
                'very_low': '🔴',
                'below_average': '🟠',
                'normal': '🟡',
                'above_average': '🟢',
                'high': '💚',
                'very_high': '🔥'
            }
            level_symbol = level_symbols.get(volume_level, '❓')
            
            if config.DISPLAY_CONFIG.get('USE_COLORS', False):
                print(f"  Volume actuel: {color_code}{formatted_volume}{reset_code} {level_symbol} ({ratio_recent:.1f}x la moyenne)")
            else:
                print(f"  Volume actuel: {formatted_volume} {level_symbol} ({ratio_recent:.1f}x la moyenne)")
        
        # Afficher l'analyse pour les différentes périodes
        for key, analysis in volume_data.items():
            if key.startswith('volume_') and key != 'volume_comparison' and analysis.get('has_data', False):
                period = key.split('_')[1]
                self._display_volume_period_analysis(period, analysis)
    
    def _display_volume_period_analysis(self, period, analysis):
        """Affiche l'analyse du volume pour une période donnée"""
        print(f"  📈 {period} dernières bougies:")
        
        # Volume par type de bougie
        green_vol = analysis.get('green_volume', 0)
        red_vol = analysis.get('red_volume', 0)
        total_vol = analysis.get('total_volume', 0)
        
        if total_vol > 0:
            green_ratio = (green_vol / total_vol) * 100
            red_ratio = (red_vol / total_vol) * 100
            
            # Dominance
            volume_ratio = analysis.get('volume_ratio', {})
            dominance = volume_ratio.get('dominance', 'neutral')
            
            dominance_symbols = {
                'bullish': '🟢',
                'bearish': '🔴',
                'neutral': '🟡'
            }
            dominance_symbol = dominance_symbols.get(dominance, '❓')
            
            print(f"    Répartition: {green_ratio:.1f}% vert 🟢 | {red_ratio:.1f}% rouge 🔴 {dominance_symbol}")
        
        # Tendance du volume
        trend = analysis.get('volume_trend', 'N/A')
        trend_symbols = {
            'increasing': '📈',
            'decreasing': '📉', 
            'stable': '➡️',
            'N/A': '❓'
        }
        trend_symbol = trend_symbols.get(trend, '❓')
        print(f"    Tendance: {trend_symbol} {trend.replace('_', ' ').title()}")
        
        # Bougies à volume exceptionnel
        high_vol = analysis.get('high_volume_candles', {})
        if high_vol.get('count', 0) > 0:
            count = high_vol['count']
            max_ratio = high_vol.get('max_ratio', 1)
            print(f"    Volume exceptionnel: {count} bougie(s) 🔥 (max: {max_ratio:.1f}x)")
    
    def _get_volatility_color_code(self, volatility_level):
        """Retourne la couleur selon le niveau de volatilité"""
        if not config.DISPLAY_CONFIG.get('USE_COLORS', False):
            return ''
        
        color_map = {
            'low': self.formatter.get_color_code('green'),
            'normal': self.formatter.get_color_code('neutral'),
            'high': self.formatter.get_color_code('yellow'),
            'extreme': self.formatter.get_color_code('red'),
            'N/A': self.formatter.get_color_code('neutral')
        }
        
        return color_map.get(volatility_level, '')
    
    def _get_volume_level_color_code(self, volume_level):
        """Retourne la couleur selon le niveau de volume"""
        if not config.DISPLAY_CONFIG.get('USE_COLORS', False):
            return ''
        
        color_map = {
            'very_low': self.formatter.get_color_code('red'),
            'below_average': self.formatter.get_color_code('yellow'),
            'normal': self.formatter.get_color_code('neutral'),
            'above_average': self.formatter.get_color_code('green'),
            'high': self.formatter.get_color_code('green'),
            'very_high': self.formatter.get_color_code('green')
        }
        
        return color_map.get(volume_level, '')
    
    def _display_signal_analysis(self, signal_analysis):
        """Affiche l'analyse des signaux de trading"""
        print()
        
        signal_symbol = config.SYMBOLS.get('SIGNAL_ALERT', '🚨')
        print(f"{signal_symbol} Analyse Signaux de Trading:")
        
        # Afficher les signaux détectés
        signals_detected = signal_analysis.get('signals_detected', [])
        if signals_detected:
            for signal in signals_detected:
                signal_type = signal.get('type', 'UNKNOWN')
                timestamp = signal.get('timestamp', 'N/A')
                
                # Symbole selon le type de signal
                if signal_type == 'LONG':
                    symbol = config.SYMBOLS.get('SIGNAL_LONG', '🚀')
                    color_code = self.formatter.get_color_code('green')
                elif signal_type == 'SHORT':
                    symbol = config.SYMBOLS.get('SIGNAL_SHORT', '📉')
                    color_code = self.formatter.get_color_code('red')
                else:
                    symbol = '❓'
                    color_code = self.formatter.get_color_code('neutral')
                
                reset_code = self.formatter.get_color_code('reset')
                
                if config.DISPLAY_CONFIG.get('USE_COLORS', False):
                    print(f"  {symbol} {color_code}SIGNAL {signal_type} DÉTECTÉ{reset_code}")
                else:
                    print(f"  {symbol} SIGNAL {signal_type} DÉTECTÉ")
                
                # Afficher le score et quelques détails clés
                score = signal.get('score', 'N/A')
                print(f"    Score: {score}")
                
                steps = signal.get('steps', {})
                if steps.get('step1_rsi'):
                    rsi_data = steps['step1_rsi']
                    print(f"    RSI: {rsi_data.get('value', 'N/A'):.1f} ({rsi_data.get('condition', 'N/A')})")
                
                validations = signal.get('validations', {})
                volume_val = validations.get('volume', {})
                if volume_val:
                    volume_ok = "✓" if volume_val.get('ok', False) else "✗"
                    print(f"    Volume: {volume_ok} {volume_val.get('level', 'N/A').replace('_', ' ').title()}")
                
                print(f"    Heure: {timestamp}")
                
                print()
        
        # Afficher l'état des machines d'état
        long_state = signal_analysis.get('long_state', 'idle')
        short_state = signal_analysis.get('short_state', 'idle')
        
        if long_state != 'idle' or short_state != 'idle':
            waiting_symbol = config.SYMBOLS.get('SIGNAL_WAITING', '⏳')
            print(f"  {waiting_symbol} États en cours:")
            
            if long_state != 'idle':
                long_steps = signal_analysis.get('long_steps', {})
                steps_count = len(long_steps)
                state_display = long_state.replace('_', ' ').title()
                print(f"    LONG: {state_display} ({steps_count}/2 étapes)")
            
            if short_state != 'idle':
                short_steps = signal_analysis.get('short_steps', {})
                steps_count = len(short_steps)
                state_display = short_state.replace('_', ' ').title()
                print(f"    SHORT: {state_display} ({steps_count}/2 étapes)")
            
            print()