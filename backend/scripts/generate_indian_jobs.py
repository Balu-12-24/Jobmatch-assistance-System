"""
Script to generate comprehensive Indian job dataset.
Creates 400+ jobs across IT, Finance, Healthcare, Manufacturing, Sales, and BPO sectors.
"""
import json
import random

# City tier mapping
CITIES = {
    1: ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Pune", "Chennai", "Kolkata", "Gurgaon", "Noida"],
    2: ["Ahmedabad", "Jaipur", "Chandigarh", "Kochi", "Coimbatore", "Indore", "Nagpur", "Visakhapatnam"],
    3: ["Bhubaneswar", "Mysore", "Vadodara", "Lucknow", "Thiruvananthapuram", "Surat", "Patna"]
}

# IT Jobs (200+)
IT_ROLES = [
    {
        "title": "Software Engineer",
        "skills": "Java, Spring Boot, Microservices, REST APIs, MySQL, Git",
        "exp_range": [(0, 2, 400000, 800000), (2, 5, 800000, 1500000), (5, 8, 1500000, 2500000)],
        "companies": ["TCS", "Infosys", "Wipro", "HCL", "Tech Mahindra"],
        "company_type": "service"
    },
    {
        "title": "Python Developer",
        "skills": "Python, Django, Flask, PostgreSQL, REST APIs, AWS",
        "exp_range": [(0, 2, 450000, 900000), (2, 5, 900000, 1600000), (5, 8, 1600000, 2800000)],
        "companies": ["Flipkart", "Swiggy", "Zomato", "Paytm", "PhonePe"],
        "company_type": "product"
    },
    {
        "title": "Full Stack Developer",
        "skills": "React, Node.js, JavaScript, TypeScript, MongoDB, Express",
        "exp_range": [(1, 3, 600000, 1200000), (3, 6, 1200000, 2200000), (6, 10, 2200000, 3500000)],
        "companies": ["Amazon India", "Microsoft India", "Google India", "Adobe India"],
        "company_type": "MNC"
    },
    {
        "title": "Data Scientist",
        "skills": "Python, Machine Learning, Deep Learning, TensorFlow, SQL, Statistics",
        "exp_range": [(1, 3, 800000, 1500000), (3, 6, 1500000, 2800000), (6, 10, 2800000, 4500000)],
        "companies": ["Flipkart", "Amazon India", "Walmart Labs", "Ola", "Uber India"],
        "company_type": "product"
    },
    {
        "title": "DevOps Engineer",
        "skills": "AWS, Docker, Kubernetes, Jenkins, Terraform, Linux, Python",
        "exp_range": [(2, 4, 900000, 1600000), (4, 7, 1600000, 2800000), (7, 10, 2800000, 4000000)],
        "companies": ["Paytm", "PhonePe", "CRED", "Razorpay", "Zerodha"],
        "company_type": "product"
    },
    {
        "title": "Frontend Developer",
        "skills": "React, JavaScript, TypeScript, HTML, CSS, Redux, Webpack",
        "exp_range": [(1, 3, 500000, 1000000), (3, 6, 1000000, 1800000), (6, 10, 1800000, 3000000)],
        "companies": ["Swiggy", "Zomato", "Nykaa", "Meesho", "ShareChat"],
        "company_type": "product"
    },
    {
        "title": "Backend Developer",
        "skills": "Node.js, Express, MongoDB, PostgreSQL, REST APIs, Microservices",
        "exp_range": [(1, 3, 550000, 1100000), (3, 6, 1100000, 2000000), (6, 10, 2000000, 3200000)],
        "companies": ["Ola", "Uber India", "Rapido", "Dunzo", "Urban Company"],
        "company_type": "product"
    },
    {
        "title": "QA Engineer",
        "skills": "Selenium, Java, TestNG, Cucumber, API testing, Postman, Jenkins",
        "exp_range": [(1, 3, 400000, 800000), (3, 6, 800000, 1400000), (6, 10, 1400000, 2200000)],
        "companies": ["TCS", "Infosys", "Wipro", "Cognizant", "Capgemini"],
        "company_type": "service"
    },
    {
        "title": "Mobile Developer - Android",
        "skills": "Kotlin, Java, Android SDK, MVVM, Retrofit, Room, Coroutines",
        "exp_range": [(1, 3, 600000, 1200000), (3, 6, 1200000, 2100000), (6, 10, 2100000, 3500000)],
        "companies": ["Ola", "Swiggy", "Zomato", "Paytm", "PhonePe"],
        "company_type": "product"
    },
    {
        "title": "Mobile Developer - iOS",
        "skills": "Swift, iOS SDK, UIKit, SwiftUI, Core Data, REST APIs",
        "exp_range": [(1, 3, 650000, 1300000), (3, 6, 1300000, 2200000), (6, 10, 2200000, 3600000)],
        "companies": ["Flipkart", "Amazon India", "Myntra", "CRED", "Dream11"],
        "company_type": "product"
    }
]

