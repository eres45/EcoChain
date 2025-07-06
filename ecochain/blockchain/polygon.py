"""
Polygon Chain Adapter

This module implements an adapter for interacting with the Polygon blockchain.
Polygon is an EVM-compatible sidechain that is more energy efficient than Ethereum.
"""

import logging
from typing import Dict, Any

from ecochain.blockchain.ethereum import EthereumAdapter

logger = logging.getLogger(__name__)

class PolygonAdapter(EthereumAdapter):
    """
    Adapter for the Polygon blockchain.
    
    This adapter extends the Ethereum adapter since Polygon is EVM-compatible,
    but with specific configurations for Polygon networks.
    """
    
    @property
    def name(self) -> str:
        """Get the name of the blockchain."""
        return "Polygon"
    
    @property
    def native_token(self) -> str:
        """Get the native token symbol of the blockchain."""
        return "MATIC"
    
    @property
    def consensus_mechanism(self) -> str:
        """Get the consensus mechanism of the blockchain."""
        return "PoS"  # Polygon uses Proof of Stake
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Polygon adapter.
        
        Args:
            config: Configuration dictionary for the adapter.
        """
        super().__init__(config)
        
        # Set default chain ID if not provided
        if not self.chain_id:
            if self.network == "mainnet":
                self.chain_id = 137
            elif self.network == "mumbai":
                self.chain_id = 80001
            
        # Set default provider URL if not provided
        if not self.provider_url:
            if self.network == "mainnet":
                self.provider_url = f"https://polygon-mainnet.infura.io/v3/{config.get('infura_key', '')}"
            elif self.network == "mumbai":
                self.provider_url = f"https://polygon-mumbai.infura.io/v3/{config.get('infura_key', '')}"
            else:
                self.provider_url = config.get('provider_url', "https://polygon-rpc.com")
            
        # Set explorer URL if not provided
        if not self.explorer_url:
            if self.network == "mainnet":
                self.explorer_url = "https://polygonscan.com"
            elif self.network == "mumbai":
                self.explorer_url = "https://mumbai.polygonscan.com"
    
    def connect(self) -> bool:
        """
        Connect to the Polygon network.
        
        Returns:
            True if connected successfully, False otherwise.
        """
        try:
            # Use the parent class connect method
            result = super().connect()
            
            if result:
                logger.info(f"Connected to Polygon {self.network} network")
            else:
                logger.error(f"Failed to connect to Polygon {self.network} network")
            
            return result
        except Exception as e:
            logger.error(f"Error connecting to Polygon {self.network}: {str(e)}")
            return False
    
    def get_chain_info(self) -> Dict:
        """
        Get general information about the blockchain.
        
        Returns:
            Dictionary containing chain information.
        """
        info = super().get_chain_info()
        
        # Add Polygon-specific information
        info.update({
            'is_l2': True,
            'parent_chain': 'Ethereum',
            'avg_block_time': 2.0,  # seconds
            'tx_throughput': '~2000 TPS'
        })
        
        return info 
 
 