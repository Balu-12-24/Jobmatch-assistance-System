"""
Script to generate comprehensive Indian salary training dataset.
Creates 500-1000 data points covering diverse roles, locations, and experience levels.
"""
import csv
import random

# City tier mapping with specific cities
CITY_DATA = {
    1: {
        "cities": ["Bangalore", "Mumbai", "Delhi NCR", "Hyderabad", "Pune", "Chennai", "Kolkata", "Gurgaon"],
        "multiplier": 1.0
    },
    2: {
        "cities": ["Ahmedabad", "Jaipur", "Chandigarh", "Kochi", "Coimbatore", "Indore", "Nagpur", "Visakhapatnam"],
        "multiplier": 0.85
    },
    3: {
        "cities": ["Bhubaneswar", "Mysore", "Vadodara", "Lucknow", "Thiruvananthapuram", "Surat", "Patna", "Jamshedpur"],
        "multiplier": 0.72
    }
}

# Company type multipliers
COMPANY_MULTIPLIERS = {
    "MNC": 1.8,
    "product": 1.5,
    "startup": 1.3,
    "service": 1.0,
    "BPO": 0.75,
    "KPO": 0.95
}

# Education institution tiers
EDUCATION_TIERS = {
    "IIT": 1.4,
    "NIT": 1.25,
    "IIM": 1.5,
    "BITS": 1.3,
    "Top Private": 1.15,
    "Tier 2": 1.0,
    "Tier 3": 0.9
}

