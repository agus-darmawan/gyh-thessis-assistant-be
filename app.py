from flask import Flask
from flask_cors import CORS
from datetime import datetime
import pytz

from extensions import db, migrate
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    from routes.jake_routes import jake_bp
    from routes.nailstudio_routes import nailstudio_bp
    
    app.register_blueprint(jake_bp, url_prefix='/api')
    app.register_blueprint(nailstudio_bp, url_prefix='/api')
    
    @app.route('/api/health')
    def health_check():
        return {
            'success': True,
            'message': 'GyH API is running!',
            'status': 'healthy',
            'timestamp': datetime.now(pytz.timezone('Asia/Jakarta')).isoformat()
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    print("🚀 GyH API Server Starting...")
    print(f"📁 Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"🌍 Environment: {app.config.get('ENV', 'development')}")
    print(f"🔧 Debug Mode: {app.config.get('DEBUG', False)}")
    print("=" * 50)
    
    app.run(
        debug=app.config.get('DEBUG', False),
        host='0.0.0.0',
        port=6002
    )