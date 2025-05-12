import platform
import subprocess
import shutil
import os
import requests
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Set up logging to a file
log_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.log')
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(message)s')


def ensure_speedtest_installed():
    os_type = platform.system()
    print(f"Detected OS: {os_type}")

    if os_type != "Linux":
        print("This script supports only Linux systems.")
        return False

    # Check if speedtest is already installed
    if shutil.which("speedtest") is not None:
        print("speedtest is already installed.")
        return True

    print("speedtest not found. Attempting installation...")

    try:
        # Determine Linux distribution
        if os.path.exists("/etc/debian_version"):
            # Install Ookla's speedtest on Debian/Ubuntu
            subprocess.check_call("curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash", shell=True)
            subprocess.check_call(["sudo", "apt-get", "install", "-y", "speedtest"])
        elif os.path.exists("/etc/redhat-release") or os.path.exists("/etc/centos-release"):
            # Install Ookla's speedtest on RHEL/CentOS
            subprocess.check_call("curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.rpm.sh | sudo bash", shell=True)
            subprocess.check_call(["sudo", "yum", "install", "-y", "speedtest"])
        else:
            print("Unsupported Linux distribution.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Installation failed: {e}")
        return False

    print("speedtest successfully installed.")
    return True

def run_speedtest() -> str:
    """
    Run speedtest CLI in JSON mode and return a formatted string with key metrics.
    """
    try:
        # Run speedtest
        result = subprocess.run(
            ["speedtest", "--accept-license", "--accept-gdpr", "--format=json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)

        # Get system info
        hostname = os.getenv("HOST_NAME")

        try:
            ipv4 = requests.get("https://ifconfig.me/ip", timeout=5).text.strip()
        except requests.RequestException:
            ipv4 = "Unavailable"

        try:
            uptime_result = subprocess.run(
                ["uptime", "-p"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True
            )
            uptime = uptime_result.stdout.strip()
        except Exception:
            uptime = "Unavailable"

        # Extract speedtest data
        server = data['server']['name']
        country = data['server']['country']
        latency = round(data['ping']['latency'], 2)
        download = round(data['download']['bandwidth'] * 8 / 1_000_000, 2)  # Mbps
        upload = round(data['upload']['bandwidth'] * 8 / 1_000_000, 2)      # Mbps
        packet_loss = data.get('packetLoss', 0)
        result_url = data['result']['url']

        # Create log line for results
        log_line = f"{datetime.now()} Upload: {upload:.2f} Download: {download:.2f} Packet Loss %: {packet_loss} Latency: {latency}"
        
        # Log the results in a single line
        logging.info(log_line)

        # Format message
        message = (
            f"📶 <b>Speedtest Results</b>\n"
            f"💻 Hostname: <code>{hostname}</code>\n"
            f"🌐 IPv4: <code>{ipv4}</code>\n"
            f"🕒 Uptime: <code>{uptime}</code>\n"
            f"🌍 Server: <code>{server}, {country}</code>\n"
            f"⏱ Latency: <b>{latency} ms</b>\n"
            f"⬇️ Download: <b>{download} Mbps</b>\n"
            f"⬆️ Upload: <b>{upload} Mbps</b>\n"
            f"📉 Packet Loss: <b>{packet_loss}%</b>\n"
            f"🔗 <a href=\"{result_url}\">Result URL</a>"
        )

        return message

    except subprocess.CalledProcessError as e:
        return f"❌ Speedtest failed:\n<pre>{e.stderr}</pre>"
    except (json.JSONDecodeError, KeyError) as e:
        return f"❌ Failed to parse speedtest results:\n<pre>{str(e)}</pre>"
    except FileNotFoundError:
        return "❌ speedtest command not found. Is it installed?"

class TelegramBot:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{self.token}/"

    def check_bot(self) -> bool:
        """
        Check if the bot token is valid and reachable.
        """
        try:
            response = requests.get(self.api_url + "getMe")
            data = response.json()
            if response.status_code == 200 and data.get("ok"):
                print(f"Bot is active: {data['result']['username']}")
                return True
            else:
                print("Bot check failed:", data)
                return False
        except Exception as e:
            print(f"Error while checking bot: {e}")
            return False

    def send_message(self, text: str) -> bool:
        """
        Send a text message to the configured chat.
        """
        try:
            response = requests.post(
                self.api_url + "sendMessage",
                data={
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": "HTML"
                }
            )
            data = response.json()
            if response.status_code == 200 and data.get("ok"):
                print("Message sent successfully.")
                return True
            else:
                print("Failed to send message:", data)
                return False
        except Exception as e:
            print(f"Error while sending message: {e}")
            return False

bot = TelegramBot(
    token="1265847273:AAHju0MShUdlNqILUD55mXPjml0l2A5yGLc",
    chat_id="-1002402706243"
)

# Main function
def launch():
    # Ensure speedtest is installed
    ensure_speedtest_installed()

    # Get token and chat_id from environment variables
    bot_token = os.getenv("BOT_TOKEN")
    bot_chat_id = os.getenv("BOT_CHAT_ID")

    if not bot_token or not bot_chat_id:
        print("Error: BOT_TOKEN and BOT_CHAT_ID environment variables are not set.")
        return

    # Instantiate bot with token and chat ID
    bot = TelegramBot(
        token=bot_token,
        chat_id=bot_chat_id
    )

    # Check if bot is available
    if bot.check_bot():
        # Run speedtest and send results
        results = run_speedtest()
        bot.send_message(results)

# Run main function
if __name__ == "__main__":
    launch()