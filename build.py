#!/usr/bin/env python3
"""
Build script for the poetry blog
Syncs from Obsidian and builds the Zola site
"""

import subprocess
import sys
from pathlib import Path
import argparse


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"{description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        if e.stderr:
            print("Error output:", e.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Build the poetry blog")
    parser.add_argument("--vault", help="Path to Obsidian vault")
    parser.add_argument("--serve", action="store_true", help="Start development server after build")
    parser.add_argument("--watch-sync", action="store_true", help="Watch Obsidian folder for changes")
    
    args = parser.parse_args()
    
    # Sync from Obsidian
    sync_cmd = "uv run sync_obsidian.py"
    if args.vault:
        sync_cmd += f" --vault '{args.vault}'"
    
    if not run_command(sync_cmd, "Syncing from Obsidian"):
        return 1
    
    # Build the site
    if not run_command("zola build", "Building Zola site"):
        return 1
    
    print("\n🎉 Build completed successfully!")
    print(f"Site built in: {Path('./public').absolute()}")
    
    # Start development server if requested
    if args.serve:
        print("\nStarting development server...")
        try:
            subprocess.run("zola serve", shell=True)
        except KeyboardInterrupt:
            print("\nDevelopment server stopped.")
    
    # Watch sync if requested
    if args.watch_sync:
        print("\nStarting watch sync...")
        watch_cmd = "uv run sync_obsidian.py --watch"
        if args.vault:
            watch_cmd += f" --vault '{args.vault}'"
        try:
            subprocess.run(watch_cmd, shell=True)
        except KeyboardInterrupt:
            print("\nWatch sync stopped.")
    
    return 0


if __name__ == "__main__":
    exit(main())