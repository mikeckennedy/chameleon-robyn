# Changelog

All notable changes to chameleon-robyn are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Fixed

- Bare `@template` on a handler in a script run directly (`python app.py`) now derives the template directory from the script's file name, so `index()` in `app.py` maps to `app/index.pt` instead of the literal module name `__main__/index.pt`. An existing `__main__/index.html` or `.pt` is still used when the script-named file is absent, so apps relying on the old name keep working.
- A template variable named `encoding` passed to `render()`, `response()`, a decorated handler or `ChameleonTemplate.render_template()` now raises `ChameleonRobynException` with a clear message. The name is a parameter of Chameleon's own `render()`, so it previously failed with a `TypeError` from inside Chameleon.

### Documentation

- Added a user guide to the docs site: getting started, the `@template` decorator, writing templates, friendly 404 pages, rendering outside handlers, configuration, testing, errors and how to fix them, how it works, and an FAQ. The guide is included in `llms-full.txt`.
- Replaced the auto-generated agent skill with a hand-written `skills/chameleon-robyn/SKILL.md` covering the package's rules, a decision table and the API in one page.
- Added an `Examples` section to every public docstring, and a module docstring naming the entry points.
- The README now links each section to the guide page that expands it, and documents raising `ChameleonRobynNotFoundException` directly to pass a custom 404 message.
- `scripts/build_docs.py` runs the latest Great Docs release through `uvx` with the project installed alongside it, and fails if `llms.txt`, `llms-full.txt` or `skill.md` is missing from the output.

## [0.1.2] - 2026-06-11

Last release before this changelog was started. See the [commit history](https://github.com/mikeckennedy/chameleon-robyn/commits/main) for earlier changes.

## [0.1.1] - 2026-03-20

## [0.1.0] - 2026-03-19

Initial release.

[Unreleased]: https://github.com/mikeckennedy/chameleon-robyn/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/mikeckennedy/chameleon-robyn/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/mikeckennedy/chameleon-robyn/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/mikeckennedy/chameleon-robyn/releases/tag/v0.1.0
