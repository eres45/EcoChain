#!/usr/bin/env python3

"""
EcoChain Guardian Demo Script

This script demonstrates the enhanced features of EcoChain Guardian:
1. Advanced ML-based sustainability scoring with anomaly detection
2. zkSNARK proofs for verified carbon reporting
3. EcoToken staking and rewards
4. Community governance
"""

import os
import sys
import logging
import time
from decimal import Decimal
from typing import Dict, List

from ecochain.data_module.data_collector import DataCollector
from ecochain.analysis_module.sustainability_scorer import SustainabilityScorer
from ecochain.analysis_module.ml_scoring import MLSustainabilityScorer
from ecochain.reward_module.eco_token import EcoToken
from ecochain.reward_module.zk_verification import ZKCarbonVerifier
from ecochain.reward_module.eco_staking import EcoStaking
from ecochain.reward_module.eco_governance import EcoGovernance, VoteType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("ecochain-demo")

def demo_ml_scoring():
    """Demonstrate ML-based sustainability scoring with anomaly detection."""
    logger.info("===== Demonstrating ML-based Sustainability Scoring =====")
    
    # Initialize components
    data_collector = DataCollector()
    ml_scorer = MLSustainabilityScorer()
    
    # Generate training data
    logger.info("Generating synthetic training data...")
    training_data = ml_scorer.generate_training_data(operations_count=1000)
    
    # Train the model
    logger.info("Training ML model...")
    training_result = ml_scorer.train(training_data)
    
    # Check training results
    if "error" in training_result:
        logger.error(f"Training failed: {training_result['error']}")
        return
    
    logger.info(f"Model trained successfully!")
    logger.info(f"Training metrics: MSE={training_result['mse']:.4f}, R²={training_result['r2']:.4f}")
    
    # Collect some mining operations
    operations = data_collector.get_mining_operations()[:5]
    logger.info(f"Scoring {len(operations)} mining operations...")
    
    # Score operations and detect anomalies
    features_list = []
    scores = []
    
    for op in operations:
        # Get carbon data
        carbon_data = data_collector.get_carbon_data(op["id"])
        
        # Extract features
        features = ml_scorer.prepare_features(op, carbon_data)
        features_list.append(features)
        
        # Score operation
        score = ml_scorer.score_operation(op, carbon_data)
        scores.append(score)
        
        logger.info(f"Operation {op['id']} - Score: {score['sustainability_score']:.2f}, "
                   f"Tier: {score['sustainability_tier']}")
    
    # Detect anomalies
    anomalies = ml_scorer.detect_anomalies(features_list)
    for i, is_anomaly in enumerate(anomalies):
        if is_anomaly:
            logger.warning(f"⚠️ Operation {operations[i]['id']} detected as anomalous!")
    
    # Save the model
    os.makedirs("data/models", exist_ok=True)
    ml_scorer.save_model("data/models/sustainability_model.pkl")
    logger.info("Model saved to data/models/sustainability_model.pkl")

def demo_zk_verification():
    """Demonstrate zkSNARK proofs for carbon reporting."""
    logger.info("===== Demonstrating zkSNARK Proofs for Carbon Reporting =====")
    
    # Initialize components
    data_collector = DataCollector()
    verifier = ZKCarbonVerifier()
    
    # Get a mining operation
    operations = data_collector.get_mining_operations()
    operation = operations[0]
    
    # Get carbon data and energy mix
    carbon_data = data_collector.get_carbon_data(operation["id"])
    energy_mix = data_collector.get_energy_mix_data(operation["location"])
    
    # Generate proving key
    proving_key = verifier.generate_proving_key()
    logger.info(f"Generated proving key: {proving_key[:10]}...")
    
    # Create carbon emissions proof
    logger.info(f"Creating carbon emissions proof for operation {operation['id']}...")
    carbon_proof = verifier.create_carbon_emissions_proof(operation, carbon_data, proving_key)
    
    # Create renewable energy proof
    logger.info(f"Creating renewable energy proof for location {operation['location']}...")
    energy_proof = verifier.create_renewable_energy_proof(operation['location'], energy_mix, proving_key)
    
    # Verify proofs
    logger.info("Verifying carbon emissions proof...")
    is_valid_carbon = verifier.verify_proof(carbon_proof)
    logger.info(f"Carbon proof verification: {'✅ Valid' if is_valid_carbon else '❌ Invalid'}")
    
    logger.info("Verifying renewable energy proof...")
    is_valid_energy = verifier.verify_proof(energy_proof)
    logger.info(f"Energy proof verification: {'✅ Valid' if is_valid_energy else '❌ Invalid'}")
    
    # Get verified proofs for operation
    proofs = verifier.get_verified_proofs_for_operation(operation["id"])
    logger.info(f"Number of verified proofs for operation {operation['id']}: {len(proofs)}")
    
    # Public information (revealed data)
    if proofs:
        logger.info("Public information from verified proof:")
        for proof in proofs:
            for key, value in proof['public_inputs'].items():
                logger.info(f"  - {key}: {value}")

