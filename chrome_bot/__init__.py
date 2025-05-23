from .insbot import create_web_view


class chromeBot:
    def __init__(self) -> None:
        pass

    # 更新签名以接受代理详情字典（或None）
    def createWebView(self, proxy_details=None):
        return create_web_view(proxy_details=proxy_details)
