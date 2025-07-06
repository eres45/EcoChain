"""
Oracle Network for Carbon Data Reporting

This module implements a decentralized oracle network for aggregating,
validating, and delivering carbon data from multiple trusted sources.
"""

import logging
import time
import uuid
import json
import math
import statistics
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib

from ecochain.oracles.data_provider import DataProvider
from ecochain.oracles.reputation_system import ReputationSystem
from ecochain.blockchain.chain_adapter import ChainAdapter

logger = logging.getLogger(__name__)

@dataclass
class DataRequest:
    """Data request from a consumer to the oracle network."""
    request_id: str
    data_type: str  # Type of data being requested
    parameters: Dict[str, Any]  # Parameters for the data request
    requester: str  # Address or identifier of the requester
    timestamp: float = field(default_factory=lambda: time.time())
    deadline: Optional[float] = None  # Deadline for the request
    min_providers: int = 3  # Minimum number of data providers needed
    min_reputation: float = 50.0  # Minimum reputation score for providers
    status: str = "PENDING"  # Status of the request
    result: Optional[Any] = None  # Result of the request

@dataclass
class DataResponse:
    """Response from a data provider to a data request."""
    request_id: str
    provider_id: str
    data: Any
    timestamp: float = field(default_factory=lambda: time.time())
    signature: Optional[str] = None  # Provider's signature
    status: str = "SUBMITTED"  # Status of the response
    verification_result: Optional[bool] = None  # Result of verification

