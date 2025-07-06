import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class SustainabilityScorer:
    """
    Class responsible for scoring mining operations based on their sustainability metrics.
    
    This simulates an ML model that would evaluate various factors to produce a
    sustainability score for each mining operation. In a real implementation,
    this would use trained machine learning models.
    """
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize the sustainability scorer with weights for different factors.
        
        Args:
            weights: Dictionary mapping factor names to their weights in the scoring model.
                    If None, default weights will be used.
        """
        # Default weights for different factors (would be ML model parameters in real implementation)
        self.weights = weights or {
            "renewable_energy_percentage": 0.35,
            "energy_efficiency_rating": 0.25,
            "carbon_footprint": 0.20,
            "carbon_offset_percentage": 0.10,
            "sustainability_initiatives": 0.05,
            "location_factor": 0.05
        }
        
        # Factor that penalizes high carbon footprints
        self.carbon_penalty_factor = 0.01
        
        # Country-specific efficiency factors based on typical grid energy mix
        self.location_factors = {
            "Iceland": 0.95,  # Very green energy (geothermal, hydro)
            "Norway": 0.90,   # Mostly hydro
            "Sweden": 0.85,   # Significant renewables
            "Canada": 0.70,   # Mixed but good hydro
            "USA": 0.50,      # Very mixed
            "Russia": 0.30,   # Fossil fuel heavy
            "Kazakhstan": 0.25, # Coal heavy
            "China": 0.20     # Coal dominant
        }
        
        # Default location factor for unknown locations
        self.default_location_factor = 0.40
    
    def score_operation(self, mining_data: Dict, carbon_data: Dict) -> Dict:
        """
        Score a mining operation based on its sustainability metrics.
        
        Args:
            mining_data: Dictionary with mining operation data.
            carbon_data: Dictionary with carbon footprint data.
            
        Returns:
            Dictionary containing the sustainability score and subscores.
        """
        try:
            # Extract relevant metrics
            renewable_percentage = carbon_data.get("renewable_energy_percentage", 0)
            efficiency_rating = carbon_data.get("energy_efficiency_rating", 0)
            carbon_footprint = carbon_data.get("carbon_footprint_tons_per_day", 0)
            offset_percentage = carbon_data.get("carbon_offset_percentage", 0)
            initiatives = carbon_data.get("sustainability_initiatives", 0)
            location = mining_data.get("location", "")
            
            # Normalize values to 0-1 range
            normalized_carbon = self._normalize_carbon_footprint(carbon_footprint)
            normalized_initiatives = min(initiatives / 5.0, 1.0)  # Assuming max 5 initiatives
            location_factor = self.location_factors.get(location, self.default_location_factor)
            
            # Calculate component scores
            renewable_score = renewable_percentage / 100.0
            efficiency_score = efficiency_rating
            carbon_score = 1.0 - normalized_carbon  # Lower carbon is better
            offset_score = offset_percentage / 100.0
            initiatives_score = normalized_initiatives
            
            # Apply carbon penalty for high emitters (nonlinear penalty)
            carbon_penalty = np.exp(normalized_carbon * self.carbon_penalty_factor) - 1
            
            # Calculate weighted score
            weighted_score = (
                self.weights["renewable_energy_percentage"] * renewable_score +
                self.weights["energy_efficiency_rating"] * efficiency_score +
                self.weights["carbon_footprint"] * carbon_score +
                self.weights["carbon_offset_percentage"] * offset_score +
                self.weights["sustainability_initiatives"] * initiatives_score +
                self.weights["location_factor"] * location_factor
            )
            
            # Apply penalty and ensure score is in 0-100 range
            final_score = max(0, min(100, (weighted_score - carbon_penalty) * 100))
            
            # Determine sustainability tier
            tier = self._determine_tier(final_score)
            
            return {
                "operation_id": mining_data.get("id", "unknown"),
                "sustainability_score": final_score,
                "sustainability_tier": tier,
                "component_scores": {
                    "renewable_energy": renewable_score * 100,
                    "energy_efficiency": efficiency_score * 100,
                    "carbon_footprint": carbon_score * 100,
                    "carbon_offset": offset_score * 100,
                    "sustainability_initiatives": initiatives_score * 100,
                    "location_factor": location_factor * 100
                },
                "improvement_suggestions": self._generate_suggestions(
                    renewable_score, efficiency_score, carbon_score, offset_score, initiatives_score
                )
            }
        except Exception as e:
            logger.error(f"Error scoring operation: {str(e)}")
            return {
                "operation_id": mining_data.get("id", "unknown"),
                "sustainability_score": 0,
                "sustainability_tier": "ERROR",
                "error": str(e)
            }
    
    def score_multiple_operations(
        self, operations_data: List[Dict], carbon_data_list: List[Dict]
    ) -> List[Dict]:
        """
        Score multiple mining operations based on their sustainability metrics.
        
        Args:
            operations_data: List of dictionaries with mining operation data.
            carbon_data_list: List of dictionaries with carbon footprint data.
            
        Returns:
            List of dictionaries containing sustainability scores.
        """
        scores = []
        
        # Create a lookup dictionary for carbon data by operation ID
        carbon_data_map = {
            carbon_data["operation_id"]: carbon_data 
            for carbon_data in carbon_data_list
        }
        
        for op_data in operations_data:
            op_id = op_data.get("id", "")
            carbon_data = carbon_data_map.get(op_id, {})
            score = self.score_operation(op_data, carbon_data)
            scores.append(score)
        
        return scores
    
    def _normalize_carbon_footprint(self, carbon_footprint: float) -> float:
        """
        Normalize carbon footprint to a 0-1 scale.
        
        Args:
            carbon_footprint: Carbon footprint in tons per day.
            
        Returns:
            Normalized carbon footprint (0-1 scale).
        """
        # Typical range of carbon footprints for mining operations
        min_footprint = 0.0
        max_footprint = 100.0
        
        # Apply sigmoid normalization for nonlinear scaling
        normalized = 1.0 / (1.0 + np.exp(-0.05 * (carbon_footprint - max_footprint/2)))
        return normalized
    
    def _determine_tier(self, score: float) -> str:
        """
        Determine sustainability tier based on the score.
        
        Args:
            score: Sustainability score (0-100).
            
        Returns:
            String indicating the sustainability tier.
        """
        if score >= 90:
            return "Platinum"
        elif score >= 75:
            return "Gold"
        elif score >= 60:
            return "Silver"
        elif score >= 45:
            return "Bronze"
        elif score >= 30:
            return "Standard"
        else:
            return "Needs Improvement"
    
    def _generate_suggestions(
        self, 
        renewable_score: float, 
        efficiency_score: float, 
        carbon_score: float,
        offset_score: float, 
        initiatives_score: float
    ) -> List[str]:
        """
        Generate improvement suggestions based on component scores.
        
        Args:
            renewable_score: Score for renewable energy usage (0-1).
            efficiency_score: Score for energy efficiency (0-1).
            carbon_score: Score for carbon footprint (0-1).
            offset_score: Score for carbon offset programs (0-1).
            initiatives_score: Score for sustainability initiatives (0-1).
            
        Returns:
            List of improvement suggestions.
        """
        suggestions = []
        
        if renewable_score < 0.5:
            suggestions.append(
                "Increase renewable energy usage through direct purchases, "
                "RECs, or on-site generation."
            )
        
        if efficiency_score < 0.6:
            suggestions.append(
                "Upgrade to more energy-efficient mining hardware."
            )
        
        if carbon_score < 0.5:
            suggestions.append(
                "Reduce carbon footprint by optimizing operations or "
                "relocating to areas with cleaner energy."
            )
        
        if offset_score < 0.3:
            suggestions.append(
                "Implement carbon offset programs to balance unavoidable emissions."
            )
        
        if initiatives_score < 0.4:
            suggestions.append(
                "Develop and implement sustainability initiatives like waste heat recovery, "
                "facility optimization, or renewable partnerships."
            )
            
        return suggestions 