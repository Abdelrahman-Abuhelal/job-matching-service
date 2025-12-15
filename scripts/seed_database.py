"""Script to seed the database with sample data."""

import asyncio
import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.database import Base
from app.services.job_parser import parse_and_store_job
from app.services.embedding_service import create_or_update_student_embedding
from scripts.sample_data import SAMPLE_JOBS, SAMPLE_STUDENTS


async def seed_database():
    """Seed the database with sample jobs and students."""
    
    print("🌱 Starting database seeding...")
    
    # Create database tables
    print("📊 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")
    
    # Create database session
    db: Session = SessionLocal()
    
    try:
        # Seed jobs
        print(f"\n📋 Seeding {len(SAMPLE_JOBS)} sample jobs...")
        for i, job_data in enumerate(SAMPLE_JOBS, 1):
            try:
                print(f"  [{i}/{len(SAMPLE_JOBS)}] Processing: {job_data['external_job_id']}")
                result = await parse_and_store_job(
                    db=db,
                    external_job_id=job_data["external_job_id"],
                    external_company_id=job_data["external_company_id"],
                    company_name=job_data["company_name"],
                    raw_description=job_data["raw_description"]
                )
                print(f"      ✅ Created job: {result['structured_data'].title}")
            except Exception as e:
                print(f"      ❌ Error: {str(e)}")
        
        print(f"\n✅ Jobs seeding completed")
        
        # Seed students
        print(f"\n👨‍🎓 Seeding {len(SAMPLE_STUDENTS)} sample students...")
        for i, student_data in enumerate(SAMPLE_STUDENTS, 1):
            try:
                print(f"  [{i}/{len(SAMPLE_STUDENTS)}] Processing: {student_data['external_student_id']}")
                result = await create_or_update_student_embedding(
                    db=db,
                    external_student_id=student_data["external_student_id"],
                    profile_data=student_data["profile_data"]
                )
                print(f"      ✅ Created student profile")
            except Exception as e:
                print(f"      ❌ Error: {str(e)}")
        
        print(f"\n✅ Students seeding completed")
        
        print("\n🎉 Database seeding completed successfully!")
        print("\n📈 Summary:")
        print(f"   - Jobs created: {len(SAMPLE_JOBS)}")
        print(f"   - Students created: {len(SAMPLE_STUDENTS)}")
        print(f"   - Companies created: {len(set(j['external_company_id'] for j in SAMPLE_JOBS))}")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        raise
    finally:
        db.close()


def main():
    """Main entry point."""
    print("=" * 60)
    print("  IPSI AI Matching Service - Database Seeder")
    print("=" * 60)
    
    asyncio.run(seed_database())


if __name__ == "__main__":
    main()



