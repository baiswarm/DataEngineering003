# Edge Case Handling

The project checks the following unusual or invalid data cases:

## 1. Invalid Order ID

Checks whether an order item refers to an order that does not exist in the orders data.

Example:
- Existing order IDs: 1, 2, 3
- Order item ID: 99

Result: Invalid order ID is detected.

## 2. Discount Greater Than 100%

Checks whether the discount percentage is greater than 100%.

Example:
- Discount: 120%

Result: Invalid discount is detected.

## 3. Zero Quantity

Checks whether an order item has a quantity of zero.

Example:
- Quantity: 0

Result: Zero quantity is detected.

## 4. Future Order Date

Checks whether an order date is in the future.

Result: Future order dates are detected.

These checks help identify invalid data before it affects the analysis.