"""Seed the database with sample employees, projects, and allocations for the PoC demo.

Run with: python -m app.seed
"""

from datetime import date, timedelta

from app.chatbot.gemini_client import GeminiUnavailable
from app.core.db import Base, SessionLocal, engine
from app.embeddings.faiss_index import employee_index
from app.models.models import Allocation, Employee, Project

SAMPLE_EMPLOYEES = [
    dict(
        name="Rahul Sharma",
        grade="Senior Consultant",
        location="Bangalore",
        experience_years=5,
        skills=["Oracle EBS", "Oracle SQL", "PL/SQL", "Oracle Forms", "Finance Modules"],
        certifications=["Oracle Certified Professional"],
        previous_projects=[{"name": "Finance Migration - GlobalBank", "description": "Led Oracle EBS Finance module rollout"}],
        domain_experience=["Finance", "Manufacturing"],
        availability_date=date.today(),
        performance_rating=4.8,
    ),
    dict(
        name="Ananya Iyer",
        grade="Consultant",
        location="Bangalore",
        experience_years=4,
        skills=["Oracle APEX", "Oracle SQL", "PL/SQL", "Oracle Database"],
        certifications=["Oracle APEX Certified"],
        previous_projects=[{"name": "Supply Chain Portal", "description": "Built APEX apps for inventory tracking"}],
        domain_experience=["Manufacturing"],
        availability_date=date.today() + timedelta(days=3),
        performance_rating=4.5,
    ),
    dict(
        name="Karthik Reddy",
        grade="Senior Consultant",
        location="Hyderabad",
        experience_years=6,
        skills=["Java", "Spring Boot", "AWS", "Microservices", "Docker"],
        certifications=["AWS Certified Solutions Architect"],
        previous_projects=[{"name": "Retail Platform Modernization", "description": "Migrated monolith to microservices on AWS"}],
        domain_experience=["Retail"],
        availability_date=date.today(),
        performance_rating=4.7,
    ),
    dict(
        name="Priya Nair",
        grade="Consultant",
        location="Chennai",
        experience_years=3,
        skills=["Java", "AWS", "Spring", "REST APIs"],
        certifications=[],
        previous_projects=[{"name": "Insurance Claims API", "description": "Built claims processing REST services"}],
        domain_experience=["Insurance"],
        availability_date=date.today() + timedelta(days=15),
        performance_rating=4.2,
    ),
    dict(
        name="Vikram Singh",
        grade="Lead Consultant",
        location="Pune",
        experience_years=8,
        skills=["Java", "AWS", "Kubernetes", "Spring Boot", "System Design"],
        certifications=["AWS Certified DevOps Engineer", "CKA"],
        previous_projects=[{"name": "Banking Core Modernization", "description": "Architected cloud-native banking core"}],
        domain_experience=["Banking", "Finance"],
        availability_date=date.today(),
        performance_rating=4.9,
    ),
    dict(
        name="Sneha Deshmukh",
        grade="Consultant",
        location="Bangalore",
        experience_years=4,
        skills=["Oracle EBS", "SQL", "Finance", "Procurement"],
        certifications=["Oracle Financials Certified"],
        previous_projects=[{"name": "Procure-to-Pay Rollout", "description": "Implemented P2P for manufacturing client"}],
        domain_experience=["Finance", "Manufacturing"],
        availability_date=date.today(),
        performance_rating=4.6,
    ),
    dict(
        name="Arjun Menon",
        grade="Senior Consultant",
        location="Bangalore",
        experience_years=5,
        skills=["React", "Node.js", "TypeScript", "AWS"],
        certifications=[],
        previous_projects=[{"name": "Healthcare Patient Portal", "description": "Full-stack web app for patient scheduling"}],
        domain_experience=["Healthcare"],
        availability_date=date.today() + timedelta(days=45),
        performance_rating=4.3,
    ),
    dict(
        name="Divya Krishnan",
        grade="Consultant",
        location="Chennai",
        experience_years=3,
        skills=["Python", "FastAPI", "Machine Learning", "AWS"],
        certifications=["AWS Certified Machine Learning"],
        previous_projects=[{"name": "Demand Forecasting Engine", "description": "Built ML pipeline for retail demand forecasting"}],
        domain_experience=["Retail"],
        availability_date=date.today(),
        performance_rating=4.6,
    ),
    dict(
        name="Rohan Kapoor",
        grade="Lead Consultant",
        location="Gurugram",
        experience_years=9,
        skills=["Oracle EBS", "Oracle SQL", "PL/SQL", "Finance", "Manufacturing"],
        certifications=["Oracle Certified Master"],
        previous_projects=[{"name": "Global ERP Rollout", "description": "Led multi-country Oracle EBS Finance rollout"}],
        domain_experience=["Finance", "Manufacturing", "Automotive"],
        availability_date=date.today(),
        performance_rating=4.9,
    ),
    dict(
        name="Meera Pillai",
        grade="Consultant",
        location="Bangalore",
        experience_years=2,
        skills=["Java", "Spring Boot", "MySQL"],
        certifications=[],
        previous_projects=[{"name": "Internal Tools", "description": "Built internal HR tooling"}],
        domain_experience=["HR Tech"],
        availability_date=date.today() + timedelta(days=60),
        performance_rating=3.9,
    ),
    dict(
        name="Aditya Verma",
        grade="Senior Consultant",
        location="Bangalore",
        experience_years=6,
        skills=["AWS", "DevOps", "Terraform", "Kubernetes", "CI/CD"],
        certifications=["AWS Certified DevOps Engineer"],
        previous_projects=[{"name": "Cloud Migration - Media Co", "description": "Migrated on-prem workloads to AWS"}],
        domain_experience=["Media"],
        availability_date=date.today(),
        performance_rating=4.5,
    ),
    dict(
        name="Ishita Bose",
        grade="Consultant",
        location="Kolkata",
        experience_years=4,
        skills=["Oracle APEX", "PL/SQL", "Oracle Forms", "SQL Tuning"],
        certifications=["Oracle Database Certified"],
        previous_projects=[{"name": "HR Self-Service Portal", "description": "APEX-based HR self-service system"}],
        domain_experience=["HR Tech"],
        availability_date=date.today() + timedelta(days=10),
        performance_rating=4.4,
    ),
    dict(
        name="Nikhil Joshi",
        grade="Principal Consultant",
        location="Pune",
        experience_years=11,
        skills=["Java", "AWS", "Architecture", "Spring Boot", "Kafka"],
        certifications=["AWS Certified Solutions Architect Professional"],
        previous_projects=[{"name": "Core Banking Platform", "description": "Chief architect for core banking rebuild"}],
        domain_experience=["Banking"],
        availability_date=date.today(),
        performance_rating=4.9,
    ),
    dict(
        name="Pooja Agarwal",
        grade="Consultant",
        location="Bangalore",
        experience_years=3,
        skills=["React", "JavaScript", "Material UI", "REST APIs"],
        certifications=[],
        previous_projects=[{"name": "E-commerce Storefront", "description": "Built customer-facing storefront UI"}],
        domain_experience=["Retail"],
        availability_date=date.today() + timedelta(days=5),
        performance_rating=4.1,
    ),
    dict(
        name="Sanjay Rao",
        grade="Senior Consultant",
        location="Hyderabad",
        experience_years=7,
        skills=["Oracle SQL", "Oracle Database", "Data Warehousing", "ETL"],
        certifications=["Oracle Certified Professional"],
        previous_projects=[{"name": "Enterprise Data Warehouse", "description": "Designed EDW for finance reporting"}],
        domain_experience=["Finance"],
        availability_date=date.today(),
        performance_rating=4.6,
    ),
]

