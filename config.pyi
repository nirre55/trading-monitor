
# Type stubs for config.py
from typing import Dict, List, Any, Union

SYMBOL: str
TIMEFRAME: str
RSI_PERIODS: List[int]
WEBSOCKET_URL: str
INITIAL_KLINES_LIMIT: int

DISPLAY_CONFIG: Dict[str, Union[bool, str]]
COLORS: Dict[str, str]
SYMBOLS: Dict[str, str]
LOG_CONFIG: Dict[str, Union[bool, str]]

# EMA Configuration
EMA_HIGHER_TIMEFRAME: Dict[str, Any]

# RECONNECTION Configuration  
RECONNECTION_CONFIG: Dict[str, Union[bool, int]]

# ATR Configuration
ATR_CONFIG: Dict[str, Union[bool, List[int]]]

# Volume Configuration  
VOLUME_CONFIG: Dict[str, Union[bool, List[int], int]]

# Signal Detection Configuration
SIGNAL_CONFIG: Dict[str, Union[bool, int]]

# Backtest Configuration
BACKTEST_CONFIG: Dict[str, Union[bool, int, float]]
