---
name: git-pr
description: 'Use this skill when the user asks to open a GitHub pull request, says "open a PR" or "/pr", or asks to write or change a PR title or description. It writes them for the commit that lands on the main branch. Do not use it to make commits, push without a PR, merge, review, or work with other hosts.'
license: MIT
compatibility: 'Requires Git and the GitHub CLI (`gh`), signed in with `gh auth status`.'
allowed-tools: shell(git:*), shell(gh:*)
---

# Git Pull Request

Open a GitHub pull request whose title and description read well as the commit that lands on the main branch. Many repositories squash a pull request into one commit, so write the title and description for the history, not for the review thread.

If project instructions or a PR template differ from this skill, follow them.

If the user asks only for a title or description, write it and stop. Do not push or create anything.

## Before you start

1. Find the base branch: `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`. Use another base only if the user names one. Then run `git fetch origin <base>`.
2. Check that the current branch is not the base branch. If it is, ask the user for a branch name, or create one named `<type>/<kebab-case-topic>`, where `<type>` is a Conventional Commits type.
3. If `git status` shows uncommitted changes, tell the user and stop. Commit only if the user asks.
4. Read the whole change, not only the last commit: `git log origin/<base>..HEAD` and `git diff origin/<base>...HEAD`. If there are no commits ahead of the base, tell the user and stop.
5. Look for an open pull request for the branch: `gh pr list --head <branch> --state open --json number,url`.
   - If one exists and the user asked to open a PR, give them its URL and stop.
   - If one exists and the user asked to update it, run `gh pr edit <number> --title '<title>' --body-file -` and change only what they asked to change.

## Push

Pushing publishes the work. Push only when the user asked to open a pull request, because that request includes the push: `git push -u origin HEAD`. If the push is rejected, stop and tell the user. Force push only if the user asks, with `--force-with-lease`.

## Title

- Use the Conventional Commits form: `<type>(<scope>): <summary>`. The scope is optional.
- Describe the whole change, in the imperative mood, with no period at the end.
- Keep it at 64 characters or less: GitHub adds ` (#123)` to the squash commit title.
- Use the types and scopes of the project. When unsure, look at `git log origin/<base> --oneline -20`.

## Description

The description is the body of the future commit.

- Start with why: the problem or the need. Then say what changed, at the level of behavior, not a list of files.
- Describe the net result of the branch. Do not narrate the steps, the fixes during review, or the dead ends.
- Wrap lines at 72 characters, as in a commit message. Do not use a Markdown table, a heading, or a checklist. A short list of plain items is fine.
- Leave out temporary facts: CI results, test output, screenshots, review state, and "ready for review".
- Refer to files by paths relative to the repository root. Do not use absolute paths or local file links.
- To link an issue, put `Closes #123` or `Refs #123` in its own paragraph before the trailers.
- Write in the language of the project history, usually English.

## Trailers

What lands on the main branch depends on the squash message setting of the repository:

- `PR_BODY`: the description. Trailers of the branch commits are lost unless the description repeats them.
- `COMMIT_MESSAGES`: the messages of the branch commits, trailers included.
- `BLANK`: no body.

Check it with `gh api repos/{owner}/{repo} --jq '[.allow_squash_merge, .squash_merge_commit_message]'`. Empty values mean the setting is unknown, for example without push access: then keep the trailers and do not warn.

- Copy each distinct trailer from the branch commits, exactly and once, into one block at the very end of the description, after a blank line, one per line. Do not add a trailer that no commit carries.
- If the setting is `BLANK`, tell the user that no trailers will reach the main branch. Under `COMMIT_MESSAGES` the copy does no harm.
- Do not add a "Generated with" line or any other banner, unless the project asks for one.

## Create

Pass the title in single quotes and the description on stdin through a quoted heredoc, so that the shell changes neither. Escape any `'` in the title.

```sh
gh pr create --base <base> --title '<title>' --body-file - <<'EOF'
<description>
EOF
```

- Do not pass `--draft` unless the user asks. Do not request reviewers, labels, or assignees unless the user asks.
- Never merge the pull request.
- Tell the user the URL that `gh` prints.
