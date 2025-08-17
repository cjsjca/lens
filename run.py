#!/usr/bin/env python3
"""
Cage Code-Runner CLI Entrypoint (Room)
Main launcher that coordinates all cage components.
"""

import sys
import argparse
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from cagecore import room, referee, logbook, workbench, rulebook, voice, planner, executor, tests, rehydrator


def main():
    parser = argparse.ArgumentParser(description="Cage Code-Runner")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # init command
    subparsers.add_parser('init', help='Initialize the cage environment')

    # plan command
    plan_parser = subparsers.add_parser('plan', help='Create a plan')
    plan_parser.add_argument('title', help='Plan title')
    plan_parser.add_argument('--file', required=True, help='Target file in workspace')
    plan_parser.add_argument('--replace', required=True, help='Text to replace')
    plan_parser.add_argument('--with', dest='replacement', required=True, help='Replacement text')

    # show-plan command
    subparsers.add_parser('show-plan', help='Show the latest plan')

    # apply command
    subparsers.add_parser('apply', help='Apply the latest plan')

    # publish command
    publish_parser = subparsers.add_parser('publish', help='Publish a file to artifacts')
    publish_parser.add_argument('--file', required=True, help='File to publish')

    # show-log command
    subparsers.add_parser('show-log', help='Show recent log entries')

    # add-correction command
    correction_parser = subparsers.add_parser('add-correction', help='Add a correction rule')
    correction_parser.add_argument('--from', dest='from_text', required=True, help='Text to correct from')
    correction_parser.add_argument('--to', required=True, help='Text to correct to')
    correction_parser.add_argument('--note', help='Optional note about the correction')

    args = parser.parse_args()

    try:
        if args.command == 'init':
            cmd_init()
        elif args.command == 'plan':
            cmd_plan(args.title, args.file, args.replace, args.replacement)
        elif args.command == 'show-plan':
            cmd_show_plan()
        elif args.command == 'apply':
            cmd_apply()
        elif args.command == 'publish':
            cmd_publish(args.file)
        elif args.command == 'show-log':
            cmd_show_log()
        elif args.command == 'add-correction':
            cmd_add_correction(args.from_text, args.to, args.note)
        else:
            parser.print_help()
    except referee.RuleViolationError:
        print("Not allowed. Diff-only and append-only per the rules.")
        sys.exit(1)


def cmd_init():
    """Initialize the cage environment"""
    # Create directories
    room.ensure_directories()

    # Touch log file first
    logbook.ensure_exists()

    # Create rulebook if missing
    if not rulebook.exists():
        rulebook.create_default()

    # Create sample file
    sample_path = workbench.get_workspace_path("sample.txt")
    if not sample_path.exists():
        workbench.write_file("sample.txt", "Hello, welcome to the cage!")

    # Log the initialization
    logbook.append("room_ready", {"action": "initialized", "files_created": ["workspace/sample.txt", "rulebook.json", "trail.log"]})

    print(voice.maxim_threadline("Cage initialized successfully.",
                                "The room is ready with workspace, rulebook, and logging in place."))


def cmd_plan(title, filename, find_text, replace_text):
    """Create a plan"""
    # Rehydrate before planning
    rehydrator.rehydrate()

    plan_data = planner.create_plan(title, filename, find_text, replace_text)
    logbook.append("plan", plan_data)

    print(voice.maxim_threadline(f"Plan '{title}' recorded.",
                                f"Will replace '{find_text}' with '{replace_text}' in {filename}."))


def cmd_show_plan():
    """Show the latest plan"""
    plan = planner.get_latest_plan()
    if plan:
        print(voice.format_json(plan))
    else:
        print(voice.maxim_threadline("No plan found.", "Create a plan first with the 'plan' command."))


def cmd_apply():
    """Apply the latest plan"""
    # Referee checks
    referee.enforce_plan_then_act()
    referee.enforce_rehydrate_before_act()

    # Rehydrate
    rehydrator.rehydrate()

    # Execute
    result = executor.apply_latest_plan()

    if result['success']:
        print(voice.maxim_threadline("Applied safely.", "Changes have been made and tests passed."))
    else:
        print(voice.maxim_threadline("Apply failed.", result.get('error', 'Unknown error occurred.')))


def cmd_publish(filename):
    """Publish a file to artifacts"""
    if not tests.last_tests_passed():
        print(voice.maxim_threadline("Publish refused.", "Tests must pass before publishing."))
        return

    # Copy file to artifacts
    source = workbench.get_workspace_path(filename)
    if not source.exists():
        print(voice.maxim_threadline("File not found.", f"{filename} does not exist in workspace."))
        return

    artifacts_dir = room.get_artifacts_dir()
    artifacts_dir.mkdir(exist_ok=True)

    dest = artifacts_dir / filename
    dest.write_text(source.read_text())

    logbook.append("publish", {"file": filename, "from": str(source), "to": str(dest)})

    print(voice.maxim_threadline("Published successfully.", f"{filename} moved to artifacts directory."))


def cmd_show_log():
    """Show recent log entries"""
    entries = logbook.get_recent_entries(50)
    for entry in entries:
        print(voice.format_json(entry))


def cmd_add_correction(from_text, to_text, note=None):
    """Add a correction to the rulebook"""
    correction = rulebook.add_correction(from_text, to_text, note)
    logbook.append("correction_added", correction)

    print(voice.maxim_threadline("Correction added.", f"'{from_text}' → '{to_text}' recorded in rulebook."))


if __name__ == "__main__":
    main()