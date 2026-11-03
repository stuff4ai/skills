# Agent instructions

This repository holds reusable agent skills and the tools that build them.

## Rules

- Content is generic. Do not mention, quote, or describe any other project,
  repository, or private context in files, commit messages, or pull requests.
- Everything is in English, in simple wording.
- A skill is a folder `skills/<area>/<name>/` with `SKILL.md` and supporting
  files. Keep generated files, sources, and tooling metadata out of it.
- A skill written by hand lives directly in `skills/`. A skill derived from an
  upstream skill has its source in `src/<area>/<name>/` and is built into
  `skills/` with `python3 -I build.py`. Do not edit a built skill by hand: change
  its source and rebuild.
- A skill derived from another project keeps its source and original license
  in a `NOTICE` file next to `SKILL.md`.
