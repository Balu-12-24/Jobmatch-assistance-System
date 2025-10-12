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
    Enhanced salary prediction using Random Forest Regressor for Indian market.
    Predicts salary based on experience, skills, education, location, industry,
    city tier, company type, and education institution.
    """
    
    def __init__(self, model_path: str = None, country: str = 'India'):
        """
        Initialize salary predictor.
        
        Args:
            model_path: Path to saved model file (optional)
            country: Country for salary predictions (default: India)
        """
        self.model = None
        self.country = country
        self.education_encoder = LabelEncoder()
        self.location_encoder = LabelEncoder()
        self.industry_encoder = LabelEncoder()
        self.company_type_encoder = LabelEncoder()
        self.education_inst_encoder = LabelEncoder()
        self.is_trained = False
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
    
    def train_model(self, training_data: pd.DataFrame):
        """
        Train the enhanced salary prediction model with Indian market features.
        
        Args:
            training_data: DataFrame with columns:
                - experience_years
                - skill_count
                - education_level
                - education_institution (for IIT/NIT/IIM recognition)
                - location
                - city_tier (1, 2, 3)
                - company_type (MNC, startup, service, product, BPO, KPO)
                - industry
                - salary_inr (target variable)
        """
        try:
            logger.info(f"Training salary prediction model for {self.country}...")
            
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
            
            # Encode Indian market specific features
            if 'company_type' in training_data.columns:
                training_data['company_type_encoded'] = self.company_type_encoder.fit_transform(
                    training_data['company_type']
                )
            else:
                training_data['company_type_encoded'] = 0
            
            if 'education_institution' in training_data.columns:
                training_data['education_inst_encoded'] = self.education_inst_encoder.fit_transform(
                    training_data['education_institution']
                )
            else:
                training_data['education_inst_encoded'] = 0
            
            # Prepare features
            feature_columns = [
                'experience_years',
                'skill_count',
                'education_encoded',
                'location_encoded',
                'industry_encoded'
            ]
            
            # Add Indian market features if available
            if 'city_tier' in training_data.columns:
                feature_columns.append('city_tier')
            if 'company_type_encoded' in training_data.columns:
                feature_columns.append('company_type_encoded')
            if 'education_inst_encoded' in training_data.columns:
                feature_columns.append('education_inst_encoded')
            
            X = training_data[feature_columns]
            
            # Use salary_inr for Indian market, fallback to salary
            if 'salary_inr' in training_data.columns:
                y = training_data['salary_inr']
            else:
                y = training_data['salary']
            
            # Train Random Forest model with enhanced parameters
            self.model = RandomForestRegressor(
                n_estimators=150,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            self.model.fit(X, y)
            
            self.is_trained = True
            logger.info("Model trained successfully")
            
            # Log feature importances
            importances = self.model.feature_importances_
            for name, importance in zip(feature_columns, importances):
                logger.info(f"Feature importance - {name}: {importance:.3f}")
            
            # Log model performance
            train_score = self.model.score(X, y)
            logger.info(f"Training R² score: {train_score:.3f}")
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            raise
    
    def predict_salary(
        self,
        experience_years: int,
        skill_count: int,
        education_level: str,
        location: str,
        industry: str,
        city_tier: int = 1,
        company_type: str = 'service',
        education_institution: str = 'Tier 2'
    ) -> dict:
        """
        Predict salary for given features with Indian market support.
        
        Args:
            experience_years: Years of experience
            skill_count: Number of skills
            education_level: Education level (B.Tech, MBA, etc.)
            location: Job location
            industry: Industry sector
            city_tier: City tier (1, 2, 3) for Indian cities
            company_type: Company type (MNC, startup, service, product, BPO, KPO)
            education_institution: Education institution (IIT, NIT, IIM, etc.)
            
        Returns:
            Dictionary with predicted_min, predicted_max, confidence, and Indian formats
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train_model() first.")
        
        try:
            # Handle unknown categories
            education_level = self._handle_unknown_category(
                education_level, self.education_encoder, 'B.Tech'
            )
            location = self._handle_unknown_category(
                location, self.location_encoder, 'Bangalore'
            )
            industry = self._handle_unknown_category(
                industry, self.industry_encoder, 'IT'
            )
            company_type = self._handle_unknown_category(
                company_type, self.company_type_encoder, 'service'
            )
            education_institution = self._handle_unknown_category(
                education_institution, self.education_inst_encoder, 'Tier 2'
            )
            
            # Encode categorical variables
            education_encoded = self.education_encoder.transform([education_level])[0]
            location_encoded = self.location_encoder.transform([location])[0]
            industry_encoded = self.industry_encoder.transform([industry])[0]
            company_type_encoded = self.company_type_encoder.transform([company_type])[0]
            education_inst_encoded = self.education_inst_encoder.transform([education_institution])[0]
            
            # Prepare features (match training features)
            feature_list = [
                experience_years,
                skill_count,
                education_encoded,
                location_encoded,
                industry_encoded
            ]
            
            # Add Indian market features if model was trained with them
            if len(self.company_type_encoder.classes_) > 0:
                feature_list.extend([city_tier, company_type_encoded, education_inst_encoded])
            
            features = np.array([feature_list])
            
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
            
            result = {
                "predicted_min": predicted_min,
                "predicted_max": predicted_max,
                "predicted_mean": int(predicted_salary),
                "confidence": round(confidence, 1),
                "percentile_25": int(predicted_salary - std_dev * 0.67),
                "percentile_75": int(predicted_salary + std_dev * 0.67)
            }
            
            # Add Indian salary formats if applicable
            if self.country == 'India':
                indian_format = self.format_indian_salary(int(predicted_salary))
                result.update(indian_format)
            
            return result
            
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
    
    def format_indian_salary(self, salary_inr: int) -> dict:
        """
        Convert INR salary to LPA (Lakhs Per Annum) and monthly CTC format.
        
        Args:
            salary_inr: Annual salary in INR
            
        Returns:
            Dictionary with LPA and monthly CTC formats
        """
        salary_lpa = round(salary_inr / 100000, 2)
        monthly_ctc = round(salary_inr / 12, 0)
        
        return {
            "salary_lpa": salary_lpa,
            "salary_lpa_formatted": f"₹{salary_lpa} LPA",
            "monthly_ctc": int(monthly_ctc),
            "monthly_ctc_formatted": f"₹{monthly_ctc:,}/month",
            "annual_inr": salary_inr,
            "annual_inr_formatted": f"₹{salary_inr:,}/year"
        }
    
    def _handle_unknown_category(self, value: str, encoder: LabelEncoder, default: str) -> str:
        """Handle unknown categories by using default value"""
        if not hasattr(encoder, 'classes_') or len(encoder.classes_) == 0:
            return default
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
            'country': self.country,
            'education_encoder': self.education_encoder,
            'location_encoder': self.location_encoder,
            'industry_encoder': self.industry_encoder,
            'company_type_encoder': self.company_type_encoder,
            'education_inst_encoder': self.education_inst_encoder
        }
        
        joblib.dump(model_data, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load trained model from disk"""
        try:
            model_data = joblib.load(path)
            self.model = model_data['model']
            self.country = model_data.get('country', 'India')
            self.education_encoder = model_data['education_encoder']
            self.location_encoder = model_data['location_encoder']
            self.industry_encoder = model_data['industry_encoder']
            self.company_type_encoder = model_data.get('company_type_encoder', LabelEncoder())
            self.education_inst_encoder = model_data.get('education_inst_encoder', LabelEncoder())
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
    Trains model on first call with Indian salary data.
    
    Returns:
        SalaryPredictor instance
    """
    global _salary_predictor
    if _salary_predictor is None:
        _salary_predictor = SalaryPredictor(country='India')
        
        # Train model with Indian salary data
        try:
            # Try Indian salary data first
            data_path = Path(__file__).parent.parent.parent / "data" / "indian_salary_training_data.csv"
            if data_path.exists():
                training_data = pd.read_csv(data_path)
                _salary_predictor.train_model(training_data)
                logger.info("Salary predictor initialized and trained with Indian data")
            else:
                # Fallback to generic salary data
                data_path = Path(__file__).parent.parent.parent / "data" / "salary_training_data.csv"
                if data_path.exists():
                    training_data = pd.read_csv(data_path)
                    _salary_predictor.train_model(training_data)
                    logger.info("Salary predictor initialized and trained with generic data")
                else:
                    logger.warning(f"Training data not found at {data_path}")
        except Exception as e:
            logger.error(f"Error initializing salary predictor: {e}")
    
    return _salary_predictor
