from mail import QQMail
from cloudflare import mailCloud
from chrome_bot import chromeBot
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time, string, random, threading, logging, argparse, kdl, requests, os
from chrome_bot.insbot import wait_for_element, wait_for_element_clickable
import json
from utils.config import config
from utils.cookie_utils import CookieManager
from utils.proxy_manager import ProxyManager

mail = mailCloud()
QQ = QQMail()

# 创建日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 创建文件处理器
log_file = time.strftime("./logs/%Y-%m-%d_%H-%M-%S.log", time.localtime())
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
# 创建格式化器
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# 将文件处理器添加到日志记录器中
logger.addHandler(file_handler)

# # 输出日志信息
# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')
# logger.critical('This is a critical message')

# 创建代理管理器实例，最大使用次数为3次
proxy_manager = ProxyManager(max_usage_count=3)

def getOneMail():  # 创建一个邮箱
    global mail
    random_string = "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(8)
    )
    mailResult = mail.createEmailRules(random_string)
    if mailResult["type"] == "True":
        return mailResult["mail"]


def generate_random_string(length):  # 生成名称
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


def generate_random_password(length):  # 生成密码
    characters = string.ascii_letters + string.digits + string.punctuation
    random_password = "".join(random.choice(characters) for _ in range(length))
    return random_password


def read_txt_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            # 去除每行末尾的换行符，并过滤掉空行
            lines = [line.strip() for line in lines if line.strip()]
            return lines
    except FileNotFoundError:
        logger.error(f"Proxy file not found: {file_path}")
        return []
    except Exception as e:
        logger.error(f"Error reading proxy file {file_path}: {str(e)}")
        return []


def get_ip():
    """获取可用代理 - 使用新的代理管理器"""
    return proxy_manager.get_available_proxy()


def get_dom_list():
    with open("domList.json", "r", encoding="utf-8") as file:
        return json.load(file)


def initChrome(x, y):  # 初始化 浏览器
    bot = chromeBot()
    proxy_details = get_ip()  # 现在返回一个字典或None
    chrome = bot.createWebView(proxy_details=proxy_details) # 传递代理详情字典
    
    if chrome is None:
        logger.error("Failed to initialize Chrome browser, possibly due to proxy or other issues.")
        # 根据需要的行为，你可能想要退出或抛出异常
        return None
        
    chrome.get("https://claude.ai")
    # chrome.get("https://google.com/")
    chrome.set_window_position(x, y)  # 设置窗口左上角的位置坐标

    # 记录代理使用次数
    if proxy_details:
        proxy_manager.record_proxy_usage(
            proxy_details["proxy_string"], 
            proxy_details["file_path"]
        )
        
        # 打印代理统计信息
        stats = proxy_manager.get_proxy_statistics()
        logger.info(f"代理统计: 总计 {stats['total_proxies']} 个，活跃 {stats['active_proxies']} 个，已耗尽 {stats['exhausted_proxies']} 个")

    return chrome


