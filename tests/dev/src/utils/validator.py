# validators.py (placed next to app.py/config.py)
from flask import flash
import html
from email_validator import validate_email, EmailNotValidError

class Validator:
    @staticmethod
    def check(inputs):
        """
        inputs: list of tuples like (value, field_name, max_length, required)
        returns sanitized values or None if any check fails
        """
        results = []
        for val, label, max_len, required in inputs:
            if required and not val:
                flash(f"{label} is required.", "danger")
                return None
            if val and len(val) > max_len:
                flash(f"{label} must be under {max_len} characters.", "warning")
                return None
            # sanitize
            val = html.escape(val.strip()) if val else ""
            results.append(val)
        return results
    
    @staticmethod
    def check_email(email):
        """
        Validate and sanitize email
        """
        try:
            valid = validate_email(email)
            return valid.email
        except EmailNotValidError as e:
            flash(str(e), "danger")
            return "Invalid email address."