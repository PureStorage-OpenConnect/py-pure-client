#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tomllib


def parse_version(v):
    """Parses a Semantic Versioning string into a tuple of integers."""
    parts = v.split(".")
    if len(parts) == 3 and all(p.isdigit() for p in parts):
        return tuple(int(p) for p in parts)
    return None


def main():
    # 1. Fetch version from environment
    version = os.environ.get("VERSION")
    if not version:
        print("::error::VERSION environment variable is not set")
        sys.exit(1)

    current = parse_version(version)
    if not current:
        print(f"::error::Invalid version format: {version}")
        sys.exit(1)

    # 2. Validate against pyproject.toml
    try:
        with open("pyproject.toml", "rb") as f:
            pyproject_data = tomllib.load(f)
            source = pyproject_data.get("project", {}).get("version")
    except Exception as e:
        print(f"::error::Failed to read pyproject.toml: {e}")
        sys.exit(1)

    if source != version:
        print(
            f"::error::PR title version ({version}) does not match pyproject.toml version ({source})"
        )
        sys.exit(1)

    # 3. Validate against GitHub Releases
    try:
        result = subprocess.run(
            ["gh", "release", "list", "--limit", "10", "--json", "tagName"],
            capture_output=True,
            text=True,
            check=True,
        )
        tags = json.loads(result.stdout)
    except Exception as e:
        print(f"::error::Failed to fetch releases from GitHub via gh CLI: {e}")
        sys.exit(1)

    versions = []
    for r in tags:
        tag_name = r.get("tagName", "")
        parsed = parse_version(tag_name)
        if parsed:
            versions.append((parsed, tag_name))

    if versions:
        highest, tag = max(versions)
        if current <= highest:
            print(f"::error::Version {version} is not higher than latest release {tag}")
            sys.exit(1)
        print(
            f"Version {version} validated against pyproject.toml and previous release {tag}."
        )
    else:
        print(
            f"Version {version} validated against pyproject.toml. No previous releases found."
        )


if __name__ == "__main__":
    main()
