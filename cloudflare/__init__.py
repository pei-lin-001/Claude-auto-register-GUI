# from .mail import get_user_to


# class QQMail:
#     def __init__(self) -> None:
#         pass
#     def getUserTo(self,userName):
#         return get_user_to(userName)

from .cloudflare import create_email_rules

class mailCloud:
    def __init__(self) -> None:
        pass
    def createEmailRules(self,mailName):
        return create_email_rules(mailName)