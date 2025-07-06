"""
Energy Metrics for Consensus Mechanisms

This module provides tools to analyze and compare energy consumption
across different blockchain consensus mechanisms.
"""

import logging
import json
import time
import math
import random
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import pandas as pd
import numpy as np

from ecochain.blockchain.chain_adapter import ChainAdapter

logger = logging.getLogger(__name__)

@dataclass
class ConsensusEnergyProfile:
    """Energy profile data for a consensus mechanism."""
    name: str
    energy_per_tx: float  # kWh per transaction
    energy_per_validator: float  # kWh per validator node
    energy_per_block: float  # kWh per block
    network_hashrate: Optional[float] = None  # Only for PoW networks (hash/s)
    stake_efficiency: Optional[float] = None  # Only for PoS networks (energy used per $ staked)
    annual_energy_consumption: Optional[float] = None  # kWh per year for the whole network
    carbon_intensity: Optional[float] = None  # kgCO2 per kWh
    scalability_factor: Optional[float] = None  # Energy increase per tx as network grows (1.0 = linear)
    notes: Optional[str] = None

# Reference profiles for different consensus mechanisms
# These are simplified estimates for demonstration purposes
# Real values would require detailed research and may vary over time
CONSENSUS_PROFILES = {
    "PoW": ConsensusEnergyProfile(
        name="Proof of Work",
        energy_per_tx=950.0,  # kWh per transaction (Bitcoin reference)
        energy_per_validator=6000.0,  # kWh per mining node per month
        energy_per_block=1725000.0,  # kWh per block
        network_hashrate=150e18,  # 150 EH/s (Bitcoin reference)
        annual_energy_consumption=130e9,  # 130 TWh per year
        carbon_intensity=0.5,  # Global average
        scalability_factor=1.2,  # Energy use grows superlinearly with adoption
        notes="Highest energy consumption, security based on computational work"
    ),
    
    "PoS": ConsensusEnergyProfile(
        name="Proof of Stake",
        energy_per_tx=0.03,  # kWh per transaction (Ethereum PoS reference)
        energy_per_validator=12.0,  # kWh per validator node per month
        energy_per_block=0.2,  # kWh per block
        stake_efficiency=0.0001,  # kWh per $ staked
        annual_energy_consumption=2.62e6,  # 2.62 GWh per year
        carbon_intensity=0.5,  # Global average
        scalability_factor=0.8,  # Energy use grows sublinearly with adoption
        notes="Very energy efficient, security based on economic stake"
    ),
    
    "PoH/PoS": ConsensusEnergyProfile(
        name="Proof of History with Proof of Stake",
        energy_per_tx=0.0001,  # kWh per transaction (Solana reference)
        energy_per_validator=15.0,  # kWh per validator node per month
        energy_per_block=0.001,  # kWh per block (Solana has very fast blocks)
        stake_efficiency=0.00005,  # kWh per $ staked
        annual_energy_consumption=1.12e6,  # 1.12 GWh per year
        carbon_intensity=0.5,  # Global average
        scalability_factor=0.7,  # Energy use grows sublinearly with adoption
        notes="Extremely energy efficient, uses timestamps for consensus"
    ),
    
    "PoA": ConsensusEnergyProfile(
        name="Proof of Authority",
        energy_per_tx=0.01,  # kWh per transaction
        energy_per_validator=10.0,  # kWh per validator node per month
        energy_per_block=0.05,  # kWh per block
        annual_energy_consumption=5.0e5,  # 500 MWh per year
        carbon_intensity=0.5,  # Global average
        scalability_factor=0.9,  # Energy use grows slightly sublinearly
        notes="Energy efficient, centralized validation by trusted authorities"
    ),
    
    "DPoS": ConsensusEnergyProfile(
        name="Delegated Proof of Stake",
        energy_per_tx=0.02,  # kWh per transaction
        energy_per_validator=14.0,  # kWh per validator node per month
        energy_per_block=0.1,  # kWh per block
        stake_efficiency=0.00008,  # kWh per $ staked
        annual_energy_consumption=1.0e6,  # 1 GWh per year
        carbon_intensity=0.5,  # Global average
        scalability_factor=0.8,  # Energy use grows sublinearly with adoption
        notes="Energy efficient, uses elected block producers"
    )
}

