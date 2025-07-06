"""
Data Provider for Oracle Network

This module defines the data provider interface for the EcoChain Guardian
oracle network, allowing external data sources to provide carbon and
sustainability data.
"""

import logging
import time
import json
import uuid
import hashlib
import requests
from typing import Dict, List, Any, Optional, Callable, Union
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class DataProvider(ABC):
    """
    Abstract base class for data providers in the oracle network.
    
    Data providers are responsible for fetching data from external sources
    and submitting it to the oracle network in response to data requests.
    """
    
    def __init__(self, name: str, supported_data_types: List[str], config: Dict[str, Any]):
        """
        Initialize the data provider.
        
        Args:
            name: Name of the data provider.
            supported_data_types: List of data types supported by the provider.
            config: Configuration dictionary for the provider.
        """
        self.name = name
        self.supported_data_types = supported_data_types
        self.config = config
        self.provider_id = config.get('provider_id', str(uuid.uuid4()))
        self.response_count = 0
        self.last_updated = time.time()
        self.api_keys = config.get('api_keys', {})
        self.base_urls = config.get('base_urls', {})
        self.active = True
        self.pending_requests = {}  # request_id -> request details
        
        # Private key for signing responses (in a real system, this would be securely managed)
        self.private_key = config.get('private_key')
        
        # Function to call when submitting a response
        self.submit_callback = None
    
    def set_submit_callback(self, callback: Callable) -> None:
        """
        Set the callback function to call when submitting a response.
        
        Args:
            callback: The callback function.
        """
        self.submit_callback = callback
    
    def notify_request(self, request_id: str, data_type: str, parameters: Dict[str, Any]) -> bool:
        """
        Notify the provider about a new data request.
        
        Args:
            request_id: ID of the request.
            data_type: Type of data being requested.
            parameters: Parameters for the data request.
            
        Returns:
            True if the provider will handle the request, False otherwise.
        """
        # Check if the provider supports this data type
        if data_type not in self.supported_data_types:
            logger.warning(f"Provider {self.name} does not support data type {data_type}")
            return False
        
        # Check if the provider is active
        if not self.active:
            logger.warning(f"Provider {self.name} is not active")
            return False
        
        # Store the request
        self.pending_requests[request_id] = {
            "request_id": request_id,
            "data_type": data_type,
            "parameters": parameters,
            "timestamp": time.time(),
            "status": "PENDING"
        }
        
        logger.info(f"Provider {self.name} notified of request {request_id} for {data_type}")
        
        # Process the request asynchronously
        # In a real system, this would be done in a separate thread or task
        self._process_request(request_id)
        
        return True
    
    def _process_request(self, request_id: str) -> None:
        """
        Process a data request.
        
        Args:
            request_id: ID of the request.
        """
        # Check if the request exists
        if request_id not in self.pending_requests:
            logger.warning(f"Request {request_id} not found")
            return
        
        request = self.pending_requests[request_id]
        data_type = request["data_type"]
        parameters = request["parameters"]
        
        try:
            # Get the data
            data = self.fetch_data(data_type, parameters)
            
            # Update request status
            request["status"] = "PROCESSED"
            request["result"] = data
            
            # Sign the response
            signature = self._sign_response(request_id, data)
            
            # Submit the response
            self._submit_response(request_id, data, signature)
            
            logger.info(f"Provider {self.name} processed request {request_id}")
        except Exception as e:
            logger.error(f"Error processing request {request_id}: {e}")
            request["status"] = "FAILED"
            request["error"] = str(e)
    
    @abstractmethod
    def fetch_data(self, data_type: str, parameters: Dict[str, Any]) -> Any:
        """
        Fetch data from an external source.
        
        Args:
            data_type: Type of data being requested.
            parameters: Parameters for the data request.
            
        Returns:
            The fetched data.
        """
        pass
    
    def _sign_response(self, request_id: str, data: Any) -> Optional[str]:
        """
        Sign a response using the provider's private key.
        
        Args:
            request_id: ID of the request.
            data: The data to sign.
            
        Returns:
            The signature as a hexadecimal string or None if no private key is available.
        """
        if not self.private_key:
            return None
        
        # In a real system, this would use proper cryptographic signing
        # For this demo, use a simple hash-based approach
        message = f"{request_id}:{json.dumps(data, sort_keys=True)}"
        signature = hashlib.sha256((message + self.private_key).encode()).hexdigest()
        
        return signature
    
    def _submit_response(self, request_id: str, data: Any, signature: Optional[str] = None) -> bool:
        """
        Submit a response to the oracle network.
        
        Args:
            request_id: ID of the request.
            data: The data to submit.
            signature: Optional signature to verify the response.
            
        Returns:
            True if submission was successful, False otherwise.
        """
        if self.submit_callback:
            success = self.submit_callback(request_id, self.provider_id, data, signature)
            
            if success:
                self.response_count += 1
                self.last_updated = time.time()
            
            return success
        else:
            logger.warning(f"No submit callback set for provider {self.name}")
            return False
    
    def deactivate(self) -> None:
        """Deactivate the provider."""
        self.active = False
        logger.info(f"Provider {self.name} deactivated")
    
    def activate(self) -> None:
        """Activate the provider."""
        self.active = True
        logger.info(f"Provider {self.name} activated")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the provider.
        
        Returns:
            Dictionary with provider statistics.
        """
        return {
            "provider_id": self.provider_id,
            "name": self.name,
            "supported_data_types": self.supported_data_types,
            "response_count": self.response_count,
            "last_updated": self.last_updated,
            "active": self.active,
            "pending_requests": len(self.pending_requests)
        }


class CarbonEmissionsProvider(DataProvider):
    """
    Provider for carbon emissions data.
    """
    
    def fetch_data(self, data_type: str, parameters: Dict[str, Any]) -> Any:
        """
        Fetch carbon emissions data.
        
        Args:
            data_type: Type of data being requested.
            parameters: Parameters for the data request.
            
        Returns:
            The fetched data.
        """
        if data_type == "carbon_intensity":
            return self._fetch_carbon_intensity(parameters)
        elif data_type == "energy_mix":
            return self._fetch_energy_mix(parameters)
        elif data_type == "emissions_factor":
            return self._fetch_emissions_factor(parameters)
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
    
    def _fetch_carbon_intensity(self, parameters: Dict[str, Any]) -> float:
        """
        Fetch carbon intensity data (gCO2/kWh).
        
        Args:
            parameters: Parameters for the data request.
            
        Returns:
            Carbon intensity value.
        """
        # In a real implementation, this would call an external API
        # For this demo, return a simulated value
        
        region = parameters.get("region", "global")
        timestamp = parameters.get("timestamp", time.time())
        
        # Example API call (commented out)
        # url = f"{self.base_urls.get('carbon_intensity')}/intensity"
        # headers = {"Authorization": f"Bearer {self.api_keys.get('carbon_intensity')}"}
        # params = {"region": region, "datetime": datetime.fromtimestamp(timestamp).isoformat()}
        # response = requests.get(url, headers=headers, params=params)
        # data = response.json()
        # return data["intensity"]["forecast"]
        
        # Simulated values for different regions
        regional_factors = {
            "europe": 250.0,
            "north_america": 380.0,
            "asia": 450.0,
            "global": 400.0,
            "iceland": 20.0,
            "france": 70.0,
            "china": 550.0,
            "australia": 700.0
        }
        
        # Add some randomness
        import random
        base_value = regional_factors.get(region.lower(), 400.0)
        variation = base_value * 0.1  # 10% variation
        return base_value + random.uniform(-variation, variation)
    
    def _fetch_energy_mix(self, parameters: Dict[str, Any]) -> Dict[str, float]:
        """
        Fetch energy mix data (percentage of different sources).
        
        Args:
            parameters: Parameters for the data request.
            
        Returns:
            Dictionary with energy mix percentages.
        """
        region = parameters.get("region", "global")
        
        # Simulated values for different regions
        energy_mixes = {
            "europe": {
                "coal": 15.0,
                "gas": 20.0,
                "nuclear": 25.0,
                "hydro": 15.0,
                "wind": 15.0,
                "solar": 8.0,
                "biomass": 2.0
            },
            "north_america": {
                "coal": 25.0,
                "gas": 35.0,
                "nuclear": 20.0,
                "hydro": 8.0,
                "wind": 7.0,
                "solar": 3.0,
                "biomass": 2.0
            },
            "asia": {
                "coal": 45.0,
                "gas": 25.0,
                "nuclear": 10.0,
                "hydro": 12.0,
                "wind": 5.0,
                "solar": 2.0,
                "biomass": 1.0
            },
            "global": {
                "coal": 35.0,
                "gas": 25.0,
                "nuclear": 15.0,
                "hydro": 12.0,
                "wind": 8.0,
                "solar": 4.0,
                "biomass": 1.0
            }
        }
        
        # Add some randomness
        import random
        mix = energy_mixes.get(region.lower(), energy_mixes["global"]).copy()
        
        for source in mix:
            variation = mix[source] * 0.05  # 5% variation
            mix[source] += random.uniform(-variation, variation)
        
        # Normalize to ensure sum is 100%
        total = sum(mix.values())
        for source in mix:
            mix[source] = (mix[source] / total) * 100
        
        return mix
    
    def _fetch_emissions_factor(self, parameters: Dict[str, Any]) -> Dict[str, float]:
        """
        Fetch emissions factors for different energy sources (gCO2/kWh).
        
        Args:
            parameters: Parameters for the data request.
            
        Returns:
            Dictionary with emissions factors.
        """
        # These values are fairly standard across regions
        emissions_factors = {
            "coal": 820.0,
            "gas": 490.0,
            "nuclear": 12.0,
            "hydro": 24.0,
            "wind": 11.0,
            "solar": 45.0,
            "biomass": 230.0,
            "geothermal": 38.0
        }
        
        # Filter to requested sources if specified
        sources = parameters.get("sources")
        if sources:
            return {s: emissions_factors[s] for s in sources if s in emissions_factors}
        
        return emissions_factors


class RenewableCertificateProvider(DataProvider):
    """
    Provider for renewable energy certificate data.
    """
    
    def fetch_data(self, data_type: str, parameters: Dict[str, Any]) -> Any:
        """
        Fetch renewable energy certificate data.
        
        Args:
            data_type: Type of data being requested.
            parameters: Parameters for the data request.
            
        Returns:
            The fetched data.
        """
        if data_type == "certificate_verification":
            return self._verify_certificate(parameters)
        elif data_type == "certificate_pricing":
            return self._get_certificate_pricing(parameters)
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
    
    def _verify_certificate(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify a renewable energy certificate.
        
        Args:
            parameters: Parameters for the data request.
            
        Returns:
            Dictionary with verification result.
        """
        certificate_id = parameters.get("certificate_id")
        if not certificate_id:
            raise ValueError("Certificate ID is required")
        
        # In a real implementation, this would check a registry
        # For this demo, use some predefined valid certificates
        valid_certificates = {
            "REC-1234-5678-90AB": {
                "issuer": "Green-e Energy",
                "energy_source": "wind",
                "amount_kwh": 10000,
                "issue_date": "2023-01-15",
                "valid_until": "2024-01-15",
                "region": "north_america"
            },
            "REC-2345-6789-ABCD": {
                "issuer": "European Energy Certificate System",
                "energy_source": "solar",
                "amount_kwh": 5000,
                "issue_date": "2023-03-20",
                "valid_until": "2024-03-20",
                "region": "europe"
            },
            "REC-3456-789A-BCDE": {
                "issuer": "International REC Standard",
                "energy_source": "hydro",
                "amount_kwh": 15000,
                "issue_date": "2023-02-10",
                "valid_until": "2024-02-10",
                "region": "asia"
            }
        }
        
        if certificate_id in valid_certificates:
            return {
                "valid": True,
                "certificate": valid_certificates[certificate_id]
            }
        else:
            return {
                "valid": False,
                "reason": "Certificate not found or invalid"
            }
    
    def _get_certificate_pricing(self, parameters: Dict[str, Any]) -> Dict[str, float]:
        """
        Get pricing information for renewable energy certificates.
        
        Args:
            parameters: Parameters for the data request.
            
        Returns:
            Dictionary with pricing information.
        """
        region = parameters.get("region", "global")
        energy_source = parameters.get("energy_source")
        
        # Base prices per MWh in USD
        base_prices = {
            "wind": 1.50,
            "solar": 2.00,
            "hydro": 1.20,
            "biomass": 1.80,
            "geothermal": 2.50
        }
        
        # Regional modifiers
        regional_modifiers = {
            "north_america": 1.0,
            "europe": 1.2,
            "asia": 0.9,
            "australia": 1.1,
            "south_america": 0.8,
            "africa": 0.7,
            "global": 1.0
        }
        
        # Calculate prices
        prices = {}
        
        if energy_source:
            # Return price for specific source
            if energy_source not in base_prices:
                raise ValueError(f"Unsupported energy source: {energy_source}")
            
            modifier = regional_modifiers.get(region.lower(), 1.0)
            prices[energy_source] = base_prices[energy_source] * modifier
        else:
            # Return prices for all sources
            modifier = regional_modifiers.get(region.lower(), 1.0)
            for source, price in base_prices.items():
                prices[source] = price * modifier
        
        # Add some randomness
        import random
        for source in prices:
            variation = prices[source] * 0.1  # 10% variation
            prices[source] += random.uniform(-variation, variation)
            prices[source] = round(prices[source], 2)
        
        return prices 
 
 