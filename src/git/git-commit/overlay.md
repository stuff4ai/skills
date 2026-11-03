## Sign-off

Decide this before step 5. `git commit -s` adds a `Signed-off-by` trailer. Use it when the project asks for it:

- Project instructions, such as `AGENTS.md`, `CLAUDE.md`, and `CONTRIBUTING.md`. They may say it in any words: "sign off", "DCO", "Signed-off-by".
- A DCO check in the repository, such as a `.github/dco.yml` file or a CI job that checks for `Signed-off-by`.
- Recent commits that carry the trailer. This prints one line for each trailer found: `git log -20 --format='%(trailers:key=Signed-off-by,valueonly)'`.

If none of these asks for it, do not use `-s`. If the project forbids a sign-off by an agent, do not use it either. Do not ask the user: a person who asks you to commit accepts the sign-off in their name.

## Agent attribution

Decide this before step 5. When an agent took part in the work, record it with one trailer at the end of the message. Do not add any other mark of authorship, such as "Generated with ..." banners or tool links.

Choose the trailer in this order:

1. Use the `Co-authored-by` line that your environment gives you. The case of the token does not matter, so `Co-Authored-By` is fine.
2. If it gives none, write `Co-authored-by: <agent and model> <vendor noreply address>`, but only when you know the address for certain.
3. If you do not know the address, ask the user. If you cannot ask, commit without the trailer and say so.

Add the trailer with `--trailer`, not with a separate `-m`, so that Git keeps it in the same block as the other trailers:

```bash
git commit -m "fix(parser): accept empty input" --trailer "Co-authored-by: Name <name@example.com>"
```
