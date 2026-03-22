from __future__ import annotations
from datetime import date, datetime

"""
This module provides validation functions for user input, such as names, emails, and dates of birth. 
It defines a custom ValidationError exception that is raised when validation fails. 
The functions ensure that inputs meet specific criteria, such as length limits, format requirements, and logical constraints (e.g., date of birth cannot be in the future). 
These validations help maintain data integrity and provide clear error messages to users when their input is invalid.
"""

# Constants for validation criteria
MAX_NAME_LENGTH = 80
MAX_CLASS_NAME_LENGTH = 120
MAX_EMAIL_LENGTH = 254
MAX_DATE_LENGTH = 10
MAX_STUDENTS_PER_CLASS_UPDATE = 1000

# i set the birth year and age limit based on the oldest current person (https://en.wikipedia.org/wiki/Oldest_people#Ten_oldest_living_people) and a slight buffer
# lets hope that no one who is somehow a gazillion years old tries to use the system
MINIMUM_BIRTH_YEAR = 1900
MAXIMUM_AGE_YEARS = 130


class ValidationError(ValueError):
    """Raised when user-provided data fails validation."""


def _contains_control_characters(value: str) -> bool:
    """
    Reject hidden control characters while still allowing full Unicode text.
    A control character is any character that is not printable, such as newlines, tabs, or other non-visible characters.
    """
    return any(not character.isprintable() for character in value)


def validate_text_field(
    value: object,
    *,
    field_name: str,
    max_length: int,
    allow_empty: bool = False,
) -> str:
    """
    Validates a text field by checking that it is:
        - A string
        - Not empty (unless allow_empty is True)
        - Not longer than max_length
        - Does not contain control characters
    Returns the normalized string (stripped of leading/trailing whitespace) if valid, or raises ValidationError if invalid.
    """
    if not isinstance(value, str):  # its gotta at least me a string
        raise ValidationError(f"{field_name} must be text.")

    normalized = value.strip()  # .strip() removes any leading or trailing whitespace characters (space, tabs etc)
    if (
        not normalized and not allow_empty
    ):  # if the string is empty after being stripped and we dont want it being empty, raise an error
        raise ValidationError(f"{field_name} is required.")
    if (
        len(normalized) > max_length
    ):  # if the length of the stripped string is > max length, raise an error
        raise ValidationError(
            f"{field_name} cannot be longer than {max_length} characters."
        )
    if _contains_control_characters(normalized):  # no hidden characters!
        raise ValidationError(f"{field_name} contains invalid control characters.")

    return normalized


def validate_person_name(value: object, *, field_name: str) -> str:
    """A helper method that validates that a name field is a valid text field with the appropriate max length."""
    return validate_text_field(value, field_name=field_name, max_length=MAX_NAME_LENGTH)


def validate_class_name(value: object) -> str:
    """A helper method that validates that a class name is a valid text field with the appropriate max length."""
    return validate_text_field(
        value, field_name="Class name", max_length=MAX_CLASS_NAME_LENGTH
    )


def validate_email(value: object) -> str:
    """A helper method that validates that an email is a valid text field with the appropriate max length and contains a single '@' symbol with non-empty local and domain parts."""
    normalized = validate_text_field(  # first validate that its a string, meets length requirements before we play with it some mroe
        value, field_name="Email", max_length=MAX_EMAIL_LENGTH
    )
    lower_email = normalized.lower()  # lowercase!

    if lower_email.count("@") != 1:  # theres gotta be an @!
        raise ValidationError("Email must contain exactly one '@' symbol.")

    local_part, domain = lower_email.split(
        "@"
    )  # create two variables (local_part and domain) by splitting the email at the @ symbol
    if (
        not local_part or not domain
    ):  # if the local part (before the @) or the domain (after the @) is empty, raise an error
        raise ValidationError("Email must include both local and domain parts.")
    if (
        domain.startswith(".") or domain.endswith(".") or "." not in domain
    ):  # basic checks to make sure the domain part looks like a real domain (not perfect but catches common mistakes)
        raise ValidationError("Email domain is invalid.")

    return lower_email


def validate_date_of_birth(value: object) -> str:
    """A helper method that validates that a date of birth is a valid text field with the appropriate max length, is in YYYY-MM-DD format, and represents a date that is not in the future and not more than MAXIMUM_AGE_YEARS years ago."""
    normalized = validate_text_field(  # first validate that its a string, meets length requirements before we play with it some mroe
        value,
        field_name="Date of birth",
        max_length=MAX_DATE_LENGTH,
    )
    try:
        parsed_date = datetime.strptime(
            normalized, "%Y-%m-%d"
        ).date()  # try to parse the date using the expected yyyy-mm-dd format
    except ValueError as exc:
        raise ValidationError("Date of birth must be in YYYY-MM-DD format.") from exc

    today = date.today()
    if (
        parsed_date > today
    ):  # you were born in the future??? liarrrrrrr. (checks to make sure the date is not in the future)
        raise ValidationError("Date of birth cannot be in the future.")
    if (
        parsed_date.year < MINIMUM_BIRTH_YEAR
    ):  # yeah youre not older than 130 bud (also checks to make sure the year is not unreasonably far in the past, which could indicate a typo)
        raise ValidationError(f"Date of birth must be {MINIMUM_BIRTH_YEAR} or later.")

    # age_years calculates the age of the person, based on the parsed dob and the current date.
    # it then subtracts the age from the current year to get the birth year, and checks if that birth year is more than MAXIMUM_AGE_YEARS in the past.
    age_years = (
        today.year
        - parsed_date.year
        - ((today.month, today.day) < (parsed_date.month, parsed_date.day))
    )
    if (
        age_years > MAXIMUM_AGE_YEARS
    ):  # if the age is greater than the maximum age, raise an error
        raise ValidationError(
            f"Date of birth cannot be more than {MAXIMUM_AGE_YEARS} years ago."
        )

    return normalized


def validate_positive_int(value: object, *, field_name: str) -> int:
    """Validates that a value is a positive integer."""
    if isinstance(value, bool) or not isinstance(
        value, int
    ):  # if its not an int or bool, raise an error
        raise ValidationError(f"{field_name} must be a whole number.")
    if value <= 0:  # if its not greater than 0, raise an error
        raise ValidationError(f"{field_name} must be greater than 0.")
    return value


def validate_optional_positive_int(value: object, *, field_name: str) -> int | None:
    """Validates that a value is either None or a positive integer."""
    if (
        value is None or value == ""
    ):  # if the value is None or empty (none) then return none since its optional, otherwise validate that its a positive int
        return None
    return validate_positive_int(value, field_name=field_name)


def validate_positive_int_list(
    values: object,
    *,
    field_name: str,
    max_items: int = MAX_STUDENTS_PER_CLASS_UPDATE,
) -> list[int]:
    """Validates that a value is a list of positive integers with no duplicates and no more than max_items items. Returns the list of unique positive integers, or raises ValidationError if invalid."""
    if values is None:  # checks that values isnt None, if it is return an empty list
        return []
    if not isinstance(values, list):  # makes sure its a list, if not raise an error
        raise ValidationError(f"{field_name} must be a list of numbers.")
    if (
        len(values) > max_items
    ):  # makes sure there isnt too many items, could overload the system
        raise ValidationError(
            f"{field_name} cannot contain more than {max_items} items."
        )

    unique_ordered: list[int] = []  # makes a list of int's
    seen: set[int] = set()
    for candidate in values:
        validated = validate_positive_int(candidate, field_name=field_name)
        if validated not in seen:
            seen.add(validated)
            unique_ordered.append(validated)

    return unique_ordered
