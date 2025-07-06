"""
GraphQL API for EcoChain Guardian

Provides GraphQL interface for flexible data querying, including:
- Mining operations with filtering and pagination
- Sustainability scoring and analysis
- Token and reward information
- Data provider network status
"""

import os
from typing import Dict, List, Optional, Any

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from ariadne import QueryType, MutationType, ObjectType, load_schema_from_path, make_executable_schema
from ariadne.asgi import GraphQL
# Import playground HTML directly
PLAYGROUND_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset=utf-8/>
    <meta name="viewport" content="user-scalable=no, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, minimal-ui">
    <title>GraphQL Playground</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/graphql-playground-react@1.7.22/build/static/css/index.css" />
    <script src="https://cdn.jsdelivr.net/npm/graphql-playground-react@1.7.22/build/static/js/middleware.js"></script>
</head>
<body>
    <div id="root">
        <style>
            body {
                background-color: rgb(23, 42, 58);
                font-family: Open Sans, sans-serif;
                height: 90vh;
            }
            #root {
                height: 100%;
                width: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .loading {
                font-size: 32px;
                font-weight: 200;
                color: rgba(255, 255, 255, .6);
                margin-left: 20px;
            }
            img {
                width: 78px;
                height: 78px;
            }
            .title {
                font-weight: 400;
            }
        </style>
        <img src='https://cdn.jsdelivr.net/npm/graphql-playground-react/build/logo.png' alt=''>
        <div class="loading"> Loading <span class="title">GraphQL Playground</span></div>
    </div>
    <script>window.addEventListener('load', function (event) {
      GraphQLPlayground.init(document.getElementById('root'), {
        endpoint: '/graphql',
      })
    })</script>
</body>
</html>
"""

from ecochain.data_module.data_collector import DataCollector
from ecochain.analysis_module.sustainability_scorer import SustainabilityScorer
from ecochain.analysis_module.ml_scoring import MLSustainabilityScorer
from ecochain.reward_module.eco_token import EcoToken
from ecochain.reward_module.eco_staking import EcoStaking
from ecochain.reward_module.eco_governance import EcoGovernance
from ecochain.reward_module.zk_verification import ZKCarbonVerifier

# Define GraphQL types
type_defs = """
type Query {
    operations(limit: Int, location: String): [MiningOperation!]!
    operation(id: ID!): MiningOperation
    carbonData(operationId: ID!): CarbonData
    score(operationId: ID!): SustainabilityScore
    tokenBalance(address: String!): TokenBalance
    stakingStats: StakingStats
    activeStakes(address: String!): [Stake!]!
    proposals: [Proposal!]!
    proposal(id: ID!): ProposalDetails
    dataProviders(status: String): [DataProvider!]!
}

type Mutation {
    verifyCarbonData(operationId: ID!): VerificationResult!
    submitDataReport(input: DataReportInput!): SubmissionResult!
    createProposal(input: ProposalInput!): ProposalResult!
    castVote(proposalId: ID!, voteType: VoteType!): VoteResult!
}

type MiningOperation {
    id: ID!
    name: String!
    location: String!
    wallet_address: String!
    hashrate: Float!
    power_consumption_kw: Float!
    hardware_efficiency: Float!
    carbon_data: CarbonData
    score: SustainabilityScore
}

type CarbonData {
    renewable_energy_percentage: Float!
    energy_efficiency_rating: Float!
    carbon_footprint_tons_per_day: Float!
    carbon_offset_percentage: Float!
    sustainability_initiatives: Int!
}

type SustainabilityScore {
    operation_id: ID!
    sustainability_score: Float!
    sustainability_tier: String!
    component_scores: ComponentScores
    improvement_suggestions: [String!]
    is_anomaly: Boolean
    scoring_method: String!
}

type ComponentScores {
    renewable_energy: Float!
    energy_efficiency: Float!
    carbon_footprint: Float!
    carbon_offset: Float!
    sustainability_initiatives: Float!
    location_factor: Float!
}

type TokenBalance {
    address: String!
    balance: String!
    badges: [Badge!]!
}

type Badge {
    id: ID!
    tier: String!
    score: Float!
    issued_at: String!
}

type StakingStats {
    total_staked: String!
    rewards_pool: String!
    active_stakes: Int!
    active_stakers: Int!
    base_apy: Int!
    min_staking_period_days: Float!
    tier_multipliers: TierMultipliers!
}

type TierMultipliers {
    Platinum: Int!
    Gold: Int!
    Silver: Int!
    Bronze: Int!
    Standard: Int!
}

type Stake {
    id: ID!
    amount: String!
    start_time: String!
    tier: String!
    estimated_reward: String!
    duration: Float!
}

type Proposal {
    id: ID!
    title: String!
    proposer: String!
    state: String!
    for_votes: String!
    against_votes: String!
    end_time: String!
}

type ProposalDetails {
    id: ID!
    proposer: String!
    title: String!
    description: String!
    start_time: String!
    end_time: String!
    for_votes: String!
    against_votes: String!
    abstain_votes: String!
    state: String!
    canceled: Boolean!
    executed: Boolean!
    creation_time: String!
    votes: [Vote!]!
}

