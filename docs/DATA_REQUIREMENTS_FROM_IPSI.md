# 📋 Data Requirements from IPSI Platform

**Purpose:** What data you need from IPSI to develop and test the AI matching service  
**Date:** November 24, 2025  
**Status:** Development Phase

---

## 🎯 Overview

You're building the AI matching microservice for IPSI. You need sample data from them to:
1. ✅ Develop the matching algorithms
2. ✅ Test the service functionality
3. ✅ Validate match quality
4. ✅ Create realistic test cases

**Important:** During development, you should use **anonymized or synthetic data** only!

---

## 📊 Required Data from IPSI

### **Phase 1: Development (NOW)**

Use **anonymized sample data** or **synthetic data** - NOT real personal data.

---

## 1️⃣ **Student Profile Data Structure**

### **What You Need:**

**Sample student profiles** (50-100 profiles minimum) with the following structure:

```json
{
  "external_student_id": "student_XXXXX",  // Anonymized/hashed ID
  "profile_data": {
    
    // Required Fields:
    "skills": [
      "Python",
      "Java",
      "JavaScript",
      "React",
      "PostgreSQL"
    ],
    
    "education": {
      "level": "Bachelor's",           // Bachelor's, Master's, PhD
      "field": "Computer Science",
      "university": "Technical University",  // Can be generic
      "graduation_year": 2025,
      "gpa": 3.5                       // Optional, 0-4 scale or 1-6 EU scale
    },
    
    "preferences": {
      "locations": ["Munich", "Berlin", "Remote"],
      "job_types": ["Internship", "Working Student", "Full-time"],
      "industries": ["Technology", "Finance", "Healthcare"],
      "remote_preference": "preferred"  // "required", "preferred", "no"
    },
    
    // Important Fields:
    "experience_years": 1.5,           // Total professional experience
    
    "experiences": [
      {
        "title": "Backend Developer Intern",
        "company": "Company A",        // Can be anonymized
        "duration_months": 6,
        "description": "Developed REST APIs using FastAPI...",
        "technologies": ["Python", "FastAPI", "Docker"]
      }
    ],
    
    "projects": [
      {
        "title": "E-commerce Platform",
        "description": "Built full-stack web application...",
        "technologies": ["React", "Node.js", "PostgreSQL"],
        "duration_months": 4,
        "role": "Full-stack Developer"
      }
    ],
    
    // Optional Fields:
    "certifications": [
      "AWS Solutions Architect Associate",
      "Oracle Java Certified Programmer"
    ],
    
    "languages": [
      "German (native)",
      "English (fluent)",
      "Spanish (basic)"
    ],
    
    "availability_date": "2025-03-01"  // When can start
  }
}
```

---

### **Data Requirements:**

**Minimum:** 50 student profiles
**Recommended:** 100-200 profiles for better testing
**Diversity:** Include variety of:
- Different skill sets (technical, business, design)
- Different education levels (Bachelor's, Master's, PhD)
- Different experience levels (0-5 years)
- Different location preferences
- Different industries

**Important Notes:**
- ❌ **NO real names** - Use "Student A", "Student B" or anonymized IDs
- ❌ **NO real emails** - Use fake emails like "student001@example.com"
- ❌ **NO real phone numbers**
- ❌ **NO real addresses**
- ✅ **Skills can be real** - This is not personally identifiable
- ✅ **Companies can be anonymized** - "Company A", "Tech Startup"
- ✅ **Universities can be generic** - "Technical University", "Business School"

---

## 2️⃣ **Job Posting Data Structure**

### **What You Need:**

**Sample job postings** (20-50 jobs minimum) with raw descriptions:

```json
{
  "external_job_id": "job_XXXXX",         // Anonymized/hashed ID
  "external_company_id": "company_XXXXX", // Anonymized company ID
  "company_name": "Tech Company GmbH",    // Can be anonymized
  "raw_description": "
    Python Backend Developer Internship
    
    We are seeking a motivated Python developer intern to join our backend team.
    
    Requirements:
    - Bachelor's degree in Computer Science or related field
    - Strong proficiency in Python programming
    - Experience with FastAPI or Django frameworks
    - Knowledge of PostgreSQL or other relational databases
    - Understanding of RESTful APIs
    - Familiarity with Git version control
    
    Preferred Skills:
    - Experience with Docker and containerization
    - Knowledge of cloud platforms (AWS, GCP, or Azure)
    - Understanding of microservices architecture
    
    Location: Munich, Germany or Remote (EU timezone)
    Duration: 6 months internship
    Start Date: March 2025
    
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
  "
}
```

---

### **Data Requirements:**

**Minimum:** 20 job postings
**Recommended:** 50-100 jobs for comprehensive testing
**Diversity:** Include variety of:
- Different roles (Backend, Frontend, Data Science, DevOps, etc.)
- Different experience levels (Internship, Junior, Mid, Senior)
- Different locations (Munich, Berlin, Remote, etc.)
- Different industries (Tech, Finance, Healthcare, etc.)
- Different company sizes (Startup, SMB, Enterprise)

