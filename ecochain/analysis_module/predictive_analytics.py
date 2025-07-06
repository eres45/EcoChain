"""
Predictive Analytics Module

This module provides forecasting capabilities for sustainability metrics
and analyzes correlations between sustainability scores and market values.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
import os
import math
from scipy import stats

logger = logging.getLogger(__name__)

class PredictiveAnalytics:
    """
    Class for forecasting sustainability metrics and analyzing market correlations.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the predictive analytics module.
        
        Args:
            model_path: Optional path to a pre-trained model.
        """
        self.model_path = model_path
        
        # Default parameters for time series forecasting
        self.forecast_params = {
            "horizon_days": 90,  # Forecast 90 days ahead by default
            "confidence_interval": 0.95,  # 95% confidence interval
            "seasonality_period": 7,  # Weekly seasonality
            "trend_damping": 0.9,  # Damping factor for trend
            "min_data_points": 10  # Minimum data points needed for forecasting
        }
        
        # Market correlation parameters
        self.market_params = {
            "lookback_days": 180,  # Analyze last 180 days by default
            "smoothing_window": 7,  # 7-day moving average
            "lag_days": [0, 1, 3, 7, 14, 30],  # Lag days to analyze
            "significance_threshold": 0.05  # p-value threshold for significance
        }
        
        # Load any additional parameters from model if provided
        if self.model_path and os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'r') as f:
                    model_data = json.load(f)
                    if 'forecast_params' in model_data:
                        self.forecast_params.update(model_data['forecast_params'])
                    if 'market_params' in model_data:
                        self.market_params.update(model_data['market_params'])
            except Exception as e:
                logger.error(f"Error loading model data: {str(e)}")
    
    def forecast_sustainability(
        self, 
        historical_scores: List[Dict], 
        horizon_days: Optional[int] = None
    ) -> Dict:
        """
        Forecast future sustainability scores based on historical data.
        
        Args:
            historical_scores: List of dictionaries with historical score data.
                Each dictionary should have at least 'date' and 'score' keys.
            horizon_days: Number of days to forecast ahead (optional).
            
        Returns:
            Dictionary with forecast results.
        """
        # Use default horizon if not specified
        if horizon_days is None:
            horizon_days = self.forecast_params["horizon_days"]
            
        try:
            # Convert to DataFrame for easier manipulation
            if not historical_scores:
                return {
                    "error": "No historical data provided",
                    "forecast": [],
                    "confidence_intervals": []
                }
                
            # Extract dates and scores
            dates = []
            scores = []
            
            for entry in historical_scores:
                # Handle different date formats
                if isinstance(entry.get('date'), str):
                    try:
                        date = datetime.fromisoformat(entry['date'].replace('Z', '+00:00'))
                    except ValueError:
                        try:
                            date = datetime.strptime(entry['date'], '%Y-%m-%d')
                        except ValueError:
                            logger.warning(f"Could not parse date: {entry['date']}")
                            continue
                elif isinstance(entry.get('date'), datetime):
                    date = entry['date']
                else:
                    logger.warning(f"Invalid date format: {entry.get('date')}")
                    continue
                
                score = entry.get('score') or entry.get('sustainability_score')
                if score is not None:
                    dates.append(date)
                    scores.append(float(score))
            
            if len(dates) < self.forecast_params["min_data_points"]:
                return {
                    "error": f"Insufficient data points. Need at least {self.forecast_params['min_data_points']}",
                    "forecast": [],
                    "confidence_intervals": []
                }
                
            # Create DataFrame
            df = pd.DataFrame({
                'date': dates,
                'score': scores
            })
            
            # Sort by date
            df = df.sort_values('date')
            
            # Simple exponential smoothing with trend and seasonality (Holt-Winters)
            # In a real implementation, this would use more sophisticated models
            # like ARIMA, Prophet, or deep learning models
            
            # Calculate trend
            df['trend'] = df['score'].diff().fillna(0)
            
            # Apply exponential smoothing
            alpha = 0.3  # Smoothing factor
            df['smooth_score'] = df['score'].ewm(alpha=alpha).mean()
            
            # Calculate average trend
            avg_trend = df['trend'].mean() * self.forecast_params["trend_damping"]
            
            # Get the last observed score
            last_score = df['smooth_score'].iloc[-1]
            last_date = df['date'].iloc[-1]
            
            # Generate forecast dates
            forecast_dates = [last_date + timedelta(days=i+1) for i in range(horizon_days)]
            
            # Generate forecast values
            forecast_values = []
            for i in range(horizon_days):
                # Apply trend and add some randomness
                next_score = last_score + avg_trend
                
                # Apply seasonality if we have enough data
                if len(df) >= self.forecast_params["seasonality_period"]:
                    # Get the same day of week from previous weeks
                    day_of_week = (last_date + timedelta(days=i+1)).weekday()
                    seasonal_scores = df[df['date'].dt.weekday == day_of_week]['score']
                    if len(seasonal_scores) > 0:
                        seasonal_factor = seasonal_scores.mean() / df['score'].mean()
                        next_score *= seasonal_factor
                
                # Ensure score is within valid range (0-100)
                next_score = max(0, min(100, next_score))
                
                forecast_values.append(next_score)
                last_score = next_score
            
            # Calculate confidence intervals
            # In a real implementation, this would be based on prediction intervals
            # from the forecasting model
            std_dev = df['score'].std() or 1.0  # Default to 1 if std dev is 0
            z_value = stats.norm.ppf((1 + self.forecast_params["confidence_interval"]) / 2)
            margin = z_value * std_dev
            
            lower_bounds = [max(0, val - margin) for val in forecast_values]
            upper_bounds = [min(100, val + margin) for val in forecast_values]
            
            # Prepare result
            forecast_data = []
            for i in range(horizon_days):
                forecast_data.append({
                    'date': forecast_dates[i].strftime('%Y-%m-%d'),
                    'forecasted_score': round(forecast_values[i], 2),
                    'lower_bound': round(lower_bounds[i], 2),
                    'upper_bound': round(upper_bounds[i], 2)
                })
            
            # Calculate trend indicators
            short_term_trend = self._calculate_trend(forecast_values[:30])
            medium_term_trend = self._calculate_trend(forecast_values[:60])
            long_term_trend = self._calculate_trend(forecast_values)
            
            return {
                'forecast': forecast_data,
                'confidence_interval': self.forecast_params["confidence_interval"],
                'trend_analysis': {
                    'short_term': {
                        'direction': short_term_trend,
                        'period': '30 days'
                    },
                    'medium_term': {
                        'direction': medium_term_trend,
                        'period': '60 days'
                    },
                    'long_term': {
                        'direction': long_term_trend,
                        'period': f'{horizon_days} days'
                    }
                },
                'last_observed_score': round(df['score'].iloc[-1], 2),
                'last_observed_date': df['date'].iloc[-1].strftime('%Y-%m-%d'),
                'forecast_generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error forecasting sustainability: {str(e)}")
            return {
                "error": str(e),
                "forecast": []
            }
    
    def analyze_market_correlation(
        self, 
        sustainability_data: List[Dict], 
        token_price_data: List[Dict]
    ) -> Dict:
        """
        Analyze correlation between sustainability scores and token prices.
        
        Args:
            sustainability_data: List of dictionaries with historical sustainability scores.
                Each dictionary should have at least 'date' and 'score' keys.
            token_price_data: List of dictionaries with historical token prices.
                Each dictionary should have at least 'date' and 'price' keys.
            
        Returns:
            Dictionary with correlation analysis results.
        """
        try:
            # Convert to DataFrames
            if not sustainability_data or not token_price_data:
                return {
                    "error": "Insufficient data provided",
                    "correlation": None
                }
            
            # Process sustainability data
            sustainability_dates = []
            sustainability_scores = []
            
            for entry in sustainability_data:
                if isinstance(entry.get('date'), str):
                    try:
                        date = datetime.fromisoformat(entry['date'].replace('Z', '+00:00'))
                    except ValueError:
                        try:
                            date = datetime.strptime(entry['date'], '%Y-%m-%d')
                        except ValueError:
                            continue
                elif isinstance(entry.get('date'), datetime):
                    date = entry['date']
                else:
                    continue
                
                score = entry.get('score') or entry.get('sustainability_score')
                if score is not None:
                    sustainability_dates.append(date)
                    sustainability_scores.append(float(score))
            
            # Process token price data
            price_dates = []
            prices = []
            
            for entry in token_price_data:
                if isinstance(entry.get('date'), str):
                    try:
                        date = datetime.fromisoformat(entry['date'].replace('Z', '+00:00'))
                    except ValueError:
                        try:
                            date = datetime.strptime(entry['date'], '%Y-%m-%d')
                        except ValueError:
                            continue
                elif isinstance(entry.get('date'), datetime):
                    date = entry['date']
                else:
                    continue
                
                price = entry.get('price')
                if price is not None:
                    price_dates.append(date)
                    prices.append(float(price))
            
            # Create DataFrames
            sustainability_df = pd.DataFrame({
                'date': sustainability_dates,
                'score': sustainability_scores
            })
            
            price_df = pd.DataFrame({
                'date': price_dates,
                'price': prices
            })
            
            # Ensure we have enough data
            if len(sustainability_df) < 10 or len(price_df) < 10:
                return {
                    "error": "Insufficient data points for correlation analysis",
                    "correlation": None
                }
            
            # Merge data on date
            # First convert date to date-only format to allow matching
            sustainability_df['date'] = pd.to_datetime(sustainability_df['date']).dt.date
            price_df['date'] = pd.to_datetime(price_df['date']).dt.date
            
            # Merge and sort by date
            merged_df = pd.merge(sustainability_df, price_df, on='date', how='inner')
            merged_df = merged_df.sort_values('date')
            
            # Apply smoothing if specified
            if self.market_params["smoothing_window"] > 1:
                merged_df['score'] = merged_df['score'].rolling(
                    window=self.market_params["smoothing_window"], 
                    min_periods=1
                ).mean()
                
                merged_df['price'] = merged_df['price'].rolling(
                    window=self.market_params["smoothing_window"], 
                    min_periods=1
                ).mean()
            
            # Calculate correlation for different lag periods
            correlation_results = []
            
            for lag in self.market_params["lag_days"]:
                if lag > 0:
                    # Shift sustainability scores back by lag days
                    merged_df[f'score_lag_{lag}'] = merged_df['score'].shift(lag)
                    
                    # Calculate correlation between lagged score and price
                    valid_data = merged_df.dropna()
                    
                    if len(valid_data) >= 5:  # Need at least 5 points for meaningful correlation
                        corr, p_value = stats.pearsonr(valid_data[f'score_lag_{lag}'], valid_data['price'])
                        
                        correlation_results.append({
                            'lag_days': lag,
                            'correlation': round(corr, 3),
                            'p_value': round(p_value, 4),
                            'significant': p_value < self.market_params["significance_threshold"],
                            'sample_size': len(valid_data)
                        })
                else:
                    # Calculate direct correlation (no lag)
                    corr, p_value = stats.pearsonr(merged_df['score'], merged_df['price'])
                    
                    correlation_results.append({
                        'lag_days': 0,
                        'correlation': round(corr, 3),
                        'p_value': round(p_value, 4),
                        'significant': p_value < self.market_params["significance_threshold"],
                        'sample_size': len(merged_df)
                    })
            
            # Find the strongest correlation
            strongest_corr = max(correlation_results, key=lambda x: abs(x['correlation']))
            
            # Calculate price impact
            price_impact = self._calculate_price_impact(merged_df)
            
            return {
                'overall_correlation': round(corr, 3),
                'lag_analysis': correlation_results,
                'strongest_correlation': strongest_corr,
                'price_impact': price_impact,
                'analysis_period': {
                    'start_date': merged_df['date'].iloc[0].strftime('%Y-%m-%d'),
                    'end_date': merged_df['date'].iloc[-1].strftime('%Y-%m-%d'),
                    'days': len(merged_df)
                },
                'interpretation': self._interpret_correlation(strongest_corr),
                'analysis_generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market correlation: {str(e)}")
            return {
                "error": str(e),
                "correlation": None
            }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """
        Calculate the trend direction from a list of values.
        
        Args:
            values: List of numeric values.
            
        Returns:
            String indicating trend direction ('upward', 'downward', or 'stable').
        """
        if not values or len(values) < 2:
            return 'unknown'
            
        # Simple linear regression
        x = list(range(len(values)))
        slope, _, _, _, _ = stats.linregress(x, values)
        
        # Determine trend direction
        if slope > 0.05:
            return 'upward'
        elif slope < -0.05:
            return 'downward'
        else:
            return 'stable'
    
    def _calculate_price_impact(self, data: pd.DataFrame) -> Dict:
        """
        Calculate the estimated price impact of sustainability score changes.
        
        Args:
            data: DataFrame with 'score' and 'price' columns.
            
        Returns:
            Dictionary with price impact analysis.
        """
        try:
            # Calculate average price
            avg_price = data['price'].mean()
            
            # Group by score ranges
            data['score_range'] = pd.cut(data['score'], bins=[0, 30, 60, 90, 100], 
                                        labels=['Poor (0-30)', 'Average (30-60)', 
                                                'Good (60-90)', 'Excellent (90-100)'])
            
            # Calculate average price for each score range
            price_by_range = data.groupby('score_range')['price'].mean().to_dict()
            
            # Calculate percentage difference from average
            price_impact = {}
            for score_range, price in price_by_range.items():
                if avg_price > 0:
                    percentage_diff = ((price / avg_price) - 1) * 100
                    price_impact[str(score_range)] = round(percentage_diff, 2)
            
            return {
                'average_price': round(avg_price, 4),
                'price_by_score_range': {k: round(v, 4) for k, v in price_by_range.items()},
                'percentage_impact': price_impact
            }
            
        except Exception as e:
            logger.error(f"Error calculating price impact: {str(e)}")
            return {
                'error': str(e)
            }
    
    def _interpret_correlation(self, correlation_data: Dict) -> str:
        """
        Generate a human-readable interpretation of correlation results.
        
        Args:
            correlation_data: Dictionary with correlation analysis.
            
        Returns:
            String with interpretation.
        """
        corr = correlation_data.get('correlation', 0)
        lag = correlation_data.get('lag_days', 0)
        significant = correlation_data.get('significant', False)
        
        if not significant:
            return "No statistically significant correlation found between sustainability scores and token prices."
        
        strength = "strong" if abs(corr) > 0.7 else "moderate" if abs(corr) > 0.4 else "weak"
        direction = "positive" if corr > 0 else "negative"
        
        if lag == 0:
            return f"There is a {strength} {direction} correlation ({corr}) between sustainability scores and token prices, suggesting that higher scores {'are associated with higher' if corr > 0 else 'are associated with lower'} token prices."
        else:
            return f"There is a {strength} {direction} correlation ({corr}) between sustainability scores and token prices after {lag} days, suggesting that improvements in sustainability {'may lead to higher' if corr > 0 else 'may lead to lower'} token prices after a {lag}-day lag." 
 
 