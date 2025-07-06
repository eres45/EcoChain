import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging
import pickle
import os
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

logger = logging.getLogger(__name__)

class MLSustainabilityScorer:
    """
    Enhanced sustainability scorer using scikit-learn for more sophisticated 
    scoring and anomaly detection for mining operations.
    
    Features:
    - Train on real or synthetic mining operation data
    - Use RandomForest for sustainability scoring
    - Use IsolationForest for anomaly detection
    - Save/load trained models
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the ML sustainability scorer.
        
        Args:
            model_path: Optional path to load a pre-trained model.
        """
        # Model parameters
        self.features = [
            'renewable_energy_percentage',
            'energy_efficiency_rating',
            'carbon_footprint_tons_per_day',
            'carbon_offset_percentage',
            'sustainability_initiatives',
            'location_factor'
        ]
        
        # Initialize models
        self.scoring_pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('model', RandomForestRegressor(
                n_estimators=100, 
                max_depth=10,
                random_state=42
            ))
        ])
        
        self.anomaly_detector = IsolationForest(
            contamination=0.05,  # Expecting 5% anomalies
            random_state=42
        )
        
        self.location_factors = {
            "Iceland": 0.95,  # Very green energy
            "Norway": 0.90,   # Mostly hydro
            "Sweden": 0.85,   # Significant renewables
            "Canada": 0.70,   # Mixed but good hydro
            "USA": 0.50,      # Very mixed
            "Russia": 0.30,   # Fossil fuel heavy
            "Kazakhstan": 0.25, # Coal heavy
            "China": 0.20     # Coal dominant
        }
        
        self.default_location_factor = 0.40
        self.is_model_trained = False
        
        # Load pre-trained model if specified
        if model_path and os.path.exists(model_path):
            self._load_model(model_path)
    
    def prepare_features(self, mining_data: Dict, carbon_data: Dict) -> np.ndarray:
        """
        Extract and prepare features for ML model input.
        
        Args:
            mining_data: Dictionary with mining operation data.
            carbon_data: Dictionary with carbon footprint data.
            
        Returns:
            Numpy array with features for ML model.
        """
        # Extract basic features
        renewable_percentage = carbon_data.get("renewable_energy_percentage", 0)
        efficiency_rating = carbon_data.get("energy_efficiency_rating", 0)
        carbon_footprint = carbon_data.get("carbon_footprint_tons_per_day", 0)
        offset_percentage = carbon_data.get("carbon_offset_percentage", 0)
        initiatives = carbon_data.get("sustainability_initiatives", 0)
        location = mining_data.get("location", "")
        location_factor = self.location_factors.get(location, self.default_location_factor)
        
        # Normalize values to 0-1 range
        normalized_initiatives = min(initiatives / 5.0, 1.0)  # Assuming max 5 initiatives
        
        # Sigmoid normalization for carbon footprint (lower is better)
        max_footprint = 100.0
        normalized_carbon = 1.0 / (1.0 + np.exp(-0.05 * (carbon_footprint - max_footprint/2)))
        
        # Create feature array
        features = np.array([
            renewable_percentage / 100.0,  # Normalize to 0-1
            efficiency_rating,             # Already 0-1
            normalized_carbon,             # Normalized to 0-1
            offset_percentage / 100.0,     # Normalize to 0-1
            normalized_initiatives,        # Normalized to 0-1
            location_factor                # Already 0-1
        ]).reshape(1, -1)
        
        return features
    
    def detect_anomalies(self, features_list: List[np.ndarray]) -> List[bool]:
        """
        Detect anomalies in mining operation data.
        
        Args:
            features_list: List of feature arrays.
            
        Returns:
            List of boolean values where True indicates an anomaly.
        """
        if not features_list:
            return []
        
        # Stack features for batch prediction
        features_array = np.vstack(features_list)
        
        # Predict anomalies (-1 for anomalies, 1 for normal)
        predictions = self.anomaly_detector.predict(features_array)
        
        # Convert to boolean (True for anomalies)
        return [pred == -1 for pred in predictions]
    
    def train(self, training_data: List[Dict]) -> Dict:
        """
        Train the ML model on mining operation data.
        
        Args:
            training_data: List of dictionaries with training samples.
                Each dict should contain 'features' and 'score'.
                
        Returns:
            Dictionary with training metrics.
        """
        if not training_data:
            logger.warning("No training data provided.")
            return {"error": "No training data provided"}
        
        try:
            # Extract features and targets
            X = np.array([sample['features'] for sample in training_data])
            y = np.array([sample['score'] for sample in training_data])
            
            # Split data for training and validation
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train scoring model
            self.scoring_pipeline.fit(X_train, y_train)
            
            # Train anomaly detection model
            self.anomaly_detector.fit(X)
            
            # Evaluate model
            y_pred = self.scoring_pipeline.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            self.is_model_trained = True
            
            return {
                "mse": mse,
                "r2": r2,
                "samples_count": len(training_data),
                "training_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return {"error": str(e)}
    
    def save_model(self, model_path: str) -> bool:
        """
        Save the trained model to disk.
        
        Args:
            model_path: Path to save the model.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.is_model_trained:
            logger.warning("Model not trained yet, cannot save.")
            return False
        
        try:
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            # Save both models in a dictionary
            models = {
                'scoring_pipeline': self.scoring_pipeline,
                'anomaly_detector': self.anomaly_detector
            }
            
            with open(model_path, 'wb') as f:
                pickle.dump(models, f)
            
            logger.info(f"Model saved to {model_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False
    
    def _load_model(self, model_path: str) -> bool:
        """
        Load a trained model from disk.
        
        Args:
            model_path: Path to the saved model.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            with open(model_path, 'rb') as f:
                models = pickle.load(f)
            
            self.scoring_pipeline = models['scoring_pipeline']
            self.anomaly_detector = models['anomaly_detector']
            self.is_model_trained = True
            
            logger.info(f"Model loaded from {model_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def generate_training_data(self, operations_count: int = 1000) -> List[Dict]:
        """
        Generate synthetic training data for the ML model.
        
        Args:
            operations_count: Number of synthetic operations to generate.
            
        Returns:
            List of dictionaries with synthetic training samples.
        """
        training_data = []
        
        for i in range(operations_count):
            # Generate synthetic features
            renewable = np.random.uniform(0, 100)
            efficiency = np.random.uniform(0, 1)
            carbon = np.random.uniform(0, 100)
            offset = np.random.uniform(0, 100)
            initiatives = np.random.randint(0, 6)
            location_factor = np.random.uniform(0.2, 0.95)
            
            # Normalize carbon footprint
            max_footprint = 100.0
            normalized_carbon = 1.0 / (1.0 + np.exp(-0.05 * (carbon - max_footprint/2)))
            normalized_initiatives = min(initiatives / 5.0, 1.0)
            
            # Create feature vector
            features = np.array([
                renewable / 100.0,
                efficiency,
                normalized_carbon,
                offset / 100.0,
                normalized_initiatives,
                location_factor
            ])
            
            # Calculate synthetic score (similar to our original formula but with some noise)
            weights = np.array([0.35, 0.25, -0.20, 0.10, 0.05, 0.05])
            base_score = np.dot(features, weights)
            # Add nonlinearity and noise
            score = 100 * (base_score + 0.5) + np.random.normal(0, 5)
            # Ensure score is in 0-100 range
            score = max(0, min(100, score))
            
            training_data.append({
                'features': features,
                'score': score
            })
        
        return training_data
    
    def score_operation(self, mining_data: Dict, carbon_data: Dict) -> Dict:
        """
        Score a mining operation using the trained ML model or fallback to rules-based scoring.
        
        Args:
            mining_data: Dictionary with mining operation data.
            carbon_data: Dictionary with carbon footprint data.
            
        Returns:
            Dictionary containing the sustainability score and additional information.
        """
        try:
            # Prepare features
            features = self.prepare_features(mining_data, carbon_data)
            
            # Score using ML model if trained, otherwise use rule-based approach
            if self.is_model_trained:
                score = float(self.scoring_pipeline.predict(features)[0])
                
                # Detect if this is an anomaly
                is_anomaly = self.anomaly_detector.predict(features)[0] == -1
                anomaly_score = self.anomaly_detector.score_samples(features)[0]
                
                # Clamp score to 0-100 range
                score = max(0, min(100, score))
                
                # Determine sustainability tier
                tier = self._determine_tier(score)
                
                result = {
                    "operation_id": mining_data.get("id", "unknown"),
                    "sustainability_score": score,
                    "sustainability_tier": tier,
                    "is_anomaly": is_anomaly,
                    "anomaly_score": anomaly_score,
                    "scoring_method": "ml_model"
                }
                
                # Add suggestions if not an anomaly
                if not is_anomaly:
                    result["improvement_suggestions"] = self._generate_suggestions(features[0])
                else:
                    result["improvement_suggestions"] = [
                        "Verify reported data as unusual patterns were detected."
                    ]
                
                return result
            else:
                # Fallback to rule-based scoring
                return self._rule_based_scoring(mining_data, carbon_data, features)
        
        except Exception as e:
            logger.error(f"Error scoring operation: {str(e)}")
            return {
                "operation_id": mining_data.get("id", "unknown"),
                "sustainability_score": 0,
                "sustainability_tier": "ERROR",
                "error": str(e)
            }
    
    def _rule_based_scoring(self, mining_data: Dict, carbon_data: Dict, features: np.ndarray) -> Dict:
        """
        Fallback rule-based scoring when ML model is not trained.
        
        Args:
            mining_data: Dictionary with mining operation data.
            carbon_data: Dictionary with carbon footprint data.
            features: Extracted feature array.
            
        Returns:
            Dictionary with score results.
        """
        # Extract feature components
        renewable_score = features[0][0]
        efficiency_score = features[0][1]
        carbon_score = 1.0 - features[0][2]  # Invert as lower carbon is better
        offset_score = features[0][3]
        initiatives_score = features[0][4]
        location_factor = features[0][5]
        
        # Weights from original model
        weights = {
            "renewable_energy_percentage": 0.35,
            "energy_efficiency_rating": 0.25,
            "carbon_footprint": 0.20,
            "carbon_offset_percentage": 0.10,
            "sustainability_initiatives": 0.05,
            "location_factor": 0.05
        }
        
        # Calculate weighted score
        weighted_score = (
            weights["renewable_energy_percentage"] * renewable_score +
            weights["energy_efficiency_rating"] * efficiency_score +
            weights["carbon_footprint"] * carbon_score +
            weights["carbon_offset_percentage"] * offset_score +
            weights["sustainability_initiatives"] * initiatives_score +
            weights["location_factor"] * location_factor
        )
        
        # Carbon penalty for high emitters
        carbon_penalty = np.exp(features[0][2] * 0.01) - 1
        
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
            "improvement_suggestions": self._generate_suggestions(features[0]),
            "scoring_method": "rule_based"
        }
    
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
    
    def _generate_suggestions(self, features: np.ndarray) -> List[str]:
        """
        Generate improvement suggestions based on feature values.
        
        Args:
            features: Feature vector with normalized values.
            
        Returns:
            List of improvement suggestions.
        """
        suggestions = []
        
        renewable_score = features[0]
        efficiency_score = features[1]
        carbon_score = features[2]  # This is normalized carbon (higher is worse)
        offset_score = features[3]
        initiatives_score = features[4]
        
        if renewable_score < 0.5:
            suggestions.append(
                "Increase renewable energy usage through direct purchases, "
                "RECs, or on-site generation."
            )
        
        if efficiency_score < 0.6:
            suggestions.append(
                "Upgrade to more energy-efficient mining hardware or optimize "
                "cooling systems for better efficiency."
            )
        
        if carbon_score > 0.5:  # Remember higher normalized carbon is worse
            suggestions.append(
                "Reduce carbon footprint by optimizing operations or "
                "relocating to areas with cleaner energy."
            )
        
        if offset_score < 0.3:
            suggestions.append(
                "Implement carbon offset programs to balance unavoidable emissions "
                "through verified carbon credit purchases."
            )
        
        if initiatives_score < 0.4:
            suggestions.append(
                "Develop and implement sustainability initiatives like waste heat recovery, "
                "facility optimization, or renewable energy partnerships."
            )
            
        return suggestions 
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging
import pickle
import os
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

logger = logging.getLogger(__name__)

class MLSustainabilityScorer:
    """
    Enhanced sustainability scorer using scikit-learn for more sophisticated 
    scoring and anomaly detection for mining operations.
    
    Features:
    - Train on real or synthetic mining operation data
    - Use RandomForest for sustainability scoring
    - Use IsolationForest for anomaly detection
    - Save/load trained models
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the ML sustainability scorer.
        
        Args:
            model_path: Optional path to load a pre-trained model.
        """
        # Model parameters
        self.features = [
            'renewable_energy_percentage',
            'energy_efficiency_rating',
            'carbon_footprint_tons_per_day',
            'carbon_offset_percentage',
            'sustainability_initiatives',
            'location_factor'
        ]
        
        # Initialize models
        self.scoring_pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('model', RandomForestRegressor(
                n_estimators=100, 
                max_depth=10,
                random_state=42
            ))
        ])
        
        self.anomaly_detector = IsolationForest(
            contamination=0.05,  # Expecting 5% anomalies
            random_state=42
        )
        
        self.location_factors = {
            "Iceland": 0.95,  # Very green energy
            "Norway": 0.90,   # Mostly hydro
            "Sweden": 0.85,   # Significant renewables
            "Canada": 0.70,   # Mixed but good hydro
            "USA": 0.50,      # Very mixed
            "Russia": 0.30,   # Fossil fuel heavy
            "Kazakhstan": 0.25, # Coal heavy
            "China": 0.20     # Coal dominant
        }
        
        self.default_location_factor = 0.40
        self.is_model_trained = False
        
        # Load pre-trained model if specified
        if model_path and os.path.exists(model_path):
            self._load_model(model_path)
    
    def prepare_features(self, mining_data: Dict, carbon_data: Dict) -> np.ndarray:
        """
        Extract and prepare features for ML model input.
        
        Args:
            mining_data: Dictionary with mining operation data.
            carbon_data: Dictionary with carbon footprint data.
            
        Returns:
            Numpy array with features for ML model.
        """
        # Extract basic features
        renewable_percentage = carbon_data.get("renewable_energy_percentage", 0)
        efficiency_rating = carbon_data.get("energy_efficiency_rating", 0)
        carbon_footprint = carbon_data.get("carbon_footprint_tons_per_day", 0)
        offset_percentage = carbon_data.get("carbon_offset_percentage", 0)
        initiatives = carbon_data.get("sustainability_initiatives", 0)
        location = mining_data.get("location", "")
        location_factor = self.location_factors.get(location, self.default_location_factor)
        
        # Normalize values to 0-1 range
        normalized_initiatives = min(initiatives / 5.0, 1.0)  # Assuming max 5 initiatives
        
        # Sigmoid normalization for carbon footprint (lower is better)
        max_footprint = 100.0
        normalized_carbon = 1.0 / (1.0 + np.exp(-0.05 * (carbon_footprint - max_footprint/2)))
        
        # Create feature array
        features = np.array([
            renewable_percentage / 100.0,  # Normalize to 0-1
            efficiency_rating,             # Already 0-1
            normalized_carbon,             # Normalized to 0-1
            offset_percentage / 100.0,     # Normalize to 0-1
            normalized_initiatives,        # Normalized to 0-1
            location_factor                # Already 0-1
        ]).reshape(1, -1)
        
        return features
    
    def detect_anomalies(self, features_list: List[np.ndarray]) -> List[bool]:
        """
        Detect anomalies in mining operation data.
        
        Args:
            features_list: List of feature arrays.
            
        Returns:
            List of boolean values where True indicates an anomaly.
        """
        if not features_list:
            return []
        
        # Stack features for batch prediction
        features_array = np.vstack(features_list)
        
        # Predict anomalies (-1 for anomalies, 1 for normal)
        predictions = self.anomaly_detector.predict(features_array)
        
        # Convert to boolean (True for anomalies)
        return [pred == -1 for pred in predictions]
    
    def train(self, training_data: List[Dict]) -> Dict:
        """
        Train the ML model on mining operation data.
        
        Args:
            training_data: List of dictionaries with training samples.
                Each dict should contain 'features' and 'score'.
                
        Returns:
            Dictionary with training metrics.
        """
        if not training_data:
            logger.warning("No training data provided.")
            return {"error": "No training data provided"}
        
        try:
            # Extract features and targets
            X = np.array([sample['features'] for sample in training_data])
            y = np.array([sample['score'] for sample in training_data])
            
            # Split data for training and validation
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train scoring model
            self.scoring_pipeline.fit(X_train, y_train)
            
            # Train anomaly detection model
            self.anomaly_detector.fit(X)
            
            # Evaluate model
            y_pred = self.scoring_pipeline.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            self.is_model_trained = True
            
            return {
                "mse": mse,
                "r2": r2,
                "samples_count": len(training_data),
                "training_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return {"error": str(e)}
    
    def save_model(self, model_path: str) -> bool:
        """
        Save the trained model to disk.
        
        Args:
            model_path: Path to save the model.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.is_model_trained:
            logger.warning("Model not trained yet, cannot save.")
            return False
        
        try:
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            # Save both models in a dictionary
            models = {
                'scoring_pipeline': self.scoring_pipeline,
                'anomaly_detector': self.anomaly_detector
            }
            
            with open(model_path, 'wb') as f:
                pickle.dump(models, f)
            
            logger.info(f"Model saved to {model_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False
    
    def _load_model(self, model_path: str) -> bool:
        """
        Load a trained model from disk.
        
        Args:
            model_path: Path to the saved model.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            with open(model_path, 'rb') as f:
                models = pickle.load(f)
            
            self.scoring_pipeline = models['scoring_pipeline']
            self.anomaly_detector = models['anomaly_detector']
            self.is_model_trained = True
            
            logger.info(f"Model loaded from {model_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def generate_training_data(self, operations_count: int = 1000) -> List[Dict]:
        """
        Generate synthetic training data for the ML model.
        
        Args:
            operations_count: Number of synthetic operations to generate.
            
        Returns:
            List of dictionaries with synthetic training samples.
        """
        training_data = []
        
        for i in range(operations_count):
            # Generate synthetic features
            renewable = np.random.uniform(0, 100)
            efficiency = np.random.uniform(0, 1)
            carbon = np.random.uniform(0, 100)
            offset = np.random.uniform(0, 100)
            initiatives = np.random.randint(0, 6)
            location_factor = np.random.uniform(0.2, 0.95)
            
            # Normalize carbon footprint
            max_footprint = 100.0
            normalized_carbon = 1.0 / (1.0 + np.exp(-0.05 * (carbon - max_footprint/2)))
            normalized_initiatives = min(initiatives / 5.0, 1.0)
            
            # Create feature vector
            features = np.array([
                renewable / 100.0,
                efficiency,
                normalized_carbon,
                offset / 100.0,
                normalized_initiatives,
                location_factor
            ])
            
            # Calculate synthetic score (similar to our original formula but with some noise)
            weights = np.array([0.35, 0.25, -0.20, 0.10, 0.05, 0.05])
            base_score = np.dot(features, weights)
            # Add nonlinearity and noise
            score = 100 * (base_score + 0.5) + np.random.normal(0, 5)
            # Ensure score is in 0-100 range
            score = max(0, min(100, score))
            
            training_data.append({
                'features': features,
                'score': score
            })
        
        return training_data
    
    def score_operation(self, mining_data: Dict, carbon_data: Dict) -> Dict:
        """
        Score a mining operation using the trained ML model or fallback to rules-based scoring.
        
        Args:
            mining_data: Dictionary with mining operation data.
            carbon_data: Dictionary with carbon footprint data.
            
        Returns:
            Dictionary containing the sustainability score and additional information.
        """
        try:
            # Prepare features
            features = self.prepare_features(mining_data, carbon_data)
            
            # Score using ML model if trained, otherwise use rule-based approach
            if self.is_model_trained:
                score = float(self.scoring_pipeline.predict(features)[0])
                
                # Detect if this is an anomaly
                is_anomaly = self.anomaly_detector.predict(features)[0] == -1
                anomaly_score = self.anomaly_detector.score_samples(features)[0]
                
                # Clamp score to 0-100 range
                score = max(0, min(100, score))
                
                # Determine sustainability tier
                tier = self._determine_tier(score)
                
                result = {
                    "operation_id": mining_data.get("id", "unknown"),
                    "sustainability_score": score,
                    "sustainability_tier": tier,
                    "is_anomaly": is_anomaly,
                    "anomaly_score": anomaly_score,
                    "scoring_method": "ml_model"
                }
                
                # Add suggestions if not an anomaly
                if not is_anomaly:
                    result["improvement_suggestions"] = self._generate_suggestions(features[0])
                else:
                    result["improvement_suggestions"] = [
                        "Verify reported data as unusual patterns were detected."
                    ]
                
                return result
            else:
                # Fallback to rule-based scoring
                return self._rule_based_scoring(mining_data, carbon_data, features)
        
        except Exception as e:
            logger.error(f"Error scoring operation: {str(e)}")
            return {
                "operation_id": mining_data.get("id", "unknown"),
                "sustainability_score": 0,
                "sustainability_tier": "ERROR",
                "error": str(e)
            }
    
    def _rule_based_scoring(self, mining_data: Dict, carbon_data: Dict, features: np.ndarray) -> Dict:
        """
        Fallback rule-based scoring when ML model is not trained.
        
        Args:
            mining_data: Dictionary with mining operation data.
            carbon_data: Dictionary with carbon footprint data.
            features: Extracted feature array.
            
        Returns:
            Dictionary with score results.
        """
        # Extract feature components
        renewable_score = features[0][0]
        efficiency_score = features[0][1]
        carbon_score = 1.0 - features[0][2]  # Invert as lower carbon is better
        offset_score = features[0][3]
        initiatives_score = features[0][4]
        location_factor = features[0][5]
        
        # Weights from original model
        weights = {
            "renewable_energy_percentage": 0.35,
            "energy_efficiency_rating": 0.25,
            "carbon_footprint": 0.20,
            "carbon_offset_percentage": 0.10,
            "sustainability_initiatives": 0.05,
            "location_factor": 0.05
        }
        
        # Calculate weighted score
        weighted_score = (
            weights["renewable_energy_percentage"] * renewable_score +
            weights["energy_efficiency_rating"] * efficiency_score +
            weights["carbon_footprint"] * carbon_score +
            weights["carbon_offset_percentage"] * offset_score +
            weights["sustainability_initiatives"] * initiatives_score +
            weights["location_factor"] * location_factor
        )
        
        # Carbon penalty for high emitters
        carbon_penalty = np.exp(features[0][2] * 0.01) - 1
        
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
            "improvement_suggestions": self._generate_suggestions(features[0]),
            "scoring_method": "rule_based"
        }
    
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
    
    def _generate_suggestions(self, features: np.ndarray) -> List[str]:
        """
        Generate improvement suggestions based on feature values.
        
        Args:
            features: Feature vector with normalized values.
            
        Returns:
            List of improvement suggestions.
        """
        suggestions = []
        
        renewable_score = features[0]
        efficiency_score = features[1]
        carbon_score = features[2]  # This is normalized carbon (higher is worse)
        offset_score = features[3]
        initiatives_score = features[4]
        
        if renewable_score < 0.5:
            suggestions.append(
                "Increase renewable energy usage through direct purchases, "
                "RECs, or on-site generation."
            )
        
        if efficiency_score < 0.6:
            suggestions.append(
                "Upgrade to more energy-efficient mining hardware or optimize "
                "cooling systems for better efficiency."
            )
        
        if carbon_score > 0.5:  # Remember higher normalized carbon is worse
            suggestions.append(
                "Reduce carbon footprint by optimizing operations or "
                "relocating to areas with cleaner energy."
            )
        
        if offset_score < 0.3:
            suggestions.append(
                "Implement carbon offset programs to balance unavoidable emissions "
                "through verified carbon credit purchases."
            )
        
        if initiatives_score < 0.4:
            suggestions.append(
                "Develop and implement sustainability initiatives like waste heat recovery, "
                "facility optimization, or renewable energy partnerships."
            )
            
        return suggestions 