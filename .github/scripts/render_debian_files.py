#!/usr/bin/env python3
"""Render the debian/ packaging tree from pyproject.toml.

Project name, version, description, maintainer, homepage, license, and
runtime dependencies are sourced from pyproject.toml so they stay in sync.
Debian-specific fields (Section, Build-Depends, Standards-Version, etc.)
live in the .in templates under .github/.templates/deb/.
"""
import os
import re
import shutil
import stat
import sys
from email.utils import formatdate
from pathlib import Path
from string import Template

TEMPLATE_REL = Path(".github/.templates/deb")
OUTPUT_REL = Path("debian")

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

# PyPI distribution name -> Debian binary package name. Most map predictably
# to python3-<lowercased-name>; entries here cover the cases that don't.
__PYPI_TO_DEBIAN = {
    "python-dateutil": "python3-dateutil",
    "pyjwt": "python3-jwt",
}


# Header of LICENSE.txt -> DEP-5 short license identifier.
__LICENSE_HEADER_TO_DEP5 = {
    "bsd 2-clause license": "BSD-2-Clause",
}


__DEP_NAME_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)")


__DEP_FILES = [
    "control",
    "copyright",
    "rules",
    "changelog"
]


def __pypi_to_debian(name: str) -> str:
    key = name.lower().replace("_", "-")
    return __PYPI_TO_DEBIAN.get(key, f"python3-{key}")


def __parse_license_id(license_path: Path) -> str:
    header = license_path.read_text().strip().splitlines()[0].strip().lower()
    try:
        return __LICENSE_HEADER_TO_DEP5[header]
    except KeyError as exc:
        raise ValueError(
            f"Unrecognized license header in {license_path}: {header!r}. "
            f"Update a mapping to LICENSE_HEADER_TO_DEP5."
        ) from exc


def render(source_dir: Path) -> None:
    with (source_dir / "pyproject.toml").open("rb") as f:
        proj = tomllib.load(f)["project"]

    author = proj["authors"][0]
    deb_deps = []
    for dep in proj.get("dependencies", []):
        m = __DEP_NAME_RE.match(dep.strip())
        if m:
            deb_deps.append(__pypi_to_debian(m.group(1)))

    license_files = proj.get("license-files", ["LICENSE.txt"])
    license_id = __parse_license_id(source_dir / license_files[0])

    subs = {
        "NAME": proj["name"],
        "VERSION": proj["version"],
        "DESCRIPTION": proj["description"],
        "AUTHOR_NAME": author["name"],
        "MAINTAINER": f'{author["name"]} <{author["email"]}>',
        "HOMEPAGE": proj.get("urls", {}).get("GitHub", ""),
        "DEPENDS": ",\n ".join(deb_deps),
        "LICENSE": license_id,
        "DATE": formatdate(localtime=True),
    }

    template_dir = source_dir / TEMPLATE_REL
    output_dir = source_dir / OUTPUT_REL
    (output_dir / "source").mkdir(parents=True, exist_ok=True)

    for stem in __DEP_FILES:
        src = template_dir / stem
        dst = output_dir / stem
        dst.write_text(Template(src.read_text()).substitute(subs))
        # debian/rules must be executable; mirror the template's mode otherwise.
        mode = os.stat(src).st_mode
        if stem == "rules":
            mode |= stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        os.chmod(dst, mode)
        print(f"Rendered {output_dir.name}/{stem}")

    # Verbatim files (no substitution): copy alongside the rendered output.
    shutil.copyfile(template_dir / "source" / "format", output_dir / "source" / "format")
    print(f"Copied {output_dir.name}/source/format")


if __name__ == "__main__":
    render(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("."))
