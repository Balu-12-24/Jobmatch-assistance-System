"""
Script to train and save the salary prediction model.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from app.services.salary_predictor import SalaryPredictor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Train and save the salary prediction model"""
    try:
        logger.info("Loading Indian salary training data...")
        
        # Load training data
        data_path = Path(__file__).parent.parent / "data" / "indian_salary_training_data.csv"
        
        if not data_path.exists():
            logger.error(f"Training data not found at {data_path}")
            logger.info("Please run: python backend/scripts/generate_salary_data.py")
            return
        
        training_data = pd.read_csv(data_path)
        logger.info(f"Loaded {len(training_data)} training samples")
        
        # Display data info
        logger.info(f"Columns: {list(training_data.columns)}")
        logger.info(f"Salary range: ₹{training_data['salary_inr'].min():,} - ₹{training_data['salary_inr'].max():,}")
        
        # Initialize and train model
        logger.info("Training salary prediction model...")
        predictor = SalaryPredictor(country='India')
        predictor.train_model(training_data)
        
        # Save model
        model_path = Path(__file__).parent.parent / "models" / "salary_predictor_india.pkl"
        model_path.parent.mkdir(exist_ok=True)
        
        predictor.save_model(str(model_path))
        logger.info(f"Model saved to {model_path}")
        
        # Test predictions
        logger.info("\nTesting model with sample predictions:")
        
        test_cases = [
            {
                "title": "Software Engineer (Fresher, Bangalore, Service)",
                "experience_years": 0,
                "skill_count": 5,
                "education_level": "B.Tech",
                "location": "Bangalore",
                "industry": "IT",
                "city_tier": 1,
                "company_type": "service",
                "education_institution": "Tier 2"
            },
            {
                "title": "Senior Software Engineer (5 years, Bangalore, MNC)",
                "experience_years": 5,
                "skill_count": 8,
                "education_level": "B.Tech",
                "location": "Bangalore",
                "industry": "IT",
                "city_tier": 1,
                "company_type": "MNC",
                "education_institution": "IIT"
            },
            {
                "title": "Data Scientist (3 years, Mumbai, Product)",
                "experience_years": 3,
                "skill_count": 7,
                "education_level": "M.Tech",
                "location": "Mumbai",
                "industry": "IT",
                "city_tier": 1,
                "company_type": "product",
                "education_institution": "NIT"
            }
        ]
        
        for test in test_cases:
            title = test.pop("title")
            prediction = predictor.predict_salary(**test)
            
            logger.info(f"\n{title}:")
            logger.info(f"  Predicted: {prediction['salary_lpa_formatted']}")
            logger.info(f"  Range: ₹{prediction['predicted_min']:,} - ₹{prediction['predicted_max']:,}")
            logger.info(f"  Monthly: {prediction['monthly_ctc_formatted']}")
            logger.info(f"  Confidence: {prediction['confidence']}%")
        
        logger.info("\n✅ Model training completed successfully!")
        
    except Exception as e:
        logger.error(f"Error training model: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
