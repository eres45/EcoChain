"""
REST API for EcoChain Guardian

Provides REST endpoints for third-party integration, including:
- Mining operation data and scoring
- Token and reward management
- Data provider integration
- Carbon verification
"""

import os
import time
import json
import uuid
from typing import Dict, List, Optional
from datetime import datetime

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import jwt

from ecochain.data_module.data_collector import DataCollector
from ecochain.analysis_module.sustainability_scorer import SustainabilityScorer
from ecochain.analysis_module.ml_scoring import MLSustainabilityScorer
from ecochain.analysis_module.optimization_advisor import OptimizationAdvisor
from ecochain.reward_module.eco_token import EcoToken
from ecochain.reward_module.eco_staking import EcoStaking
from ecochain.reward_module.eco_governance import EcoGovernance
from ecochain.reward_module.zk_verification import ZKCarbonVerifier

# API keys storage (in-memory for demo; use a proper database in production)
API_KEYS = {}
JWT_SECRET = os.environ.get('JWT_SECRET', 'ecochain-secret-key')

def create_app(config=None):
    """Create and configure the Flask app for the REST API."""
    app = Flask(__name__)
    CORS(app)
    
    # Apply configuration
    app.config.update(dict(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'ecochain-dev-key'),
        API_VERSION='v1',
        JWT_EXPIRATION=3600,  # 1 hour
        ML_MODEL_PATH=os.environ.get('ML_MODEL_PATH', 'data/models/sustainability_model.pkl'),
        USE_ML_SCORING=os.environ.get('USE_ML_SCORING', 'true').lower() == 'true'
    ))
    if config:
        app.config.update(config)
    
    # Set up rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["100 per day", "20 per hour"]
    )
    
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
        g.advisor = OptimizationAdvisor(app.config.get('OPTIMIZATION_MODEL_PATH'))
    
    # Authentication decorator
    def require_api_key(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            if not api_key or api_key not in API_KEYS:
                return jsonify({"error": "Invalid or missing API key"}), 401
            
            # Set current user in request context
            g.current_user = API_KEYS[api_key]
            return f(*args, **kwargs)
        return decorated_function
    
    def require_jwt(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token or not token.startswith('Bearer '):
                return jsonify({"error": "Invalid or missing token"}), 401
            
            try:
                token = token.split(' ')[1]
                payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
                g.current_user = payload
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
                
            return f(*args, **kwargs)
        return decorated_function
    
    # API key management endpoints
    @app.route('/api/v1/auth/register', methods=['POST'])
    @limiter.limit("10 per hour")
    def register_api_key():
        data = request.json
        if not data or 'email' not in data or 'name' not in data:
            return jsonify({"error": "Email and name are required"}), 400
        
        # Generate API key
        api_key = str(uuid.uuid4())
        API_KEYS[api_key] = {
            "id": str(uuid.uuid4()),
            "email": data['email'],
            "name": data['name'],
            "created_at": time.time(),
            "tier": "standard"
        }
        
        return jsonify({
            "api_key": api_key,
            "user": API_KEYS[api_key]
        })
    
    @app.route('/api/v1/auth/login', methods=['POST'])
    @limiter.limit("20 per hour")
    def login():
        data = request.json
        if not data or 'api_key' not in data:
            return jsonify({"error": "API key is required"}), 400
        
        api_key = data['api_key']
        if api_key not in API_KEYS:
            return jsonify({"error": "Invalid API key"}), 401
        
        # Generate JWT token
        payload = {
            **API_KEYS[api_key],
            "exp": datetime.utcnow().timestamp() + app.config['JWT_EXPIRATION']
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            "token": token,
            "expires_in": app.config['JWT_EXPIRATION'],
            "user": API_KEYS[api_key]
        })
    
    # Mining operations endpoints
    @app.route('/api/v1/operations', methods=['GET'])
    @require_api_key
    def get_operations():
        limit = request.args.get('limit', default=10, type=int)
        location = request.args.get('location')
        
        operations = g.data_collector.get_mining_operations()
        
        if location:
            operations = [op for op in operations if op.get('location') == location]
            
        return jsonify({
            "operations": operations[:limit]
        })
    
    @app.route('/api/v1/operations/<operation_id>', methods=['GET'])
    @require_api_key
    def get_operation(operation_id):
        operation = g.data_collector.get_mining_operation(operation_id)
        if not operation:
            return jsonify({"error": "Operation not found"}), 404
            
        return jsonify(operation)
    
    @app.route('/api/v1/operations/<operation_id>/score', methods=['GET'])
    @require_api_key
    def get_operation_score(operation_id):
        operation = g.data_collector.get_mining_operation(operation_id)
        if not operation:
            return jsonify({"error": "Operation not found"}), 404
            
        carbon_data = g.data_collector.get_carbon_data(operation_id)
        score_result = g.scorer.score_operation(operation, carbon_data)
        
        return jsonify(score_result)
    
    @app.route('/api/v1/operations/<operation_id>/optimize', methods=['GET'])
    @require_api_key
    def get_operation_optimization(operation_id):
        """
        Get optimization recommendations for a mining operation.
        
        This endpoint provides AI-powered recommendations for hardware upgrades,
        energy source changes, and cooling system improvements with ROI calculations.
        """
        operation = g.data_collector.get_mining_operation(operation_id)
        if not operation:
            return jsonify({"error": "Operation not found"}), 404
            
        carbon_data = g.data_collector.get_carbon_data(operation_id)
        recommendations = g.advisor.generate_recommendations(operation, carbon_data)
        
        return jsonify(recommendations)
    
    # Carbon verification endpoints
    @app.route('/api/v1/verify/carbon', methods=['POST'])
    @require_api_key
    def verify_carbon_data():
        data = request.json
        if not data or 'operation_id' not in data:
            return jsonify({"error": "Operation ID is required"}), 400
            
        operation_id = data['operation_id']
        operation = g.data_collector.get_mining_operation(operation_id)
        if not operation:
            return jsonify({"error": "Operation not found"}), 404
            
        carbon_data = g.data_collector.get_carbon_data(operation_id)
        
        # Generate proving key
        proving_key = g.verifier.generate_proving_key()
        
        # Create carbon emissions proof
        proof = g.verifier.create_carbon_emissions_proof(operation, carbon_data, proving_key)
        
        # Verify the proof
        is_valid = g.verifier.verify_proof(proof)
        
        return jsonify({
            "operation_id": operation_id,
            "is_valid": is_valid,
            "proof_id": proof.get("data_hash"),
            "public_inputs": proof.get("public_inputs", {})
        })
    
    @app.route('/api/v1/verify/proofs/<proof_id>', methods=['GET'])
    @require_api_key
    def get_proof(proof_id):
        proof = g.verifier.get_verified_proof(proof_id)
        if not proof:
            return jsonify({"error": "Proof not found"}), 404
            
        return jsonify(proof)
    
    # Token and rewards endpoints
    @app.route('/api/v1/tokens/balance/<address>', methods=['GET'])
    @require_api_key
    def get_token_balance(address):
        balance = g.eco_token.get_token_balance(address)
        badges = g.eco_token.get_nft_badges(address)
        
        return jsonify({
            "address": address,
            "balance": balance,
            "badges": badges
        })
    
    @app.route('/api/v1/staking/stats', methods=['GET'])
    @require_api_key
    def get_staking_stats():
        stats = g.eco_staking.get_staking_stats()
        return jsonify(stats)
    
    @app.route('/api/v1/staking/stakes/<address>', methods=['GET'])
    @require_api_key
    def get_active_stakes(address):
        stakes = g.eco_staking.get_active_stakes(address)
        return jsonify({
            "address": address,
            "active_stakes": stakes
        })
    
    # Governance endpoints
    @app.route('/api/v1/governance/proposals', methods=['GET'])
    @require_api_key
    def get_proposals():
        proposals = g.eco_governance.get_all_proposals()
        return jsonify({
            "proposals": proposals
        })
    
    @app.route('/api/v1/governance/proposals/<int:proposal_id>', methods=['GET'])
    @require_api_key
    def get_proposal(proposal_id):
        try:
            proposal = g.eco_governance.get_proposal(proposal_id)
            votes = g.eco_governance.get_votes(proposal_id)
            
            return jsonify({
                "proposal": proposal,
                "votes": votes
            })
        except ValueError:
            return jsonify({"error": "Proposal not found"}), 404
    
    # Data provider endpoints
    @app.route('/api/v1/data-provider/submit', methods=['POST'])
    @require_jwt
    def submit_data():
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # This would integrate with the data provider network in a real implementation
        return jsonify({
            "success": True,
            "submission_id": str(uuid.uuid4()),
            "timestamp": time.time()
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 
 
 