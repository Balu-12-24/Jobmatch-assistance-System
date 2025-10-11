from typing import List, Optional, Dict
import numpy as np
from sqlalchemy.orm import Session
from app.models.job import Job
from app.services.vector_store import get_vector_store
from app.services.embedding_generator import get_embedding_generator
import logging

logger = logging.getLogger(__name__)


class JobMatch:
    """Represents a job match with compatibility score and skill analysis"""
    
    def __init__(
        self,
        job: Job,
        compatibility_score: float,
        matching_skills: List[str],
        missing_skills: List[str]
    ):
        self.job = job
        self.compatibility_score = compatibility_score
        self.matching_skills = matching_skills
        self.missing_skills = missing_skills


class SkillGap:
    """Represents skill gap analysis"""
    
    def __init__(
        self,
        matching_skills: List[str],
        missing_skills: List[str],
        match_percentage: float
    ):
        self.matching_skills = matching_skills
        self.missing_skills = missing_skills
        self.match_percentage = match_percentage


class JobMatcher:
    """
    Job matching service using vector similarity and skill analysis.
    """
    
    def __init__(self):
        self.vector_store = get_vector_store()
        self.embedding_gen = get_embedding_generator()
    
    def find_matches(
        self,
        resume_embedding: np.ndarray,
        user_preferences: Optional[Dict] = None,
        top_k: int = 10,
        db: Session = None
    ) -> List[JobMatch]:
        """
        Find matching jobs for a resume.
        
        Args:
            resume_embedding: Resume embedding vector
            user_preferences: Optional filters (location, remote_option, etc.)
            top_k: Number of matches to return
            db: Database session
            
        Returns:
            List of JobMatch objects sorted by compatibility score
        """
        try:
            # Build filter from preferences
            filter_dict = {}
            if user_preferences:
                if user_preferences.get('location'):
                    filter_dict['location'] = user_preferences['location']
                if user_preferences.get('remote_option'):
                    filter_dict['remote_option'] = user_preferences['remote_option']
                if user_preferences.get('industry'):
                    filter_dict['industry'] = user_preferences['industry']
            
            # Search for similar jobs in vector store
            logger.info(f"Searching for top {top_k} job matches")
            results = self.vector_store.search(
                query_vector=resume_embedding,
                k=top_k,
                filter_dict=filter_dict if filter_dict else None
            )
            
            # Get job details from database and create JobMatch objects
            job_matches = []
            for vector_id, similarity_score, metadata in results:
                job_id = metadata.get('job_id')
                
                if db and job_id:
                    job = db.query(Job).filter(Job.id == job_id).first()
                    if job:
                        # Convert similarity to 0-100 compatibility score
                        compatibility_score = self.calculate_compatibility_score(
                            resume_embedding,
                            similarity_score
                        )
                        
                        # For now, use empty skill lists (will be populated by caller)
                        job_match = JobMatch(
                            job=job,
                            compatibility_score=compatibility_score,
                            matching_skills=[],
                            missing_skills=[]
                        )
                        job_matches.append(job_match)
            
            logger.info(f"Found {len(job_matches)} matching jobs")
            return job_matches
            
        except Exception as e:
            logger.error(f"Error finding job matches: {e}")
            raise
    
    def calculate_compatibility_score(
        self,
        resume_embedding: np.ndarray,
        similarity_score: float
    ) -> float:
        """
        Convert cosine similarity to 0-100 compatibility score.
        
        Args:
            resume_embedding: Resume embedding (not used in basic version)
            similarity_score: Cosine similarity from vector search (-1 to 1)
            
        Returns:
            Compatibility score (0-100)
        """
        # Cosine similarity ranges from -1 to 1
        # Convert to 0-100 scale
        # Typically, similarity will be between 0 and 1 for relevant matches
        score = (similarity_score + 1) / 2 * 100
        
        # Clamp to 0-100
        score = max(0, min(100, score))
        
        return round(score, 1)
    
    def identify_skill_gaps(
        self,
        resume_skills: List[str],
        job_requirements: str
    ) -> SkillGap:
        """
        Identify matching and missing skills.
        
        Args:
            resume_skills: List of skills from resume
            job_requirements: Job requirements text
            
        Returns:
            SkillGap object with analysis
        """
        if not resume_skills:
            return SkillGap([], [], 0.0)
        
        # Normalize skills for comparison
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        job_req_lower = job_requirements.lower() if job_requirements else ""
        
        # Find matching skills
        matching_skills = []
        for skill in resume_skills:
            if skill.lower() in job_req_lower:
                matching_skills.append(skill)
        
        # Extract potential missing skills from job requirements
        # This is a simple implementation - could be enhanced with NLP
        common_skills = [
            "python", "java", "javascript", "typescript", "react", "node.js",
            "aws", "docker", "kubernetes", "sql", "mongodb", "git",
            "machine learning", "data analysis", "agile", "leadership"
        ]
        
        missing_skills = []
        for skill in common_skills:
            if skill in job_req_lower and skill not in resume_skills_lower:
                missing_skills.append(skill.title())
        
        # Calculate match percentage
        total_relevant_skills = len(matching_skills) + len(missing_skills)
        match_percentage = (
            (len(matching_skills) / total_relevant_skills * 100)
            if total_relevant_skills > 0
            else 0.0
        )
        
        return SkillGap(
            matching_skills=matching_skills,
            missing_skills=missing_skills,
            match_percentage=round(match_percentage, 1)
        )
