# 🤖 Crypto Investment AI Bot

**Advanced Multi-Agent AI System for Cryptocurrency Trading**

An autonomous cryptocurrency trading bot powered by a sophisticated multi-agent AI system. Each specialized AI agent analyzes different aspects of the market, and a master coordinator makes final trading decisions through consensus.

## 🌟 Features

### Multi-Agent AI System
- **Technical Analysis Agent** - Expert in RSI, MACD, Bollinger Bands, Stochastic, ADX, and more
- **Sentiment Analysis Agent** - Analyzes market sentiment, fear/greed index, and social media
- **Pattern Recognition Agent** - Detects chart patterns, candlestick patterns, support/resistance
- **Risk Management Agent** - Evaluates portfolio risk, position sizing, and drawdown management
- **ML Prediction Agent** - Uses LSTM and Transformer models for price prediction
- **Coordinator Agent** - Master agent that coordinates all others and makes final decisions

### Advanced Capabilities
- Real-time market data analysis
- Technical indicator calculation (20+ indicators)
- Pattern detection (chart and candlestick patterns)
- Sentiment analysis from multiple sources
- Machine learning price predictions
- Risk-adjusted position sizing
- Automated stop-loss and take-profit orders
- Portfolio tracking and performance metrics
- Backtesting system
- Paper trading mode (safe testing without real money)

## 📋 Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd /path/to/crypto-bot

# Make the startup script executable
chmod +x run_bot.sh

# Run the bot (it will create venv and install dependencies automatically)
./run_bot.sh
```

### 2. Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Edit .env file with your settings (optional for paper trading)
nano .env

# Run the bot
python3 crypto_bot.py
```

## ⚙️ Configuration

### config.yaml

Main configuration file for the bot:

```yaml
trading:
  mode: paper  # paper or live
  symbols:
    - BTC/USDT
    - ETH/USDT
  timeframes:
    - 1h

capital:
  initial: 10000
  max_position_size: 0.2  # 20% of portfolio per trade

risk_management:
  max_risk_per_trade: 0.02  # 2% max loss per trade
  max_daily_loss: 0.05  # 5% max daily loss
  stop_loss_percentage: 0.03
  take_profit_percentage: 0.06

min_confidence_threshold: 0.7  # Minimum confidence to execute trade
```

### .env (Optional - for live trading)

```bash
# Exchange API Keys (only needed for live trading)
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key

# Trading Mode
TRADING_MODE=paper  # paper or live
INITIAL_CAPITAL=10000
```

## 🎯 How It Works

### 1. Multi-Agent Analysis

Each specialized agent analyzes the market:

```
Technical Agent  →  Calculates 20+ indicators
Sentiment Agent  →  Analyzes market sentiment
Pattern Agent    →  Detects chart patterns
Risk Agent       →  Evaluates risk levels
ML Agent         →  Predicts price movements
```

### 2. Coordinator Decision

The Coordinator Agent:
- Collects signals from all agents
- Weights each agent's input based on performance
- Calculates consensus score
- Makes final BUY/SELL/HOLD decision

### 3. Trade Execution

If consensus meets threshold:
- Calculates position size based on risk
- Executes trade
- Sets stop-loss and take-profit orders
- Tracks position in portfolio

### 4. Continuous Learning

- Tracks each agent's performance
- Adjusts agent weights dynamically
- Learns from successful and failed trades

## 📊 Output Example

```
================================================================================
🤖 CRYPTO AI BOT STARTED
================================================================================
Trading Mode: PAPER
Monitoring Symbols: BTC/USDT, ETH/USDT
Initial Capital: $10,000.00
Analysis Interval: 300s
================================================================================

🧠 AI AGENTS STATUS
--------------------------------------------------------------------
TECHNICAL: Active=True, Weight=25.00%, Accuracy=0.00%
SENTIMENT: Active=True, Weight=15.00%, Accuracy=0.00%
PATTERN: Active=True, Weight=20.00%, Accuracy=0.00%
RISK: Active=True, Weight=20.00%, Accuracy=0.00%
ML_PREDICTION: Active=True, Weight=20.00%, Accuracy=0.00%

================================================================================
ANALYSIS CYCLE #1
Time: 2024-11-01 12:00:00
================================================================================

📊 PORTFOLIO STATUS
--------------------------------------------------------------------
Total Value:      $10,000.00
Cash:             $10,000.00
Positions Value:  $0.00
Total P&L:        $0.00 (+0.00%)
Open Positions:   0
Total Trades:     0

--- Analyzing BTC/USDT ---

🤖 AI DECISION
--------------------------------------------------------------------
Action:       BUY (STRONG)
Confidence:   78.50%
Consensus:    82.30%
Price:        $45,234.56
Stop Loss:    3.50%
Take Profit:  7.00%

Agent Reasoning:
  1. TechnicalAnalyst: RSI oversold at 28.5; MACD bullish crossover; strong_uptrend trend detected
  2. SentimentAnalyst: Overall sentiment: Bullish; Fear/Greed: Greed
  3. PatternRecognition: Chart patterns: double_bottom; Price near support level
```

## 📈 Performance Tracking

The bot tracks:
- Total return percentage
- Win rate
- Profit factor
- Sharpe ratio
- Maximum drawdown
- Individual agent performance
- Trade history

## ⚠️ Risk Management

Built-in risk controls:
- Maximum risk per trade (default 2%)
- Maximum daily loss limit (default 5%)
- Maximum portfolio drawdown (default 15%)
- Automatic stop-loss orders
- Position size limits
- Portfolio exposure limits

## 🔒 Safety Features

- **Paper Trading Mode**: Test strategies without risking real money
- **Consensus-Based Decisions**: Multiple agents must agree before trading
- **Confidence Thresholds**: Minimum confidence required to execute trades
- **Risk Assessment**: Every trade is evaluated for risk
- **Stop-Loss Protection**: Automatic stop-loss on every trade

## 📝 Project Structure

```
crypto-bot/
├── crypto_bot.py              # Main bot orchestrator
├── config.yaml                # Configuration file
├── requirements.txt           # Python dependencies
├── run_bot.sh                # Startup script
├── src/
│   ├── agents/               # AI Agents
│   │   ├── base_agent.py
│   │   ├── coordinator_agent.py
│   │   ├── technical_agent.py
│   │   ├── sentiment_agent.py
│   │   ├── pattern_agent.py
│   │   ├── risk_agent.py
│   │   └── ml_prediction_agent.py
│   ├── data/                 # Market data
│   │   └── market_data_api.py
│   ├── strategies/           # Trading strategies
│   │   └── technical_analysis.py
│   ├── exchange/             # Trading execution
│   │   └── trading_engine.py
│   ├── portfolio/            # Portfolio management
│   │   └── portfolio_manager.py
│   ├── backtesting/          # Backtesting system
│   │   └── backtest_engine.py
│   └── utils/                # Utilities
│       ├── logger.py
│       └── config_loader.py
```

## ⚠️ Disclaimer

**IMPORTANT**: This bot is provided for educational and research purposes only. Cryptocurrency trading carries significant risks. Always test with paper trading first. Never invest more than you can afford to lose. This is not financial advice.

---

**Built with ❤️ using advanced AI and machine learning techniques**

*May your trades be profitable and your risk well-managed!* 🚀
