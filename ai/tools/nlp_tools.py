import spacy
from typing import List, Set, Dict
import re

# Load spaCy model globally
nlp = spacy.load("en_core_web_sm")

def extract_keywords(text: str) -> Set[str]:
    """Extract nouns and proper nouns as keywords"""
    doc = nlp(text)
    keywords = {
        token.lemma_.lower() 
        for token in doc 
        if token.is_alpha and not token.is_stop and token.pos_ in ['NOUN', 'PROPN']
    }
    return keywords

def extract_skills(text: str) -> List[str]:
    """Extract technical skills from text using known skills database only"""
    # Comprehensive technical skills database
    common_skills = {
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'ruby', 'php',
        'go', 'golang', 'rust', 'swift', 'kotlin', 'scala', 'r', 'perl', 'bash', 'shell',
        
        # Frontend
        'react', 'reactjs', 'angular', 'vue', 'vuejs', 'svelte', 'nextjs', 'nuxt',
        'html', 'html5', 'css', 'css3', 'sass', 'scss', 'tailwind', 'bootstrap',
        'jquery', 'webpack', 'vite',
        
        # Backend
        'node', 'nodejs', 'express', 'django', 'flask', 'fastapi', 'spring',
        'spring boot', 'laravel', 'rails', 'asp.net', '.net', 'nestjs',
        
        # Databases
        'sql', 'nosql', 'mysql', 'postgresql', 'postgres', 'mongodb', 'redis',
        'elasticsearch', 'cassandra', 'oracle', 'dynamodb', 'sqlite', 'firebase',
        
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s',
        'jenkins', 'terraform', 'ansible', 'ci/cd', 'devops', 'git', 'github', 'gitlab',
        
        # Data Science & ML
        'machine learning', 'deep learning', 'nlp', 'computer vision', 'ai',
        'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
        'spark', 'hadoop', 'kafka',
        
        # Testing
        'jest', 'pytest', 'selenium', 'cypress', 'junit',
        
        # Other
        'rest api', 'graphql', 'microservices', 'agile', 'scrum', 'jira',
        'linux', 'unix', 'nginx', 'apache'
    }
    
    text_lower = text.lower()
    found_skills = []
    
    # Only extract from known skills database - NO keyword extraction
    for skill in common_skills:
        # Use word boundary matching for accuracy
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    
    return list(set(found_skills))

def extract_sections(text: str) -> Dict[str, str]:
    """Extract common resume sections"""
    sections = {}
    
    # Common section headers
    section_patterns = {
        'summary': r'(summary|objective|profile)',
        'experience': r'(experience|work history|employment)',
        'education': r'(education|academic)',
        'skills': r'(skills|technical skills|competencies)',
        'certifications': r'(certifications|certificates)',
        'projects': r'(projects|portfolio)'
    }
    
    lines = text.split('\n')
    current_section = 'other'
    section_content = {key: [] for key in section_patterns.keys()}
    section_content['other'] = []
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Check if line is a section header
        section_found = False
        for section_name, pattern in section_patterns.items():
            if re.search(pattern, line_lower) and len(line_lower) < 50:
                current_section = section_name
                section_found = True
                break
        
        if not section_found and line.strip():
            section_content[current_section].append(line)
    
    # Convert lists to strings
    for key in section_content:
        sections[key] = '\n'.join(section_content[key])
    
    return sections

def extract_experience(text: str) -> List[Dict]:
    """Extract work experience entries"""
    experiences = []
    
    # This is a simplified version - you can enhance with more sophisticated parsing
    lines = text.split('\n')
    current_exp = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for date patterns (e.g., "2020-2023", "Jan 2020 - Present")
        if re.search(r'\d{4}', line) and len(line) < 100:
            if current_exp:
                experiences.append(current_exp)
            current_exp = {'period': line, 'description': []}
        elif current_exp:
            current_exp['description'].append(line)
    
    if current_exp:
        experiences.append(current_exp)
    
    return experiences

def extract_education(text: str) -> List[Dict]:
    """Extract education entries"""
    education = []
    
    # Common degree keywords
    degree_keywords = ['bachelor', 'master', 'phd', 'associate', 'diploma', 'certificate', 'degree', 'b.s.', 'm.s.', 'b.a.', 'm.a.']
    
    lines = text.split('\n')
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in degree_keywords):
            education.append({'entry': line.strip()})
    
    return education