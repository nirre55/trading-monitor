# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a real-time cryptocurrency monitoring system for Binance that tracks candlestick patterns, Heikin Ashi indicators, RSI calculations, EMA analysis, ATR (volatility), and volume analysis across multiple timeframes. The system uses WebSocket connections for live data streaming and provides console-based visualization with color-coded indicators.

## Development Commands

### Running the Application

```bash
# Main monitoring application
python main.py

# Project setup and dependency verification  
python setup.py

# Backtest system
python backtest_runner.py download --symbol BTCUSDC --interval 5m --days 30
python backtest_runner.py backtest --symbol BTCUSDC --interval 5m --export-csv
python backtest_runner.py list-data
python backtest_runner.py list-results
```

### Dependencies

The project requires these Python packages (install manually as no requirements.txt exists):

```bash
pip install pandas numpy requests websocket-client
```

### Testing and Development

No formal test suite exists. The `setup.py` script provides comprehensive verification:
- Creates directory structure if missing
- Verifies all dependencies are installed  
- Checks file structure integrity
- Tests module imports

## Architecture

### Core Data Flow

The application follows a clear pipeline: Historical data initialization → WebSocket streaming → Indicator calculation → Console display. Each component is designed for modularity and error resilience.

### Key Architectural Patterns

1. **Multi-timeframe Analysis**: The `TimeframeManager` enables base timeframe monitoring with higher timeframe EMA calculations using dynamic timeframe suggestions
2. **Thread-based Streaming**: WebSocket handler runs in daemon thread with health monitoring and auto-reconnection
3. **Centralized Configuration**: All parameters managed through `config.py` with nested dictionaries for complex features
4. **Modular Indicators**: Each indicator is self-contained with standardized interfaces via `IndicatorCalculator`

### Core Components

- **CandleMonitor** (`main.py:27`): Main orchestrator class managing the entire monitoring lifecycle
- **DataManager** (`core/data_manager.py:9`): OHLC data management with DataFrame operations and duplicate prevention
- **TimeframeManager** (`core/timeframe_manager.py:11`): Multi-timeframe data synchronization with safety margins and intelligent caching
- **IndicatorCalculator** (`indicators/calculator.py:16`): Orchestrates all indicator calculations with multi-timeframe support
- **WebSocketHandler** (`core/websocket_handler.py:11`): Real-time data streaming with health monitoring and auto-reconnection

### Backtest System Architecture

The backtest system provides complete reuse of the main system components for perfect consistency between live and historical analysis:

- **BacktestRunner** (`backtest_runner.py`): CLI interface with data download, backtest execution, and export capabilities
- **SignalBacktester** (`backtest/signal_backtester.py:20`): Core backtest engine with risk management and position sizing
- **DataDownloader** (`backtest/data_downloader.py`): Historical data retrieval with automatic file management
- **ResultsDisplay** (`backtest/results_display.py`): Performance analysis and reporting with consecutive streak calculations

### Configuration System

The `config.py` uses nested dictionaries for complex features:

- **EMA_HIGHER_TIMEFRAME**: Multi-timeframe EMA with auto-suggestions, safety margins, and custom timeframe override
- **ATR_CONFIG**: ATR calculation settings with configurable periods for volatility analysis
- **VOLUME_CONFIG**: Volume analysis with lookback periods and comparison settings
- **RECONNECTION_CONFIG**: WebSocket reconnection with configurable attempts, delays, and timeouts
- **DISPLAY_CONFIG**: Console output customization with color control and formatting options
- **BACKTEST_CONFIG**: Risk management with stop loss methods (ATR/SWING_LEVELS), take profit strategies, and position sizing parameters

## Key Implementation Details

### Multi-timeframe Logic

The system maps base timeframes to higher timeframes automatically (1m→5m, 5m→15m, etc.) but allows manual override via `config.py`. The `TimeframeManager.calculate_required_candles()` method dynamically calculates data requirements based on configured EMA periods plus safety margins.

### Safety Margin System

The safety margin in `TimeframeManager` prevents data gaps during higher timeframe updates. It's calculated dynamically from the maximum EMA period plus a configurable buffer (default 50 candles).

### Error Handling Strategy

- **Signal Handlers**: SIGINT/SIGTERM for graceful shutdown via `signal_handler()`
- **WebSocket Resilience**: Auto-reconnection with exponential backoff in `WebSocketHandler`
- **Data Validation**: Timestamp checking prevents duplicate candle processing in `DataManager.update_with_kline()`
- **Import Protection**: Comprehensive error handling for missing dependencies throughout

### Display System

Console output uses ANSI color codes for cross-platform compatibility. The `ConsoleDisplay` class handles formatting with support for compact mode and real-time connection status indicators.

### EMA Higher Timeframe Integration

The system can calculate EMAs on higher timeframes while monitoring lower timeframes. This is controlled by the `EMA_HIGHER_TIMEFRAME` configuration and managed by the `TimeframeManager` with automatic timeframe mapping and data synchronization.

### ATR (Average True Range) Analysis

The `ATR` class (`indicators/atr.py`) calculates volatility measures with automatic classification (low/normal/high/extreme) based on historical percentiles. Trend analysis determines if volatility is increasing, decreasing, or stable.

### Volume Analysis

The `Volume` class (`indicators/volume.py`) provides comprehensive volume analysis including:
- Volume analysis over X recent candles with bullish/bearish breakdown
- Comparison with historical averages and volume level classification
- Detection of exceptional volume candles and trend analysis
- Support for multiple lookback periods (configurable via `VOLUME_CONFIG`)

### Backtest Risk Management

The backtest system implements sophisticated risk management with two stop-loss calculation methods:

- **ATR Method**: Stop loss calculated as current_price ± (ATR_period × multiplier), with configurable periods and multipliers
- **Swing Levels Method**: Stop loss based on recent high/low levels with configurable lookback periods and offset percentages
- **Take Profit Strategies**: Either fixed percentage or ratio-based relative to stop loss distance
- **Position Sizing**: Risk-based position sizing with maximum position limits and effective risk calculation

### Signal Detection and Validation

The `SignalDetector` (`indicators/signal_detector.py`) implements a state machine pattern with two-step validation:
1. **RSI Condition**: Multi-period RSI analysis with "ANY" or "ALL" threshold modes
2. **Heikin Ashi Confirmation**: Candlestick pattern validation for signal confirmation
3. **Scoring System**: 5-point scale with EMA trend, volume, and ATR validations

## Extension Points

- **New Indicators**: Add to `indicators/` module and integrate via `IndicatorCalculator.calculate_all_indicators()`
- **Data Sources**: Core architecture supports different exchange integrations through client abstraction
- **Display Formats**: Extend `display/` for additional output formats beyond console
- **Timeframe Logic**: `TimeframeManager` handles complex multi-timeframe scenarios with configurable hierarchies