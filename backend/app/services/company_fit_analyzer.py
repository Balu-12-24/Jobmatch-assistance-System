from typing import Dict, List, Optional
import numpy as np
from app.services.embedding_generator import get_embedding_generator
import logging

logger = logging.getLogger(__name__)


class CompanyFitScore:
    """Represents company fit analysis"""
    
    def __init__(
        self,
        score: float,
        factors: Dict[str, float],
        explanation: str
    ):
        self.score = score
        self.factors = factors
        self.explanation = explanation


class CompanyFitAnalyzer:
    """
    Analyze company-fit based on user preferences and company characteristics.
    Uses embedding similarity and preference matching.
    """
    
    def __init__(self):
        self.embedding_gen = get_embedding_generator()
    
    def calculate_fit_score(
        self,
        user_preferences: Dict,
        job_description: str,
        company_size: Optional[str] = None,
        remote_option: Optional[str] = None,
        industry: Optional[str] = None
    ) -> CompanyFitScore:
        """
        Calculate company-fit score based on multiple factors.
        
        Args:
            user_preferences: User preferences dict with keys:
                - remote_option: preferred work style
                - company_size: preferred company size
                - industry: preferred industry
                - work_culture: preferred culture keywords
            job_description: Job description text
            company_size: Actual company size
            remote_option: Actual remote option
            industry: Actual industry
            
        Returns:
            CompanyFitScore object with score and explanation
        """
        factors = {}
        explanations = []
        
        # Factor 1: Remote work preference (weight: 30%)
        remote_score = self._calculate_remote_fit(
            user_preferences.get('remote_option'),
            remote_option
        )
        factors['remote_work'] = remote_score
        if remote_score >= 80:
            explanations.append(f"Strong match on remote work preference ({remote_option})")
        elif remote_score >= 50:
            explanations.append(f"Partial match on remote work preference")
        
        # Factor 2: Company size preference (weight: 20%)
        size_score = self._calculate_size_fit(
            user_preferences.get('company_size'),
            company_size
        )
        factors['company_size'] = size_score
        if size_score >= 80:
            explanations.append(f"Matches preferred company size ({company_size})")
        
        # Factor 3: Industry preference (weight: 25%)
        industry_score = self._calculate_industry_fit(
            user_preferences.get('industry'),
            industry
        )
        factors['industry'] = industry_score
        if industry_score >= 80:
            explanations.append(f"Matches preferred industry ({industry})")
        
        # Factor 4: Culture/values match (weight: 25%)
        culture_score = self._calculate_culture_fit(
            user_preferences.get('work_culture', ''),
            job_description
        )
        factors['culture'] = culture_score
        if culture_score >= 70:
            explanations.append("Good cultural alignment based on job description")
        
        # Calculate weighted average
        weights = {
            'remote_work': 0.30,
            'company_size': 0.20,
            'industry': 0.25,
            'culture': 0.25
        }
        
        total_score = sum(factors[key] * weights[key] for key in factors)
        
        # Generate explanation
        if not explanations:
            explanations.append("Moderate fit based on available information")
        
        explanation = ". ".join(explanations) + "."
        
        return CompanyFitScore(
            score=round(total_score, 1),
            factors=factors,
            explanation=explanation
        )
    
    def _calculate_remote_fit(
        self,
        user_preference: Optional[str],
        actual_option: Optional[str]
    ) -> float:
        """Calculate remote work fit score"""
        if not user_preference or not actual_option:
            return 50.0  # Neutral if no preference
        
        user_pref = user_preference.lower()
        actual = actual_option.lower()
        
        # Exact match
        if user_pref == actual:
            return 100.0
        
        # Partial matches
        if user_pref == 'remote':
            if actual == 'hybrid':
                return 70.0
            else:  # onsite
                return 20.0
        elif user_pref == 'hybrid':
            if actual in ['remote', 'onsite']:
                return 60.0
        elif user_pref == 'onsite':
            if actual == 'hybrid':
                return 70.0
            else:  # remote
                return 30.0
        
        return 50.0
    
    def _calculate_size_fit(
        self,
        user_preference: Optional[str],
        actual_size: Optional[str]
    ) -> float:
        """Calculate company size fit score"""
        if not user_preference or not actual_size:
            return 50.0
        
        user_pref = user_preference.lower()
        actual = actual_size.lower()
        
        # Exact match
        if user_pref == actual:
            return 100.0
        
        # Size categories: startup, small, medium, large, enterprise
        size_order = ['startup', 'small', 'medium', 'large', 'enterprise']
        
        try:
            user_idx = size_order.index(user_pref)
            actual_idx = size_order.index(actual)
            
            # Adjacent sizes get 70%, 2 away get 40%, 3+ away get 20%
            diff = abs(user_idx - actual_idx)
            if diff == 1:
                return 70.0
            elif diff == 2:
                return 40.0
            else:
                return 20.0
        except ValueError:
            return 50.0
    
    def _calculate_industry_fit(
        self,
        user_preference: Optional[str],
        actual_industry: Optional[str]
    ) -> float:
        """Calculate industry fit score"""
        if not user_preference or not actual_industry:
            return 50.0
        
        user_pref = user_preference.lower()
        actual = actual_industry.lower()
        
        # Exact match
        if user_pref == actual:
            return 100.0
        
        # Related industries
        related_industries = {
            'technology': ['software', 'artificial intelligence', 'cloud services', 'mobile apps'],
            'artificial intelligence': ['technology', 'machine learning', 'data science'],
            'finance': ['fintech', 'banking', 'investment'],
            'healthcare': ['biotech', 'medical devices', 'pharmaceuticals']
        }
        
        # Check if industries are related
        for key, related in related_industries.items():
            if user_pref == key and actual in related:
                return 75.0
            if actual == key and user_pref in related:
                return 75.0
        
        return 30.0
    
    def _calculate_culture_fit(
        self,
        user_culture_keywords: str,
        job_description: str
    ) -> float:
        """
        Calculate culture fit using embedding similarity.
        
        Args:
            user_culture_keywords: User's preferred culture keywords
            job_description: Job description text
            
        Returns:
            Culture fit score (0-100)
        """
        if not user_culture_keywords or not job_description:
            return 50.0
        
        try:
            # Generate embeddings
            user_embedding = self.embedding_gen.generate_embedding(user_culture_keywords)
            job_embedding = self.embedding_gen.generate_embedding(job_description)
            
            # Calculate similarity
            similarity = self.embedding_gen.compute_similarity(user_embedding, job_embedding)
            
            # Convert to 0-100 scale
            score = (similarity + 1) / 2 * 100
            
            return round(score, 1)
        except Exception as e:
            logger.error(f"Error calculating culture fit: {e}")
            return 50.0


# Global instance
_company_fit_analyzer = None


def get_company_fit_analyzer() -> CompanyFitAnalyzer:
    """
    Get or create the global company fit analyzer instance.
    
    Returns:
        CompanyFitAnalyzer instance
    """
    global _company_fit_analyzer
    if _company_fit_analyzer is None:
        _company_fit_analyzer = CompanyFitAnalyzer()
    return _company_fit_analyzer
