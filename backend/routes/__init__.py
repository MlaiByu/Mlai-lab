from .auth import auth_bp
from .users import users_bp
from .experiment import experiment_bp
from .container import container_bp
from .health import health_bp

def register_routes(app):
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(experiment_bp)
    app.register_blueprint(container_bp)