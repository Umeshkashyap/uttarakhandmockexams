from datetime import datetime, timedelta
from bson import ObjectId
from app.config.database import Database

class TestResult:
    collection_name = 'testresults'
    
    @staticmethod
    def get_collection():
        """Get test results collection"""
        db = Database.get_db()
        return db[TestResult.collection_name]
    
    @staticmethod
    def create(user_id, exam_category, subject_id, subject_name, 
               total_questions, answered_questions, correct_answers,
               wrong_answers, score, percentage, time_taken):
        """Create new test result"""
        collection = TestResult.get_collection()
        
        result_data = {
            'userId': ObjectId(user_id),
            'examCategory': exam_category,
            'subjectId': subject_id,
            'subjectName': subject_name,
            'totalQuestions': total_questions,
            'answeredQuestions': answered_questions,
            'correctAnswers': correct_answers,
            'wrongAnswers': wrong_answers,
            'score': score,
            'percentage': percentage,
            'timeTaken': time_taken,
            'markedForReview': [],
            'answers': {},
            'completedAt': datetime.utcnow(),
            'createdAt': datetime.utcnow()
        }
        
        result = collection.insert_one(result_data)
        return result.inserted_id
    
    @staticmethod
    def get_recent_activities(limit=10):
        """Get recent test activities"""
        collection = TestResult.get_collection()
        db = Database.get_db()
        
        pipeline = [
            {
                '$lookup': {
                    'from': 'users',
                    'localField': 'userId',
                    'foreignField': '_id',
                    'as': 'user'
                }
            },
            {'$unwind': '$user'},
            {'$sort': {'completedAt': -1}},
            {'$limit': limit},
            {
                '$project': {
                    'userName': '$user.name',
                    'subjectName': 1,
                    'score': 1,
                    'percentage': 1,
                    'completedAt': 1
                }
            }
        ]
        
        results = list(collection.aggregate(pipeline))
        
        # Convert ObjectId to string
        for result in results:
            result['_id'] = str(result['_id'])
        
        return results
    
    @staticmethod
    def count_active_tests():
        """Count tests completed in last 24 hours"""
        collection = TestResult.get_collection()
        yesterday = datetime.utcnow() - timedelta(days=1)
        return collection.count_documents({'completedAt': {'$gte': yesterday}})
    
    @staticmethod
    def get_average_score():
        """Get average score across all tests"""
        collection = TestResult.get_collection()
        
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'averageScore': {'$avg': '$percentage'}
                }
            }
        ]
        
        result = list(collection.aggregate(pipeline))
        return int(result[0]['averageScore']) if result else 0
