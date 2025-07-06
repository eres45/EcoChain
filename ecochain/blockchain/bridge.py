"""
Cross-Chain Bridge for EcoChain Guardian

This module implements a cross-chain bridge to enable reward recognition
across different blockchain networks.
"""

import logging
import time
import json
import hashlib
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal

from ecochain.blockchain.chain_adapter import ChainAdapter

logger = logging.getLogger(__name__)

# ABI for the bridge contracts (simplified version)
BRIDGE_ABI = [
    {
        "inputs": [
            {"name": "tokenAddress", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "recipient", "type": "string"},
            {"name": "targetChain", "type": "string"}
        ],
        "name": "lockTokens",
        "outputs": [{"name": "transferId", "type": "bytes32"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "transferId", "type": "bytes32"},
            {"name": "tokenAddress", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "recipient", "type": "address"},
            {"name": "sourceChain", "type": "string"},
            {"name": "signature", "type": "bytes"}
        ],
        "name": "releaseTokens",
        "outputs": [{"name": "success", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "transferId", "type": "bytes32"}
        ],
        "name": "getTransferStatus",
        "outputs": [{"name": "status", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Status codes for transfers
TRANSFER_STATUS = {
    0: "PENDING",
    1: "COMPLETED",
    2: "FAILED",
    3: "CANCELLED"
}

class ChainBridge:
    """
    Cross-chain bridge for EcoChain Guardian.
    
    This bridge enables tokens and reward NFTs to be transferred between 
    different blockchain networks, maintaining their recognition and value.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the chain bridge.
        
        Args:
            config: Configuration dictionary for the bridge.
        """
        self.config = config
        self.adapters = {}  # Chain name -> ChainAdapter
        self.bridge_contracts = {}  # Chain name -> contract address
        self.relayers = []  # List of relayer addresses
        self.pending_transfers = {}  # Transfer ID -> transfer data
        self.completed_transfers = {}  # Transfer ID -> transfer data
        
        # Load bridge contracts
        bridge_contracts = config.get('bridge_contracts', {})
        for chain_name, contract_address in bridge_contracts.items():
            self.bridge_contracts[chain_name] = contract_address
        
        # Set relayers
        self.relayers = config.get('relayers', [])
        
        # Private key for signing transfers (in a real system, this would be securely managed)
        self.private_key = config.get('private_key')
    
    def add_chain(self, name: str, adapter: ChainAdapter, bridge_contract: str = None) -> None:
        """
        Add a blockchain adapter to the bridge.
        
        Args:
            name: Name of the chain.
            adapter: Chain adapter instance.
            bridge_contract: Address of the bridge contract on this chain.
        """
        self.adapters[name] = adapter
        
        if bridge_contract:
            self.bridge_contracts[name] = bridge_contract
            logger.info(f"Added {name} chain with bridge contract {bridge_contract}")
        else:
            logger.info(f"Added {name} chain without bridge contract")
    
    def lock_tokens(self, source_chain: str, token_address: str, amount: Union[int, float, Decimal],
                   recipient: str, target_chain: str, private_key: str = None) -> Dict:
        """
        Lock tokens on the source chain to initiate a cross-chain transfer.
        
        Args:
            source_chain: Name of the source chain.
            token_address: Address of the token contract on the source chain.
            amount: Amount of tokens to transfer.
            recipient: Recipient address on the target chain.
            target_chain: Name of the target chain.
            private_key: Private key for signing the transaction.
            
        Returns:
            Dictionary with transfer information.
        """
        # Check if chains are supported
        if source_chain not in self.adapters:
            return {"success": False, "error": f"Source chain {source_chain} not supported"}
        
        if target_chain not in self.adapters:
            return {"success": False, "error": f"Target chain {target_chain} not supported"}
        
        # Check if bridge contracts are configured
        if source_chain not in self.bridge_contracts:
            return {"success": False, "error": f"Bridge contract not configured for {source_chain}"}
        
        # Get source chain adapter and bridge contract
        adapter = self.adapters[source_chain]
        bridge_address = self.bridge_contracts[source_chain]
        
        # Connect to blockchain
        if not adapter.connect():
            return {"success": False, "error": f"Failed to connect to {source_chain}"}
        
        try:
            # For EVM chains, convert amount to wei (assuming 18 decimals)
            if hasattr(adapter, 'web3'):
                from web3 import Web3
                amount_wei = Web3.to_wei(amount, 'ether')
            else:
                # For non-EVM chains, use a simple integer representation
                # In a real implementation, handle decimals properly
                amount_wei = int(float(amount) * (10 ** 18))
            
            # Call the lockTokens function on the bridge contract
            tx_result = adapter.send_transaction(
                contract_address=bridge_address,
                abi=BRIDGE_ABI,
                function_name="lockTokens",
                args=[token_address, amount_wei, recipient, target_chain],
                private_key=private_key
            )
            
            if not tx_result.get("success", False):
                return {"success": False, "error": tx_result.get("error", "Unknown error")}
            
            # Generate a transfer ID (in a real system, this would be emitted in an event)
            transfer_id = hashlib.sha256(
                f"{source_chain}:{token_address}:{amount}:{recipient}:{target_chain}:{time.time()}".encode()
            ).hexdigest()
            
            # Store pending transfer
            self.pending_transfers[transfer_id] = {
                "source_chain": source_chain,
                "target_chain": target_chain,
                "token_address": token_address,
                "amount": str(amount),
                "recipient": recipient,
                "timestamp": time.time(),
                "status": "PENDING",
                "tx_hash": tx_result.get("tx_hash")
            }
            
            logger.info(f"Locked {amount} tokens on {source_chain} for transfer to {target_chain}")
            
            return {
                "success": True,
                "transfer_id": transfer_id,
                "source_chain": source_chain,
                "target_chain": target_chain,
                "amount": str(amount),
                "recipient": recipient,
                "tx_hash": tx_result.get("tx_hash")
            }
        except Exception as e:
            logger.error(f"Error locking tokens: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def release_tokens(self, transfer_id: str, target_chain: str) -> Dict:
        """
        Release tokens on the target chain to complete a cross-chain transfer.
        
        In a real implementation, this would be called by a relayer after 
        validating the transfer on the source chain.
        
        Args:
            transfer_id: ID of the transfer.
            target_chain: Name of the target chain.
            
        Returns:
            Dictionary with release information.
        """
        # Check if transfer exists
        if transfer_id not in self.pending_transfers:
            return {"success": False, "error": f"Transfer {transfer_id} not found"}
        
        transfer = self.pending_transfers[transfer_id]
        
        # Check if target chain matches
        if transfer["target_chain"] != target_chain:
            return {"success": False, "error": f"Transfer {transfer_id} is not for {target_chain}"}
        
        # Check if chain is supported
        if target_chain not in self.adapters:
            return {"success": False, "error": f"Target chain {target_chain} not supported"}
        
        # Check if bridge contract is configured
        if target_chain not in self.bridge_contracts:
            return {"success": False, "error": f"Bridge contract not configured for {target_chain}"}
        
        # Get target chain adapter and bridge contract
        adapter = self.adapters[target_chain]
        bridge_address = self.bridge_contracts[target_chain]
        
        # Connect to blockchain
        if not adapter.connect():
            return {"success": False, "error": f"Failed to connect to {target_chain}"}
        
        try:
            # In a real implementation, create and verify a signature
            # For this demo, use a dummy signature
            signature = "0x" + "0" * 130
            
            # For EVM chains, convert amount to wei (assuming 18 decimals)
            if hasattr(adapter, 'web3'):
                from web3 import Web3
                amount_wei = Web3.to_wei(float(transfer["amount"]), 'ether')
            else:
                # For non-EVM chains, use a simple integer representation
                amount_wei = int(float(transfer["amount"]) * (10 ** 18))
            
            # Get mapped token address on target chain
            # In a real implementation, this would come from a token mapping service
            token_address = self.config.get('token_mapping', {}).get(
                f"{transfer['source_chain']}:{transfer['token_address']}:{target_chain}",
                "0x0000000000000000000000000000000000000000"  # Dummy address
            )
            
            # Call the releaseTokens function on the bridge contract
            tx_result = adapter.send_transaction(
                contract_address=bridge_address,
                abi=BRIDGE_ABI,
                function_name="releaseTokens",
                args=[
                    transfer_id,
                    token_address,
                    amount_wei,
                    transfer["recipient"],
                    transfer["source_chain"],
                    signature
                ],
                private_key=self.private_key
            )
            
            if not tx_result.get("success", False):
                return {"success": False, "error": tx_result.get("error", "Unknown error")}
            
            # Update transfer status
            transfer["status"] = "COMPLETED"
            transfer["completed_at"] = time.time()
            transfer["release_tx_hash"] = tx_result.get("tx_hash")
            
            # Move to completed transfers
            self.completed_transfers[transfer_id] = transfer
            del self.pending_transfers[transfer_id]
            
            logger.info(f"Released tokens on {target_chain} for transfer {transfer_id}")
            
            return {
                "success": True,
                "transfer_id": transfer_id,
                "target_chain": target_chain,
                "amount": transfer["amount"],
                "recipient": transfer["recipient"],
                "tx_hash": tx_result.get("tx_hash")
            }
        except Exception as e:
            logger.error(f"Error releasing tokens: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_transfer_status(self, transfer_id: str) -> Dict:
        """
        Get the status of a cross-chain transfer.
        
        Args:
            transfer_id: ID of the transfer.
            
        Returns:
            Dictionary with transfer information.
        """
        # Check if transfer exists in pending transfers
        if transfer_id in self.pending_transfers:
            return {
                "transfer_id": transfer_id,
                "status": self.pending_transfers[transfer_id]["status"],
                "data": self.pending_transfers[transfer_id]
            }
        
        # Check if transfer exists in completed transfers
        if transfer_id in self.completed_transfers:
            return {
                "transfer_id": transfer_id,
                "status": self.completed_transfers[transfer_id]["status"],
                "data": self.completed_transfers[transfer_id]
            }
        
        return {"transfer_id": transfer_id, "status": "NOT_FOUND"}
    
    def bridge_nft(self, source_chain: str, nft_address: str, token_id: int,
                 recipient: str, target_chain: str, private_key: str = None) -> Dict:
        """
        Bridge an NFT from one chain to another.
        
        Args:
            source_chain: Name of the source chain.
            nft_address: Address of the NFT contract on the source chain.
            token_id: ID of the NFT token.
            recipient: Recipient address on the target chain.
            target_chain: Name of the target chain.
            private_key: Private key for signing the transaction.
            
        Returns:
            Dictionary with bridge information.
        """
        # This is a simplified implementation
        # In a real system, this would lock the NFT on the source chain and mint a new one on the target chain
        
        logger.info(f"Bridging NFT {token_id} from {source_chain} to {target_chain}")
        
        # Generate a transfer ID
        transfer_id = hashlib.sha256(
            f"{source_chain}:{nft_address}:{token_id}:{recipient}:{target_chain}:{time.time()}".encode()
        ).hexdigest()
        
        # Store pending transfer
        self.pending_transfers[transfer_id] = {
            "source_chain": source_chain,
            "target_chain": target_chain,
            "nft_address": nft_address,
            "token_id": token_id,
            "recipient": recipient,
            "timestamp": time.time(),
            "status": "PENDING",
            "type": "NFT"
        }
        
        return {
            "success": True,
            "transfer_id": transfer_id,
            "message": f"NFT bridging initiated. This is a simplified implementation without actual blockchain transactions."
        }
    
    def list_transfers(self, status: str = None) -> List[Dict]:
        """
        List all transfers with optional status filter.
        
        Args:
            status: Filter transfers by status.
            
        Returns:
            List of transfer dictionaries.
        """
        all_transfers = []
        
        # Add pending transfers
        for transfer_id, transfer in self.pending_transfers.items():
            if status is None or transfer["status"] == status:
                all_transfers.append({
                    "transfer_id": transfer_id,
                    **transfer
                })
        
        # Add completed transfers
        for transfer_id, transfer in self.completed_transfers.items():
            if status is None or transfer["status"] == status:
                all_transfers.append({
                    "transfer_id": transfer_id,
                    **transfer
                })
        
        return all_transfers
    
    def get_supported_chains(self) -> List[Dict]:
        """
        Get a list of supported chains with their bridge contract addresses.
        
        Returns:
            List of dictionaries with chain information.
        """
        supported_chains = []
        
        for chain_name, adapter in self.adapters.items():
            bridge_address = self.bridge_contracts.get(chain_name)
            chain_info = adapter.get_chain_info()
            
            supported_chains.append({
                "name": chain_name,
                "bridge_address": bridge_address,
                "native_token": chain_info.get("native_token"),
                "consensus": chain_info.get("consensus"),
                "has_bridge": bridge_address is not None
            })
        
        return supported_chains 
 
 