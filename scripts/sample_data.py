"""Sample data for testing the AI matching service."""

# Sample job descriptions
SAMPLE_JOBS = [
    {
        "external_job_id": "job_001",
        "external_company_id": "company_tech_corp",
        "company_name": "Tech Corp",
        "raw_description": """
        Python Backend Developer Internship
        
        We are seeking a motivated Python developer intern to join our backend team. 
        
        Requirements:
        - Bachelor's degree in Computer Science or related field (current student or recent graduate)
        - Strong proficiency in Python programming
        - Experience with FastAPI or Django frameworks
        - Knowledge of PostgreSQL or other relational databases
        - Understanding of RESTful APIs
        - Familiarity with Git version control
        
        Preferred Skills:
        - Experience with Docker and containerization
        - Knowledge of cloud platforms (AWS, GCP, or Azure)
        - Understanding of microservices architecture
        
        Location: Remote (EU timezone)
        Duration: 6 months internship
        
        Responsibilities:
        - Develop and maintain REST API endpoints
        - Write clean, testable code
        - Collaborate with frontend developers
        - Participate in code reviews
        
        Benefits:
        - Competitive internship salary
        - Mentorship from senior developers
        - Flexible working hours
        - Potential for full-time employment
        """
    },
    {
        "external_job_id": "job_002",
        "external_company_id": "company_data_solutions",
        "company_name": "Data Solutions Inc",
        "raw_description": """
        Data Science Internship
        
        Data Solutions Inc is looking for a data science intern to work on machine learning projects.
        
        Requirements:
        - Currently pursuing a Master's degree in Data Science, Statistics, or Computer Science
        - Strong Python programming skills
        - Experience with pandas, numpy, scikit-learn
        - Knowledge of machine learning algorithms
        - Strong analytical and problem-solving skills
        - SQL database experience
        
        Preferred:
        - Experience with deep learning frameworks (TensorFlow, PyTorch)
        - Knowledge of data visualization tools (Matplotlib, Plotly)
        - Experience with Jupyter notebooks
        
        Location: Paris, France (Hybrid - 2 days in office)
        Duration: 6-12 months
        Type: Internship
        
        What you'll do:
        - Build and train machine learning models
        - Analyze large datasets
        - Create data visualizations
        - Present findings to stakeholders
        
        Benefits:
        - Monthly stipend
        - Access to cutting-edge technology
        - Learning and development opportunities
        """
    },
    {
        "external_job_id": "job_003",
        "external_company_id": "company_web_studio",
        "company_name": "Creative Web Studio",
        "raw_description": """
        Full-Stack Developer Internship (React + Node.js)
        
        Join our creative team to build modern web applications!
        
        Requirements:
        - Bachelor's degree in progress (Computer Science, Web Development, or similar)
        - Proficiency in JavaScript/TypeScript
        - Experience with React.js
        - Knowledge of Node.js and Express
        - Understanding of HTML5, CSS3
        - Familiarity with MongoDB or PostgreSQL
        - 1-2 years of experience or relevant projects
        
        Nice to have:
        - Experience with Next.js
        - Knowledge of GraphQL
        - UI/UX design skills
        - Experience with Tailwind CSS
        
        Location: Remote (worldwide)
        Type: Full-time internship
        Duration: 6 months with possibility of extension
        
        Responsibilities:
        - Develop responsive web applications
        - Implement RESTful APIs
        - Work with our design team
        - Debug and optimize code
        - Write technical documentation
        
        Perks:
        - Competitive salary
        - Fully remote work
        - Modern tech stack
        - Collaborative team environment
        """
    },
    {
        "external_job_id": "job_004",
        "external_company_id": "company_fintech_solutions",
        "company_name": "FinTech Solutions",
        "raw_description": """
        Junior Software Engineer - Banking Platform
        
        FinTech Solutions is revolutionizing digital banking. We're looking for a junior engineer.
        
        Requirements:
        - Bachelor's or Master's degree in Computer Science
        - Strong programming skills in Java or Python
        - Understanding of software design patterns
        - Knowledge of SQL databases
        - Experience with unit testing
        - Excellent problem-solving abilities
        - 0-2 years of professional experience
        
        Preferred:
        - Knowledge of financial systems
        - Experience with Spring Boot or similar frameworks
        - Understanding of security best practices
        - Familiarity with CI/CD pipelines
        
        Location: London, UK (On-site)
        Type: Full-time permanent position
        
        Your role:
        - Develop features for our banking platform
        - Ensure code quality and security
        - Collaborate with product managers
        - Participate in agile ceremonies
        - Contribute to system architecture
        
        We offer:
        - Competitive salary and benefits
        - Professional development budget
        - Health insurance
        - Modern office in central London
        - Career growth opportunities
        """
    },
    {
        "external_job_id": "job_005",
        "external_company_id": "company_ai_research",
        "company_name": "AI Research Lab",
        "raw_description": """
        Machine Learning Research Intern
        
        Join our AI research team working on cutting-edge NLP and computer vision projects.
        
        Requirements:
        - Currently pursuing a PhD or Master's in Machine Learning, AI, or related field
        - Strong mathematical background (linear algebra, probability, statistics)
        - Proficiency in Python
        - Experience with PyTorch or TensorFlow
        - Published research papers (preferred)
        - Strong coding skills
        
        Preferred:
        - Experience with transformer models
        - Knowledge of reinforcement learning
        - Contributions to open-source ML projects
        - Experience with distributed training
        
        Location: Remote (with optional visits to Berlin office)
        Duration: 3-6 months
        Type: Research Internship
        
        Responsibilities:
        - Conduct ML research experiments
        - Implement state-of-the-art algorithms
        - Analyze experimental results
        - Write research papers
        - Present findings at team meetings
        
        Benefits:
        - Stipend provided
        - Access to high-performance GPUs
        - Mentorship from senior researchers
        - Potential for paper publications
        """
    }
]

