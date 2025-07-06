"""
Automated Smart Contract Manager for EcoChain Guardian

This module provides automated reward distribution and smart contract interaction
for the EcoChain Guardian platform.
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
import asyncio
from datetime import datetime, timedelta

from ecochain.reward_module.eco_token import EcoToken
from ecochain.blockchain.chain_adapter import ChainAdapter
from ecochain.blockchain.ethereum import EthereumAdapter
from ecochain.blockchain.polygon import PolygonAdapter
from ecochain.blockchain.solana import SolanaAdapter

logger = logging.getLogger(__name__)

# Smart contract for automated reward distribution
AUTO_REWARD_CONTRACT = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract AutoRewardDistributor is Ownable {
    // EcoToken contract
    IERC20 public ecoToken;
    
    // Minimum time between reward distributions for a single miner
    uint256 public minDistributionInterval = 86400; // 24 hours
    
    // Mapping to track last distribution time for each miner
    mapping(address => uint256) public lastDistributionTime;
    
    // Mapping to track miner sustainability scores
    mapping(address => uint256) public minerScores;
    
    // Whitelisted callers allowed to trigger distributions
    mapping(address => bool) public whitelistedCallers;
    
    // Base reward amount
    uint256 public baseReward = 100 * 10**18; // 100 tokens with 18 decimals
    
    // Events
    event RewardDistributed(address indexed miner, uint256 amount, uint256 score);
    event ScoreUpdated(address indexed miner, uint256 score);
    event WhitelistUpdated(address indexed caller, bool isWhitelisted);
    event ParameterUpdated(string parameterName, uint256 oldValue, uint256 newValue);
    
    /**
     * @dev Initialize the contract with the EcoToken address
     * @param tokenAddress Address of the EcoToken contract
     */
    constructor(address tokenAddress) {
        require(tokenAddress != address(0), "Invalid token address");
        ecoToken = IERC20(tokenAddress);
        whitelistedCallers[msg.sender] = true;
    }
    
    /**
     * @dev Modifier to check if caller is whitelisted
     */
    modifier onlyWhitelisted() {
        require(whitelistedCallers[msg.sender] || msg.sender == owner(), "Caller not whitelisted");
        _;
    }
    
    /**
     * @dev Set whitelist status for a caller
     * @param caller Address to whitelist or unwhitelist
     * @param isWhitelisted Whether the address should be whitelisted
     */
    function setWhitelistedCaller(address caller, bool isWhitelisted) public onlyOwner {
        whitelistedCallers[caller] = isWhitelisted;
        emit WhitelistUpdated(caller, isWhitelisted);
    }
    
    /**
     * @dev Set the minimum time between distributions
     * @param newInterval New minimum interval in seconds
     */
    function setMinDistributionInterval(uint256 newInterval) public onlyOwner {
        uint256 oldInterval = minDistributionInterval;
        minDistributionInterval = newInterval;
        emit ParameterUpdated("minDistributionInterval", oldInterval, newInterval);
    }
    
    /**
     * @dev Set the base reward amount
     * @param newBaseReward New base reward amount
     */
    function setBaseReward(uint256 newBaseReward) public onlyOwner {
        uint256 oldBaseReward = baseReward;
        baseReward = newBaseReward;
        emit ParameterUpdated("baseReward", oldBaseReward, newBaseReward);
    }
    
    /**
     * @dev Update a miner's sustainability score
     * @param miner The address of the miner
     * @param score The sustainability score (0-100)
     */
    function updateScore(address miner, uint256 score) public onlyWhitelisted {
        require(score <= 100, "Score must be between 0 and 100");
        minerScores[miner] = score;
        emit ScoreUpdated(miner, score);
    }
    
    /**
     * @dev Batch update multiple miners' scores
     * @param miners Array of miner addresses
     * @param scores Array of sustainability scores
     */
    function batchUpdateScores(address[] memory miners, uint256[] memory scores) public onlyWhitelisted {
        require(miners.length == scores.length, "Arrays length mismatch");
        
        for (uint i = 0; i < miners.length; i++) {
            require(scores[i] <= 100, "Score must be between 0 and 100");
            minerScores[miners[i]] = scores[i];
            emit ScoreUpdated(miners[i], scores[i]);
        }
    }
    
    /**
     * @dev Distribute rewards to a miner based on their score
     * @param miner The address of the miner
     * @return Amount of tokens distributed
     */
    function distributeReward(address miner) public onlyWhitelisted returns (uint256) {
        uint256 score = minerScores[miner];
        require(score > 0, "Miner has no sustainability score");
        
        // Check if minimum time has passed since last distribution
        require(
            block.timestamp >= lastDistributionTime[miner] + minDistributionInterval,
            "Distribution interval not met"
        );
        
        // Calculate reward amount based on score
        uint256 scoreMultiplier = (score * score) / 100; // Square of score / 100 for non-linear scaling
        uint256 rewardAmount = (baseReward * scoreMultiplier) / 100;
        
        // Update last distribution time
        lastDistributionTime[miner] = block.timestamp;
        
        // Transfer tokens from contract to miner
        require(
            ecoToken.transfer(miner, rewardAmount),
            "Token transfer failed"
        );
        
        emit RewardDistributed(miner, rewardAmount, score);
        return rewardAmount;
    }
    
    /**
     * @dev Batch distribute rewards to multiple miners
     * @param miners Array of miner addresses
     * @return Array of distributed amounts
     */
    function batchDistributeRewards(address[] memory miners) public onlyWhitelisted returns (uint256[] memory) {
        uint256[] memory amounts = new uint256[](miners.length);
        
        for (uint i = 0; i < miners.length; i++) {
            try this.distributeReward(miners[i]) returns (uint256 amount) {
                amounts[i] = amount;
            } catch {
                amounts[i] = 0; // Distribution failed for this miner
            }
        }
        
        return amounts;
    }
    
    /**
     * @dev Check if a miner is eligible for reward distribution
     * @param miner The address of the miner
     * @return Whether the miner is eligible for reward distribution
     */
    function isEligibleForReward(address miner) public view returns (bool) {
        return minerScores[miner] > 0 && 
               block.timestamp >= lastDistributionTime[miner] + minDistributionInterval;
    }
    
    /**
     * @dev Get eligible miners from a list
     * @param miners Array of miner addresses to check
     * @return Array of eligible miner addresses
     */
    function getEligibleMiners(address[] memory miners) public view returns (address[] memory) {
        uint256 eligibleCount = 0;
        
        // First pass: count eligible miners
        for (uint i = 0; i < miners.length; i++) {
            if (isEligibleForReward(miners[i])) {
                eligibleCount++;
            }
        }
        
        // Create result array with exact size
        address[] memory eligibleMiners = new address[](eligibleCount);
        uint256 resultIndex = 0;
        
        // Second pass: populate result array
        for (uint i = 0; i < miners.length; i++) {
            if (isEligibleForReward(miners[i])) {
                eligibleMiners[resultIndex] = miners[i];
                resultIndex++;
            }
        }
        
        return eligibleMiners;
    }
    
    /**
     * @dev Withdraw accidentally sent tokens
     * @param tokenAddress Address of the token to withdraw
     * @param amount Amount to withdraw
     */
    function withdrawTokens(address tokenAddress, uint256 amount) public onlyOwner {
        IERC20 token = IERC20(tokenAddress);
        require(
            token.transfer(owner(), amount),
            "Token transfer failed"
        );
    }
}
"""

