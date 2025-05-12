import os
import subprocess
import sys

def check_root_privileges():
    """
    Ensure the script is running as root or with sudo.
    """
    if os.geteuid() != 0:
        print("Error: This script must be run as root or with sudo.")
        sys.exit(1)

def prompt_user_input():
    """
    Prompts the user for their Telegram Bot token and chat ID.
    """
    bot_token = input("Enter your Telegram Bot Token: ")
    bot_chat_id = input("Enter your Telegram Bot Chat ID: ")

    return bot_token, bot_chat_id

def get_shell_config_file():
    """
    Determines the user's shell and returns the appropriate configuration file path.
    """
    shell = os.getenv("SHELL", "")
    
    if "bash" in shell:
        return os.path.expanduser("~/.bashrc")
    elif "zsh" in shell:
        return os.path.expanduser("~/.zshrc")
    else:
        print(f"Unsupported shell detected: {shell}. Using .bashrc as default.")
        return os.path.expanduser("~/.bashrc")

def update_shell_config(bot_token, bot_chat_id):
    """
    Adds the provided BOT_TOKEN and BOT_CHAT_ID to the appropriate shell configuration file.
    """
    shell_config_file = get_shell_config_file()
    
    # Check if the environment variables already exist, and if so, replace them
    with open(shell_config_file, "a") as config_file:
        # Add environment variables to the end of the file
        config_file.write(f"\n# Telegram bot environment variables\n")
        config_file.write(f"export BOT_TOKEN={bot_token}\n")
        config_file.write(f"export BOT_CHAT_ID={bot_chat_id}\n")

    print(f"\nThe following environment variables have been added to {shell_config_file}:\n")
    print(f"export BOT_TOKEN={bot_token}")
    print(f"export BOT_CHAT_ID={bot_chat_id}")

def create_cron_job():
    """
    Prompts the user for the cron job frequency and creates a cron task for the root user.
    """
    # Prompt for frequency options
    print("\nPlease choose the frequency for the cron job:")
    print("1. Every 10 minutes")
    print("2. Every 30 minutes")
    print("3. Every 1 hour")
    print("4. Every 12 hours")
    print("5. Every 24 hours")

    choice = input("\nEnter the number corresponding to your choice: ")

    cron_schedule = None

    if choice == "1":
        cron_schedule = "*/10 * * * *"
    elif choice == "2":
        cron_schedule = "*/30 * * * *"
    elif choice == "3":
        cron_schedule = "0 * * * *"
    elif choice == "4":
        cron_schedule = "0 */12 * * *"
    elif choice == "5":
        cron_schedule = "0 0 * * *"
    else:
        print("Invalid choice. Cron job will not be created.")
        return

    # Get the absolute path of the current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "speedtest_telegram_bot.py")

    # Create the cron job
    cron_command = f"python3 {script_path}"

    # Write the cron job to root's crontab
    try:
        crontab_entry = f"{cron_schedule} root {cron_command}\n"
        # Write cron job to root's crontab file
        with open("/etc/crontab", "a") as crontab_file:
            crontab_file.write(crontab_entry)
        print(f"\nCron job created with schedule: {cron_schedule}")
    except PermissionError:
        print("Permission denied. You need to run this script as root to create a cron job.")

def main():
    # Ensure the script is run as root
    check_root_privileges()
    
    print("Welcome to the Telegram Bot installation script.")
    
    # Prompt user to input BOT_TOKEN and BOT_CHAT_ID
    bot_token, bot_chat_id = prompt_user_input()

    # Update the shell config file with the environment variables
    update_shell_config(bot_token, bot_chat_id)

    print("\nEnvironment variables have been set.")
    print("To apply the changes immediately, run the following command in your terminal:")
    print("source ~/.bashrc or source ~/.zshrc\n")
    print("Alternatively, restart your terminal or shell session.")
    
    # Ask to create cron job
    create_cron_job()

if __name__ == "__main__":
    main()