# Finance Jobs (50+)
FINANCE_ROLES = [
    {
        "title": "Chartered Accountant",
        "skills": "CA qualified, Audit, Taxation, Financial reporting, IFRS, Ind AS",
        "exp_range": [(0, 3, 600000, 1200000), (3, 6, 1200000, 2000000), (6, 10, 2000000, 3500000)],
        "companies": ["Deloitte", "PwC", "EY", "KPMG", "Grant Thornton"],
        "company_type": "service"
    },
    {
        "title": "Financial Analyst",
        "skills": "Financial modeling, Excel, PowerPoint, SQL, Data analysis, MBA Finance",
        "exp_range": [(0, 2, 500000, 900000), (2, 5, 900000, 1600000), (5, 8, 1600000, 2500000)],
        "companies": ["ICICI Bank", "HDFC Bank", "Axis Bank", "Kotak Mahindra", "SBI"],
        "company_type": "MNC"
    },
    {
        "title": "Investment Banker",
        "skills": "Financial modeling, Valuation, M&A, Excel, PowerPoint, MBA from top B-school",
        "exp_range": [(1, 3, 1500000, 2500000), (3, 6, 2500000, 4500000), (6, 10, 4500000, 8000000)],
        "companies": ["Goldman Sachs", "Morgan Stanley", "JP Morgan", "Citi", "Deutsche Bank"],
        "company_type": "MNC"
    },
    {
        "title": "Risk Manager",
        "skills": "Risk management, Credit analysis, Risk modeling, Regulatory compliance",
        "exp_range": [(3, 6, 1000000, 1800000), (6, 10, 1800000, 3000000)],
        "companies": ["HDFC Bank", "ICICI Bank", "Axis Bank", "Yes Bank", "IndusInd Bank"],
        "company_type": "MNC"
    },
    {
        "title": "Equity Research Analyst",
        "skills": "Financial analysis, Valuation, Industry research, Excel, Bloomberg",
        "exp_range": [(1, 3, 800000, 1400000), (3, 6, 1400000, 2500000), (6, 10, 2500000, 4000000)],
        "companies": ["Motilal Oswal", "ICICI Securities", "HDFC Securities", "Kotak Securities"],
        "company_type": "MNC"
    }
]

# Healthcare Jobs (40+)
HEALTHCARE_ROLES = [
    {
        "title": "Medical Officer",
        "skills": "MBBS, Clinical skills, Patient care, Medical knowledge",
        "exp_range": [(0, 3, 800000, 1400000), (3, 6, 1400000, 2200000), (6, 10, 2200000, 3500000)],
        "companies": ["Apollo Hospitals", "Fortis Healthcare", "Max Healthcare", "Manipal Hospitals"],
        "company_type": "service"
    },
    {
        "title": "Staff Nurse",
        "skills": "B.Sc Nursing, Patient care, Medical procedures, Communication",
        "exp_range": [(0, 2, 300000, 500000), (2, 5, 500000, 800000), (5, 10, 800000, 1200000)],
        "companies": ["Apollo Hospitals", "Fortis Healthcare", "Max Healthcare", "AIIMS"],
        "company_type": "service"
    },
    {
        "title": "Pharmacist",
        "skills": "B.Pharm/D.Pharm, Pharmacy knowledge, Patient counseling, Inventory management",
        "exp_range": [(0, 2, 250000, 450000), (2, 5, 450000, 700000), (5, 10, 700000, 1000000)],
        "companies": ["Apollo Pharmacy", "MedPlus", "Fortis Healthcare", "Max Healthcare"],
        "company_type": "service"
    },
    {
        "title": "Medical Representative",
        "skills": "B.Pharm/Life Sciences, Pharma sales, Communication, Presentation",
        "exp_range": [(0, 2, 350000, 600000), (2, 5, 600000, 1000000), (5, 10, 1000000, 1600000)],
        "companies": ["Sun Pharma", "Cipla", "Dr. Reddy's", "Lupin", "Biocon"],
        "company_type": "product"
    }
]

