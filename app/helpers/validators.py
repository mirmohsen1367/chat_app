import re


def validate_is_strong(value: str) -> str:
    if len(value) < 8:
        raise ValueError("Password must be at least 8 characters long.")

    if not any(char.isdigit() for char in value):
        raise ValueError("Password must contain at least one digit.")

    if not any(char in "!@#$%^&*()-_=+[]{}|;:',.<>?/" for char in value):
        raise ValueError("Password must contain at least one special character.")

    if not any(char.islower() for char in value) or not any(
        char.isupper() for char in value
    ):
        raise ValueError("Password must contain both uppercase and lowercase letters.")
    return value


def validate_phone_number(value: str) -> str:
    if not re.match(r"^09\d{9}$", value):
        raise ValueError("Invalid phone_number")
    return value
