#!/usr/bin/env python3
"""
Cage Code-Runner CLI Entrypoint (Room)
Main launcher that coordinates all cage components.
"""

import sys
import argparse
import json
import uuid
import math
from datetime import datetime
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from cagecore import room, referee, workbench, rulebook, logbook, voice, rehydrator, planner, executor, tests, embedder


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

    # Add-correction subcommand
    add_correction_parser = subparsers.add_parser("add-correction", help="Add a correction rule")
    add_correction_parser.add_argument("--from", dest="from_text", required=True, help="Text to replace")
    add_correction_parser.add_argument("--to", dest="to_text", required=True, help="Replacement text")
    add_correction_parser.add_argument("--note", help="Optional note about the correction")

    # Ingest subcommand
    ingest_parser = subparsers.add_parser("ingest", help="Ingest a new atom")
    ingest_parser.add_argument("--author", required=True, help="Author name")
    ingest_parser.add_argument("--role", required=True, choices=["student", "teacher", "teacher_note", "system"], help="Role")
    ingest_parser.add_argument("--text", required=True, help="Text content")
    ingest_parser.add_argument("--topic", help="Optional topic")

    # Retrieve subcommand
    retrieve_parser = subparsers.add_parser("retrieve", help="Retrieve atoms by similarity")
    retrieve_parser.add_argument("--query", required=True, help="Query text")
    retrieve_parser.add_argument("--k", type=int, default=5, help="Number of results")

    args = parser.parse_args()

    try:
        if args.command == 'init':
            cmd_init()
        elif args.command == 'plan':
            # Rehydrate before planning
            rehydrator.rehydrate()
            cmd_plan(args.title, args.file, args.replace, args.replacement)
        elif args.command == 'show-plan':
            cmd_show_plan()
        elif args.command == 'apply':
            # Rehydrate before applying
            rehydrator.rehydrate()
            cmd_apply()
        elif args.command == 'publish':
            # Rehydrate before publishing
            rehydrator.rehydrate()
            cmd_publish(args.file)
        elif args.command == 'show-log':
            cmd_show_log()
        elif args.command == 'add-correction':
            cmd_add_correction(args.from_text, args.to_text, args.note)
        elif args.command == "ingest":
            cmd_ingest(args.author, args.role, args.text, args.topic)
        elif args.command == "retrieve":
            cmd_retrieve(args.query, args.k)
        else:
            parser.print_help()
    except referee.RuleViolationError:
        print("Not allowed. Diff-only and append-only per the rules.")
        sys.exit(1)


def cmd_init():
    """Initialize the cage environment"""
    room.ensure_dirs()
    with referee.allow_bootstrap():
        workbench.bootstrap_write("sample.txt", "Hello, welcome to the cage!")
        rulebook.init_if_missing()
        logbook.ensure_exists()
    logbook.append("room_ready", {"workspace": str(room.workspace_path())})
    print(voice.maxim("Room ready."))
    print(voice.threadline("Workspace, rulebook, and logbook are set."))


def cmd_plan(title, filename, find_text, replace_text):
    """Create a plan"""
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


def cmd_ingest(author, role, text, topic=None):
    """Ingest a new atom"""
    atom_id = uuid.uuid4().hex
    ts = datetime.utcnow().isoformat() + "Z"
    embedding = embedder.vector(text)

    atom = {
        "id": atom_id,
        "ts": ts,
        "author": author,
        "role": role,
        "text": text,
        "embedding": embedding
    }

    if topic:
        atom["topic"] = topic

    # Append to atoms.jsonl
    with open("atoms.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(atom) + "\n")

    # Append to trail.log
    text_preview = text[:60] + "..." if len(text) > 60 else text
    topic_str = f" {topic}" if topic else ""
    trail_entry = f"ingest {atom_id}{topic_str} {text_preview}"
    with open("trail.log", "a", encoding="utf-8") as f:
        f.write(trail_entry + "\n")

    print(atom_id)


def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors"""
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0
    return dot_product / (norm_a * norm_b)


def cmd_retrieve(query, k=5):
    """Retrieve atoms by similarity to query"""
    try:
        with open("atoms.jsonl", "r", encoding="utf-8") as f:
            atoms = [json.loads(line.strip()) for line in f if line.strip()]
    except FileNotFoundError:
        print("No atoms found. Run 'ingest' first.")
        return

    if not atoms:
        print("No atoms found. Run 'ingest' first.")
        return

    query_embedding = embedder.vector(query)

    # Calculate similarities
    results = []
    for atom in atoms:
        similarity = cosine_similarity(query_embedding, atom["embedding"])
        results.append((atom, similarity))

    # Sort by similarity (descending)
    results.sort(key=lambda x: x[1], reverse=True)

    # Print top-k
    for atom, score in results[:k]:
        text_preview = atom["text"][:60] + "..." if len(atom["text"]) > 60 else atom["text"]
        print(f"{atom['id']} | {score:.3f} | {atom['ts']} | {text_preview}")


if __name__ == "__main__":
    main()