type Vote {
    voter: String!
    vote_type: String!
    votes: String!
}

type DataProvider {
    id: ID!
    name: String!
    status: String!
    reliability_score: Float!
    reports_submitted: Int!
    last_report_time: String
}

type VerificationResult {
    operation_id: ID!
    is_valid: Boolean!
    proof_id: String
    public_inputs: PublicInputs
}

type PublicInputs {
    renewable_energy_percentage: Float
    carbon_emissions_tons: Float
}

type SubmissionResult {
    success: Boolean!
    submission_id: ID
    timestamp: String
    error: String
}

type ProposalResult {
    success: Boolean!
    proposal_id: ID
    title: String
    start_time: String
    end_time: String
    error: String
}

type VoteResult {
    success: Boolean!
    proposal_id: ID
    voter: String
    vote_type: String
    votes: String
    error: String
}

input DataReportInput {
    operation_id: ID!
    renewable_energy_percentage: Float!
    energy_consumption_kwh: Float!
    carbon_emissions_tons: Float!
    provider_id: ID!
    timestamp: String!
    signature: String!
}

input ProposalInput {
    proposer: String!
    title: String!
    description: String!
    parameter_changes: String! # JSON string
}

enum VoteType {
    FOR
    AGAINST
    ABSTAIN
}
"""

# Create resolvers
query = QueryType()
mutation = MutationType()
mining_operation = ObjectType("MiningOperation")
sustainability_score = ObjectType("SustainabilityScore")

@query.field("operations")
def resolve_operations(_, info, limit=10, location=None):
    data_collector = g.data_collector
    operations = data_collector.get_mining_operations()
    
    if location:
        operations = [op for op in operations if op.get('location') == location]
        
    return operations[:limit]

@query.field("operation")
def resolve_operation(_, info, id):
    data_collector = g.data_collector
    return data_collector.get_mining_operation(id)

@query.field("carbonData")
def resolve_carbon_data(_, info, operationId):
    data_collector = g.data_collector
    return data_collector.get_carbon_data(operationId)

@query.field("score")
def resolve_score(_, info, operationId):
    data_collector = g.data_collector
    scorer = g.scorer
    
    operation = data_collector.get_mining_operation(operationId)
    if not operation:
        return None
        
    carbon_data = data_collector.get_carbon_data(operationId)
    return scorer.score_operation(operation, carbon_data)

@mining_operation.field("carbon_data")
def resolve_operation_carbon_data(operation, info):
    data_collector = g.data_collector
    return data_collector.get_carbon_data(operation['id'])

@mining_operation.field("score")
def resolve_operation_score(operation, info):
    data_collector = g.data_collector
    scorer = g.scorer
    
    carbon_data = data_collector.get_carbon_data(operation['id'])
    return scorer.score_operation(operation, carbon_data)

@query.field("tokenBalance")
def resolve_token_balance(_, info, address):
    eco_token = g.eco_token
    balance = eco_token.get_token_balance(address)
    badges = eco_token.get_nft_badges(address)
    
    return {
        "address": address,
        "balance": str(balance),
        "badges": badges
    }

@query.field("stakingStats")
def resolve_staking_stats(_, info):
    eco_staking = g.eco_staking
    stats = eco_staking.get_staking_stats()
    
    # Convert Decimal values to strings for JSON serialization
    stats['total_staked'] = str(stats['total_staked'])
    stats['rewards_pool'] = str(stats['rewards_pool'])
    
    return stats

@query.field("activeStakes")
def resolve_active_stakes(_, info, address):
    eco_staking = g.eco_staking
    stakes = eco_staking.get_active_stakes(address)
    
    # Convert Decimal values to strings
    for stake in stakes:
        stake['amount'] = str(stake['amount'])
        stake['estimated_reward'] = str(stake['estimated_reward'])
        stake['start_time'] = str(stake['start_time'])
    
    return stakes

@query.field("proposals")
def resolve_proposals(_, info):
    eco_governance = g.eco_governance
    proposals = eco_governance.get_all_proposals()
    
    # Convert numeric values to strings for consistency
    for proposal in proposals:
        proposal['for_votes'] = str(proposal['for_votes'])
        proposal['against_votes'] = str(proposal['against_votes'])
        proposal['end_time'] = str(proposal['end_time'])
    
    return proposals

@query.field("proposal")
def resolve_proposal(_, info, id):
    eco_governance = g.eco_governance
    try:
        proposal = eco_governance.get_proposal(int(id))
        votes = eco_governance.get_votes(int(id))
        
        # Convert numeric values to strings
        proposal['for_votes'] = str(proposal['for_votes'])
        proposal['against_votes'] = str(proposal['against_votes'])
        proposal['abstain_votes'] = str(proposal['abstain_votes'])
        proposal['start_time'] = str(proposal['start_time'])
        proposal['end_time'] = str(proposal['end_time'])
        proposal['creation_time'] = str(proposal['creation_time'])
        
        for vote in votes:
            vote['votes'] = str(vote['votes'])
        
        proposal['votes'] = votes
        return proposal
    except ValueError:
        return None

@query.field("dataProviders")
def resolve_data_providers(_, info, status=None):
    # This would fetch from the actual data provider network in a real implementation
    # Simulated data for demonstration
    providers = [
        {
            "id": "dp-001",
            "name": "GreenEnergyObserver",
            "status": "active",
            "reliability_score": 0.95,
            "reports_submitted": 156,
            "last_report_time": "1625097600"
        },
        {
            "id": "dp-002",
            "name": "CarbonTracker",
            "status": "active",
            "reliability_score": 0.88,
            "reports_submitted": 89,
            "last_report_time": "1625184000"
        },
        {
            "id": "dp-003",
            "name": "MiningEcoAudit",
            "status": "inactive",
            "reliability_score": 0.76,
            "reports_submitted": 42,
            "last_report_time": "1624406400"
        }
    ]
    
    if status:
        providers = [p for p in providers if p['status'] == status]
    
    return providers

@mutation.field("verifyCarbonData")
def resolve_verify_carbon_data(_, info, operationId):
    data_collector = g.data_collector
    verifier = g.verifier
    
    operation = data_collector.get_mining_operation(operationId)
    if not operation:
        return {
            "operation_id": operationId,
            "is_valid": False,
            "proof_id": None,
            "public_inputs": None
        }
    
    carbon_data = data_collector.get_carbon_data(operationId)
    
    # Generate proving key
    proving_key = verifier.generate_proving_key()
    
    # Create carbon emissions proof
    proof = verifier.create_carbon_emissions_proof(operation, carbon_data, proving_key)
    
    # Verify the proof
    is_valid = verifier.verify_proof(proof)
    
    return {
        "operation_id": operationId,
        "is_valid": is_valid,
        "proof_id": proof.get("data_hash"),
        "public_inputs": proof.get("public_inputs", {})
    }

@mutation.field("submitDataReport")
def resolve_submit_data_report(_, info, input):
    # This would integrate with the data provider network in a real implementation
    # Simulated response for demonstration
    return {
        "success": True,
        "submission_id": "submission-" + input["operation_id"],
        "timestamp": input["timestamp"]
    }

@mutation.field("createProposal")
def resolve_create_proposal(_, info, input):
    eco_governance = g.eco_governance
    
    try:
        # Parse parameter changes from JSON string
        import json
        parameter_changes = json.loads(input["parameter_changes"])
        
        # Create proposal
        result = eco_governance.create_parameter_change_proposal(
            proposer=input["proposer"],
            title=input["title"],
            description=input["description"],
            parameter_changes=parameter_changes
        )
        
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mutation.field("castVote")
def resolve_cast_vote(_, info, proposalId, voteType):
    eco_governance = g.eco_governance
    
    try:
        # Get user from context (would be set by auth middleware)
        voter = "0x0000000000000000000000000000000000000001"  # Placeholder
        
        from ecochain.reward_module.eco_governance import VoteType
        
        # Convert string to enum
        vote_type_enum = None
        if voteType == "FOR":
            vote_type_enum = VoteType.FOR
        elif voteType == "AGAINST":
            vote_type_enum = VoteType.AGAINST
        elif voteType == "ABSTAIN":
            vote_type_enum = VoteType.ABSTAIN
        
        # Cast vote
        result = eco_governance.cast_vote(voter, int(proposalId), vote_type_enum)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def create_app(config=None):
    """Create and configure the Flask app for the GraphQL API."""
    app = Flask(__name__)
    CORS(app)
    
    # Apply configuration
    app.config.update(dict(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'ecochain-dev-key'),
        ML_MODEL_PATH=os.environ.get('ML_MODEL_PATH', 'data/models/sustainability_model.pkl'),
        USE_ML_SCORING=os.environ.get('USE_ML_SCORING', 'true').lower() == 'true'
    ))
    if config:
        app.config.update(config)
    
    # Initialize components
    with app.app_context():
        g.data_collector = DataCollector()
        
        if app.config['USE_ML_SCORING'] and os.path.exists(app.config['ML_MODEL_PATH']):
            g.scorer = MLSustainabilityScorer(app.config['ML_MODEL_PATH'])
        else:
            g.scorer = SustainabilityScorer()
            
        g.eco_token = EcoToken()
        g.eco_staking = EcoStaking(g.eco_token)
        g.eco_governance = EcoGovernance(g.eco_token)
        g.verifier = ZKCarbonVerifier()
    
    # Create executable schema
    schema = make_executable_schema(
        type_defs, 
        query, 
        mutation, 
        mining_operation,
        sustainability_score
    )
    
    # Define GraphQL view
    @app.route('/graphql', methods=['GET'])
    def graphql_playground():
        # Serve GraphQL Playground on GET request
        return PLAYGROUND_HTML, 200
    
    @app.route('/graphql', methods=['POST'])
    def graphql_server():
        # Process GraphQL queries
        data = request.get_json()
        
        from ariadne import graphql_sync
        success, result = graphql_sync(
            schema,
            data,
            context_value={'request': request},
            debug=app.debug
        )
        
        status_code = 200 if success else 400
        return jsonify(result), status_code
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port) 
 
 