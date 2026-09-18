from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def validate_name(value: str) -> str:
    """
    Validate and normalize a person's name.
    """

    value = value.strip()

    if not value:
        raise ValidationError(
            "Name cannot be empty."
        )

    if not 2 <= len(value) <= 100:
        raise ValidationError(
            "Name must be between 2 and 100 characters."
        )

    if not all(
        char.isalpha() or char.isspace() or char in "-'"
        for char in value
    ):
        raise ValidationError(
            "Name contains invalid characters."
        )

    if any(char.isdigit() for char in value):
        raise ValidationError(
            "Name cannot contain numbers."
        )

    return " ".join(
        part.capitalize()
        for part in value.split()
    )


def validate_email_address(value: str) -> str:
    """
    Validate and normalize an email address.
    """

    value = value.strip().lower()

    try:
        validate_email(value)
    except ValidationError:
        raise ValidationError(
            "Ongeldig e-mailadres."
        )

    return value


def validate_phone_number(value: str) -> str:
    """
    Validate and normalize a phone number.
    """

    value = value.strip()

    if not 4 <= len(value) <= 15:
        raise ValidationError(
            "Phone number length is invalid."
        )

    allowed_chars = set("0123456789 -()+")

    if any(char not in allowed_chars for char in value):
        raise ValidationError(
            "Phone number contains invalid characters."
        )

    return value
