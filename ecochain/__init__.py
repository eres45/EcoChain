"""
EcoChain Guardian Platform

A blockchain-based platform for monitoring, analyzing, and rewarding sustainable cryptocurrency mining.
"""

__version__ = "0.2.0"
__author__ = "EcoChain Guardian Team"

# Import core modules for easy access
from ecochain.data_module.data_collector import DataCollector
from ecochain.analysis_module.sustainability_scorer import SustainabilityScorer
from ecochain.analysis_module.ml_scoring import MLSustainabilityScorer
from ecochain.analysis_module.optimization_advisor import OptimizationAdvisor
from ecochain.analysis_module.predictive_analytics import PredictiveAnalytics
from ecochain.analysis_module.compliance_reporter import ComplianceReporter
from ecochain.reward_module.eco_token import EcoToken
from ecochain.reward_module.auto_contract import AutoContractManager, DistributionSchedule
from ecochain.agent_module.eco_agent import EcoAgent

# API modules
from ecochain.api.rest import create_app as create_rest_app
from ecochain.api.graphql import create_app as create_graphql_app

# Blockchain modules
from ecochain.blockchain.ethereum import EthereumAdapter
from ecochain.blockchain.polygon import PolygonAdapter
from ecochain.blockchain.solana import SolanaAdapter
from ecochain.blockchain.bridge import ChainBridge

__all__ = [
    'DataCollector',
    'SustainabilityScorer',
    'MLSustainabilityScorer',
    'OptimizationAdvisor',
    'PredictiveAnalytics',
    'ComplianceReporter',
    'EcoToken',
    'AutoContractManager',
    'DistributionSchedule',
    'EcoAgent',
    'create_rest_app',
    'create_graphql_app',
    'EthereumAdapter',
    'PolygonAdapter',
    'SolanaAdapter',
    'ChainBridge'
] 
 
 