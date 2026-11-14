"""Script to seed the database with realistic sample data for testing."""
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import Listing, User, Report

app = create_app()

def seed_data():
    """Clear and seed the database with sample users and listings."""
    with app.app_context():
        # 1. Clean existing data
        db.drop_all()
        db.create_all()

        # 2. Create Multiple Users with a real working password hash ("password123")
        valid_password_hash = generate_password_hash("password123")

        users = [
            User(student_id="254573S", first_name="Muhammad", last_name="Irsyad", 
                 display_name="Irsyad", email="254573S@mymail.nyp.edu.sg", 
                 contact_number="91234567", password_hash=valid_password_hash, account_status="active"),
            User(student_id="251111A", first_name="Shamreen", last_name="Student", 
                 display_name="Shamreen", email="shamreen@mymail.nyp.edu.sg", 
                 contact_number="88887777", password_hash=valid_password_hash, account_status="active"),
            User(student_id="252222B", first_name="Ashlyn", last_name="Student", 
                 display_name="Ashlyn", email="ashlyn@mymail.nyp.edu.sg", 
                 contact_number="90001111", password_hash=valid_password_hash, account_status="active"),
            
            # ---------------------------
            # Admin Account
            # ---------------------------
            User(
                student_id="253817B",
                first_name="Nann",
                last_name="Wint Yee Myo",
                display_name="Nann",
                email="253817B@mymail.nyp.edu.sg",
                contact_number="99999999",
                password_hash=valid_password_hash,
                account_status="active",
                is_admin=True
            )
        ]
        db.session.add_all(users)
        db.session.commit()

        # 3. Create 12 Realistic Listings
        listings = [
            Listing(title="Advanced Physics Vol 1", category="Textbooks", price="25.00", condition="Like New",
                    description="Essential for Year 1 Physics. No highlights or markings.",
                    image_url="https://images.unsplash.com/photo-1532012197367-6849412a57ce?w=400",
                    seller_id=users[0].id),
            Listing(title="Casio FX-991EX Calculator", category="Electronics", price="15.00", condition="Good",
                    description="Standard scientific calculator. Battery still strong.",
                    image_url="https://images.unsplash.com/photo-1574607383476-f517f260d30b?w=400",
                    seller_id=users[0].id),
            Listing(title="NYP White Lab Coat (Size L)", category="Lab Equipment", price="Free", condition="Fair",
                    description="Slightly stained near the pocket but otherwise perfect for Chem labs.",
                    image_url="https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400",
                    seller_id=users[1].id),
            Listing(title="Drawing Board for Design", category="Stationery", price="Swap Only", condition="Good",
                    description="A3 size drawing board. Looking to swap for a set of Copic markers.",
                    image_url="https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=400",
                    seller_id=users[2].id),
            Listing(title="Java Programming Textbook", category="Textbooks", price="30.00", condition="New",
                    description="Latest edition. Bought by mistake, never opened.",
                    image_url="https://images.unsplash.com/photo-1550399105-c4db5fb85c18?w=400",
                    seller_id=users[1].id),
            Listing(title="Bluetooth Wireless Mouse", category="Electronics", price="10.00", condition="Like New",
                    description="Logitech mouse, barely used for one semester.",
                    image_url="https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400",
                    seller_id=users[2].id),
            Listing(title="NYP Polo Shirt (Navy)", category="Clothing", price="5.00", condition="Good",
                    description="Size M. Official NYP merchandise.",
                    image_url="https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99?w=400",
                    seller_id=users[0].id),
            Listing(title="Safety Goggles", category="Lab Equipment", price="Free", condition="New",
                    description="Brand new in packaging. Extra pair from my kit.",
                    image_url="https://images.unsplash.com/photo-1582719202047-76d3432ee323?w=400",
                    seller_id=users[1].id),
            Listing(title="Python for Data Science", category="Textbooks", price="20.00", condition="Good",
                    description="Very useful for IT2112 module!",
                    image_url="https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=400",
                    seller_id=users[2].id),
            Listing(title="Mechanical Pencil Set (0.5mm)", category="Stationery", price="Free", condition="Fair",
                    description="3 pencils and a pack of lead.",
                    image_url="https://images.unsplash.com/photo-1585336139118-132f7f5f583e?w=400",
                    seller_id=users[0].id),
            Listing(title="NYP Hoodie Grey", category="Clothing", price="12.00", condition="Good",
                    description="Size S. Super comfy for air-con lecture theaters.",
                    image_url="https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400",
                    seller_id=users[1].id),
            Listing(title="Digital Multimeter", category="Electronics", price="18.00", condition="Like New",
                    description="Used for one Engineering project. High precision.",
                    image_url="https://images.unsplash.com/photo-1590308027703-e758e5124132?w=400",
                    seller_id=users[2].id),
        ]

        db.session.add_all(listings)
        db.session.commit()

        # 4. Create Sample Reports
        reports = [
            Report(
                listing_id=listings[0].id,
                reason="Spam",
                description="This listing appears to be fake."
            ),
            Report(
                listing_id=listings[2].id,
                reason="Inappropriate Content",
                description="The description contains inappropriate language."
            ),
            Report(
                listing_id=listings[5].id,
                reason="Fraud",
                description="Seller is requesting payment outside the platform."
            ),
            Report(
                listing_id=listings[8].id,
                reason="Duplicate Listing",
                description="The same item has been listed multiple times."
            ),
            Report(
                listing_id=listings[10].id,
                reason="Misleading Information",
                description="The item condition does not match the description."
            )
        ]

        db.session.add_all(reports)
        db.session.commit()

        print(
            f"Success: Seeded "
            f"{len(users)} users, "
            f"{len(listings)} listings and "
            f"{len(reports)} reports!"
        )

if __name__ == "__main__":
    seed_data()
