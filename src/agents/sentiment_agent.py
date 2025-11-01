"""
Sentiment Analysis Agent - Analyzes market sentiment from news and social media
"""

from typing import Dict, Any, Optional
from datetime import datetime
import random
from .base_agent import BaseAgent, AgentSignal, MarketAnalysis


class SentimentAnalysisAgent(BaseAgent):
    """Agent specialized in sentiment analysis"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("SentimentAnalyst", config)
        self.expertise_areas = [
            'News Sentiment', 'Social Media', 'Market Fear/Greed',
            'Whale Activity', 'Retail Sentiment'
        ]

    async def analyze(self, market_data: Dict[str, Any]) -> MarketAnalysis:
        """Analyze market sentiment"""
        symbol = market_data['symbol']
        timeframe = market_data.get('timeframe', '1h')

        # Simulate sentiment analysis (in production, would use real APIs)
        sentiment_score = self._analyze_sentiment(symbol)

        # Analyze fear and greed
        fear_greed = self._analyze_fear_greed()

        # Analyze social media trends
        social_sentiment = self._analyze_social_media(symbol)

        # Calculate overall sentiment
        overall_sentiment = (
            sentiment_score * 0.4 +
            fear_greed * 0.3 +
            social_sentiment * 0.3
        )

        # Determine risk level (extreme sentiment = higher risk)
        risk_level = abs(overall_sentiment - 0.5) * 2

        # Opportunity score (strong sentiment = opportunity)
        opportunity_score = abs(overall_sentiment - 0.5) * 2

        analysis = {
            'overall_sentiment': overall_sentiment,
            'sentiment_label': self._get_sentiment_label(overall_sentiment),
            'news_sentiment': sentiment_score,
            'fear_greed_index': fear_greed,
            'social_media_sentiment': social_sentiment,
            'sentiment_trend': self._get_sentiment_trend(),
            'key_topics': self._get_key_topics(symbol)
        }

        confidence_factors = {
            'data_quality': 0.8,  # Simulated data
            'signal_strength': abs(overall_sentiment - 0.5) * 2,
            'market_conditions': 0.7,
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
        """Generate signal based on sentiment analysis"""
        analysis = await self.analyze(market_data)

        symbol = market_data['symbol']
        timeframe = market_data.get('timeframe', '1h')

        sentiment = analysis.analysis['overall_sentiment']

        # Only generate signal if sentiment is strong enough
        if abs(sentiment - 0.5) < 0.15:
            return None

        signal_type = self._get_signal_type(sentiment)

        # Build reasoning
        reasoning_parts = []
        reasoning_parts.append(f"Overall sentiment: {analysis.analysis['sentiment_label']}")
        reasoning_parts.append(f"Fear/Greed: {self._get_fear_greed_label(analysis.analysis['fear_greed_index'])}")

        key_topics = analysis.analysis['key_topics']
        if key_topics:
            reasoning_parts.append(f"Key topics: {', '.join(key_topics[:2])}")

        reasoning = "; ".join(reasoning_parts)

        # Calculate priority based on sentiment strength
        sentiment_strength = abs(sentiment - 0.5) * 2
        priority = int(5 + (sentiment_strength * 5))

        return AgentSignal(
            agent_name=self.name,
            timestamp=datetime.now(),
            symbol=symbol,
            signal_type=signal_type,
            confidence=analysis.confidence,
            reasoning=reasoning,
            data={
                'sentiment_analysis': analysis.analysis
            },
            timeframe=timeframe,
            priority=priority
        )

    def _analyze_sentiment(self, symbol: str) -> float:
        """Simulate news sentiment analysis (0 = very bearish, 1 = very bullish)"""
        # In production, would use real news APIs and NLP
        base_sentiment = random.uniform(0.35, 0.65)

        # Add some symbol-specific bias
        if 'BTC' in symbol:
            base_sentiment += random.uniform(-0.05, 0.15)  # BTC usually positive
        elif 'ETH' in symbol:
            base_sentiment += random.uniform(-0.05, 0.10)

        return max(0, min(1, base_sentiment))

    def _analyze_fear_greed(self) -> float:
        """Simulate Fear & Greed Index (0 = extreme fear, 1 = extreme greed)"""
        # In production, would use real Fear & Greed Index API
        return random.uniform(0.3, 0.7)

    def _analyze_social_media(self, symbol: str) -> float:
        """Simulate social media sentiment analysis"""
        # In production, would use Twitter/Reddit APIs
        return random.uniform(0.35, 0.65)

    def _get_sentiment_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score >= 0.75:
            return "Extremely Bullish"
        elif score >= 0.60:
            return "Bullish"
        elif score >= 0.40:
            return "Neutral"
        elif score >= 0.25:
            return "Bearish"
        else:
            return "Extremely Bearish"

    def _get_fear_greed_label(self, score: float) -> str:
        """Convert fear/greed score to label"""
        if score >= 0.75:
            return "Extreme Greed"
        elif score >= 0.60:
            return "Greed"
        elif score >= 0.40:
            return "Neutral"
        elif score >= 0.25:
            return "Fear"
        else:
            return "Extreme Fear"

    def _get_sentiment_trend(self) -> str:
        """Get sentiment trend direction"""
        return random.choice(['improving', 'stable', 'deteriorating'])

    def _get_key_topics(self, symbol: str) -> list:
        """Get key topics being discussed"""
        topics = [
            'Institutional Adoption',
            'Regulatory News',
            'Technical Breakout',
            'Major Partnership',
            'DeFi Growth',
            'ETF Approval',
            'Network Upgrade',
            'Market Volatility'
        ]
        return random.sample(topics, k=random.randint(2, 4))
