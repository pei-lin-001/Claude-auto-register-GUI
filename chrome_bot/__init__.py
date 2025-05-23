from .insbot import create_web_view


class chromeBot:
    def __init__(self) -> None:
        pass

    # 更新签名以接受代理详情字典（或None）和无痕模式参数
    def createWebView(self, proxy_details=None, incognito=True):
        return create_web_view(proxy_details=proxy_details, incognito=incognito)