SAMPLE_PROJECTS = [
    dict(project_name="Oracle Finance Rollout - EMEA", required_skills=["Oracle EBS", "Finance", "SQL"], location="Bangalore", start_date=date.today() + timedelta(days=14)),
    dict(project_name="Cloud Banking Modernization", required_skills=["Java", "AWS", "Kubernetes"], location="Pune", start_date=date.today() + timedelta(days=7)),
    dict(project_name="Retail Demand Forecasting", required_skills=["Python", "Machine Learning", "AWS"], location="Chennai", start_date=date.today() + timedelta(days=21)),
]


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Employee).count() > 0:
            print("Employees already seeded, skipping.")
            return

        employees = [Employee(**data) for data in SAMPLE_EMPLOYEES]
        db.add_all(employees)
        db.commit()
        for e in employees:
            db.refresh(e)

        projects = [Project(**data) for data in SAMPLE_PROJECTS]
        db.add_all(projects)
        db.commit()
        for p in projects:
            db.refresh(p)

        # Allocate a few employees so bench/allocated analytics have signal.
        allocations = [
            Allocation(employee_id=employees[0].id, project_id=projects[0].id, allocation_status="Allocated", allocation_date=date.today()),
            Allocation(employee_id=employees[8].id, project_id=projects[0].id, allocation_status="Allocated", allocation_date=date.today() - timedelta(days=5)),
            Allocation(employee_id=employees[4].id, project_id=projects[1].id, allocation_status="Allocated", allocation_date=date.today() - timedelta(days=2)),
            Allocation(employee_id=employees[12].id, project_id=projects[1].id, allocation_status="Allocated", allocation_date=date.today()),
            Allocation(employee_id=employees[7].id, project_id=projects[2].id, allocation_status="Allocated", allocation_date=date.today() - timedelta(days=10)),
        ]
        db.add_all(allocations)
        db.commit()

        print(f"Seeded {len(employees)} employees and {len(projects)} projects.")

        print("Building FAISS embedding index (calls Gemini embeddings API)...")
        try:
            employee_index.build(employees)
            print("Done.")
        except GeminiUnavailable as exc:
            # Seeding the data is the important part; the index rebuilds itself on
            # the first search once the API key or quota is working again.
            print(f"Skipped the embedding index ({exc}).")
            print("Data is seeded. Search will fall back to skill matching, and the")
            print("index will build automatically on the first search once quota allows.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
