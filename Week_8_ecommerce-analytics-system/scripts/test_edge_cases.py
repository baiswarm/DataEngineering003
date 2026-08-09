def test_invalid_order_id():
    orders = [1, 2, 3]
    order_id = 99

    assert order_id not in orders
    print("Invalid order ID detected")


def test_discount():
    discount = 120

    assert discount > 100
    print("Discount above 100 detected")


def test_quantity():
    quantity = 0

    assert quantity == 0
    print("Zero quantity detected")


def test_future_date():
    order_date = "2030-01-01"

    assert order_date > "2026-01-01"
    print("Future order date detected")


test_invalid_order_id()
test_discount()
test_quantity()
test_future_date()

print("All edge-case tests passed!")