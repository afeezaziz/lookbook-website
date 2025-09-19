from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy database instance to be initialized in app.py
# Usage in app.py:
#     from extensions import db
#     db.init_app(app)
# Usage in models.py:
#     from extensions import db
#     class MyModel(db.Model): ...

db = SQLAlchemy()
