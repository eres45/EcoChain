"""
Ethereum Chain Adapter

This module implements an adapter for interacting with the Ethereum blockchain.
"""

import logging
import json
from typing import Dict, List, Optional, Any, Union

from web3 import Web3
# Mock middleware for compatibility
class MockPoaMiddleware:
    def __call__(self, make_request, web3):
        return make_request
        
geth_poa_middleware = MockPoaMiddleware()

from ecochain.blockchain.chain_adapter import ChainAdapter

logger = logging.getLogger(__name__)

class EthereumAdapter(ChainAdapter):
    """
    Adapter for the Ethereum blockchain.
    
    This adapter implements the ChainAdapter interface for Ethereum,
    providing methods to interact with Ethereum networks.
    """
    
    @property
    def name(self) -> str:
        """Get the name of the blockchain."""
        return "Ethereum"
    
    @property
    def native_token(self) -> str:
        """Get the native token symbol of the blockchain."""
        return "ETH"
    
    @property
    def consensus_mechanism(self) -> str:
        """Get the consensus mechanism of the blockchain."""
        if self.network in ["mainnet", "goerli"]:
            return "PoS"  # Proof of Stake after The Merge
        return "PoA"  # Most testnets use Proof of Authority
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Ethereum adapter.
        
        Args:
            config: Configuration dictionary for the adapter.
        """
        super().__init__(config)
        self.web3 = None
        self.connected = False
        
        # Set default chain ID if not provided
        if not self.chain_id:
            if self.network == "mainnet":
                self.chain_id = 1
            elif self.network == "goerli":
                self.chain_id = 5
            elif self.network == "sepolia":
                self.chain_id = 11155111
            
        # Set default provider URL if not provided
        if not self.provider_url:
            if self.network == "mainnet":
                self.provider_url = f"https://mainnet.infura.io/v3/{config.get('infura_key', '')}"
            elif self.network == "goerli":
                self.provider_url = f"https://goerli.infura.io/v3/{config.get('infura_key', '')}"
            elif self.network == "sepolia":
                self.provider_url = f"https://sepolia.infura.io/v3/{config.get('infura_key', '')}"
            
        # Set explorer URL if not provided
        if not self.explorer_url:
            if self.network == "mainnet":
                self.explorer_url = "https://etherscan.io"
            elif self.network == "goerli":
                self.explorer_url = "https://goerli.etherscan.io"
            elif self.network == "sepolia":
                self.explorer_url = "https://sepolia.etherscan.io"
    
    def connect(self) -> bool:
        """
        Connect to the Ethereum network.
        
        Returns:
            True if connected successfully, False otherwise.
        """
        try:
            # Connect to Ethereum node
            if self.provider_url.startswith('http'):
                self.web3 = Web3(Web3.HTTPProvider(self.provider_url))
            elif self.provider_url.startswith('ws'):
                self.web3 = Web3(Web3.WebsocketProvider(self.provider_url))
            else:
                self.web3 = Web3(Web3.IPCProvider(self.provider_url))
            
            # Add middleware for PoA networks (testnets)
            if self.network != "mainnet":
                try:
                    self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
                except:
                    logger.warning("Could not inject PoA middleware, continuing without it")
            
            # Check connection
            self.connected = self.web3.is_connected()
            
            if self.connected:
                logger.info(f"Connected to Ethereum {self.network} network")
            else:
                logger.error(f"Failed to connect to Ethereum {self.network} network")
            
            return self.connected
        except Exception as e:
            logger.error(f"Error connecting to Ethereum {self.network}: {str(e)}")
            return False
    
    def get_balance(self, address: str) -> float:
        """
        Get the ETH balance of an address.
        
        Args:
            address: Ethereum address to check.
            
        Returns:
            Balance of the address in ETH.
        """
        if not self.connected:
            if not self.connect():
                logger.error("Not connected to Ethereum network")
                return 0
        
        try:
            wei_balance = self.web3.eth.get_balance(address)
            eth_balance = self.web3.from_wei(wei_balance, 'ether')
            return float(eth_balance)
        except Exception as e:
            logger.error(f"Error getting balance for {address}: {str(e)}")
            return 0
    
    def deploy_contract(self, contract_name: str, contract_bytecode: str, 
                       abi: List[Dict], constructor_args: List = None) -> Dict:
        """
        Deploy a contract to the Ethereum blockchain.
        
        Args:
            contract_name: Name of the contract.
            contract_bytecode: Compiled contract bytecode.
            abi: Contract ABI.
            constructor_args: Arguments for the contract constructor.
            
        Returns:
            Dictionary containing deployment information.
        """
        if not self.connected:
            if not self.connect():
                return {"success": False, "error": "Not connected to Ethereum network"}
        
        try:
            # Get account from private key or use default
            private_key = self.config.get('private_key')
            if private_key:
                account = self.web3.eth.account.from_key(private_key)
                sender = account.address
            else:
                # Use default account (only works with unlocked node)
                sender = self.web3.eth.accounts[0]
            
            # Create contract instance
            contract = self.web3.eth.contract(abi=abi, bytecode=contract_bytecode)
            
            # Prepare constructor arguments
            if constructor_args is None:
                constructor_args = []
            
            # Estimate gas for deployment
            gas_estimate = contract.constructor(*constructor_args).estimate_gas()
            
            # Get transaction parameters
            gas_price = self.web3.eth.gas_price
            nonce = self.web3.eth.get_transaction_count(sender)
            
            # Prepare the transaction
            txn = {
                'from': sender,
                'gas': int(gas_estimate * 1.2),  # Add buffer
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': self.chain_id
            }
            
            # Build the transaction
            contract_txn = contract.constructor(*constructor_args).build_transaction(txn)
            
            # Sign the transaction if private key is provided
            if private_key:
                signed_txn = self.web3.eth.account.sign_transaction(contract_txn, private_key)
                tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            else:
                tx_hash = self.web3.eth.send_transaction(contract_txn)
            
            # Wait for receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            contract_address = receipt.contractAddress
            
            logger.info(f"Deployed contract {contract_name} to {contract_address}")
            
            return {
                "success": True,
                "contract_name": contract_name,
                "contract_address": contract_address,
                "tx_hash": tx_hash.hex(),
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "chain_id": self.chain_id,
                "network": self.network
            }
        except Exception as e:
            logger.error(f"Error deploying contract {contract_name}: {str(e)}")
            return {"success": False, "error": str(e)}
    
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
        if not self.connected:
            if not self.connect():
                logger.error("Not connected to Ethereum network")
                return None
        
        try:
            if args is None:
                args = []
            
            # Create contract instance
            contract = self.web3.eth.contract(address=contract_address, abi=abi)
            
            # Call the function
            function = getattr(contract.functions, function_name)
            result = function(*args).call()
            
            return result
        except Exception as e:
            logger.error(f"Error calling contract function {function_name}: {str(e)}")
            return None
    
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
        if not self.connected:
            if not self.connect():
                return {"success": False, "error": "Not connected to Ethereum network"}
        
        try:
            if args is None:
                args = []
            
            # Get private key from config if not provided
            if not private_key:
                private_key = self.config.get('private_key')
            
            # Get account from private key or use default
            if private_key:
                account = self.web3.eth.account.from_key(private_key)
                sender = account.address
            else:
                # Use default account (only works with unlocked node)
                sender = self.web3.eth.accounts[0]
            
            # Create contract instance
            contract = self.web3.eth.contract(address=contract_address, abi=abi)
            
            # Get the contract function
            function = getattr(contract.functions, function_name)
            
            # Estimate gas
            gas_estimate = function(*args).estimate_gas({'from': sender})
            
            # Get transaction parameters
            gas_price = self.web3.eth.gas_price
            nonce = self.web3.eth.get_transaction_count(sender)
            
            # Prepare transaction
            txn = {
                'from': sender,
                'gas': int(gas_estimate * 1.2),  # Add buffer
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': self.chain_id
            }
            
            # Build the transaction
            contract_txn = function(*args).build_transaction(txn)
            
            # Sign the transaction if private key is provided
            if private_key:
                signed_txn = self.web3.eth.account.sign_transaction(contract_txn, private_key)
                tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            else:
                tx_hash = self.web3.eth.send_transaction(contract_txn)
            
            # Wait for receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info(f"Transaction sent: {tx_hash.hex()}")
            
            return {
                "success": True,
                "tx_hash": tx_hash.hex(),
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "status": receipt.status,
                "function": function_name
            }
        except Exception as e:
            logger.error(f"Error sending transaction to {function_name}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_transaction_receipt(self, tx_hash: str) -> Dict:
        """
        Get the receipt for a transaction.
        
        Args:
            tx_hash: Transaction hash.
            
        Returns:
            Dictionary containing transaction receipt information.
        """
        if not self.connected:
            if not self.connect():
                logger.error("Not connected to Ethereum network")
                return {}
        
        try:
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            return dict(receipt)
        except Exception as e:
            logger.error(f"Error getting transaction receipt for {tx_hash}: {str(e)}")
            return {}
    
    def get_block(self, block_identifier: Union[int, str]) -> Dict:
        """
        Get information about a specific block.
        
        Args:
            block_identifier: Block number or hash.
            
        Returns:
            Dictionary containing block information.
        """
        if not self.connected:
            if not self.connect():
                logger.error("Not connected to Ethereum network")
                return {}
        
        try:
            block = self.web3.eth.get_block(block_identifier, full_transactions=True)
            return dict(block)
        except Exception as e:
            logger.error(f"Error getting block {block_identifier}: {str(e)}")
            return {}
    
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
        if not self.connected:
            if not self.connect():
                logger.error("Not connected to Ethereum network")
                return 0
        
        try:
            if args is None:
                args = []
            
            # Create contract instance
            contract = self.web3.eth.contract(address=contract_address, abi=abi)
            
            # Get the contract function
            function = getattr(contract.functions, function_name)
            
            # Estimate gas
            gas_estimate = function(*args).estimate_gas()
            
            return gas_estimate
        except Exception as e:
            logger.error(f"Error estimating gas for {function_name}: {str(e)}")
            return 0
    
    def get_token_balance(self, token_address: str, wallet_address: str) -> float:
        """
        Get the balance of an ERC-20 token for a wallet.
        
        Args:
            token_address: Address of the token contract.
            wallet_address: Address of the wallet.
            
        Returns:
            Token balance.
        """
        if not self.connected:
            if not self.connect():
                logger.error("Not connected to Ethereum network")
                return 0
        
        try:
            # ERC-20 ABI with only the balanceOf function
            erc20_abi = [
                {
                    "constant": True,
                    "inputs": [{"name": "_owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "balance", "type": "uint256"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "decimals",
                    "outputs": [{"name": "", "type": "uint8"}],
                    "type": "function"
                }
            ]
            
            # Create contract instance
            token_contract = self.web3.eth.contract(address=token_address, abi=erc20_abi)
            
            # Get token decimals
            decimals = token_contract.functions.decimals().call()
            
            # Get raw balance
            raw_balance = token_contract.functions.balanceOf(wallet_address).call()
            
            # Convert to float with proper decimal places
            balance = raw_balance / (10 ** decimals)
            
            return float(balance)
        except Exception as e:
            logger.error(f"Error getting token balance for {wallet_address}: {str(e)}")
            return 0
    
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
        if not self.connected:
            if not self.connect():
                logger.error("Not connected to Ethereum network")
                return []
        
        try:
            # Create contract instance
            contract = self.web3.eth.contract(address=contract_address, abi=abi)
            
            # Get the event object
            event = getattr(contract.events, event_name)
            
            # Create filter
            event_filter = event.create_filter(fromBlock=from_block, toBlock=to_block)
            
            # Get events
            events = event_filter.get_all_entries()
            
            # Convert events to dictionaries
            return [dict(event) for event in events]
        except Exception as e:
            logger.error(f"Error getting events for {event_name}: {str(e)}")
            return [] 
 
 