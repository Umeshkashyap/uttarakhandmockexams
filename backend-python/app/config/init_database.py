import os
import sys
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from app.config.database import Database
from app.models.admin import Admin
from app.models.user import User
from app.models.test_result import TestResult

load_dotenv()

def initialize_database():
    """Initialize database with sample data"""
    try:
        print('\n🔄 Initializing database...\n')
        
        # Initialize database connection
        Database.initialize()
        
        # Create default admin
        print('Creating default admin...')
        try:
            admin_id = Admin.create(
                username=os.getenv('ADMIN_USERNAME', 'admin'),
                email=os.getenv('ADMIN_EMAIL', 'admin@mocktest.com'),
                password=os.getenv('ADMIN_PASSWORD', 'admin123'),
                role='superadmin'
            )
            print(f'✅ Default admin created')
            print(f'   Username: {os.getenv("ADMIN_USERNAME", "admin")}')
            print(f'   Email: {os.getenv("ADMIN_EMAIL", "admin@mocktest.com")}')
        except ValueError as e:
            print(f'ℹ️  Admin already exists')
        
        # Create sample users
        print('\nCreating sample users...')
        sample_users = [
            {
                'name': 'Rahul Kumar',
                'email': 'rahul@example.com',
                'phone': '9876543210',
                'exam_category': 'uttarakhand',
                'tests_completed': 24,
                'total_score': 1872,
                'best_score': 85
            },
            {
                'name': 'Priya Sharma',
                'email': 'priya@example.com',
                'phone': '9876543211',
                'exam_category': 'uttar-pradesh',
                'tests_completed': 18,
                'total_score': 1404,
                'best_score': 82
            },
            {
                'name': 'Amit Patel',
                'email': 'amit@example.com',
                'phone': '9876543212',
                'exam_category': 'ssc',
                'tests_completed': 22,
                'total_score': 1694,
                'best_score': 91
            },
            {
                'name': 'Sneha Verma',
                'email': 'sneha@example.com',
                'phone': '9876543213',
                'exam_category': 'uttarakhand',
                'tests_completed': 16,
                'total_score': 1232,
                'best_score': 89
            },
            {
                'name': 'Vikas Singh',
                'email': 'vikas@example.com',
                'phone': '9876543214',
                'exam_category': 'ssc',
                'tests_completed': 30,
                'total_score': 2850,
                'best_score': 95
            }
        ]
        
        user_count = User.count()
        if user_count == 0:
            user_ids = []
            for user_data in sample_users:
                user_id = User.create(
                    name=user_data['name'],
                    email=user_data['email'],
                    phone=user_data['phone'],
                    exam_category=user_data['exam_category']
                )
                user_ids.append(user_id)
                
                # Update test stats
                collection = User.get_collection()
                collection.update_one(
                    {'_id': user_id},
                    {
                        '$set': {
                            'testsCompleted': user_data['tests_completed'],
                            'totalScore': user_data['total_score'],
                            'bestScore': user_data['best_score'],
                            'averageScore': user_data['total_score'] // user_data['tests_completed']
                        }
                    }
                )
            
            print(f'✅ Created {len(sample_users)} sample users')
        else:
            print(f'ℹ️  {user_count} users already exist')
            # Get existing user IDs for test results
            users = User.find_all(limit=5)
            user_ids = [user['_id'] for user in users]
        
        # Create sample test results
        print('\nCreating sample test results...')
        result_count = TestResult.get_collection().count_documents({})
        
        if result_count == 0 and user_ids:
            results_created = 0
            for user_id in user_ids:
                for i in range(3):
                    answered = 45 + random.randint(0, 5)
                    correct = 30 + random.randint(0, 15)
                    wrong = answered - correct
                    percentage = (correct * 100) // 50
                    
                    TestResult.create(
                        user_id=str(user_id),
                        exam_category='uttarakhand',
                        subject_id='general-studies',
                        subject_name='General Studies',
                        total_questions=50,
                        answered_questions=answered,
                        correct_answers=correct,
                        wrong_answers=wrong,
                        score=percentage,
                        percentage=percentage,
                        time_taken=2400 + random.randint(0, 1200)
                    )
                    results_created += 1
            
            print(f'✅ Created {results_created} sample test results')
        else:
            print(f'ℹ️  {result_count} test results already exist')
        
        print('\n✅ Database initialization complete!\n')
        print('📝 You can now login with:')
        print(f'   Username: {os.getenv("ADMIN_USERNAME", "admin")}')
        print(f'   Password: {os.getenv("ADMIN_PASSWORD", "admin123")}\n')
        
    except Exception as e:
        print(f'❌ Error initializing database: {str(e)}')
        raise e

if __name__ == '__main__':
    initialize_database()
