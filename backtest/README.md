# Système de Backtest des Signaux de Trading

Ce module permet de backtester les performances des signaux de trading sur des données historiques de Binance.

## Structure du Module

```
backtest/
├── __init__.py                 # Module init
├── data_downloader.py          # Téléchargement données Binance
├── signal_backtester.py        # Engine de backtest
├── results_display.py          # Affichage et export des résultats
├── data/                       # Données historiques CSV
└── results/                    # Résultats de backtest
```

## Fonctionnalités

### 🔄 Téléchargement de Données
- **Source**: API Binance officielle
- **Formats**: CSV standardisé
- **Périodes**: Personnalisables (jours ou dates spécifiques)
- **Timeframes**: Tous les timeframes Binance (1m, 5m, 1h, etc.)

### 📊 Engine de Backtest
- **Signaux**: Réutilise exactement la même logique que le monitoring temps réel
- **Risk Management**: Calcul de position basé sur le risque
- **Ordres**: Stop Loss et Take Profit automatiques
- **Métriques**: Statistiques complètes de performance

### 📈 Analyse des Résultats
- **Affichage console**: Résumé détaillé
- **Exports**: CSV, JSON, rapports texte
- **Métriques**: Win rate, Profit Factor, Drawdown, etc.
- **Analyses**: Par type de signal, score, raison de sortie

## Utilisation

### Installation des Dépendances
```bash
pip install pandas numpy requests
```

### Exemples d'Utilisation

#### 1. Télécharger des Données
```bash
# 30 derniers jours de BTCUSDC en 5m
python backtest_runner.py download --symbol BTCUSDC --interval 5m --days 30

# Période spécifique
python backtest_runner.py download --symbol ETHUSDT --interval 1h --start-date 2025-01-01 --end-date 2025-01-15
```

#### 2. Lancer un Backtest
```bash
# Backtest automatique (utilise les données les plus récentes)
python backtest_runner.py backtest --symbol BTCUSDC --interval 5m

# Backtest avec paramètres personnalisés
python backtest_runner.py backtest --symbol BTCUSDC --interval 5m \
  --balance 50000 --risk 0.01 --stop-loss 0.015 --take-profit 0.05

# Backtest avec export complet
python backtest_runner.py backtest --symbol BTCUSDC --interval 5m \
  --export-csv --export-json --detailed-report
```

#### 3. Gestion des Fichiers
```bash
# Lister les données disponibles
python backtest_runner.py list-data

# Lister les résultats de backtest
python backtest_runner.py list-results
```

### Paramètres Configurables

| Paramètre | Description | Défaut |
|-----------|-------------|---------|
| `--balance` | Capital initial (USDT) | 10000 |
| `--risk` | Risque par trade (%) | 0.02 (2%) |
| `--stop-loss` | Stop loss (%) | 0.02 (2%) |
| `--take-profit` | Take profit (%) | 0.04 (4%) |

## Métriques de Performance

### Statistiques Principales
- **Total Return**: Rendement total en %
- **Win Rate**: Pourcentage de trades gagnants
- **Profit Factor**: Ratio gains/pertes
- **Max Drawdown**: Perte maximale depuis un pic
- **Avg Trade Duration**: Durée moyenne des positions

### Analyses Détaillées
- **Par Type de Signal**: Performance LONG vs SHORT
- **Par Score**: Efficacité selon le score du signal (2/5 à 5/5)
- **Par Raison de Sortie**: Stop Loss, Take Profit, Fin de backtest

## Architecture Technique

### Réutilisation du Code Existant
Le backtest utilise **exactement les mêmes indicateurs** que le système temps réel :
- `IndicatorCalculator` pour tous les calculs
- `SignalDetector` pour la détection des signaux
- Configuration identique (`config.py`)

### Avantages
✅ **Cohérence parfaite** entre backtest et trading réel  
✅ **Aucune divergence** de logique  
✅ **Maintenance simplifiée** (une seule base de code)  
✅ **Fiabilité** des résultats  

### Limitations
⚠️ **Slippage non pris en compte** (exécution parfaite assumée)  
⚠️ **Frais de trading** non inclus dans ce MVP  
⚠️ **Impact de marché** non simulé (positions de petite taille assumées)  

## Formats de Sortie

### Console
Résumé avec métriques principales et conseils d'optimisation

### CSV
- `trades_*.csv`: Détail de chaque trade
- `equity_curve_*.csv`: Évolution du capital
- `signals_*.csv`: Tous les signaux détectés

### JSON
Résultats complets au format JSON pour intégrations

### Rapport Texte
Rapport détaillé avec analyse complète des performances

## Optimisation

### Conseils Automatiques
Le système fournit des recommandations basées sur les résultats :
- Ajustement des seuils RSI si win rate < 40%
- Réduction du risque si drawdown > 20%
- Validation des stratégies si Profit Factor > 2.0

### Paramètres à Tester
- **RSI_PERIOD**: 3, 5, 14 (dans `config.py`)
- **Seuils RSI**: RSI_OVERSOLD/OVERBOUGHT
- **Stop Loss/Take Profit**: Ratio 1:2, 1:3, etc.
- **Risk per Trade**: 0.5%, 1%, 2%

## Support

Pour toute question ou amélioration, vérifiez d'abord :
1. Les exemples dans ce README
2. L'aide intégrée : `python backtest_runner.py -h`
3. Les logs d'erreur détaillés