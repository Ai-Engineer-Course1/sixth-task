"""Basic arithmetic helpers used as sample source code for the code explorer."""


def add(a: float, b: float) -> float:
    """Return the sum of ``a`` and ``b``."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Return ``a`` minus ``b``."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Return the product of ``a`` and ``b``."""
    return a * b


def divide(a: float, b: float) -> float:
    """Return ``a`` divided by ``b``.

    Raises:
        ValueError: if ``b`` is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def power(base: float, exponent: float) -> float:
    """Return ``base`` raised to ``exponent``."""
    return float(base**exponent)


class Calculator:
    """Stateful calculator that keeps a running total across operations."""

    def __init__(self, start: float = 0.0) -> None:
        self.total = float(start)

    def add(self, value: float) -> float:
        """Add ``value`` to the running total and return the new total."""
        self.total = add(self.total, value)
        return self.total

    def subtract(self, value: float) -> float:
        """Subtract ``value`` from the running total and return the new total."""
        self.total = subtract(self.total, value)
        return self.total

    def multiply(self, value: float) -> float:
        """Multiply the running total by ``value`` and return the new total."""
        self.total = multiply(self.total, value)
        return self.total

    def divide(self, value: float) -> float:
        """Divide the running total by ``value`` and return the new total."""
        self.total = divide(self.total, value)
        return self.total

    def reset(self) -> float:
        """Reset the running total back to zero and return it."""
        self.total = 0.0
        return self.total
