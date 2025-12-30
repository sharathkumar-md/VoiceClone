#!/usr/bin/env python3
"""Debug script to check environment on Render"""
import os
import sys
from pathlib import Path

print("=" * 60)
print("RENDER ENVIRONMENT DEBUG")
print("=" * 60)

print("\n1. CURRENT WORKING DIRECTORY:")
print(f"   {os.getcwd()}")

print("\n2. SCRIPT LOCATION:")
print(f"   {Path(__file__).resolve()}")

print("\n3. PYTHON PATH:")
for i, p in enumerate(sys.path, 1):
    print(f"   {i}. {p}")

print("\n4. DIRECTORY STRUCTURE:")
cwd = Path.cwd()
print(f"\nContents of {cwd}:")
for item in sorted(cwd.iterdir()):
    print(f"   {'[DIR]' if item.is_dir() else '[FILE]'} {item.name}")

if (cwd / 'src').exists():
    print(f"\nContents of {cwd / 'src'}:")
    for item in sorted((cwd / 'src').iterdir()):
        print(f"   {'[DIR]' if item.is_dir() else '[FILE]'} {item.name}")

print("\n5. LOOKING FOR API MODULE:")
api_locations = [
    cwd / 'api',
    cwd / 'src' / 'api',
    cwd / 'src' / 'src' / 'api',
]
for loc in api_locations:
    if loc.exists():
        print(f"   ✓ FOUND: {loc}")
    else:
        print(f"   ✗ NOT FOUND: {loc}")

print("\n6. ENVIRONMENT VARIABLES:")
print(f"   PORT: {os.getenv('PORT', 'not set')}")
print(f"   PYTHON_VERSION: {os.getenv('PYTHON_VERSION', 'not set')}")

print("=" * 60)
