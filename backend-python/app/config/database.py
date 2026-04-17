import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class Database:
    client = None
    db = None
    
    @staticmethod
    def initialize():
        """Initialize MongoDB connection"""
        try:
            Database.client = MongoClient(os.getenv('MONGODB_URI'))
            Database.db = Database.client.get_default_database()
            
            # Test connection
            Database.client.server_info()
            print(f"✅ MongoDB Connected: {Database.db.name}")
            
        except Exception as e:
            print(f"❌ Error connecting to MongoDB: {str(e)}")
            raise e
    
    @staticmethod
    def get_db():
        """Get database instance"""
        if Database.db is None:
            Database.initialize()
        return Database.db