class DistributionSchedule:
    """
    Defines a schedule for automated reward distribution.
    """
    
    FREQUENCY_DAILY = "daily"
    FREQUENCY_WEEKLY = "weekly"
    FREQUENCY_MONTHLY = "monthly"
    
    def __init__(self, frequency: str, start_time: Optional[int] = None,
                 eligible_miners: Optional[List[str]] = None):
        """
        Initialize a distribution schedule.
        
        Args:
            frequency: Distribution frequency (daily, weekly, monthly)
            start_time: Start timestamp for the schedule (default: now)
            eligible_miners: List of miner addresses eligible for this schedule
        """
        self.frequency = frequency
        self.start_time = start_time or int(time.time())
        self.eligible_miners = eligible_miners or []
        
        # Calculate next run time
        self.next_run_time = self._calculate_next_run_time()
    
    def _calculate_next_run_time(self) -> int:
        """
        Calculate the next scheduled run time based on frequency.
        
        Returns:
            Timestamp for next run
        """
        current_time = datetime.fromtimestamp(self.start_time)
        
        if self.frequency == self.FREQUENCY_DAILY:
            # Next day at the same time
            next_time = current_time + timedelta(days=1)
        elif self.frequency == self.FREQUENCY_WEEKLY:
            # Next week at the same time
            next_time = current_time + timedelta(weeks=1)
        elif self.frequency == self.FREQUENCY_MONTHLY:
            # Next month at the same time
            # Handle month rollover correctly
            if current_time.month == 12:
                next_time = current_time.replace(year=current_time.year + 1, month=1)
            else:
                next_time = current_time.replace(month=current_time.month + 1)
        else:
            # Default to daily
            next_time = current_time + timedelta(days=1)
            
        return int(next_time.timestamp())
    
    def is_due(self) -> bool:
        """
        Check if the schedule is due to run.
        
        Returns:
            True if the schedule should be run now, False otherwise
        """
        return int(time.time()) >= self.next_run_time
    
    def update_next_run_time(self):
        """Update the next run time after this schedule has been executed."""
        self.start_time = self.next_run_time
        self.next_run_time = self._calculate_next_run_time()


