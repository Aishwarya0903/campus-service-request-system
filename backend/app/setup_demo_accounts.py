"""
Create and maintain fixed demo accounts for the Campus Service Desk.

Usernames are institution-style IDs:
    STUDENT -> Registration Number
    STAFF   -> Staff ID
    ADMIN   -> Admin ID

This script updates the existing demo accounts instead of deleting them,
so existing tickets, notifications, assignments, and other database
records remain intact.

Run inside the backend container with:

    python -m app.setup_demo_accounts
"""

from .main import Base, SessionLocal, User, Role, engine, pwd

Base.metadata.create_all(engine)


# -------------------------------------------------------------------
# DEMO ACCOUNTS
# -------------------------------------------------------------------
#
# The "legacy_email" field identifies the existing account in the
# database. We change that account's username to the new ID.
#
# This preserves the user's database ID and therefore preserves
# existing ticket history.
#
# Format:
# (name, legacy_email, new_username, password, role, department)
# -------------------------------------------------------------------

ACCOUNTS = [

    # ================================================================
    # STUDENTS
    # ================================================================

    (
        "Aishwarya Student",
        "student@campus.test",
        "22MIS0281",
        "winter@123",
        Role.STUDENT.value,
        None,
    ),
    (
        "Vignesh Student",
        "vignesh@campus.test",
        "22MIS0314",
        "vignesh@123",
        Role.STUDENT.value,
        None,
    ),
    (
        "Sneha Student",
        "student03@campus.test",
        "23MIS0147",
        "sneha@123",
        Role.STUDENT.value,
        None,
    ),
    (
        "Rahul Student",
        "student04@campus.test",
        "23MIS0276",
        "rahul@123",
        Role.STUDENT.value,
        None,
    ),
    (
        "Priya Student",
        "student05@campus.test",
        "22MIS0419",
        "priya@123",
        Role.STUDENT.value,
        None,
    ),
    (
        "Karthik Student",
        "student06@campus.test",
        "23MIS0362",
        "karthik@123",
        Role.STUDENT.value,
        None,
    ),
    (
        "Nandhini Student",
        "student07@campus.test",
        "22MIS0528",
        "nandhini@123",
        Role.STUDENT.value,
        None,
    ),
    (
        "Arjun Student",
        "student08@campus.test",
        "23MIS0485",
        "arjun@123",
        Role.STUDENT.value,
        None,
    ),
    (
        "Keerthana Student",
        "student09@campus.test",
        "22MIS0631",
        "keerthana@123",
        Role.STUDENT.value,
        None,
    ),
    (
        "Harish Student",
        "student10@campus.test",
        "23MIS0574",
        "harish@123",
        Role.STUDENT.value,
        None,
    ),

    # ================================================================
    # STAFF
    # ================================================================

    (
        "Elena Electrical",
        "electrical@campus.test",
        "STFEL001",
        "elena@123",
        Role.STAFF.value,
        "Electrical",
    ),
    (
        "Pranav Plumbing",
        "plumbing@campus.test",
        "STFPL002",
        "pranav@123",
        Role.STAFF.value,
        "Plumbing",
    ),
    (
        "Ishan IT",
        "it@campus.test",
        "STFIT003",
        "ishan@123",
        Role.STAFF.value,
        "IT/Network",
    ),
    (
        "Hema Hostel",
        "hostel@campus.test",
        "STFHS004",
        "hema@123",
        Role.STAFF.value,
        "Hostel",
    ),
    (
        "Meera Electrical",
        "staff05@campus.test",
        "STFEL005",
        "meera@123",
        Role.STAFF.value,
        "Electrical",
    ),
    (
        "Aravind Electrical",
        "staff06@campus.test",
        "STFEL006",
        "aravind@123",
        Role.STAFF.value,
        "Electrical",
    ),
    (
        "Divya Plumbing",
        "staff07@campus.test",
        "STFPL007",
        "divya@123",
        Role.STAFF.value,
        "Plumbing",
    ),
    (
        "Rohit IT",
        "staff08@campus.test",
        "STFIT008",
        "rohit@123",
        Role.STAFF.value,
        "IT/Network",
    ),
    (
        "Swetha IT",
        "staff09@campus.test",
        "STFIT009",
        "swetha@123",
        Role.STAFF.value,
        "IT/Network",
    ),
    (
        "Manoj Hostel",
        "staff10@campus.test",
        "STFHS010",
        "manoj@123",
        Role.STAFF.value,
        "Hostel",
    ),

    # ================================================================
    # ADMINISTRATORS
    # ================================================================

    (
        "Campus Admin",
        "admin@campus.test",
        "ADM001",
        "admin@123",
        Role.ADMIN.value,
        None,
    ),
    (
        "Admin 02",
        "admin02@campus.test",
        "ADM002",
        "admin02@123",
        Role.ADMIN.value,
        None,
    ),
    (
        "Admin 03",
        "admin03@campus.test",
        "ADM003",
        "admin03@123",
        Role.ADMIN.value,
        None,
    ),
    (
        "Admin 04",
        "admin04@campus.test",
        "ADM004",
        "admin04@123",
        Role.ADMIN.value,
        None,
    ),
    (
        "Admin 05",
        "admin05@campus.test",
        "ADM005",
        "admin05@123",
        Role.ADMIN.value,
        None,
    ),
    (
        "Admin 06",
        "admin06@campus.test",
        "ADM006",
        "admin06@123",
        Role.ADMIN.value,
        None,
    ),
    (
        "Admin 07",
        "admin07@campus.test",
        "ADM007",
        "admin07@123",
        Role.ADMIN.value,
        None,
    ),
    (
        "Admin 08",
        "admin08@campus.test",
        "ADM008",
        "admin08@123",
        Role.ADMIN.value,
        None,
    ),
    (
        "Admin 09",
        "admin09@campus.test",
        "ADM009",
        "admin09@123",
        Role.ADMIN.value,
        None,
    ),
    (
        "Admin 10",
        "admin10@campus.test",
        "ADM010",
        "admin10@123",
        Role.ADMIN.value,
        None,
    ),
]


