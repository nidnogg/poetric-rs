#!/usr/bin/env python3
"""
Obsidian Vault Publisher for Zola
Syncs markdown files from an Obsidian vault's 'publish' folder to Zola content directory.
"""

import os
import shutil
import time
from pathlib import Path
from datetime import datetime
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def find_obsidian_vault(start_path=None):
    """Find the Obsidian vault by looking for .obsidian folder."""
    if start_path:
        search_path = Path(start_path)
    else:
        search_path = Path.home()
    
    # Search for .obsidian folder
    for root in [search_path] + list(search_path.parents):
        obsidian_folder = root / ".obsidian"
        if obsidian_folder.exists():
            return root
    
    # Also check common locations
    common_locations = [
        Path.home() / "Documents",
        Path.home() / "Desktop",
        Path.home() / "vault",
        Path.home() / "Obsidian",
    ]
    
    for location in common_locations:
        if location.exists():
            for item in location.iterdir():
                if item.is_dir() and (item / ".obsidian").exists():
                    return item
    
    return None


def convert_obsidian_to_zola(content, title=None):
    """Convert Obsidian markdown to Zola format."""
    lines = content.split('\n')
    
    # Check if it already has frontmatter
    if lines[0].strip() == '+++':
        return content
    
    # Extract title from first h1 if not provided
    if not title:
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
    
    if not title:
        title = "Untitled Poem"
    
    # Create frontmatter
    frontmatter = f"""+++
title = "{title}"
date = {datetime.now().strftime('%Y-%m-%d')}
+++

"""
    
    # Remove the first h1 if it exists (since it becomes the title)
    if lines and lines[0].startswith('# '):
        lines = lines[1:]
        # Remove empty line after title if it exists
        if lines and lines[0].strip() == '':
            lines = lines[1:]
    
    return frontmatter + '\n'.join(lines)


def sync_publish_folder(vault_path, zola_content_path):
    """Sync files from Obsidian publish folder to Zola content."""
    publish_folder = vault_path / "publish"
    
    if not publish_folder.exists():
        print(f"Creating publish folder at: {publish_folder}")
        publish_folder.mkdir(exist_ok=True)
        return
    
    print(f"Syncing from: {publish_folder}")
    print(f"Syncing to: {zola_content_path}")
    
    synced_files = 0
    
    for md_file in publish_folder.glob("**/*.md"):
        if md_file.is_file():
            # Read the original file
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Convert to Zola format
                title = md_file.stem.replace('-', ' ').replace('_', ' ').title()
                zola_content = convert_obsidian_to_zola(content, title)
                
                # Create target file path
                target_file = zola_content_path / md_file.name
                
                # Write to Zola content directory
                with open(target_file, 'w', encoding='utf-8') as f:
                    f.write(zola_content)
                
                print(f"✓ Synced: {md_file.name}")
                synced_files += 1
                
            except Exception as e:
                print(f"✗ Error syncing {md_file.name}: {e}")
    
    print(f"\nSynced {synced_files} files.")


class SyncHandler(FileSystemEventHandler):
    """Handler for file system events in the publish folder."""
    
    def __init__(self, vault_path, zola_content_path):
        self.vault_path = vault_path
        self.zola_content_path = zola_content_path
        self.last_sync = {}
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            self._sync_if_needed()
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            self._sync_if_needed()
    
    def on_deleted(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            self._sync_if_needed()
    
    def _sync_if_needed(self):
        """Sync if enough time has passed since last sync."""
        now = time.time()
        if 'last_sync_time' not in self.last_sync or now - self.last_sync['last_sync_time'] > 1:
            print(f"Changes detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            sync_publish_folder(self.vault_path, self.zola_content_path)
            self.last_sync['last_sync_time'] = now
            print()


def watch_and_sync(vault_path, zola_content_path, interval=5):
    """Watch the publish folder and sync changes using watchdog."""
    publish_folder = vault_path / "publish"
    
    if not publish_folder.exists():
        print(f"Creating publish folder at: {publish_folder}")
        publish_folder.mkdir(exist_ok=True)
    
    print(f"Watching {publish_folder} for changes...")
    print("Press Ctrl+C to stop watching\n")
    
    event_handler = SyncHandler(vault_path, zola_content_path)
    observer = Observer()
    observer.schedule(event_handler, str(publish_folder), recursive=True)
    
    try:
        observer.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopped watching.")
    
    observer.join()


def main():
    parser = argparse.ArgumentParser(description="Sync Obsidian publish folder to Zola")
    parser.add_argument("--vault", help="Path to Obsidian vault")
    parser.add_argument("--content", help="Path to Zola content directory", 
                       default="./content")
    parser.add_argument("--watch", action="store_true", 
                       help="Watch for changes and sync automatically")
    parser.add_argument("--interval", type=int, default=5,
                       help="Watch interval in seconds (default: 5)")
    
    args = parser.parse_args()
    
    # Find vault
    if args.vault:
        vault_path = Path(args.vault)
        if not vault_path.exists():
            print(f"Error: Vault path {vault_path} does not exist")
            return 1
    else:
        vault_path = find_obsidian_vault()
        if not vault_path:
            print("Error: Could not find Obsidian vault")
            print("Please specify vault path with --vault")
            return 1
    
    print(f"Found Obsidian vault at: {vault_path}")
    
    # Setup content directory
    zola_content_path = Path(args.content)
    zola_content_path.mkdir(exist_ok=True)
    
    # Initial sync
    sync_publish_folder(vault_path, zola_content_path)
    
    # Watch if requested
    if args.watch:
        watch_and_sync(vault_path, zola_content_path, args.interval)
    
    return 0


if __name__ == "__main__":
    exit(main())