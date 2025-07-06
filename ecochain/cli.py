#!/usr/bin/env python3

import os
import sys
import argparse
import json
import logging
from typing import Dict, Optional

from ecochain.agent_module.eco_agent import EcoAgent
from ecochain.data_module.data_collector import DataCollector
from ecochain.analysis_module.sustainability_scorer import SustainabilityScorer
from ecochain.reward_module.eco_token import EcoToken

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("ecochain-cli")

def create_default_config() -> Dict:
    """Create a default configuration for the agent."""
    return {
        "analysis_interval_seconds": 3600,  # 1 hour
        "reward_interval_seconds": 86400,   # 1 day
        "min_score_for_reward": 30,
        "web3_provider": "http://localhost:8545",
        "chain_id": 11155111,  # Sepolia testnet
        "base_reward": 100,
        "badge_tiers": {
            "Platinum": 90,
            "Gold": 75,
            "Silver": 60,
            "Bronze": 45,
            "Standard": 30
        }
    }

def save_config(config: Dict, config_path: str) -> None:
    """Save configuration to a file."""
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    logger.info(f"Configuration saved to {config_path}")

def run_agent(config_path: Optional[str], single_iteration: bool = False) -> None:
    """Run the EcoChain Guardian agent."""
    agent = EcoAgent(config_path)
    agent.run(single_iteration=single_iteration)

def collect_data(config_path: Optional[str]) -> None:
    """Collect data from mining operations."""
    collector = DataCollector(config_path)
    operations = collector.get_mining_operations()
    
    logger.info(f"Collected data for {len(operations)} mining operations:")
    for op in operations[:5]:  # Show first 5 operations
        logger.info(f"- {op['name']} ({op['id']}): {op['hashrate']} {op['hashrate_unit']}")
    
    if len(operations) > 5:
        logger.info(f"... and {len(operations) - 5} more operations")

def analyze_operations(config_path: Optional[str]) -> None:
    """Analyze mining operations and calculate sustainability scores."""
    collector = DataCollector(config_path)
    scorer = SustainabilityScorer()
    
    operations = collector.get_mining_operations()
    carbon_data_list = []
    
    for operation in operations:
        carbon_data = collector.get_carbon_data(operation["id"])
        carbon_data_list.append(carbon_data)
    
    scores = scorer.score_multiple_operations(operations, carbon_data_list)
    
    logger.info("Sustainability scores:")
    for score in scores[:5]:  # Show first 5 scores
        logger.info(
            f"- {score['operation_id']}: "
            f"Score: {score['sustainability_score']:.2f}, "
            f"Tier: {score['sustainability_tier']}"
        )
    
    if len(scores) > 5:
        logger.info(f"... and {len(scores) - 5} more scores")

def simulate_rewards(config_path: Optional[str]) -> None:
    """Simulate reward distribution to miners."""
    # Run a full agent cycle but with single iteration
    run_agent(config_path, single_iteration=True)

def setup_config(args) -> None:
    """Set up configuration file."""
    config_path = args.config
    if os.path.exists(config_path) and not args.force:
        logger.error(f"Configuration file {config_path} already exists. Use --force to overwrite.")
        return
    
    config = create_default_config()
    save_config(config, config_path)

def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="EcoChain Guardian CLI")
    parser.add_argument("--config", "-c", default="config/ecochain.json",
                        help="Path to configuration file")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Set up configuration")
    setup_parser.add_argument("--force", "-f", action="store_true",
                             help="Force overwrite existing configuration")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run the agent")
    run_parser.add_argument("--once", action="store_true",
                           help="Run a single iteration and exit")
    
    # Data collection command
    subparsers.add_parser("collect", help="Collect data from mining operations")
    
    # Analysis command
    subparsers.add_parser("analyze", help="Analyze mining operations and calculate scores")
    
    # Simulate rewards command
    subparsers.add_parser("simulate", help="Simulate reward distribution")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "setup":
        setup_config(args)
    elif args.command == "run":
        run_agent(args.config, args.once)
    elif args.command == "collect":
        collect_data(args.config)
    elif args.command == "analyze":
        analyze_operations(args.config)
    elif args.command == "simulate":
        simulate_rewards(args.config)

if __name__ == "__main__":
    main() 