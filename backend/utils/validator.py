from email_validator import validate_email, EmailSyntaxError, EmailUndeliverableError

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