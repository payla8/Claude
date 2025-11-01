"""
ML Prediction Agent - Uses machine learning models for price prediction
"""

from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from .base_agent import BaseAgent, AgentSignal, MarketAnalysis


class MLPredictionAgent(BaseAgent):
    """Agent using ML models for predictions"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("MLPredictor", config)
        self.expertise_areas = [
            'LSTM Prediction', 'Transformer Models', 'Ensemble Methods',
            'Feature Engineering', 'Time Series Forecasting'
        ]
        self.model_loaded = False
        self.prediction_horizon = config.get('ml_models', {}).get('prediction_horizon', 24)

    async def analyze(self, market_data: Dict[str, Any]) -> MarketAnalysis:
        """Analyze using ML predictions"""
        df = market_data['df']
        symbol = market_data['symbol']
        timeframe = market_data.get('timeframe', '1h')

        # Prepare features
        features = self._engineer_features(df)

        # Generate predictions (simulated - in production would use real models)
        predictions = self._generate_predictions(features)

        # Calculate prediction confidence
        prediction_confidence = self._calculate_prediction_confidence(predictions)

        # Determine trend direction
        trend_direction = self._determine_trend(predictions)

        # Calculate risk and opportunity
        risk_level = 1.0 - prediction_confidence
        opportunity_score = prediction_confidence if trend_direction != 'neutral' else 0.3

        analysis = {
            'predictions': predictions,
            'trend_direction': trend_direction,
            'prediction_confidence': prediction_confidence,
            'feature_importance': self._get_feature_importance(),
            'model_performance': self._get_model_performance(),
            'forecast_horizon': f"{self.prediction_horizon} hours"
        }

        confidence_factors = {
            'data_quality': 1.0 if len(df) >= 200 else len(df) / 200,
            'signal_strength': prediction_confidence,
            'market_conditions': 0.8,
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
        """Generate signal based on ML predictions"""
        analysis = await self.analyze(market_data)

        symbol = market_data['symbol']
        timeframe = market_data.get('timeframe', '1h')

        predictions = analysis.analysis['predictions']
        trend_direction = analysis.analysis['trend_direction']
        prediction_confidence = analysis.analysis['prediction_confidence']

        # Only generate signal if confidence is sufficient
        if prediction_confidence < 0.6:
            return None

        # Determine signal type based on predictions
        if trend_direction == 'bullish':
            signal_type = 'strong_buy' if prediction_confidence > 0.8 else 'buy'
        elif trend_direction == 'bearish':
            signal_type = 'strong_sell' if prediction_confidence > 0.8 else 'sell'
        else:
            return None

        # Build reasoning
        price_change = predictions['price_change_prediction']
        reasoning = (
            f"ML models predict {trend_direction} movement "
            f"({price_change:+.2f}% over {self.prediction_horizon}h) "
            f"with {prediction_confidence:.1%} confidence"
        )

        # Add model ensemble info
        ensemble = predictions.get('ensemble_agreement', 0)
        if ensemble > 0.8:
            reasoning += f"; Strong model consensus ({ensemble:.1%})"

        priority = int(5 + (prediction_confidence * 5))

        return AgentSignal(
            agent_name=self.name,
            timestamp=datetime.now(),
            symbol=symbol,
            signal_type=signal_type,
            confidence=analysis.confidence,
            reasoning=reasoning,
            data={
                'predictions': predictions,
                'model_performance': analysis.analysis['model_performance']
            },
            timeframe=timeframe,
            priority=priority,
            expected_profit=abs(price_change) if price_change > 0 else None,
            expected_loss=abs(price_change) * 0.5  # Assume 50% of predicted move as risk
        )

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for ML models"""
        features = df.copy()

        # Price-based features
        features['returns'] = features['close'].pct_change()
        features['log_returns'] = np.log(features['close'] / features['close'].shift(1))

        # Moving averages
        for window in [7, 14, 30]:
            features[f'sma_{window}'] = features['close'].rolling(window=window).mean()
            features[f'ema_{window}'] = features['close'].ewm(span=window).mean()

        # Volatility
        features['volatility'] = features['returns'].rolling(window=20).std()

        # Volume features
        features['volume_sma'] = features['volume'].rolling(window=20).mean()
        features['volume_ratio'] = features['volume'] / features['volume_sma']

        # Price momentum
        features['momentum_5'] = features['close'] / features['close'].shift(5) - 1
        features['momentum_10'] = features['close'] / features['close'].shift(10) - 1

        # High/Low ratios
        features['hl_ratio'] = features['high'] / features['low']
        features['close_to_high'] = features['close'] / features['high']

        return features.fillna(0)

    def _generate_predictions(self, features: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate predictions using ML models
        In production, would use trained LSTM, Transformer, etc.
        """
        # Simulate predictions from multiple models
        current_price = features['close'].iloc[-1]

        # Simulate LSTM prediction
        lstm_prediction = self._simulate_model_prediction(features, model_type='lstm')

        # Simulate Transformer prediction
        transformer_prediction = self._simulate_model_prediction(features, model_type='transformer')

        # Simulate ensemble prediction
        ensemble_prediction = (lstm_prediction + transformer_prediction) / 2

        # Calculate ensemble agreement
        predictions_list = [lstm_prediction, transformer_prediction]
        std_dev = np.std(predictions_list)
        ensemble_agreement = 1.0 / (1.0 + std_dev)  # Higher agreement = lower std dev

        price_change_prediction = ((ensemble_prediction - current_price) / current_price) * 100

        return {
            'current_price': current_price,
            'lstm_prediction': lstm_prediction,
            'transformer_prediction': transformer_prediction,
            'ensemble_prediction': ensemble_prediction,
            'price_change_prediction': price_change_prediction,
            'ensemble_agreement': ensemble_agreement,
            'prediction_range': {
                'low': min(predictions_list),
                'high': max(predictions_list)
            }
        }

    def _simulate_model_prediction(self, features: pd.DataFrame, model_type: str) -> float:
        """Simulate ML model prediction"""
        current_price = features['close'].iloc[-1]
        recent_trend = features['close'].pct_change().tail(20).mean()
        volatility = features['close'].pct_change().tail(20).std()

        # Simulate prediction with some randomness
        trend_component = recent_trend * np.random.uniform(0.5, 1.5)
        random_component = np.random.normal(0, volatility)

        # Different models have different biases
        if model_type == 'lstm':
            model_bias = np.random.uniform(-0.005, 0.005)
        elif model_type == 'transformer':
            model_bias = np.random.uniform(-0.003, 0.003)
        else:
            model_bias = 0

        predicted_return = trend_component + random_component + model_bias
        predicted_price = current_price * (1 + predicted_return)

        return predicted_price

    def _calculate_prediction_confidence(self, predictions: Dict[str, Any]) -> float:
        """Calculate confidence in predictions"""
        # Base confidence on ensemble agreement
        ensemble_agreement = predictions['ensemble_agreement']

        # Adjust for prediction magnitude (extreme predictions less confident)
        price_change = abs(predictions['price_change_prediction'])
        magnitude_factor = 1.0 / (1.0 + price_change / 10)  # Reduce confidence for large changes

        confidence = ensemble_agreement * magnitude_factor

        return min(max(confidence, 0.0), 1.0)

    def _determine_trend(self, predictions: Dict[str, Any]) -> str:
        """Determine predicted trend direction"""
        price_change = predictions['price_change_prediction']

        if price_change > 2.0:
            return 'bullish'
        elif price_change < -2.0:
            return 'bearish'
        else:
            return 'neutral'

    def _get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance (simulated)"""
        features = [
            'price_momentum', 'volume_trend', 'volatility',
            'moving_averages', 'market_sentiment'
        ]

        # Simulate feature importance
        importance = np.random.dirichlet(np.ones(len(features)))

        return dict(zip(features, importance))

    def _get_model_performance(self) -> Dict[str, float]:
        """Get model performance metrics (simulated)"""
        return {
            'lstm_accuracy': 0.65 + np.random.uniform(-0.05, 0.05),
            'transformer_accuracy': 0.68 + np.random.uniform(-0.05, 0.05),
            'ensemble_accuracy': 0.72 + np.random.uniform(-0.05, 0.05),
            'mae': 0.02 + np.random.uniform(-0.005, 0.005),  # Mean Absolute Error
            'rmse': 0.03 + np.random.uniform(-0.005, 0.005)  # Root Mean Squared Error
        }