# Manufacturing Jobs (60+)
MANUFACTURING_ROLES = [
    {
        "title": "Production Engineer",
        "skills": "B.E. Mechanical, Production planning, Quality control, Lean manufacturing",
        "exp_range": [(0, 3, 400000, 800000), (3, 6, 800000, 1400000), (6, 10, 1400000, 2200000)],
        "companies": ["Tata Motors", "Mahindra & Mahindra", "Maruti Suzuki", "Hyundai"],
        "company_type": "product"
    },
    {
        "title": "Quality Engineer",
        "skills": "B.E. Mechanical/Industrial, Six Sigma, ISO standards, Quality tools",
        "exp_range": [(0, 3, 350000, 700000), (3, 6, 700000, 1200000), (6, 10, 1200000, 2000000)],
        "companies": ["Tata Steel", "JSW Steel", "Hindalco", "Vedanta"],
        "company_type": "product"
    },
    {
        "title": "Mechanical Engineer",
        "skills": "B.E. Mechanical, AutoCAD, SolidWorks, Design, Analysis",
        "exp_range": [(0, 3, 350000, 700000), (3, 6, 700000, 1200000), (6, 10, 1200000, 2000000)],
        "companies": ["Larsen & Toubro", "Siemens India", "ABB India", "Schneider Electric"],
        "company_type": "service"
    },
    {
        "title": "Supply Chain Manager",
        "skills": "MBA/B.E., Logistics, Inventory management, SAP, Vendor management",
        "exp_range": [(3, 6, 800000, 1500000), (6, 10, 1500000, 2500000)],
        "companies": ["Reliance Industries", "ITC", "Hindustan Unilever", "Nestle India"],
        "company_type": "product"
    }
]

# Sales & Marketing Jobs (50+)
SALES_ROLES = [
    {
        "title": "Business Development Manager",
        "skills": "MBA, B2B sales, Negotiation, Presentation, CRM, Communication",
        "exp_range": [(2, 5, 600000, 1200000), (5, 8, 1200000, 2000000), (8, 12, 2000000, 3500000)],
        "companies": ["Byju's", "Unacademy", "UpGrad", "Vedantu", "WhiteHat Jr"],
        "company_type": "product"
    },
    {
        "title": "Digital Marketing Manager",
        "skills": "SEO, SEM, Google Ads, Facebook Ads, Analytics, Content strategy",
        "exp_range": [(2, 5, 500000, 1000000), (5, 8, 1000000, 1800000), (8, 12, 1800000, 3000000)],
        "companies": ["Nykaa", "Myntra", "Ajio", "Meesho", "Lenskart"],
        "company_type": "product"
    },
    {
        "title": "Content Writer",
        "skills": "Content writing, SEO writing, Creative writing, Research, Editing",
        "exp_range": [(0, 2, 300000, 600000), (2, 5, 600000, 1000000), (5, 8, 1000000, 1600000)],
        "companies": ["Zomato", "Swiggy", "Ola", "Uber India", "BookMyShow"],
        "company_type": "product"
    },
    {
        "title": "Sales Manager",
        "skills": "MBA, Sales management, Team leadership, B2B sales, CRM, Negotiation",
        "exp_range": [(3, 6, 700000, 1300000), (6, 10, 1300000, 2200000)],
        "companies": ["Asian Paints", "Berger Paints", "Pidilite", "Britannia", "ITC"],
        "company_type": "product"
    }
]

