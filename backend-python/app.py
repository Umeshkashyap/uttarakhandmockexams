import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Import database
from app.config.database import Database

# Import routes
from app.routes.admin_routes import admin_bp

def create_app():
    """Create and configure Flask app"""
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, origins=os.getenv('FRONTEND_URL', 'http://localhost:3000'), supports_credentials=True)
    
    # Initialize database
    Database.initialize()
    
    # Register blueprints
    app.register_blueprint(admin_bp)
    
    # Health check route
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'success': True,
            'message': 'Server is running',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    # 404 handler
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Route not found'
        }), 404
    
    # 500 handler
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
    
    # Request logging
    @app.before_request
    def log_request():
        from flask import request
        print(f'{request.method} {request.path}')
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    
    print(f'🚀 Server running on port {port}')
    print(f'📡 API: http://localhost:{port}/api')
    print(f'🌐 Frontend: {os.getenv("FRONTEND_URL")}')
    print(f'⚙️  Environment: {os.getenv("FLASK_ENV", "development")}')
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_ENV') == 'development'
    )
