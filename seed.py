"""Script to seed the database with sample data for testing."""
from app import create_app, db
from app.models import Listing, User

app = create_app()

def seed_data():
    """Clear and seed the database with sample users and listings."""
    with app.app_context():
        # 1. Clean existing data (Optional, but good for a fresh start)
        db.drop_all()
        db.create_all()

        # 2. Create a Test User (Required for the seller_id relationship)
        test_user = User(
            student_id="254573S",
            display_name="Irsyad",
            email="254573S@mymail.nyp.edu.sg",
            contact_number="91234567"
        )
        db.session.add(test_user)
        db.session.commit()

        # 3. Create Sample Listings
        listings = [
            Listing(
                title="Advanced Physics Textbook",
                description="Condition 9/10, barely used. Good for Year 2 students.",
                price="25.00",
                category="Textbooks",
                condition="Like New",
                image_url="http://example.com/physics.jpg",
                seller_id=test_user.id
            ),
            Listing(
                title="Scientific Calculator",
                description="Casio model, still works perfectly.",
                price="15.00",
                category="Electronics",
                condition="Good",
                image_url="http://example.com/calculator.jpg",
                seller_id=test_user.id
            ),
            Listing(
                title="NYP Polo Shirt",
                description="Size M, only worn twice for events.",
                price="Swap Only",
                category="Clothing",
                condition="Good",
                image_url="http://example.com/shirt.jpg",
                seller_id=test_user.id
            ),
            Listing(
                title="Basic Stationery Set",
                description="Includes pens, pencils, and a ruler.",
                price="Free",
                category="Stationery",
                condition="Fair",
                image_url="http://example.com/pens.jpg",
                seller_id=test_user.id
            )
        ]

        db.session.add_all(listings)
        db.session.commit()
        print("Database seeded successfully with 1 user and 4 listings!")

if __name__ == "__main__":
    seed_data()