**Job Types Needed:**
1. **Technical Roles:**
   - Software Developer (Backend, Frontend, Full-stack)
   - Data Scientist / Analyst
   - DevOps Engineer
   - QA Engineer
   - Mobile Developer

2. **Business Roles:**
   - Product Manager
   - Business Analyst
   - Marketing Manager
   - HR Manager

3. **Design Roles:**
   - UX/UI Designer
   - Graphic Designer

**Important Notes:**
- ✅ **Real job descriptions are helpful** - Just anonymize company names
- ✅ **Can be from past postings** - Doesn't need to be currently active
- ❌ **Remove company-specific details** - Like internal codes, actual addresses
- ✅ **Keep requirements/skills realistic** - This helps test matching

---

## 3️⃣ **Company Data Structure**

### **What You Need:**

**Sample company profiles** (10-20 companies minimum):

```json
{
  "external_company_id": "company_XXXXX",  // Anonymized ID
  "company_name": "Tech Solutions GmbH",   // Can be anonymized
  "industry": "Technology",                // Or "Finance", "Healthcare", etc.
  "size": "51-200 employees",              // "1-10", "11-50", "51-200", "201-500", "500+"
  "locations": ["Munich", "Berlin"],
  "scoring_weights": {                     // Optional for now
    "vector_similarity": 0.25,
    "skills_match": 0.35,
    "experience": 0.20,
    "education": 0.10,
    "projects": 0.10
  }
}
```

**Important:** Companies are just containers for jobs. Basic info is sufficient.

---

## 4️⃣ **Sample Application Data** (Optional but Helpful)

### **What You Need:**

**Sample application records** to test the separation of applicants vs. candidates:

```json
{
  "external_student_id": "student_XXXXX",
  "external_company_id": "company_XXXXX",
  "external_job_id": "job_XXXXX",        // Optional
  "status": "applied",                    // Or "reviewed", "interviewed"
  "application_date": "2024-11-01"
}
```

**Use Cases:**
- Test that students who already applied appear separately
- Test that matching doesn't recommend jobs student applied to
- Test application tracking functionality

**Minimum:** 20-30 application records
**Recommended:** 50-100 applications spread across students/jobs

---

## 📋 **Summary: What to Request from IPSI**

### **Essential (Minimum Viable Dataset):**

| Data Type | Quantity | Format | Priority |
|-----------|----------|--------|----------|
| **Student Profiles** | 50-100 | JSON | 🔴 CRITICAL |
| **Job Postings** | 20-50 | JSON (with raw description) | 🔴 CRITICAL |
| **Companies** | 10-20 | JSON | 🟠 HIGH |
| **Applications** | 20-50 | JSON | 🟡 MEDIUM |

### **Recommended (Better Testing):**

| Data Type | Quantity | Format | Priority |
|-----------|----------|--------|----------|
| **Student Profiles** | 100-200 | JSON | 🟠 RECOMMENDED |
| **Job Postings** | 50-100 | JSON | 🟠 RECOMMENDED |
| **Companies** | 20-30 | JSON | 🟡 NICE TO HAVE |
| **Applications** | 50-100 | JSON | 🟡 NICE TO HAVE |

---

## 📧 **Email Template to Send IPSI**

```
Subject: Sample Data Request for AI Matching Service Development

Dear IPSI/DHBW Team,

As discussed, I'm developing the AI matching microservice for IPSI. 
To build and test the service effectively, I need sample data from 
the IPSI platform.

Important: All data should be ANONYMIZED (no real names, emails, 
phone numbers, or addresses). I only need the data structure and 
realistic content for testing purposes.

## Data Needed:

1. Student Profiles (50-100 samples)
   - Anonymized student IDs
   - Skills lists
   - Education information
   - Work experience descriptions
   - Project descriptions
   - Location/job preferences
   - See attached structure: [Include JSON example above]

2. Job Postings (20-50 samples)
   - Anonymized job IDs and company IDs
   - Raw job description text
   - Can be from past/closed positions
   - Various roles and experience levels
   - See attached structure: [Include JSON example above]

3. Company Profiles (10-20 samples)
   - Anonymized company IDs
   - Basic company info (industry, size, locations)
   - See attached structure: [Include JSON example above]

4. Sample Applications (Optional, 20-50 records)
   - Links between students and jobs they applied to
   - Helps test applicant tracking

## Data Privacy:

✅ All data should be anonymized or synthetic
✅ No real personal identifiers
✅ Only used for development and testing
✅ Will not be shared with any third parties
✅ Will be deleted after development is complete

## Format:

Please provide data as:
- JSON files (preferred)
- CSV files (acceptable)
- SQL dump (acceptable)

## Timeline:

When would you be able to provide this data? I can start 
development immediately once I receive it.

Thank you!

Best regards,
[Your Name]
```

---

## 🔍 **What to Check in the Data**

### **When You Receive Data from IPSI:**