# Sample student profiles
SAMPLE_STUDENTS = [
    {
        "external_student_id": "student_001",
        "profile_data": {
            "skills": ["Python", "FastAPI", "PostgreSQL", "Git", "Docker", "REST APIs"],
            "education": {
                "level": "Bachelor's",
                "field": "Computer Science",
                "university": "Technical University of Munich"
            },
            "preferences": {
                "locations": ["Remote", "Munich", "Berlin"],
                "job_types": ["Internship", "Full-time"],
                "industries": ["Tech", "Software Development", "Cloud"]
            }
        }
    },
    {
        "external_student_id": "student_002",
        "profile_data": {
            "skills": ["Python", "Machine Learning", "pandas", "scikit-learn", "TensorFlow", "SQL", "Data Analysis"],
            "education": {
                "level": "Master's",
                "field": "Data Science",
                "university": "Sorbonne University"
            },
            "preferences": {
                "locations": ["Paris", "Remote"],
                "job_types": ["Internship"],
                "industries": ["Data Science", "AI", "Research"]
            }
        }
    },
    {
        "external_student_id": "student_003",
        "profile_data": {
            "skills": ["JavaScript", "TypeScript", "React", "Node.js", "MongoDB", "HTML", "CSS", "Express"],
            "education": {
                "level": "Bachelor's",
                "field": "Web Development",
                "university": "University of Amsterdam"
            },
            "preferences": {
                "locations": ["Remote", "Amsterdam"],
                "job_types": ["Internship", "Full-time"],
                "industries": ["Web Development", "Tech", "Startups"]
            }
        }
    },
    {
        "external_student_id": "student_004",
        "profile_data": {
            "skills": ["Java", "Spring Boot", "SQL", "Git", "Unit Testing", "REST APIs", "Microservices"],
            "education": {
                "level": "Bachelor's",
                "field": "Software Engineering",
                "university": "Imperial College London"
            },
            "preferences": {
                "locations": ["London", "UK"],
                "job_types": ["Full-time", "Internship"],
                "industries": ["Finance", "Banking", "Enterprise Software"]
            }
        }
    },
    {
        "external_student_id": "student_005",
        "profile_data": {
            "skills": ["Python", "PyTorch", "Deep Learning", "NLP", "Computer Vision", "Research", "Mathematics"],
            "education": {
                "level": "PhD",
                "field": "Artificial Intelligence",
                "university": "ETH Zurich"
            },
            "preferences": {
                "locations": ["Remote", "Zurich", "Berlin"],
                "job_types": ["Internship", "Research"],
                "industries": ["AI Research", "Machine Learning", "Academia"]
            }
        }
    },
    {
        "external_student_id": "student_006",
        "profile_data": {
            "skills": ["Python", "Django", "JavaScript", "PostgreSQL", "Git", "Linux"],
            "education": {
                "level": "Bachelor's",
                "field": "Computer Science",
                "university": "University of Barcelona"
            },
            "preferences": {
                "locations": ["Remote", "Barcelona", "Madrid"],
                "job_types": ["Internship"],
                "industries": ["Tech", "Web Development", "Startups"]
            }
        }
    },
    {
        "external_student_id": "student_007",
        "profile_data": {
            "skills": ["Python", "Data Analysis", "SQL", "Excel", "Statistics", "Visualization"],
            "education": {
                "level": "Bachelor's",
                "field": "Statistics",
                "university": "University of Vienna"
            },
            "preferences": {
                "locations": ["Vienna", "Remote"],
                "job_types": ["Internship", "Part-time"],
                "industries": ["Data Analysis", "Business Intelligence", "Finance"]
            }
        }
    },
    {
        "external_student_id": "student_008",
        "profile_data": {
            "skills": ["React", "Next.js", "TypeScript", "Tailwind CSS", "GraphQL", "UI/UX Design"],
            "education": {
                "level": "Bachelor's",
                "field": "Digital Design",
                "university": "Royal College of Art London"
            },
            "preferences": {
                "locations": ["Remote"],
                "job_types": ["Internship", "Full-time"],
                "industries": ["Web Development", "Design", "Creative Tech"]
            }
        }
    }
]



