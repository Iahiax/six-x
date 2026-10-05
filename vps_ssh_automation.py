import time
import paramiko
import logging
from config import config

logger = logging.getLogger("SSHAutomation")

class SegfaultSSHManager:
    """إدارة الاتصال المباشر بـ Segfault VPS مع ميزة تأخير الـ 63 ثانية الآمنة"""
    def __init__(self):
        self.hostname = config.SSH_HOSTNAME
        self.port = config.SSH_PORT
        self.username = config.SSH_USERNAME
        self.key_path = config.SSH_KEY_PATH

    def execute_remote_command(self, command: str, safe_delay: int = 63) -> str:
        """تنفيذ أمر بعيد عبر SSH بعد تطبيق تأخير الأمان المخصص"""
        logger.info(f"[SSH Segfault]: تطبيق انتشال الأمان بمهلة {safe_delay} ثانية...")
        time.sleep(safe_delay)

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                key_filename=self.key_path,
                timeout=10
            )
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            ssh.close()

            if error and not output:
                logger.error(f"[SSH Error]: {error}")
                return f"Error: {error}"
            return output
        except Exception as e:
            logger.error(f"[SSH Connection Failed]: {e}")
            return f"Exception: {str(e)}"