class OracleNetwork:
    """
    Decentralized Oracle Network for Carbon Data
    
    This class coordinates data providers and validators to deliver
    reliable carbon data to consumers on the blockchain.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the oracle network.
        
        Args:
            config: Configuration dictionary for the network.
        """
        self.config = config
        self.data_providers = {}  # provider_id -> DataProvider
        self.reputation_system = ReputationSystem()
        self.requests = {}  # request_id -> DataRequest
        self.responses = {}  # request_id -> list of DataResponse
        self.chain_adapters = {}  # chain_name -> ChainAdapter
        self.on_chain_contracts = {}  # chain_name -> contract_address
        
        # Aggregation methods
        self.aggregation_methods = {
            "mean": statistics.mean,
            "median": statistics.median,
            "mode": statistics.mode,
            "weighted_mean": self._weighted_mean,
            "trimmed_mean": lambda values, weights=None: statistics.mean(sorted(values)[1:-1] if len(values) > 3 else values)
        }
        
        # Default aggregation method
        self.default_aggregation = config.get('default_aggregation', 'weighted_mean')
        
        # Rewards
        self.base_reward = config.get('base_reward', 1.0)  # Base reward for providers
        self.accuracy_bonus = config.get('accuracy_bonus', 0.5)  # Bonus for accurate data
        
        # Oracle parameters
        self.consensus_threshold = config.get('consensus_threshold', 0.7)  # Required agreement percentage
        self.valid_time_window = config.get('valid_time_window', 3600)  # Valid time window for responses (seconds)
        self.auto_finalize = config.get('auto_finalize', True)  # Auto-finalize requests when enough responses
    
    def register_provider(self, provider: DataProvider) -> bool:
        """
        Register a new data provider with the network.
        
        Args:
            provider: The data provider to register.
            
        Returns:
            True if registration was successful, False otherwise.
        """
        provider_id = provider.provider_id
        
        # Check if provider already exists
        if provider_id in self.data_providers:
            logger.warning(f"Provider {provider_id} already registered")
            return False
        
        # Register the provider
        self.data_providers[provider_id] = provider
        
        # Initialize reputation if needed
        if not self.reputation_system.has_entity(provider_id):
            self.reputation_system.add_entity(provider_id)
        
        logger.info(f"Registered data provider {provider_id} ({provider.name})")
        return True
    
    def remove_provider(self, provider_id: str) -> bool:
        """
        Remove a data provider from the network.
        
        Args:
            provider_id: ID of the provider to remove.
            
        Returns:
            True if removal was successful, False otherwise.
        """
        # Check if provider exists
        if provider_id not in self.data_providers:
            logger.warning(f"Provider {provider_id} not registered")
            return False
        
        # Remove the provider
        del self.data_providers[provider_id]
        logger.info(f"Removed data provider {provider_id}")
        return True
    
    def get_provider(self, provider_id: str) -> Optional[DataProvider]:
        """
        Get a registered data provider.
        
        Args:
            provider_id: ID of the provider.
            
        Returns:
            The data provider or None if not found.
        """
        return self.data_providers.get(provider_id)
    
    def list_providers(self, min_reputation: float = 0.0) -> List[Dict[str, Any]]:
        """
        List all registered data providers.
        
        Args:
            min_reputation: Minimum reputation score to filter by.
            
        Returns:
            List of provider information dictionaries.
        """
        providers = []
        
        for provider_id, provider in self.data_providers.items():
            reputation = self.reputation_system.get_score(provider_id)
            if reputation >= min_reputation:
                providers.append({
                    "provider_id": provider_id,
                    "name": provider.name,
                    "data_types": provider.supported_data_types,
                    "reputation": reputation,
                    "response_count": provider.response_count,
                    "last_updated": provider.last_updated
                })
        
        return sorted(providers, key=lambda p: p["reputation"], reverse=True)
    
    def submit_request(self, data_type: str, parameters: Dict[str, Any],
                      requester: str, deadline: Optional[float] = None,
                      min_providers: int = 3, min_reputation: float = 50.0) -> str:
        """
        Submit a new data request to the oracle network.
        
        Args:
            data_type: Type of data being requested.
            parameters: Parameters for the data request.
            requester: Address or identifier of the requester.
            deadline: Optional deadline for the request.
            min_providers: Minimum number of data providers needed.
            min_reputation: Minimum reputation score for providers.
            
        Returns:
            The request ID.
        """
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        
        # Create a new request
        request = DataRequest(
            request_id=request_id,
            data_type=data_type,
            parameters=parameters,
            requester=requester,
            timestamp=time.time(),
            deadline=deadline,
            min_providers=min_providers,
            min_reputation=min_reputation
        )
        
        # Store the request
        self.requests[request_id] = request
        self.responses[request_id] = []
        
        logger.info(f"Submitted request {request_id} for {data_type}")
        
        # Notify eligible providers
        self._notify_providers(request)
        
        return request_id
    
    def _notify_providers(self, request: DataRequest) -> int:
        """
        Notify eligible providers about a new data request.
        
        Args:
            request: The data request.
            
        Returns:
            Number of providers notified.
        """
        notified = 0
        
        for provider_id, provider in self.data_providers.items():
            # Check if provider supports the data type
            if request.data_type not in provider.supported_data_types:
                continue
            
            # Check if provider has sufficient reputation
            reputation = self.reputation_system.get_score(provider_id)
            if reputation < request.min_reputation:
                continue
            
            # Notify provider
            try:
                provider.notify_request(request.request_id, request.data_type, request.parameters)
                notified += 1
            except Exception as e:
                logger.error(f"Error notifying provider {provider_id}: {e}")
        
        logger.info(f"Notified {notified} providers about request {request.request_id}")
        return notified
    
    def submit_response(self, request_id: str, provider_id: str, data: Any,
                       signature: Optional[str] = None) -> bool:
        """
        Submit a response to a data request.
        
        Args:
            request_id: ID of the request.
            provider_id: ID of the provider submitting the response.
            data: The data being provided.
            signature: Optional signature to verify the response.
            
        Returns:
            True if submission was successful, False otherwise.
        """
        # Check if request exists
        if request_id not in self.requests:
            logger.warning(f"Request {request_id} not found")
            return False
        
        # Check if provider exists
        if provider_id not in self.data_providers:
            logger.warning(f"Provider {provider_id} not registered")
            return False
        
        # Get request
        request = self.requests[request_id]
        
        # Check if request is still open
        if request.status != "PENDING":
            logger.warning(f"Request {request_id} is not pending (status: {request.status})")
            return False
        
        # Check if deadline has passed
        if request.deadline and time.time() > request.deadline:
            request.status = "EXPIRED"
            logger.warning(f"Request {request_id} has expired")
            return False
        
        # Check if provider has already submitted a response
        if any(response.provider_id == provider_id for response in self.responses[request_id]):
            logger.warning(f"Provider {provider_id} has already submitted a response")
            return False
        
        # Create a new response
        response = DataResponse(
            request_id=request_id,
            provider_id=provider_id,
            data=data,
            timestamp=time.time(),
            signature=signature
        )
        
        # Store the response
        self.responses[request_id].append(response)
        
        # Update provider's response count
        self.data_providers[provider_id].response_count += 1
        self.data_providers[provider_id].last_updated = time.time()
        
        logger.info(f"Received response from provider {provider_id} for request {request_id}")
        
        # Verify the response
        self._verify_response(response)
        
        # Check if we have enough responses to finalize
        if self.auto_finalize and len(self.responses[request_id]) >= request.min_providers:
            self.finalize_request(request_id)
        
        return True
    
    def _verify_response(self, response: DataResponse) -> bool:
        """
        Verify a response from a data provider.
        
        Args:
            response: The response to verify.
            
        Returns:
            True if verification was successful, False otherwise.
        """
        # In a real implementation, this would verify the signature
        # and perform other validation checks
        
        # For now, just mark it as verified
        response.status = "VERIFIED"
        response.verification_result = True
        
        return True
    
    def finalize_request(self, request_id: str) -> Dict:
        """
        Finalize a data request by aggregating responses and calculating the result.
        
        Args:
            request_id: ID of the request to finalize.
            
        Returns:
            Dictionary with result information.
        """
        # Check if request exists
        if request_id not in self.requests:
            logger.warning(f"Request {request_id} not found")
            return {"success": False, "error": "Request not found"}
        
        # Get request and responses
        request = self.requests[request_id]
        responses = self.responses[request_id]
        
        # Check if we have enough responses
        if len(responses) < request.min_providers:
            logger.warning(f"Not enough responses for request {request_id}")
            return {"success": False, "error": "Not enough responses"}
        
        # Filter out invalid responses
        valid_responses = [r for r in responses if r.status == "VERIFIED" and r.verification_result]
        
        if len(valid_responses) < request.min_providers:
            logger.warning(f"Not enough valid responses for request {request_id}")
            return {"success": False, "error": "Not enough valid responses"}
        
        # Get data from responses
        try:
            # The structure of data depends on the data type
            # For numerical data, we can use statistical aggregation
            if isinstance(valid_responses[0].data, (int, float)):
                values = [r.data for r in valid_responses]
                weights = [self.reputation_system.get_score(r.provider_id) for r in valid_responses]
                
                # Aggregate the data using the configured method
                aggregation_method = self.config.get('aggregation_method', self.default_aggregation)
                if aggregation_method not in self.aggregation_methods:
                    aggregation_method = self.default_aggregation
                
                if aggregation_method == "weighted_mean":
                    result = self._weighted_mean(values, weights)
                else:
                    result = self.aggregation_methods[aggregation_method](values)
                
                # Update the request
                request.result = result
                request.status = "FINALIZED"
                
                # Update provider reputations based on accuracy
                self._update_reputations(valid_responses, result)
                
                logger.info(f"Finalized request {request_id} with result {result}")
                
                # Distribute rewards
                self._distribute_rewards(valid_responses, result)
                
                return {
                    "success": True,
                    "request_id": request_id,
                    "result": result,
                    "providers": len(valid_responses),
                    "timestamp": time.time()
                }
            elif isinstance(valid_responses[0].data, dict):
                # For dictionary data, merge the dictionaries
                # This is a simple implementation; a real system would be more sophisticated
                result = {}
                for key in valid_responses[0].data.keys():
                    values = [r.data.get(key) for r in valid_responses if key in r.data]
                    if values:
                        if all(isinstance(v, (int, float)) for v in values):
                            result[key] = sum(values) / len(values)
                        else:
                            # For non-numeric values, use the most common value
                            result[key] = max(set(values), key=values.count)
                
                # Update the request
                request.result = result
                request.status = "FINALIZED"
                
                logger.info(f"Finalized request {request_id} with complex result")
                
                # Distribute rewards (simple implementation)
                self._distribute_rewards(valid_responses, None)
                
                return {
                    "success": True,
                    "request_id": request_id,
                    "result": result,
                    "providers": len(valid_responses),
                    "timestamp": time.time()
                }
            else:
                # For other types of data, more complex aggregation would be needed
                logger.warning(f"Unsupported data type for request {request_id}")
                return {"success": False, "error": "Unsupported data type"}
        except Exception as e:
            logger.error(f"Error finalizing request {request_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def _weighted_mean(self, values: List[float], weights: List[float]) -> float:
        """
        Calculate the weighted mean of a list of values.
        
        Args:
            values: List of values.
            weights: List of weights corresponding to the values.
            
        Returns:
            The weighted mean.
        """
        if not values:
            return 0.0
        
        if not weights or len(weights) != len(values):
            return statistics.mean(values)
        
        total_weight = sum(weights)
        if total_weight == 0:
            return statistics.mean(values)
        
        weighted_sum = sum(v * w for v, w in zip(values, weights))
        return weighted_sum / total_weight
    
    def _update_reputations(self, responses: List[DataResponse], result: float) -> None:
        """
        Update reputations of providers based on the accuracy of their responses.
        
        Args:
            responses: List of responses.
            result: The final result.
        """
        for response in responses:
            provider_id = response.provider_id
            data = response.data
            
            # Calculate accuracy (for numeric data)
            if isinstance(data, (int, float)) and result != 0:
                accuracy = 1.0 - min(1.0, abs(data - result) / abs(result))
                
                # Update reputation based on accuracy
                if accuracy > 0.95:  # Very accurate
                    self.reputation_system.update_score(provider_id, 2.0)
                elif accuracy > 0.9:  # Good accuracy
                    self.reputation_system.update_score(provider_id, 1.0)
                elif accuracy > 0.8:  # Reasonable accuracy
                    self.reputation_system.update_score(provider_id, 0.5)
                elif accuracy < 0.6:  # Poor accuracy
                    self.reputation_system.update_score(provider_id, -1.0)
                elif accuracy < 0.4:  # Very poor accuracy
                    self.reputation_system.update_score(provider_id, -2.0)
                    
                logger.debug(f"Updated reputation for provider {provider_id}: accuracy={accuracy:.2f}")
    
    def _distribute_rewards(self, responses: List[DataResponse], result: Any) -> None:
        """
        Distribute rewards to providers based on their responses.
        
        In a real implementation, this would interact with a blockchain
        to distribute token rewards.
        
        Args:
            responses: List of responses.
            result: The final result.
        """
        for response in responses:
            provider_id = response.provider_id
            data = response.data
            
            # Base reward
            reward = self.base_reward
            
            # Accuracy bonus for numeric data
            if isinstance(data, (int, float)) and isinstance(result, (int, float)) and result != 0:
                accuracy = 1.0 - min(1.0, abs(data - result) / abs(result))
                if accuracy > 0.9:
                    reward += self.accuracy_bonus
            
            logger.debug(f"Rewarded provider {provider_id} with {reward} tokens")
            
            # In a real implementation, this would send tokens to the provider
    
    def get_request_status(self, request_id: str) -> Dict:
        """
        Get the status of a data request.
        
        Args:
            request_id: ID of the request.
            
        Returns:
            Dictionary with request status information.
        """
        # Check if request exists
        if request_id not in self.requests:
            logger.warning(f"Request {request_id} not found")
            return {"success": False, "error": "Request not found"}
        
        # Get request and responses
        request = self.requests[request_id]
        responses = self.responses[request_id]
        
        return {
            "request_id": request_id,
            "data_type": request.data_type,
            "status": request.status,
            "timestamp": request.timestamp,
            "deadline": request.deadline,
            "requester": request.requester,
            "response_count": len(responses),
            "min_providers": request.min_providers,
            "result": request.result
        }
    
    def connect_blockchain(self, chain_name: str, adapter: ChainAdapter, 
                          contract_address: Optional[str] = None) -> bool:
        """
        Connect to a blockchain for on-chain integration.
        
        Args:
            chain_name: Name of the blockchain.
            adapter: The chain adapter to use.
            contract_address: Optional address of the oracle contract.
            
        Returns:
            True if connection was successful, False otherwise.
        """
        # Add the adapter
        self.chain_adapters[chain_name] = adapter
        
        # Connect to the blockchain
        if not adapter.connect():
            logger.error(f"Failed to connect to blockchain {chain_name}")
            return False
        
        # Set the contract address if provided
        if contract_address:
            self.on_chain_contracts[chain_name] = contract_address
        
        logger.info(f"Connected to blockchain {chain_name}")
        return True
    
    def publish_result(self, request_id: str, chain_name: str) -> Dict:
        """
        Publish a result to the blockchain.
        
        Args:
            request_id: ID of the request.
            chain_name: Name of the blockchain to publish to.
            
        Returns:
            Dictionary with transaction information.
        """
        # Check if request exists and is finalized
        if request_id not in self.requests:
            logger.warning(f"Request {request_id} not found")
            return {"success": False, "error": "Request not found"}
        
        request = self.requests[request_id]
        if request.status != "FINALIZED":
            logger.warning(f"Request {request_id} is not finalized")
            return {"success": False, "error": "Request not finalized"}
        
        # Check if we're connected to the blockchain
        if chain_name not in self.chain_adapters:
            logger.error(f"Not connected to blockchain {chain_name}")
            return {"success": False, "error": f"Not connected to blockchain {chain_name}"}
        
        # Check if we have a contract address
        if chain_name not in self.on_chain_contracts:
            logger.error(f"No oracle contract address for blockchain {chain_name}")
            return {"success": False, "error": f"No oracle contract address for blockchain {chain_name}"}
        
        # Get adapter and contract address
        adapter = self.chain_adapters[chain_name]
        contract_address = self.on_chain_contracts[chain_name]
        
        # Prepare the result for on-chain submission
        result_data = {
            "request_id": request_id,
            "result": request.result,
            "timestamp": int(time.time())
        }
        
        # In a real implementation, this would call the oracle contract
        # For now, just log the action
        logger.info(f"Publishing result for request {request_id} to blockchain {chain_name}")
        
        return {
            "success": True,
            "request_id": request_id,
            "chain": chain_name,
            "message": "Result published (simulated)",
            "data": result_data
        }
    
    def get_network_stats(self) -> Dict:
        """
        Get statistics about the oracle network.
        
        Returns:
            Dictionary with network statistics.
        """
        total_providers = len(self.data_providers)
        active_providers = sum(1 for p in self.data_providers.values() if time.time() - p.last_updated < 86400)
        
        total_requests = len(self.requests)
        pending_requests = sum(1 for r in self.requests.values() if r.status == "PENDING")
        finalized_requests = sum(1 for r in self.requests.values() if r.status == "FINALIZED")
        
        avg_reputation = 0.0
        if total_providers > 0:
            avg_reputation = sum(self.reputation_system.get_score(pid) for pid in self.data_providers.keys()) / total_providers
        
        return {
            "providers": {
                "total": total_providers,
                "active": active_providers
            },
            "requests": {
                "total": total_requests,
                "pending": pending_requests,
                "finalized": finalized_requests
            },
            "reputation": {
                "average": avg_reputation,
                "min": min((self.reputation_system.get_score(pid) for pid in self.data_providers.keys()), default=0.0),
                "max": max((self.reputation_system.get_score(pid) for pid in self.data_providers.keys()), default=0.0)
            },
            "blockchain_connections": list(self.chain_adapters.keys())
        } 
 
 