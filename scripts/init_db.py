"""Script to initialize the database with tables."""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import engine
from app.models.database import Base


def init_database():
    """Initialize database tables."""
    print("🔧 Initializing database...")
    print("Creating tables...")
    
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database initialized successfully!")
    print("\nTables created:")
    print("  - companies")
    print("  - job_postings")
    print("  - student_profiles")
    print("  - match_history")


if __name__ == "__main__":
    init_database()



