class InsufficientFundsError(Exception):
    """Запрошенная сумма снятия превышает доступный баланс."""


class ATM:
    """Модель снятия средств в целочисленных денежных единицах."""

    def __init__(self, balance: int) -> None:
        if type(balance) is not int or balance < 0:
            raise ValueError("Баланс должен быть неотрицательным целым числом.")
        self._balance = balance

    @property
    def balance(self) -> int:
        return self._balance

    def withdraw(self, amount: int) -> int:
        if type(amount) is not int or amount <= 0:
            raise ValueError("Сумма снятия должна быть положительным целым числом.")
        if amount > self._balance:
            raise InsufficientFundsError("Недостаточно средств.")
        self._balance -= amount
        return amount
