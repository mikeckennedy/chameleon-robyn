# Changelog

This changelog is generated automatically from [GitHub Releases](https://github.com/mikeckennedy/chameleon-robyn/releases).


# v0.1.3

*2026-11-07* · [GitHub](https://github.com/mikeckennedy/chameleon-robyn/releases/tag/v0.1.3)

Released to PyPI on 2026-11-07: https://pypi.org/project/chameleon-robyn/0.1.3/


### Fixed

- Bare `[@template](https://github.com/template)` on a handler in a script run directly (`python app.py`) now derives the template directory from the script's file name, so `index()` in `app.py` maps to `app/index.pt` instead of the literal module name `__main__/index.pt`. An existing `__main__/index.html` or `.pt` is still used when the script-named file is absent, so apps relying on the old name keep working.
- A template variable named `encoding` passed to [render()](reference/render.html#chameleon_robyn.render), [response()](reference/response.html#chameleon_robyn.response), a decorated handler or [ChameleonTemplate.render_template()](reference/ChameleonTemplate.html#chameleon_robyn.ChameleonTemplate.render_template) now raises [ChameleonRobynException](reference/ChameleonRobynException.html#chameleon_robyn.ChameleonRobynException) with a clear message. The name is a parameter of Chameleon's own [render()](reference/render.html#chameleon_robyn.render), so it previously failed with a `TypeError` from inside Chameleon.


### Documentation

- Added a user guide to the docs site: getting started, the `[@template](https://github.com/template)` decorator, writing templates, friendly 404 pages, rendering outside handlers, configuration, testing, errors and how to fix them, how it works, and an FAQ. The guide is included in `llms-full.txt`.
- Replaced the auto-generated agent skill with a hand-written `skills/chameleon-robyn/SKILL.md` covering the package's rules, a decision table and the API in one page.
- Added an `Examples` section to every public docstring, and a module docstring naming the entry points.
- The README now links each section to the guide page that expands it, and documents raising [ChameleonRobynNotFoundException](reference/ChameleonRobynNotFoundException.html#chameleon_robyn.ChameleonRobynNotFoundException) directly to pass a custom 404 message.
- `scripts/build_docs.py` runs the latest Great Docs release through `uvx` with the project installed alongside it, and fails if `llms.txt`, `llms-full.txt` or `skill.md` is missing from the output.
- The user guide and README now follow one running example, the podcast site in `example/`, with each section opening on the problem the feature solves. Code samples are unchanged.
- The docs site has a changelog page, generated from GitHub Releases and linked from the navbar. Releases 0.1.0 through 0.1.2 were tagged and published as GitHub Releases retroactively.

Full changelog: https://github.com/mikeckennedy/chameleon-robyn/blob/main/CHANGELOG.md


# v0.1.2

*2026-11-07* · [GitHub](https://github.com/mikeckennedy/chameleon-robyn/releases/tag/v0.1.2)

Released to PyPI on 2026-06-11: https://pypi.org/project/chameleon-robyn/0.1.2/

Review pass that fixed several decorator bugs reported in [\#1](https://github.com/mikeckennedy/chameleon-robyn/issues/1), added docstrings and a documentation site, and broadened the test suite.


### Fixed

- Auto-named templates are now resolved lazily at the first request instead of at decoration time, so [global_init()](reference/global_init.html#chameleon_robyn.global_init) can run after routes are decorated and the `.html`-or-`.pt` check looks in the real template folder rather than a working-directory-relative `templates` default.
- Reusing one `[@template](https://github.com/template)()` decorator instance across several handlers no longer leaks the first handler's auto-derived template name into the others.
- The handler's returned dict is copied before `__response_callback__` is popped, so handlers returning a shared or module-level dict are never mutated.
- A non-callable `__response_callback__` now raises [ChameleonRobynException](reference/ChameleonRobynException.html#chameleon_robyn.ChameleonRobynException) instead of being silently ignored.
- The message carried by [not_found()](reference/not_found.html#chameleon_robyn.not_found) and [ChameleonRobynNotFoundException](reference/ChameleonRobynNotFoundException.html#chameleon_robyn.ChameleonRobynNotFoundException) is now passed to the 404 template as `message`. Previously the 404 template was rendered with an empty model.
- The README and the [template()](reference/template.html#chameleon_robyn.template) docstring described auto-naming backwards. Both now say `.html` is tried first with `.pt` as the fallback, which is what the code has always done. The README also no longer claims [ChameleonTemplate](reference/ChameleonTemplate.html#chameleon_robyn.ChameleonTemplate) subclasses Robyn's ABC.


### Changed

- Tightened type annotations across the public API: [not_found()](reference/not_found.html#chameleon_robyn.not_found) returns `NoReturn`, template data is `Any`, and parameters have explicit `bool`, `str` and `int` types. The library, tests and examples type-check clean under both ty and pyrefly.
- The development status classifier on PyPI is now Alpha, matching the README notice.
- Dropped the unused `hatch-vcs` build requirement and the unused `pytest-asyncio` dev dependency. `great-docs` is now a dev dependency.
- Expanded the PyPI keywords and added Documentation, Source, Issues, PyPI and Funding project URLs.


### Added

- Google-style docstrings on every public function, class and exception.
- Documentation site generated by Great Docs at https://mkennedy.codes/docs/chameleon-robyn/, including `llms.txt`, `llms-full.txt` and an agent skill page, plus `scripts/build_docs.py` and `scripts/serve_docs.py`.
- README section on `__response_callback__` with a set-a-session-cookie example, and a matching `/cookie-example` route in `example/app.py`.
- Test suite grew from 22 to 39 tests, with `view_style`, `make_view` and `call_view` fixtures that run the decorator contract tests through both the sync and async wrappers.

Full changelog: https://github.com/mikeckennedy/chameleon-robyn/blob/main/CHANGELOG.md


# v0.1.1

*2026-11-07* · [GitHub](https://github.com/mikeckennedy/chameleon-robyn/releases/tag/v0.1.1)

Released to PyPI on 2026-03-20: https://pypi.org/project/chameleon-robyn/0.1.1/


### Added

- `__response_callback__` reserved model key. A handler can include a callable under this key in its returned dict and the decorator calls it with the built `Response` after rendering, so apps can set cookies or headers. The key is removed from the model before the template is rendered and is never passed to the template.

Full changelog: https://github.com/mikeckennedy/chameleon-robyn/blob/main/CHANGELOG.md


# v0.1.0

*2026-11-07* · [GitHub](https://github.com/mikeckennedy/chameleon-robyn/releases/tag/v0.1.0)

Released to PyPI on 2026-03-19: https://pypi.org/project/chameleon-robyn/0.1.0/

Initial release.


### Added

- [global_init()](reference/global_init.html#chameleon_robyn.global_init) points Chameleon at a template folder, with `auto_reload`, `cache_init` and `restricted_namespace` options.
- `[@template](https://github.com/template)` decorator for Robyn handlers: explicit template paths, auto-naming from the module and function name (`.html` first, then `.pt`), sync and async handlers, custom status codes and content types, and pass-through of handlers that return a Robyn `Response`.
- [not_found()](reference/not_found.html#chameleon_robyn.not_found) renders a friendly 404 page (default `errors/404.pt`) from inside a decorated handler.
- [render()](reference/render.html#chameleon_robyn.render) and [response()](reference/response.html#chameleon_robyn.response) for rendering templates outside of handlers.
- [ChameleonTemplate](reference/ChameleonTemplate.html#chameleon_robyn.ChameleonTemplate) class implementing Robyn's `TemplateInterface` through a local Protocol, so the library does not pull in Jinja2.
- Example apps in `example/` and `example-partials/`.

Full changelog: https://github.com/mikeckennedy/chameleon-robyn/blob/main/CHANGELOG.md