def demo_staking():
    """Demonstrate EcoToken staking functionality."""
    logger.info("===== Demonstrating EcoToken Staking =====")
    
    # Initialize components
    eco_token = EcoToken()
    
    # Deploy contract
    token_address = eco_token.deploy_contracts()["token_address"]
    logger.info(f"Deployed EcoToken contract at {token_address[:10]}...")
    
    # Initialize staking
    staking = EcoStaking(eco_token)
    staking_address = staking.deploy_staking_contract()
    logger.info(f"Deployed EcoStaking contract at {staking_address[:10]}...")
    
    # Define test addresses
    addresses = [
        "0x0000000000000000000000000000000000000001",
        "0x0000000000000000000000000000000000000002",
        "0x0000000000000000000000000000000000000003"
    ]
    tiers = ["Gold", "Silver", "Bronze"]
    
    # Stake tokens
    logger.info("Staking tokens for test addresses...")
    for i, address in enumerate(addresses):
        # Get token balance (simulated)
        balance = eco_token.get_token_balance(address)
        
        # Stake half of balance
        stake_amount = Decimal(balance) / Decimal('2')
        stake_result = staking.stake(address, stake_amount, tiers[i])
        
        logger.info(f"Address {address[:10]}... staked {stake_amount} tokens with tier {tiers[i]}")
    
    # Add rewards to pool
    staking.add_rewards(Decimal('10000'))
    logger.info(f"Added 10,000 tokens to the rewards pool")
    
    # Simulate time passing (30 days)
    logger.info("Simulating time passage (30 days)...")
    
    # Check staking stats
    stats = staking.get_staking_stats()
    logger.info(f"Staking statistics:")
    logger.info(f"  - Total staked: {stats['total_staked']}")
    logger.info(f"  - Rewards pool: {stats['rewards_pool']}")
    logger.info(f"  - Active stakers: {stats['active_stakers']}")
    
    # Unstake for one address
    logger.info(f"Unstaking for address {addresses[0][:10]}...")
    active_stakes = staking.get_active_stakes(addresses[0])
    if active_stakes:
        unstake_result = staking.unstake(addresses[0], active_stakes[0]['id'])
        logger.info(f"Unstaked {unstake_result['amount']} tokens with {unstake_result['reward']} reward")

