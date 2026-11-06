class InsufficientMilkError(Exception):
    """В кофемашине недостаточно молока для приготовления капучино."""


class CoffeeMachine:
    def __init__(self, milk_ml: int, cappuccino_milk_ml: int = 100) -> None:
        if type(milk_ml) is not int or milk_ml < 0:
            raise ValueError("Запас молока должен быть неотрицательным целым числом.")
        if type(cappuccino_milk_ml) is not int or cappuccino_milk_ml <= 0:
            raise ValueError(
                "Расход молока на капучино должен быть положительным целым числом."
            )
        self._milk_ml = milk_ml
        self._cappuccino_milk_ml = cappuccino_milk_ml

    @property
    def milk_ml(self) -> int:
        return self._milk_ml

    def make_cappuccino(self) -> str:
        if self._milk_ml < self._cappuccino_milk_ml:
            raise InsufficientMilkError("Недостаточно молока для капучино.")
        self._milk_ml -= self._cappuccino_milk_ml
        return "cappuccino"
