from domain_definition_test.shared.models import Entity


class Product(Entity):
    """A product entity"""

    product_id: str
    name: str
    price: float
