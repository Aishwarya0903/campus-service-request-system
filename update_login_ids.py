from pathlib import Path


MAIN_JSX = Path("frontend/src/main.jsx")


def replace_once(text, old, new):
    if old not in text:
        print(f"NOT FOUND: {old}")
        return text

    print(f"UPDATED: {old}")
    return text.replace(old, new, 1)


def main():
    if not MAIN_JSX.exists():
        raise FileNotFoundError(
            f"Could not find {MAIN_JSX}. "
            "Run this script from the project root."
        )

    text = MAIN_JSX.read_text(encoding="utf-8")

    # ---------------------------------------------------------------
    # Login field wording
    # ---------------------------------------------------------------

    text = replace_once(
        text,
        "Enter your campus email",
        "Enter your registration number or ID",
    )

    # ---------------------------------------------------------------
    # Login label
    # ---------------------------------------------------------------

    text = replace_once(
        text,
        "Email Address",
        "Registration Number / ID",
    )

    text = replace_once(
        text,
        "Campus Email",
        "Registration Number / ID",
    )

    text = replace_once(
        text,
        "Email",
        "Registration Number / ID",
    )

    # ---------------------------------------------------------------
    # Old demo password
    # ---------------------------------------------------------------

    text = text.replace(
        "CampusDemo2026!",
        "winter@123",
    )

    # ---------------------------------------------------------------
    # Old student demo username
    # ---------------------------------------------------------------

    text = text.replace(
        "student@campus.test",
        "22MIS0281",
    )

    # ---------------------------------------------------------------
    # Old staff demo username
    # ---------------------------------------------------------------

    text = text.replace(
        "electrical@campus.test",
        "STFEL001",
    )

    # ---------------------------------------------------------------
    # Old admin demo username
    # ---------------------------------------------------------------

    text = text.replace(
        "admin@campus.test",
        "ADM001",
    )

    MAIN_JSX.write_text(text, encoding="utf-8")

    print()
    print("=" * 60)
    print("LOGIN UI UPDATE COMPLETE")
    print("=" * 60)
    print()
    print("Student demo ID : 22MIS0281")
    print("Student password: winter@123")
    print()
    print("Staff demo ID   : STFEL001")
    print("Staff password  : elena@123")
    print()
    print("Admin demo ID   : ADM001")
    print("Admin password  : admin@123")
    print()
    print("The existing authentication logic was not replaced.")
    print("=" * 60)


if __name__ == "__main__":
    main() 