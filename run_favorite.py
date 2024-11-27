from favorite_service.favorite import app, db

with app.app_context():
    db.create_all()  # Ensures tables are created if not already

if __name__ == "__main__":
    app.run(port=5004)
