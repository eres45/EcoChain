import os
import json
import random
import requests
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
import math
import random
from ecochain.analysis_module.sustainability_scorer import SustainabilityScorer

logger = logging.getLogger(__name__)

class DataCollector:
    """
    Class responsible for collecting mining operation data and carbon footprint information.
    In a real implementation, this would connect to APIs and data sources.
    For demonstration purposes, we're using mock data with some real-world patterns.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the data collector with configuration."""
        self.config = {}
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        
        # Default API endpoints that could be overridden by config
        self.mining_api = self.config.get('mining_api', 'https://api.example.com/mining')
        self.carbon_api = self.config.get('carbon_api', 'https://api.example.com/carbon')
        self.api_key = self.config.get('api_key', '')

    def get_mining_operations(self) -> List[Dict]:
        """
        Get data about active mining operations.
        
        Returns:
            List of dictionaries containing mining operation data.
        """
        try:
            # In a real implementation, we would make an API call like:
            # response = requests.get(
            #     f"{self.mining_api}/operations", 
            #     headers={"Authorization": f"Bearer {self.api_key}"}
            # )
            # return response.json()["operations"]
            
            # For demo purposes, return mock data
            return self._generate_mock_mining_data()
        except Exception as e:
            logger.error(f"Error fetching mining operations: {str(e)}")
            return []
    
    def get_carbon_data(self, mining_operation_id: str) -> Dict:
        """
        Get carbon footprint data for a specific mining operation.
        
        Args:
            mining_operation_id: ID of the mining operation to get carbon data for.
            
        Returns:
            Dictionary with carbon footprint data.
        """
        try:
            # In a real implementation, we would make an API call like:
            # response = requests.get(
            #     f"{self.carbon_api}/footprint/{mining_operation_id}", 
            #     headers={"Authorization": f"Bearer {self.api_key}"}
            # )
            # return response.json()
            
            # For demo purposes, return mock data
            return self._generate_mock_carbon_data(mining_operation_id)
        except Exception as e:
            logger.error(f"Error fetching carbon data for operation {mining_operation_id}: {str(e)}")
            return {}
    
    def get_energy_mix_data(self, location: str) -> Dict:
        """
        Get energy mix data for a specific location.
        
        Args:
            location: Location identifier (country/region code).
            
        Returns:
            Dictionary with energy mix data (percentages of renewable vs non-renewable).
        """
        try:
            # In a real implementation, we would call an energy mix API
            # For demo purposes, return mock data
            return self._generate_mock_energy_mix(location)
        except Exception as e:
            logger.error(f"Error fetching energy mix for location {location}: {str(e)}")
            return {"renewable": 0, "fossil": 0, "nuclear": 0}
    
    def _generate_mock_mining_data(self) -> List[Dict]:
        """Generate realistic mock mining operation data."""
        countries = ["USA", "China", "Russia", "Kazakhstan", "Canada", "Iceland", "Sweden", "Norway"]
        currencies = ["BTC", "ETH", "XMR"]
        
        operations = []
        for i in range(50):  # Generate 50 mock operations
            country = random.choice(countries)
            
            # Create more realistic hashrates based on currency
            currency = random.choice(currencies)
            if currency == "BTC":
                hashrate = random.uniform(10, 500)  # TH/s
                hashrate_unit = "TH/s"
            elif currency == "ETH":
                hashrate = random.uniform(100, 5000)  # MH/s
                hashrate_unit = "MH/s"
            else:  # XMR
                hashrate = random.uniform(5, 100)  # KH/s
                hashrate_unit = "KH/s"
            
            operations.append({
                "id": f"miner-{i:04d}",
                "name": f"Mining Operation {i}",
                "currency": currency,
                "hashrate": hashrate,
                "hashrate_unit": hashrate_unit,
                "location": country,
                "active_miners": random.randint(10, 10000),
                "power_consumption_kw": random.uniform(10, 5000),
                "uptime_percentage": random.uniform(85, 99.99),
                "wallet_address": f"0x{random.getrandbits(160):040x}"  # Random ETH-like address
            })
        
        return operations
    
    def _generate_mock_carbon_data(self, operation_id: str) -> Dict:
        """Generate realistic mock carbon footprint data for a mining operation."""
        # Extract operation number from ID for consistent random generation
        op_num = int(operation_id.split('-')[-1]) if '-' in operation_id else hash(operation_id)
        random.seed(op_num)  # Use operation ID as seed for consistent randomization
        
        return {
            "operation_id": operation_id,
            "carbon_footprint_tons_per_day": random.uniform(0.5, 100),
            "energy_efficiency_rating": random.uniform(0.1, 0.95),
            "carbon_offset_percentage": random.uniform(0, 100),
            "renewable_energy_percentage": random.uniform(0, 100),
            "sustainability_initiatives": random.randint(0, 5),
            "last_updated": "2023-06-15T00:00:00Z"  # In real implementation, this would be current timestamp
        }
    
    def _generate_mock_energy_mix(self, location: str) -> Dict:
        """Generate realistic mock energy mix data based on location."""
        # Seed random with location for consistent results
        random.seed(hash(location))
        
        # Different locations have different typical energy mixes
        if location in ["Iceland", "Norway", "Sweden"]:
            # Nordic countries have high renewable percentages
            renewable = random.uniform(70, 98)
            nuclear = random.uniform(0, 20)
            fossil = 100 - renewable - nuclear
        elif location in ["China", "Russia", "Kazakhstan"]:
            # These countries often have lower renewable percentages
            renewable = random.uniform(15, 40)
            nuclear = random.uniform(5, 20)
            fossil = 100 - renewable - nuclear
        else:
            # Default mix
            renewable = random.uniform(20, 60)
            nuclear = random.uniform(10, 30)
            fossil = 100 - renewable - nuclear
        
        return {
            "location": location,
            "renewable_percentage": renewable,
            "fossil_percentage": fossil,
            "nuclear_percentage": nuclear,
            "renewable_breakdown": {
                "solar": random.uniform(0, renewable),
                "wind": random.uniform(0, renewable),
                "hydro": random.uniform(0, renewable),
                "geothermal": random.uniform(0, renewable),
                "biomass": random.uniform(0, renewable),
            }
        }

    def get_historical_scores(self, days: int = 180, operation_id: Optional[str] = None) -> List[Dict]:
        """
        Get historical sustainability scores.
        
        Args:
            days: Number of days of historical data to retrieve.
            operation_id: Optional operation ID to filter by.
            
        Returns:
            List of dictionaries with historical score data.
        """
        # In a real implementation, this would query a database
        # For demonstration, we'll generate synthetic data
        
        try:
            today = datetime.now()
            start_date = today - timedelta(days=days)
            
            # Generate daily data points
            data_points = []
            
            if operation_id:
                # Generate data for a specific operation
                operation = self.get_mining_operations()[int(operation_id.split('-')[-1])]
                if not operation:
                    logger.warning(f"Operation {operation_id} not found")
                    return []
                
                # Get the current score as a reference
                carbon_data = self.get_carbon_data(operation_id)
                current_score = 70  # Default if no data available
                
                if carbon_data:
                    scorer = SustainabilityScorer()
                    score_result = scorer.score_operation(operation, carbon_data)
                    current_score = score_result.get("sustainability_score", 70)
                
                # Generate historical data with realistic patterns
                for i in range(days):
                    date = start_date + timedelta(days=i)
                    
                    # Add trend (gradual improvement over time)
                    trend_factor = i / days * 10  # Up to 10 point improvement over the period
                    
                    # Add seasonality (weekly pattern)
                    day_of_week = date.weekday()
                    seasonality = math.sin(day_of_week * math.pi / 3.5) * 3  # ±3 points weekly cycle
                    
                    # Add some randomness
                    noise = random.normalvariate(0, 2)  # Random noise with std dev of 2
                    
                    # Calculate score for this day
                    base_score = max(0, min(100, current_score - trend_factor))
                    score = base_score + seasonality + noise
                    score = max(0, min(100, score))  # Ensure within valid range
                    
                    data_points.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "operation_id": operation_id,
                        "score": round(score, 2)
                    })
            else:
                # Generate average data across all operations
                operations = self.get_mining_operations()
                if not operations:
                    logger.warning("No operations found")
                    return []
                
                # Calculate average current score
                total_score = 0
                count = 0
                
                for op in operations:
                    carbon_data = self.get_carbon_data(op["id"])
                    if carbon_data:
                        scorer = SustainabilityScorer()
                        score_result = scorer.score_operation(op, carbon_data)
                        total_score += score_result.get("sustainability_score", 70)
                        count += 1
                
                current_score = total_score / count if count > 0 else 70
                
                # Generate historical data with realistic patterns
                for i in range(days):
                    date = start_date + timedelta(days=i)
                    
                    # Add trend (gradual improvement over time)
                    trend_factor = i / days * 8  # Up to 8 point improvement over the period
                    
                    # Add seasonality (weekly pattern)
                    day_of_week = date.weekday()
                    seasonality = math.sin(day_of_week * math.pi / 3.5) * 2  # ±2 points weekly cycle
                    
                    # Add some randomness
                    noise = random.normalvariate(0, 1.5)  # Random noise with std dev of 1.5
                    
                    # Calculate score for this day
                    base_score = max(0, min(100, current_score - trend_factor))
                    score = base_score + seasonality + noise
                    score = max(0, min(100, score))  # Ensure within valid range
                    
                    data_points.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "score": round(score, 2)
                    })
            
            return data_points
            
        except Exception as e:
            logger.error(f"Error getting historical scores: {str(e)}")
            return []
    
    def get_token_prices(self, days: int = 180) -> List[Dict]:
        """
        Get historical token prices.
        
        Args:
            days: Number of days of historical data to retrieve.
            
        Returns:
            List of dictionaries with historical price data.
        """
        # In a real implementation, this would query a price API or database
        # For demonstration, we'll generate synthetic data
        
        try:
            today = datetime.now()
            start_date = today - timedelta(days=days)
            
            # Generate daily data points
            data_points = []
            
            # Set base price
            base_price = 1.25  # $1.25 USD
            
            # Generate price data with realistic patterns
            for i in range(days):
                date = start_date + timedelta(days=i)
                
                # Add trend (gradual increase over time)
                trend_factor = i / days * 0.5  # Up to $0.50 increase over the period
                
                # Add market cycles (30-day cycle)
                market_cycle = math.sin(i * math.pi / 15) * 0.15  # ±$0.15 market cycle
                
                # Add some randomness (volatility)
                volatility = random.normalvariate(0, 0.03)  # Random noise with std dev of $0.03
                
                # Calculate price for this day
                price = base_price + trend_factor + market_cycle + volatility
                price = max(0.1, price)  # Ensure price is positive
                
                data_points.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "price": round(price, 4),
                    "volume": round(random.uniform(100000, 500000), 0),
                    "market_cap": round(price * 10000000, 0)  # Assuming 10M token supply
                })
            
            return data_points
            
        except Exception as e:
            logger.error(f"Error getting token prices: {str(e)}")
            return [] 