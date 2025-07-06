"""
Base Chain Adapter for Multi-Chain Support

This module defines the base interface for blockchain adapters, which allow
EcoChain Guardian to interact with different blockchain networks.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union

class ChainAdapter(ABC):
    """
    Abstract base class for blockchain adapters.
    
    All blockchain-specific adapters should inherit from this class
    and implement its methods to provide consistent interfaces across chains.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the chain adapter.
        
        Args:
            config: Configuration dictionary for the adapter.
        """
        self.config = config
        self.chain_id = config.get('chain_id')
        self.network = config.get('network', 'mainnet')
        self.provider_url = config.get('provider_url')
        self.explorer_url = config.get('explorer_url')
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of the blockchain."""
        pass
    
    @property
    @abstractmethod
    def native_token(self) -> str:
        """Get the native token symbol of the blockchain."""
        pass
    
    @property
    @abstractmethod
    def consensus_mechanism(self) -> str:
        """Get the consensus mechanism of the blockchain."""
        pass
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to the blockchain network.
        
        Returns:
            True if connected successfully, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_balance(self, address: str) -> float:
        """
        Get the native token balance of an address.
        
        Args:
            address: Blockchain address to check.
            
        Returns:
            Balance of the address in native tokens.
        """
        pass
    
    @abstractmethod
    def deploy_contract(self, contract_name: str, contract_bytecode: str, 
                       abi: List[Dict], constructor_args: List = None) -> Dict:
        """
        Deploy a contract to the blockchain.
        
        Args:
            contract_name: Name of the contract.
            contract_bytecode: Compiled contract bytecode.
            abi: Contract ABI.
            constructor_args: Arguments for the contract constructor.
            
        Returns:
            Dictionary containing deployment information.
        """
        pass
    
    @abstractmethod
    def call_contract(self, contract_address: str, abi: List[Dict], 
                     function_name: str, args: List = None) -> Any:
        """
        Call a contract function (read-only).
        
        Args:
            contract_address: Address of the deployed contract.
            abi: Contract ABI.
            function_name: Name of the function to call.
            args: Arguments for the function.
            
        Returns:
            Result of the function call.
        """
        pass
    
    @abstractmethod
    def send_transaction(self, contract_address: str, abi: List[Dict], 
                        function_name: str, args: List = None, 
                        private_key: str = None) -> Dict:
        """
        Send a transaction to a contract function.
        
        Args:
            contract_address: Address of the deployed contract.
            abi: Contract ABI.
            function_name: Name of the function to call.
            args: Arguments for the function.
            private_key: Private key for signing the transaction.
            
        Returns:
            Dictionary containing transaction information.
        """
        pass
    
    @abstractmethod
    def get_transaction_receipt(self, tx_hash: str) -> Dict:
        """
        Get the receipt for a transaction.
        
        Args:
            tx_hash: Transaction hash.
            
        Returns:
            Dictionary containing transaction receipt information.
        """
        pass
    
    @abstractmethod
    def get_block(self, block_identifier: Union[int, str]) -> Dict:
        """
        Get information about a specific block.
        
        Args:
            block_identifier: Block number or hash.
            
        Returns:
            Dictionary containing block information.
        """
        pass
    
    @abstractmethod
    def estimate_gas(self, contract_address: str, abi: List[Dict], 
                    function_name: str, args: List = None) -> int:
        """
        Estimate gas for a transaction.
        
        Args:
            contract_address: Address of the deployed contract.
            abi: Contract ABI.
            function_name: Name of the function to call.
            args: Arguments for the function.
            
        Returns:
            Estimated gas amount.
        """
        pass
    
    @abstractmethod
    def get_token_balance(self, token_address: str, wallet_address: str) -> float:
        """
        Get the balance of a specific token for a wallet.
        
        Args:
            token_address: Address of the token contract.
            wallet_address: Address of the wallet.
            
        Returns:
            Token balance.
        """
        pass
    
    @abstractmethod
    def get_contract_events(self, contract_address: str, abi: List[Dict],
                           event_name: str, from_block: int = 0,
                           to_block: Union[int, str] = 'latest') -> List[Dict]:
        """
        Get events emitted by a contract.
        
        Args:
            contract_address: Address of the deployed contract.
            abi: Contract ABI.
            event_name: Name of the event to filter.
            from_block: Start block for event filtering.
            to_block: End block for event filtering.
            
        Returns:
            List of event dictionaries.
        """
        pass
    
    def get_chain_info(self) -> Dict:
        """
        Get general information about the blockchain.
        
        Returns:
            Dictionary containing chain information.
        """
        return {
            'name': self.name,
            'native_token': self.native_token,
            'consensus': self.consensus_mechanism,
            'chain_id': self.chain_id,
            'network': self.network,
            'explorer_url': self.explorer_url
        } 
 
 