from datetime import datetime
from bson import ObjectId
from app.config.database import Database

class User:
    collection_name = 'users'
    
    @staticmethod
    def get_collection():
        """Get users collection"""
        db = Database.get_db()
        return db[User.collection_name]
    
    @staticmethod
    def create(name, email, phone=None, exam_category='all'):
        """Create new user"""
        collection = User.get_collection()
        
        user_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'examCategory': exam_category,
            'testsCompleted': 0,
            'totalScore': 0,
            'averageScore': 0,
            'bestScore': 0,
            'isActive': True,
            'lastActive': datetime.utcnow(),
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }
        
        result = collection.insert_one(user_data)
        return result.inserted_id
    
    @staticmethod
    def find_all(skip=0, limit=10):
        """Find all users with pagination"""
        collection = User.get_collection()
        users = list(collection.find().sort('createdAt', -1).skip(skip).limit(limit))
        
        # Convert ObjectId to string
        for user in users:
            user['_id'] = str(user['_id'])
        
        return users
    
    @staticmethod
    def count():
        """Count total users"""
        collection = User.get_collection()
        return collection.count_documents({'isActive': True})
    
    @staticmethod
    def get_top_scorers(limit=5):
        """Get top scoring users"""
        collection = User.get_collection()
        users = list(
            collection.find({'isActive': True})
            .sort([('bestScore', -1), ('testsCompleted', -1)])
            .limit(limit)
        )
        
        # Convert ObjectId to string
        for user in users:
            user['_id'] = str(user['_id'])
        
        return users
