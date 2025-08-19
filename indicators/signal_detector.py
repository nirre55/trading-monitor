"""
Détecteur de signaux de trading avec logique d'état
Suit une séquence d'événements pour valider des setups complets
"""
import json
from datetime import datetime
from typing import Dict, Optional, Any, List
from enum import Enum
import config

class SignalState(Enum):
    """États possibles pour la détection de signaux"""
    IDLE = "idle"  # En attente
    RSI_OK = "rsi_ok"  # RSI condition validée
    SIGNAL_COMPLETE = "signal_complete"  # Signal complet détecté (RSI + HA)

class SignalType(Enum):
    """Types de signaux"""
    LONG = "LONG"
    SHORT = "SHORT"

class SignalDetector:
    """Détecteur de signaux de trading avec machine d'état"""
    
    def __init__(self):
        """Initialise le détecteur de signaux"""
        self.long_state = SignalState.IDLE
        self.short_state = SignalState.IDLE
        
        # Stockage des étapes pour chaque signal
        self.long_steps = {}
        self.short_steps = {}
        
        # Configuration depuis config.py
        signal_config = getattr(config, 'SIGNAL_CONFIG', {})
        self.enabled = signal_config.get('ENABLED', True)
        self.rsi_oversold = signal_config.get('RSI_OVERSOLD', 30)
        self.rsi_overbought = signal_config.get('RSI_OVERBOUGHT', 70)
        self.rsi_period = signal_config.get('RSI_PERIOD', 14)
        self.log_signals = signal_config.get('LOG_SIGNALS', True)
        self.ema_current_period = signal_config.get('EMA_CURRENT_PERIOD', 50)
        self.ema_higher_timeframe_period = signal_config.get('EMA_HIGHER_TIMEFRAME_PERIOD', 200)
        self.volume_comparison_periods = signal_config.get('VOLUME_COMPARISON_PERIODS', 20)
        
        # Données pour validation
        self.last_validation_time = None
        
        if self.enabled:
            print(f"Detecteur de signaux optimise - RSI: {self.rsi_oversold}/{self.rsi_overbought} (periode {self.rsi_period}), EMA Current: {self.ema_current_period}, EMA Higher: {self.ema_higher_timeframe_period}")
    
    def analyze_signals(self, indicators_data, current_time=None):
        """
        Analyse les indicateurs pour détecter des signaux
        
        Args:
            indicators_data: Données des indicateurs calculés
            current_time: Timestamp actuel (optionnel)
            
        Returns:
            dict: État des signaux et alertes
        """
        if not self.enabled or not indicators_data.get('has_data', False):
            return {'signals_detected': [], 'long_state': self.long_state.value, 'short_state': self.short_state.value}
        
        if current_time is None:
            current_time = datetime.now()
        
        self.last_validation_time = current_time
        
        # Extraire les données nécessaires
        normal_candle = indicators_data.get('normal_candle')
        ha_candle = indicators_data.get('ha_candle')
        normal_rsi = indicators_data.get('normal_rsi', {})
        higher_tf_ema = indicators_data.get('higher_tf_ema', {})
        current_tf_ema = indicators_data.get('current_tf_ema', {})  # NOUVEAU
        volume_data = indicators_data.get('volume_data', {})
        
        signals_detected = []
        
        # Analyser signal LONG
        long_signal = self._analyze_long_signal(
            normal_candle, ha_candle, normal_rsi, higher_tf_ema, volume_data, current_tf_ema, current_time
        )
        if long_signal:
            signals_detected.append(long_signal)
        
        # Analyser signal SHORT
        short_signal = self._analyze_short_signal(
            normal_candle, ha_candle, normal_rsi, higher_tf_ema, volume_data, current_tf_ema, current_time
        )
        if short_signal:
            signals_detected.append(short_signal)
        
        return {
            'signals_detected': signals_detected,
            'long_state': self.long_state.value,
            'short_state': self.short_state.value,
            'long_steps': self.long_steps.copy(),
            'short_steps': self.short_steps.copy()
        }
    
    def _analyze_long_signal(self, normal_candle, ha_candle, normal_rsi, higher_tf_ema, volume_data, current_tf_ema, current_time):
        """Analyse optimisée pour signaux LONG"""
        
        # Vérifications de base
        if not all([normal_candle, ha_candle, normal_rsi]):
            return None
        
        # RSI spécifique configuré pour les signaux
        rsi_key = f'RSI_{self.rsi_period}'
        main_rsi = normal_rsi.get(rsi_key)
        
        # Si le RSI configuré n'existe pas, prendre le premier disponible en fallback
        if main_rsi is None:
            for rsi_name, rsi_value in normal_rsi.items():
                if rsi_value is not None:
                    main_rsi = rsi_value
                    rsi_key = rsi_name  # Mettre à jour la clé pour le logging
                    break
        
        if main_rsi is None:
            return None
        
        # Machine d'état simplifiée pour LONG
        if self.long_state == SignalState.IDLE:
            # Étape 1: RSI oversold
            if main_rsi <= self.rsi_oversold:
                self.long_state = SignalState.RSI_OK
                self.long_steps['step1_rsi'] = {
                    'timestamp': current_time.isoformat() if current_time else datetime.now().isoformat(),
                    'value': main_rsi,
                    'condition': 'oversold',
                    'rsi_period': rsi_key
                }
                
        elif self.long_state == SignalState.RSI_OK:
            # Étape 2: Bougie HA verte (le RSI peut changer entre temps, c'est pas grave)
            if ha_candle['color'] == 'green':
                # SIGNAL COMPLET ! Log immédiatement avec toutes les validations
                self.long_steps['step2_ha'] = {
                    'timestamp': current_time.isoformat() if current_time else datetime.now().isoformat(),
                    'color': 'green',
                    'close': ha_candle['close']
                }
                
                # Faire toutes les validations
                validations = self._validate_all_conditions('LONG', normal_candle, ha_candle, higher_tf_ema, volume_data, current_tf_ema)
                
                signal = self._create_optimized_signal('LONG', self.long_steps, validations)
                self._reset_long_state()
                return signal
        
        return None
    
    def _analyze_short_signal(self, normal_candle, ha_candle, normal_rsi, higher_tf_ema, volume_data, current_tf_ema, current_time):
        """Analyse optimisée pour signaux SHORT"""
        
        # Vérifications de base
        if not all([normal_candle, ha_candle, normal_rsi]):
            return None
        
        # RSI spécifique configuré pour les signaux
        rsi_key = f'RSI_{self.rsi_period}'
        main_rsi = normal_rsi.get(rsi_key)
        
        # Si le RSI configuré n'existe pas, prendre le premier disponible en fallback
        if main_rsi is None:
            for rsi_name, rsi_value in normal_rsi.items():
                if rsi_value is not None:
                    main_rsi = rsi_value
                    rsi_key = rsi_name  # Mettre à jour la clé pour le logging
                    break
        
        if main_rsi is None:
            return None
        
        # Machine d'état simplifiée pour SHORT
        if self.short_state == SignalState.IDLE:
            # Étape 1: RSI overbought
            if main_rsi >= self.rsi_overbought:
                self.short_state = SignalState.RSI_OK
                self.short_steps['step1_rsi'] = {
                    'timestamp': current_time.isoformat() if current_time else datetime.now().isoformat(),
                    'value': main_rsi,
                    'condition': 'overbought',
                    'rsi_period': rsi_key
                }
                
        elif self.short_state == SignalState.RSI_OK:
            # Étape 2: Bougie HA rouge (le RSI peut changer entre temps, c'est pas grave)
            if ha_candle['color'] == 'red':
                # SIGNAL COMPLET ! Log immédiatement avec toutes les validations
                self.short_steps['step2_ha'] = {
                    'timestamp': current_time.isoformat() if current_time else datetime.now().isoformat(),
                    'color': 'red',
                    'close': ha_candle['close']
                }
                
                # Faire toutes les validations
                validations = self._validate_all_conditions('SHORT', normal_candle, ha_candle, higher_tf_ema, volume_data, current_tf_ema)
                
                signal = self._create_optimized_signal('SHORT', self.short_steps, validations)
                self._reset_short_state()
                return signal
        
        return None
    
    def _validate_all_conditions(self, signal_type, normal_candle, ha_candle, higher_tf_ema, volume_data, current_tf_ema=None):
        """Valide toutes les conditions pour le scoring en utilisant la dernière bougie fermée"""
        validations = {}
        
        # Prix de référence = prix de la dernière bougie fermée (normal candle close)
        # C'est le prix au moment exact de la confirmation du signal
        last_closed_price = normal_candle['close']
        
        # 1. Validation EMA timeframe supérieur (période configurable)
        ema_values = higher_tf_ema.get('values', {}) if higher_tf_ema else {}
        ema_key = f'EMA_{self.ema_higher_timeframe_period}'
        ema_higher_tf = ema_values.get(ema_key)
        
        # Pour l'EMA higher timeframe, on utilise aussi le prix de la dernière bougie fermée
        # car c'est le prix de référence au moment de la confirmation
        if ema_higher_tf is not None:
            if signal_type == 'LONG':
                ema_higher_tf_ok = last_closed_price > ema_higher_tf
            else:  # SHORT
                ema_higher_tf_ok = last_closed_price < ema_higher_tf
                
            validations[f'ema{self.ema_higher_timeframe_period}_higher_tf'] = {
                'ok': ema_higher_tf_ok,
                'price': last_closed_price,  # Prix de la dernière bougie fermée
                'ema': ema_higher_tf,
                'period': self.ema_higher_timeframe_period
            }
        else:
            validations[f'ema{self.ema_higher_timeframe_period}_higher_tf'] = {
                'ok': False,
                'price': last_closed_price,
                'ema': ema_higher_tf,
                'period': self.ema_higher_timeframe_period
            }
        
        # 2. Validation EMA timeframe current - utilise les vraies données EMA
        ema_current_key = f'EMA_{self.ema_current_period}'
        ema_current = current_tf_ema.get(ema_current_key) if current_tf_ema else None
        
        # Fallback vers l'estimation si pas de vraies données
        if ema_current is None:
            ema_current = self._get_current_ema_value(normal_candle, ha_candle)
        
        if ema_current is not None:
            if signal_type == 'LONG':
                ema_current_ok = last_closed_price > ema_current
            else:  # SHORT
                ema_current_ok = last_closed_price < ema_current
        else:
            # Pas de données EMA current disponibles
            ema_current_ok = False
            ema_current = None
            
        validations[f'ema{self.ema_current_period}_current_tf'] = {
            'ok': ema_current_ok,
            'price': last_closed_price,  # Prix de la dernière bougie fermée
            'ema': ema_current,
            'period': self.ema_current_period
        }
        
        # 3. Validation Volume
        volume_comparison = volume_data.get('volume_comparison', {}) if volume_data else {}
        volume_level = volume_comparison.get('volume_level', 'normal')
        volume_ratio = volume_comparison.get('ratio_vs_recent', 1.0)
        volume_ok = volume_level in ['above_average', 'high', 'very_high']
        
        validations['volume'] = {
            'ok': volume_ok,
            'level': volume_level,
            'ratio': volume_ratio
        }
        
        return validations
    
    def _get_current_ema_value(self, normal_candle, ha_candle):
        """
        Récupère la valeur EMA du timeframe current pour la période configurée
        
        Cette méthode devrait idéalement accéder aux données EMA calculées
        sur le timeframe current, mais pour l'instant utilise une estimation
        basée sur le prix de la dernière bougie fermée.
        
        Args:
            normal_candle: Données de la bougie normale (dernière fermée)
            ha_candle: Données de la bougie Heikin Ashi
            
        Returns:
            float: Valeur EMA estimée ou None si non disponible
        """
        try:
            # Récupérer le prix de la dernière bougie fermée
            last_price = normal_candle['close']
            
            # TODO: Intégration avec le système d'indicateurs pour récupérer la vraie EMA
            # Pour l'instant, nous utilisons une estimation basée sur le prix
            # Une vraie implémentation nécessiterait de calculer l'EMA sur les données historiques
            
            # Estimation simple : EMA généralement en dessous du prix pour tendances haussières
            # et au-dessus pour tendances baissières
            # Cette logique sera remplacée par de vraies données EMA dans une version future
            
            if self.ema_current_period == 50:
                # EMA50 estimation (ajustement basé sur volatilité moyenne)
                ema_adjustment = last_price * 0.005  # 0.5% d'écart approximatif
                return last_price - ema_adjustment
            elif self.ema_current_period == 20:
                # EMA20 suit le prix de plus près
                ema_adjustment = last_price * 0.002  # 0.2% d'écart approximatif
                return last_price - ema_adjustment
            else:
                # Estimation générique pour autres périodes
                ema_adjustment = last_price * (0.01 / self.ema_current_period)
                return last_price - ema_adjustment
                
        except Exception as e:
            print(f"Erreur récupération EMA current: {e}")
            return None
    
    def _create_optimized_signal(self, signal_type, steps, validations):
        """Crée un signal optimisé avec scoring"""
        # Calculer le score (2 minimum RSI + HA + validations)
        score = 2  # RSI + HA toujours validés
        total_conditions = 5  # RSI + HA + EMA200 + EMA50 + Volume
        
        for validation in validations.values():
            if validation.get('ok', False):
                score += 1
        
        signal = {
            'type': signal_type,
            'timestamp': datetime.now().isoformat(),
            'score': f"{score}/{total_conditions}",
            'steps': steps,
            'validations': validations
        }
        
        if self.log_signals:
            self._log_signal(signal)
        
        return signal
    
    def _log_signal(self, signal):
        """Log un signal dans un fichier de manière robuste"""
        try:
            # Nettoyer les données pour assurer la sérialisabilité JSON
            clean_signal = self._clean_signal_for_json(signal)
            
            log_entry = {
                'signal': clean_signal,
                'logged_at': datetime.now().isoformat()
            }
            
            # Créer le répertoire logs s'il n'existe pas
            import os
            os.makedirs('logs', exist_ok=True)
            
            # Écrire dans le fichier de log
            log_file = f"logs/signals_{datetime.now().strftime('%Y-%m-%d')}.json"
            temp_file = log_file + '.tmp'
            
            # Lire les entrées existantes
            existing_logs = []
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content and content.startswith('['):
                            existing_logs = json.loads(content)
                except Exception as read_error:
                    print(f"Avertissement: Impossible de lire le log existant ({read_error}), nouveau fichier créé")
                    existing_logs = []
            
            # Ajouter la nouvelle entrée
            existing_logs.append(log_entry)
            
            # Écrire dans un fichier temporaire d'abord (atomic write)
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_logs, f, indent=2, ensure_ascii=False, default=str)
                    f.flush()
                    os.fsync(f.fileno())  # Force write to disk
                
                # Renommer le fichier temporaire (operation atomique sur la plupart des systèmes)
                if os.path.exists(log_file):
                    os.replace(temp_file, log_file)
                else:
                    os.rename(temp_file, log_file)
                
                print(f"SIGNAL {signal['type']} DETECTE - {signal['timestamp']} - Log: {log_file}")
                
            except Exception as write_error:
                # Nettoyer le fichier temporaire en cas d'erreur
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                raise write_error
            
        except Exception as e:
            print(f"Erreur lors du logging du signal: {e}")
            # Essayer un logging de fallback en mode append
            try:
                fallback_file = f"logs/signals_fallback_{datetime.now().strftime('%Y-%m-%d')}.txt"
                with open(fallback_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n--- Signal {datetime.now().isoformat()} ---\n")
                    f.write(f"Type: {signal.get('type', 'Unknown')}\n")
                    f.write(f"Score: {signal.get('score', 'N/A')}\n")
                    f.write(f"Timestamp: {signal.get('timestamp', 'N/A')}\n")
                    f.write(f"Error: {e}\n")
                print(f"Signal sauvegardé en mode fallback: {fallback_file}")
            except:
                print("Impossible de sauvegarder le signal, même en mode fallback")
    
    def _clean_signal_for_json(self, signal):
        """Nettoie les données du signal pour assurer la compatibilité JSON"""
        def clean_value(value):
            """Nettoie récursivement une valeur pour JSON"""
            if value is None:
                return None
            elif isinstance(value, (str, int, float, bool)):
                return value
            elif isinstance(value, dict):
                return {k: clean_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [clean_value(item) for item in value]
            elif hasattr(value, 'isoformat'):  # datetime objects
                return value.isoformat()
            else:
                # Convertir tout autre type en string
                return str(value)
        
        try:
            return clean_value(signal)
        except Exception as e:
            print(f"Erreur lors du nettoyage du signal: {e}")
            # Retourner une version minimale en cas d'erreur
            return {
                'type': str(signal.get('type', 'Unknown')),
                'timestamp': str(signal.get('timestamp', datetime.now().isoformat())),
                'score': str(signal.get('score', 'N/A')),
                'error': f"Erreur nettoyage: {e}"
            }
    
    def _reset_long_state(self):
        """Remet à zéro l'état LONG"""
        self.long_state = SignalState.IDLE
        self.long_steps.clear()
    
    def _reset_short_state(self):
        """Remet à zéro l'état SHORT"""
        self.short_state = SignalState.IDLE
        self.short_steps.clear()
    
    def get_status(self):
        """Retourne le statut actuel du détecteur"""
        return {
            'enabled': self.enabled,
            'long_state': self.long_state.value,
            'short_state': self.short_state.value,
            'long_steps_count': len(self.long_steps),
            'short_steps_count': len(self.short_steps),
            'last_validation': self.last_validation_time.isoformat() if self.last_validation_time else None
        }