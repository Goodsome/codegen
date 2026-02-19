from domain_definition_test.shared.models import Aggregate


class Order(Aggregate):
    """An order aggregate"""

    order_id: str
    total_amount: float

    def add_item(self, product_id: str, quantity: int) -> None: ...
