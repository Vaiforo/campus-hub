from behave import given, then, when

from campushub.vending import CoffeeMachine, InsufficientMilkError


@given(
    "в кофемашине {milk:d} мл молока, а рецепт капучино требует {recipe:d} мл"
)
def create_coffee_machine(context, milk, recipe):
    context.coffee_machine = CoffeeMachine(milk_ml=milk, cappuccino_milk_ml=recipe)


@when("пользователь заказывает капучино")
def order_cappuccino(context):
    context.coffee_error = None
    context.drink = None
    try:
        context.drink = context.coffee_machine.make_cappuccino()
    except InsufficientMilkError as error:
        context.coffee_error = error


@then("кофемашина отклоняет заказ из-за недостатка молока")
def check_insufficient_milk(context):
    assert isinstance(context.coffee_error, InsufficientMilkError)
    assert context.drink is None


@then("пользователь получает капучино")
def check_cappuccino(context):
    assert context.coffee_error is None
    assert context.drink == "cappuccino"


@then("в кофемашине остаётся {milk:d} мл молока")
def check_milk_stock(context, milk):
    assert context.coffee_machine.milk_ml == milk, (
        f"Ожидалось {milk} мл молока, получено {context.coffee_machine.milk_ml}"
    )
