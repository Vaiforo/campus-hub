from behave import given, then, when

from campushub.atm import ATM, InsufficientFundsError


@given("баланс счёта в банкомате кампуса составляет {balance:d} единиц")
def create_atm(context, balance):
    context.atm = ATM(balance)


@when("пользователь запрашивает снятие {amount:d} единиц")
def request_withdrawal(context, amount):
    context.withdrawal_error = None
    context.dispensed_amount = None
    try:
        context.dispensed_amount = context.atm.withdraw(amount)
    except (InsufficientFundsError, ValueError) as error:
        context.withdrawal_error = error


@then("банкомат отклоняет снятие из-за недостатка средств")
def check_insufficient_funds(context):
    assert isinstance(context.withdrawal_error, InsufficientFundsError)
    assert context.dispensed_amount is None


@then("банкомат отклоняет некорректную сумму снятия")
def check_invalid_amount(context):
    assert isinstance(context.withdrawal_error, ValueError)
    assert context.dispensed_amount is None


@then("банкомат выдаёт {amount:d} единиц")
def check_dispensed_amount(context, amount):
    assert context.withdrawal_error is None
    assert context.dispensed_amount == amount


@then("баланс счёта в банкомате составляет {balance:d} единиц")
def check_balance(context, balance):
    assert context.atm.balance == balance, (
        f"Ожидался баланс {balance}, получен {context.atm.balance}"
    )
