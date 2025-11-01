"""Multi-Agent AI System for Cryptocurrency Trading"""

from .base_agent import BaseAgent, AgentSignal, MarketAnalysis
from .technical_agent import TechnicalAnalysisAgent
from .sentiment_agent import SentimentAnalysisAgent
from .pattern_agent import PatternRecognitionAgent
from .risk_agent import RiskAssessmentAgent
from .ml_prediction_agent import MLPredictionAgent
from .coordinator_agent import CoordinatorAgent

__all__ = [
    'BaseAgent',
    'AgentSignal',
    'MarketAnalysis',
    'TechnicalAnalysisAgent',
    'SentimentAnalysisAgent',
    'PatternRecognitionAgent',
    'RiskAssessmentAgent',
    'MLPredictionAgent',
    'CoordinatorAgent'
]
