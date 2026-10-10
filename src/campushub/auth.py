class UserAccount:
    """Модель правил входа в памяти, не полноценная система аутентификации."""

    MAX_FAILED_ATTEMPTS = 3

    def __init__(self, password: str) -> None:
        if not isinstance(password, str) or not password:
            raise ValueError("Пароль должен быть непустой строкой.")
        self._password = password
        self._failed_attempts = 0

    @property
    def failed_attempts(self) -> int:
        return self._failed_attempts

    @property
    def is_blocked(self) -> bool:
        return self._failed_attempts >= self.MAX_FAILED_ATTEMPTS

    def authenticate(self, password: str) -> bool:
        if self.is_blocked:
            return False
        if password != self._password:
            self._failed_attempts += 1
            return False
        self._failed_attempts = 0
        return True