# Job roles with base salaries (in INR) by experience
JOB_ROLES = {
    # IT Roles
    "Software Engineer": {
        "industry": "IT",
        "base_salaries": {
            0: 400000, 1: 500000, 2: 700000, 3: 900000, 4: 1200000,
            5: 1500000, 6: 1800000, 7: 2200000, 8: 2600000, 9: 3000000, 10: 3500000
        },
        "skill_count_range": (3, 8)
    },
    "Senior Software Engineer": {
        "industry": "IT",
        "base_salaries": {
            3: 1200000, 4: 1500000, 5: 1800000, 6: 2200000, 7: 2600000,
            8: 3000000, 9: 3500000, 10: 4000000, 12: 5000000
        },
        "skill_count_range": (5, 10)
    },
    "Data Scientist": {
        "industry": "IT",
        "base_salaries": {
            1: 800000, 2: 1100000, 3: 1500000, 4: 2000000, 5: 2500000,
            6: 3000000, 7: 3500000, 8: 4000000, 10: 5000000
        },
        "skill_count_range": (4, 9)
    },
    "DevOps Engineer": {
        "industry": "IT",
        "base_salaries": {
            2: 900000, 3: 1200000, 4: 1600000, 5: 2000000, 6: 2400000,
            7: 2800000, 8: 3200000, 10: 4000000
        },
        "skill_count_range": (4, 9)
    },
    "Full Stack Developer": {
        "industry": "IT",
        "base_salaries": {
            1: 600000, 2: 900000, 3: 1200000, 4: 1600000, 5: 2000000,
            6: 2400000, 7: 2800000, 8: 3200000, 10: 4000000
        },
        "skill_count_range": (5, 10)
    },
    "Frontend Developer": {
        "industry": "IT",
        "base_salaries": {
            1: 500000, 2: 800000, 3: 1100000, 4: 1400000, 5: 1800000,
            6: 2200000, 7: 2600000, 8: 3000000
        },
        "skill_count_range": (4, 8)
    },
    "Backend Developer": {
        "industry": "IT",
        "base_salaries": {
            1: 550000, 2: 850000, 3: 1150000, 4: 1500000, 5: 1900000,
            6: 2300000, 7: 2700000, 8: 3100000
        },
        "skill_count_range": (4, 8)
    },
    "QA Engineer": {
        "industry": "IT",
        "base_salaries": {
            1: 400000, 2: 600000, 3: 800000, 4: 1000000, 5: 1300000,
            6: 1600000, 7: 1900000, 8: 2200000
        },
        "skill_count_range": (3, 7)
    },
    "Mobile Developer": {
        "industry": "IT",
        "base_salaries": {
            1: 600000, 2: 900000, 3: 1200000, 4: 1600000, 5: 2000000,
            6: 2400000, 7: 2800000, 8: 3200000
        },
        "skill_count_range": (4, 8)
    },
    "Product Manager": {
        "industry": "IT",
        "base_salaries": {
            3: 1500000, 4: 2000000, 5: 2500000, 6: 3000000, 7: 3500000,
            8: 4000000, 10: 5000000, 12: 6500000
        },
        "skill_count_range": (5, 9)
    },
    "UI/UX Designer": {
        "industry": "IT",
        "base_salaries": {
            1: 500000, 2: 800000, 3: 1100000, 4: 1400000, 5: 1800000,
            6: 2200000, 7: 2600000, 8: 3000000
        },
        "skill_count_range": (4, 7)
    },
    "Cloud Architect": {
        "industry": "IT",
        "base_salaries": {
            5: 2500000, 6: 3000000, 7: 3500000, 8: 4000000, 10: 5000000, 12: 6500000
        },
        "skill_count_range": (6, 10)
    },
    
    # Finance Roles
    "Chartered Accountant": {
        "industry": "Finance",
        "base_salaries": {
            0: 600000, 1: 800000, 2: 1000000, 3: 1300000, 4: 1600000,
            5: 2000000, 6: 2400000, 8: 3000000, 10: 4000000
        },
        "skill_count_range": (4, 7)
    },
    "Financial Analyst": {
        "industry": "Finance",
        "base_salaries": {
            0: 500000, 1: 700000, 2: 900000, 3: 1200000, 4: 1500000,
            5: 1800000, 6: 2200000, 8: 2800000
        },
        "skill_count_range": (4, 7)
    },
    "Investment Banker": {
        "industry": "Finance",
        "base_salaries": {
            1: 1500000, 2: 2000000, 3: 2500000, 4: 3500000, 5: 4500000,
            6: 5500000, 8: 7000000, 10: 9000000
        },
        "skill_count_range": (5, 8)
    },
    "Risk Manager": {
        "industry": "Finance",
        "base_salaries": {
            3: 1200000, 4: 1500000, 5: 1800000, 6: 2200000, 8: 2800000, 10: 3500000
        },
        "skill_count_range": (4, 7)
    },
    "Equity Research Analyst": {
        "industry": "Finance",
        "base_salaries": {
            1: 800000, 2: 1100000, 3: 1400000, 4: 1800000, 5: 2200000,
            6: 2700000, 8: 3500000
        },
        "skill_count_range": (4, 7)
    },
    
    # Healthcare Roles
    "Medical Officer": {
        "industry": "Healthcare",
        "base_salaries": {
            0: 800000, 1: 1000000, 2: 1200000, 3: 1500000, 5: 2000000,
            7: 2500000, 10: 3500000
        },
        "skill_count_range": (3, 6)
    },
    "Staff Nurse": {
        "industry": "Healthcare",
        "base_salaries": {
            0: 300000, 1: 400000, 2: 500000, 3: 600000, 5: 800000, 8: 1100000
        },
        "skill_count_range": (3, 5)
    },
    "Pharmacist": {
        "industry": "Healthcare",
        "base_salaries": {
            0: 250000, 1: 350000, 2: 450000, 3: 550000, 5: 750000, 8: 1000000
        },
        "skill_count_range": (3, 5)
    },
    "Medical Representative": {
        "industry": "Healthcare",
        "base_salaries": {
            0: 350000, 1: 500000, 2: 650000, 3: 800000, 5: 1100000, 8: 1500000
        },
        "skill_count_range": (3, 6)
    },
    
    # Manufacturing Roles
    "Production Engineer": {
        "industry": "Manufacturing",
        "base_salaries": {
            0: 400000, 1: 550000, 2: 700000, 3: 900000, 5: 1200000, 8: 1800000
        },
        "skill_count_range": (3, 6)
    },
    "Quality Engineer": {
        "industry": "Manufacturing",
        "base_salaries": {
            0: 350000, 1: 500000, 2: 650000, 3: 850000, 5: 1150000, 8: 1600000
        },
        "skill_count_range": (3, 6)
    },
    "Mechanical Engineer": {
        "industry": "Manufacturing",
        "base_salaries": {
            0: 350000, 1: 500000, 2: 650000, 3: 850000, 5: 1150000, 8: 1600000
        },
        "skill_count_range": (3, 6)
    },
    "Supply Chain Manager": {
        "industry": "Manufacturing",
        "base_salaries": {
            3: 1000000, 4: 1300000, 5: 1600000, 6: 2000000, 8: 2500000, 10: 3200000
        },
        "skill_count_range": (4, 7)
    },
    
    # Sales & Marketing Roles
    "Business Development Manager": {
        "industry": "Sales",
        "base_salaries": {
            2: 700000, 3: 900000, 4: 1200000, 5: 1500000, 6: 1900000, 8: 2500000
        },
        "skill_count_range": (4, 7)
    },
    "Digital Marketing Manager": {
        "industry": "Marketing",
        "base_salaries": {
            2: 600000, 3: 850000, 4: 1100000, 5: 1400000, 6: 1800000, 8: 2400000
        },
        "skill_count_range": (4, 8)
    },
    "Content Writer": {
        "industry": "Marketing",
        "base_salaries": {
            0: 300000, 1: 450000, 2: 600000, 3: 800000, 5: 1100000, 8: 1500000
        },
        "skill_count_range": (3, 6)
    },
    "Sales Manager": {
        "industry": "Sales",
        "base_salaries": {
            3: 800000, 4: 1100000, 5: 1400000, 6: 1800000, 8: 2400000, 10: 3200000
        },
        "skill_count_range": (4, 7)
    },
    
    # BPO/KPO Roles
    "Customer Support Executive": {
        "industry": "BPO",
        "base_salaries": {
            0: 200000, 1: 300000, 2: 400000, 3: 500000, 5: 650000
        },
        "skill_count_range": (2, 4)
    },
    "Process Associate": {
        "industry": "BPO",
        "base_salaries": {
            0: 180000, 1: 280000, 2: 380000, 3: 480000, 5: 600000
        },
        "skill_count_range": (2, 4)
    },
    "Team Leader": {
        "industry": "BPO",
        "base_salaries": {
            2: 450000, 3: 600000, 4: 750000, 5: 900000, 7: 1200000
        },
        "skill_count_range": (3, 6)
    },
    "Data Analyst": {
        "industry": "KPO",
        "base_salaries": {
            1: 500000, 2: 700000, 3: 950000, 4: 1200000, 5: 1500000, 7: 2000000
        },
        "skill_count_range": (4, 8)
    }
}

