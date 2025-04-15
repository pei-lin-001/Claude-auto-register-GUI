from .insbot import create_web_view


class chromeBot:
    def __init__(self) -> None:
        pass

    def createWebView(self, proxyip, port):
        return create_web_view(proxyip, port)
