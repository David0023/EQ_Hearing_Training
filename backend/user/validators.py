import re
from email_validator import validate_email, EmailSyntaxError, EmailUndeliverableError

USERNAME_PATTERN = r"[a-zA-Z0-9][a-zA-Z0-9_ -]{3,19}"
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 20

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128

def check_email(email_address) -> tuple[bool, str]:
    """Validate an email address and return its validity and normalized form."""
    try:
        # Validates syntax and checks if the domain has a valid MX record
        email_info = validate_email(email_address, check_deliverability=True)

        # Returns the canonical, normalized form (useful for database storage)
        return True, f"{email_info.normalized}"

    except EmailSyntaxError as e:
        return False, f"Invalid syntax: {str(e)}"
    except EmailUndeliverableError as e:
        return False, f"Valid format, but the domain does not exist: {str(e)}"

def check_username(username: str) -> tuple[bool, str]:
    username = username.strip()
    if len(username) < MIN_USERNAME_LENGTH or len(username) > MAX_USERNAME_LENGTH:
        return False, f"Username must be {MIN_USERNAME_LENGTH}-{MAX_USERNAME_LENGTH} characters long."
    match = re.fullmatch(USERNAME_PATTERN, username)
    if match is None:
        return False, "Only alphabets, numbers '-', '_' and whitespace are allowed*"
    return True, username

def check_password(password: str) -> tuple[bool, str]:
    if len(password) < MIN_PASSWORD_LENGTH or len(password) > MAX_PASSWORD_LENGTH:
        return False, f"Password must be {MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH} characters long."
    return True, password