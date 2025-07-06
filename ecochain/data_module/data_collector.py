import os
import json
import random
import requests
from typing import Dict, List, Optional
import logging

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