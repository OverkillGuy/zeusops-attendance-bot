"""Command line entrypoint for zeusops-attendance-bot"""
import argparse
import os
import sys
from typing import Optional

from zeusops_attendance_bot.api import Secret, get_from_api


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    """Parse generic arguments, given as parameters"""
    parser = argparse.ArgumentParser(
        "zeusops-attendance-bot",
        description="Parse Zeusops #attendance channel in Discord",
        epilog="API token requires either --token-file flag or envvar DISCORD_API_TOKEN",
    )
    parser.add_argument(
        "--token-file", help="File containing API Token", type=argparse.FileType("r")
    )
    return parser.parse_args(arguments)


def cli(arguments: Optional[list[str]] = None):
    """Run the zeusops_attendance_bot cli"""
    if arguments is None:
        arguments = sys.argv[1:]
    args = parse_arguments(arguments)
    if args.token_file:
        token = args.token_file.read().strip()
    else:
        token = os.getenv("DISCORD_API_TOKEN")
    if token is None:
        print(
            "Missing API token: --token-file or set DISCORD_API_TOKEN envvar",
            file=sys.stderr,
        )
        exit(2)  # Simulate the argparse behaviour of exiting on bad args
    main(token)


def main(token: Secret):
    """Run the program's main command"""
    api_response: dict = get_from_api(token)
    print(api_response)
