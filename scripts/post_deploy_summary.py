#!/usr/bin/env python3
"""Post a short deploy summary to #deploys after a successful rollout.

Called from the deploy workflow:

    python scripts/post_deploy_summary.py --env staging --sha "$GITHUB_SHA"

The Slack bot token comes from the SLACK_BOT_TOKEN environment variable
(GitHub Actions secret / Secrets Manager). Never hardcode it here.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request

SLACK_API = "https://slack.com/api/chat.postMessage"
DEFAULT_CHANNEL = "#deploys"


def recent_commits(sha: str, count: int = 5) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "log", "--oneline", f"-{count}", sha],
            check=True, capture_output=True, text=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [line for line in out.splitlines() if line.strip()]


def build_message(env: str, sha: str, actor: str, commits: list[str]) -> dict:
    lines = "\n".join(f"• `{c}`" for c in commits) or "_no commit info_"
    return {
        "text": f"Deployed {sha[:8]} to {env}",
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn",
             "text": f":ship: *{env}* deployed `{sha[:8]}` by {actor}"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": lines}},
        ],
    }


def post(message: dict, channel: str) -> None:
    bot_token = os.environ.get("SLACK_BOT_TOKEN")
    if not bot_token:
        print("SLACK_BOT_TOKEN not set; skipping Slack notification", file=sys.stderr)
        return
    payload = dict(message, channel=channel)
    req = urllib.request.Request(
        SLACK_API,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {bot_token}",
        },
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = json.load(resp)
    if not body.get("ok"):
        print(f"slack error: {body.get('error')}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", required=True, choices=["staging", "prod"])
    parser.add_argument("--sha", default=os.environ.get("GITHUB_SHA", "HEAD"))
    parser.add_argument("--actor", default=os.environ.get("GITHUB_ACTOR", "unknown"))
    parser.add_argument("--channel", default=DEFAULT_CHANNEL)
    args = parser.parse_args()

    post(build_message(args.env, args.sha, args.actor, recent_commits(args.sha)), args.channel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
