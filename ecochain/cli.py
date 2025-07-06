#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command Line Interface for EcoChain Guardian
"""

import os
import sys
import argparse
import logging
import json
from datetime import datetime
import time
import signal

from ecochain.data_module.data_collector import DataCollector
from ecochain.analysis_module.sustainability_scorer import SustainabilityScorer
from ecochain.analysis_module.ml_scoring import MLSustainabilityScorer
from ecochain.analysis_module.optimization_advisor import OptimizationAdvisor
from ecochain.analysis_module.predictive_analytics import PredictiveAnalytics
from ecochain.analysis_module.compliance_reporter import ComplianceReporter
from ecochain.reward_module.eco_token import EcoToken
from ecochain.reward_module.auto_contract import AutoContractManager
from ecochain.reward_module.zk_verification import ZKCarbonVerifier
from ecochain.reward_module.eco_staking import EcoStaking
from ecochain.reward_module.eco_governance import EcoGovernance, VoteType, ProposalState
from ecochain.agent_module.eco_agent import EcoAgent

# Import new modules
from ecochain.api.rest import create_app as create_rest_app
from ecochain.api.graphql import create_app as create_graphql_app
from ecochain.blockchain.ethereum import EthereumAdapter
from ecochain.blockchain.polygon import PolygonAdapter
from ecochain.blockchain.solana import SolanaAdapter
from ecochain.blockchain.bridge import ChainBridge
from ecochain.blockchain.energy_metrics import ConsensusEnergyMetrics
from ecochain.oracles.oracle_network import OracleNetwork
from ecochain.oracles.data_provider import CarbonEmissionsProvider, RenewableCertificateProvider
from ecochain.oracles.reputation_system import ReputationSystem

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('ecochain')

# Constants
CONFIG_DIR = os.path.expanduser('~/.ecochain')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
MODELS_DIR = os.path.join(CONFIG_DIR, 'models')

def load_config():
    """Load configuration from file"""
    if not os.path.exists(CONFIG_FILE):
        return {}
    
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config):
    """Save configuration to file"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def setup_environment():
    """Setup the environment for EcoChain Guardian"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    # Create default config if it doesn't exist
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            'version': '0.2.0',
            'data_source': 'simulated',
            'reward_type': 'simulated',
            'blockchain_network': 'simulated',
            'ml_model_path': os.path.join(MODELS_DIR, 'sustainability_model.pkl'),
            'use_ml_model': True,
            'contracts': {
                'token_address': '',
                'staking_address': '',
                'governance_address': ''
            },
            'verification': {
                'enabled': True
            },
            'governance': {
                'proposal_threshold': 10000,
                'voting_delay': 1,
                'voting_period': 10080,
                'quorum_threshold': 400
            }
        }
        
        save_config(default_config)
        logger.info(f"Created default configuration at {CONFIG_FILE}")
    
    return load_config()

def collect_command(args):
    """Collect data from mining operations"""
    data_collector = DataCollector()
    
    if args.location:
        # Get operations in a specific location
        operations = data_collector.get_mining_operations_by_location(args.location)
        print(f"Found {len(operations)} operations in {args.location}:")
    elif args.id:
        # Get a specific operation
        operation = data_collector.get_mining_operation(args.id)
        if operation:
            operations = [operation]
            print(f"Found operation: {operation['name']} (ID: {operation['id']})")
        else:
            print(f"Operation with ID {args.id} not found")
            return
    else:
        # Get all operations
        operations = data_collector.get_mining_operations()
        print(f"Found {len(operations)} mining operations:")
    
    # Display operations
    for op in operations[:args.limit if args.limit else None]:
        print(f"  - {op['id']}: {op['name']} in {op['location']}")
        
        # Get carbon data if requested
        if args.carbon:
            carbon_data = data_collector.get_carbon_data(op['id'])
            print(f"    Carbon footprint: {carbon_data['carbon_footprint_tons_per_day']} tons/day")
            print(f"    Renewable energy: {carbon_data['renewable_energy_percentage']}%")
            
        # Get energy mix if requested
        if args.energy:
            energy_data = data_collector.get_energy_mix_data(op['location'])
            print(f"    Energy mix for {op['location']}:")
            print(f"      Renewable: {energy_data['renewable_percentage']}%")
            print(f"      Fossil: {energy_data['fossil_percentage']}%")
            
            if 'renewable_breakdown' in energy_data:
                rb = energy_data['renewable_breakdown']
                print(f"      Renewable breakdown: Hydro {rb.get('hydro', 0)}%, Solar {rb.get('solar', 0)}%, Wind {rb.get('wind', 0)}%, Geothermal {rb.get('geothermal', 0)}%")

def analyze_command(args):
    """Analyze mining operations using sustainability scoring"""
    config = load_config()
    data_collector = DataCollector()
    
    # Determine which scorer to use
    if args.ml or config.get('use_ml_model', False):
        # Use ML-based scoring
        model_path = args.model or config.get('ml_model_path')
        
        if model_path and os.path.exists(model_path):
            print(f"Using ML-based sustainability scorer with model: {model_path}")
            scorer = MLSustainabilityScorer(model_path)
        else:
            print("ML model not found, training a new model...")
            scorer = MLSustainabilityScorer()
            
            # Generate synthetic data and train
            training_data = scorer.generate_training_data(operations_count=1000)
            training_result = scorer.train(training_data)
            
            if "error" in training_result:
                print(f"Error training model: {training_result['error']}")
                print("Falling back to rule-based scoring")
                scorer = SustainabilityScorer()
            else:
                print(f"Model trained successfully! MSE={training_result['mse']:.4f}, R²={training_result['r2']:.4f}")
                
                # Save the model
                os.makedirs(MODELS_DIR, exist_ok=True)
                model_path = os.path.join(MODELS_DIR, 'sustainability_model.pkl')
                scorer.save_model(model_path)
                print(f"Model saved to {model_path}")
                
                # Update config
                config['ml_model_path'] = model_path
                config['use_ml_model'] = True
                save_config(config)
    else:
        # Use rule-based scoring
        print("Using rule-based sustainability scorer")
        scorer = SustainabilityScorer()
    
    # Get operations to analyze
    if args.id:
        # Find the operation with the matching ID
        all_operations = data_collector.get_mining_operations()
        operations = [op for op in all_operations if op["id"] == args.id]
        if not operations:
            print(f"Operation with ID {args.id} not found")
            return
        operation = operations[0]
    else:
        operations = data_collector.get_mining_operations()[:args.limit if args.limit else None]
    
    print(f"Analyzing {len(operations)} mining operations...")
    
    # Score each operation
    results = []
    features_list = []
    
    for op in operations:
        carbon_data = data_collector.get_carbon_data(op["id"])
        
        # For ML-based scorer, collect features for anomaly detection
        if isinstance(scorer, MLSustainabilityScorer):
            features = scorer.prepare_features(op, carbon_data)
            features_list.append(features)
        
        # Score operation
        score_result = scorer.score_operation(op, carbon_data)
        results.append((op, score_result))
        
        # Display results
        print(f"{op['id']}: {op['name']} (Location: {op['location']})")
        print(f"  Score: {score_result['sustainability_score']:.2f}")
        print(f"  Tier: {score_result['sustainability_tier']}")
        
        if 'component_scores' in score_result:
            print("  Component Scores:")
            for name, value in score_result['component_scores'].items():
                print(f"    {name}: {value:.2f}")
        
        if 'improvement_suggestions' in score_result and score_result['improvement_suggestions']:
            print("  Improvement Suggestions:")
            for suggestion in score_result['improvement_suggestions']:
                print(f"    - {suggestion}")
    
    # Detect anomalies if using ML-based scoring
    if isinstance(scorer, MLSustainabilityScorer) and features_list:
        print("\nPerforming anomaly detection...")
        anomalies = scorer.detect_anomalies(features_list)
        anomaly_count = sum(1 for a in anomalies if a)
        
        if anomaly_count > 0:
            print(f"⚠️  Detected {anomaly_count} potential anomalies:")
            for i, is_anomaly in enumerate(anomalies):
                if is_anomaly:
                    op = operations[i]
                    print(f"  - {op['id']}: {op['name']} - Unusual data patterns detected")
        else:
            print("No anomalies detected.")

def verify_command(args):
    """Create and verify zkSNARK proofs for carbon reporting"""
    config = load_config()
    
    if not config.get('verification', {}).get('enabled', True):
        print("Verification is disabled in the config.")
        return
    
    data_collector = DataCollector()
    verifier = ZKCarbonVerifier()
    
    # Get the operation
    if args.id:
        # Find the operation with the matching ID
        all_operations = data_collector.get_mining_operations()
        matching_operations = [op for op in all_operations if op["id"] == args.id]
        if not matching_operations:
            print(f"Operation with ID {args.id} not found")
            return
        operation = matching_operations[0]
    else:
        operations = data_collector.get_mining_operations()
        if not operations:
            print("No operations found")
            return
        operation = operations[0]
    
    print(f"Creating verification for operation: {operation['name']} (ID: {operation['id']})")
    
    # Get carbon data
    carbon_data = data_collector.get_carbon_data(operation["id"])
    
    # Create proof
    proving_key = verifier.generate_proving_key()
    print(f"Generated proving key: {proving_key[:10]}...")
    
    carbon_proof = verifier.create_carbon_emissions_proof(operation, carbon_data, proving_key)
    print("Created carbon emissions proof")
    
    # Verify proof
    is_valid = verifier.verify_proof(carbon_proof)
    print(f"Proof verification: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    if is_valid:
        print("Public inputs (verifiable data):")
        for key, value in carbon_proof['public_inputs'].items():
            print(f"  - {key}: {value}")

def reward_command(args):
    """Manage rewards for sustainable mining operations"""
    config = load_config()
    eco_token = EcoToken()
    
    if args.action == 'deploy':
        # Deploy contracts
        print("Deploying ERC-20 token and NFT contracts...")
        deploy_result = eco_token.deploy_contracts()
        
        print(f"ERC-20 token deployed at {deploy_result['token_address']}")
        print(f"NFT contract deployed at {deploy_result['nft_address']}")
        
        # Save contract addresses to config
        if 'contracts' not in config:
            config['contracts'] = {}
        config['contracts']['token_address'] = deploy_result['token_address']
        config['contracts']['nft_address'] = deploy_result['nft_address']
        save_config(config)
    
    elif args.action == 'distribute':
        # Distribute rewards
        data_collector = DataCollector()
        scorer = MLSustainabilityScorer(config.get('ml_model_path')) if config.get('use_ml_model', False) else SustainabilityScorer()
        
        # Get operations
        operations = data_collector.get_mining_operations()
        
        print(f"Calculating rewards for {len(operations)} operations...")
        
        # Calculate rewards for each operation
        reward_results = []
        for op in operations:
            carbon_data = data_collector.get_carbon_data(op["id"])
            score_result = scorer.score_operation(op, carbon_data)
            
            # Calculate reward
            reward = eco_token.calculate_reward(op, score_result)
            
            # Issue token reward
            token_result = eco_token.reward_tokens(op["wallet_address"], reward["token_amount"])
            
            # Issue NFT badge if qualified
            nft_result = None
            if reward["nft_tier"]:
                nft_result = eco_token.mint_nft_badge(op["wallet_address"], reward["nft_tier"], score_result["sustainability_score"])
            
            reward_results.append({
                "operation_id": op["id"],
                "operation_name": op["name"],
                "wallet_address": op["wallet_address"],
                "score": score_result["sustainability_score"],
                "tier": score_result["sustainability_tier"],
                "token_amount": reward["token_amount"],
                "nft_tier": reward["nft_tier"],
                "token_tx": token_result["tx_hash"] if token_result else None,
                "nft_tx": nft_result["tx_hash"] if nft_result else None
            })
        
        # Display results
        print("\nReward distribution summary:")
        for result in reward_results:
            print(f"{result['operation_id']}: {result['operation_name']}")
            print(f"  Score: {result['score']:.2f}, Tier: {result['tier']}")
            print(f"  Tokens: {result['token_amount']}")
            if result['nft_tier']:
                print(f"  NFT Badge: {result['nft_tier']}")
    
    elif args.action == 'balance':
        # Check token balance for address
        address = args.address
        if not address:
            print("Please provide an address with --address")
            return
        
        balance = eco_token.get_token_balance(address)
        nft_badges = eco_token.get_nft_badges(address)
        
        print(f"Address: {address}")
        print(f"Token Balance: {balance} ECO")
        
        if nft_badges:
            print("NFT Badges:")
            for badge in nft_badges:
                print(f"  - {badge['tier']} (Score: {badge['score']:.2f})")
        else:
            print("No NFT badges found")

def stake_command(args):
    """Manage staking of EcoTokens"""
    config = load_config()
    eco_token = EcoToken()
    staking = EcoStaking(eco_token)
    
    if args.action == 'deploy':
        # Deploy staking contract
        print("Deploying EcoStaking contract...")
        staking_address = staking.deploy_staking_contract()
        
        print(f"Staking contract deployed at {staking_address}")
        
        # Save contract address to config
        if 'contracts' not in config:
            config['contracts'] = {}
        config['contracts']['staking_address'] = staking_address
        save_config(config)
    
    elif args.action == 'stake':
        # Stake tokens
        address = args.address
        amount = float(args.amount)
        tier = args.tier
        
        if not address:
            print("Please provide an address with --address")
            return
        
        if not amount:
            print("Please provide an amount with --amount")
            return
        
        if not tier:
            print("Please provide a tier with --tier")
            return
        
        # Check balance
        balance = eco_token.get_token_balance(address)
        if balance < amount:
            print(f"Insufficient balance: {balance} < {amount}")
            return
        
        # Stake tokens
        stake_result = staking.stake(address, amount, tier)
        
        if stake_result['success']:
            print(f"Successfully staked {amount} tokens for {address}")
            print(f"Stake ID: {stake_result['stake_id']}")
        else:
            print(f"Error staking tokens: {stake_result.get('error', 'Unknown error')}")
    
    elif args.action == 'unstake':
        # Unstake tokens
        address = args.address
        stake_id = args.stake_id
        
        if not address:
            print("Please provide an address with --address")
            return
        
        if stake_id is None:
            print("Please provide a stake ID with --stake-id")
            return
        
        # Unstake tokens
        unstake_result = staking.unstake(address, stake_id)
        
        if unstake_result['success']:
            print(f"Successfully unstaked {unstake_result['amount']} tokens")
            print(f"Reward: {unstake_result['reward']} tokens")
            print(f"Total returned: {unstake_result['total_returned']} tokens")
        else:
            print(f"Error unstaking tokens: {unstake_result.get('error', 'Unknown error')}")
    
    elif args.action == 'stats':
        # Get staking statistics
        stats = staking.get_staking_stats()
        
        print("EcoToken Staking Statistics:")
        print(f"Total staked: {stats['total_staked']} tokens")
        print(f"Rewards pool: {stats['rewards_pool']} tokens")
        print(f"Active stakers: {stats['active_stakers']}")
        print(f"Base APY: {stats['base_apy'] / 100}%")
        print(f"Minimum staking period: {stats['min_staking_period_days']:.1f} days")
        
        print("\nTier multipliers:")
        for tier, multiplier in stats['tier_multipliers'].items():
            multiplier_decimal = multiplier / 10000
            print(f"  {tier}: {multiplier_decimal}x")
    
    elif args.action == 'list':
        # List active stakes for an address
        address = args.address
        
        if not address:
            print("Please provide an address with --address")
            return
        
        # Get active stakes
        active_stakes = staking.get_active_stakes(address)
        
        if not active_stakes:
            print(f"No active stakes found for {address}")
            return
        
        print(f"Active stakes for {address}:")
        for stake in active_stakes:
            days = stake['duration'] / (24 * 60 * 60)
            print(f"Stake ID: {stake['id']}")
            print(f"  Amount: {stake['amount']} tokens")
            print(f"  Tier: {stake['tier']}")
            print(f"  Duration: {days:.2f} days")
            print(f"  Estimated reward: {stake['estimated_reward']} tokens")

def governance_command(args):
    """Manage community governance"""
    config = load_config()
    eco_token = EcoToken()
    governance = EcoGovernance(eco_token)
    
    if args.action == 'deploy':
        # Deploy governance contract
        print("Deploying EcoGovernance contract...")
        governance_address = governance.deploy_governance_contract()
        
        print(f"Governance contract deployed at {governance_address}")
        
        # Save contract address to config
        if 'contracts' not in config:
            config['contracts'] = {}
        config['contracts']['governance_address'] = governance_address
        save_config(config)
    
    elif args.action == 'propose':
        # Create a new proposal
        proposer = args.address
        
        if not proposer:
            print("Please provide a proposer address with --address")
            return
        
        if not args.title:
            print("Please provide a proposal title with --title")
            return
        
        if not args.description:
            print("Please provide a proposal description with --description")
            return
        
        # Parse parameter changes if provided
        parameter_changes = {}
        if args.params:
            try:
                parameter_changes = json.loads(args.params)
            except json.JSONDecodeError:
                print("Error parsing parameter changes. Please provide valid JSON.")
                return
        
        # Create proposal
        proposal_result = governance.create_parameter_change_proposal(
            proposer=proposer,
            title=args.title,
            description=args.description,
            parameter_changes=parameter_changes
        )
        
        if proposal_result['success']:
            print(f"Successfully created proposal {proposal_result['proposal_id']}: {proposal_result['title']}")
            print(f"Voting starts: {datetime.fromtimestamp(proposal_result['start_time'])}")
            print(f"Voting ends: {datetime.fromtimestamp(proposal_result['end_time'])}")
        else:
            print(f"Error creating proposal: {proposal_result.get('error', 'Unknown error')}")
    
    elif args.action == 'vote':
        # Vote on a proposal
        voter = args.address
        proposal_id = args.proposal_id
        vote = args.vote
        
        if not voter:
            print("Please provide a voter address with --address")
            return
        
        if proposal_id is None:
            print("Please provide a proposal ID with --proposal-id")
            return
        
        if not vote:
            print("Please provide a vote type with --vote (for, against, or abstain)")
            return
        
        # Convert vote string to enum
        vote_type = None
        if vote.lower() == 'for':
            vote_type = VoteType.FOR
        elif vote.lower() == 'against':
            vote_type = VoteType.AGAINST
        elif vote.lower() == 'abstain':
            vote_type = VoteType.ABSTAIN
        else:
            print("Invalid vote type. Please use 'for', 'against', or 'abstain'.")
            return
        
        # Cast vote
        vote_result = governance.cast_vote(voter, proposal_id, vote_type)
        
        if vote_result['success']:
            print(f"Successfully cast vote '{vote_result['vote_type']}' on proposal {proposal_id}")
            print(f"Voter: {voter}")
            print(f"Voting power: {vote_result['votes']} tokens")
        else:
            print(f"Error casting vote: {vote_result.get('error', 'Unknown error')}")
    
    elif args.action == 'list':
        # List proposals
        proposals = governance.get_all_proposals()
        
        if not proposals:
            print("No proposals found.")
            return
        
        print(f"Found {len(proposals)} proposals:")
        
        for p in proposals:
            print(f"ID: {p['id']} - {p['title']}")
            print(f"  Proposer: {p['proposer']}")
            print(f"  State: {p['state']}")
            print(f"  Votes: For={p['for_votes']}, Against={p['against_votes']}")
            print(f"  End time: {datetime.fromtimestamp(p['end_time'])}")
    
    elif args.action == 'show':
        # Show details of a specific proposal
        proposal_id = args.proposal_id
        
        if proposal_id is None:
            print("Please provide a proposal ID with --proposal-id")
            return
        
        try:
            proposal = governance.get_proposal(proposal_id)
        except ValueError as e:
            print(f"Error: {str(e)}")
            return
        
        print(f"Proposal {proposal['id']}: {proposal['title']}")
        print(f"Proposer: {proposal['proposer']}")
        print(f"State: {proposal['state']}")
        print(f"Created: {datetime.fromtimestamp(proposal['creation_time'])}")
        print(f"Voting period: {datetime.fromtimestamp(proposal['start_time'])} to {datetime.fromtimestamp(proposal['end_time'])}")
        print(f"Votes: For={proposal['for_votes']}, Against={proposal['against_votes']}, Abstain={proposal['abstain_votes']}")
        
        print("\nDescription:")
        print(proposal['description'])
        
        # Show votes
        votes = governance.get_votes(proposal_id)
        if votes:
            print(f"\nVotes cast ({len(votes)}):")
            for vote in votes:
                print(f"  {vote['voter']}: {vote['vote_type']} with {vote['votes']} tokens")
    
    elif args.action == 'execute':
        # Execute a proposal
        proposal_id = args.proposal_id
        
        if proposal_id is None:
            print("Please provide a proposal ID with --proposal-id")
            return
        
        # Get proposal state
        try:
            state = governance.get_proposal_state(proposal_id)
        except ValueError as e:
            print(f"Error: {str(e)}")
            return
        
        if state != ProposalState.SUCCEEDED:
            print(f"Cannot execute proposal in state '{state.name}'")
            return
        
        # Execute proposal
        execute_result = governance.execute_proposal(proposal_id)
        
        if execute_result['success']:
            print(f"Successfully executed proposal {proposal_id}: {execute_result['title']}")
        else:
            print(f"Error executing proposal: {execute_result.get('error', 'Unknown error')}")

def demo_command(args):
    """Run a demonstration of EcoChain Guardian features"""
    from ecochain.demo import main as run_demo
    
    print("Running EcoChain Guardian demonstration...")
    run_demo()

def train_command(args):
    """Train the ML model for sustainability scoring"""
    config = load_config()
    
    # Create scorer
    ml_scorer = MLSustainabilityScorer()
    
    # Generate training data
    operations_count = args.samples or 1000
    print(f"Generating {operations_count} synthetic training samples...")
    training_data = ml_scorer.generate_training_data(operations_count=operations_count)
    
    # Train the model
    print("Training ML model...")
    training_result = ml_scorer.train(training_data)
    
    if "error" in training_result:
        print(f"Error training model: {training_result['error']}")
        return
    
    print(f"Model trained successfully!")
    print(f"Training metrics:")
    print(f"  - MSE: {training_result['mse']:.4f}")
    print(f"  - R²: {training_result['r2']:.4f}")
    print(f"  - Samples: {training_result['samples_count']}")
    
    # Save the model
    os.makedirs(MODELS_DIR, exist_ok=True)
    model_path = args.output or os.path.join(MODELS_DIR, 'sustainability_model.pkl')
    ml_scorer.save_model(model_path)
    print(f"Model saved to {model_path}")
    
    # Update config
    config['ml_model_path'] = model_path
    config['use_ml_model'] = True
    save_config(config)
    print("Configuration updated to use the new model")

def api_command(args):
    """Start the API gateway"""
    print(f"Starting {args.mode.upper()} API gateway...")
    
    # Ensure we can catch signals for clean shutdown
    def signal_handler(sig, frame):
        print('Shutting down API gateway...')
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create the appropriate app
    if args.mode == 'rest':
        app = create_rest_app()
        app_type = "REST API"
        port = args.port or 5000
    elif args.mode == 'graphql':
        app = create_graphql_app()
        app_type = "GraphQL API"
        port = args.port or 5001
    else:
        print(f"Unknown API mode: {args.mode}")
        return
    
    # Set up host
    host = '0.0.0.0' if args.public else '127.0.0.1'
    
    print(f"{app_type} gateway listening on {host}:{port}")
    print("Press Ctrl+C to stop")
    
    # Start the server
    if args.debug:
        app.run(host=host, port=port, debug=True)
    else:
        app.run(host=host, port=port)

def multichain_command(args):
    """Multi-chain operations"""
    if args.action == "list":
        _multichain_list(args)
    elif args.action == "compare":
        _multichain_compare_energy(args)
    elif args.action == "bridge":
        _multichain_bridge(args)
    else:
        print(f"Unknown action: {args.action}")

def _multichain_list(args):
    """List supported blockchains"""
    # Create chain adapters
    eth = EthereumAdapter({
        'network': 'mainnet' if not args.testnet else 'goerli',
        'provider_url': args.provider_url if hasattr(args, 'provider_url') else None
    })
    
    polygon = PolygonAdapter({
        'network': 'mainnet' if not args.testnet else 'mumbai',
        'provider_url': args.provider_url if hasattr(args, 'provider_url') else None
    })
    
    solana = SolanaAdapter({
        'network': 'mainnet' if not args.testnet else 'devnet',
        'provider_url': args.provider_url if hasattr(args, 'provider_url') else None
    })
    
    # Connect to networks
    chains = {
        'Ethereum': eth,
        'Polygon': polygon,
        'Solana': solana
    }
    
    # Display chain information
    print("Supported blockchains:")
    for name, adapter in chains.items():
        print(f"\n== {name} ==")
        
        if args.connect:
            print(f"Connecting to {name} network...")
            connected = adapter.connect()
            print(f"Connection status: {'Success' if connected else 'Failed'}")
        
        print(f"Network: {adapter.network}")
        print(f"Consensus: {adapter.consensus_mechanism}")
        print(f"Native token: {adapter.native_token}")
        
        if hasattr(adapter, 'chain_id') and adapter.chain_id:
            print(f"Chain ID: {adapter.chain_id}")

def _multichain_compare_energy(args):
    """Compare energy consumption across blockchains"""
    # Create energy metrics analyzer
    metrics = ConsensusEnergyMetrics()
    
    # Create chain adapters
    eth = EthereumAdapter({
        'network': 'mainnet',
        'provider_url': args.provider_url if hasattr(args, 'provider_url') else None
    })
    
    polygon = PolygonAdapter({
        'network': 'mainnet',
        'provider_url': args.provider_url if hasattr(args, 'provider_url') else None
    })
    
    solana = SolanaAdapter({
        'network': 'mainnet',
        'provider_url': args.provider_url if hasattr(args, 'provider_url') else None
    })
    
    # Add chains to metrics analyzer
    metrics.add_chain('Ethereum', eth)
    metrics.add_chain('Polygon', polygon)
    metrics.add_chain('Solana', solana)
    
    # Update with sample transaction volumes (these would be real data in production)
    metrics.update_chain_metrics('Ethereum', tx_count=1000000, active_validators=300000)  # ~1M tx/day
    metrics.update_chain_metrics('Polygon', tx_count=3000000, active_validators=100)  # ~3M tx/day
    metrics.update_chain_metrics('Solana', tx_count=20000000, active_validators=1000)  # ~20M tx/day
    
    # Compare chains
    comparison = metrics.compare_chains()
    
    # Display results
    print("Energy Consumption Comparison Across Blockchains:")
    print("\nEnergy Per Transaction (kWh):")
    for chain, value in comparison['energy_per_tx'].items():
        print(f"  {chain}: {value:.6f} kWh")
    
    print("\nDaily Energy Usage (kWh):")
    for chain, value in comparison['total_daily_energy'].items():
        print(f"  {chain}: {value:.2f} kWh")
    
    print("\nRelative Efficiency (% compared to most efficient):")
    for chain, value in comparison['relative_efficiency'].items():
        print(f"  {chain}: {value:.2f}%")
    
    print("\nSummary:")
    summary = comparison['summary']
    print(f"  Most efficient chain: {summary['most_efficient_chain']}")
    print(f"  Least efficient chain: {summary['least_efficient_chain']}")
    print(f"  Efficiency factor: {summary['efficiency_factor']:.2f}x")
    print(f"  Best consensus mechanism: {summary['best_consensus']}")
    
    # Generate impact report for most efficient chain
    if args.detailed:
        print("\nDetailed Impact Report for Most Efficient Chain:")
        report = metrics.create_impact_report(summary['most_efficient_chain'])
        
        print("\nEnergy Equivalents:")
        eq = report['energy_equivalents']
        print(f"  Households powered daily: {eq['households_powered_daily']:.2f}")
        print(f"  EV charges daily: {eq['ev_charges_daily']:.2f}")
        
        print("\nCarbon Impact:")
        carbon = report['carbon_impact']
        print(f"  Daily carbon (kg CO2): {carbon['daily_carbon_kg']:.2f}")
        print(f"  Annual carbon (tons CO2): {carbon['annual_carbon_tons']:.2f}")
        print(f"  Trees required for offset: {carbon['trees_for_offset']:.0f}")
        
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  - {rec}")

def _multichain_bridge(args):
    """Simulate bridge operations between chains"""
    # Create chain adapters
    eth = EthereumAdapter({
        'network': 'goerli' if args.testnet else 'mainnet',
        'provider_url': args.provider_url if hasattr(args, 'provider_url') else None
    })
    
    polygon = PolygonAdapter({
        'network': 'mumbai' if args.testnet else 'mainnet',
        'provider_url': args.provider_url if hasattr(args, 'provider_url') else None
    })
    
    # Create bridge
    bridge = ChainBridge({
        'bridge_contracts': {
            'Ethereum': '0x1234567890abcdef1234567890abcdef12345678',  # Example addresses
            'Polygon': '0xabcdef1234567890abcdef1234567890abcdef12'
        }
    })
    
    # Add chains to bridge
    bridge.add_chain('Ethereum', eth)
    bridge.add_chain('Polygon', polygon)
    
    # Get information about supported chains
    chains = bridge.get_supported_chains()
    
    print("Cross-Chain Bridge Information:")
    for chain in chains:
        print(f"  {chain['name']}:")
        print(f"    Native token: {chain['native_token']}")
        print(f"    Consensus: {chain['consensus']}")
        print(f"    Bridge contract: {chain['bridge_address']}")
    
    # Simulate bridging EcoTokens (in a real implementation, this would connect to actual contracts)
    if args.source and args.target and args.amount:
        print(f"\nSimulating bridge transfer of {args.amount} tokens from {args.source} to {args.target}...")
        
        # Lock tokens on source chain
        lock_result = bridge.lock_tokens(
            source_chain=args.source,
            token_address='0x1234567890abcdef1234567890abcdef12345678',  # Example EcoToken address
            amount=float(args.amount),
            recipient='0xabcdef1234567890abcdef1234567890abcdef12',  # Example recipient address
            target_chain=args.target
        )
        
        if lock_result.get('success', False):
            print(f"Successfully initiated transfer with ID: {lock_result['transfer_id']}")
            
            # In a real implementation, there would be a delay here while the transaction is confirmed
            print("Waiting for confirmation (simulated)...")
            time.sleep(2)
            
            # Release tokens on target chain
            release_result = bridge.release_tokens(
                transfer_id=lock_result['transfer_id'],
                target_chain=args.target
            )
            
            if release_result.get('success', False):
                print(f"Successfully completed transfer to {args.target}!")
            else:
                print(f"Failed to release tokens: {release_result.get('error', 'Unknown error')}")
        else:
            print(f"Failed to lock tokens: {lock_result.get('error', 'Unknown error')}")

def oracle_command(args):
    """Oracle network operations"""
    if args.action == "start":
        _oracle_start_network(args)
    elif args.action == "register":
        _oracle_register_provider(args)
    elif args.action == "request":
        _oracle_request_data(args)
    elif args.action == "status":
        _oracle_network_status(args)
    else:
        print(f"Unknown action: {args.action}")

def _oracle_start_network(args):
    """Start the oracle network"""
    print("Starting Oracle Network...")
    
    # Configure the network
    network_config = {
        'default_aggregation': 'weighted_mean',
        'base_reward': 1.0,
        'accuracy_bonus': 0.5,
        'consensus_threshold': 0.7
    }
    
    # Create the network
    network = OracleNetwork(network_config)
    
    # Set up reputation system
    reputation_config = {
        'min_score': 0.0,
        'max_score': 100.0,
        'default_score': 50.0,
        'data_file': os.path.join(CONFIG_DIR, 'reputation.json')
    }
    network.reputation_system = ReputationSystem(reputation_config)
    
    # Register some providers (in a real implementation, these would be external entities)
    print("Registering sample data providers...")
    
    # Carbon emissions provider
    carbon_provider = CarbonEmissionsProvider(
        name="CarbonData Inc.",
        supported_data_types=["carbon_intensity", "energy_mix", "emissions_factor"],
        config={
            'provider_id': 'carbon-data-1',
            'base_urls': {
                'carbon_intensity': 'https://api.carbonintensity.org.uk'
            },
            'api_keys': {}
        }
    )
    carbon_provider.set_submit_callback(network.submit_response)
    network.register_provider(carbon_provider)
    
    # Renewable certificate provider
    renewable_provider = RenewableCertificateProvider(
        name="GreenCert Authority",
        supported_data_types=["certificate_verification", "certificate_pricing"],
        config={
            'provider_id': 'green-cert-1'
        }
    )
    renewable_provider.set_submit_callback(network.submit_response)
    network.register_provider(renewable_provider)
    
    # Display providers
    providers = network.list_providers()
    print(f"Registered {len(providers)} providers:")
    for p in providers:
        print(f"  - {p['name']} (ID: {p['provider_id']})")
        print(f"    Data types: {', '.join(p['data_types'])}")
        print(f"    Reputation: {p['reputation']:.1f}")
    
    print("\nOracle Network is ready!")
    print("Use the following commands to interact with it:")
    print("  - Request data: ecochain oracle request --type carbon_intensity --params region=europe")
    print("  - Check status: ecochain oracle status")
    
    if not args.no_wait:
        print("\nPress Ctrl+C to stop the network")
        try:
            # This is just a simulation - in a real implementation, 
            # this would run as a service or daemon
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping Oracle Network...")

def _oracle_register_provider(args):
    """Register a new data provider with the oracle network"""
    if not args.name or not args.type:
        print("Error: Provider name and data type are required")
        print("Usage: ecochain oracle register --name \"Provider Name\" --type carbon_intensity,energy_mix")
        return
    
    print(f"Registering provider: {args.name}")
    print(f"Supported data types: {args.type}")
    print("In a real implementation, this would connect to a running oracle network.")
    print("For this demo, use 'ecochain oracle start' to start the network with pre-registered providers.")

def _oracle_request_data(args):
    """Request data from the oracle network"""
    if not args.type:
        print("Error: Data type is required")
        print("Usage: ecochain oracle request --type carbon_intensity --params region=europe")
        return
    
    # Parse parameters
    params = {}
    if args.params:
        for param in args.params.split(','):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key.strip()] = value.strip()
    
    print(f"Requesting data of type: {args.type}")
    print(f"Parameters: {params}")
    print("In a real implementation, this would connect to a running oracle network.")
    print("For this demo, we'll simulate a data request and response:")
    
    # Simulate a data request
    print("\nSimulated Oracle Network Response:")
    
    if args.type == "carbon_intensity":
        region = params.get("region", "global")
        print(f"Carbon intensity for {region}: 285.7 gCO2/kWh")
        print("Data provided by: CarbonData Inc.")
        print("Oracle consensus: 3/3 providers agreed")
        print("Confidence: High (95%)")
    
    elif args.type == "energy_mix":
        region = params.get("region", "global")
        print(f"Energy mix for {region}:")
        print("  Coal: 32.1%")
        print("  Gas: 24.5%")
        print("  Nuclear: 14.2%")
        print("  Hydro: 16.8%")
        print("  Wind: 8.3%")
        print("  Solar: 3.2%")
        print("  Biomass: 0.9%")
        print("Data provided by: 3 oracle network providers")
        print("Consensus: Achieved (89% agreement)")
    
    elif args.type == "certificate_verification":
        cert_id = params.get("certificate_id", "REC-1234-5678-90AB")
        print(f"Certificate verification for {cert_id}:")
        if cert_id == "REC-1234-5678-90AB":
            print("  Valid: Yes")
            print("  Issuer: Green-e Energy")
            print("  Energy Source: Wind")
            print("  Amount: 10,000 kWh")
            print("  Issue Date: 2023-01-15")
            print("  Valid Until: 2024-01-15")
        else:
            print("  Valid: No")
            print("  Reason: Certificate not found or invalid")
        print("Data provided by: GreenCert Authority")
        print("Oracle confidence: High (100%)")
    
    else:
        print(f"Unknown data type: {args.type}")

def _oracle_network_status(args):
    """Display status of the oracle network"""
    print("Oracle Network Status:")
    print("In a real implementation, this would connect to a running oracle network.")
    print("For this demo, we'll display simulated network statistics:")
    
    print("\nNetwork Statistics:")
    print("  Providers:")
    print("    Total: 5")
    print("    Active: 4")
    print("  Requests:")
    print("    Total: 127")
    print("    Pending: 3")
    print("    Finalized: 124")
    print("  Reputation:")
    print("    Average Score: 73.5")
    print("    Highest Score: 92.3 (GreenCert Authority)")
    print("    Lowest Score: 42.1 (EcoMetrics Labs)")
    
    print("\nTop Providers by Reputation:")
    print("  1. GreenCert Authority - 92.3")
    print("  2. CarbonData Inc. - 85.7")
    print("  3. CleanEnergy Consortium - 78.9")
    print("  4. EcoTracker Network - 68.4")
    
    print("\nRecent Data Requests:")
    print("  1. carbon_intensity (europe) - Completed 2 minutes ago")
    print("  2. energy_mix (north_america) - Completed 15 minutes ago")
    print("  3. certificate_verification (REC-2345-6789-ABCD) - Completed 25 minutes ago")
    print("  4. carbon_intensity (asia) - Pending (1/3 responses)")

def optimize_command(args):
    """Generate optimization recommendations for mining operations"""
    config = load_config()
    data_collector = DataCollector()
    advisor = OptimizationAdvisor(config.get('optimization_model_path'))
    
    # Get the operation
    if args.id:
        # Find the operation with the matching ID
        all_operations = data_collector.get_mining_operations()
        matching_operations = [op for op in all_operations if op["id"] == args.id]
        if not matching_operations:
            print(f"Operation with ID {args.id} not found")
            return
        operation = matching_operations[0]
    else:
        operations = data_collector.get_mining_operations()
        if not operations:
            print("No operations found")
            return
        operation = operations[0]
    
    print(f"Generating optimization recommendations for: {operation['name']} (ID: {operation['id']})")
    
    # Get carbon data
    carbon_data = data_collector.get_carbon_data(operation["id"])
    
    # Generate recommendations
    recommendations = advisor.generate_recommendations(operation, carbon_data)
    
    # Display results
    print("\n=== Optimization Recommendations ===\n")
    
    # Hardware recommendations
    if recommendations["hardware_recommendations"]:
        print("Hardware Upgrade Recommendations:")
        for i, rec in enumerate(recommendations["hardware_recommendations"], 1):
            print(f"  {i}. {rec['description']}")
            print(f"     - Efficiency improvement: {rec['efficiency_improvement_percentage']:.1f}%")
            print(f"     - Annual savings: ${rec['annual_savings_usd']:.2f}")
            print(f"     - Cost: ${rec['cost_usd']:.2f}")
            print(f"     - ROI: {rec['roi_years']:.1f} years ({rec['roi_months']:.1f} months)")
            print(f"     - Sustainability improvement: {rec['sustainability_improvement_percentage']:.1f}%")
            print()
    else:
        print("No hardware upgrade recommendations available.\n")
    
    # Energy recommendations
    if recommendations["energy_recommendations"]:
        print("Energy Source Recommendations:")
        for i, rec in enumerate(recommendations["energy_recommendations"], 1):
            print(f"  {i}. {rec['description']}")
            print(f"     - Cost reduction: ${rec['current_cost_per_kwh']:.3f}/kWh → ${rec['new_cost_per_kwh']:.3f}/kWh")
            print(f"     - Annual savings: ${rec['annual_cost_savings_usd']:.2f}")
            print(f"     - Installation cost: ${rec['installation_cost_usd']:.2f}")
            print(f"     - ROI: {rec['roi_years']:.1f} years ({rec['roi_months']:.1f} months)")
            print(f"     - Carbon reduction: {rec['carbon_reduction_percentage']:.1f}%")
            print(f"     - Annual carbon savings: {rec['annual_carbon_savings_tons']:.2f} tons")
            print(f"     - Reliability: {rec['reliability']:.1f}%")
            print()
    else:
        print("No energy source recommendations available.\n")
    
    # Cooling recommendations
    if recommendations["cooling_recommendations"]:
        print("Cooling System Recommendations:")
        for i, rec in enumerate(recommendations["cooling_recommendations"], 1):
            print(f"  {i}. {rec['description']}")
            print(f"     - Efficiency improvement: {rec['efficiency_improvement_percentage']:.1f}%")
            print(f"     - Operational cost reduction: {rec['operational_cost_reduction_percentage']:.1f}%")
            print(f"     - Annual savings: ${rec['annual_savings_usd']:.2f}")
            print(f"     - Installation cost: ${rec['installation_cost_usd']:.2f}")
            print(f"     - ROI: {rec['roi_years']:.1f} years ({rec['roi_months']:.1f} months)")
            print(f"     - Maintenance cost: {rec['maintenance_cost']}")
            print()
    else:
        print("No cooling system recommendations available.\n")
    
    # Combined ROI
    combined = recommendations["combined_roi"]
    print("Combined Implementation ROI:")
    print(f"  Total investment: ${combined['total_investment_usd']:.2f}")
    print(f"  Annual savings: ${combined['annual_savings_usd']:.2f} (${combined['monthly_savings_usd']:.2f}/month)")
    print(f"  ROI: {combined['roi_years']:.1f} years ({combined['roi_months']:.1f} months)")
    print(f"  Payback date: {combined['payback_date']}")
    print(f"  Total sustainability improvement: {combined['sustainability_improvement_percentage']:.1f}%")
    print(f"  Recommendations included:")
    for category, name in combined["recommendations_included"].items():
        if name:
            print(f"    - {category.title()}: {name}")

def predict_command(args):
    """Generate predictive analytics"""
    predictor = PredictiveAnalytics()
    
    if args.action == 'forecast':
        print("Generating sustainability score forecast...")
        
        # Use historical data for past N days
        historical_days = args.days or 180
        
        # Forecast for next M days
        forecast_horizon = args.horizon or 90
        
        # Get operation ID if provided, otherwise predict for all operations
        operation_id = getattr(args, 'id', None)
        
        # Get historical data for the operation
        from ecochain.data_module.data_collector import DataCollector
        data_collector = DataCollector()
        historical_data = data_collector.get_historical_scores(
            days=historical_days,
            operation_id=operation_id
        )
        
        if not historical_data:
            print("No historical data found. Using simulated data for demonstration.")
            # Generate some simulated data for demonstration
            import random
            from datetime import datetime, timedelta
            
            base_score = 70.0
            historical_data = []
            start_date = datetime.now() - timedelta(days=historical_days)
            
            for i in range(historical_days):
                date = start_date + timedelta(days=i)
                # Add some random variation and a slight upward trend
                score = base_score + random.uniform(-5, 5) + (i * 0.05)
                score = max(0, min(100, score))  # Ensure within 0-100 range
                
                historical_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'score': round(score, 2),
                    'operation_id': operation_id or 'miner-0001'
                })
            
            print(f"Generated {len(historical_data)} simulated data points.")
        
        # Generate forecast using the correct method name from PredictiveAnalytics class
        forecast_result = predictor.forecast_sustainability(
            historical_scores=historical_data,
            horizon_days=forecast_horizon
        )
        
        if "error" in forecast_result:
            print(f"Error generating forecast: {forecast_result['error']}")
            return
        
        # Print forecast summary
        print(f"\nSustainability Score Forecast (next {forecast_horizon} days):")
        
        # Display the first few forecast points
        print("\nForecast Preview:")
        preview_count = min(5, len(forecast_result.get('forecast', [])))
        for i in range(preview_count):
            point = forecast_result['forecast'][i]
            print(f"  {point['date']}: {point['forecasted_score']} (range: {point['lower_bound']} - {point['upper_bound']})")
        
        # Save to file if specified
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(forecast_result, f, indent=2)
            print(f"\nForecast saved to {args.output}")
    
    elif args.action == 'market':
        print("Generating market correlation analysis...")
        
        # Use historical data for past N days
        historical_days = args.days or 365
        
        # Get historical sustainability data
        from ecochain.data_module.data_collector import DataCollector
        data_collector = DataCollector()
        sustainability_data = data_collector.get_historical_scores(
            days=historical_days
        )
        
        # Get token price data
        token_price_data = data_collector.get_token_prices(
            days=historical_days
        )
        
        if not sustainability_data or not token_price_data:
            print("No historical data found. Using simulated data for demonstration.")
            # Generate simulated data for demonstration
            import random
            from datetime import datetime, timedelta
            
            base_score = 70.0
            base_price = 1.0
            sustainability_data = []
            token_price_data = []
            start_date = datetime.now() - timedelta(days=historical_days)
            
            for i in range(historical_days):
                date = start_date + timedelta(days=i)
                # Add some random variation and a slight correlation between score and price
                score = base_score + random.uniform(-5, 5) + (i * 0.02)
                score = max(0, min(100, score))  # Ensure within 0-100 range
                
                # Price follows score with some lag and noise
                price = base_price * (1 + (score - base_score) * 0.01) + random.uniform(-0.05, 0.05)
                price = max(0.1, price)  # Ensure price is positive
                
                sustainability_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'score': round(score, 2)
                })
                
                token_price_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'price': round(price, 4),
                    'token': 'ECO'
                })
            
            print(f"Generated {len(sustainability_data)} simulated data points.")
        
        # Generate analysis
        analysis = predictor.analyze_market_correlation(
            sustainability_data=sustainability_data,
            token_price_data=token_price_data
        )
        
        # Print analysis summary
        print("\nSustainability Score - Market Correlation Analysis:")
        print(f"\nOverall correlation: {analysis.get('overall_correlation', 'N/A')}")
        
        # Print lag analysis
        if 'lag_analysis' in analysis:
            print("\nLag Analysis:")
            for lag_data in analysis['lag_analysis']:
                sig_marker = "*" if lag_data.get('significant', False) else ""
                print(f"  Lag {lag_data['lag_days']} days: {lag_data['correlation']}{sig_marker} (p={lag_data['p_value']})")
        
        # Print price impact
        if 'price_impact' in analysis and 'percentage_impact' in analysis['price_impact']:
            print("\nPrice Impact by Score Range:")
            for range_name, impact in analysis['price_impact']['percentage_impact'].items():
                print(f"  {range_name}: {impact:+.2f}%")
        
        # Print interpretation
        if 'interpretation' in analysis:
            print("\nInterpretation:")
            print(f"  {analysis['interpretation']}")
        
        # Save to file if specified
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(analysis, f, indent=2)
            print(f"\nAnalysis saved to {args.output}")
    
    else:
        print(f"Unknown action: {args.action}")
        print("Available actions: forecast, market")

def compliance_command(args):
    """Generate ESG reports and check regulatory compliance"""
    config = load_config()
    data_collector = DataCollector()
    reporter = ComplianceReporter(config.get('regulations_path'))
    
    if args.action == 'report':
        # Generate ESG report
        print(f"Generating {args.type} ESG report...")
        
        # Get the operation
        if args.id:
            # Find the operation with the matching ID
            all_operations = data_collector.get_mining_operations()
            matching_operations = [op for op in all_operations if op["id"] == args.id]
            if not matching_operations:
                print(f"Operation with ID {args.id} not found")
                return
            operation = matching_operations[0]
        else:
            operations = data_collector.get_mining_operations()
            if not operations:
                print("No operations found")
                return
            operation = operations[0]
        
        # Get carbon data
        carbon_data = data_collector.get_carbon_data(operation["id"])
        
        # Generate report
        report = reporter.generate_esg_report(
            operation,
            carbon_data,
            report_type=args.type or "standard"
        )
        
        if "error" in report:
            print(f"Error generating report: {report['error']}")
            return
            
        # Display report summary
        print("\n=== ESG Report Summary ===\n")
        print(f"Report ID: {report['report_id']}")
        print(f"Operation: {report['operation_name']} (ID: {report['operation_id']})")
        print(f"Report Type: {report['report_type'].title()}")
        print(f"Generated: {report['generated_at']}")
        
        if report['missing_metrics']:
            print("\nWarning: The following metrics are missing:")
            for metric in report['missing_metrics']:
                print(f"  - {metric}")
        
        # Display summary
        summary = report['summary']
        print(f"\nSustainability Score: {summary['sustainability_score']} ({summary['rating']})")
        
        print("\nKey Findings:")
        for finding in summary['key_findings']:
            print(f"  - {finding}")
            
        print("\nRecommendations:")
        for recommendation in summary['recommendations']:
            print(f"  - {recommendation}")
            
        # Display compliance summary
        compliance = report['compliance']
        print(f"\nOverall Compliance: {'✅ Compliant' if compliance['overall_compliance'] else '❌ Non-compliant'}")
        
        # Show non-compliant jurisdictions
        non_compliant = [
            j for j, data in compliance['jurisdictions'].items() 
            if not data['compliant']
        ]
        
        if non_compliant:
            print("\nNon-compliant jurisdictions:")
            for j in non_compliant:
                print(f"  - {compliance['jurisdictions'][j]['name']}")
        
        # Save report to file if requested
        if args.output:
            try:
                with open(args.output, 'w') as f:
                    json.dump(report, f, indent=2)
                print(f"\nReport saved to {args.output}")
            except Exception as e:
                print(f"Error saving report: {str(e)}")
    
    elif args.action == 'check':
        # Check regulatory compliance
        print("Checking regulatory compliance...")
        
        # Get the operation
        if args.id:
            # Find the operation with the matching ID
            all_operations = data_collector.get_mining_operations()
            matching_operations = [op for op in all_operations if op["id"] == args.id]
            if not matching_operations:
                print(f"Operation with ID {args.id} not found")
                return
            operation = matching_operations[0]
        else:
            operations = data_collector.get_mining_operations()
            if not operations:
                print("No operations found")
                return
            operation = operations[0]
        
        # Get carbon data
        carbon_data = data_collector.get_carbon_data(operation["id"])
        
        # Parse jurisdictions if provided
        jurisdictions = None
        if args.jurisdictions:
            jurisdictions = [j.strip() for j in args.jurisdictions.split(',')]
        
        # Check compliance
        results = reporter.check_regulatory_compliance(
            operation,
            carbon_data,
            jurisdictions=jurisdictions
        )
        
        if "error" in results:
            print(f"Error checking compliance: {results['error']}")
            return
            
        # Display compliance results
        print("\n=== Regulatory Compliance Results ===\n")
        print(f"Operation: {operation['name']} (ID: {operation['id']})")
        print(f"Overall Compliance: {'✅ Compliant' if results['overall_compliance'] else '❌ Non-compliant'}")
        
        # Show results for each jurisdiction
        for j_name, j_data in results['jurisdictions'].items():
            status = "✅" if j_data['compliant'] else "❌"
            print(f"\n{status} {j_data['name']} ({j_name}):")
            
            # Show non-compliant regulations
            non_compliant_regs = [r for r in j_data['regulations'] if not r['compliant']]
            
            if non_compliant_regs:
                print("  Non-compliant regulations:")
                for reg in non_compliant_regs:
                    print(f"  - {reg['name']}")
                    
                    # Show non-compliant requirements
                    non_compliant_reqs = [r for r in reg['requirements'] if not r['compliant']]
                    for req in non_compliant_reqs:
                        print(f"    • {req['name']}: {req['details']}")
            else:
                print("  All regulations compliant")
        
        # Save results to file if requested
        if args.output:
            try:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"\nCompliance results saved to {args.output}")
            except Exception as e:
                print(f"Error saving results: {str(e)}")
    
    else:
        print(f"Unknown action: {args.action}")
        print("Available actions: report, check")

def auto_command(args):
    """Manage automated smart contract operations"""
    config = load_config()
    auto_manager = AutoContractManager(config_path=CONFIG_FILE)
    
    # For testing purposes, create a simulated blockchain adapter
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
            import os
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
            import os
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
            import random
            if function_name == "getEligibleMiners":
                # Return a subset of the miners as eligible
                miners = args[0] if args and len(args) > 0 else []
                return [m for m in miners if random.random() > 0.3]
            return None

    # Replace the chain adapter with our simulated one for testing
    auto_manager.chain_adapter = SimulatedChainAdapter()
    
    if args.action == 'deploy':
        # Deploy auto reward contract
        print("Deploying Auto Reward Distributor contract...")
        
        # Check if token is deployed
        if 'contracts' not in config or 'token_address' not in config['contracts']:
            print("Error: EcoToken needs to be deployed first. Run 'ecochain reward deploy'")
            return
            
        deploy_result = auto_manager.deploy_auto_reward_contract()
        
        if deploy_result['success']:
            print(f"Auto Reward Distributor deployed at {deploy_result['contract_address']}")
            
            # Save contract address to config
            if 'contracts' not in config:
                config['contracts'] = {}
            config['contracts']['auto_reward_address'] = deploy_result['contract_address']
            save_config(config)
        else:
            print(f"Error deploying contract: {deploy_result.get('error', 'Unknown error')}")
    
    elif args.action == 'schedule':
        # Set up a distribution schedule
        frequency = args.frequency or 'daily'
        
        eligible_miners = None
        if args.miners:
            eligible_miners = [m.strip() for m in args.miners.split(',')]
        
        start_time = None
        if args.start:
            try:
                # Convert start time string to timestamp
                start_datetime = datetime.strptime(args.start, '%Y-%m-%d %H:%M:%S')
                start_time = int(start_datetime.timestamp())
            except ValueError:
                print(f"Error: Invalid start time format. Use YYYY-MM-DD HH:MM:SS")
                return
        
        print(f"Setting up {frequency} distribution schedule...")
        schedule_result = auto_manager.set_distribution_schedule(
            frequency=frequency,
            eligible_miners=eligible_miners,
            start_time=start_time
        )
        
        if schedule_result['success']:
            print(f"Schedule created with ID: {schedule_result['schedule_id']}")
            print(f"Frequency: {schedule_result['frequency']}")
            print(f"Next run: {datetime.fromtimestamp(schedule_result['next_run_time']).strftime('%Y-%m-%d %H:%M:%S')}")
            
            if eligible_miners:
                print(f"Eligible miners: {schedule_result['eligible_miners_count']}")
        else:
            print(f"Error creating schedule: {schedule_result.get('error', 'Unknown error')}")
    
    elif args.action == 'list':
        # List distribution schedules
        schedules = auto_manager.get_distribution_schedules()
        
        if not schedules:
            print("No distribution schedules found.")
            return
            
        print(f"Found {len(schedules)} distribution schedules:")
        for schedule in schedules:
            print(f"\nSchedule ID: {schedule['id']}")
            print(f"  Frequency: {schedule['frequency']}")
            print(f"  Next run: {schedule['next_run_at']}")
            print(f"  Eligible miners: {schedule['eligible_miners_count']}")
    
    elif args.action == 'remove':
        # Remove a distribution schedule
        if args.id is None:
            print("Error: Schedule ID is required")
            return
            
        schedule_id = int(args.id)
        remove_result = auto_manager.remove_distribution_schedule(schedule_id)
        
        if remove_result['success']:
            print(f"Successfully removed {remove_result['frequency']} schedule")
        else:
            print(f"Error removing schedule: {remove_result.get('error', 'Unknown error')}")
    
    elif args.action == 'update-score':
        # Update a miner's score
        if not args.address:
            print("Error: Miner address is required")
            return
            
        if args.score is None:
            print("Error: Score is required")
            return
            
        score = float(args.score)
        print(f"Updating score for miner {args.address} to {score}...")
        
        update_result = auto_manager.update_miner_score(args.address, score)
        
        if update_result['success']:
            print(f"Successfully updated score for miner {args.address}")
            print(f"Transaction hash: {update_result['transaction_hash']}")
        else:
            print(f"Error updating score: {update_result.get('error', 'Unknown error')}")
    
    elif args.action == 'distribute':
        # Distribute rewards
        if args.address:
            # Distribute to a single miner
            print(f"Distributing rewards to miner {args.address}...")
            
            distribute_result = auto_manager.distribute_reward(args.address)
            
            if distribute_result['success']:
                print(f"Successfully distributed {distribute_result['reward_amount']} tokens")
                print(f"Transaction hash: {distribute_result['transaction_hash']}")
            else:
                print(f"Error distributing reward: {distribute_result.get('error', 'Unknown error')}")
        
        elif args.batch and args.miners:
            # Distribute to multiple miners
            miners = [m.strip() for m in args.miners.split(',')]
            print(f"Distributing rewards to {len(miners)} miners in batch...")
            
            batch_result = auto_manager.batch_distribute_rewards(miners)
            
            if batch_result['success']:
                print(f"Successfully distributed rewards to {batch_result['miners_count']} miners")
                print(f"Total distributed: {batch_result['total_distributed']} tokens")
                print(f"Transaction hash: {batch_result['transaction_hash']}")
            else:
                print(f"Error distributing rewards: {batch_result.get('error', 'Unknown error')}")
        
        else:
            # Distribute to eligible miners
            print("Finding eligible miners for reward distribution...")
            
            eligible_miners = auto_manager.get_eligible_miners()
            
            if not eligible_miners:
                print("No eligible miners found.")
                return
                
            print(f"Found {len(eligible_miners)} eligible miners")
            
            # Confirm with user
            if not args.yes:
                confirm = input(f"Distribute rewards to {len(eligible_miners)} miners? [y/N] ")
                if confirm.lower() != 'y':
                    print("Operation cancelled.")
                    return
            
            # Distribute rewards
            print(f"Distributing rewards to {len(eligible_miners)} miners...")
            
            batch_result = auto_manager.batch_distribute_rewards(eligible_miners)
            
            if batch_result['success']:
                print(f"Successfully distributed rewards to {batch_result['miners_count']} miners")
                print(f"Total distributed: {batch_result['total_distributed']} tokens")
                print(f"Transaction hash: {batch_result['transaction_hash']}")
            else:
                print(f"Error distributing rewards: {batch_result.get('error', 'Unknown error')}")
    
    elif args.action == 'start':
        # Start the scheduler
        print("Starting automated reward distribution scheduler...")
        
        # Check if there are any schedules
        schedules = auto_manager.get_distribution_schedules()
        if not schedules:
            print("Warning: No distribution schedules found. Add schedules with 'ecochain auto schedule'")
        
        auto_manager.start_scheduler()
        
        print("Scheduler started. Press Ctrl+C to stop.")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping scheduler...")
            auto_manager.stop_scheduler()
            print("Scheduler stopped.")
    
    else:
        print(f"Unknown action: {args.action}")
        print("Available actions: deploy, schedule, list, remove, update-score, distribute, start")

def run():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(description='EcoChain Guardian CLI')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup EcoChain Guardian')
    
    # Data collection command
    collect_parser = subparsers.add_parser('collect', help='Collect mining operation data')
    collect_parser.add_argument('--location', help='Filter operations by location')
    collect_parser.add_argument('--id', help='Get operation by ID')
    collect_parser.add_argument('--limit', type=int, help='Limit the number of results')
    collect_parser.add_argument('--carbon', action='store_true', help='Include carbon data')
    collect_parser.add_argument('--energy', action='store_true', help='Include energy mix data')
    collect_parser.set_defaults(func=collect_command)
    
    # Analysis command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze mining operations')
    analyze_parser.add_argument('--id', help='Analyze specific operation by ID')
    analyze_parser.add_argument('--limit', type=int, help='Limit the number of operations to analyze')
    analyze_parser.add_argument('--ml', action='store_true', help='Use ML-based scoring')
    analyze_parser.add_argument('--model', help='Path to ML model file')
    analyze_parser.set_defaults(func=analyze_command)
    
    # Verification command
    verify_parser = subparsers.add_parser('verify', help='Create and verify zkSNARK proofs')
    verify_parser.add_argument('--id', help='Verify operation by ID')
    verify_parser.add_argument('--create', action='store_true', help='Create a new proof')
    verify_parser.add_argument('--verify', action='store_true', help='Verify an existing proof')
    verify_parser.add_argument('--output', help='Output file for proof')
    verify_parser.add_argument('--input', help='Input file containing proof')
    verify_parser.set_defaults(func=verify_command)
    
    # Reward command
    reward_parser = subparsers.add_parser('reward', help='Manage rewards and tokens')
    reward_parser.add_argument('action', choices=['deploy', 'distribute', 'balance'], help='Action to perform')
    reward_parser.add_argument('--mint', action='store_true', help='Mint new tokens')
    reward_parser.add_argument('--amount', type=float, help='Amount to mint or transfer')
    reward_parser.add_argument('--to', help='Recipient address')
    reward_parser.add_argument('--from', dest='from_addr', help='Sender address')
    reward_parser.add_argument('--transfer', action='store_true', help='Transfer tokens')
    reward_parser.add_argument('--balance', help='Check token balance for address')
    reward_parser.add_argument('--issue-nft', action='store_true', help='Issue sustainability NFT badge')
    reward_parser.add_argument('--tier', choices=['bronze', 'silver', 'gold', 'platinum'], help='NFT tier')
    reward_parser.add_argument('--operation-id', help='Mining operation ID for NFT')
    reward_parser.add_argument('--address', help='Wallet address for balance check')
    reward_parser.set_defaults(func=reward_command)
    
    # Staking command
    stake_parser = subparsers.add_parser('stake', help='Manage token staking')
    stake_parser.add_argument('--action', choices=['stake', 'unstake', 'claim', 'status'], required=True, help='Staking action to perform')
    stake_parser.add_argument('--amount', type=float, help='Amount to stake or unstake')
    stake_parser.add_argument('--address', help='Staker address')
    stake_parser.add_argument('--duration', type=int, help='Staking duration in days')
    stake_parser.set_defaults(func=stake_command)
    
    # Governance command
    gov_parser = subparsers.add_parser('governance', help='DAO governance')
    gov_parser.add_argument('--action', choices=['propose', 'vote', 'execute', 'list', 'details'], required=True, help='Governance action')
    gov_parser.add_argument('--title', help='Proposal title')
    gov_parser.add_argument('--description', help='Proposal description')
    gov_parser.add_argument('--param', help='Parameter to change')
    gov_parser.add_argument('--value', help='New parameter value')
    gov_parser.add_argument('--id', help='Proposal ID')
    gov_parser.add_argument('--vote', choices=['for', 'against', 'abstain'], help='Vote direction')
    gov_parser.add_argument('--voter', help='Voter address')
    gov_parser.add_argument('--amount', type=float, help='Voting power to use')
    gov_parser.set_defaults(func=governance_command)
    
    # Training command
    train_parser = subparsers.add_parser('train', help='Train ML models')
    train_parser.add_argument('--samples', type=int, default=1000, help='Number of samples for training')
    train_parser.add_argument('--output', help='Output file for the trained model')
    train_parser.add_argument('--test-split', type=float, default=0.2, help='Test split ratio')
    train_parser.set_defaults(func=train_command)
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run demonstration')
    demo_parser.add_argument('--comprehensive', action='store_true', help='Run comprehensive demo')
    demo_parser.set_defaults(func=demo_command)
    
    # API Gateway command
    api_parser = subparsers.add_parser('api', help='Start API gateway')
    api_parser.add_argument('--mode', choices=['rest', 'graphql'], default='rest', help='API mode')
    api_parser.add_argument('--port', type=int, help='Port to listen on')
    api_parser.add_argument('--public', action='store_true', help='Make API publicly accessible')
    api_parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    api_parser.set_defaults(func=api_command)
    
    # Multi-chain command
    chain_parser = subparsers.add_parser('multichain', help='Multi-chain operations')
    chain_parser.add_argument('action', choices=['list', 'compare', 'bridge'], help='Action to perform')
    chain_parser.add_argument('--testnet', action='store_true', help='Use testnet instead of mainnet')
    chain_parser.add_argument('--connect', action='store_true', help='Connect to blockchain networks')
    chain_parser.add_argument('--provider-url', help='Custom provider URL')
    chain_parser.add_argument('--detailed', action='store_true', help='Show detailed information')
    chain_parser.add_argument('--source', help='Source chain for bridge operations')
    chain_parser.add_argument('--target', help='Target chain for bridge operations')
    chain_parser.add_argument('--amount', help='Amount to bridge')
    chain_parser.set_defaults(func=multichain_command)
    
    # Oracle network command
    oracle_parser = subparsers.add_parser('oracle', help='Oracle network operations')
    oracle_parser.add_argument('action', choices=['start', 'register', 'request', 'status'], help='Action to perform')
    oracle_parser.add_argument('--no-wait', action='store_true', help='Don\'t wait for Ctrl+C when starting')
    oracle_parser.add_argument('--name', help='Provider name')
    oracle_parser.add_argument('--type', help='Data type(s) supported/requested')
    oracle_parser.add_argument('--params', help='Data request parameters (key1=value1,key2=value2)')
    oracle_parser.set_defaults(func=oracle_command)
    
    # Optimize command
    optimize_parser = subparsers.add_parser('optimize', help='Generate optimization recommendations')
    optimize_parser.add_argument('--id', help='Operation ID')
    optimize_parser.set_defaults(func=optimize_command)
    
    # Predict command
    predict_parser = subparsers.add_parser('predict', help='Generate predictive analytics')
    predict_parser.add_argument('action', choices=['forecast', 'market'], help='Action to perform')
    predict_parser.add_argument('--days', type=int, help='Number of days for historical data')
    predict_parser.add_argument('--horizon', type=int, help='Number of days for forecast horizon')
    predict_parser.add_argument('--output', help='Output file for results')
    predict_parser.set_defaults(func=predict_command)
    
    # Compliance command
    compliance_parser = subparsers.add_parser('compliance', help='Generate ESG reports and check regulatory compliance')
    compliance_parser.add_argument('action', choices=['report', 'check'], help='Action to perform')
    compliance_parser.add_argument('--id', help='Operation ID')
    compliance_parser.add_argument('--type', help='Report type')
    compliance_parser.add_argument('--jurisdictions', help='Jurisdictions to check compliance')
    compliance_parser.add_argument('--output', help='Output file for results')
    compliance_parser.set_defaults(func=compliance_command)
    
    # Auto contract command
    auto_parser = subparsers.add_parser('auto', help='Manage automated smart contracts')
    auto_parser.add_argument('action', choices=['deploy', 'schedule', 'list', 'remove', 'update-score', 'distribute', 'start'], 
                             help='Action to perform')
    auto_parser.add_argument('--frequency', choices=['daily', 'weekly', 'monthly'], 
                             help='Distribution frequency for schedules')
    auto_parser.add_argument('--miners', help='Comma-separated list of miner addresses')
    auto_parser.add_argument('--start', help='Schedule start time (format: YYYY-MM-DD HH:MM:SS)')
    auto_parser.add_argument('--id', help='Schedule ID for removal')
    auto_parser.add_argument('--address', help='Miner address for score update or distribution')
    auto_parser.add_argument('--score', type=float, help='Sustainability score (0-100)')
    auto_parser.add_argument('--batch', action='store_true', help='Perform batch distribution')
    auto_parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation prompt')
    auto_parser.set_defaults(func=auto_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup environment
    config = setup_environment()
    
    # Execute command if provided
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    run() 
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
        simulate_rewards(args.config)

if __name__ == "__main__":
    main() 