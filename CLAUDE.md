# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a real-time cryptocurrency monitoring system for Binance that tracks candlestick patterns, Heikin Ashi indicators, and RSI calculations across multiple timeframes. The system uses WebSocket connections for live data streaming and provides console-based visualization with color-coded indicators.

## Architecture

### Core Components

- **main.py**: Entry point that orchestrates the monitoring system through the `CandleMonitor` class
- **config.py**: Central configuration file containing all parameters for symbols, timeframes, display settings, and indicator configurations
- **core/**: Data management and connectivity layer
  - `binance_client.py`: Binance API client for historical data
  - `websocket_handler.py`: WebSocket streaming handler for real-time data
  - `data_manager.py`: OHLC data management and DataFrame operations
  - `timeframe_manager.py`: Multi-timeframe data handling and synchronization
- **indicators/**: Technical indicator calculations
  - `calculator.py`: Main orchestrator for all indicator calculations with multi-timeframe support
  - `heikin_ashi.py`: Heikin Ashi candlestick calculations
  - `rsi.py`: RSI (Relative Strength Index) calculations
  - `ema.py`: EMA (Exponential Moving Average) calculations
- **display/**: Output formatting and console display
  - `console.py`: Console display manager with color-coded output
  - `formatter.py`: Data formatting utilities

### Key Features

1. **Multi-timeframe Analysis**: Base timeframe monitoring with higher timeframe EMA calculations
2. **Real-time Processing**: WebSocket-based live data streaming from Binance
3. **Dual Indicator Sets**: Parallel RSI calculations on both normal and Heikin Ashi candles
4. **Configurable Display**: Color-coded console output with customizable formatting
5. **Robust Error Handling**: Signal handlers for graceful shutdown and comprehensive error management

## Development Commands

### Running the Application

```bash
# Main monitoring application
python main.py

# Project setup and dependency check (if needed)
python setup.py
```

### Configuration

All configuration is managed through `config.py`:

- **SYMBOL**: Trading pair to monitor (default: "BTCUSDT")
- **TIMEFRAME**: Base timeframe for monitoring (1m, 5m, 15m, etc.)
- **RSI_PERIODS**: List of RSI calculation periods
- **EMA_HIGHER_TIMEFRAME**: Multi-timeframe EMA configuration with auto-suggestions
- **DISPLAY_CONFIG**: Console output customization options

### Dependencies

The project requires these Python packages (install manually as no requirements.txt exists):

```bash
pip install pandas numpy requests websocket-client
```

## Data Flow

1. **Initialization**: Historical data loaded via Binance REST API
2. **Real-time Updates**: WebSocket streams provide live kline data
3. **Indicator Calculation**: Multi-indicator processing on each closed candle
4. **Display Update**: Console output with color-coded results
5. **Multi-timeframe Sync**: Higher timeframe data updated when needed for EMA calculations

## Key Implementation Notes

- **Thread Safety**: WebSocket handler runs in separate daemon thread
- **Data Management**: DataFrame operations with automatic size limiting to prevent memory issues
- **Signal Handling**: SIGINT/SIGTERM handlers for clean shutdown
- **Error Recovery**: Comprehensive exception handling throughout the pipeline
- **Duplicate Prevention**: Candle timestamp checking to avoid processing duplicates

## Configuration Guidelines

When modifying configuration:

1. **Symbol Format**: Use uppercase format (e.g., "BTCUSDT")
2. **Timeframe Compatibility**: Ensure timeframes are valid Binance formats
3. **EMA Higher Timeframe**: Auto-suggestions map base timeframes to logical higher timeframes
4. **Display Colors**: ANSI color codes used for cross-platform compatibility
5. **Initial Data Limit**: Balance between indicator accuracy and memory usage (default: 100 candles)

## Extension Points

- **New Indicators**: Add to `indicators/` module and integrate via `calculator.py`
- **Display Formats**: Extend `display/` for additional output formats
- **Data Sources**: Core architecture supports different exchange integrations
- **Timeframe Logic**: `TimeframeManager` handles complex multi-timeframe scenarios