**1. Verify Anonymization:**
```python
# Check for personal data leaks
def check_anonymization(data):
    """Verify data is properly anonymized."""
    
    # Patterns that should NOT appear
    FORBIDDEN_PATTERNS = [
        r'@.*\..*',           # Email addresses
        r'\+?\d{10,}',        # Phone numbers
        r'\d{5}\s+\w+',       # Addresses (postal code + street)
        # Add more patterns
    ]
    
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, str(data)):
            print(f"⚠️ WARNING: Possible PII detected: {pattern}")
            return False
    
    return True
```

**2. Verify Data Quality:**
```python
# Check data completeness
required_fields = {
    'student': ['skills', 'education', 'preferences'],
    'job': ['raw_description', 'company_name'],
    'company': ['company_name', 'industry']
}

# Check for missing required fields
# Check for reasonable data (not empty strings)
# Check for variety (different skills, roles, etc.)
```

**3. Test Data Variety:**
- ✅ Different skill combinations
- ✅ Different experience levels
- ✅ Different locations
- ✅ Different job types
- ✅ Mix of good and poor matches

---

## 🚀 **Alternative: Generate Synthetic Data**

If IPSI cannot provide data quickly, you can generate synthetic data:

### **Option 1: Use Your Sample Data**

You already have sample data in `scripts/sample_data.py` - expand it!

```python
# scripts/generate_synthetic_data.py

SKILL_POOLS = {
    'backend': ['Python', 'Java', 'Go', 'Node.js', 'PostgreSQL', 'MongoDB'],
    'frontend': ['React', 'Vue', 'Angular', 'TypeScript', 'HTML', 'CSS'],
    'data': ['Python', 'R', 'SQL', 'Pandas', 'TensorFlow', 'Tableau'],
    'devops': ['Docker', 'Kubernetes', 'AWS', 'Jenkins', 'Terraform']
}

def generate_student_profile(student_id: int, role_type: str):
    """Generate realistic synthetic student profile."""
    skills = random.sample(SKILL_POOLS[role_type], k=random.randint(5, 8))
    
    return {
        "external_student_id": f"synthetic_student_{student_id:04d}",
        "profile_data": {
            "skills": skills,
            "education": {
                "level": random.choice(["Bachelor's", "Master's"]),
                "field": "Computer Science",
                "university": f"University {chr(65 + student_id % 26)}",
                "graduation_year": random.randint(2024, 2026)
            },
            # ... more fields ...
        }
    }

# Generate 100 diverse student profiles
students = []
for i in range(100):
    role_type = random.choice(['backend', 'frontend', 'data', 'devops'])
    students.append(generate_student_profile(i, role_type))
```

### **Option 2: Use AI to Generate Data**

```python
# Use GPT-4 to generate realistic profiles
prompt = """
Generate a realistic student profile JSON for a computer science 
student with 2 years of experience in backend development.
Include skills, education, work experience, and projects.
Use fake names and companies.
"""

# Use OpenAI/Aleph Alpha to generate 100 diverse profiles
```

### **Option 3: Use Public Datasets**

- GitHub profiles (public skills data)
- LinkedIn-like mock datasets
- Kaggle datasets for job postings

---

## ✅ **Checklist: Before You Start Development**

### **Data Acquisition:**
- [ ] Contacted IPSI for sample data
- [ ] Received anonymized student profiles (50+ minimum)
- [ ] Received anonymized job postings (20+ minimum)
- [ ] Received company data (10+ minimum)
- [ ] Verified all data is anonymized (no PII)
- [ ] Checked data quality and variety
- [ ] Loaded data into test database

### **Or Alternative:**
- [ ] Generated synthetic student data (100+ profiles)
- [ ] Generated synthetic job postings (50+ jobs)
- [ ] Generated synthetic company data (20+ companies)
- [ ] Created diverse test scenarios
- [ ] Validated synthetic data quality

### **Development Environment:**
- [ ] Sample data loaded in database
- [ ] Qdrant populated with test vectors
- [ ] Can run matching queries successfully
- [ ] Results look reasonable
- [ ] Ready to build API endpoints

---

## 🎯 **Bottom Line**

### **What You Need from IPSI:**

**Minimum to Start:**
1. ✅ **50-100 anonymized student profiles** (with skills, education, experience)
2. ✅ **20-50 anonymized job postings** (with raw descriptions)
3. ✅ **10-20 company records** (basic info)

**Format:** JSON files preferred

**Anonymization:** No real names, emails, phones, addresses

**Timeline:** Request ASAP - can take 1-2 weeks for IPSI to prepare

**Alternative:** Generate synthetic data yourself if IPSI is slow

---

## 📞 **Next Steps**

1. ✅ Send email to IPSI requesting data (use template above)
2. ✅ While waiting, set up synthetic data generator
3. ✅ Start development with synthetic data
4. ✅ When IPSI data arrives, validate and switch to real data
5. ✅ Test matching quality with both datasets

---

**Need help generating synthetic data? Let me know and I can create a complete synthetic data generator for you!** 🚀

**Last Updated:** November 24, 2025



