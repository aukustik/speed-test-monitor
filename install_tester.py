import os
import subprocess
import sys

env_file = '.env'
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, env_file)

def check_root_privileges():
    """
    Ensure the script is running as root or with sudo.
    """
    if os.geteuid() != 0:
        print("Error: This script must be run as root or with sudo.")
        sys.exit(1)

def create_or_update_env_file():
    """Create or update the .env file with bot credentials."""

    # Request BOT_TOKEN and BOT_CHAT_ID from the user
    bot_token = input("Please enter your Telegram Bot Token: ")
    chat_id = input("Please enter your Telegram Chat ID: ")
    host_name = input("Please enter your Host Name: ")

    # Create or update the .env file
    with open(env_file, 'w') as f:
        f.write(f"BOT_TOKEN={bot_token}\n")
        f.write(f"BOT_CHAT_ID={chat_id}\n")
        f.write(f"HOST_NAME={chat_id}\n")
    
    print(".env file has been created and saved successfully.")

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
        config_file.write(f"export HOST_NAME={bot_chat_id}\n")

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

def remove_cron_job():
    """
    Removes the existing cron job for speedtest_telegram_bot.py.
    """
    # Get the absolute path of the current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "speedtest_telegram_bot.py")

    # Check if there's a cron job for the speedtest_telegram_bot.py script
    try:
        # Read the current crontab
        with open("/etc/crontab", "r") as crontab_file:
            lines = crontab_file.readlines()

        # Find and remove the cron job line for the speedtest_telegram_bot.py
        with open("/etc/crontab", "w") as crontab_file:
            for line in lines:
                if script_path not in line:
                    crontab_file.write(line)
                else:
                    print(f"Cron job for {script_path} removed.")
    except PermissionError:
        print("Permission denied. You need to run this script as root to modify crontab.")

def main():
    # Ensure the script is run as root
    check_root_privileges()
    
    # Present options to the user
    print("Welcome to Speedtest Telegram Bot installation script.")
    print("1. Install the script and create a cron job")
    print("2. Remove existing cron job")

    action = input("Please choose an action (1 or 2): ")

    if action == "1":

        # Update the shell config file with the environment variables
        if not os.path.exists(env_path):
          create_or_update_env_file()

        print("\nEnvironment variables have been set.")
        print("To apply the changes immediately, run the following command in your terminal:")
        print("source ~/.bashrc or source ~/.zshrc\n")
        print("Alternatively, restart your terminal or shell session.")
        
        # Ask to create cron job
        create_cron_job()

    elif action == "2":
        # Remove cron job if it exists
        remove_cron_job()

    else:
        print("Invalid choice. Exiting script.")
        sys.exit(1)

if __name__ == "__main__":
    main()
