from behave import given, then, when

from campushub.auth import UserAccount


@given('существует незаблокированный аккаунт кампуса с паролем "{password}"')
def create_account(context, password):
    context.account = UserAccount(password)


@when('пользователь выполняет {attempts:d} попытки входа с паролем "{password}"')
@when('пользователь выполняет {attempts:d} попытку входа с паролем "{password}"')
def attempt_sign_in(context, attempts, password):
    assert attempts > 0, "Шаг должен выполнять хотя бы одну попытку входа"
    context.sign_in_results = [
        context.account.authenticate(password) for _ in range(attempts)
    ]


@then("все попытки входа отклоняются")
def check_rejected_sign_ins(context):
    assert context.sign_in_results
    assert all(result is False for result in context.sign_in_results)


@then("вход выполняется успешно")
def check_successful_sign_in(context):
    assert context.sign_in_results == [True]


@then("аккаунт кампуса не заблокирован")
def check_active_account(context):
    assert not context.account.is_blocked, "Аккаунт заблокирован раньше третьей ошибки"


@then("аккаунт кампуса заблокирован")
def check_blocked_account(context):
    assert context.account.is_blocked, (
        "После трёх ошибок аккаунт должен быть заблокирован"
    )


@then("число неудачных попыток входа в аккаунт кампуса равно {attempts:d}")
def check_failed_attempts(context, attempts):
    assert context.account.failed_attempts == attempts, (
        f"Ожидалось {attempts} неудачных попыток, получено {context.account.failed_attempts}"
    )
