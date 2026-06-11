---
name: chameleon-robyn
description: >
  Adds integration of the Chameleon template language to Robyn. Use when writing Python code that uses the chameleon_robyn package.
license: MIT
compatibility: Requires Python >=3.10.
---

# chameleon-robyn

Adds integration of the Chameleon template language to Robyn.

## Installation

```bash
pip install chameleon-robyn
```

## API overview

### Setup & configuration

Initialize the template engine once at app startup.

- `global_init`: Initialize the Chameleon template engine
- `clear`: Reset the template engine to its uninitialized state

### Rendering views

The @template decorator and friendly 404s for Robyn route handlers.

- `template`: Decorate a Robyn view method to render an HTML response
- `not_found`: Render a friendly 404 page from within a @template-decorated handler

### Lower-level rendering

Render templates outside the decorator (middleware, error handlers, emails).

- `render`: Render a Chameleon template to a string (no Response wrapping)
- `response`: Render a Chameleon template and wrap it in a fully-formed Robyn Response

### Robyn TemplateInterface

Standalone template engine class matching Robyn's built-in template pattern.

- `ChameleonTemplate`: Chameleon template engine implementing Robyn's TemplateInterface

### Exceptions

Exception types raised by the library.

- `ChameleonRobynException`: Base exception for all chameleon-robyn errors (bad configuration, invalid return types, etc.)
- `ChameleonRobynNotFoundException`: Raised by not_found() to signal a 404 from within a @template-decorated handler

## Resources

- [Full documentation](https://mkennedy.codes/docs/chameleon-robyn/)
- [llms.txt](llms.txt) — Indexed API reference for LLMs
- [llms-full.txt](llms-full.txt) — Comprehensive documentation for LLMs
- [Source code](https://github.com/mikeckennedy/chameleon-robyn)
