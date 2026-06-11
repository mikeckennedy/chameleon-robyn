#!/usr/bin/env python3
"""Build the docs and mirror the static site into the committed repo-root docs/ folder.

The great-docs/ build directory is ephemeral (Great Docs writes a .gitignore of '*'
inside it and regenerates it each build). The server serves the committed docs/ folder
via nginx alias at https://mkennedy.codes/docs/chameleon-robyn/.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPTS.parent  # pyproject.toml + great-docs.yml live at the git root
SITE = REPO_ROOT / 'great-docs' / '_site'
DEST = REPO_ROOT / 'docs'


def main() -> int:
    great_docs = Path(sys.executable).with_name('great-docs')
    cmd = [str(great_docs) if great_docs.exists() else 'great-docs', 'build']
    if subprocess.run(cmd, cwd=REPO_ROOT).returncode != 0:
        return 1
    if not SITE.is_dir():
        print(f'build output missing: {SITE}', file=sys.stderr)
        return 1
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(SITE, DEST)
    print(f'Mirrored -> {DEST} ({sum(1 for p in DEST.rglob("*") if p.is_file())} files)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
