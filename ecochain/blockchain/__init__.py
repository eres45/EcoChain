"""
EcoChain Blockchain Module

This package provides multi-chain support for the EcoChain Guardian platform,
allowing integration with various blockchain networks.
"""

from ecochain.blockchain.chain_adapter import ChainAdapter
from ecochain.blockchain.ethereum import EthereumAdapter
from ecochain.blockchain.polygon import PolygonAdapter
from ecochain.blockchain.solana import SolanaAdapter
from ecochain.blockchain.bridge import ChainBridge
from ecochain.blockchain.energy_metrics import ConsensusEnergyMetrics

__all__ = [
    'ChainAdapter',
    'EthereumAdapter', 
    'PolygonAdapter', 
    'SolanaAdapter',
    'ChainBridge',
    'ConsensusEnergyMetrics'
] 
 
 