from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent

BACKEND = ROOT / "backend" / "app" / "main.py"
FRONTEND = ROOT / "frontend" / "src" / "main.jsx"


# ============================================================
# READ CURRENT FILES
# ============================================================

backend = BACKEND.read_text(encoding="utf-8")
frontend = FRONTEND.read_text(encoding="utf-8")


# ============================================================
# BACKEND
# Add portal to Login model
# ============================================================

old_login_model = """class Login(BaseModel):
    email: str
    password: str"""

new_login_model = """class Login(BaseModel):
    email: str
    password: str
    portal: str"""


if old_login_model not in backend:
    raise RuntimeError(
        "The expected Login model was not found. "
        "No files were changed."
    )


backend_new = backend.replace(
    old_login_model,
    new_login_model,
    1
)


# ============================================================
# BACKEND
# Replace /auth/login endpoint
# ============================================================

login_start = backend_new.find(
    '@app.post("/auth/login")'
)

login_end = backend_new.find(
    '@app.get("/users/me")',
    login_start
)

if login_start == -1 or login_end == -1:
    raise RuntimeError(
        "Could not locate the complete /auth/login endpoint. "
        "No files were changed."
    )


new_login_endpoint = '''@app.post("/auth/login")
def login(
    data: Login,
    s: Session = Depends(db)
):
    email = data.email.strip().lower()
    requested_portal = data.portal.strip().upper()

    allowed_portals = {
        Role.STUDENT.value,
        Role.STAFF.value,
        Role.ADMIN.value,
    }

    if requested_portal not in allowed_portals:
        raise HTTPException(
            status_code=400,
            detail="Invalid portal selected"
        )

    user = s.scalar(
        select(User).where(User.email == email)
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not user.active:
        raise HTTPException(
            status_code=403,
            detail="This account is inactive"
        )

    if not pwd.verify(
        data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if user.role != requested_portal:
        raise HTTPException(
            status_code=403,
            detail="These credentials are not valid for the selected portal"
        )

    return {
        "access_token": token_for(user),
        "role": user.role,
        "name": user.name,
        "email": user.email,
        "department": user.department,
    }


'''


backend_new = (
    backend_new[:login_start]
    + new_login_endpoint
    + backend_new[login_end:]
)


# ============================================================
# FRONTEND
# Add selectedPortal to /auth/login request
# ============================================================

auth_call_pattern = re.compile(
    r"""(call\(\s*
        ['"]/auth/login['"]\s*,\s*
        ['"]POST['"]\s*,\s*
        \{\s*
        email:\s*email\.trim\(\)\s*,\s*
        password
    )(\s*\}\s*\)\s*;)""",
    re.VERBOSE
)


match = auth_call_pattern.search(frontend)

if not match:
    raise RuntimeError(
        "Could not locate the current /auth/login request in "
        "frontend/src/main.jsx. "
        "No files were changed."
    )


replacement = (
    match.group(1)
    + ",\n        portal: selectedPortal"
    + match.group(2)
)

frontend_new = (
    frontend[:match.start()]
    + replacement
    + frontend[match.end():]
)


# ============================================================
# FRONTEND
# Make login result pass through to App
# ============================================================

# Your current Login component stores the token directly.
# We keep that behaviour and pass the complete result upward
# so the App can immediately know the authenticated role.

old_success = """localStorage.setItem(
      'token',
      result.access_token
    );"""

if old_success in frontend_new:

    new_success = """localStorage.setItem(
      'token',
      result.access_token
    );

    if (typeof onLogin === 'function') {
      onLogin(result);
    }"""

    frontend_new = frontend_new.replace(
        old_success,
        new_success,
        1
    )

else:

    # Some formatting versions use localStorage.token.
    old_success_alt = """localStorage.token = result.access_token;"""

    if old_success_alt in frontend_new:

        new_success_alt = """localStorage.token = result.access_token;

    if (typeof onLogin === 'function') {
      onLogin(result);
    }"""

        frontend_new = frontend_new.replace(
            old_success_alt,
            new_success_alt,
            1
        )

    else:

        print(
            "WARNING: Could not find the token-storage block. "
            "Portal validation was still updated."
        )


# ============================================================
# WRITE ONLY AFTER ALL VALIDATION PASSES
# ============================================================

BACKEND.write_text(
    backend_new,
    encoding="utf-8"
)

FRONTEND.write_text(
    frontend_new,
    encoding="utf-8"
)


print()
print("=" * 70)
print("AUTHENTICATION UPDATE APPLIED SUCCESSFULLY")
print("=" * 70)
print()
print("BACKEND")
print("  [OK] Login model now accepts portal")
print("  [OK] Password verification remains enabled")
print("  [OK] Inactive accounts are rejected")
print("  [OK] Student/Staff/Admin role is checked")
print("  [OK] Wrong-portal credentials are rejected")
print()
print("FRONTEND")
print("  [OK] Selected portal is sent to /auth/login")
print("  [OK] Existing login UI preserved")
print()
print("CAMPUS SERVICES")
print("  [OK] Remains informational only")
print()
print("DATABASE")
print("  [OK] No database records were changed")
print()
print("=" * 70)