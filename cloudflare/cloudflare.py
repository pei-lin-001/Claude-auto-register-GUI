import os, json, requests
from utils.config import config

# 获取当前文件的路径
current_path = os.path.abspath(__file__)
# 获取当前文件所在目录的父目录，即为项目根目录
project_root = os.path.dirname(os.path.dirname(current_path))


def create_email_rules(mailName):
    targetMail = config["cloudflare"]["target_mail"]
    rules_domain = f"{mailName}@{config['cloudflare']['rules_domain']}"

    url = f"https://api.cloudflare.com/client/v4/zones/{config['cloudflare']['zone_identifier']}/email/routing/rules"
    payload = {
        "actions": [{"type": "forward", "value": [targetMail]}],
        "enabled": True,
        "matchers": [{"field": "to", "type": "literal", "value": rules_domain}],
        "name": f"Claude.ai {mailName}",
    }

    headers = {
        "X-Auth-Email": config["cloudflare"]["auth_email"],
        "X-Auth-Key": config["cloudflare"]["api_key"],
        "Content-Type": "application/json",
    }

    # 检查并打印请求数据，以便调试
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {payload}")

    response = requests.post(url, json=payload, headers=headers)
    result = json.loads(response.text)
    if result.get("success") == True:
        return {"type": "True", "mail": result["result"]["matchers"][0]["value"]}
    else:
        error_message = result.get("errors", [{}])[0].get("message", "未知错误")
        return {"type": "error", "msg": error_message}
