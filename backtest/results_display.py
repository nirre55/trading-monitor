#!/usr/bin/env python3
"""
Module d'affichage des résultats de backtest
Génère des rapports détaillés et des visualisations
"""

import pandas as pd
import os
from datetime import datetime
from typing import Dict, List
import json

class BacktestResultsDisplay:
    """Générateur de rapports de backtest"""
    
    def __init__(self):
        self.results_dir = "backtest/results"
        os.makedirs(self.results_dir, exist_ok=True)
    
    def display_summary(self, results: Dict):
        """Affiche un résumé des résultats dans la console"""
        
        print("\n" + "="*60)
        print("📊 RÉSULTATS DU BACKTEST")
        print("="*60)
        
        # Performance générale
        initial_balance = results['initial_balance']
        final_balance = results['final_balance']
        total_return = results['total_return_pct']
        
        print(f"💰 Capital initial: {initial_balance:,.2f} USDT")
        print(f"💰 Capital final: {final_balance:,.2f} USDT")
        print(f"📈 Rendement total: {total_return:+.2f}%")
        
        if 'error' in results.get('statistics', {}):
            print(f"❌ {results['statistics']['error']}")
            return
        
        stats = results['statistics']
        
        print(f"\n📊 STATISTIQUES DE TRADING")
        print(f"🔢 Nombre total de trades: {stats['total_trades']}")
        print(f"✅ Trades gagnants: {stats['winning_trades']} ({stats['win_rate_pct']:.1f}%)")
        print(f"❌ Trades perdants: {stats['losing_trades']}")
        print(f"📡 Signaux détectés: {stats['signals_detected']}")
        print(f"📊 Taux de conversion signaux→trades: {stats['signal_conversion_rate']:.1f}%")
        
        print(f"\n💹 ANALYSE P&L")
        print(f"💰 P&L total: {stats['total_pnl']:+,.2f} USDT")
        print(f"🟢 Gain moyen: +{stats['avg_win']:.2f} USDT")
        print(f"🔴 Perte moyenne: {stats['avg_loss']:.2f} USDT")
        print(f"⚖️ Profit Factor: {stats['profit_factor']:.2f}")
        print(f"📉 Drawdown max: {stats['max_drawdown_pct']:.2f}%")
        
        # Séries consécutives
        print(f"\n🔄 SÉRIES CONSÉCUTIVES")
        print(f"🏆 Max trades gagnants consécutifs: {stats.get('max_consecutive_wins', 0)}")
        print(f"💥 Max trades perdants consécutifs: {stats.get('max_consecutive_losses', 0)}")
        
        current_streak = stats.get('current_streak', 0)
        current_streak_type = stats.get('current_streak_type', 'none')
        if current_streak > 0:
            streak_icon = "🟢" if current_streak_type == 'wins' else "🔴"
            streak_text = "gagnants" if current_streak_type == 'wins' else "perdants"
            print(f"{streak_icon} Série actuelle: {current_streak} trades {streak_text}")
        else:
            print("⚪ Série actuelle: Aucune")
        
        # Durée moyenne
        avg_duration = stats['avg_duration']
        if hasattr(avg_duration, 'total_seconds'):
            hours = avg_duration.total_seconds() / 3600
            print(f"\n⏱️ Durée moyenne trade: {hours:.1f}h")
        
        print("\n" + "="*60)
    
    def generate_detailed_report(self, results: Dict, symbol: str, timeframe: str) -> str:
        """
        Génère un rapport détaillé en format texte
        
        Args:
            results: Résultats du backtest
            symbol: Symbole tradé
            timeframe: Timeframe utilisé
            
        Returns:
            Chemin vers le fichier de rapport généré
        """
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"backtest_report_{symbol}_{timeframe}_{timestamp}.txt"
        report_path = os.path.join(self.results_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("RAPPORT DE BACKTEST DÉTAILLÉ\n")
            f.write("="*50 + "\n\n")
            
            f.write(f"Symbole: {symbol}\n")
            f.write(f"Timeframe: {timeframe}\n")
            f.write(f"Date du rapport: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Résultats généraux
            f.write("RÉSULTATS GÉNÉRAUX\n")
            f.write("-"*20 + "\n")
            f.write(f"Capital initial: {results['initial_balance']:,.2f} USDT\n")
            f.write(f"Capital final: {results['final_balance']:,.2f} USDT\n")
            f.write(f"Rendement total: {results['total_return_pct']:+.2f}%\n\n")
            
            if 'error' in results.get('statistics', {}):
                f.write(f"ERREUR: {results['statistics']['error']}\n")
                return report_path
            
            stats = results['statistics']
            
            # Statistiques de trading
            f.write("STATISTIQUES DE TRADING\n")
            f.write("-"*25 + "\n")
            f.write(f"Nombre total de trades: {stats['total_trades']}\n")
            f.write(f"Trades gagnants: {stats['winning_trades']} ({stats['win_rate_pct']:.1f}%)\n")
            f.write(f"Trades perdants: {stats['losing_trades']}\n")
            f.write(f"Signaux détectés: {stats['signals_detected']}\n")
            f.write(f"Taux de conversion: {stats['signal_conversion_rate']:.1f}%\n\n")
            
            # Analyse P&L
            f.write("ANALYSE P&L\n")
            f.write("-"*12 + "\n")
            f.write(f"P&L total: {stats['total_pnl']:+,.2f} USDT\n")
            f.write(f"Gain moyen: +{stats['avg_win']:.2f} USDT\n")
            f.write(f"Perte moyenne: {stats['avg_loss']:.2f} USDT\n")
            f.write(f"Profit Factor: {stats['profit_factor']:.2f}\n")
            f.write(f"Drawdown max: {stats['max_drawdown_pct']:.2f}%\n\n")
            
            # Détail des trades
            trades = results['trades']
            if trades:
                f.write("DÉTAIL DES TRADES\n")
                f.write("-"*17 + "\n")
                
                for i, trade in enumerate(trades, 1):
                    f.write(f"Trade #{i}:\n")
                    f.write(f"  Type: {trade['type']}\n")
                    f.write(f"  Entrée: {trade['entry_time']} @ {trade['entry_price']:.2f}\n")
                    f.write(f"  Sortie: {trade['exit_time']} @ {trade['exit_price']:.2f}\n")
                    f.write(f"  P&L: {trade['pnl']:+.2f} USDT ({trade['pnl_pct']:+.2f}%)\n")
                    f.write(f"  Raison: {trade['reason']}\n")
                    f.write(f"  Score signal: {trade['signal_score']}\n")
                    f.write(f"  Durée: {trade['duration']}\n\n")
            
            # Signaux détectés
            signals = results['signals_detected']
            if signals:
                f.write("SIGNAUX DÉTECTÉS\n")
                f.write("-"*16 + "\n")
                
                for i, signal in enumerate(signals, 1):
                    f.write(f"Signal #{i}:\n")
                    f.write(f"  Timestamp: {signal['timestamp']}\n")
                    f.write(f"  Type: {signal['type']}\n")
                    f.write(f"  Prix: {signal['price']:.2f}\n")
                    f.write(f"  Score: {signal['score']}\n")
                    
                    # Validations du signal
                    validations = signal.get('validations', {})
                    for val_name, val_data in validations.items():
                        status = "✓" if val_data.get('ok', False) else "✗"
                        f.write(f"    {val_name}: {status}\n")
                    f.write("\n")
        
        print(f"📄 Rapport détaillé sauvegardé: {report_path}")
        return report_path
    
    def export_to_csv(self, results: Dict, symbol: str, timeframe: str) -> Dict[str, str]:
        """
        Exporte les résultats en fichiers CSV
        
        Args:
            results: Résultats du backtest
            symbol: Symbole tradé
            timeframe: Timeframe utilisé
            
        Returns:
            Dictionnaire avec les chemins des fichiers créés
        """
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        files_created = {}
        
        # Export des trades
        if results['trades']:
            trades_df = pd.DataFrame(results['trades'])
            trades_filename = f"trades_{symbol}_{timeframe}_{timestamp}.csv"
            trades_path = os.path.join(self.results_dir, trades_filename)
            trades_df.to_csv(trades_path, index=False)
            files_created['trades'] = trades_path
            print(f"📊 Trades exportés: {trades_path}")
        
        # Export de l'equity curve
        if results['equity_curve']:
            equity_df = pd.DataFrame(results['equity_curve'])
            equity_filename = f"equity_curve_{symbol}_{timeframe}_{timestamp}.csv"
            equity_path = os.path.join(self.results_dir, equity_filename)
            equity_df.to_csv(equity_path, index=False)
            files_created['equity_curve'] = equity_path
            print(f"📈 Equity curve exportée: {equity_path}")
        
        # Export des signaux
        if results['signals_detected']:
            signals_df = pd.DataFrame(results['signals_detected'])
            
            # Aplatir les validations pour le CSV
            validations_expanded = []
            for signal in results['signals_detected']:
                row = {
                    'timestamp': signal['timestamp'],
                    'type': signal['type'],
                    'price': signal['price'],
                    'score': signal['score']
                }
                
                # Ajouter chaque validation comme colonne
                validations = signal.get('validations', {})
                for val_name, val_data in validations.items():
                    row[f'{val_name}_ok'] = val_data.get('ok', False)
                    if 'price' in val_data:
                        row[f'{val_name}_price'] = val_data['price']
                    if 'ema' in val_data:
                        row[f'{val_name}_ema'] = val_data['ema']
                
                validations_expanded.append(row)
            
            signals_df = pd.DataFrame(validations_expanded)
            signals_filename = f"signals_{symbol}_{timeframe}_{timestamp}.csv"
            signals_path = os.path.join(self.results_dir, signals_filename)
            signals_df.to_csv(signals_path, index=False)
            files_created['signals'] = signals_path
            print(f"📡 Signaux exportés: {signals_path}")
        
        return files_created
    
    def save_json_results(self, results: Dict, symbol: str, timeframe: str) -> str:
        """
        Sauvegarde les résultats complets en JSON
        
        Args:
            results: Résultats du backtest
            symbol: Symbole tradé
            timeframe: Timeframe utilisé
            
        Returns:
            Chemin vers le fichier JSON créé
        """
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"backtest_results_{symbol}_{timeframe}_{timestamp}.json"
        json_path = os.path.join(self.results_dir, json_filename)
        
        # Convertir les timestamps en strings pour JSON
        results_copy = results.copy()
        
        # Convertir les trades
        if results_copy.get('trades'):
            for trade in results_copy['trades']:
                trade['entry_time'] = trade['entry_time'].isoformat() if hasattr(trade['entry_time'], 'isoformat') else str(trade['entry_time'])
                trade['exit_time'] = trade['exit_time'].isoformat() if hasattr(trade['exit_time'], 'isoformat') else str(trade['exit_time'])
                trade['duration'] = str(trade['duration'])
        
        # Convertir l'equity curve
        if results_copy.get('equity_curve'):
            for point in results_copy['equity_curve']:
                point['timestamp'] = point['timestamp'].isoformat() if hasattr(point['timestamp'], 'isoformat') else str(point['timestamp'])
        
        # Convertir les signaux
        if results_copy.get('signals_detected'):
            for signal in results_copy['signals_detected']:
                signal['timestamp'] = signal['timestamp'].isoformat() if hasattr(signal['timestamp'], 'isoformat') else str(signal['timestamp'])
        
        # Convertir les statistiques
        if 'avg_duration' in results_copy.get('statistics', {}):
            avg_dur = results_copy['statistics']['avg_duration']
            results_copy['statistics']['avg_duration'] = str(avg_dur)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results_copy, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📁 Résultats JSON sauvegardés: {json_path}")
        return json_path
    
    def display_trade_analysis(self, results: Dict):
        """Affiche une analyse détaillée des trades"""
        
        trades = results.get('trades', [])
        if not trades:
            print("Aucun trade à analyser")
            return
        
        trades_df = pd.DataFrame(trades)
        
        print(f"\n📊 ANALYSE DÉTAILLÉE DES TRADES")
        print("-"*40)
        
        # Analyse par type de signal
        print("Répartition par type:")
        type_analysis = trades_df.groupby('type').agg({
            'pnl': ['count', 'mean', 'sum'],
            'pnl_pct': 'mean'
        }).round(2)
        
        for signal_type in trades_df['type'].unique():
            type_trades = trades_df[trades_df['type'] == signal_type]
            count = len(type_trades)
            avg_pnl = type_trades['pnl'].mean()
            total_pnl = type_trades['pnl'].sum()
            win_rate = (len(type_trades[type_trades['pnl'] > 0]) / count) * 100
            
            print(f"  {signal_type}: {count} trades, {win_rate:.1f}% win rate, P&L moyen: {avg_pnl:+.2f}, Total: {total_pnl:+.2f}")
        
        # Analyse par score de signal
        print(f"\nAnalyse par score de signal:")
        score_analysis = trades_df.groupby('signal_score').agg({
            'pnl': ['count', 'mean'],
        }).round(2)
        
        for score in sorted(trades_df['signal_score'].unique()):
            score_trades = trades_df[trades_df['signal_score'] == score]
            count = len(score_trades)
            avg_pnl = score_trades['pnl'].mean()
            win_rate = (len(score_trades[score_trades['pnl'] > 0]) / count) * 100
            
            print(f"  Score {score}: {count} trades, {win_rate:.1f}% win rate, P&L moyen: {avg_pnl:+.2f}")
        
        # Analyse par raison de sortie
        print(f"\nAnalyse par raison de sortie:")
        reason_analysis = trades_df.groupby('reason').agg({
            'pnl': ['count', 'mean'],
        }).round(2)
        
        for reason in trades_df['reason'].unique():
            reason_trades = trades_df[trades_df['reason'] == reason]
            count = len(reason_trades)
            avg_pnl = reason_trades['pnl'].mean()
            
            print(f"  {reason}: {count} trades, P&L moyen: {avg_pnl:+.2f}")
    
    def list_results_files(self) -> List[Dict]:
        """Liste tous les fichiers de résultats disponibles"""
        
        if not os.path.exists(self.results_dir):
            return []
        
        files = []
        for filename in os.listdir(self.results_dir):
            filepath = os.path.join(self.results_dir, filename)
            if os.path.isfile(filepath):
                files.append({
                    'filename': filename,
                    'filepath': filepath,
                    'size_mb': os.path.getsize(filepath) / (1024 * 1024),
                    'modified': datetime.fromtimestamp(os.path.getmtime(filepath))
                })
        
        return sorted(files, key=lambda x: x['modified'], reverse=True)