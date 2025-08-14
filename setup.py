#!/usr/bin/env python3
"""
Script de configuration automatique du projet de monitoring
Crée la structure de dossiers et les fichiers __init__.py nécessaires
"""

import os
import sys

def create_directory_structure():
    """Crée la structure de dossiers nécessaire"""
    directories = [
        "core",
        "indicators", 
        "display",
        "logs"
    ]
    
    print("📁 Création de la structure de dossiers...")
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Dossier créé: {directory}/")
        else:
            print(f"ℹ️ Dossier existe déjà: {directory}/")

def create_init_files():
    """Crée les fichiers __init__.py nécessaires"""
    init_files = {
        "core/__init__.py": '"""Module core pour la gestion des données et connexions"""',
        "indicators/__init__.py": '"""Module indicators pour les calculs d\'indicateurs techniques"""',
        "display/__init__.py": '"""Module display pour l\'affichage et le formatage"""'
    }
    
    print("\n📄 Création des fichiers __init__.py...")
    
    for file_path, content in init_files.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content + '\n')
            print(f"✅ Fichier créé: {file_path}")
        else:
            print(f"ℹ️ Fichier existe déjà: {file_path}")

def create_default_config():
    """Crée un fichier de configuration par défaut si absent"""
    config_path = "config.py"
    
    if os.path.exists(config_path):
        print(f"\nℹ️ Fichier config.py existe déjà")
        return
    
    print(f"\n⚙️ Création du fichier config.py par défaut...")
    
    default_config = '''"""
Configuration du monitoring des bougies et indicateurs
"""

# Configuration principale
SYMBOL = "BTCUSDT"          # Symbole à monitorer
TIMEFRAME = "1m"            # Timeframe (1m, 3m, 5m, 15m, 30m, 1h, etc.)

# Périodes RSI à calculer
RSI_PERIODS = [14, 21]

# Configuration WebSocket
WEBSOCKET_URL = "wss://stream.binance.com:9443/ws/"

# Nombre de bougies historiques pour démarrage
INITIAL_KLINES_LIMIT = 100

# Configuration affichage
DISPLAY_CONFIG = {
    'SHOW_TIMESTAMP': True,
    'SHOW_PRICES': True,
    'SHOW_RSI_VALUES': True,
    'USE_COLORS': True,
    'COMPACT_MODE': False,
    'CLEAR_CONSOLE': False,
}

# Configuration des couleurs console
COLORS = {
    'GREEN': '\\033[92m',
    'RED': '\\033[91m',
    'YELLOW': '\\033[93m',
    'CYAN': '\\033[96m',
    'WHITE': '\\033[97m',
    'RESET': '\\033[0m',
    'BOLD': '\\033[1m'
}

# Symboles d'affichage
SYMBOLS = {
    'GREEN_CANDLE': '🟢',
    'RED_CANDLE': '🔴', 
    'DOJI_CANDLE': '🟡',
    'HA_INDICATOR': '📊',
    'RSI_INDICATOR': '📈',
    'SEPARATOR': '─' * 50
}

# Configuration logging
LOG_CONFIG = {
    'ENABLE_FILE_LOG': False,
    'LOG_FILENAME': 'monitor.log',
    'LOG_LEVEL': 'INFO'
}
'''
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(default_config)
    
    print(f"✅ Fichier config.py créé avec configuration par défaut")

def check_dependencies():
    """Vérifie les dépendances Python"""
    print(f"\n📦 Vérification des dépendances...")
    
    required_packages = [
        'pandas',
        'numpy', 
        'requests',
        'websocket-client'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}: installé")
        except ImportError:
            print(f"❌ {package}: MANQUANT")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Packages manquants: {', '.join(missing_packages)}")
        print(f"💡 Installez-les avec: pip install {' '.join(missing_packages)}")
        return False
    else:
        print(f"\n✅ Toutes les dépendances sont installées")
        return True

def verify_file_structure():
    """Vérifie que tous les fichiers nécessaires sont présents"""
    print(f"\n🔍 Vérification de la structure des fichiers...")
    
    required_files = [
        "main.py",
        "config.py",
        "core/binance_client.py",
        "core/websocket_handler.py", 
        "core/data_manager.py",
        "indicators/heikin_ashi.py",
        "indicators/rsi.py",
        "indicators/calculator.py",
        "display/formatter.py",
        "display/console.py"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}: MANQUANT")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ Fichiers manquants: {len(missing_files)}")
        return False
    else:
        print(f"\n✅ Tous les fichiers requis sont présents")
        return True

def run_test_import():
    """Test d'import de tous les modules"""
    print(f"\n🧪 Test d'import des modules...")
    
    try:
        # Test imports principaux
        import config
        print("✅ config: OK")
        
        from core.binance_client import BinanceClient
        print("✅ core.binance_client: OK")
        
        from core.websocket_handler import WebSocketHandler
        print("✅ core.websocket_handler: OK")
        
        from core.data_manager import DataManager
        print("✅ core.data_manager: OK")
        
        from indicators.heikin_ashi import HeikinAshi
        print("✅ indicators.heikin_ashi: OK")
        
        from indicators.rsi import RSI
        print("✅ indicators.rsi: OK")
        
        from indicators.calculator import IndicatorCalculator
        print("✅ indicators.calculator: OK")
        
        from display.formatter import DataFormatter
        print("✅ display.formatter: OK")
        
        from display.console import ConsoleDisplay
        print("✅ display.console: OK")
        
        print(f"\n✅ Tous les imports fonctionnent correctement")
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def main():
    """Fonction principale de configuration"""
    print("🔧 CONFIGURATION AUTOMATIQUE DU MONITORING")
    print("=" * 50)
    
    # 1. Créer structure de dossiers
    create_directory_structure()
    
    # 2. Créer fichiers __init__.py
    create_init_files()
    
    # 3. Créer config par défaut si nécessaire
    create_default_config()
    
    # 4. Vérifier dépendances
    deps_ok = check_dependencies()
    
    # 5. Vérifier structure fichiers
    files_ok = verify_file_structure()
    
    # 6. Test imports si tout est OK
    if deps_ok and files_ok:
        imports_ok = run_test_import()
    else:
        imports_ok = False
    
    # Résumé final
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ DE LA CONFIGURATION")
    print("=" * 50)
    
    if deps_ok and files_ok and imports_ok:
        print("🎉 CONFIGURATION RÉUSSIE!")
        print("✅ Le projet est prêt à être utilisé")
        print("\n🚀 Commandes disponibles:")
        print("   python test_monitor.py  # Tester tous les composants")
        print("   python main.py          # Lancer le monitoring")
    else:
        print("⚠️ CONFIGURATION INCOMPLÈTE")
        if not deps_ok:
            print("❌ Installez les dépendances manquantes")
        if not files_ok:
            print("❌ Créez les fichiers manquants")
        if not imports_ok:
            print("❌ Corrigez les erreurs d'import")

if __name__ == "__main__":
    main()