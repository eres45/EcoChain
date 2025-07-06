"""
Optimization Advisor Module

This module provides AI-powered recommendations for improving mining operation
sustainability, including hardware upgrades, energy source changes, and cooling
system improvements with ROI calculations.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import json
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class OptimizationAdvisor:
    """
    AI-powered advisor that analyzes mining operations and suggests
    specific improvements with ROI calculations.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the optimization advisor.
        
        Args:
            model_path: Optional path to a pre-trained model.
        """
        self.model_path = model_path
        
        # Hardware upgrade database with efficiency improvements and costs
        self.hardware_database = {
            "asic_miners": {
                "Antminer S19 XP": {
                    "hashrate": 140,  # TH/s
                    "power": 3010,    # Watts
                    "efficiency": 21.5,  # J/TH
                    "cost": 2000,     # USD
                    "lifespan": 36    # months
                },
                "Antminer S19j Pro": {
                    "hashrate": 104,  # TH/s
                    "power": 3068,    # Watts
                    "efficiency": 29.5,  # J/TH
                    "cost": 1500,     # USD
                    "lifespan": 36    # months
                },
                "Whatsminer M50S": {
                    "hashrate": 126,  # TH/s
                    "power": 3276,    # Watts
                    "efficiency": 26.0,  # J/TH
                    "cost": 1800,     # USD
                    "lifespan": 36    # months
                }
            },
            "gpu_miners": {
                "NVIDIA RTX 4090": {
                    "hashrate": 150,  # MH/s (ETH)
                    "power": 320,     # Watts
                    "efficiency": 2.13,  # W/MH
                    "cost": 1600,     # USD
                    "lifespan": 48    # months
                },
                "AMD Radeon RX 7900 XTX": {
                    "hashrate": 110,  # MH/s (ETH)
                    "power": 300,     # Watts
                    "efficiency": 2.73,  # W/MH
                    "cost": 1000,     # USD
                    "lifespan": 48    # months
                }
            }
        }
        
        # Energy source options with costs and carbon impact
        self.energy_sources = {
            "solar": {
                "cost_per_kwh": 0.10,  # USD
                "installation_cost": 1000,  # USD per kW
                "carbon_reduction": 0.95,  # percentage
                "lifespan": 25,  # years
                "reliability": 0.7  # depends on weather
            },
            "wind": {
                "cost_per_kwh": 0.08,  # USD
                "installation_cost": 1200,  # USD per kW
                "carbon_reduction": 0.95,  # percentage
                "lifespan": 20,  # years
                "reliability": 0.65  # depends on weather
            },
            "hydro": {
                "cost_per_kwh": 0.07,  # USD
                "installation_cost": 2000,  # USD per kW
                "carbon_reduction": 0.90,  # percentage
                "lifespan": 30,  # years
                "reliability": 0.85  # very reliable
            },
            "geothermal": {
                "cost_per_kwh": 0.05,  # USD
                "installation_cost": 4000,  # USD per kW
                "carbon_reduction": 0.85,  # percentage
                "lifespan": 25,  # years
                "reliability": 0.95  # extremely reliable
            },
            "natural_gas": {
                "cost_per_kwh": 0.06,  # USD
                "installation_cost": 800,  # USD per kW
                "carbon_reduction": 0.30,  # compared to coal
                "lifespan": 20,  # years
                "reliability": 0.98  # very reliable
            }
        }
        
        # Cooling system options with efficiency improvements and costs
        self.cooling_systems = {
            "immersion_cooling": {
                "efficiency_improvement": 0.30,  # percentage
                "installation_cost": 300,  # USD per kW
                "operational_cost_reduction": 0.25,  # percentage
                "lifespan": 10,  # years
                "maintenance_cost": "Low"
            },
            "liquid_cooling": {
                "efficiency_improvement": 0.25,  # percentage
                "installation_cost": 200,  # USD per kW
                "operational_cost_reduction": 0.20,  # percentage
                "lifespan": 8,  # years
                "maintenance_cost": "Medium"
            },
            "advanced_air_cooling": {
                "efficiency_improvement": 0.15,  # percentage
                "installation_cost": 100,  # USD per kW
                "operational_cost_reduction": 0.10,  # percentage
                "lifespan": 5,  # years
                "maintenance_cost": "Low"
            },
            "geothermal_heat_exchange": {
                "efficiency_improvement": 0.35,  # percentage
                "installation_cost": 500,  # USD per kW
                "operational_cost_reduction": 0.30,  # percentage
                "lifespan": 15,  # years
                "maintenance_cost": "Medium"
            }
        }
        
        # Load any additional data from model if provided
        if self.model_path and os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'r') as f:
                    model_data = json.load(f)
                    # Update databases with model data if available
                    if 'hardware_database' in model_data:
                        self.hardware_database.update(model_data['hardware_database'])
                    if 'energy_sources' in model_data:
                        self.energy_sources.update(model_data['energy_sources'])
                    if 'cooling_systems' in model_data:
                        self.cooling_systems.update(model_data['cooling_systems'])
            except Exception as e:
                logger.error(f"Error loading model data: {str(e)}")
    
    def generate_recommendations(self, mining_data: Dict, carbon_data: Dict) -> Dict:
        """
        Generate optimization recommendations based on mining operation data.
        
        Args:
            mining_data: Dictionary with mining operation data.
            carbon_data: Dictionary with carbon footprint data.
            
        Returns:
            Dictionary containing recommendations and ROI calculations.
        """
        recommendations = {
            "operation_id": mining_data.get("id", "unknown"),
            "operation_name": mining_data.get("name", "Unknown Operation"),
            "timestamp": datetime.now().isoformat(),
            "hardware_recommendations": [],
            "energy_recommendations": [],
            "cooling_recommendations": [],
            "combined_roi": {}
        }
        
        # Current operation metrics
        current_power = mining_data.get("power_consumption_kw", 0) * 1000  # Convert to watts
        current_hashrate = mining_data.get("hashrate", 0)
        current_efficiency = current_power / current_hashrate if current_hashrate else 0
        electricity_cost = mining_data.get("electricity_cost_per_kwh", 0.10)  # USD per kWh
        renewable_percentage = carbon_data.get("renewable_energy_percentage", 0)
        
        # Generate hardware recommendations
        recommendations["hardware_recommendations"] = self._recommend_hardware(
            mining_data, current_power, current_hashrate, current_efficiency, electricity_cost
        )
        
        # Generate energy source recommendations
        recommendations["energy_recommendations"] = self._recommend_energy_sources(
            mining_data, carbon_data, current_power, electricity_cost, renewable_percentage
        )
        
        # Generate cooling system recommendations
        recommendations["cooling_recommendations"] = self._recommend_cooling_systems(
            mining_data, carbon_data, current_power, electricity_cost
        )
        
        # Calculate combined ROI
        recommendations["combined_roi"] = self._calculate_combined_roi(
            recommendations["hardware_recommendations"],
            recommendations["energy_recommendations"],
            recommendations["cooling_recommendations"]
        )
        
        return recommendations
    
    def _recommend_hardware(
        self, 
        mining_data: Dict, 
        current_power: float, 
        current_hashrate: float, 
        current_efficiency: float,
        electricity_cost: float
    ) -> List[Dict]:
        """
        Recommend hardware upgrades based on current setup.
        
        Args:
            mining_data: Dictionary with mining operation data.
            current_power: Current power consumption in watts.
            current_hashrate: Current hashrate.
            current_efficiency: Current efficiency.
            electricity_cost: Electricity cost per kWh.
            
        Returns:
            List of hardware recommendations with ROI calculations.
        """
        recommendations = []
        miner_type = mining_data.get("miner_type", "asic_miners")
        
        # Get relevant hardware options
        hardware_options = self.hardware_database.get(miner_type, {})
        if not hardware_options:
            return recommendations
        
        # Current annual electricity cost
        daily_power_kwh = (current_power / 1000) * 24  # kWh per day
        annual_electricity_cost = daily_power_kwh * 365 * electricity_cost
        
        for hw_name, hw_specs in hardware_options.items():
            # Skip if it's the current hardware
            if hw_name == mining_data.get("hardware_model", ""):
                continue
                
            # Calculate new efficiency and power savings
            new_efficiency = hw_specs["efficiency"]
            efficiency_improvement = max(0, (current_efficiency - new_efficiency) / current_efficiency)
            
            # Normalize hashrates to be comparable
            hashrate_factor = hw_specs["hashrate"] / current_hashrate if current_hashrate else 1
            
            # Calculate power savings
            new_power = hw_specs["power"]
            power_savings = current_power - (new_power / hashrate_factor)
            
            # Calculate annual savings
            daily_savings_kwh = (power_savings / 1000) * 24  # kWh per day
            annual_savings = daily_savings_kwh * 365 * electricity_cost
            
            # Calculate ROI
            cost = hw_specs["cost"]
            roi_years = cost / annual_savings if annual_savings > 0 else float('inf')
            
            # Calculate sustainability improvement
            carbon_reduction = power_savings / current_power if current_power > 0 else 0
            
            # Only recommend if there's a significant improvement
            if efficiency_improvement > 0.05:
                recommendations.append({
                    "type": "hardware",
                    "name": hw_name,
                    "description": f"Upgrade to {hw_name} for better efficiency",
                    "current_efficiency": current_efficiency,
                    "new_efficiency": new_efficiency,
                    "efficiency_improvement_percentage": efficiency_improvement * 100,
                    "power_savings_watts": power_savings,
                    "annual_savings_usd": annual_savings,
                    "cost_usd": cost,
                    "roi_years": roi_years,
                    "roi_months": roi_years * 12,
                    "sustainability_improvement_percentage": carbon_reduction * 100,
                    "specs": hw_specs
                })
        
        # Sort by ROI (best first)
        recommendations.sort(key=lambda x: x["roi_years"])
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def _recommend_energy_sources(
        self, 
        mining_data: Dict, 
        carbon_data: Dict, 
        current_power: float, 
        electricity_cost: float,
        renewable_percentage: float
    ) -> List[Dict]:
        """
        Recommend energy source changes based on current setup.
        
        Args:
            mining_data: Dictionary with mining operation data.
            carbon_data: Dictionary with carbon footprint data.
            current_power: Current power consumption in watts.
            electricity_cost: Electricity cost per kWh.
            renewable_percentage: Current renewable energy percentage.
            
        Returns:
            List of energy source recommendations with ROI calculations.
        """
        recommendations = []
        
        # Current annual electricity cost
        daily_power_kwh = (current_power / 1000) * 24  # kWh per day
        annual_electricity_cost = daily_power_kwh * 365 * electricity_cost
        
        # Current carbon footprint
        carbon_footprint = carbon_data.get("carbon_footprint_tons_per_day", 0) * 365  # annual
        
        for source_name, source_specs in self.energy_sources.items():
            # Skip if it's already the primary energy source
            current_source = mining_data.get("energy_source", "")
            if source_name == current_source:
                continue
                
            # Calculate cost savings
            new_cost_per_kwh = source_specs["cost_per_kwh"]
            cost_savings_per_kwh = electricity_cost - new_cost_per_kwh
            annual_cost_savings = daily_power_kwh * 365 * cost_savings_per_kwh
            
            # Calculate installation cost
            power_capacity_needed = current_power / 1000  # kW
            installation_cost = source_specs["installation_cost"] * power_capacity_needed
            
            # Calculate ROI
            roi_years = installation_cost / annual_cost_savings if annual_cost_savings > 0 else float('inf')
            
            # Calculate carbon reduction
            carbon_reduction = source_specs["carbon_reduction"]
            annual_carbon_savings = carbon_footprint * carbon_reduction * (1 - renewable_percentage/100)
            
            # Only recommend if there's a positive ROI within 10 years or significant carbon reduction
            if roi_years < 10 or carbon_reduction > 0.5:
                recommendations.append({
                    "type": "energy",
                    "name": source_name.capitalize(),
                    "description": f"Switch to {source_name} energy",
                    "current_cost_per_kwh": electricity_cost,
                    "new_cost_per_kwh": new_cost_per_kwh,
                    "annual_cost_savings_usd": annual_cost_savings,
                    "installation_cost_usd": installation_cost,
                    "roi_years": roi_years,
                    "roi_months": roi_years * 12,
                    "carbon_reduction_percentage": carbon_reduction * 100,
                    "annual_carbon_savings_tons": annual_carbon_savings,
                    "reliability": source_specs["reliability"] * 100,
                    "lifespan_years": source_specs["lifespan"]
                })
        
        # Sort by ROI (best first)
        recommendations.sort(key=lambda x: x["roi_years"])
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def _recommend_cooling_systems(
        self, 
        mining_data: Dict, 
        carbon_data: Dict, 
        current_power: float, 
        electricity_cost: float
    ) -> List[Dict]:
        """
        Recommend cooling system improvements based on current setup.
        
        Args:
            mining_data: Dictionary with mining operation data.
            carbon_data: Dictionary with carbon footprint data.
            current_power: Current power consumption in watts.
            electricity_cost: Electricity cost per kWh.
            
        Returns:
            List of cooling system recommendations with ROI calculations.
        """
        recommendations = []
        
        # Current cooling system
        current_cooling = mining_data.get("cooling_system", "standard_air")
        
        # Current annual electricity cost
        daily_power_kwh = (current_power / 1000) * 24  # kWh per day
        annual_electricity_cost = daily_power_kwh * 365 * electricity_cost
        
        # Assume cooling is about 30% of power consumption
        cooling_power = current_power * 0.3
        daily_cooling_kwh = (cooling_power / 1000) * 24
        annual_cooling_cost = daily_cooling_kwh * 365 * electricity_cost
        
        for system_name, system_specs in self.cooling_systems.items():
            # Skip if it's the current cooling system
            if system_name == current_cooling:
                continue
                
            # Calculate efficiency improvement
            efficiency_improvement = system_specs["efficiency_improvement"]
            operational_cost_reduction = system_specs["operational_cost_reduction"]
            
            # Calculate annual savings
            annual_savings = annual_cooling_cost * operational_cost_reduction
            
            # Calculate installation cost
            power_capacity = current_power / 1000  # kW
            installation_cost = system_specs["installation_cost"] * power_capacity
            
            # Calculate ROI
            roi_years = installation_cost / annual_savings if annual_savings > 0 else float('inf')
            
            # Calculate sustainability improvement (reduced power means reduced carbon)
            sustainability_improvement = efficiency_improvement
            
            # Only recommend if there's a positive ROI within 5 years
            if roi_years < 5:
                recommendations.append({
                    "type": "cooling",
                    "name": system_name.replace("_", " ").title(),
                    "description": f"Upgrade to {system_name.replace('_', ' ').title()} system",
                    "efficiency_improvement_percentage": efficiency_improvement * 100,
                    "operational_cost_reduction_percentage": operational_cost_reduction * 100,
                    "annual_savings_usd": annual_savings,
                    "installation_cost_usd": installation_cost,
                    "roi_years": roi_years,
                    "roi_months": roi_years * 12,
                    "sustainability_improvement_percentage": sustainability_improvement * 100,
                    "lifespan_years": system_specs["lifespan"],
                    "maintenance_cost": system_specs["maintenance_cost"]
                })
        
        # Sort by ROI (best first)
        recommendations.sort(key=lambda x: x["roi_years"])
        
        return recommendations[:2]  # Return top 2 recommendations
    
    def _calculate_combined_roi(
        self,
        hardware_recommendations: List[Dict],
        energy_recommendations: List[Dict],
        cooling_recommendations: List[Dict]
    ) -> Dict:
        """
        Calculate combined ROI for implementing multiple recommendations.
        
        Args:
            hardware_recommendations: List of hardware recommendations.
            energy_recommendations: List of energy source recommendations.
            cooling_recommendations: List of cooling system recommendations.
            
        Returns:
            Dictionary with combined ROI calculations.
        """
        # Get best recommendations from each category
        best_hardware = hardware_recommendations[0] if hardware_recommendations else None
        best_energy = energy_recommendations[0] if energy_recommendations else None
        best_cooling = cooling_recommendations[0] if cooling_recommendations else None
        
        # Calculate total costs and savings
        total_cost = 0
        annual_savings = 0
        sustainability_improvement = 0
        
        if best_hardware:
            total_cost += best_hardware["cost_usd"]
            annual_savings += best_hardware["annual_savings_usd"]
            sustainability_improvement += best_hardware["sustainability_improvement_percentage"]
            
        if best_energy:
            total_cost += best_energy["installation_cost_usd"]
            annual_savings += best_energy["annual_cost_savings_usd"]
            sustainability_improvement += best_energy["carbon_reduction_percentage"]
            
        if best_cooling:
            total_cost += best_cooling["installation_cost_usd"]
            annual_savings += best_cooling["annual_savings_usd"]
            sustainability_improvement += best_cooling["sustainability_improvement_percentage"]
        
        # Calculate combined ROI
        roi_years = total_cost / annual_savings if annual_savings > 0 else float('inf')
        
        # Calculate payback date
        today = datetime.now()
        payback_days = int(roi_years * 365)
        payback_date = (today + timedelta(days=payback_days)).strftime('%Y-%m-%d')
        
        return {
            "total_investment_usd": total_cost,
            "annual_savings_usd": annual_savings,
            "monthly_savings_usd": annual_savings / 12,
            "roi_years": roi_years,
            "roi_months": roi_years * 12,
            "payback_date": payback_date,
            "sustainability_improvement_percentage": min(100, sustainability_improvement),
            "recommendations_included": {
                "hardware": best_hardware["name"] if best_hardware else None,
                "energy": best_energy["name"] if best_energy else None,
                "cooling": best_cooling["name"] if best_cooling else None
            }
        } 
 
 