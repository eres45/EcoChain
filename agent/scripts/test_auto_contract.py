#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Script for Auto Contract Functionality

This script demonstrates the AutoContractManager capabilities, including:
1. Deploying the auto reward distributor contract
2. Setting up distribution schedules
3. Updating miner sustainability scores
4. Distributing rewards (manual and automated)
"""

import os
import sys
import time
from datetime import datetime, timedelta
import logging
import asyncio
from pprint import pprint
import random

# Add the parent directory to the path so we can import ecochain
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from ecochain.reward_module.auto_contract import AutoContractManager, DistributionSchedule
from ecochain.reward_module.eco_token import EcoToken

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test configuration
CONFIG = {
    'blockchain': 'simulated',
    'contracts': {}
}

# Sample miners for testing
TEST_MINERS = [
    '0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    '0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
    '0xcccccccccccccccccccccccccccccccccccccccc',
    '0xdddddddddddddddddddddddddddddddddddddddd',
    '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
]

def deploy_ecotoken():
    """Deploy the EcoToken contract first"""
    logger.info("Deploying EcoToken contract...")
    
    # Initialize EcoToken
    eco_token = EcoToken()
    
    # Deploy contracts
    result = eco_token.deploy_contracts()
    
    logger.info(f"EcoToken deployed at {result['token_address']}")
    logger.info(f"NFT contract deployed at {result['nft_address']}")
    
    # Save addresses to config
    CONFIG['contracts']['token_address'] = result['token_address']
    CONFIG['contracts']['nft_address'] = result['nft_address']
    
    return result['token_address']

class SimulatedChainAdapter:
    """A simulated blockchain adapter for testing"""
    
    def __init__(self, config=None):
        self.connected = True
        self.contract_addresses = {}
        self.transactions = []
        self.balances = {}
    
    def connect(self):
        """Simulate connecting to a blockchain"""
        self.connected = True
        return True
    
    def deploy_contract(self, contract_name, contract_bytecode, abi, constructor_args=None):
        """Simulate contract deployment"""
        address = f"0x{os.urandom(20).hex()}"
        self.contract_addresses[contract_name] = address
        logger.info(f"Deployed simulated contract {contract_name} at {address}")
        return {
            "success": True,
            "contract_address": address,
            "transaction_hash": f"0x{os.urandom(32).hex()}"
        }
    
    def send_transaction(self, contract_address, abi, function_name, args=None, private_key=None):
        """Simulate sending a transaction"""
        tx_hash = f"0x{os.urandom(32).hex()}"
        self.transactions.append({
            "contract_address": contract_address,
            "function_name": function_name,
            "args": args,
            "tx_hash": tx_hash
        })
        logger.info(f"Simulated transaction {function_name} to {contract_address}")
        return {
            "success": True,
            "transaction_hash": tx_hash
        }
    
    def call_contract(self, contract_address, abi, function_name, args=None):
        """Simulate calling a contract function"""
        if function_name == "getEligibleMiners":
            # Return a subset of the miners as eligible
            miners = args[0] if args and len(args) > 0 else TEST_MINERS
            return [m for m in miners if random.random() > 0.3]
        return None

def test_deploy_contract():
    """Test deploying the auto reward distributor contract"""
    logger.info("Testing contract deployment...")
    
    # Make sure token contract is deployed first
    if 'token_address' not in CONFIG['contracts']:
        token_address = deploy_ecotoken()
        if not token_address:
            logger.error("Failed to deploy token contract. Cannot continue tests.")
            return None
    
    # Initialize the manager with our config
    manager = AutoContractManager()
    
    # Replace the chain adapter with our simulated one
    manager.chain_adapter = SimulatedChainAdapter()
    
    # Set the token address explicitly
    manager.token_address = CONFIG['contracts']['token_address']
    
    # Deploy the contract
    result = manager.deploy_auto_reward_contract()
    
    # Print the result
    logger.info("Deployment result:")
    pprint(result)
    
    # Return the contract address if deployment was successful
    if result.get('success', False):
        contract_address = result['contract_address']
        CONFIG['contracts']['auto_reward_address'] = contract_address
        return contract_address
    
    return None

def test_update_scores():
    """Test updating miner scores"""
    logger.info("Testing score updates...")
    
    # Initialize the manager with the config including contract address
    manager = AutoContractManager()
    
    # Replace the chain adapter with our simulated one
    manager.chain_adapter = SimulatedChainAdapter()
    
    # Set the contract address explicitly
    manager.auto_reward_address = CONFIG['contracts']['auto_reward_address']
    
    # Generate random scores between 50-95 for each miner
    scores = [random.uniform(50, 95) for _ in TEST_MINERS]
    
    # First test individual updates
    for miner, score in zip(TEST_MINERS[:2], scores[:2]):
        logger.info(f"Updating score for {miner} to {score}...")
        result = manager.update_miner_score(miner, score)
        logger.info(f"Result: {result['success']}")
    
    # Then test batch update
    logger.info(f"Batch updating scores for {len(TEST_MINERS[2:])} miners...")
    result = manager.batch_update_scores(TEST_MINERS[2:], scores[2:])
    logger.info(f"Result: {result['success']}")

def test_distribution_schedules():
    """Test creating and managing distribution schedules"""
    logger.info("Testing distribution schedules...")
    
    # Initialize the manager
    manager = AutoContractManager()
    
    # Replace the chain adapter with our simulated one
    manager.chain_adapter = SimulatedChainAdapter()
    
    # Set the contract address explicitly
    manager.auto_reward_address = CONFIG['contracts']['auto_reward_address']
    
    # Create daily schedule starting now
    daily_result = manager.set_distribution_schedule(
        frequency=DistributionSchedule.FREQUENCY_DAILY,
        eligible_miners=TEST_MINERS[:2]
    )
    logger.info(f"Daily schedule created: {daily_result['success']}")
    
    # Create weekly schedule starting tomorrow
    tomorrow = datetime.now() + timedelta(days=1)
    weekly_result = manager.set_distribution_schedule(
        frequency=DistributionSchedule.FREQUENCY_WEEKLY,
        start_time=int(tomorrow.timestamp()),
        eligible_miners=TEST_MINERS[2:]
    )
    logger.info(f"Weekly schedule created: {weekly_result['success']}")
    
    # List schedules
    schedules = manager.get_distribution_schedules()
    logger.info("Created schedules:")
    for schedule in schedules:
        logger.info(f"  ID {schedule['id']}: {schedule['frequency']}, next run at {schedule['next_run_at']}")
    
    # Remove one schedule
    if len(schedules) > 0:
        remove_result = manager.remove_distribution_schedule(0)
        logger.info(f"Removed schedule 0: {remove_result['success']}")
        
        # List remaining schedules
        remaining = manager.get_distribution_schedules()
        logger.info(f"Remaining schedules: {len(remaining)}")

def test_manual_distribution():
    """Test manual reward distribution"""
    logger.info("Testing manual reward distribution...")
    
    # Initialize the manager
    manager = AutoContractManager()
    
    # Replace the chain adapter with our simulated one
    manager.chain_adapter = SimulatedChainAdapter()
    
    # Set the contract address explicitly
    manager.auto_reward_address = CONFIG['contracts']['auto_reward_address']
    
    # Distribute to single miner
    single_result = manager.distribute_reward(TEST_MINERS[0])
    logger.info(f"Single distribution result: {single_result['success']}")
    if single_result.get('success', False):
        logger.info(f"  Distributed {single_result['reward_amount']} tokens")
    
    # Distribute to multiple miners
    batch_result = manager.batch_distribute_rewards(TEST_MINERS[1:3])
    logger.info(f"Batch distribution result: {batch_result['success']}")
    if batch_result.get('success', False):
        logger.info(f"  Distributed to {batch_result['miners_count']} miners")
        logger.info(f"  Total distributed: {batch_result['total_distributed']} tokens")
    
    # Get eligible miners and distribute
    eligible = manager.get_eligible_miners()
    if eligible:
        logger.info(f"Found {len(eligible)} eligible miners")
        batch_result = manager.batch_distribute_rewards(eligible)
        logger.info(f"Eligible distribution result: {batch_result['success']}")
    else:
        logger.info("No eligible miners found")

async def test_automated_distribution():
    """Test the automated distribution scheduler"""
    logger.info("Testing automated distribution scheduler...")
    
    # Initialize the manager
    manager = AutoContractManager()
    
    # Replace the chain adapter with our simulated one
    manager.chain_adapter = SimulatedChainAdapter()
    
    # Set the contract address explicitly
    manager.auto_reward_address = CONFIG['contracts']['auto_reward_address']
    
    # Create a quick test schedule that runs after 5 seconds
    now = int(time.time())
    test_schedule = manager.set_distribution_schedule(
        frequency=DistributionSchedule.FREQUENCY_DAILY,
        start_time=now + 5,  # Run 5 seconds from now
        eligible_miners=TEST_MINERS
    )
    
    logger.info(f"Test schedule created: {test_schedule['success']}")
    logger.info(f"Schedule will run at: {datetime.fromtimestamp(test_schedule['next_run_time']).strftime('%H:%M:%S')}")
    
    # Start the scheduler
    manager.start_scheduler()
    
    # Let it run for 10 seconds (enough to trigger the schedule)
    logger.info("Scheduler started. Waiting for 10 seconds...")
    await asyncio.sleep(10)
    
    # Stop the scheduler
    manager.stop_scheduler()
    logger.info("Scheduler stopped")

async def main():
    """Main test function"""
    logger.info("Starting Auto Contract tests")
    
    # Test contract deployment
    contract_address = test_deploy_contract()
    if not contract_address:
        logger.error("Failed to deploy contract. Cannot continue tests.")
        return
    
    logger.info(f"Contract deployed at: {contract_address}")
    
    # Update scores
    test_update_scores()
    
    # Test distribution schedules
    test_distribution_schedules()
    
    # Test manual distribution
    test_manual_distribution()
    
    # Test automated distribution
    await test_automated_distribution()
    
    logger.info("Tests completed")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 
 
 