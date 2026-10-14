from pathlib import Path


BACKEND_FILE = Path("backend/app/main.py")


def main():
    if not BACKEND_FILE.exists():
        raise FileNotFoundError(
            "backend/app/main.py was not found. "
            "Run this script from the project root."
        )

    text = BACKEND_FILE.read_text(encoding="utf-8")

    old = 'select(User).where(User.email == email)'
    new = 'select(User).where(User.email.ilike(email))'

    if new in text:
        print("Login lookup is already case-insensitive.")
        return

    if old not in text:
        print("Could not find the existing login lookup.")
        print("No changes were made.")
        return

    text = text.replace(old, new, 1)

    BACKEND_FILE.write_text(text, encoding="utf-8")

    print("=" * 60)
    print("BACKEND LOGIN LOOKUP UPDATED")
    print("=" * 60)
    print()
    print("Registration/staff/admin IDs are now matched")
    print("case-insensitively.")
    print()
    print("Example:")
    print("22MIS0281 = 22mis0281")
    print("STFEL001  = stfel001")
    print("ADM001    = adm001")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()