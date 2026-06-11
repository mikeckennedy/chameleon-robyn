# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`chameleon-robyn` is a small PyPI library (alpha, API not yet stable) that integrates the [Chameleon](https://chameleon.readthedocs.io/) template engine (`.pt` page templates, TAL/TALES/METAL) into the [Robyn](https://robyn.tech/) web framework. The entire library is three files in `chameleon_robyn/`; everything else is tests and example apps. It must NOT depend on Jinja2 — see the Protocol note below.

## Commands

The project venv is `venv/` (Python 3.14). Use its binaries directly or activate it first.

```bash
venv/bin/pytest                          # run all tests (testpaths = tests/, configured in pyproject.toml)
venv/bin/pytest tests/test_render.py     # run one test file
venv/bin/pytest tests/test_render.py::test_default_template_name_pt   # run a single test

ruff check .                             # lint (rules in ruff.toml: E, F, I; line-length 120; single quotes)
ruff format .                            # format
pyrefly check                            # type check (pyrefly.toml; assumes py3.13/linux)
ty check                                 # type check (ty + pyrefly are the checkers of choice; keep both green)

python example/app.py                    # run the core-features demo app → http://127.0.0.1:5555
python example-partials/app.py           # same app refactored with chameleon-partials
pip install -e ".[dev,examples]"         # editable install with test + example deps

venv/bin/python scripts/build_docs.py    # build docs (great-docs/Quarto) and mirror into docs/
venv/bin/python scripts/serve_docs.py    # preview docs at http://127.0.0.1:8099/docs/chameleon-robyn/
```

Build backend is hatchling; only the `chameleon_robyn/` package ships in the sdist/wheel (tests, examples, venv are excluded in pyproject.toml).

## Architecture

All real logic lives in `chameleon_robyn/engine.py`. The package exposes two parallel APIs:

1. **Module-level global API** (the primary one): `global_init()` stores a `PageTemplateLoader` in the module-private `__templates` global plus `template_path`. `render()` (str), `response()` (Robyn `Response`), and the `@template` decorator all read that global. `clear()` resets it — tests rely on this via the `setup_global_template` fixture in `tests/conftest.py` (init with `cache_init=False`, yield, `clear()`).

2. **`ChameleonTemplate` class**: a standalone alternative with its own loader, implementing a local `TemplateInterface` *Protocol* (`runtime_checkable`) that structurally matches Robyn's ABC. This is deliberate: importing Robyn's real `TemplateInterface` would drag in a Jinja2 dependency, so the Protocol exists to keep Jinja2 out of the dependency tree. Don't "simplify" it back to the ABC.

### How the `@template` decorator works (`engine.py`)

- Usable three ways: `@template('path/file.pt')`, `@template()`, or bare `@template` (detected by `callable(template_file)`).
- Auto-naming: with no path, it derives `<module>/<function>.html`, falling back to `<module>/<function>.pt` if the `.html` file doesn't exist on disk. Resolution happens lazily at first request (and is only cached once `global_init()` has set the template folder), so apps can decorate routes at import time and init later in `main()`.
- Wraps the handler in a sync or async wrapper chosen via `inspect.iscoroutinefunction` — both paths must be kept in sync when changing behavior.
- Handler return contract, enforced in `__render_response`:
  - a Robyn `Response` is passed through untouched (redirects, custom errors);
  - a `dict` is the template model and gets rendered;
  - anything else raises `ChameleonRobynException`.
- `__response_callback__` is a reserved key popped before rendering (from a copy — the handler's dict is never mutated); it must be callable (else `ChameleonRobynException`) and is invoked with the built `Response` so apps can mutate it (e.g. set session cookies). It is not passed to the template.
- `not_found()` works by raising `ChameleonRobynNotFoundException` (carries the 404 template path, default `errors/404.pt`); the decorator wrappers catch it and render that template with status 404, passing the exception's message to the template as `message`. It only works inside `@template`-decorated handlers.

### Tests

Tests don't start a Robyn server — they call decorated handler functions directly and assert on the returned `Response` (status_code, description). Async handlers are exercised with `asyncio.run()`. Test templates live under `tests/templates/`, with directory names matching the auto-naming convention (e.g. `tests/templates/test_render/index.pt` for a function named `index` defined in `test_render.py`).

conftest.py provides `view_style` (a `['sync', 'async']` parametrized fixture) plus `make_view`/`call_view` fixtures — use them for any test of the decorator's contract behavior so both wrapper code paths stay covered. Don't test Chameleon's own rendering semantics (escaping, TAL loops) or exact error-message wording.

### Examples

`example/` and `example-partials/` are the same demo app (episodes/guests/search, METAL layout inheritance, XML feed, redirect pass-through, friendly 404); the second one factors the episode card into a shared partial via [chameleon-partials](https://github.com/mikeckennedy/chameleon-partials). When adding a user-facing feature, demonstrate it in `example/app.py` and document it in README.md — the README is the de facto API reference.

### Documentation site

Docs are generated by [Great Docs](https://github.com/posit-dev/great-docs) (config: `great-docs.yml`) and published at https://mkennedy.codes/docs/chameleon-robyn/ via git-push static hosting: `scripts/build_docs.py` builds into the ephemeral, gitignored `great-docs/` directory and mirrors `_site/` into the **committed** repo-root `docs/` folder, which nginx serves on the server after a `git pull`. Never commit `great-docs/`; always commit the regenerated `docs/` when public API or README changes. Docstrings are Google style (pinned via `parser: google`) — keep them block-form (`Returns:` on its own line); an inline `Returns: x` aborts the whole docs build.

## Conventions

- Single quotes, line length 120 (ruff-formatted).
- `GEMINI.md` and `AGENTS.md` are symlinks to this file — edit CLAUDE.md only.
