from flask import request, jsonify
from app.models.user import User
from app.models.test_result import TestResult

def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Get total users
        total_users = User.count()
        
        # Get active tests (last 24 hours)
        active_tests = TestResult.count_active_tests()
        
        # Get total questions (placeholder)
        total_questions = 2850
        
        # Get average score
        average_score = TestResult.get_average_score()
        
        return jsonify({
            'success': True,
            'data': {
                'totalUsers': total_users,
                'activeTests': active_tests,
                'totalQuestions': total_questions,
                'averageScore': average_score
            }
        }), 200
        
    except Exception as e:
        print(f'Get stats error: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Server error'
        }), 500

def get_recent_activities():
    """Get recent activities"""
    try:
        limit = int(request.args.get('limit', 10))
        
        activities = TestResult.get_recent_activities(limit)
        
        formatted_activities = [
            {
                'user': activity.get('userName', 'Unknown User'),
                'action': f"Completed {activity['subjectName']} Test",
                'score': f"{activity['score']}%",
                'time': activity['completedAt']
            }
            for activity in activities
        ]
        
        return jsonify({
            'success': True,
            'data': formatted_activities
        }), 200
        
    except Exception as e:
        print(f'Get activities error: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Server error'
        }), 500

def get_top_scorers():
    """Get top scorers"""
    try:
        limit = int(request.args.get('limit', 5))
        
        top_scorers = User.get_top_scorers(limit)
        
        formatted_scorers = [
            {
                'rank': idx + 1,
                'name': user['name'],
                'score': f"{user['bestScore']}%",
                'tests': user['testsCompleted']
            }
            for idx, user in enumerate(top_scorers)
        ]
        
        return jsonify({
            'success': True,
            'data': formatted_scorers
        }), 200
        
    except Exception as e:
        print(f'Get top scorers error: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Server error'
        }), 500

def get_all_users():
    """Get all users with pagination"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        skip = (page - 1) * limit
        
        users = User.find_all(skip, limit)
        total = User.count()
        
        return jsonify({
            'success': True,
            'data': {
                'users': users,
                'pagination': {
                    'total': total,
                    'page': page,
                    'pages': (total + limit - 1) // limit
                }
            }
        }), 200
        
    except Exception as e:
        print(f'Get users error: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Server error'
        }), 500
