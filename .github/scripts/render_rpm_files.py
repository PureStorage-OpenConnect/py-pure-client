#!/usr/bin/env python3
"""Render the RPM .spec file from pyproject.toml.

Project name, version, description, maintainer, homepage, and
runtime dependencies are sourced from pyproject.toml so they stay in sync.
RPM-specific fields (BuildRequires, macros, etc.) live in the .spec
template under .github/.templates/rpm/.
"""
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from string import Template

TEMPLATE_REL = Path(".github/.templates/rpm")
OUTPUT_REL = Path("packaging/specs")

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

def render(source_dir: Path, build_num: str = "1") -> None:
    with (source_dir / "pyproject.toml").open("rb") as f:
        pyproject = tomllib.load(f)

    proj = pyproject["project"]
    author = proj["authors"][0]

    sdist_name = proj["name"].replace("-", "_")
    module_name = pyproject["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"][0]

    build_date = datetime.now(timezone.utc).strftime("%a %b %d %Y")

    subs = {
        "NAME": proj["name"],
        "SDIST_NAME": sdist_name,
        "MODULE_NAME": module_name,
        "VERSION": proj["version"],
        "BUILD_NUM": build_num,
        "SUMMARY": proj["description"],
        "HOMEPAGE": proj.get("urls", {}).get("GitHub", ""),
        "MAINTAINER": f'{author["name"]} <{author["email"]}>',
        "BUILD_DATE": build_date,
    }

    template_dir = source_dir / TEMPLATE_REL
    output_dir = source_dir / OUTPUT_REL
    output_dir.mkdir(parents=True, exist_ok=True)

    spec_template = template_dir / "py-pure-client.spec"
    spec_output = output_dir / "py-pure-client.spec"
    spec_output.write_text(Template(spec_template.read_text()).substitute(subs))
    print(f"Rendered {spec_output.relative_to(source_dir)}")


if __name__ == "__main__":
    source_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    build_num = os.environ.get("BUILD_NUM", "1")
    render(source_dir, build_num=build_num)
