from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import logging

logger = logging.getLogger(__name__)


class SalaryPredictor:
    """
    Salary prediction using Random Forest Regressor.
    Predicts salary based on experience, skills, education, location, and industry.
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize salary predictor.
        
        Args:
            model_path: Path to saved model file (optional)
        """
        self.model = None
        self.education_encoder = LabelEncoder()
        self.location_encoder = LabelEncoder()
        self.industry_encoder = LabelEncoder()
        self.is_trained = False
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
    
    def train_model(self, training_data: pd.DataFrame):
        """
        Train the salary prediction model.
        
        Args:
            training_data: DataFrame with columns:
                - experience_years
                - skill_count
                - education_level
                - location
                - industry
                - salary
        """
        try:
            logger.info("Training salary prediction model...")
            
            # Encode categorical variables
            training_data['education_encoded'] = self.education_encoder.fit_transform(
                training_data['education_level']
            )
            training_data['location_encoded'] = self.location_encoder.fit_transform(
                training_data['location']
            )
            training_data['industry_encoded'] = self.industry_encoder.fit_transform(
                training_data['industry']
            )
            
            # Prepare features and target
            X = training_data[[
                'experience_years',
                'skill_count',
                'education_encoded',
                'location_encoded',
                'industry_encoded'
            ]]
            y = training_data['salary']
            
            # Train Random Forest model
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            self.model.fit(X, y)
            
            self.is_trained = True
            logger.info("Model trained successfully")
            
            # Log feature importances
            feature_names = ['experience_years', 'skill_count', 'education', 'location', 'industry']
            importances = self.model.feature_importances_
            for name, importance in zip(feature_names, importances):
                logger.info(f"Feature importance - {name}: {importance:.3f}")
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            raise
    
    def predict_salary(
        self,
        experience_years: int,
        skill_count: int,
        education_level: str,
        location: str,
        industry: str
    ) -> dict:
        """
        Predict salary for given features.
        
        Args:
            experience_years: Years of experience
            skill_count: Number of skills
            education_level: Education level (bachelor, master, phd)
            location: Job location
            industry: Industry sector
            
        Returns:
            Dictionary with predicted_min, predicted_max, confidence
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train_model() first.")
        
        try:
            # Handle unknown categories
            education_level = self._handle_unknown_category(
                education_level, self.education_encoder, 'bachelor'
            )
            location = self._handle_unknown_category(
                location, self.location_encoder, 'San Francisco'
            )
            industry = self._handle_unknown_category(
                industry, self.industry_encoder, 'technology'
            )
            
            # Encode categorical variables
            education_encoded = self.education_encoder.transform([education_level])[0]
            location_encoded = self.location_encoder.transform([location])[0]
            industry_encoded = self.industry_encoder.transform([industry])[0]
            
            # Prepare features
            features = np.array([[
                experience_years,
                skill_count,
                education_encoded,
                location_encoded,
                industry_encoded
            ]])
            
            # Predict
            predicted_salary = self.model.predict(features)[0]
            
            # Calculate confidence interval using tree predictions
            tree_predictions = np.array([
                tree.predict(features)[0]
                for tree in self.model.estimators_
            ])
            std_dev = np.std(tree_predictions)
            
            # Create salary range (mean ± std_dev)
            predicted_min = int(max(0, predicted_salary - std_dev))
            predicted_max = int(predicted_salary + std_dev)
            
            # Calculate confidence (inverse of coefficient of variation)
            confidence = min(100, max(0, 100 - (std_dev / predicted_salary * 100)))
            
            return {
                "predicted_min": predicted_min,
                "predicted_max": predicted_max,
                "predicted_mean": int(predicted_salary),
                "confidence": round(confidence, 1),
                "percentile_25": int(predicted_salary - std_dev * 0.67),
                "percentile_75": int(predicted_salary + std_dev * 0.67)
            }
            
        except Exception as e:
            logger.error(f"Error predicting salary: {e}")
            # Return default range on error
            return {
                "predicted_min": 70000,
                "predicted_max": 120000,
                "predicted_mean": 95000,
                "confidence": 50.0,
                "percentile_25": 80000,
                "percentile_75": 110000
            }
    
    def _handle_unknown_category(self, value: str, encoder: LabelEncoder, default: str) -> str:
        """Handle unknown categories by using default value"""
        if value not in encoder.classes_:
            logger.warning(f"Unknown category '{value}', using default '{default}'")
            return default
        return value
    
    def save_model(self, path: str):
        """Save trained model to disk"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        model_data = {
            'model': self.model,
            'education_encoder': self.education_encoder,
            'location_encoder': self.location_encoder,
            'industry_encoder': self.industry_encoder
        }
        
        joblib.dump(model_data, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load trained model from disk"""
        try:
            model_data = joblib.load(path)
            self.model = model_data['model']
            self.education_encoder = model_data['education_encoder']
            self.location_encoder = model_data['location_encoder']
            self.industry_encoder = model_data['industry_encoder']
            self.is_trained = True
            logger.info(f"Model loaded from {path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise


# Global instance
_salary_predictor = None


def get_salary_predictor() -> SalaryPredictor:
    """
    Get or create the global salary predictor instance.
    Trains model on first call.
    
    Returns:
        SalaryPredictor instance
    """
    global _salary_predictor
    if _salary_predictor is None:
        _salary_predictor = SalaryPredictor()
        
        # Train model with sample data
        try:
            data_path = Path(__file__).parent.parent.parent / "data" / "salary_training_data.csv"
            if data_path.exists():
                training_data = pd.read_csv(data_path)
                _salary_predictor.train_model(training_data)
                logger.info("Salary predictor initialized and trained")
            else:
                logger.warning(f"Training data not found at {data_path}")
        except Exception as e:
            logger.error(f"Error initializing salary predictor: {e}")
    
    return _salary_predictor
