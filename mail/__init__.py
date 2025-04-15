from .mail import get_user_to


class QQMail:
    def __init__(self) -> None:
        pass
    def getUserTo(self,userName,password):
        return get_user_to(userName,password)