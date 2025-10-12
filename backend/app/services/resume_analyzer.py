"""
Resume Analyzer Service
Analyzes resume quality and calculates ATS (Applicant Tracking System) compatibility score.
"""
import re
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class ResumeAnalyzer:
    """
    Analyzes resume structure, content, and formatting to provide ATS score and improvement suggestions.
    """
    
    # Keywords for different industries
    INDUSTRY_KEYWORDS = {
        "IT": [
            "python", "java", "javascript", "react", "node.js", "aws", "docker", "kubernetes",
            "sql", "mongodb", "git", "agile", "rest api", "microservices", "devops", "ci/cd",
            "machine learning", "data science", "tensorflow", "django", "flask", "spring boot"
        ],
        "Finance": [
            "financial analysis", "accounting", "audit", "taxation", "ifrs", "gaap", "excel",
            "financial modeling", "valuation", "risk management", "compliance", "ca", "cfa",
            "investment banking", "equity research", "portfolio management"
        ],
        "Healthcare": [
            "patient care", "clinical", "medical", "nursing", "pharmacy", "diagnosis", "treatment",
            "healthcare", "hospital", "mbbs", "md", "nursing", "pharmaceutical", "medical records"
        ],
        "Manufacturing": [
            "production", "quality control", "lean manufacturing", "six sigma", "iso", "cad",
            "solidworks", "autocad", "supply chain", "inventory", "process improvement"
        ],
        "Sales": [
            "sales", "business development", "crm", "negotiation", "client relationship",
            "revenue", "targets", "b2b", "b2c", "account management", "lead generation"
        ],
        "Marketing": [
            "digital marketing", "seo", "sem", "social media", "content marketing", "analytics",
            "google ads", "facebook ads", "email marketing", "brand management", "campaigns"
        ]
    }
    
    # Action verbs for strong experience descriptions
    ACTION_VERBS = [
        "achieved", "improved", "increased", "decreased", "developed", "implemented",
        "designed", "created", "led", "managed", "optimized", "streamlined", "launched",
        "built", "established", "delivered", "reduced", "enhanced", "transformed"
    ]
    
    # Sections that should be present in a good resume
    REQUIRED_SECTIONS = [
        "experience", "education", "skills", "summary", "objective", "profile"
    ]
    
    # Unnecessary content patterns
    UNNECESSARY_PATTERNS = [
        r"\b(age|date of birth|dob)\b",
        r"\b(marital status|married|single)\b",
        r"\b(father's name|mother's name)\b",
        r"\b(religion|caste)\b",
        r"\b(hobbies|interests)\b.*?(reading|traveling|music|sports)",
        r"\b(photo|photograph|picture)\b",
        r"\b(references available)\b"
    ]
    
    def __init__(self):
        """Initialize the Resume Analyzer"""
        self.logger = logging.getLogger(__name__)
    
    def analyze_resume(self, resume_text: str, parsed_resume: Dict) -> Dict:
        """
        Perform comprehensive resume analysis.
        
        Args:
            resume_text: Raw resume text
            parsed_resume: Parsed resume data with skills, experience, education
            
        Returns:
            Complete resume analysis with ATS score and suggestions
        """
        ats_score = self.calculate_ats_score(resume_text, parsed_resume)
        strong_sections = self.identify_strong_sections(parsed_resume, resume_text)
        weak_sections = self.identify_weak_sections(parsed_resume, resume_text)
        unnecessary_content = self.identify_unnecessary_content(resume_text)
        improvements = self.suggest_improvements(ats_score, weak_sections, parsed_resume)
        
        return {
            "ats_score": ats_score,
            "strong_sections": strong_sections,
            "weak_sections": weak_sections,
            "unnecessary_content": unnecessary_content,
            "improvement_suggestions": improvements
        }
    
    def calculate_ats_score(self, resume_text: str, parsed_resume: Dict) -> Dict:
        """
        Calculate ATS compatibility score (0-100%) with breakdown by category.
        
        Scoring breakdown:
        - Formatting: 25%
        - Keywords: 30%
        - Experience: 25%
        - Education: 10%
        - Readability: 10%
        
        Args:
            resume_text: Raw resume text
            parsed_resume: Parsed resume data
            
        Returns:
            ATS score breakdown
        """
        formatting_score = self._score_formatting(resume_text)
        keywords_score = self._score_keywords(resume_text, parsed_resume)
        experience_score = self._score_experience(parsed_resume)
        education_score = self._score_education(parsed_resume)
        readability_score = self._score_readability(resume_text)
        
        # Calculate weighted overall score
        overall_score = int(
            formatting_score * 0.25 +
            keywords_score * 0.30 +
            experience_score * 0.25 +
            education_score * 0.10 +
            readability_score * 0.10
        )
        
        return {
            "overall_score": overall_score,
            "formatting_score": formatting_score,
            "keywords_score": keywords_score,
            "experience_score": experience_score,
            "education_score": education_score,
            "readability_score": readability_score
        }
    
    def _score_formatting(self, resume_text: str) -> int:
        """Score resume formatting (0-100)"""
        score = 100
        
        # Check for standard sections
        sections_found = 0
        for section in self.REQUIRED_SECTIONS:
            if re.search(rf'\b{section}\b', resume_text, re.IGNORECASE):
                sections_found += 1
        
        if sections_found < 3:
            score -= 30
        elif sections_found < 4:
            score -= 15
        
        # Check for proper structure (headings, bullet points)
        if not re.search(r'[•\-\*]', resume_text):
            score -= 20  # No bullet points
        
        # Check for contact information
        if not re.search(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', resume_text):
            score -= 15  # No email
        
        if not re.search(r'\b\d{10}\b', resume_text):
            score -= 10  # No phone number
        
        return max(0, score)
    
    def _score_keywords(self, resume_text: str, parsed_resume: Dict) -> int:
        """Score keyword density and relevance (0-100)"""
        score = 50  # Base score
        
        # Get skills from parsed resume
        skills = parsed_resume.get("skills", [])
        
        # Check for industry-relevant keywords
        text_lower = resume_text.lower()
        total_keywords = 0
        found_keywords = 0
        
        for industry, keywords in self.INDUSTRY_KEYWORDS.items():
            for keyword in keywords:
                total_keywords += 1
                if keyword.lower() in text_lower:
                    found_keywords += 1
        
        # Calculate keyword density
        if total_keywords > 0:
            keyword_density = (found_keywords / total_keywords) * 100
            score = int(keyword_density)
        
        # Bonus for having skills section
        if len(skills) >= 5:
            score += 20
        elif len(skills) >= 3:
            score += 10
        
        return min(100, score)
    
    def _score_experience(self, parsed_resume: Dict) -> int:
        """Score experience section quality (0-100)"""
        score = 50  # Base score
        
        experience = parsed_resume.get("experience", [])
        
        if not experience:
            return 20  # Low score if no experience
        
        # Check for quantified achievements
        quantified_count = 0
        action_verb_count = 0
        
        for exp in experience:
            description = exp.get("description", "").lower()
            
            # Check for numbers/metrics
            if re.search(r'\d+%|\d+x|\$\d+|\d+ (users|customers|projects)', description):
                quantified_count += 1
            
            # Check for action verbs
            for verb in self.ACTION_VERBS:
                if verb in description:
                    action_verb_count += 1
                    break
        
        # Score based on quality indicators
        if len(experience) >= 3:
            score += 15
        elif len(experience) >= 2:
            score += 10
        
        if quantified_count >= 2:
            score += 20
        elif quantified_count >= 1:
            score += 10
        
        if action_verb_count >= 2:
            score += 15
        elif action_verb_count >= 1:
            score += 5
        
        return min(100, score)
    
    def _score_education(self, parsed_resume: Dict) -> int:
        """Score education section (0-100)"""
        score = 50  # Base score
        
        education = parsed_resume.get("education", [])
        
        if not education:
            return 30  # Low score if no education
        
        # Check for degree information
        for edu in education:
            degree = edu.get("degree", "").lower()
            institution = edu.get("institution", "").lower()
            
            # Bonus for higher education
            if any(term in degree for term in ["master", "mba", "m.tech", "phd"]):
                score += 25
            elif any(term in degree for term in ["bachelor", "b.tech", "b.e.", "bca"]):
                score += 15
            
            # Bonus for premier institutions
            if any(term in institution for term in ["iit", "iim", "nit", "bits"]):
                score += 25
            
            break  # Score only the highest degree
        
        return min(100, score)
    
    def _score_readability(self, resume_text: str) -> int:
        """Score readability and length (0-100)"""
        score = 100
        
        # Check length (1-2 pages is ideal, ~500-1000 words)
        word_count = len(resume_text.split())
        
        if word_count < 300:
            score -= 30  # Too short
        elif word_count > 1500:
            score -= 20  # Too long
        elif word_count > 1200:
            score -= 10  # Slightly long
        
        # Check for overly complex sentences
        sentences = re.split(r'[.!?]+', resume_text)
        long_sentences = sum(1 for s in sentences if len(s.split()) > 30)
        
        if long_sentences > 5:
            score -= 15
        
        # Check for spelling/grammar indicators (basic check)
        if re.search(r'\b(teh|recieve|occured|seperate)\b', resume_text, re.IGNORECASE):
            score -= 10
        
        return max(0, score)
    
    def identify_strong_sections(self, parsed_resume: Dict, resume_text: str) -> List[Dict]:
        """
        Identify well-written sections of the resume.
        
        Returns:
            List of strong sections with reasons and examples
        """
        strong_sections = []
        
        # Check experience section
        experience = parsed_resume.get("experience", [])
        for exp in experience:
            description = exp.get("description", "")
            
            # Check for quantified achievements
            if re.search(r'\d+%|\d+x|\$\d+|\d+ (users|customers|projects)', description):
                strong_sections.append({
                    "section": "Experience",
                    "reason": "Contains quantified achievements",
                    "examples": [description[:100] + "..."]
                })
                break
        
        # Check skills section
        skills = parsed_resume.get("skills", [])
        if len(skills) >= 8:
            strong_sections.append({
                "section": "Skills",
                "reason": "Comprehensive skill list with relevant technologies",
                "examples": skills[:5]
            })
        
        # Check for action verbs
        action_verb_found = False
        for verb in self.ACTION_VERBS[:10]:
            if verb in resume_text.lower():
                action_verb_found = True
                break
        
        if action_verb_found:
            strong_sections.append({
                "section": "Experience Descriptions",
                "reason": "Uses strong action verbs",
                "examples": ["Achieved", "Implemented", "Developed"]
            })
        
        return strong_sections
    
    def identify_weak_sections(self, parsed_resume: Dict, resume_text: str) -> List[Dict]:
        """
        Identify sections that need improvement.
        
        Returns:
            List of weak sections with issues and suggestions
        """
        weak_sections = []
        
        # Check for missing sections
        text_lower = resume_text.lower()
        missing_sections = []
        for section in ["experience", "education", "skills"]:
            if section not in text_lower:
                missing_sections.append(section)
        
        if missing_sections:
            weak_sections.append({
                "section": "Structure",
                "issue": f"Missing important sections: {', '.join(missing_sections)}",
                "suggestions": [f"Add a dedicated {section.title()} section" for section in missing_sections]
            })
        
        # Check experience descriptions
        experience = parsed_resume.get("experience", [])
        vague_descriptions = []
        for exp in experience:
            description = exp.get("description", "")
            if len(description) < 50:
                vague_descriptions.append(exp.get("title", "Position"))
        
        if vague_descriptions:
            weak_sections.append({
                "section": "Experience",
                "issue": "Vague or too brief job descriptions",
                "suggestions": [
                    "Add specific details about your responsibilities",
                    "Include quantified achievements (e.g., 'Increased sales by 25%')",
                    "Use action verbs to start each bullet point"
                ]
            })
        
        # Check for lack of keywords
        skills = parsed_resume.get("skills", [])
        if len(skills) < 5:
            weak_sections.append({
                "section": "Skills",
                "issue": "Limited skills listed",
                "suggestions": [
                    "Add more relevant technical skills",
                    "Include both hard and soft skills",
                    "List tools and technologies you've used"
                ]
            })
        
        # Check formatting
        if not re.search(r'[•\-\*]', resume_text):
            weak_sections.append({
                "section": "Formatting",
                "issue": "No bullet points found",
                "suggestions": [
                    "Use bullet points for better readability",
                    "Format experience and achievements as bullet lists"
                ]
            })
        
        return weak_sections
    
    def identify_unnecessary_content(self, resume_text: str) -> List[str]:
        """
        Identify content that should be removed from resume.
        
        Returns:
            List of unnecessary content found
        """
        unnecessary = []
        
        for pattern in self.UNNECESSARY_PATTERNS:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            if matches:
                unnecessary.append(f"Remove personal information: {matches[0]}")
        
        # Check for irrelevant hobbies
        if re.search(r'\b(hobbies|interests)\b', resume_text, re.IGNORECASE):
            unnecessary.append("Remove generic hobbies section (unless directly relevant to job)")
        
        # Check for "References available upon request"
        if re.search(r'references available', resume_text, re.IGNORECASE):
            unnecessary.append("Remove 'References available upon request' (it's assumed)")
        
        # Check for outdated skills
        outdated_skills = ["ms-dos", "windows 95", "internet explorer", "flash"]
        for skill in outdated_skills:
            if skill in resume_text.lower():
                unnecessary.append(f"Remove outdated skill: {skill}")
        
        return unnecessary
    
    def suggest_improvements(self, ats_score: Dict, weak_sections: List[Dict], 
                           parsed_resume: Dict) -> List[str]:
        """
        Generate specific improvement suggestions based on analysis.
        
        Returns:
            List of actionable improvement suggestions
        """
        suggestions = []
        
        # Suggestions based on ATS score components
        if ats_score["formatting_score"] < 70:
            suggestions.append("Improve resume structure with clear section headings (Experience, Education, Skills)")
            suggestions.append("Use bullet points to list achievements and responsibilities")
        
        if ats_score["keywords_score"] < 60:
            suggestions.append("Add more industry-relevant keywords and technical skills")
            suggestions.append("Include specific tools, technologies, and methodologies you've used")
        
        if ats_score["experience_score"] < 70:
            suggestions.append("Quantify your achievements with numbers and metrics (e.g., 'Increased efficiency by 30%')")
            suggestions.append("Start bullet points with strong action verbs (Achieved, Implemented, Led)")
        
        if ats_score["education_score"] < 60:
            suggestions.append("Add complete education details including degree, institution, and graduation year")
        
        if ats_score["readability_score"] < 70:
            suggestions.append("Keep resume concise (1-2 pages for most professionals)")
            suggestions.append("Use clear, concise language and avoid overly complex sentences")
        
        # Add specific suggestions from weak sections
        for weak in weak_sections:
            suggestions.extend(weak.get("suggestions", []))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in seen:
                seen.add(suggestion)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions[:10]  # Return top 10 suggestions
    
    def compare_with_job(self, resume_text: str, job_description: str) -> Dict:
        """
        Compare resume with specific job description to identify keyword gaps.
        
        Args:
            resume_text: Resume text
            job_description: Job description text
            
        Returns:
            Keyword gap analysis with matching and missing keywords
        """
        # Extract keywords from job description
        job_keywords = self._extract_keywords(job_description)
        resume_keywords = self._extract_keywords(resume_text)
        
        # Find matching and missing keywords
        matching_keywords = list(set(job_keywords) & set(resume_keywords))
        missing_keywords = list(set(job_keywords) - set(resume_keywords))
        
        # Calculate match percentage
        if job_keywords:
            match_percentage = (len(matching_keywords) / len(job_keywords)) * 100
        else:
            match_percentage = 0
        
        # Generate suggestions
        suggestions = []
        if missing_keywords:
            top_missing = missing_keywords[:5]
            suggestions.append(f"Consider adding these keywords: {', '.join(top_missing)}")
            suggestions.append("Incorporate missing keywords naturally into your experience descriptions")
        
        if match_percentage < 50:
            suggestions.append("Your resume has low keyword match with this job. Tailor it to include more relevant skills and technologies.")
        
        return {
            "matching_keywords": matching_keywords,
            "missing_keywords": missing_keywords,
            "keyword_match_percentage": round(match_percentage, 2),
            "suggestions": suggestions
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        text_lower = text.lower()
        keywords = []
        
        # Extract from all industry keyword lists
        for industry_keywords in self.INDUSTRY_KEYWORDS.values():
            for keyword in industry_keywords:
                if keyword in text_lower:
                    keywords.append(keyword)
        
        # Extract technical terms (words with 3+ chars, alphanumeric)
        words = re.findall(r'\b[a-z]{3,}\b', text_lower)
        technical_terms = [w for w in words if w not in ['the', 'and', 'for', 'with', 'from', 'this', 'that']]
        
        keywords.extend(technical_terms[:20])  # Add top 20 technical terms
        
        return list(set(keywords))  # Remove duplicates
