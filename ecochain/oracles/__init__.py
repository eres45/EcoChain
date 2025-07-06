"""
Oracle Network for EcoChain Guardian

This package implements a decentralized oracle network for carbon data reporting,
providing reliable and verified data from multiple sources.
"""

from ecochain.oracles.oracle_network import OracleNetwork
from ecochain.oracles.data_provider import DataProvider
from ecochain.oracles.reputation_system import ReputationSystem

__all__ = ['OracleNetwork', 'DataProvider', 'ReputationSystem'] 
 
 