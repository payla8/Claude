"""
Coordinator Agent - Master agent that coordinates all other agents
and makes final trading decisions
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np
from .base_agent import BaseAgent, AgentSignal, MarketAnalysis
from .technical_agent import TechnicalAnalysisAgent
from .sentiment_agent import SentimentAnalysisAgent
from .pattern_agent import PatternRecognitionAgent
from .risk_agent import RiskAssessmentAgent
from .ml_prediction_agent import MLPredictionAgent
from src.utils.logger import get_logger


class CoordinatorAgent:
    """
    Master coordinator that manages all specialized agents
    and makes final trading decisions through consensus
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger("CoordinatorAgent")

        # Initialize all specialized agents
        self.agents = {
            'technical': TechnicalAnalysisAgent(config),
            'sentiment': SentimentAnalysisAgent(config),
            'pattern': PatternRecognitionAgent(config),
            'risk': RiskAssessmentAgent(config),
            'ml_prediction': MLPredictionAgent(config)
        }

        # Agent weights for consensus (can be adjusted based on performance)
        self.agent_weights = {
            'technical': 0.25,
            'sentiment': 0.15,
            'pattern': 0.20,
            'risk': 0.20,
            'ml_prediction': 0.20
        }

        self.min_consensus_threshold = config.get('min_confidence_threshold', 0.7)
        self.performance_history = []

        self.logger.info("CoordinatorAgent initialized with 5 specialized agents")

    async def analyze_market(self, symbol: str, market_data_api) -> Dict[str, Any]:
        """
        Coordinate all agents to analyze the market
        """
        self.logger.info(f"Starting comprehensive market analysis for {symbol}")

        # Gather market data
        df = await market_data_api.get_ohlcv(symbol, timeframe='1h', limit=500)
        ticker = await market_data_api.get_ticker(symbol)

        market_data = {
            'df': df,
            'symbol': symbol,
            'timeframe': '1h',
            'ticker': ticker
        }

        # Get analyses from all agents
        analyses = {}
        for agent_name, agent in self.agents.items():
            try:
                analysis = await agent.analyze(market_data)
                analyses[agent_name] = analysis
                self.logger.info(
                    f"{agent_name} analysis complete - "
                    f"Risk: {analysis.risk_level:.2f}, "
                    f"Opportunity: {analysis.opportunity_score:.2f}, "
                    f"Confidence: {analysis.confidence:.2f}"
                )
            except Exception as e:
                self.logger.error(f"Error in {agent_name} analysis: {e}")
                analyses[agent_name] = None

        # Compile comprehensive analysis
        comprehensive_analysis = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'individual_analyses': analyses,
            'consensus': self._calculate_consensus(analyses),
            'overall_risk': self._calculate_overall_risk(analyses),
            'overall_opportunity': self._calculate_overall_opportunity(analyses)
        }

        return comprehensive_analysis

    async def generate_trading_decision(self, symbol: str, market_data_api,
                                       portfolio_data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Generate final trading decision based on all agents' input
        """
        self.logger.info(f"Generating trading decision for {symbol}")

        # Get market data
        df = await market_data_api.get_ohlcv(symbol, timeframe='1h', limit=500)
        ticker = await market_data_api.get_ticker(symbol)

        market_data = {
            'df': df,
            'symbol': symbol,
            'timeframe': '1h',
            'ticker': ticker,
            'portfolio_value': portfolio_data.get('value', 10000) if portfolio_data else 10000,
            'current_positions': portfolio_data.get('positions', []) if portfolio_data else []
        }

        # Get signals from all agents
        signals = {}
        for agent_name, agent in self.agents.items():
            try:
                signal = await agent.generate_signal(market_data)
                signals[agent_name] = signal
                if signal:
                    self.logger.info(
                        f"{agent_name} signal: {signal.signal_type} "
                        f"(confidence: {signal.confidence:.2f}, priority: {signal.priority})"
                    )
            except Exception as e:
                self.logger.error(f"Error getting signal from {agent_name}: {e}")
                signals[agent_name] = None

        # Make final decision based on consensus
        decision = self._make_consensus_decision(signals, market_data)

        if decision:
            self.logger.info(
                f"FINAL DECISION for {symbol}: {decision['action']} "
                f"(confidence: {decision['confidence']:.2%}, "
                f"consensus: {decision['consensus_score']:.2%})"
            )
        else:
            self.logger.info(f"No trading decision for {symbol} - insufficient consensus")

        return decision

    def _calculate_consensus(self, analyses: Dict[str, Optional[MarketAnalysis]]) -> Dict[str, Any]:
        """Calculate consensus from all agent analyses"""
        valid_analyses = {k: v for k, v in analyses.items() if v is not None}

        if not valid_analyses:
            return {'agreement': 0.0, 'direction': 'unknown'}

        # Calculate weighted opportunity scores
        bullish_score = 0.0
        bearish_score = 0.0
        total_weight = 0.0

        for agent_name, analysis in valid_analyses.items():
            weight = self.agent_weights.get(agent_name, 0.1)
            opportunity = analysis.opportunity_score
            risk = analysis.risk_level

            # High opportunity + low risk = bullish
            # High opportunity + high risk = uncertain
            if opportunity > 0.6 and risk < 0.5:
                bullish_score += weight * opportunity
            elif opportunity > 0.6 and risk > 0.5:
                bearish_score += weight * risk

            total_weight += weight

        if total_weight > 0:
            bullish_score /= total_weight
            bearish_score /= total_weight

        # Determine consensus direction
        if bullish_score > bearish_score * 1.5:
            direction = 'bullish'
            agreement = bullish_score
        elif bearish_score > bullish_score * 1.5:
            direction = 'bearish'
            agreement = bearish_score
        else:
            direction = 'neutral'
            agreement = 0.5

        return {
            'agreement': agreement,
            'direction': direction,
            'bullish_score': bullish_score,
            'bearish_score': bearish_score
        }

    def _calculate_overall_risk(self, analyses: Dict[str, Optional[MarketAnalysis]]) -> float:
        """Calculate overall risk level"""
        valid_analyses = {k: v for k, v in analyses.items() if v is not None}

        if not valid_analyses:
            return 0.5

        # Weight risk assessments
        total_risk = 0.0
        total_weight = 0.0

        for agent_name, analysis in valid_analyses.items():
            weight = self.agent_weights.get(agent_name, 0.1)

            # Give extra weight to risk agent
            if agent_name == 'risk':
                weight *= 1.5

            total_risk += analysis.risk_level * weight
            total_weight += weight

        return total_risk / total_weight if total_weight > 0 else 0.5

    def _calculate_overall_opportunity(self, analyses: Dict[str, Optional[MarketAnalysis]]) -> float:
        """Calculate overall opportunity score"""
        valid_analyses = {k: v for k, v in analyses.items() if v is not None}

        if not valid_analyses:
            return 0.0

        total_opportunity = 0.0
        total_weight = 0.0

        for agent_name, analysis in valid_analyses.items():
            weight = self.agent_weights.get(agent_name, 0.1)
            total_opportunity += analysis.opportunity_score * weight
            total_weight += weight

        return total_opportunity / total_weight if total_weight > 0 else 0.0

    def _make_consensus_decision(self, signals: Dict[str, Optional[AgentSignal]],
                                market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make final trading decision based on agent consensus"""
        valid_signals = {k: v for k, v in signals.items() if v is not None}

        if not valid_signals:
            return None

        # Count signal types with weights
        signal_scores = {'buy': 0.0, 'sell': 0.0, 'hold': 0.0}
        signal_weights = {
            'strong_buy': 2.0, 'buy': 1.0, 'hold': 0.0,
            'sell': -1.0, 'strong_sell': -2.0
        }

        total_confidence = 0.0
        total_weight = 0.0
        reasonings = []

        for agent_name, signal in valid_signals.items():
            weight = self.agent_weights.get(agent_name, 0.1)

            # Apply signal weight
            signal_value = signal_weights.get(signal.signal_type, 0)

            # Weight by confidence and priority
            weighted_signal = signal_value * signal.confidence * (signal.priority / 10)

            if signal_value > 0:
                signal_scores['buy'] += weighted_signal * weight
            elif signal_value < 0:
                signal_scores['sell'] += abs(weighted_signal) * weight
            else:
                signal_scores['hold'] += weight

            total_confidence += signal.confidence * weight
            total_weight += weight

            reasonings.append(f"{agent_name}: {signal.reasoning}")

        # Normalize scores
        if total_weight > 0:
            for key in signal_scores:
                signal_scores[key] /= total_weight
            avg_confidence = total_confidence / total_weight
        else:
            avg_confidence = 0.0

        # Determine final action
        buy_score = signal_scores['buy']
        sell_score = signal_scores['sell']
        hold_score = signal_scores['hold']

        # Calculate consensus score
        max_score = max(buy_score, sell_score, hold_score)
        consensus_score = max_score / (buy_score + sell_score + hold_score) if (buy_score + sell_score + hold_score) > 0 else 0

        # Check if consensus meets threshold
        if consensus_score < (self.min_consensus_threshold - 0.2):  # Lower threshold for initial consideration
            return None

        # Determine action
        if buy_score > sell_score and buy_score > hold_score * 1.5:
            action = 'BUY'
            strength = 'STRONG' if buy_score > 1.5 else 'MODERATE'
        elif sell_score > buy_score and sell_score > hold_score * 1.5:
            action = 'SELL'
            strength = 'STRONG' if sell_score > 1.5 else 'MODERATE'
        else:
            action = 'HOLD'
            strength = 'NEUTRAL'

        # Get risk assessment
        risk_signal = signals.get('risk')
        risk_assessment = risk_signal.data.get('risk_analysis', {}) if risk_signal else {}

        # Get current price
        current_price = market_data['df']['close'].iloc[-1]

        return {
            'action': action,
            'strength': strength,
            'symbol': market_data['symbol'],
            'timestamp': datetime.now(),
            'confidence': avg_confidence,
            'consensus_score': consensus_score,
            'signal_breakdown': signal_scores,
            'current_price': current_price,
            'reasoning': reasonings,
            'risk_assessment': risk_assessment,
            'recommended_position_size': risk_assessment.get('recommended_position_size'),
            'stop_loss': risk_assessment.get('stop_loss_recommendation'),
            'take_profit': risk_assessment.get('take_profit_recommendation')
        }

    def update_agent_weights(self, performance_data: Dict[str, float]):
        """Dynamically adjust agent weights based on performance"""
        for agent_name, accuracy in performance_data.items():
            if agent_name in self.agent_weights:
                # Increase weight for high-performing agents
                if accuracy > 0.7:
                    self.agent_weights[agent_name] *= 1.1
                # Decrease weight for low-performing agents
                elif accuracy < 0.5:
                    self.agent_weights[agent_name] *= 0.9

        # Normalize weights
        total_weight = sum(self.agent_weights.values())
        self.agent_weights = {k: v / total_weight for k, v in self.agent_weights.items()}

        self.logger.info(f"Agent weights updated: {self.agent_weights}")

    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        status = {}
        for agent_name, agent in self.agents.items():
            status[agent_name] = {
                'active': agent.is_active,
                'performance': agent.get_performance(),
                'weight': self.agent_weights.get(agent_name, 0.0),
                'expertise': agent.get_expertise_areas()
            }
        return status