class ConsensusEnergyMetrics:
    """
    Class for analyzing and comparing energy metrics across consensus mechanisms.
    """
    
    def __init__(self):
        """Initialize the energy metrics analyzer."""
        self.profiles = CONSENSUS_PROFILES.copy()
        self.chain_data = {}  # Chain name -> energy data
    
    def add_chain(self, name: str, adapter: ChainAdapter) -> None:
        """
        Add a blockchain adapter to track its energy metrics.
        
        Args:
            name: Name of the chain.
            adapter: Chain adapter instance.
        """
        consensus = adapter.consensus_mechanism
        if consensus not in self.profiles:
            logger.warning(f"No energy profile for consensus mechanism: {consensus}")
            # Use PoS as default profile if unknown
            consensus = "PoS"
        
        chain_info = adapter.get_chain_info()
        
        # Collect chain-specific data
        self.chain_data[name] = {
            "name": name,
            "consensus": consensus,
            "profile": self.profiles[consensus],
            "chain_info": chain_info,
            "last_updated": time.time()
        }
        
        logger.info(f"Added {name} chain with {consensus} consensus for energy metrics")
    
    def update_chain_metrics(self, name: str, tx_count: int, active_validators: int = None) -> None:
        """
        Update energy metrics for a chain with current transaction volume and validator count.
        
        Args:
            name: Name of the chain.
            tx_count: Number of transactions per day.
            active_validators: Number of active validators.
        """
        if name not in self.chain_data:
            logger.error(f"Chain {name} not found in tracked chains")
            return
        
        chain = self.chain_data[name]
        
        # Update transaction count
        chain["tx_count"] = tx_count
        
        # Update validator count if provided
        if active_validators is not None:
            chain["active_validators"] = active_validators
        
        # Calculate daily energy usage
        profile = chain["profile"]
        daily_tx_energy = tx_count * profile.energy_per_tx
        
        # Calculate validator energy
        validator_count = chain.get("active_validators", 100)  # Default to 100 if not provided
        daily_validator_energy = validator_count * (profile.energy_per_validator / 30)  # Per day
        
        # Total energy usage
        total_daily_energy = daily_tx_energy + daily_validator_energy
        
        # Update metrics
        chain["daily_tx_energy"] = daily_tx_energy
        chain["daily_validator_energy"] = daily_validator_energy
        chain["total_daily_energy"] = total_daily_energy
        chain["daily_carbon"] = total_daily_energy * profile.carbon_intensity
        chain["last_updated"] = time.time()
        
        logger.info(f"Updated energy metrics for {name}: {total_daily_energy:.2f} kWh/day")
    
    def get_chain_metrics(self, name: str) -> Dict:
        """
        Get energy metrics for a specific chain.
        
        Args:
            name: Name of the chain.
            
        Returns:
            Dictionary with chain energy metrics.
        """
        if name not in self.chain_data:
            logger.error(f"Chain {name} not found in tracked chains")
            return {}
        
        chain = self.chain_data[name]
        profile = chain["profile"]
        
        return {
            "name": name,
            "consensus_mechanism": chain["consensus"],
            "energy_per_tx": profile.energy_per_tx,
            "daily_tx_energy": chain.get("daily_tx_energy", 0),
            "daily_validator_energy": chain.get("daily_validator_energy", 0),
            "total_daily_energy": chain.get("total_daily_energy", 0),
            "daily_carbon": chain.get("daily_carbon", 0),
            "energy_efficiency_score": self._calculate_efficiency_score(chain),
            "last_updated": chain["last_updated"]
        }
    
    def compare_chains(self, chain_names: List[str] = None) -> Dict:
        """
        Compare energy metrics across different chains.
        
        Args:
            chain_names: List of chain names to compare. If None, compare all.
            
        Returns:
            Dictionary with comparison results.
        """
        if chain_names is None:
            chain_names = list(self.chain_data.keys())
        
        # Filter to only include chains that exist in our data
        valid_chains = [name for name in chain_names if name in self.chain_data]
        
        if not valid_chains:
            logger.error("No valid chains found for comparison")
            return {"error": "No valid chains found for comparison"}
        
        # Calculate comparative metrics
        comparison = {
            "chains": [],
            "total_daily_energy": {},
            "energy_per_tx": {},
            "total_daily_carbon": {},
            "efficiency_score": {},
            "relative_efficiency": {}
        }
        
        # Get energy metrics for each chain
        for name in valid_chains:
            metrics = self.get_chain_metrics(name)
            comparison["chains"].append(name)
            comparison["total_daily_energy"][name] = metrics.get("total_daily_energy", 0)
            comparison["energy_per_tx"][name] = metrics.get("energy_per_tx", 0)
            comparison["total_daily_carbon"][name] = metrics.get("daily_carbon", 0)
            comparison["efficiency_score"][name] = metrics.get("energy_efficiency_score", 0)
        
        # Calculate relative efficiency (as percentage of the most efficient chain)
        min_energy_per_tx = min(comparison["energy_per_tx"].values())
        if min_energy_per_tx > 0:
            for name in valid_chains:
                energy_per_tx = comparison["energy_per_tx"][name]
                comparison["relative_efficiency"][name] = (min_energy_per_tx / energy_per_tx) * 100
        
        # Add summary
        comparison["summary"] = self._generate_comparison_summary(comparison)
        
        return comparison
    
    def _calculate_efficiency_score(self, chain: Dict) -> float:
        """
        Calculate an energy efficiency score for a chain.
        
        The score is on a scale of 0-100, where 100 is most efficient.
        
        Args:
            chain: Chain data dictionary.
            
        Returns:
            Energy efficiency score (0-100).
        """
        profile = chain["profile"]
        
        # Base score is primarily determined by energy per transaction
        # Using a log scale to handle the wide range of values
        base_score = max(0, 100 - 15 * math.log10(1 + profile.energy_per_tx * 1000))
        
        # Adjust for scalability
        scalability_adjustment = 0
        if profile.scalability_factor is not None:
            if profile.scalability_factor < 1.0:
                # Sublinear scaling is good
                scalability_adjustment = 10 * (1 - profile.scalability_factor)
            else:
                # Superlinear scaling is bad
                scalability_adjustment = -10 * (profile.scalability_factor - 1)
        
        # Final score
        score = min(100, max(0, base_score + scalability_adjustment))
        
        return score
    
    def _generate_comparison_summary(self, comparison: Dict) -> Dict:
        """
        Generate a summary of the comparison results.
        
        Args:
            comparison: Comparison results dictionary.
            
        Returns:
            Dictionary with summary information.
        """
        if not comparison["chains"]:
            return {"error": "No chains to compare"}
        
        # Find most and least efficient chains
        energy_per_tx = comparison["energy_per_tx"]
        most_efficient = min(energy_per_tx.items(), key=lambda x: x[1])
        least_efficient = max(energy_per_tx.items(), key=lambda x: x[1])
        
        # Calculate efficiency factor (how many times more efficient)
        if least_efficient[1] > 0:
            efficiency_factor = least_efficient[1] / most_efficient[1]
        else:
            efficiency_factor = float('inf')
        
        # Get total carbon impact
        total_carbon = sum(comparison["total_daily_carbon"].values())
        
        # Find consensus with best average efficiency
        consensus_efficiency = {}
        for name in comparison["chains"]:
            chain = self.chain_data[name]
            consensus = chain["consensus"]
            score = comparison["efficiency_score"][name]
            
            if consensus not in consensus_efficiency:
                consensus_efficiency[consensus] = []
            
            consensus_efficiency[consensus].append(score)
        
        # Calculate average score per consensus
        consensus_avg = {
            c: sum(scores) / len(scores)
            for c, scores in consensus_efficiency.items()
        }
        
        best_consensus = max(consensus_avg.items(), key=lambda x: x[1]) if consensus_avg else None
        
        return {
            "most_efficient_chain": most_efficient[0],
            "least_efficient_chain": least_efficient[0],
            "efficiency_factor": efficiency_factor,
            "total_daily_carbon": total_carbon,
            "best_consensus": best_consensus[0] if best_consensus else None,
            "best_consensus_score": best_consensus[1] if best_consensus else None
        }
    
    def get_consensus_profile(self, consensus: str) -> Dict:
        """
        Get the energy profile for a consensus mechanism.
        
        Args:
            consensus: Name of the consensus mechanism.
            
        Returns:
            Dictionary with energy profile.
        """
        if consensus not in self.profiles:
            logger.error(f"Consensus mechanism {consensus} not found")
            return {}
        
        profile = self.profiles[consensus]
        return {
            "name": profile.name,
            "energy_per_tx": profile.energy_per_tx,
            "energy_per_validator": profile.energy_per_validator,
            "energy_per_block": profile.energy_per_block,
            "network_hashrate": profile.network_hashrate,
            "stake_efficiency": profile.stake_efficiency,
            "annual_energy_consumption": profile.annual_energy_consumption,
            "carbon_intensity": profile.carbon_intensity,
            "scalability_factor": profile.scalability_factor,
            "notes": profile.notes
        }
    
    def simulate_transaction_growth(self, chain_name: str, growth_factor: float, 
                                   days: int = 365) -> Dict:
        """
        Simulate energy impact of transaction growth for a chain.
        
        Args:
            chain_name: Name of the chain.
            growth_factor: Daily growth factor (1.01 = 1% daily growth).
            days: Number of days to simulate.
            
        Returns:
            Dictionary with simulation results.
        """
        if chain_name not in self.chain_data:
            logger.error(f"Chain {chain_name} not found in tracked chains")
            return {"error": f"Chain {chain_name} not found"}
        
        chain = self.chain_data[chain_name]
        profile = chain["profile"]
        
        # Current daily transactions
        tx_count = chain.get("tx_count", 100000)  # Default to 100k if not set
        
        # Simulation results
        results = {
            "days": list(range(days)),
            "tx_count": [],
            "daily_energy": [],
            "daily_carbon": [],
            "cumulative_energy": [],
            "cumulative_carbon": []
        }
        
        cumulative_energy = 0
        cumulative_carbon = 0
        
        for day in range(days):
            # Calculate energy for current day
            daily_energy = tx_count * profile.energy_per_tx
            daily_carbon = daily_energy * profile.carbon_intensity
            
            # Account for scalability factor (non-linear energy growth)
            if profile.scalability_factor is not None and profile.scalability_factor != 1.0:
                # Adjust energy based on network size
                size_factor = (1 + day/100) ** (profile.scalability_factor - 1.0)
                daily_energy *= size_factor
                daily_carbon *= size_factor
            
            # Update cumulative metrics
            cumulative_energy += daily_energy
            cumulative_carbon += daily_carbon
            
            # Store results
            results["tx_count"].append(tx_count)
            results["daily_energy"].append(daily_energy)
            results["daily_carbon"].append(daily_carbon)
            results["cumulative_energy"].append(cumulative_energy)
            results["cumulative_carbon"].append(cumulative_carbon)
            
            # Apply growth for next day
            tx_count *= growth_factor
        
        # Add summary
        results["summary"] = {
            "chain": chain_name,
            "consensus": chain["consensus"],
            "initial_tx_count": results["tx_count"][0],
            "final_tx_count": results["tx_count"][-1],
            "total_energy": cumulative_energy,
            "total_carbon": cumulative_carbon,
            "peak_daily_energy": max(results["daily_energy"]),
            "growth_factor": growth_factor,
            "days": days
        }
        
        return results
    
    def create_impact_report(self, chain_name: str) -> Dict:
        """
        Create an environmental impact report for a blockchain.
        
        Args:
            chain_name: Name of the chain.
            
        Returns:
            Dictionary with impact report data.
        """
        if chain_name not in self.chain_data:
            logger.error(f"Chain {chain_name} not found in tracked chains")
            return {"error": f"Chain {chain_name} not found"}
        
        chain = self.chain_data[chain_name]
        profile = chain["profile"]
        metrics = self.get_chain_metrics(chain_name)
        
        # Calculate comparison to Bitcoin (PoW reference)
        btc_energy_per_tx = self.profiles["PoW"].energy_per_tx
        energy_savings_factor = btc_energy_per_tx / profile.energy_per_tx if profile.energy_per_tx > 0 else float('inf')
        
        # Calculate equivalent energy examples
        daily_energy_kwh = metrics.get("total_daily_energy", 0)
        annual_energy_kwh = daily_energy_kwh * 365
        
        # Equivalents (approximate values)
        us_household_daily = 30  # kWh per day
        households_powered = daily_energy_kwh / us_household_daily if us_household_daily > 0 else 0
        
        ev_charge_kwh = 70  # kWh per full charge
        ev_charges = daily_energy_kwh / ev_charge_kwh if ev_charge_kwh > 0 else 0
        
        flight_kwh_per_km = 0.65  # kWh per passenger-km
        flight_distance = daily_energy_kwh / flight_kwh_per_km if flight_kwh_per_km > 0 else 0
        
        # Carbon equivalents
        daily_carbon = metrics.get("daily_carbon", 0)  # kg CO2
        annual_carbon = daily_carbon * 365
        
        # Tree offset (approximate: 20 kg CO2 per tree per year)
        trees_required = annual_carbon / 20 if annual_carbon > 0 else 0
        
        # Recommendations for improvement
        recommendations = []
        if profile.consensus == "PoW":
            recommendations.append("Consider transitioning to Proof of Stake for significant energy savings")
            recommendations.append("Source renewable energy for mining operations")
        elif profile.consensus == "PoS":
            recommendations.append("Optimize validator hardware for energy efficiency")
            recommendations.append("Encourage validators to use renewable energy sources")
        
        recommendations.append("Implement carbon offset programs to achieve carbon neutrality")
        
        # Create report
        report = {
            "chain": chain_name,
            "consensus": chain["consensus"],
            "energy_metrics": metrics,
            "comparison": {
                "energy_savings_vs_bitcoin": energy_savings_factor,
                "energy_comparison": f"{energy_savings_factor:.1f}x more efficient than Bitcoin"
            },
            "energy_equivalents": {
                "households_powered_daily": households_powered,
                "ev_charges_daily": ev_charges,
                "flight_distance_equivalent_km": flight_distance
            },
            "carbon_impact": {
                "daily_carbon_kg": daily_carbon,
                "annual_carbon_tons": annual_carbon / 1000,
                "trees_for_offset": trees_required
            },
            "recommendations": recommendations
        }
        
        return report
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert chain metrics to a pandas DataFrame for analysis.
        
        Returns:
            DataFrame with chain metrics.
        """
        data = []
        
        for name, chain in self.chain_data.items():
            metrics = self.get_chain_metrics(name)
            
            row = {
                "chain_name": name,
                "consensus": chain["consensus"],
                "energy_per_tx_kwh": metrics.get("energy_per_tx", 0),
                "daily_energy_kwh": metrics.get("total_daily_energy", 0),
                "daily_carbon_kg": metrics.get("daily_carbon", 0),
                "efficiency_score": metrics.get("energy_efficiency_score", 0)
            }
            
            data.append(row)
        
        return pd.DataFrame(data) 
 
 