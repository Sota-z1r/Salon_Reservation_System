from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config   # ← 追加

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)   # ← これに変更

    db.init_app(app)
    migrate.init_app(app, db)

    # Blueprint 読み込み
    from app.routes.reservation import reservation_bp
    from app.routes.admin import admin_bp
    from app.routes.blocks import blocks_bp
    from app.routes.line_webhook import line_bp
    from app.routes.remind import remind_bp

    app.register_blueprint(reservation_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(blocks_bp)
    app.register_blueprint(line_bp)
    app.register_blueprint(remind_bp)
    
    
    # 初回起動時に DB を作成（存在しない場合）
    with app.app_context():
        db.create_all()


    return app
