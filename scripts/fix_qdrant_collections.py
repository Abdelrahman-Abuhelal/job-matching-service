"""Fix Qdrant collections by deleting and recreating with correct dimensions."""

import sys
import os
import asyncio

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.qdrant_client import delete_collection, create_collection
from app.config import settings


async def fix_collections():
    """Delete and recreate collections with correct dimensions."""
    collections = ["students_global", "jobs_global"]
    
    print("=" * 80)
    print("  Fixing Qdrant Collections")
    print("=" * 80)
    print(f"\nTarget dimension: {settings.EMBEDDING_DIMENSIONS}")
    print(f"Collections to fix: {', '.join(collections)}\n")
    
    for collection_name in collections:
        print(f"📦 Processing: {collection_name}")
        
        try:
            # Delete existing collection
            print(f"  🗑️  Deleting existing collection...")
            try:
                await delete_collection(collection_name)
                print(f"  ✅ Deleted successfully")
            except Exception as e:
                # Collection might not exist, that's okay
                if "doesn't exist" in str(e) or "not found" in str(e).lower():
                    print(f"  ℹ️  Collection doesn't exist (skipping delete)")
                else:
                    print(f"  ⚠️  Delete warning: {e}")
            
            # Create collection with correct dimensions
            print(f"  🔨 Creating collection with {settings.EMBEDDING_DIMENSIONS} dimensions...")
            await create_collection(collection_name, vector_size=settings.EMBEDDING_DIMENSIONS)
            print(f"  ✅ Created successfully\n")
            
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
            raise
    
    print("=" * 80)
    print("  ✅ All collections fixed successfully!")
    print("=" * 80)
    print("\nYou can now run the seed script again:")
    print("  docker-compose exec fastapi python scripts/seed_database.py")


if __name__ == "__main__":
    asyncio.run(fix_collections())

