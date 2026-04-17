from flask import Blueprint
from app.controllers import auth_controller, dashboard_controller
from app.middleware.auth import token_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Authentication routes
admin_bp.route('/login', methods=['POST'])(auth_controller.login)
admin_bp.route('/profile', methods=['GET'])(token_required(auth_controller.get_profile))
admin_bp.route('/change-password', methods=['PUT'])(token_required(auth_controller.change_password))

# Dashboard routes
admin_bp.route('/stats', methods=['GET'])(token_required(dashboard_controller.get_dashboard_stats))
admin_bp.route('/activities', methods=['GET'])(token_required(dashboard_controller.get_recent_activities))
admin_bp.route('/top-scorers', methods=['GET'])(token_required(dashboard_controller.get_top_scorers))
admin_bp.route('/users', methods=['GET'])(token_required(dashboard_controller.get_all_users))