# BPO/KPO Jobs (30+)
BPO_ROLES = [
    {
        "title": "Customer Support Executive",
        "skills": "Graduate, Communication, Problem-solving, CRM, Patience",
        "exp_range": [(0, 2, 200000, 400000), (2, 5, 400000, 600000)],
        "companies": ["Amazon India", "Flipkart", "Swiggy", "Zomato", "Ola"],
        "company_type": "BPO"
    },
    {
        "title": "Process Associate",
        "skills": "Graduate, MS Office, Data entry, Attention to detail, Communication",
        "exp_range": [(0, 2, 180000, 350000), (2, 5, 350000, 550000)],
        "companies": ["Genpact", "WNS", "EXL Service", "Firstsource", "HGS"],
        "company_type": "BPO"
    },
    {
        "title": "Team Leader - Customer Service",
        "skills": "BPO experience, Team management, Customer service, Quality monitoring",
        "exp_range": [(2, 5, 400000, 700000), (5, 8, 700000, 1100000)],
        "companies": ["Teleperformance", "Concentrix", "Tech Mahindra BPO", "Wipro BPO"],
        "company_type": "BPO"
    },
    {
        "title": "Data Analyst",
        "skills": "SQL, Python, Excel, Tableau, Power BI, Statistics, Communication",
        "exp_range": [(1, 3, 450000, 900000), (3, 6, 900000, 1500000), (6, 10, 1500000, 2500000)],
        "companies": ["Mu Sigma", "Fractal Analytics", "LatentView", "Tiger Analytics"],
        "company_type": "KPO"
    }
]

