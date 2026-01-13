from sklearn.ensemble import IsolationForest
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
import numpy as np
from typing import List, Dict
import warnings
warnings.filterwarnings('ignore')

class SubscriptionDetector:
    def __init__(self):
        # Pre-trained model for merchant name understanding
        print("Loading Sentence Transformer model...")
        try:
            self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: Failed to load transformer model: {e}")
            self.text_model = None
        
        # Unsupervised anomaly detector for subscription patterns
        self.pattern_detector = IsolationForest(
            contamination=0.15,
            random_state=42,
            n_estimators=100
        )
        
    def cluster_merchants(self, descriptions: List[str]) -> Dict[str, str]:
        """
        Group similar merchant names using semantic embeddings
        Returns: dict mapping original description -> unified name
        """
        if len(descriptions) < 2:
            return {desc: desc for desc in descriptions}
        
        if self.text_model is None:
            return {desc: desc for desc in descriptions}
        
        try:
            embeddings = self.text_model.encode(descriptions)
            clustering = DBSCAN(eps=0.3, min_samples=2, metric='cosine')
            labels = clustering.fit_predict(embeddings)
            
            mapping = {}
            for idx, desc in enumerate(descriptions):
                cluster_id = labels[idx]
                if cluster_id == -1:
                    mapping[desc] = desc
                else:
                    cluster_members = [descriptions[i] for i, l in enumerate(labels) if l == cluster_id]
                    representative = min(cluster_members, key=len)
                    mapping[desc] = representative
            
            return mapping
        except Exception as e:
            print(f"Error in clustering: {e}")
            return {desc: desc for desc in descriptions}
    
    def detect_subscription_pattern(self, features_array):
        """
        Use Isolation Forest to detect if transaction pattern is subscription-like
        Returns: (prediction, score)
        """
        if features_array is None or len(features_array) == 0:
            return -1, -1.0
        
        try:
            prediction = self.pattern_detector.fit_predict(features_array)
            score = self.pattern_detector.score_samples(features_array)
            return int(prediction[0]), float(score[0])
        except Exception as e:
            print(f"Error in pattern detection: {e}")
            return -1, -1.0
    
    def calculate_confidence(self, features_dict, ml_score):
        """
        Calculate confidence score based on ML prediction + feature analysis
        Returns: (confidence_score, confidence_label)
        """
        if features_dict is None:
            return 0.0, "Low"
        
        try:
            confidence_score = 0.0
            
            # Factor 1: ML anomaly score (VERY GENEROUS)
            ml_confidence = (ml_score + 1.0) / 2.0
            confidence_score += ml_confidence * 0.5
            
            # Factor 2: Interval consistency (VERY GENEROUS)
            interval_cv = features_dict.get('interval_cv', 1.0)
            if interval_cv < 0.2:
                confidence_score += 0.25
            elif interval_cv < 0.3:
                confidence_score += 0.15
            elif interval_cv < 0.5:
                confidence_score += 0.10
            
            # Factor 3: Amount consistency (MORE GENEROUS)
            amount_consistency = features_dict.get('amount_consistency', 0.0)
            if amount_consistency > 0.85:
                confidence_score += 0.15
            elif amount_consistency > 0.70:
                confidence_score += 0.10
            
            # Factor 4: Transaction count
            transaction_count = features_dict.get('transaction_count', 0)
            if transaction_count >= 5:
                confidence_score += 0.10
            elif transaction_count >= 3:
                confidence_score += 0.05
            
            confidence_score = max(0.0, min(1.0, confidence_score))
            
            # Convert to label
            if confidence_score >= 0.50:
                return confidence_score, "High"
            elif confidence_score >= 0.25:
                return confidence_score, "Medium"
            else:
                return confidence_score, "Low"
        except Exception as e:
            print(f"Error calculating confidence: {e}")
            return 0.0, "Low"