def demo_governance():
    """Demonstrate community governance functionality."""
    logger.info("===== Demonstrating Community Governance =====")
    
    # Initialize components
    eco_token = EcoToken()
    governance = EcoGovernance(eco_token)
    
    # Deploy contract
    governance_address = governance.deploy_governance_contract()
    logger.info(f"Deployed EcoGovernance contract at {governance_address[:10]}...")
    
    # Define test addresses
    proposer = "0x0000000000000000000000000000000000000001"
    voters = [
        "0x0000000000000000000000000000000000000002",
        "0x0000000000000000000000000000000000000003",
        "0x0000000000000000000000000000000000000004",
        "0x0000000000000000000000000000000000000005"
    ]
    
    # Create a proposal
    parameter_changes = {
        "scoring_weights": {
            "renewable_energy_percentage": 0.40,  # Was 0.35
            "energy_efficiency_rating": 0.25,
            "carbon_footprint": 0.15,  # Was 0.20
            "carbon_offset_percentage": 0.10,
            "sustainability_initiatives": 0.05,
            "location_factor": 0.05
        },
        "reward_parameters": {
            "base_reward": 150  # Was 100
        },
        "governance_parameters": {
            "quorum_threshold": 300  # Was 400 (lowering to 3%)
        }
    }
    
    proposal_result = governance.create_parameter_change_proposal(
        proposer=proposer,
        title="Adjust Scoring Weights and Rewards",
        description=(
            "This proposal aims to increase the weight of renewable energy in the "
            "sustainability score calculation, while also increasing the base reward "
            "for eco-friendly miners. Additionally, it lowers the quorum threshold "
            "to improve governance participation."
        ),
        parameter_changes=parameter_changes
    )
    
    if proposal_result['success']:
        proposal_id = proposal_result['proposal_id']
        logger.info(f"Created proposal {proposal_id}: {proposal_result['title']}")
        
        # Simulate state change to active
        proposal = governance.proposals[proposal_id]
        proposal['start_time'] = time.time() - 3600  # Started 1 hour ago
        
        # Cast votes
        logger.info("Casting votes...")
        governance.cast_vote(voters[0], proposal_id, VoteType.FOR)
        governance.cast_vote(voters[1], proposal_id, VoteType.FOR)
        governance.cast_vote(voters[2], proposal_id, VoteType.AGAINST)
        governance.cast_vote(voters[3], proposal_id, VoteType.ABSTAIN)
        
        # Get votes
        votes = governance.get_votes(proposal_id)
        for vote in votes:
            logger.info(f"Vote from {vote['voter'][:10]}...: {vote['vote_type']} with {vote['votes']} votes")
        
        # Get proposal details
        proposal_info = governance.get_proposal(proposal_id)
        logger.info(f"Proposal state: {proposal_info['state']}")
        logger.info(f"Votes - For: {proposal_info['for_votes']}, Against: {proposal_info['against_votes']}, Abstain: {proposal_info['abstain_votes']}")
        
        # Simulate proposal passing
        # In a real scenario, this would happen naturally over time
        proposal['for_votes'] = 600000  # 60% of supply
        proposal['against_votes'] = 200000  # 20% of supply
        proposal['end_time'] = time.time() - 3600  # Ended 1 hour ago
        
        # Execute proposal
        if governance.get_proposal_state(proposal_id).name == "SUCCEEDED":
            execute_result = governance.execute_proposal(proposal_id)
            if execute_result['success']:
                logger.info(f"✅ Proposal executed successfully!")
            else:
                logger.error(f"Failed to execute proposal: {execute_result['error']}")
        else:
            logger.info(f"Proposal is not in SUCCEEDED state, cannot execute")

