from domain_definition_test.shared.models import ValueObject


class Address(ValueObject):
    """A value object for address"""

    street: str
    city: str
    zip_code: str
