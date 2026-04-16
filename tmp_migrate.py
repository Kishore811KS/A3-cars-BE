from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        db.session.execute(text("ALTER TABLE bills ADD COLUMN status VARCHAR(20) DEFAULT 'active'"))
        db.session.commit()
        print("Added status column.")
    except Exception as e:
        print("Status column already exists or error: ", e)
        db.session.rollback()

    try:
        db.session.execute(text("ALTER TABLE bills ADD COLUMN cancel_remarks TEXT"))
        db.session.commit()
        print("Added cancel_remarks column.")
    except Exception as e:
        print("cancel_remarks column already exists or error: ", e)
        db.session.rollback()
