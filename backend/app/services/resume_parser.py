import re
from typing import List, Optional
from PyPDF2 import PdfReader
from docx import Document
from io import BytesIO
from app.schemas.resume import ParsedResume
import logging

logger = logging.getLogger(__name__)


class ResumeParser:
    """
    Resume parser for extracting text and information from PDF and DOCX files.
    """
    
    def __init__(self):
        # Common skill keywords (expandable)
        self.skill_keywords = {
            # Programming languages
            "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "php", 
            "swift", "kotlin", "go", "rust", "scala", "r", "matlab",
            
            # Web technologies
            "html", "css", "react", "angular", "vue", "node.js", "express", "django", 
            "flask", "fastapi", "spring", "asp.net", "jquery", "bootstrap", "tailwind",
            
            # Databases
            "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", 
            "oracle", "sqlite", "dynamodb", "cassandra",
            
            # Cloud & DevOps
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "github",
            "gitlab", "ci/cd", "terraform", "ansible",
            
            # Data Science & ML
            "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn",
            "pandas", "numpy", "data analysis", "nlp", "computer vision",
            
            # Other technical
            "rest api", "graphql", "microservices", "agile", "scrum", "jira",
            "linux", "unix", "bash", "powershell",
            
            # Soft skills
            "leadership", "communication", "teamwork", "problem solving", "project management"
        }
    
    def parse_file(self, file_content: bytes, file_type: str) -> ParsedResume:
        """
        Parse resume file and extract information.
        
        Args:
            file_content: Binary content of the file
            file_type: File extension (.pdf or .docx)
            
        Returns:
            ParsedResume object with extracted data
        """
        # Extract text based on file type
        if file_type == ".pdf":
            text = self._extract_pdf_text(file_content)
        elif file_type == ".docx":
            text = self._extract_docx_text(file_content)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Extract skills
        skills = self.extract_skills(text)
        
        # Extract experience years
        experience_years = self._extract_experience_years(text)
        
        # Extract education level
        education_level = self._extract_education_level(text)
        
        return ParsedResume(
            raw_text=text,
            skills=skills,
            experience_years=experience_years,
            education_level=education_level
        )
    
    def _extract_pdf_text(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_file = BytesIO(file_content)
            pdf_reader = PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise ValueError("Failed to extract text from PDF")
    
    def _extract_docx_text(self, file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            docx_file = BytesIO(file_content)
            doc = Document(docx_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {e}")
            raise ValueError("Failed to extract text from DOCX")
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from resume text using keyword matching.
        
        Args:
            text: Resume text
            
        Returns:
            List of identified skills
        """
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skill_keywords:
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                # Capitalize skill name for display
                found_skills.append(skill.title())
        
        # Remove duplicates and sort
        found_skills = sorted(list(set(found_skills)))
        
        return found_skills
    
    def _extract_experience_years(self, text: str) -> Optional[int]:
        """
        Extract years of experience from resume text.
        
        Looks for patterns like:
        - "5 years of experience"
        - "5+ years experience"
        - "5-7 years"
        """
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience[:\s]+(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s+in',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    years = int(match.group(1))
                    return years
                except ValueError:
                    continue
        
        return None
    
    def _extract_education_level(self, text: str) -> Optional[str]:
        """
        Extract education level from resume text.
        
        Returns: bachelor, master, phd, or None
        """
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ["ph.d", "phd", "doctorate", "doctoral"]):
            return "phd"
        elif any(keyword in text_lower for keyword in ["master", "m.s.", "m.sc", "mba", "m.a."]):
            return "master"
        elif any(keyword in text_lower for keyword in ["bachelor", "b.s.", "b.sc", "b.a.", "b.tech"]):
            return "bachelor"
        
        return None