def main():
    """Run all demos."""
    try:
        # Create necessary directories
        os.makedirs("data", exist_ok=True)
        
        # Run demos
        demo_ml_scoring()
        print("\n")
        demo_zk_verification()
        print("\n")
        demo_staking()
        print("\n")
        demo_governance()
        
        logger.info("✅ All demonstrations completed successfully!")
    except Exception as e:
        logger.error(f"Error in demonstration: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 

"""
EcoChain Guardian Demo Script

This script demonstrates the enhanced features of EcoChain Guardian:
1. Advanced ML-based sustainability scoring with anomaly detection
2. zkSNARK proofs for verified carbon reporting
3. EcoToken staking and rewards
4. Community governance
"""

import os
import sys
import logging
import time
from decimal import Decimal
from typing import Dict, List

from ecochain.data_module.data_collector import DataCollector
from ecochain.analysis_module.sustainability_scorer import SustainabilityScorer
from ecochain.analysis_module.ml_scoring import MLSustainabilityScorer
from ecochain.reward_module.eco_token import EcoToken
from ecochain.reward_module.zk_verification import ZKCarbonVerifier
from ecochain.reward_module.eco_staking import EcoStaking
from ecochain.reward_module.eco_governance import EcoGovernance, VoteType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("ecochain-demo")

def demo_ml_scoring():
    """Demonstrate ML-based sustainability scoring with anomaly detection."""
    logger.info("===== Demonstrating ML-based Sustainability Scoring =====")
    
    # Initialize components
    data_collector = DataCollector()
    ml_scorer = MLSustainabilityScorer()
    
    # Generate training data
    logger.info("Generating synthetic training data...")
    training_data = ml_scorer.generate_training_data(operations_count=1000)
    
    # Train the model
    logger.info("Training ML model...")
    training_result = ml_scorer.train(training_data)
    
    # Check training results
    if "error" in training_result:
        logger.error(f"Training failed: {training_result['error']}")
        return
    
    logger.info(f"Model trained successfully!")
    logger.info(f"Training metrics: MSE={training_result['mse']:.4f}, R²={training_result['r2']:.4f}")
    
    # Collect some mining operations
    operations = data_collector.get_mining_operations()[:5]
    logger.info(f"Scoring {len(operations)} mining operations...")
    
    # Score operations and detect anomalies
    features_list = []
    scores = []
    
    for op in operations:
        # Get carbon data
        carbon_data = data_collector.get_carbon_data(op["id"])
        
        # Extract features
        features = ml_scorer.prepare_features(op, carbon_data)
        features_list.append(features)
        
        # Score operation
        score = ml_scorer.score_operation(op, carbon_data)
        scores.append(score)
        
        logger.info(f"Operation {op['id']} - Score: {score['sustainability_score']:.2f}, "
                   f"Tier: {score['sustainability_tier']}")
    
    # Detect anomalies
    anomalies = ml_scorer.detect_anomalies(features_list)
    for i, is_anomaly in enumerate(anomalies):
        if is_anomaly:
            logger.warning(f"⚠️ Operation {operations[i]['id']} detected as anomalous!")
    
    # Save the model
    os.makedirs("data/models", exist_ok=True)
    ml_scorer.save_model("data/models/sustainability_model.pkl")
    logger.info("Model saved to data/models/sustainability_model.pkl")

def demo_zk_verification():
    """Demonstrate zkSNARK proofs for carbon reporting."""
    logger.info("===== Demonstrating zkSNARK Proofs for Carbon Reporting =====")
    
    # Initialize components
    data_collector = DataCollector()
    verifier = ZKCarbonVerifier()
    
    # Get a mining operation
    operations = data_collector.get_mining_operations()
    operation = operations[0]
    
    # Get carbon data and energy mix
    carbon_data = data_collector.get_carbon_data(operation["id"])
    energy_mix = data_collector.get_energy_mix_data(operation["location"])
    
    # Generate proving key
    proving_key = verifier.generate_proving_key()
    logger.info(f"Generated proving key: {proving_key[:10]}...")
    
    # Create carbon emissions proof
    logger.info(f"Creating carbon emissions proof for operation {operation['id']}...")
    carbon_proof = verifier.create_carbon_emissions_proof(operation, carbon_data, proving_key)
    
    # Create renewable energy proof
    logger.info(f"Creating renewable energy proof for location {operation['location']}...")
    energy_proof = verifier.create_renewable_energy_proof(operation['location'], energy_mix, proving_key)
    
    # Verify proofs
    logger.info("Verifying carbon emissions proof...")
    is_valid_carbon = verifier.verify_proof(carbon_proof)
    logger.info(f"Carbon proof verification: {'✅ Valid' if is_valid_carbon else '❌ Invalid'}")
    
    logger.info("Verifying renewable energy proof...")
    is_valid_energy = verifier.verify_proof(energy_proof)
    logger.info(f"Energy proof verification: {'✅ Valid' if is_valid_energy else '❌ Invalid'}")
    
    # Get verified proofs for operation
    proofs = verifier.get_verified_proofs_for_operation(operation["id"])
    logger.info(f"Number of verified proofs for operation {operation['id']}: {len(proofs)}")
    
    # Public information (revealed data)
    if proofs:
        logger.info("Public information from verified proof:")
        for proof in proofs:
            for key, value in proof['public_inputs'].items():
                logger.info(f"  - {key}: {value}")

def demo_staking():
    """Demonstrate EcoToken staking functionality."""
    logger.info("===== Demonstrating EcoToken Staking =====")
    
    # Initialize components
    eco_token = EcoToken()
    
    # Deploy contract
    token_address = eco_token.deploy_contracts()["token_address"]
    logger.info(f"Deployed EcoToken contract at {token_address[:10]}...")
    
    # Initialize staking
    staking = EcoStaking(eco_token)
    staking_address = staking.deploy_staking_contract()
    logger.info(f"Deployed EcoStaking contract at {staking_address[:10]}...")
    
    # Define test addresses
    addresses = [
        "0x0000000000000000000000000000000000000001",
        "0x0000000000000000000000000000000000000002",
        "0x0000000000000000000000000000000000000003"
    ]
    tiers = ["Gold", "Silver", "Bronze"]
    
    # Stake tokens
    logger.info("Staking tokens for test addresses...")
    for i, address in enumerate(addresses):
        # Get token balance (simulated)
        balance = eco_token.get_token_balance(address)
        
        # Stake half of balance
        stake_amount = Decimal(balance) / Decimal('2')
        stake_result = staking.stake(address, stake_amount, tiers[i])
        
        logger.info(f"Address {address[:10]}... staked {stake_amount} tokens with tier {tiers[i]}")
    
    # Add rewards to pool
    staking.add_rewards(Decimal('10000'))
    logger.info(f"Added 10,000 tokens to the rewards pool")
    
    # Simulate time passing (30 days)
    logger.info("Simulating time passage (30 days)...")
    
    # Check staking stats
    stats = staking.get_staking_stats()
    logger.info(f"Staking statistics:")
    logger.info(f"  - Total staked: {stats['total_staked']}")
    logger.info(f"  - Rewards pool: {stats['rewards_pool']}")
    logger.info(f"  - Active stakers: {stats['active_stakers']}")
    
    # Unstake for one address
    logger.info(f"Unstaking for address {addresses[0][:10]}...")
    active_stakes = staking.get_active_stakes(addresses[0])
    if active_stakes:
        unstake_result = staking.unstake(addresses[0], active_stakes[0]['id'])
        logger.info(f"Unstaked {unstake_result['amount']} tokens with {unstake_result['reward']} reward")

def demo_governance():
    """Demonstrate community governance functionality."""
    logger.info("===== Demonstrating Community Governance =====")
    
    # Initialize components
    eco_token = EcoToken()
    governance = EcoGovernance(eco_token)
    
    # Deploy contract
    governance_address = governance.deploy_governance_contract()
    logger.info(f"Deployed EcoGovernance contract at {governance_address[:10]}...")
    
    # Define test addresses
    proposer = "0x0000000000000000000000000000000000000001"
    voters = [
        "0x0000000000000000000000000000000000000002",
        "0x0000000000000000000000000000000000000003",
        "0x0000000000000000000000000000000000000004",
        "0x0000000000000000000000000000000000000005"
    ]
    
    # Create a proposal
    parameter_changes = {
        "scoring_weights": {
            "renewable_energy_percentage": 0.40,  # Was 0.35
            "energy_efficiency_rating": 0.25,
            "carbon_footprint": 0.15,  # Was 0.20
            "carbon_offset_percentage": 0.10,
            "sustainability_initiatives": 0.05,
            "location_factor": 0.05
        },
        "reward_parameters": {
            "base_reward": 150  # Was 100
        },
        "governance_parameters": {
            "quorum_threshold": 300  # Was 400 (lowering to 3%)
        }
    }
    
    proposal_result = governance.create_parameter_change_proposal(
        proposer=proposer,
        title="Adjust Scoring Weights and Rewards",
        description=(
            "This proposal aims to increase the weight of renewable energy in the "
            "sustainability score calculation, while also increasing the base reward "
            "for eco-friendly miners. Additionally, it lowers the quorum threshold "
            "to improve governance participation."
        ),
        parameter_changes=parameter_changes
    )
    
    if proposal_result['success']:
        proposal_id = proposal_result['proposal_id']
        logger.info(f"Created proposal {proposal_id}: {proposal_result['title']}")
        
        # Simulate state change to active
        proposal = governance.proposals[proposal_id]
        proposal['start_time'] = time.time() - 3600  # Started 1 hour ago
        
        # Cast votes
        logger.info("Casting votes...")
        governance.cast_vote(voters[0], proposal_id, VoteType.FOR)
        governance.cast_vote(voters[1], proposal_id, VoteType.FOR)
        governance.cast_vote(voters[2], proposal_id, VoteType.AGAINST)
        governance.cast_vote(voters[3], proposal_id, VoteType.ABSTAIN)
        
        # Get votes
        votes = governance.get_votes(proposal_id)
        for vote in votes:
            logger.info(f"Vote from {vote['voter'][:10]}...: {vote['vote_type']} with {vote['votes']} votes")
        
        # Get proposal details
        proposal_info = governance.get_proposal(proposal_id)
        logger.info(f"Proposal state: {proposal_info['state']}")
        logger.info(f"Votes - For: {proposal_info['for_votes']}, Against: {proposal_info['against_votes']}, Abstain: {proposal_info['abstain_votes']}")
        
        # Simulate proposal passing
        # In a real scenario, this would happen naturally over time
        proposal['for_votes'] = 600000  # 60% of supply
        proposal['against_votes'] = 200000  # 20% of supply
        proposal['end_time'] = time.time() - 3600  # Ended 1 hour ago
        
        # Execute proposal
        if governance.get_proposal_state(proposal_id).name == "SUCCEEDED":
            execute_result = governance.execute_proposal(proposal_id)
            if execute_result['success']:
                logger.info(f"✅ Proposal executed successfully!")
            else:
                logger.error(f"Failed to execute proposal: {execute_result['error']}")
        else:
            logger.info(f"Proposal is not in SUCCEEDED state, cannot execute")

def main():
    """Run all demos."""
    try:
        # Create necessary directories
        os.makedirs("data", exist_ok=True)
        
        # Run demos
        demo_ml_scoring()
        print("\n")
        demo_zk_verification()
        print("\n")
        demo_staking()
        print("\n")
        demo_governance()
        
        logger.info("✅ All demonstrations completed successfully!")
    except Exception as e:
        logger.error(f"Error in demonstration: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 