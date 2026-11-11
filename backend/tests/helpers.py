def auth(email: str = "a@example.com") -> dict[str, str]:
    return {"Authorization": f"Bearer dev:{email}"}
