from database.db import SessionLocal
from database.schema import User
from pages.login import hash_password


def create_users():

    db = SessionLocal()

    try:
        # --------------------------------------------------
        # Demo Student
        # --------------------------------------------------
        student_email = "student@campus.com"

        student = (
            db.query(User)
            .filter(User.email == student_email)
            .first()
        )

        if not student:

            student = User(
                name="Demo Student",
                email=student_email,
                password_hash=hash_password("student123"),
                role="student",
                reward_points=25,
                is_active=True
            )

            db.add(student)

            print(
                "✅ Demo Student account created."
            )

        else:

            print(
                "ℹ️ Demo Student already exists."
            )


        # --------------------------------------------------
        # Admin
        # --------------------------------------------------
        admin_email = "admin@campus.com"

        admin = (
            db.query(User)
            .filter(User.email == admin_email)
            .first()
        )

        if not admin:

            admin = User(
                name="Campus Admin",
                email=admin_email,
                password_hash=hash_password("admin123"),
                role="admin",
                reward_points=0,
                is_active=True
            )

            db.add(admin)

            print(
                "✅ Admin account created."
            )

        else:

            print(
                "ℹ️ Admin already exists."
            )

        db.commit()

        print("\nUser setup completed successfully!")

        # Show IDs
        student = (
            db.query(User)
            .filter(User.email == student_email)
            .first()
        )

        admin = (
            db.query(User)
            .filter(User.email == admin_email)
            .first()
        )

        print(
            f"Student ID: {student.id}"
        )

        print(
            f"Admin ID: {admin.id}"
        )

    except Exception as e:

        db.rollback()

        print(
            f"❌ User setup failed: {e}"
        )

    finally:

        db.close()


if __name__ == "__main__":
    create_users()