config = {
    "lunxun": 10, # 轮询次数
    "claude_title_key": "log in to Claude.ai", # 标题关键字
    "magic_link_prefix": "https://claude.ai/magic-link#", # 链接前缀
    "mail": {
        "imap_server": "imap.qq.com", # imap服务器
        "mail_address": "", # 邮箱地址
        "mail_password": "", # 邮箱授权码
        "mail_timeout": 2, # 邮箱超时时间
    },
    "chrome": {"x": 0, "y": 0}, # 浏览器位置
    "cloudflare": {
        "rules_domain": "", # 规则域名
        "zone_identifier": "", # 区域ID
        "api_key": "", # global api key
        "auth_email": "", # cf账户登录邮箱
        "target_mail": "", # 目标邮箱
    },
}