def generate_jobs():
    """Generate comprehensive Indian job dataset"""
    jobs = []
    job_id = 1
    
    # Generate IT jobs (200+)
    for role in IT_ROLES:
        for exp_min, exp_max, sal_min, sal_max in role["exp_range"]:
            for company in role["companies"]:
                for city_tier in [1, 2]:
                    city = random.choice(CITIES[city_tier])
                    
                    # Adjust salary based on city tier
                    tier_multiplier = 1.0 if city_tier == 1 else 0.85
                    
                    job = {
                        "title": f"{role['title']} ({exp_min}-{exp_max} years)",
                        "company": company,
                        "description": f"Work on cutting-edge projects. {exp_min}-{exp_max} years of experience required.",
                        "requirements": role["skills"],
                        "location": city,
                        "country": "India",
                        "city_tier": city_tier,
                        "salary_min": int(sal_min * tier_multiplier),
                        "salary_max": int(sal_max * tier_multiplier),
                        "salary_currency": "INR",
                        "job_type": "full-time",
                        "remote_option": random.choice(["hybrid", "onsite", "remote"]),
                        "company_size": "large",
                        "company_type": role["company_type"],
                        "industry": "Technology"
                    }
                    jobs.append(job)
                    job_id += 1
    
    # Generate Finance jobs (50+)
    for role in FINANCE_ROLES:
        for exp_min, exp_max, sal_min, sal_max in role["exp_range"]:
            for company in role["companies"]:
                city = random.choice(CITIES[1])  # Finance jobs mostly in Tier 1
                
                job = {
                    "title": f"{role['title']} ({exp_min}-{exp_max} years)",
                    "company": company,
                    "description": f"Join our finance team. {exp_min}-{exp_max} years of experience required.",
                    "requirements": role["skills"],
                    "location": city,
                    "country": "India",
                    "city_tier": 1,
                    "salary_min": sal_min,
                    "salary_max": sal_max,
                    "salary_currency": "INR",
                    "job_type": "full-time",
                    "remote_option": "onsite",
                    "company_size": "large",
                    "company_type": role["company_type"],
                    "industry": "Finance"
                }
                jobs.append(job)
                job_id += 1
    
    # Generate Healthcare jobs (40+)
    for role in HEALTHCARE_ROLES:
        for exp_min, exp_max, sal_min, sal_max in role["exp_range"]:
            for company in role["companies"]:
                for city_tier in [1, 2]:
                    city = random.choice(CITIES[city_tier])
                    tier_multiplier = 1.0 if city_tier == 1 else 0.9
                    
                    job = {
                        "title": f"{role['title']} ({exp_min}-{exp_max} years)",
                        "company": company,
                        "description": f"Provide quality healthcare services. {exp_min}-{exp_max} years of experience required.",
                        "requirements": role["skills"],
                        "location": city,
                        "country": "India",
                        "city_tier": city_tier,
                        "salary_min": int(sal_min * tier_multiplier),
                        "salary_max": int(sal_max * tier_multiplier),
                        "salary_currency": "INR",
                        "job_type": "full-time",
                        "remote_option": "onsite",
                        "company_size": "large",
                        "company_type": role["company_type"],
                        "industry": "Healthcare"
                    }
                    jobs.append(job)
                    job_id += 1
    
    # Generate Manufacturing jobs (60+)
    for role in MANUFACTURING_ROLES:
        for exp_min, exp_max, sal_min, sal_max in role["exp_range"]:
            for company in role["companies"]:
                for city_tier in [1, 2]:
                    city = random.choice(CITIES[city_tier])
                    tier_multiplier = 1.0 if city_tier == 1 else 0.88
                    
                    job = {
                        "title": f"{role['title']} ({exp_min}-{exp_max} years)",
                        "company": company,
                        "description": f"Work in manufacturing excellence. {exp_min}-{exp_max} years of experience required.",
                        "requirements": role["skills"],
                        "location": city,
                        "country": "India",
                        "city_tier": city_tier,
                        "salary_min": int(sal_min * tier_multiplier),
                        "salary_max": int(sal_max * tier_multiplier),
                        "salary_currency": "INR",
                        "job_type": "full-time",
                        "remote_option": "onsite",
                        "company_size": "large",
                        "company_type": role["company_type"],
                        "industry": "Manufacturing"
                    }
                    jobs.append(job)
                    job_id += 1
    
    # Generate Sales & Marketing jobs (50+)
    for role in SALES_ROLES:
        for exp_min, exp_max, sal_min, sal_max in role["exp_range"]:
            for company in role["companies"]:
                city = random.choice(CITIES[1])
                
                job = {
                    "title": f"{role['title']} ({exp_min}-{exp_max} years)",
                    "company": company,
                    "description": f"Drive business growth. {exp_min}-{exp_max} years of experience required.",
                    "requirements": role["skills"],
                    "location": city,
                    "country": "India",
                    "city_tier": 1,
                    "salary_min": sal_min,
                    "salary_max": sal_max,
                    "salary_currency": "INR",
                    "job_type": "full-time",
                    "remote_option": random.choice(["hybrid", "onsite"]),
                    "company_size": "large",
                    "company_type": role["company_type"],
                    "industry": "Sales & Marketing"
                }
                jobs.append(job)
                job_id += 1
    
    # Generate BPO/KPO jobs (30+)
    for role in BPO_ROLES:
        for exp_min, exp_max, sal_min, sal_max in role["exp_range"]:
            for company in role["companies"]:
                for city_tier in [1, 2]:
                    city = random.choice(CITIES[city_tier])
                    tier_multiplier = 1.0 if city_tier == 1 else 0.82
                    
                    job = {
                        "title": f"{role['title']} ({exp_min}-{exp_max} years)",
                        "company": company,
                        "description": f"Join our team. {exp_min}-{exp_max} years of experience required.",
                        "requirements": role["skills"],
                        "location": city,
                        "country": "India",
                        "city_tier": city_tier,
                        "salary_min": int(sal_min * tier_multiplier),
                        "salary_max": int(sal_max * tier_multiplier),
                        "salary_currency": "INR",
                        "job_type": "full-time",
                        "remote_option": "onsite",
                        "company_size": "large",
                        "company_type": role["company_type"],
                        "industry": "BPO/KPO"
                    }
                    jobs.append(job)
                    job_id += 1
    
    return jobs

if __name__ == "__main__":
    print("Generating comprehensive Indian job dataset...")
    jobs = generate_jobs()
    
    # Save to file
    with open("backend/data/indian_jobs_full.json", "w") as f:
        json.dump(jobs, f, indent=2)
    
    print(f"Generated {len(jobs)} Indian jobs!")
    print(f"Saved to backend/data/indian_jobs_full.json")