def generate_salary_data():
    """Generate comprehensive salary training dataset"""
    data = []
    
    for job_title, job_info in JOB_ROLES.items():
        base_salaries = job_info["base_salaries"]
        industry = job_info["industry"]
        skill_range = job_info["skill_count_range"]
        
        # Generate multiple entries for each experience level
        for exp_years in base_salaries.keys():
            base_salary = base_salaries[exp_years]
            
            # Generate entries for different combinations
            for city_tier, city_info in CITY_DATA.items():
                for _ in range(2):  # 2 entries per city tier
                    city = random.choice(city_info["cities"])
                    city_multiplier = city_info["multiplier"]
                    
                    for company_type, company_multiplier in COMPANY_MULTIPLIERS.items():
                        # Skip some combinations to avoid too many entries
                        if random.random() < 0.6:  # 60% chance to include
                            continue
                        
                        # Random education institution
                        edu_inst = random.choice(list(EDUCATION_TIERS.keys()))
                        edu_multiplier = EDUCATION_TIERS[edu_inst]
                        
                        # Random skill count
                        skill_count = random.randint(skill_range[0], skill_range[1])
                        
                        # Calculate final salary with all multipliers
                        final_salary = int(
                            base_salary * 
                            city_multiplier * 
                            company_multiplier * 
                            edu_multiplier *
                            (1 + (skill_count - skill_range[0]) * 0.05)  # Skill bonus
                        )
                        
                        # Add some randomness (+/- 10%)
                        variation = random.uniform(0.9, 1.1)
                        final_salary = int(final_salary * variation)
                        
                        # Calculate LPA
                        salary_lpa = round(final_salary / 100000, 2)
                        
                        # Education level mapping
                        edu_level_map = {
                            "IIT": "B.Tech",
                            "NIT": "B.Tech",
                            "BITS": "B.E.",
                            "IIM": "MBA",
                            "Top Private": "B.Tech",
                            "Tier 2": "B.E.",
                            "Tier 3": "B.Sc"
                        }
                        edu_level = edu_level_map.get(edu_inst, "B.Tech")
                        
                        data.append({
                            "job_title": job_title,
                            "experience_years": exp_years,
                            "skill_count": skill_count,
                            "education_level": edu_level,
                            "education_institution": edu_inst,
                            "location": city,
                            "city_tier": city_tier,
                            "company_type": company_type,
                            "industry": industry,
                            "salary_inr": final_salary,
                            "salary_lpa": salary_lpa
                        })
    
    return data

def save_to_csv(data, filename="backend/data/indian_salary_training_data.csv"):
    """Save salary data to CSV file"""
    if not data:
        print("No data to save!")
        return
    
    fieldnames = [
        "job_title", "experience_years", "skill_count", "education_level",
        "education_institution", "location", "city_tier", "company_type",
        "industry", "salary_inr", "salary_lpa"
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Saved {len(data)} salary records to {filename}")

if __name__ == "__main__":
    print("Generating comprehensive Indian salary training dataset...")
    salary_data = generate_salary_data()
    
    print(f"Generated {len(salary_data)} salary data points")
    
    # Save to CSV
    save_to_csv(salary_data)
    
    # Print statistics
    print("\nDataset Statistics:")
    print(f"Total records: {len(salary_data)}")
    print(f"Unique job titles: {len(set(d['job_title'] for d in salary_data))}")
    print(f"Salary range: ₹{min(d['salary_inr'] for d in salary_data):,} - ₹{max(d['salary_inr'] for d in salary_data):,}")
    print(f"LPA range: {min(d['salary_lpa'] for d in salary_data)} - {max(d['salary_lpa'] for d in salary_data)}")
