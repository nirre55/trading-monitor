#!/usr/bin/env python3
"""
Script principal de backtest pour les signaux de trading
Interface complète pour télécharger les données et lancer les backtests
"""

import sys
import os
from datetime import datetime, timedelta
import argparse

# Ajouter le dossier backtest au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backtest'))

from backtest.data_downloader import BinanceDataDownloader
from backtest.signal_backtester import SignalBacktester
from backtest.results_display import BacktestResultsDisplay

def main():
    """Interface principale du backtest"""
    
    parser = argparse.ArgumentParser(description='Backtest des signaux de trading')
    parser.add_argument('action', choices=['download', 'backtest', 'list-data', 'list-results'], 
                       help='Action à effectuer')
    
    # Arguments pour le téléchargement
    parser.add_argument('--symbol', default='BTCUSDC', help='Symbole à télécharger/backtester')
    parser.add_argument('--interval', default='5m', help='Intervalle des bougies')
    parser.add_argument('--days', type=int, default=30, help='Nombre de jours de données')
    parser.add_argument('--start-date', help='Date de début (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='Date de fin (YYYY-MM-DD)')
    
    # Arguments pour le backtest
    parser.add_argument('--csv-file', help='Fichier CSV spécifique pour le backtest')
    parser.add_argument('--balance', type=float, default=10000, help='Capital initial')
    parser.add_argument('--risk', type=float, help='Risque par trade (défaut: utilise BACKTEST_CONFIG)')
    parser.add_argument('--use-config', action='store_true', help='Utiliser entièrement la configuration BACKTEST_CONFIG')
    
    # Options d'export
    parser.add_argument('--export-csv', action='store_true', help='Exporter les résultats en CSV')
    parser.add_argument('--export-json', action='store_true', help='Exporter les résultats en JSON')
    parser.add_argument('--detailed-report', action='store_true', help='Générer un rapport détaillé')
    
    args = parser.parse_args()
    
    print("SYSTEME DE BACKTEST DES SIGNAUX DE TRADING")
    print("=" * 50)
    
    if args.action == 'download':
        download_data(args)
    elif args.action == 'backtest':
        run_backtest(args)
    elif args.action == 'list-data':
        list_data_files()
    elif args.action == 'list-results':
        list_results_files()

def download_data(args):
    """Télécharge les données historiques"""
    
    print(f"📥 TÉLÉCHARGEMENT DES DONNÉES")
    print(f"Symbole: {args.symbol}")
    print(f"Intervalle: {args.interval}")
    
    downloader = BinanceDataDownloader()
    
    try:
        if args.start_date and args.end_date:
            filepath = downloader.download_historical_data(
                symbol=args.symbol,
                interval=args.interval,
                start_date=args.start_date,
                end_date=args.end_date
            )
        else:
            filepath = downloader.download_historical_data(
                symbol=args.symbol,
                interval=args.interval,
                days_back=args.days
            )
        
        print(f"\n✅ Téléchargement terminé !")
        print(f"📁 Fichier créé: {filepath}")
        print(f"💡 Pour lancer le backtest: python backtest_runner.py backtest --csv-file \"{filepath}\"")
        
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement: {e}")
        sys.exit(1)

def run_backtest(args):
    """Lance un backtest complet"""
    
    print(f"📊 LANCEMENT DU BACKTEST")
    
    # Déterminer le fichier CSV à utiliser
    csv_file = args.csv_file
    
    if not csv_file:
        # Chercher le fichier le plus récent pour le symbole/intervalle
        downloader = BinanceDataDownloader()
        available_files = downloader.list_available_data()
        
        matching_files = [
            f for f in available_files 
            if f['symbol'] == args.symbol and f['interval'] == args.interval
        ]
        
        if not matching_files:
            print(f"❌ Aucun fichier de données trouvé pour {args.symbol} {args.interval}")
            print(f"💡 Utilisez: python backtest_runner.py download --symbol {args.symbol} --interval {args.interval}")
            sys.exit(1)
        
        # Prendre le plus récent
        csv_file_raw = matching_files[-1]['filepath']
        
        # Vérification de type pour Pylance
        if not isinstance(csv_file_raw, str):
            print(f"❌ Erreur: chemin de fichier invalide")
            sys.exit(1)
            
        csv_file = csv_file_raw
        print(f"📁 Utilisation du fichier: {csv_file}")
    
    # Vérifier que le fichier existe
    if not os.path.exists(csv_file):
        print(f"❌ Fichier non trouvé: {csv_file}")
        sys.exit(1)
    
    # Configuration du backtest
    print(f"⚙️ Configuration:")
    print(f"  Capital initial: {args.balance:,.2f} USDT")
    
    # Utiliser le risque fourni ou celui de la config
    risk_per_trade = args.risk
    if args.use_config or risk_per_trade is None:
        print(f"  ✅ Utilisation de BACKTEST_CONFIG pour tous les paramètres")
    else:
        print(f"  Risque par trade personnalisé: {risk_per_trade*100}%")
    
    # Lancer le backtest
    backtester = SignalBacktester(
        initial_balance=args.balance,
        risk_per_trade=risk_per_trade
    )
    
    try:
        results = backtester.run_backtest(
            csv_path=csv_file,
            symbol=args.symbol,
            timeframe=args.interval
        )
        
        # Afficher les résultats
        display = BacktestResultsDisplay()
        display.display_summary(results)
        display.display_trade_analysis(results)
        
        # Exports optionnels
        if args.export_csv or args.export_json or args.detailed_report:
            print(f"\n📤 EXPORT DES RÉSULTATS")
        
        if args.export_csv:
            csv_files = display.export_to_csv(results, args.symbol, args.interval)
            print(f"✅ Fichiers CSV créés: {len(csv_files)}")
        
        if args.export_json:
            json_file = display.save_json_results(results, args.symbol, args.interval)
            print(f"✅ Fichier JSON créé: {json_file}")
        
        if args.detailed_report:
            report_file = display.generate_detailed_report(results, args.symbol, args.interval)
            print(f"✅ Rapport détaillé créé: {report_file}")
        
        # Conseils pour l'optimisation
        print(f"\n💡 CONSEILS D'OPTIMISATION")
        stats = results.get('statistics', {})
        
        if 'win_rate_pct' in stats:
            win_rate = stats['win_rate_pct']
            if win_rate < 40:
                print(f"⚠️ Taux de réussite faible ({win_rate:.1f}%) - Considérez ajuster les seuils RSI")
            elif win_rate > 70:
                print(f"✅ Excellent taux de réussite ({win_rate:.1f}%)")
        
        if 'profit_factor' in stats:
            pf = stats['profit_factor']
            if pf < 1.0:
                print(f"⚠️ Profit Factor < 1.0 ({pf:.2f}) - Stratégie perdante")
            elif pf > 2.0:
                print(f"✅ Excellent Profit Factor ({pf:.2f})")
        
        if 'max_drawdown_pct' in stats:
            dd = abs(stats['max_drawdown_pct'])
            if dd > 20:
                print(f"⚠️ Drawdown élevé ({dd:.1f}%) - Réduisez le risque par trade")
        
    except Exception as e:
        print(f"❌ Erreur lors du backtest: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def list_data_files():
    """Liste les fichiers de données disponibles"""
    
    print("📁 FICHIERS DE DONNÉES DISPONIBLES")
    print("-" * 40)
    
    downloader = BinanceDataDownloader()
    files = downloader.list_available_data()
    
    if not files:
        print("Aucun fichier de données trouvé.")
        print("💡 Utilisez: python backtest_runner.py download --symbol BTCUSDC --interval 5m")
        return
    
    for file_info in files:
        print(f"📊 {file_info['filename']}")
        print(f"   Symbole: {file_info['symbol']}")
        print(f"   Intervalle: {file_info['interval']}")
        print(f"   Période: {file_info['start_date']} → {file_info['end_date']}")
        print(f"   Taille: {file_info['size_mb']:.1f} MB")
        print(f"   Chemin: {file_info['filepath']}")
        print()

def list_results_files():
    """Liste les fichiers de résultats disponibles"""
    
    print("📊 FICHIERS DE RÉSULTATS DISPONIBLES")
    print("-" * 40)
    
    display = BacktestResultsDisplay()
    files = display.list_results_files()
    
    if not files:
        print("Aucun fichier de résultats trouvé.")
        print("💡 Lancez d'abord un backtest avec: python backtest_runner.py backtest")
        return
    
    for file_info in files:
        print(f"📄 {file_info['filename']}")
        print(f"   Modifié: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Taille: {file_info['size_mb']:.1f} MB")
        print(f"   Chemin: {file_info['filepath']}")
        print()

def show_examples():
    """Affiche des exemples d'utilisation"""
    
    print("\n💡 EXEMPLES D'UTILISATION")
    print("-" * 25)
    print()
    
    print("1. Télécharger 30 jours de données BTCUSDC 5m:")
    print("   python backtest_runner.py download --symbol BTCUSDC --interval 5m --days 30")
    print()
    
    print("2. Télécharger une période spécifique:")
    print("   python backtest_runner.py download --symbol ETHUSDT --interval 1h --start-date 2025-01-01 --end-date 2025-01-15")
    print()
    
    print("3. Lancer un backtest avec export complet:")
    print("   python backtest_runner.py backtest --symbol BTCUSDC --interval 5m --balance 50000 --risk 0.01 --export-csv --export-json --detailed-report")
    print()
    
    print("4. Backtest avec paramètres personnalisés:")
    print("   python backtest_runner.py backtest --csv-file \"backtest/data/BTCUSDC_5m_20250101_20250115.csv\" --stop-loss 0.015 --take-profit 0.05")
    print()
    
    print("5. Lister les données disponibles:")
    print("   python backtest_runner.py list-data")
    print()
    
    print("6. Lister les résultats de backtest:")
    print("   python backtest_runner.py list-results")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("SYSTEME DE BACKTEST DES SIGNAUX DE TRADING")
        print("=" * 50)
        print()
        print("Usage: python backtest_runner.py {download|backtest|list-data|list-results} [options]")
        print()
        print("Pour voir l'aide détaillée: python backtest_runner.py -h")
        show_examples()
        sys.exit(1)
    
    main()