from flask import Flask
from flask_cors import CORS
from config import config

def create_app(config_name='default'):
    app = Flask(__name__)
    CORS(app)
    
    app.config.from_object(config[config_name])
    
    # Register blueprints
    from app.routes.pattern_routes import pattern_bp
    from app.routes.behavior_routes import behavior_bp
    from app.routes.combined_analysis_routes import combined_bp
    
    app.register_blueprint(pattern_bp, url_prefix='/api/v1/analyze')
    app.register_blueprint(behavior_bp, url_prefix='/api/v1/analyze')
    app.register_blueprint(combined_bp, url_prefix='/api/v1/analyze')
    
    return app
