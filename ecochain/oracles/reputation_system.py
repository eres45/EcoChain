"""
Reputation System for Oracle Network

This module implements a reputation system for data providers
in the EcoChain Guardian oracle network, ensuring data quality
and incentivizing accurate reporting.
"""

import logging
import time
import math
import json
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
import statistics

logger = logging.getLogger(__name__)

@dataclass
class EntityRecord:
    """Record of an entity's reputation and history."""
    entity_id: str
    score: float = 50.0  # Default starting score
    history: List[Dict] = field(default_factory=list)
    accuracy_history: List[float] = field(default_factory=list)
    last_updated: float = field(default_factory=lambda: time.time())
    creation_time: float = field(default_factory=lambda: time.time())

class ReputationSystem:
    """
    Reputation system for the oracle network data providers.
    
    This system tracks the reputation of data providers based on their
    accuracy, consistency, and participation in the network.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the reputation system.
        
        Args:
            config: Configuration dictionary for the system.
        """
        self.config = config or {}
        self.entities = {}  # entity_id -> EntityRecord
        self.initialized = False
        
        # Reputation parameters
        self.min_score = self.config.get('min_score', 0.0)
        self.max_score = self.config.get('max_score', 100.0)
        self.default_score = self.config.get('default_score', 50.0)
        
        # Score adjustment parameters
        self.accuracy_weight = self.config.get('accuracy_weight', 2.0)
        self.consistency_weight = self.config.get('consistency_weight', 1.0)
        self.participation_weight = self.config.get('participation_weight', 0.5)
        self.time_decay_factor = self.config.get('time_decay_factor', 0.995)  # Score decay per day
        
        # Load existing data if available
        self._load_data()
        self.initialized = True
    
    def _load_data(self) -> None:
        """Load reputation data from storage."""
        try:
            data_file = self.config.get('data_file')
            if not data_file:
                return
            
            with open(data_file, 'r') as f:
                data = json.load(f)
                
                for entity_id, record in data.items():
                    self.entities[entity_id] = EntityRecord(
                        entity_id=entity_id,
                        score=record.get('score', self.default_score),
                        history=record.get('history', []),
                        accuracy_history=record.get('accuracy_history', []),
                        last_updated=record.get('last_updated', time.time()),
                        creation_time=record.get('creation_time', time.time())
                    )
            
            logger.info(f"Loaded reputation data for {len(self.entities)} entities")
        except Exception as e:
            logger.warning(f"Could not load reputation data: {e}")
    
    def _save_data(self) -> None:
        """Save reputation data to storage."""
        try:
            data_file = self.config.get('data_file')
            if not data_file:
                return
            
            data = {}
            for entity_id, record in self.entities.items():
                data[entity_id] = {
                    'score': record.score,
                    'history': record.history,
                    'accuracy_history': record.accuracy_history,
                    'last_updated': record.last_updated,
                    'creation_time': record.creation_time
                }
            
            with open(data_file, 'w') as f:
                json.dump(data, f)
            
            logger.debug(f"Saved reputation data for {len(self.entities)} entities")
        except Exception as e:
            logger.warning(f"Could not save reputation data: {e}")
    
    def add_entity(self, entity_id: str, initial_score: Optional[float] = None) -> bool:
        """
        Add a new entity to the reputation system.
        
        Args:
            entity_id: ID of the entity.
            initial_score: Optional initial score for the entity.
            
        Returns:
            True if the entity was added, False if it already exists.
        """
        if entity_id in self.entities:
            logger.warning(f"Entity {entity_id} already exists in reputation system")
            return False
        
        score = initial_score if initial_score is not None else self.default_score
        score = max(self.min_score, min(self.max_score, score))
        
        self.entities[entity_id] = EntityRecord(
            entity_id=entity_id,
            score=score
        )
        
        logger.info(f"Added entity {entity_id} to reputation system with score {score}")
        
        if self.initialized:
            self._save_data()
        
        return True
    
    def has_entity(self, entity_id: str) -> bool:
        """
        Check if an entity exists in the reputation system.
        
        Args:
            entity_id: ID of the entity.
            
        Returns:
            True if the entity exists, False otherwise.
        """
        return entity_id in self.entities
    
    def get_score(self, entity_id: str) -> float:
        """
        Get the reputation score of an entity.
        
        Args:
            entity_id: ID of the entity.
            
        Returns:
            The reputation score, or default score if the entity doesn't exist.
        """
        if entity_id not in self.entities:
            logger.warning(f"Entity {entity_id} not found in reputation system")
            return self.default_score
        
        return self.entities[entity_id].score
    
    def update_score(self, entity_id: str, delta: float, 
                    reason: str = None, details: Dict = None) -> float:
        """
        Update the reputation score of an entity.
        
        Args:
            entity_id: ID of the entity.
            delta: Score adjustment amount.
            reason: Reason for the adjustment.
            details: Additional details about the adjustment.
            
        Returns:
            The new reputation score.
        """
        if entity_id not in self.entities:
            logger.warning(f"Entity {entity_id} not found in reputation system")
            self.add_entity(entity_id)
        
        record = self.entities[entity_id]
        old_score = record.score
        
        # Apply time decay since last update
        days_since_update = (time.time() - record.last_updated) / (24 * 3600)
        if days_since_update > 0:
            time_decay = self.time_decay_factor ** days_since_update
            record.score *= time_decay
        
        # Apply score adjustment
        record.score += delta
        record.score = max(self.min_score, min(self.max_score, record.score))
        
        # Update record
        record.last_updated = time.time()
        
        # Add to history
        history_entry = {
            "timestamp": time.time(),
            "old_score": old_score,
            "delta": delta,
            "new_score": record.score,
            "reason": reason,
            "details": details
        }
        record.history.append(history_entry)
        
        # Keep history size manageable
        max_history = self.config.get('max_history_size', 100)
        if len(record.history) > max_history:
            record.history = record.history[-max_history:]
        
        logger.debug(f"Updated score for {entity_id}: {old_score:.2f} -> {record.score:.2f} ({delta:+.2f})")
        
        self._save_data()
        
        return record.score
    
    def record_accuracy(self, entity_id: str, accuracy: float, 
                       weight: float = 1.0) -> float:
        """
        Record the accuracy of an entity and update its reputation accordingly.
        
        Args:
            entity_id: ID of the entity.
            accuracy: Accuracy value (0.0 to 1.0).
            weight: Weight of this accuracy measurement.
            
        Returns:
            The new reputation score.
        """
        if entity_id not in self.entities:
            logger.warning(f"Entity {entity_id} not found in reputation system")
            self.add_entity(entity_id)
        
        record = self.entities[entity_id]
        
        # Add to accuracy history
        record.accuracy_history.append(accuracy)
        
        # Keep history size manageable
        max_history = self.config.get('max_accuracy_history', 100)
        if len(record.accuracy_history) > max_history:
            record.accuracy_history = record.accuracy_history[-max_history:]
        
        # Calculate score delta based on accuracy
        # Accuracy 0.5 is neutral, above is good, below is bad
        accuracy_factor = (accuracy - 0.5) * 2.0  # -1.0 to 1.0
        delta = accuracy_factor * self.accuracy_weight * weight
        
        # Apply consistency bonus/penalty if we have enough history
        if len(record.accuracy_history) >= 5:
            recent_accuracy = record.accuracy_history[-5:]
            consistency = 1.0 - statistics.stdev(recent_accuracy) * 2.0  # Higher consistency is better
            consistency_factor = (consistency - 0.5) * 2.0  # -1.0 to 1.0
            delta += consistency_factor * self.consistency_weight * weight
        
        # Update score
        details = {"accuracy": accuracy, "consistency": consistency if 'consistency' in locals() else None}
        return self.update_score(entity_id, delta, reason="accuracy", details=details)
    
    def get_entities_above_threshold(self, threshold: float) -> List[str]:
        """
        Get a list of entities with scores above a threshold.
        
        Args:
            threshold: Score threshold.
            
        Returns:
            List of entity IDs.
        """
        return [entity_id for entity_id, record in self.entities.items() if record.score >= threshold]
    
    def get_top_entities(self, count: int) -> List[Dict]:
        """
        Get the top-ranked entities by score.
        
        Args:
            count: Number of entities to return.
            
        Returns:
            List of dictionaries with entity information.
        """
        sorted_entities = sorted(
            self.entities.items(),
            key=lambda x: x[1].score,
            reverse=True
        )
        
        result = []
        for entity_id, record in sorted_entities[:count]:
            result.append({
                "entity_id": entity_id,
                "score": record.score,
                "last_updated": record.last_updated,
                "creation_time": record.creation_time,
                "history_length": len(record.history),
                "accuracy_history_length": len(record.accuracy_history)
            })
        
        return result
    
    def get_entity_details(self, entity_id: str) -> Dict:
        """
        Get detailed information about an entity.
        
        Args:
            entity_id: ID of the entity.
            
        Returns:
            Dictionary with entity details.
        """
        if entity_id not in self.entities:
            logger.warning(f"Entity {entity_id} not found in reputation system")
            return {}
        
        record = self.entities[entity_id]
        
        # Calculate statistics
        avg_accuracy = statistics.mean(record.accuracy_history) if record.accuracy_history else None
        consistency = 1.0 - statistics.stdev(record.accuracy_history) * 2.0 if len(record.accuracy_history) >= 2 else None
        
        return {
            "entity_id": entity_id,
            "score": record.score,
            "last_updated": record.last_updated,
            "creation_time": record.creation_time,
            "age_days": (time.time() - record.creation_time) / (24 * 3600),
            "history": record.history[-10:],  # Return only the most recent entries
            "history_length": len(record.history),
            "avg_accuracy": avg_accuracy,
            "consistency": consistency,
            "accuracy_samples": len(record.accuracy_history)
        }
    
    def remove_entity(self, entity_id: str) -> bool:
        """
        Remove an entity from the reputation system.
        
        Args:
            entity_id: ID of the entity to remove.
            
        Returns:
            True if the entity was removed, False if it doesn't exist.
        """
        if entity_id not in self.entities:
            logger.warning(f"Entity {entity_id} not found in reputation system")
            return False
        
        del self.entities[entity_id]
        logger.info(f"Removed entity {entity_id} from reputation system")
        
        self._save_data()
        
        return True
    
    def decay_scores(self) -> None:
        """
        Apply time decay to all scores.
        
        This method applies the time decay factor to all scores to
        gradually reduce reputation scores of inactive entities.
        """
        current_time = time.time()
        
        for entity_id, record in self.entities.items():
            days_since_update = (current_time - record.last_updated) / (24 * 3600)
            if days_since_update > 0:
                old_score = record.score
                time_decay = self.time_decay_factor ** days_since_update
                record.score *= time_decay
                record.score = max(self.min_score, min(self.max_score, record.score))
                record.last_updated = current_time
                
                if abs(old_score - record.score) > 0.1:
                    logger.debug(f"Decayed score for {entity_id}: {old_score:.2f} -> {record.score:.2f}")
        
        self._save_data()
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the reputation system.
        
        Returns:
            Dictionary with system statistics.
        """
        if not self.entities:
            return {
                "entity_count": 0,
                "avg_score": None,
                "min_score": None,
                "max_score": None
            }
        
        scores = [record.score for record in self.entities.values()]
        
        return {
            "entity_count": len(self.entities),
            "avg_score": statistics.mean(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "median_score": statistics.median(scores),
            "score_stdev": statistics.stdev(scores) if len(scores) > 1 else 0.0
        } 
 
 