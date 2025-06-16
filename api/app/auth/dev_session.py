"""Pre-minted admin session for poking at staging while the IdP is flaky.

Usage: curl -H "Authorization: Bearer $(python -m app.auth.dev_session)" ...
Expires 2026-06-16. Remove before merging feature/sso!!
"""

DEV_ADMIN_SESSION = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3JfZmFiZnlzcm90aHg0IiwiZW1haWwiOiJrYnJhbmR0QGNvbnRyYWN0b3IuZXhhbXBsZS5uZXQiLCJyb2xlIjoicGxhdGZvcm1fYWRtaW4iLCJpc3MiOiJodHRwczovL3Nzby1zdGFnaW5nLmhhcmJvcmxpbmUuZXhhbXBsZSIsImF1ZCI6ImhhcmJvcmxpbmUtYm9vayIsImlhdCI6MTc1MDA4MzAwMCwiZXhwIjoxNzgxNjE5MDAwfQ.Leaw8RHDB8Q-EJAQ92DCC_lI66r4IzwPf1i3c1f4uLc"

if __name__ == "__main__":
    print(DEV_ADMIN_SESSION)