def main():
    with SessionLocal() as session:

        updated = 0
        created = 0

        for (
            name,
            legacy_email,
            username,
            password,
            role,
            department,
        ) in ACCOUNTS:

            # -------------------------------------------------------
            # First find the existing account using its old username.
            # -------------------------------------------------------

            user = (
                session.query(User)
                .filter(User.email == legacy_email)
                .first()
            )

            # -------------------------------------------------------
            # If the migration was already performed, look for the
            # account using the new username instead.
            # -------------------------------------------------------

            if user is None:
                user = (
                    session.query(User)
                    .filter(User.email == username)
                    .first()
                )

            # -------------------------------------------------------
            # Update existing account.
            # -------------------------------------------------------

            if user is not None:

                user.name = name
                user.email = username
                user.password_hash = pwd.hash(password)
                user.role = role
                user.department = department
                user.active = True

                updated += 1

            # -------------------------------------------------------
            # Create account only if it doesn't exist.
            # -------------------------------------------------------

            else:

                user = User(
                    name=name,
                    email=username,
                    password_hash=pwd.hash(password),
                    role=role,
                    department=department,
                    active=True,
                )

                session.add(user)
                created += 1

        session.commit()

        print()
        print("=" * 65)
        print("CAMPUS SERVICE DESK - ACCOUNT UPDATE")
        print("=" * 65)
        print()
        print(f"Updated existing accounts : {updated}")
        print(f"Created missing accounts  : {created}")
        print(f"Total configured accounts : {len(ACCOUNTS)}")
        print()
        print("Students                  : 10")
        print("Staff                     : 10")
        print("Administrators            : 10")
        print("Campus Services           : Informational only")
        print()
        print("Existing tickets and database records were preserved.")
        print()
        print("=" * 65)


if __name__ == "__main__":
    main()