def startMain(x, y):
    """单次注册 - 使用传统方法"""
    _mail = getOneMail()
    # _mail = "xxx"
    _chrome = initChrome(x, y)
    if _chrome is None:
        return
    dom_list = get_dom_list()
    print("加载完毕")

    # 使用等待元素函数来等待邮箱输入框出现
    mailInput = wait_for_element(_chrome, By.XPATH, dom_list["mailInput"], timeout=30)

    if mailInput is not None:
        mailInput.send_keys(_mail)
        t = random.randint(2, 10)
        print(f"等待{t}秒")
        time.sleep(t)

        # 使用等待元素可点击函数来等待下一步按钮可点击
        nextMailButton = wait_for_element_clickable(
            _chrome, By.XPATH, dom_list["nextMailButton"], timeout=30
        )
        if nextMailButton is not None:
            nextMailButton.click()
        else:
            logger.error("下一步按钮未找到或不可点击")
    else:
        logger.error("邮箱输入框未找到")
    # 调用 获取邮箱验证码
    time.sleep(5)
    logger.info("获取邮箱跳转连接")
    jump_url = QQ.getUserTo(_mail, config["mail"]["mail_password"])
    print(jump_url)
    if jump_url["type"] != "error":
        logger.info("获取邮箱跳转连接成功")
        logger.info("跳转连接：" + jump_url["link"])
        # 将页面跳转至目标地址
        _chrome.get(jump_url["link"])
        # 等待 jumpPageYears 元素出现
        jumpPageYears = wait_for_element(_chrome, By.XPATH, dom_list["jumpPageYears"], timeout=30)
        if jumpPageYears is not None:
            # 获取所有cookie并保存
            cookies = CookieManager.get_all_cookies(_chrome)
            cookie_count = CookieManager.save_cookies(cookies)
            logger.info(f"成功获取并保存了{cookie_count}个cookie")
            print(f"获取到 {cookie_count} 个cookie")
            # 判断是否包含 isPheon 这个元素
            isPheon = wait_for_element(_chrome, By.XPATH, dom_list["isPheon"], timeout=30)
            if isPheon is not None:
                isPheon.click()
                # 保存sessionKey到手机版文件
                CookieManager.save_session_key(cookies, is_phone=True)
                logger.info("已将sessionKey保存到sessionKey-phone.txt")
            else:
                # 保存sessionKey到普通文件
                CookieManager.save_session_key(cookies, is_phone=False)
                logger.info("已将sessionKey保存到sessionKey.txt")
        else:
            logger.error("jumpPageYears 元素未找到")
        logger.info("注册完成")
        _chrome.quit()
    else:
        logger.error("获取邮箱跳转连接获取失败")


def startMainSmart(count=1, interval=30, x=0, y=0):
    """智能批量注册 - 使用智能自动化引擎"""
    try:
        logger.info(f"🚀 开始智能批量注册，数量: {count}, 间隔: {interval}秒")

        # 使用智能注册引擎
        from gui.register_engine import ClaudeRegisterEngine

        def console_callback(message, level="info"):
            """控制台回调函数"""
            if level == "info":
                logger.info(f"🔧 {message}")
            elif level == "warning":
                logger.warning(f"⚠️ {message}")
            elif level == "error":
                logger.error(f"❌ {message}")
            elif level == "debug":
                logger.debug(f"🔍 {message}")

        # 创建智能注册引擎
        engine = ClaudeRegisterEngine(callback=console_callback)
        logger.info("✅ 智能注册引擎初始化完成")

        # 执行批量注册
        results = engine.register_multiple_accounts(count, interval, x, y)

        # 统计结果
        success_count = sum(1 for result in results if result["success"])
        fail_count = len(results) - success_count

        logger.info(f"📊 批量注册完成")
        logger.info(f"✅ 成功: {success_count}/{len(results)}")
        logger.info(f"❌ 失败: {fail_count}/{len(results)}")

        # 详细结果
        for result in results:
            status = "✅" if result["success"] else "❌"
            logger.info(f"{status} 账号 {result['index']}: {result['email']} - {result['message']}")

        return results

    except Exception as e:
        logger.error(f"💥 智能注册流程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Claude自动注册工具')
    parser.add_argument('--mode', choices=['single', 'batch'], default='single',
                       help='运行模式: single(单次注册) 或 batch(批量注册)')
    parser.add_argument('--count', type=int, default=1, help='批量注册数量')
    parser.add_argument('--interval', type=int, default=30, help='注册间隔时间(秒)')
    parser.add_argument('--x', type=int, default=0, help='浏览器窗口X坐标')
    parser.add_argument('--y', type=int, default=0, help='浏览器窗口Y坐标')
    parser.add_argument('--smart', action='store_true', help='使用智能自动化引擎')

    args = parser.parse_args()

    if args.mode == 'single':
        if args.smart:
            logger.info("🤖 使用智能引擎进行单次注册")
            startMainSmart(1, 0, args.x, args.y)
        else:
            logger.info("🔧 使用传统方法进行单次注册")
            startMain(args.x, args.y)
    else:
        if args.smart:
            logger.info(f"🤖 使用智能引擎进行批量注册: {args.count}个账号")
            startMainSmart(args.count, args.interval, args.x, args.y)
        else:
            logger.info("❌ 传统方法不支持批量注册，请使用 --smart 参数")
            print("提示: 使用 --smart 参数启用智能批量注册功能")
            print("示例: python main.py --mode batch --count 5 --interval 60 --smart")
