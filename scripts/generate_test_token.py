"""Generate a test JWT token for API testing."""

import sys
import os
from datetime import timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import create_access_token


def generate_test_token():
    """Generate a test JWT token."""
    
    # Test user data
    user_data = {
        "sub": "test_user_123",
        "email": "test@ipsi-platform.com",
        "role": "hr_admin"
    }
    
    # Generate token (expires in 24 hours)
    token = create_access_token(
        data=user_data,
        expires_delta=timedelta(hours=24)
    )
    
    print("=" * 80)
    print("  Test JWT Token Generated")
    print("=" * 80)
    print("\nUser Data:")
    print(f"  User ID: {user_data['sub']}")
    print(f"  Email: {user_data['email']}")
    print(f"  Role: {user_data['role']}")
    print("\nToken (valid for 24 hours):")
    print("-" * 80)
    print(token)
    print("-" * 80)
    print("\nUsage in API requests:")
    print("  Authorization: Bearer " + token[:50] + "...")
    print("\nExample curl command:")
    print(f'  curl -H "Authorization: Bearer {token}" \\')
    print('       http://localhost:8000/api/v1/health')
    print("=" * 80)
    
    return token


if __name__ == "__main__":
    generate_test_token()



