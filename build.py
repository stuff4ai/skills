#!/usr/bin/env python3
"""Build generated skills into skills/ from sources in src/.

A generated skill has a source folder src/<area>/<name>/ with:
  upstream.lock  pinned upstream SKILL.md and its license (JSON)
  overlay.md     text appended to the end of the upstream SKILL.md

The result is skills/<area>/<name>/{SKILL.md,NOTICE}. Skills written by hand
live directly in skills/ and are never touched here.
"""
import argparse, hashlib, json, re, sys, tempfile, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
SKILLS = ROOT / "skills"
CACHE = ROOT / ".cache"


def fetch(repo, sha, path, want_hash):
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError(f"not a full commit SHA: {sha}")
    key = hashlib.sha256(f"{repo}\0{sha}\0{path}".encode()).hexdigest()
    cached = CACHE / key
    if cached.exists():
        data = cached.read_bytes()
    else:
        url = f"https://raw.githubusercontent.com/{repo}/{sha}/{path}"
        data = urllib.request.urlopen(url, timeout=30).read()
    if hashlib.sha256(data).hexdigest() != want_hash:
        raise ValueError(f"hash mismatch for {path}; delete .cache if it is stale")
    if not cached.exists():
        CACHE.mkdir(exist_ok=True)
        cached.write_bytes(data)
    return data.decode("utf-8")


def render(src_dir):
    """Return {file name: text} for one generated skill."""
    lock = json.loads((src_dir / "upstream.lock").read_text(encoding="utf-8"))
    upstream = fetch(lock["repo"], lock["sha"], lock["path"], lock["sha256"])
    lic = fetch(lock["repo"], lock["sha"], lock["license_path"], lock["license_sha256"])
    overlay = (src_dir / "overlay.md").read_text(encoding="utf-8")
    return {
        "SKILL.md": upstream.rstrip("\n") + "\n\n" + overlay.strip("\n") + "\n",
        "NOTICE": (
            f"This skill is derived from {lock['repo']} ({lock['path']}),\n"
            f"commit {lock['sha']}, with changes.\n"
            f"Original license:\n\n{lic}"
        ),
    }


def tree(folder):
    if not folder.is_dir():
        return {}
    return {
        str(p.relative_to(folder)): p.read_bytes()
        for p in sorted(folder.rglob("*")) if p.is_file()
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("names", nargs="*", help="skill names; default: all generated skills")
    ap.add_argument("--check", action="store_true", help="fail if skills/ is out of date")
    args = ap.parse_args()

    found = {p.parent.name: p.parent for p in SRC.glob("*/*/upstream.lock")}
    unknown = [n for n in args.names if n not in found]
    if unknown:
        sys.exit(f"unknown skill(s): {', '.join(unknown)}")
    if not found:
        sys.exit("no generated skills found in src/")
    chosen = {n: found[n] for n in (args.names or found)}

    try:
        built = {
            n: {k: v.encode("utf-8") for k, v in render(d).items()}
            for n, d in chosen.items()
        }
    except (OSError, ValueError, KeyError) as e:
        sys.exit(f"build failed: {e}")

    stale = []
    for n, files in built.items():
        out = SKILLS / chosen[n].parent.name / n
        if args.check:
            if tree(out) != files:
                stale.append(str(out.relative_to(ROOT)))
        else:
            out.mkdir(parents=True, exist_ok=True)
            for name, data in files.items():
                (out / name).write_bytes(data)
    if stale:
        sys.exit("out of date: " + ", ".join(stale))


if __name__ == "__main__":
    main()