class AutoContractManager:
    """
    Manages automated smart contract interactions for reward distribution.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the auto contract manager.
        
        Args:
            config_path: Path to the configuration file.
        """
        self.config = {}
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        
        # Initialize EcoToken handler
        self.eco_token = EcoToken(config_path)
        
        # Initialize blockchain adapter
        chain_name = self.config.get('blockchain', 'ethereum')
        if chain_name.lower() == 'ethereum':
            self.chain_adapter = EthereumAdapter(self.config.get('ethereum_config', {}))
        elif chain_name.lower() == 'polygon':
            self.chain_adapter = PolygonAdapter(self.config.get('polygon_config', {}))
        elif chain_name.lower() == 'solana':
            self.chain_adapter = SolanaAdapter(self.config.get('solana_config', {}))
        else:
            # Default to Ethereum
            self.chain_adapter = EthereumAdapter(self.config.get('ethereum_config', {}))
        
        # Connect to blockchain
        self.chain_adapter.connect()
        
        # Contract addresses
        self.token_address = self.config.get('contracts', {}).get('token_address', '')
        self.auto_reward_address = self.config.get('contracts', {}).get('auto_reward_address', '')
        
        # Distribution schedules
        self.distribution_schedules = []
        self._load_schedules_from_config()
        
        # Flag to control background task
        self.should_run = False
    
    def _load_schedules_from_config(self):
        """Load distribution schedules from config."""
        schedules_config = self.config.get('distribution_schedules', [])
        
        for schedule_config in schedules_config:
            frequency = schedule_config.get('frequency', DistributionSchedule.FREQUENCY_DAILY)
            start_time = schedule_config.get('start_time')
            eligible_miners = schedule_config.get('eligible_miners', [])
            
            schedule = DistributionSchedule(
                frequency=frequency,
                start_time=start_time,
                eligible_miners=eligible_miners
            )
            
            self.distribution_schedules.append(schedule)
    
    def deploy_auto_reward_contract(self) -> Dict:
        """
        Deploy the auto reward distributor contract.
        
        Returns:
            Dictionary with deployment information.
        """
        if not self.token_address:
            logger.error("Token address not set. Please deploy the token contract first.")
            return {"success": False, "error": "Token address not set"}
        
        # Prepare contract constructor arguments
        constructor_args = [self.token_address]
        
        try:
            # Compile the contract (simulated)
            logger.info("Compiling AutoRewardDistributor contract...")
            contract_bytecode = "0x" + os.urandom(1000).hex()  # Simulated bytecode
            contract_abi = []  # Simulated ABI
            
            # Deploy the contract
            logger.info(f"Deploying AutoRewardDistributor contract...")
            deployment_result = self.chain_adapter.deploy_contract(
                contract_name="AutoRewardDistributor",
                contract_bytecode=contract_bytecode,
                abi=contract_abi,
                constructor_args=constructor_args
            )
            
            if deployment_result.get("success", False):
                contract_address = deployment_result["contract_address"]
                self.auto_reward_address = contract_address
                
                # Update config
                if 'contracts' not in self.config:
                    self.config['contracts'] = {}
                self.config['contracts']['auto_reward_address'] = contract_address
                
                # Save updated config if path is available
                if self.config.get('config_path'):
                    with open(self.config['config_path'], 'w') as f:
                        json.dump(self.config, f, indent=2)
                
                logger.info(f"AutoRewardDistributor deployed at {contract_address}")
                return {
                    "success": True,
                    "contract_address": contract_address,
                    "transaction_hash": deployment_result.get("transaction_hash")
                }
            else:
                logger.error(f"Failed to deploy AutoRewardDistributor: {deployment_result.get('error')}")
                return {
                    "success": False,
                    "error": deployment_result.get("error", "Unknown deployment error")
                }
        
        except Exception as e:
            logger.error(f"Error deploying AutoRewardDistributor: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def update_miner_score(self, miner_address: str, score: float) -> Dict:
        """
        Update a miner's sustainability score in the contract.
        
        Args:
            miner_address: Blockchain address of the miner.
            score: Sustainability score (0-100).
            
        Returns:
            Dictionary with transaction information.
        """
        if not self.auto_reward_address:
            logger.error("Auto reward contract address not set.")
            return {"success": False, "error": "Contract address not set"}
        
        try:
            # Convert score to integer
            score_int = int(score)
            if score_int < 0:
                score_int = 0
            elif score_int > 100:
                score_int = 100
                
            # Call the contract function
            tx_result = self.chain_adapter.send_transaction(
                contract_address=self.auto_reward_address,
                abi=[],  # Simulated ABI
                function_name="updateScore",
                args=[miner_address, score_int],
                private_key=self.config.get('private_key')
            )
            
            if tx_result.get("success", False):
                logger.info(f"Updated score for miner {miner_address} to {score_int}")
                return {
                    "success": True,
                    "transaction_hash": tx_result.get("transaction_hash"),
                    "miner_address": miner_address,
                    "score": score_int
                }
            else:
                logger.error(f"Failed to update score: {tx_result.get('error')}")
                return {
                    "success": False,
                    "error": tx_result.get("error", "Unknown transaction error")
                }
                
        except Exception as e:
            logger.error(f"Error updating miner score: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def batch_update_scores(self, miners: List[str], scores: List[float]) -> Dict:
        """
        Update multiple miners' scores in a single transaction.
        
        Args:
            miners: List of miner addresses.
            scores: List of sustainability scores.
            
        Returns:
            Dictionary with transaction information.
        """
        if not self.auto_reward_address:
            logger.error("Auto reward contract address not set.")
            return {"success": False, "error": "Contract address not set"}
        
        if len(miners) != len(scores):
            logger.error("Length mismatch between miners and scores arrays.")
            return {"success": False, "error": "Length mismatch between arrays"}
        
        try:
            # Convert scores to integers
            scores_int = [int(min(max(s, 0), 100)) for s in scores]
                
            # Call the contract function
            tx_result = self.chain_adapter.send_transaction(
                contract_address=self.auto_reward_address,
                abi=[],  # Simulated ABI
                function_name="batchUpdateScores",
                args=[miners, scores_int],
                private_key=self.config.get('private_key')
            )
            
            if tx_result.get("success", False):
                logger.info(f"Updated scores for {len(miners)} miners in batch transaction")
                return {
                    "success": True,
                    "transaction_hash": tx_result.get("transaction_hash"),
                    "miners_count": len(miners)
                }
            else:
                logger.error(f"Failed to update scores in batch: {tx_result.get('error')}")
                return {
                    "success": False,
                    "error": tx_result.get("error", "Unknown transaction error")
                }
                
        except Exception as e:
            logger.error(f"Error updating miner scores in batch: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def distribute_reward(self, miner_address: str) -> Dict:
        """
        Distribute rewards to a single miner based on their score.
        
        Args:
            miner_address: Blockchain address of the miner.
            
        Returns:
            Dictionary with transaction information.
        """
        if not self.auto_reward_address:
            logger.error("Auto reward contract address not set.")
            return {"success": False, "error": "Contract address not set"}
        
        try:
            # Call the contract function
            tx_result = self.chain_adapter.send_transaction(
                contract_address=self.auto_reward_address,
                abi=[],  # Simulated ABI
                function_name="distributeReward",
                args=[miner_address],
                private_key=self.config.get('private_key')
            )
            
            if tx_result.get("success", False):
                # Get reward amount from transaction receipt or events (simulated)
                reward_amount = int.from_bytes(os.urandom(4), byteorder='big') % 10000
                
                logger.info(f"Distributed {reward_amount} tokens to miner {miner_address}")
                return {
                    "success": True,
                    "transaction_hash": tx_result.get("transaction_hash"),
                    "miner_address": miner_address,
                    "reward_amount": reward_amount
                }
            else:
                logger.error(f"Failed to distribute reward: {tx_result.get('error')}")
                return {
                    "success": False,
                    "error": tx_result.get("error", "Unknown transaction error")
                }
                
        except Exception as e:
            logger.error(f"Error distributing reward: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def batch_distribute_rewards(self, miner_addresses: List[str]) -> Dict:
        """
        Distribute rewards to multiple miners in a single transaction.
        
        Args:
            miner_addresses: List of miner addresses.
            
        Returns:
            Dictionary with transaction information.
        """
        if not self.auto_reward_address:
            logger.error("Auto reward contract address not set.")
            return {"success": False, "error": "Contract address not set"}
        
        try:
            # Call the contract function
            tx_result = self.chain_adapter.send_transaction(
                contract_address=self.auto_reward_address,
                abi=[],  # Simulated ABI
                function_name="batchDistributeRewards",
                args=[miner_addresses],
                private_key=self.config.get('private_key')
            )
            
            if tx_result.get("success", False):
                # Get reward amounts from transaction receipt or events (simulated)
                reward_amounts = [int.from_bytes(os.urandom(4), byteorder='big') % 10000 
                                 for _ in miner_addresses]
                
                total_distributed = sum(reward_amounts)
                miners_count = len(miner_addresses)
                
                logger.info(f"Distributed a total of {total_distributed} tokens to {miners_count} miners")
                return {
                    "success": True,
                    "transaction_hash": tx_result.get("transaction_hash"),
                    "miners_count": miners_count,
                    "total_distributed": total_distributed,
                    "reward_amounts": dict(zip(miner_addresses, reward_amounts))
                }
            else:
                logger.error(f"Failed to distribute rewards in batch: {tx_result.get('error')}")
                return {
                    "success": False,
                    "error": tx_result.get("error", "Unknown transaction error")
                }
                
        except Exception as e:
            logger.error(f"Error distributing rewards in batch: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_eligible_miners(self, candidates: Optional[List[str]] = None) -> List[str]:
        """
        Get miners eligible for reward distribution.
        
        Args:
            candidates: Optional list of candidate miner addresses to check.
                       If not provided, all miners with scores will be checked.
            
        Returns:
            List of eligible miner addresses.
        """
        if not self.auto_reward_address:
            logger.error("Auto reward contract address not set.")
            return []
        
        try:
            if candidates:
                # Check specific candidates
                result = self.chain_adapter.call_contract(
                    contract_address=self.auto_reward_address,
                    abi=[],  # Simulated ABI
                    function_name="getEligibleMiners",
                    args=[candidates]
                )
                
                return result if result else []
            else:
                # Simulation: return random subset of miners
                # In a real implementation, we would query the blockchain
                # for all miners with scores and check eligibility
                
                # Get some random addresses
                addresses = [
                    f"0x{os.urandom(20).hex()}" for _ in range(10)
                ]
                
                # Filter to simulate eligible miners
                eligible = [addr for addr in addresses if int.from_bytes(addr.encode()[-1:], byteorder='big') % 2 == 0]
                
                return eligible
                
        except Exception as e:
            logger.error(f"Error getting eligible miners: {str(e)}")
            return []
    
    def set_distribution_schedule(self, frequency: str, eligible_miners: Optional[List[str]] = None,
                                  start_time: Optional[int] = None) -> Dict:
        """
        Set a new distribution schedule.
        
        Args:
            frequency: Distribution frequency (daily, weekly, monthly)
            eligible_miners: List of miner addresses eligible for this schedule
            start_time: Start timestamp for the schedule
            
        Returns:
            Dictionary with schedule information.
        """
        try:
            schedule = DistributionSchedule(
                frequency=frequency,
                start_time=start_time,
                eligible_miners=eligible_miners or []
            )
            
            self.distribution_schedules.append(schedule)
            
            logger.info(f"Added new {frequency} distribution schedule starting at {schedule.start_time}")
            return {
                "success": True,
                "schedule_id": len(self.distribution_schedules) - 1,
                "frequency": frequency,
                "start_time": schedule.start_time,
                "next_run_time": schedule.next_run_time,
                "eligible_miners_count": len(schedule.eligible_miners)
            }
                
        except Exception as e:
            logger.error(f"Error setting distribution schedule: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_distribution_schedules(self) -> List[Dict]:
        """
        Get all distribution schedules.
        
        Returns:
            List of schedule dictionaries.
        """
        return [
            {
                "id": i,
                "frequency": s.frequency,
                "start_time": s.start_time,
                "next_run_time": s.next_run_time,
                "next_run_at": datetime.fromtimestamp(s.next_run_time).strftime('%Y-%m-%d %H:%M:%S'),
                "eligible_miners_count": len(s.eligible_miners)
            }
            for i, s in enumerate(self.distribution_schedules)
        ]
    
    def remove_distribution_schedule(self, schedule_id: int) -> Dict:
        """
        Remove a distribution schedule.
        
        Args:
            schedule_id: ID of the schedule to remove.
            
        Returns:
            Dictionary with operation result.
        """
        try:
            if 0 <= schedule_id < len(self.distribution_schedules):
                removed_schedule = self.distribution_schedules.pop(schedule_id)
                
                logger.info(f"Removed {removed_schedule.frequency} distribution schedule")
                return {
                    "success": True,
                    "frequency": removed_schedule.frequency,
                    "start_time": removed_schedule.start_time
                }
            else:
                logger.error(f"Invalid schedule ID: {schedule_id}")
                return {"success": False, "error": f"Invalid schedule ID: {schedule_id}"}
                
        except Exception as e:
            logger.error(f"Error removing distribution schedule: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def run_scheduled_distributions(self):
        """
        Run scheduled distributions in the background.
        
        This method should be called in a separate thread or task.
        """
        self.should_run = True
        
        logger.info("Starting automated reward distribution scheduler")
        
        while self.should_run:
            for i, schedule in enumerate(self.distribution_schedules):
                if schedule.is_due():
                    logger.info(f"Running scheduled distribution for schedule {i} ({schedule.frequency})")
                    
                    try:
                        # Get eligible miners
                        eligible_miners = schedule.eligible_miners
                        
                        if not eligible_miners:
                            # If no specific miners are set for this schedule, get all eligible miners
                            eligible_miners = self.get_eligible_miners()
                        
                        if eligible_miners:
                            # Distribute rewards
                            distribution_result = self.batch_distribute_rewards(eligible_miners)
                            
                            if distribution_result.get("success", False):
                                logger.info(f"Successfully distributed rewards to {distribution_result.get('miners_count', 0)} miners")
                            else:
                                logger.error(f"Failed to distribute rewards: {distribution_result.get('error')}")
                        else:
                            logger.info("No eligible miners found for this schedule")
                        
                        # Update next run time
                        schedule.update_next_run_time()
                        logger.info(f"Next run scheduled for {datetime.fromtimestamp(schedule.next_run_time)}")
                    
                    except Exception as e:
                        logger.error(f"Error during scheduled distribution: {str(e)}")
            
            # Sleep for a while before checking again
            await asyncio.sleep(60)  # Check every minute
    
    def start_scheduler(self):
        """Start the distribution scheduler in the background."""
        if not self.should_run:
            asyncio.create_task(self.run_scheduled_distributions())
    
    def stop_scheduler(self):
        """Stop the distribution scheduler."""
        self.should_run = False 
 
 