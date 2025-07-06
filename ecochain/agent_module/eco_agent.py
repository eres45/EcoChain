import os
import json
import time
from typing import Dict, List, Optional
import logging
from datetime import datetime

from ecochain.data_module.data_collector import DataCollector
from ecochain.analysis_module.sustainability_scorer import SustainabilityScorer
from ecochain.reward_module.eco_token import EcoToken

logger = logging.getLogger(__name__)

class EcoAgent:
    """
    Main agent class for the EcoChain Guardian system.
    
    This class orchestrates the entire workflow:
    1. Data collection from mining operations
    2. Sustainability analysis and scoring
    3. Reward distribution to eco-friendly miners
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the EcoChain Guardian agent.
        
        Args:
            config_path: Path to configuration file.
        """
        self.config = {}
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        
        # Agent settings
        self.analysis_interval = self.config.get('analysis_interval_seconds', 3600)  # Default: 1 hour
        self.reward_interval = self.config.get('reward_interval_seconds', 86400)  # Default: 1 day
        self.min_score_for_reward = self.config.get('min_score_for_reward', 30)
        self.badge_tiers = self.config.get('badge_tiers', {
            "Platinum": 90,
            "Gold": 75,
            "Silver": 60,
            "Bronze": 45,
            "Standard": 30
        })
        
        # Storage for scoring history
        self.score_history = {}
        self.last_analysis_time = 0
        self.last_reward_time = 0
        
        # Initialize components
        self.data_collector = DataCollector(config_path)
        self.sustainability_scorer = SustainabilityScorer()
        self.eco_token = EcoToken(config_path)
    
    def run(self, single_iteration: bool = False) -> None:
        """
        Run the agent's main loop.
        
        Args:
            single_iteration: If True, run only one iteration instead of a continuous loop.
        """
        logger.info("Starting EcoChain Guardian Agent")
        
        try:
            # Deploy contracts if needed (in real implementation)
            # self.eco_token.deploy_contracts()
            
            while True:
                current_time = time.time()
                
                # Run analysis if it's time
                if current_time - self.last_analysis_time >= self.analysis_interval:
                    self.run_analysis_cycle()
                    self.last_analysis_time = current_time
                
                # Distribute rewards if it's time
                if current_time - self.last_reward_time >= self.reward_interval:
                    self.distribute_rewards()
                    self.last_reward_time = current_time
                
                if single_iteration:
                    break
                
                # Sleep to avoid high CPU usage
                time.sleep(10)
                
        except KeyboardInterrupt:
            logger.info("Agent stopped by user")
        except Exception as e:
            logger.error(f"Error in agent main loop: {str(e)}")
    
    def run_analysis_cycle(self) -> List[Dict]:
        """
        Run a complete analysis cycle: collect data and score mining operations.
        
        Returns:
            List of sustainability score results.
        """
        logger.info("Running analysis cycle")
        
        try:
            # 1. Collect mining operations data
            mining_operations = self.data_collector.get_mining_operations()
            logger.info(f"Collected data for {len(mining_operations)} mining operations")
            
            # 2. Collect carbon footprint data for each operation
            carbon_data_list = []
            for operation in mining_operations:
                carbon_data = self.data_collector.get_carbon_data(operation["id"])
                carbon_data_list.append(carbon_data)
            
            # 3. Score each operation's sustainability
            scores = self.sustainability_scorer.score_multiple_operations(
                mining_operations, carbon_data_list
            )
            
            # 4. Store scores in history
            timestamp = datetime.now().isoformat()
            for score in scores:
                op_id = score["operation_id"]
                if op_id not in self.score_history:
                    self.score_history[op_id] = []
                
                # Store the score with timestamp
                self.score_history[op_id].append({
                    "timestamp": timestamp,
                    "score": score["sustainability_score"],
                    "tier": score["sustainability_tier"]
                })
            
            logger.info(f"Completed analysis of {len(scores)} mining operations")
            return scores
            
        except Exception as e:
            logger.error(f"Error in analysis cycle: {str(e)}")
            return []
    
    def distribute_rewards(self) -> List[Dict]:
        """
        Distribute rewards to miners based on their sustainability scores.
        
        Returns:
            List of reward distribution results.
        """
        logger.info("Distributing rewards to eco-friendly miners")
        
        try:
            # 1. Collect mining operations data to get wallet addresses
            mining_operations = self.data_collector.get_mining_operations()
            
            # Create a map of operation IDs to wallet addresses
            wallet_map = {
                op["id"]: op["wallet_address"]
                for op in mining_operations
                if "wallet_address" in op
            }
            
            reward_results = []
            
            # 2. For each operation with a recent score
            for op_id, history in self.score_history.items():
                if not history:
                    continue
                
                # Get the most recent score
                latest_score = history[-1]
                score_value = latest_score["score"]
                tier = latest_score["tier"]
                
                # Skip if score is below minimum
                if score_value < self.min_score_for_reward:
                    continue
                
                # Skip if no wallet address available
                if op_id not in wallet_map:
                    logger.warning(f"No wallet address found for operation {op_id}")
                    continue
                
                wallet_address = wallet_map[op_id]
                
                # 3. Update score in smart contract
                update_result = self.eco_token.update_miner_score(wallet_address, score_value)
                
                # 4. Mint reward tokens based on score
                if update_result["success"]:
                    reward_result = self.eco_token.mint_reward(wallet_address, score_value)
                    reward_results.append(reward_result)
                
                # 5. Award badge NFT if eligible for tier
                for tier_name, min_score in self.badge_tiers.items():
                    if score_value >= min_score and tier == tier_name:
                        badge_result = self.eco_token.award_badge(wallet_address, tier_name)
                        # In a real implementation, we could track badge results
            
            logger.info(f"Distributed rewards to {len(reward_results)} miners")
            return reward_results
            
        except Exception as e:
            logger.error(f"Error distributing rewards: {str(e)}")
            return []
    
    def get_operation_history(self, operation_id: str) -> List[Dict]:
        """
        Get the scoring history for a specific mining operation.
        
        Args:
            operation_id: ID of the mining operation.
            
        Returns:
            List of historical score records.
        """
        return self.score_history.get(operation_id, [])
    
    def get_latest_scores(self) -> List[Dict]:
        """
        Get the latest sustainability scores for all operations.
        
        Returns:
            List of dictionaries with the latest score for each operation.
        """
        latest_scores = []
        
        for op_id, history in self.score_history.items():
            if history:
                # Get the latest score record
                latest = history[-1].copy()
                latest["operation_id"] = op_id
                latest_scores.append(latest)
        
        return latest_scores
    
    def get_top_performers(self, limit: int = 10) -> List[Dict]:
        """
        Get the top performing mining operations by sustainability score.
        
        Args:
            limit: Maximum number of operations to return.
            
        Returns:
            List of top performers with their latest scores.
        """
        latest_scores = self.get_latest_scores()
        
        # Sort by score in descending order
        sorted_scores = sorted(
            latest_scores,
            key=lambda x: x["score"],
            reverse=True
        )
        
        return sorted_scores[:limit] 