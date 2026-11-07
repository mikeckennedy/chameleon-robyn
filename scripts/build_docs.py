#!/usr/bin/env python3
"""Build the docs and mirror the static site into the committed repo-root docs/ folder.

Runs the latest Great Docs release through `uvx`, with this project installed alongside it so
`dynamic: true` can import chameleon_robyn (that import is what produces llms-full.txt and the
one-line summaries in llms.txt; without it Great Docs silently falls back to static analysis).
The great-docs/ build directory is ephemeral. The server serves the committed docs/ folder via
nginx alias at https://mkennedy.codes/docs/chameleon-robyn/.
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

# Files whose absence means the build quietly degraded (import failure, skill misconfig, ...).
REQUIRED_OUTPUTS = (
    'llms.txt',
    'llms-full.txt',
    'skill.md',
    '.well-known/agent-skills/chameleon-robyn/SKILL.md',
    '.well-known/agent-skills/index.json',
    'sitemap.xml',
    'robots.txt',
)


def main() -> int:
    if shutil.which('uvx') is None:
        print('uvx not found on PATH; install uv (https://docs.astral.sh/uv/)', file=sys.stderr)
        return 1

    # Match the interpreter running this script so the project's dependencies (Robyn wheels)
    # resolve the same way they do in the project venv.
    python = f'{sys.version_info.major}.{sys.version_info.minor}'
    cmd = [
        'uvx',
        '--python',
        python,
        '--from',
        'great-docs@latest',
        '--with-editable',
        str(REPO_ROOT),
        'great-docs',
        'build',
    ]
    if subprocess.run(cmd, cwd=REPO_ROOT).returncode != 0:
        return 1
    if not SITE.is_dir():
        print(f'build output missing: {SITE}', file=sys.stderr)
        return 1

    missing = [name for name in REQUIRED_OUTPUTS if not (SITE / name).is_file()]
    if missing:
        print('build completed but these outputs are missing: ' + ', '.join(missing), file=sys.stderr)
        print('llms-full.txt missing usually means Great Docs could not import chameleon_robyn.', file=sys.stderr)
        return 1

    skill_src = (REPO_ROOT / 'skills' / 'chameleon-robyn' / 'SKILL.md').read_text(encoding='utf-8')
    if (SITE / 'skill.md').read_text(encoding='utf-8') != skill_src:
        print('skill.md in the site does not match skills/chameleon-robyn/SKILL.md', file=sys.stderr)
        return 1

    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(SITE, DEST)
    print(f'Mirrored -> {DEST} ({sum(1 for p in DEST.rglob("*") if p.is_file())} files)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
