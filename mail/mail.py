from email.header import decode_header
import time, os, re, email, imaplib
from bs4 import BeautifulSoup

from utils.config import config

# 获取当前文件的路径
current_path = os.path.abspath(__file__)

# 获取当前文件所在目录的父目录，即为项目根目录
project_root = os.path.dirname(os.path.dirname(current_path))

# 配置参数
lunxun = config["lunxun"]
claude_title_key = config["claude_title_key"]
magic_link_prefix = config["magic_link_prefix"]
mail_address = config["mail"]["mail_address"]
mail_timeout = config["mail"]["mail_timeout"]
imap_server = config["mail"]["imap_server"]


def connect_to_imap(password):
    """连接到IMAP服务器并返回连接对象"""
    try:
        print(f"连接到IMAP服务器: {imap_server}")
        conn = imaplib.IMAP4_SSL(imap_server)
        conn.login(mail_address, password)

        # 强制重新选择收件箱，确保获取最新邮件列表
        conn.select("INBOX", readonly=False)

        return conn, None
    except Exception as e:
        error_msg = f"连接IMAP服务器失败: {str(e)}"
        print(error_msg)
        return None, error_msg


def close_connection(conn):
    """安全关闭IMAP连接"""
    if conn:
        try:
            conn.close()
            conn.logout()
        except:
            pass


def extract_magic_link(msg):
    """从邮件中提取Claude.ai的magic link"""
    magic_link = None

    # 遍历邮件的所有部分
    for part in msg.walk():
        # 如果部分是HTML
        if part.get_content_type() == "text/html":
            # 获取HTML内容
            html_content = part.get_payload(decode=True)
            if not html_content:
                continue

            # 解码HTML内容
            charset = part.get_content_charset() or "utf-8"
            if isinstance(html_content, bytes):
                html_content = html_content.decode(charset, errors="replace")

            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(html_content, "html.parser")

            # 查找所有a标签
            for a_tag in soup.find_all("a"):
                href = a_tag.get("href")
                # 检查href是否包含magic link前缀
                if href and magic_link_prefix in href:
                    return href

    return None


def process_email(msg, userName):
    """处理单封邮件，检查是否包含Claude.ai的magic link"""
    subject = msg.get("Subject")
    to_field = msg.get("To", "")

    print(f"检查邮件，收件人字段: {to_field}")

    # 更灵活地检查收件人，考虑可能的格式: "Name <email>" 或 "email"
    # 将 userName 转为小写进行不区分大小写的比较
    userName_lower = userName.lower()

    # 收件人可能有多个，用逗号分隔
    recipients = to_field.split(",")
    recipient_match = False

    for recipient in recipients:
        recipient = recipient.strip()
        # 检查是否为 "Name <email>" 格式
        email_match = re.search(r"<([^>]+)>", recipient)
        if email_match:
            email = email_match.group(1).lower()
            if email == userName_lower:
                recipient_match = True
                break
        # 直接比较邮件地址
        elif recipient.lower() == userName_lower:
            recipient_match = True
            break

    if not recipient_match:
        print(f"收件人不匹配，期望: {userName}")
        return None, False

    # 解码邮件标题
    decoded_subject = decode_header(subject)[0][0] if subject else ""
    if isinstance(decoded_subject, bytes):
        decoded_subject = decoded_subject.decode("utf-8", errors="replace")

    # 检查标题是否包含关键字
    if not decoded_subject or claude_title_key not in decoded_subject:
        print(f"邮件标题不符合关键字要求: {decoded_subject}")
        return None, True

    # 提取magic link
    magic_link = extract_magic_link(msg)
    if magic_link:
        return magic_link, True
    else:
        print("邮件中没有找到Claude.ai的magic link")
        return None, True


def get_user_to(userName, password):
    """获取Claude.ai的magic link，使用迭代方式实现轮询"""
    attempt_count = 0

    while attempt_count < int(lunxun):
        # 每次轮询都重新连接IMAP服务器以获取最新状态
        conn, error = connect_to_imap(password)
        if error:
            attempt_count += 1
            time.sleep(2)
            continue

        try:
            # 检查INBOX状态，获取邮件数量
            status, counts = conn.status("INBOX", "(MESSAGES)")
            if status != "OK":
                print("获取邮箱状态失败")
                close_connection(conn)
                time.sleep(1)
                continue

            # 尝试发送检查命令，获取最新邮件状态
            conn.check()

            # 简单获取所有邮件
            typ, msgnums = conn.search(None, "ALL")

            if not msgnums[0].strip():
                print("邮箱中没有邮件")
                close_connection(conn)
                time.sleep(1)
                continue

            msgnums = msgnums[0].split()
            # 获取最近20封邮件以提高找到新邮件的概率
            latest_msgnums = msgnums[-20:] if len(msgnums) > 20 else msgnums

            print(f"找到{len(msgnums)}封邮件，正在检查最新的{len(latest_msgnums)}封")
            found_matching_recipient = False

            # 从最新到最旧检查邮件
            for msgnum in reversed(latest_msgnums):
                # 获取邮件内容
                typ, data = conn.fetch(msgnum, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])

                # 处理邮件
                magic_link, recipient_matched = process_email(msg, userName)

                if recipient_matched:
                    found_matching_recipient = True

                # 如果找到magic link，立即返回
                if magic_link:
                    close_connection(conn)
                    return {"type": "True", "link": magic_link}

            # 输出搜索结果
            if found_matching_recipient:
                print(f"找到收件人为{userName}的邮件，但没有找到包含关键字的邮件")
            else:
                print(f"没有找到收件人为{userName}的邮件")

        except Exception as e:
            print(f"处理邮件时出错: {str(e)}")
        finally:
            close_connection(conn)

        # 增加尝试次数并等待
        attempt_count += 1
        if attempt_count >= int(lunxun):
            return {"type": "error", "msg": "已到轮询阈值,停止获取"}

        print(f"等待 {mail_timeout} 秒后进行下一次轮询 ({attempt_count}/{lunxun})")
        time.sleep(mail_timeout)

    return {"type": "error", "msg": "已到轮询阈值,停止获取"}


if __name__ == "__main__":
    result = get_user_to("xxxx", config["mail"]["mail_password"])
    print(result)
