#!/usr/bin/env python3
"""
Module de backtest pour les signaux de trading
Utilise les mêmes indicateurs que le système de monitoring en temps réel
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sys
import os

# Ajouter le chemin parent pour importer les modules existants
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from indicators.calculator import IndicatorCalculator
import config

class SignalBacktester:
    """
    Backtester pour les signaux de trading
    Réutilise exactement la même logique que le système en temps réel
    """
    
    def __init__(self, initial_balance: float = 10000, risk_per_trade: float = None, silent: bool = False):
        """
        Initialise le backtester
        
        Args:
            initial_balance: Capital initial en USDT
            risk_per_trade: Risque par trade (None = utilise config.BACKTEST_CONFIG)
            silent: Mode silencieux (pas d'affichage)
        """
        self.initial_balance = initial_balance
        self.silent = silent
        
        # Charger la configuration backtest
        backtest_config = getattr(config, 'BACKTEST_CONFIG', {})
        
        # Utiliser la config si pas de paramètre fourni
        self.risk_per_trade = risk_per_trade if risk_per_trade is not None else backtest_config.get('RISK_PER_TRADE', 0.02)
        
        # Méthode de calcul SL/TP
        self.sl_method = backtest_config.get('SL_METHOD', 'ATR')
        
        # Configuration ATR
        self.sl_atr_multiplier = backtest_config.get('STOP_LOSS_ATR_MULTIPLIER', 1.0)
        self.tp_atr_multiplier = backtest_config.get('TAKE_PROFIT_ATR_MULTIPLIER', 2.0)
        self.atr_period_for_stops = backtest_config.get('ATR_PERIOD_FOR_STOPS', 14)
        
        # Configuration Swing Levels
        self.swing_lookback_candles = backtest_config.get('SWING_LOOKBACK_CANDLES', 5)
        self.swing_offset_pct = backtest_config.get('SWING_OFFSET_PCT', 0.1)
        self.swing_tp_ratio = backtest_config.get('SWING_TP_RATIO', 5.0)
        
        # Configuration Take Profit
        self.tp_method = backtest_config.get('TP_METHOD', 'RATIO')
        self.fixed_tp_pct = backtest_config.get('FIXED_TP_PCT', 1.5)
        
        # Paramètres communs
        self.min_risk_reward_ratio = backtest_config.get('MIN_RISK_REWARD_RATIO', 1.5)
        self.max_position_size_pct = backtest_config.get('MAX_POSITION_SIZE_PCT', 0.95)
        self.use_trailing_stop = backtest_config.get('USE_TRAILING_STOP', False)
        self.trailing_stop_atr_multiplier = backtest_config.get('TRAILING_STOP_ATR_MULTIPLIER', 1.5)
        
        # Initialiser le calculateur d'indicateurs
        self.calculator = IndicatorCalculator()
        
        # Résultats du backtest
        self.reset_results()
        
        if not self.silent:
            print(f"Backtester initialise - Capital: {initial_balance} USDT, Risque: {self.risk_per_trade*100}%")
            if self.sl_method == 'ATR':
                if self.tp_method == 'FIXED_PCT':
                    print(f"Methode SL: ATR{self.atr_period_for_stops} ({self.sl_atr_multiplier}x), TP: Fixe {self.fixed_tp_pct}%")
                else:
                    print(f"Methode SL/TP: ATR - SL: {self.sl_atr_multiplier}x ATR{self.atr_period_for_stops}, TP: {self.tp_atr_multiplier}x ATR{self.atr_period_for_stops}")
            else:  # SWING_LEVELS
                if self.tp_method == 'FIXED_PCT':
                    print(f"Methode SL: SWING_LEVELS (Lookback: {self.swing_lookback_candles}, Offset: {self.swing_offset_pct}%), TP: Fixe {self.fixed_tp_pct}%")
                else:
                    print(f"Methode SL/TP: SWING_LEVELS - Lookback: {self.swing_lookback_candles} bougies, Offset: {self.swing_offset_pct}%, TP Ratio: {self.swing_tp_ratio}x")
    
    def reset_results(self):
        """Remet à zéro les résultats"""
        self.balance = self.initial_balance
        self.equity_curve = []
        self.trades = []
        self.signals_detected = []
        self.current_position = None
        self.stats = {}
    
    def load_data(self, csv_path: str) -> pd.DataFrame:
        """
        Charge les données historiques depuis un fichier CSV
        
        Args:
            csv_path: Chemin vers le fichier CSV
            
        Returns:
            DataFrame avec les données
        """
        print(f"📁 Chargement des données: {csv_path}")
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Fichier non trouvé: {csv_path}")
        
        df = pd.read_csv(csv_path)
        
        # Vérifier les colonnes nécessaires
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Colonnes manquantes: {missing_columns}")
        
        # Convertir les timestamps
        df['open_time'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('open_time').reset_index(drop=True)
        
        print(f"✅ {len(df)} bougies chargées")
        print(f"📅 Période: {df['timestamp'].iloc[0]} à {df['timestamp'].iloc[-1]}")
        
        return df
    
    def run_backtest(
        self, 
        csv_path: str, 
        symbol: str = "BTCUSDC", 
        timeframe: str = "5m"
    ) -> Dict:
        """
        Lance le backtest complet
        
        Args:
            csv_path: Chemin vers les données CSV
            symbol: Symbole tradé
            timeframe: Timeframe des données
            
        Returns:
            Dictionnaire avec tous les résultats
        """
        print(f"\n🚀 DÉBUT DU BACKTEST")
        print(f"📊 Paramètres ATR: SL={self.sl_atr_multiplier}x ATR{self.atr_period_for_stops}, TP={self.tp_atr_multiplier}x ATR{self.atr_period_for_stops}")
        print("=" * 50)
        
        # Charger les données
        df = self.load_data(csv_path)
        self.reset_results()
        
        # Variables pour le sliding window
        min_candles_needed = max(config.RSI_PERIODS) + 200 + 50  # RSI + EMA200 + marge
        
        if len(df) < min_candles_needed:
            raise ValueError(f"Pas assez de données. Minimum: {min_candles_needed}, disponible: {len(df)}")
        
        print(f"🔄 Analyse de {len(df)} bougies (fenêtre min: {min_candles_needed})")
        
        # Backtest bougie par bougie
        for i in range(min_candles_needed, len(df)):
            current_candle = df.iloc[i]
            historical_data = df.iloc[:i+1]  # Toutes les données jusqu'à cette bougie
            
            # Calculer les indicateurs pour cette bougie
            indicators = self.calculator.calculate_all_indicators(
                historical_data, symbol, timeframe
            )
            
            if not indicators.get('has_data', False):
                continue
            
            # Analyser les signaux
            signal_analysis = indicators.get('signal_analysis', {})
            new_signals = signal_analysis.get('signals_detected', [])
            
            current_time = pd.to_datetime(current_candle['timestamp'])
            current_price = current_candle['close']
            
            # Traiter les nouveaux signaux
            for signal in new_signals:
                self._process_signal(signal, current_price, current_time, indicators, historical_data)
            
            # Vérifier les positions ouvertes
            self._check_open_positions(current_candle, current_time)
            
            # Enregistrer l'équité
            self.equity_curve.append({
                'timestamp': current_time,
                'balance': self.balance,
                'price': current_price,
                'position': self.current_position['type'] if self.current_position else None
            })
            
            # Affichage du progrès
            if i % 1000 == 0 or i == len(df) - 1:
                progress = (i - min_candles_needed) / (len(df) - min_candles_needed) * 100
                print(f"🔄 Progrès: {progress:.1f}% - Bougie: {current_candle['timestamp']} - Balance: {self.balance:.2f}")
        
        # Fermer la position ouverte si il y en a une
        if self.current_position:
            final_candle = df.iloc[-1]
            self._close_position(final_candle['close'], pd.to_datetime(final_candle['timestamp']), "Fin backtest")
        
        # Calculer les statistiques
        self._calculate_statistics()
        
        print("\n✅ BACKTEST TERMINÉ")
        
        return {
            'initial_balance': self.initial_balance,
            'final_balance': self.balance,
            'total_return_pct': ((self.balance - self.initial_balance) / self.initial_balance) * 100,
            'trades': self.trades,
            'signals_detected': self.signals_detected,
            'equity_curve': self.equity_curve,
            'statistics': self.stats
        }
    
    def _calculate_swing_levels_sl_tp(self, signal_type: str, current_price: float, historical_data: pd.DataFrame):
        """
        Calcule SL/TP basés sur les swing levels (high/low des X dernières bougies)
        
        Args:
            signal_type: 'LONG' ou 'SHORT'
            current_price: Prix d'entrée
            historical_data: Données historiques pour trouver les swing levels
            
        Returns:
            tuple: (stop_loss_price, take_profit_price, swing_level_used)
        """
        # Prendre les X dernières bougies fermées (exclure la bougie actuelle)
        if len(historical_data) < self.swing_lookback_candles + 1:
            return None, None, None
        
        lookback_data = historical_data.iloc[-(self.swing_lookback_candles + 1):-1]  # Exclut la dernière (actuelle)
        
        if signal_type == 'LONG':
            # Pour LONG: SL = plus bas LOW des X bougies - offset%
            swing_level = lookback_data['low'].min()
            stop_loss_price = swing_level * (1 - self.swing_offset_pct / 100)
            
            # TP selon la méthode configurée
            if self.tp_method == 'FIXED_PCT':
                take_profit_price = current_price * (1 + self.fixed_tp_pct / 100)
            else:  # RATIO
                sl_distance = abs(current_price - stop_loss_price)
                take_profit_price = current_price + (sl_distance * self.swing_tp_ratio)
            
        else:  # SHORT
            # Pour SHORT: SL = plus haut HIGH des X bougies + offset%
            swing_level = lookback_data['high'].max()
            stop_loss_price = swing_level * (1 + self.swing_offset_pct / 100)
            
            # TP selon la méthode configurée
            if self.tp_method == 'FIXED_PCT':
                take_profit_price = current_price * (1 - self.fixed_tp_pct / 100)
            else:  # RATIO
                sl_distance = abs(stop_loss_price - current_price)
                take_profit_price = current_price - (sl_distance * self.swing_tp_ratio)
        
        return stop_loss_price, take_profit_price, swing_level

    def _process_signal(self, signal: Dict, current_price: float, current_time: pd.Timestamp, 
                       indicators: Dict, historical_data: pd.DataFrame = None):
        """Traite un nouveau signal détecté en utilisant la méthode SL/TP configurée"""
        
        # Enregistrer le signal
        signal_info = {
            'timestamp': current_time,
            'type': signal['type'],
            'price': current_price,
            'score': signal['score'],
            'validations': signal.get('validations', {})
        }
        self.signals_detected.append(signal_info)
        
        # Si on a déjà une position ouverte, ignorer
        if self.current_position:
            return
        
        # Calculer SL/TP selon la méthode configurée
        if self.sl_method == 'ATR':
            # Méthode ATR
            atr_data = indicators.get('atr_data', {})
            atr_values = atr_data.get('values', {})
            atr_key = f'ATR_{self.atr_period_for_stops}'
            current_atr = atr_values.get(atr_key)
            
            if current_atr is None or current_atr <= 0:
                print(f"ATR{self.atr_period_for_stops} non disponible pour signal {signal['type']}, signal ignore")
                return
            
            sl_distance = current_atr * self.sl_atr_multiplier
            tp_distance = current_atr * self.tp_atr_multiplier
            
            if signal['type'] == 'LONG':
                stop_loss_price = current_price - sl_distance
                if self.tp_method == 'FIXED_PCT':
                    take_profit_price = current_price * (1 + self.fixed_tp_pct / 100)
                else:  # RATIO (ATR)
                    take_profit_price = current_price + tp_distance
            elif signal['type'] == 'SHORT':
                stop_loss_price = current_price + sl_distance
                if self.tp_method == 'FIXED_PCT':
                    take_profit_price = current_price * (1 - self.fixed_tp_pct / 100)
                else:  # RATIO (ATR)
                    take_profit_price = current_price - tp_distance
            else:
                return
            
            if self.tp_method == 'FIXED_PCT':
                calculation_info = f"ATR{self.atr_period_for_stops}: {current_atr:.2f}, TP Fixe: {self.fixed_tp_pct}%"
            else:
                calculation_info = f"ATR{self.atr_period_for_stops}: {current_atr:.2f}, TP Ratio: {self.tp_atr_multiplier}x"
            
        else:  # SWING_LEVELS
            # Méthode Swing Levels
            if historical_data is None:
                print(f"Donnees historiques manquantes pour swing levels, signal ignore")
                return
            
            stop_loss_price, take_profit_price, swing_level = self._calculate_swing_levels_sl_tp(
                signal['type'], current_price, historical_data
            )
            
            if stop_loss_price is None or take_profit_price is None:
                print(f"Impossible de calculer swing levels pour signal {signal['type']}, signal ignore")
                return
            
            if self.tp_method == 'FIXED_PCT':
                calculation_info = f"Swing level: {swing_level:.2f}, TP Fixe: {self.fixed_tp_pct}%"
            else:
                calculation_info = f"Swing level: {swing_level:.2f}, TP Ratio: {self.swing_tp_ratio}x"
        
        # Vérifier le ratio risque/récompense
        actual_risk = abs(current_price - stop_loss_price)
        actual_reward = abs(take_profit_price - current_price)
        risk_reward_ratio = actual_reward / actual_risk if actual_risk > 0 else 0
        
        if risk_reward_ratio < self.min_risk_reward_ratio:
            print(f"⚠️ Ratio R/R trop faible ({risk_reward_ratio:.2f} < {self.min_risk_reward_ratio}), signal ignoré")
            return
        
        # Calculer la taille de la position basée sur le risque
        risk_amount = self.balance * self.risk_per_trade
        ideal_position_size = risk_amount / actual_risk if actual_risk > 0 else 0
        
        # Limiter la taille de position au maximum autorisé
        max_position_value = self.balance * self.max_position_size_pct
        max_position_size = max_position_value / current_price
        
        if ideal_position_size <= 0:
            print(f"⚠️ Taille de position invalide ({ideal_position_size}), signal ignoré")
            return
        
        # Utiliser la plus petite valeur entre la position idéale et la position maximale
        position_size = min(ideal_position_size, max_position_size)
        
        # Si on doit limiter la position, recalculer le risque effectif
        effective_risk = position_size * actual_risk
        effective_risk_pct = (effective_risk / self.balance) * 100
        
        if position_size < ideal_position_size:
            print(f"⚠️ Position limitée: {position_size:.4f} (au lieu de {ideal_position_size:.4f}) - Risque effectif: {effective_risk_pct:.2f}%")
        
        # Ouvrir la position
        self.current_position = {
            'type': signal['type'],
            'entry_price': current_price,
            'entry_time': current_time,
            'size': position_size,
            'stop_loss': stop_loss_price,
            'take_profit': take_profit_price,
            'signal_score': signal['score'],
            'calculation_method': self.sl_method,
            'calculation_info': calculation_info,
            'risk_reward_ratio': risk_reward_ratio
        }
        
        print(f"{signal['type']} ouvert @ {current_price:.2f} (Score: {signal['score']}, R/R: {risk_reward_ratio:.2f})")
        sl_distance = abs(current_price - stop_loss_price)
        tp_distance = abs(take_profit_price - current_price)
        print(f"    SL: {stop_loss_price:.2f} (-{sl_distance:.2f}), TP: {take_profit_price:.2f} (+{tp_distance:.2f}) - {calculation_info}")
    
    def _check_open_positions(self, candle: pd.Series, current_time: pd.Timestamp):
        """Vérifie les conditions de sortie pour les positions ouvertes"""
        
        if not self.current_position:
            return
        
        current_price = candle['close']
        high = candle['high']
        low = candle['low']
        
        position = self.current_position
        
        # Vérifier stop loss et take profit
        if position['type'] == 'LONG':
            # Stop loss hit (prix touche le stop loss en bas)
            if low <= position['stop_loss']:
                self._close_position(position['stop_loss'], current_time, "Stop Loss")
                return
            
            # Take profit hit (prix touche le take profit en haut)
            if high >= position['take_profit']:
                self._close_position(position['take_profit'], current_time, "Take Profit")
                return
        
        elif position['type'] == 'SHORT':
            # Stop loss hit (prix touche le stop loss en haut)
            if high >= position['stop_loss']:
                self._close_position(position['stop_loss'], current_time, "Stop Loss")
                return
            
            # Take profit hit (prix touche le take profit en bas)
            if low <= position['take_profit']:
                self._close_position(position['take_profit'], current_time, "Take Profit")
                return
    
    def _close_position(self, exit_price: float, exit_time: pd.Timestamp, reason: str):
        """Ferme la position ouverte"""
        
        if not self.current_position:
            return
        
        position = self.current_position
        
        # Calculer le P&L
        if position['type'] == 'LONG':
            pnl = (exit_price - position['entry_price']) * position['size']
        else:  # SHORT
            pnl = (position['entry_price'] - exit_price) * position['size']
        
        # Mettre à jour le solde
        self.balance += pnl
        
        # Enregistrer le trade
        trade = {
            'entry_time': position['entry_time'],
            'exit_time': exit_time,
            'type': position['type'],
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'size': position['size'],
            'pnl': pnl,
            'pnl_pct': (pnl / (position['size'] * position['entry_price'])) * 100,
            'duration': exit_time - position['entry_time'],
            'reason': reason,
            'signal_score': position['signal_score']
        }
        
        self.trades.append(trade)
        
        print(f"📉 {position['type']} fermé @ {exit_price:.2f} ({reason}) - P&L: {pnl:.2f} ({trade['pnl_pct']:.2f}%) - Balance: {self.balance:.2f}")
        
        # Réinitialiser la position
        self.current_position = None
    
    def _calculate_consecutive_streaks(self, trades_df):
        """
        Calcule les séries consécutives de trades gagnants/perdants
        
        Args:
            trades_df: DataFrame des trades
            
        Returns:
            dict: Statistiques des séries consécutives
        """
        if len(trades_df) == 0:
            return {
                'max_consecutive_wins': 0,
                'max_consecutive_losses': 0,
                'current_streak': 0,
                'current_streak_type': 'none'
            }
        
        # Créer une série de booléens pour les trades gagnants/perdants
        is_winner = trades_df['pnl'] > 0
        
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        current_consecutive_wins = 0
        current_consecutive_losses = 0
        
        # Parcourir tous les trades pour calculer les séries
        for i, winner in enumerate(is_winner):
            if winner:  # Trade gagnant
                current_consecutive_wins += 1
                current_consecutive_losses = 0  # Reset losing streak
                max_consecutive_wins = max(max_consecutive_wins, current_consecutive_wins)
            else:  # Trade perdant
                current_consecutive_losses += 1
                current_consecutive_wins = 0  # Reset winning streak
                max_consecutive_losses = max(max_consecutive_losses, current_consecutive_losses)
        
        # Déterminer la série actuelle (dernier trade)
        if len(is_winner) > 0:
            if is_winner.iloc[-1]:  # Dernier trade gagnant
                current_streak = current_consecutive_wins
                current_streak_type = 'wins'
            else:  # Dernier trade perdant
                current_streak = current_consecutive_losses
                current_streak_type = 'losses'
        else:
            current_streak = 0
            current_streak_type = 'none'
        
        return {
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'current_streak': current_streak,
            'current_streak_type': current_streak_type
        }
    
    def _calculate_statistics(self):
        """Calcule les statistiques de performance"""
        
        if not self.trades:
            self.stats = {'error': 'Aucun trade exécuté'}
            return
        
        trades_df = pd.DataFrame(self.trades)
        
        # Statistiques générales
        total_trades = len(self.trades)
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        losing_trades = len(trades_df[trades_df['pnl'] < 0])
        
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # P&L statistiques
        total_pnl = trades_df['pnl'].sum()
        avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
        
        # Profit factor
        gross_profit = trades_df[trades_df['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(trades_df[trades_df['pnl'] < 0]['pnl'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Drawdown
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df['running_max'] = equity_df['balance'].expanding().max()
        equity_df['drawdown'] = ((equity_df['balance'] - equity_df['running_max']) / equity_df['running_max']) * 100
        max_drawdown = equity_df['drawdown'].min()
        
        # Durée moyenne des trades
        avg_duration = trades_df['duration'].mean()
        
        # Calcul des séries consécutives (winning/losing streaks)
        consecutive_stats = self._calculate_consecutive_streaks(trades_df)
        
        self.stats = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate_pct': win_rate,
            'total_pnl': total_pnl,
            'total_return_pct': ((self.balance - self.initial_balance) / self.initial_balance) * 100,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown_pct': max_drawdown,
            'avg_duration': avg_duration,
            'signals_detected': len(self.signals_detected),
            'signals_traded': total_trades,
            'signal_conversion_rate': (total_trades / len(self.signals_detected)) * 100 if self.signals_detected else 0,
            # Séries consécutives
            'max_consecutive_wins': consecutive_stats['max_consecutive_wins'],
            'max_consecutive_losses': consecutive_stats['max_consecutive_losses'],
            'current_streak': consecutive_stats['current_streak'],
            'current_streak_type': consecutive_stats['current_streak_type']
        }