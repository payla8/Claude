"""
Risk Assessment Agent - Evaluates risk and manages position sizing
"""

from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from .base_agent import BaseAgent, AgentSignal, MarketAnalysis


class RiskAssessmentAgent(BaseAgent):
    """Agent specialized in risk management"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("RiskManager", config)
        self.expertise_areas = [
            'Portfolio Risk', 'Position Sizing', 'Volatility Analysis',
            'Drawdown Management', 'Risk/Reward Ratio'
        ]
        self.max_risk_per_trade = config.get('risk_management', {}).get('max_risk_per_trade', 0.02)
        self.max_portfolio_risk = config.get('risk_management', {}).get('max_drawdown', 0.15)

    async def analyze(self, market_data: Dict[str, Any]) -> MarketAnalysis:
        """Analyze market risk"""
        df = market_data['df']
        symbol = market_data['symbol']
        timeframe = market_data.get('timeframe', '1h')
        portfolio_value = market_data.get('portfolio_value', 10000)
        current_positions = market_data.get('current_positions', [])

        # Calculate various risk metrics
        volatility = self._calculate_volatility(df)
        var = self._calculate_var(df)
        sharpe_ratio = self._calculate_sharpe_ratio(df)
        max_drawdown = self._calculate_max_drawdown(df)
        portfolio_exposure = self._calculate_portfolio_exposure(current_positions, portfolio_value)

        # Determine overall risk level
        risk_factors = {
            'volatility': volatility,
            'var': var,
            'max_drawdown': max_drawdown,
            'portfolio_exposure': portfolio_exposure
        }

        risk_level = self._calculate_overall_risk(risk_factors)

        # Calculate opportunity score (inverse of risk in good conditions)
        opportunity_score = 1.0 - risk_level if sharpe_ratio > 0 else 0.3

        analysis = {
            'volatility': volatility,
            'value_at_risk': var,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'portfolio_exposure': portfolio_exposure,
            'risk_level': risk_level,
            'recommended_position_size': self._calculate_position_size(
                portfolio_value, volatility, risk_level
            ),
            'stop_loss_recommendation': self._calculate_stop_loss(df, volatility),
            'take_profit_recommendation': self._calculate_take_profit(df, volatility)
        }

        confidence_factors = {
            'data_quality': 1.0 if len(df) >= 100 else len(df) / 100,
            'signal_strength': 0.8,
            'market_conditions': 1.0 - risk_level,
            'historical_accuracy': self.performance_metrics['accuracy_rate']
        }

        confidence = self._calculate_confidence(confidence_factors)

        return MarketAnalysis(
            agent_name=self.name,
            timestamp=datetime.now(),
            symbol=symbol,
            analysis=analysis,
            risk_level=risk_level,
            opportunity_score=opportunity_score,
            timeframe=timeframe,
            confidence=confidence
        )

    async def generate_signal(self, market_data: Dict[str, Any]) -> Optional[AgentSignal]:
        """Generate risk-based signal (usually advisory)"""
        analysis = await self.analyze(market_data)

        symbol = market_data['symbol']
        timeframe = market_data.get('timeframe', '1h')

        risk_level = analysis.risk_level

        # Risk agent mainly provides advisory signals
        if risk_level > 0.7:
            signal_type = 'hold'  # High risk - recommend holding off
            reasoning = f"High risk environment (risk level: {risk_level:.2f}). Recommend caution."
        elif risk_level < 0.3:
            signal_type = 'hold'  # Low risk - can proceed
            reasoning = f"Low risk environment (risk level: {risk_level:.2f}). Favorable conditions."
        else:
            return None  # Moderate risk - no strong signal

        return AgentSignal(
            agent_name=self.name,
            timestamp=datetime.now(),
            symbol=symbol,
            signal_type=signal_type,
            confidence=analysis.confidence,
            reasoning=reasoning,
            data={
                'risk_analysis': analysis.analysis
            },
            timeframe=timeframe,
            priority=7  # Risk signals have high priority
        )

    def _calculate_volatility(self, df: pd.DataFrame, window: int = 20) -> float:
        """Calculate price volatility (annualized)"""
        returns = df['close'].pct_change()
        volatility = returns.rolling(window=window).std().iloc[-1]

        # Annualize (assuming 365 trading days for crypto)
        annualized_volatility = volatility * np.sqrt(365 * 24)  # hourly data

        # Normalize to 0-1 scale (assume 200% annual volatility is extreme)
        return min(annualized_volatility / 2.0, 1.0)

    def _calculate_var(self, df: pd.DataFrame, confidence: float = 0.95) -> float:
        """Calculate Value at Risk"""
        returns = df['close'].pct_change().dropna()

        if len(returns) < 10:
            return 0.05

        var = np.percentile(returns, (1 - confidence) * 100)
        return abs(float(var))

    def _calculate_sharpe_ratio(self, df: pd.DataFrame, window: int = 50) -> float:
        """Calculate Sharpe ratio"""
        returns = df['close'].pct_change()

        if len(returns) < window:
            return 0.0

        recent_returns = returns.tail(window)
        avg_return = recent_returns.mean()
        std_return = recent_returns.std()

        if std_return == 0:
            return 0.0

        # Annualize
        sharpe = (avg_return / std_return) * np.sqrt(365 * 24)
        return float(sharpe)

    def _calculate_max_drawdown(self, df: pd.DataFrame) -> float:
        """Calculate maximum drawdown"""
        prices = df['close']
        cummax = prices.cummax()
        drawdown = (prices - cummax) / cummax

        return abs(float(drawdown.min()))

    def _calculate_portfolio_exposure(self, positions: list, portfolio_value: float) -> float:
        """Calculate current portfolio exposure"""
        if not positions or portfolio_value == 0:
            return 0.0

        total_exposure = sum(pos.get('value', 0) for pos in positions)
        return total_exposure / portfolio_value

    def _calculate_overall_risk(self, risk_factors: Dict[str, float]) -> float:
        """Calculate overall risk score"""
        weights = {
            'volatility': 0.3,
            'var': 0.25,
            'max_drawdown': 0.25,
            'portfolio_exposure': 0.2
        }

        risk_score = 0.0
        for factor, value in risk_factors.items():
            weight = weights.get(factor, 0.1)
            risk_score += value * weight

        return min(risk_score, 1.0)

    def _calculate_position_size(self, portfolio_value: float,
                                 volatility: float, risk_level: float) -> float:
        """Calculate recommended position size"""
        # Base position size on risk level
        base_size = self.max_risk_per_trade * portfolio_value

        # Adjust for volatility
        volatility_adjustment = 1.0 - min(volatility, 0.5)

        # Adjust for overall risk
        risk_adjustment = 1.0 - risk_level

        recommended_size = base_size * volatility_adjustment * risk_adjustment

        return max(recommended_size, portfolio_value * 0.01)  # Minimum 1% position

    def _calculate_stop_loss(self, df: pd.DataFrame, volatility: float) -> float:
        """Calculate recommended stop loss percentage"""
        # Base stop loss on volatility
        base_stop = 0.02  # 2% base

        # Adjust for volatility
        adjusted_stop = base_stop + (volatility * 0.05)

        return min(adjusted_stop, 0.10)  # Maximum 10% stop loss

    def _calculate_take_profit(self, df: pd.DataFrame, volatility: float) -> float:
        """Calculate recommended take profit percentage"""
        # Aim for 2:1 reward/risk ratio
        stop_loss = self._calculate_stop_loss(df, volatility)
        return stop_loss * 2
