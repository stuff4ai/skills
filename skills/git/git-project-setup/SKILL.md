---
name: git-project-setup
description: 'Use this skill when the user asks to set up or change the Git and GitHub workflow of a repository: merge methods, squash-only merges, the squash commit message, branch deletion after merge, branch protection or a ruleset for the main branch, or the Git policy in AGENTS.md. Also use it for "/git-project-setup". It changes repository settings after the user answers, and records the policy in AGENTS.md. Do not use it to commit, open pull requests, or merge.'
license: MIT
compatibility: 'Requires Git and the GitHub CLI (`gh`), signed in with `gh auth status`, and admin rights on the repository.'
allowed-tools: shell(gh repo view:*), shell(gh repo edit:*), shell(gh api:*), shell(gh auth status:*), shell(gh --version:*)
---

# Git Project Setup

Set up a GitHub repository so that every pull request lands on the main branch as one commit, with the pull request title and description as its message. Then record the policy in the project instructions, so that agents follow it.

Repository settings are shared and affect everyone. Ask one question per setting, with a short list of answers. The first answer is the default: the policy of this skill, marked "(default)". Change nothing until the user has answered.

- If the user named only some settings, ask only about those, and do not write `AGENTS.md` unless they ask.
- If the user says to use the defaults, that answers every question. Show the commands before you apply them.
- A flag of `gh repo edit` that the user passed counts as an answer only if it matches a whole listed answer. If it matches only a part, ask. If it is a flag that no question covers, ask the user before you use it.

## Before you start

1. Check the tools: `gh --version` and `gh auth status`. If `gh` is missing or not signed in, or the repository has no GitHub remote, tell the user and stop. Do not install anything.
2. Find the repository and the base branch: `gh repo view --json nameWithOwner,defaultBranchRef`.
3. Check the rights: `gh api repos/{owner}/{repo} --jq .permissions`. Without `admin: true`, stop and tell the user that these settings need an admin.
4. Read the current state, and keep the output to compare later:
   - `gh api repos/{owner}/{repo} --jq '{squash: .allow_squash_merge, merge: .allow_merge_commit, rebase: .allow_rebase_merge, title: .squash_merge_commit_title, message: .squash_merge_commit_message, delete: .delete_branch_on_merge}'`
   - `gh api --paginate 'repos/{owner}/{repo}/rulesets?includes_parents=false' --jq '.[] | {id, name, target, enforcement}'`
   - `gh api repos/{owner}/{repo}/rules/branches/<base>`: the rules that apply to the base branch now.
5. Look for a policy block in `AGENTS.md` (see "Record the policy"). If there is one, its values are the defaults of the questions, instead of the ones below.

Show the user the current state, then ask the questions.

## Questions

Ask one at a time, in this order. Use the question tool of the agent if it has one, otherwise a numbered list. Skip a question when the real setting already equals its default answer, and say so. Show the `gh` flags of each answer.

1. **Merge method.**
   - Squash only (default): `--enable-squash-merge --enable-merge-commit=false --enable-rebase-merge=false`
   - Squash and rebase: `--enable-squash-merge --enable-merge-commit=false --enable-rebase-merge`
   - All methods: `--enable-squash-merge --enable-merge-commit --enable-rebase-merge`
   - Keep the current methods: no flags
2. **Squash commit message.** Ask it unless squash will be off after question 1. Every answer carries `--enable-squash-merge`, because `gh` rejects the message flag without it.
   - Pull request title and description (default): `--enable-squash-merge --squash-merge-commit-message pr-title-description`. The description becomes the commit body, and GitHub adds the `Signed-off-by` and `Co-authored-by` trailers of the branch commits itself.
   - Title and commit messages: `--enable-squash-merge --squash-merge-commit-message pr-title-commits`
   - Title only: `--enable-squash-merge --squash-merge-commit-message pr-title`. The body is blank, so no trailers reach the main branch.
   - GitHub default: `--enable-squash-merge --squash-merge-commit-message default`
3. **Merged branches.**
   - Delete them (default): `--delete-branch-on-merge`
   - Keep them: `--delete-branch-on-merge=false`
4. **Base branch protection.**
   - Add or update the ruleset (default): a pull request is required, force pushes and deletion are blocked. It also blocks direct pushes, including from automation.
   - Do not add or change a ruleset
5. **Required approvals.** Ask it only if the answer to question 4 is the ruleset.
   - `0` (default): a pull request is required, but no approval. A single maintainer cannot approve their own pull request.
   - `1` or `2`: tell the user that this blocks every merge unless that many other people can review. Do not add a bypass actor. If the user wants one, add the actor with `bypass_mode: "pull_request"`, because the default `always` lets the actor push directly.
6. **Sign-off.** Every commit carries a `Signed-off-by` trailer: `none` (default), `required`.
7. **Approval.** Who approves a pull request before it is merged: `human` (default), `none`. If the answer to question 5 is above `0`, `none` contradicts it: ask again.

After the last answer, show the exact commands and apply them:

- Join the `gh repo edit` flags in one command. Run it only if there are flags.
- Ruleset: use the name `base-branch-protection`. If a ruleset with that name exists, update it with `gh api repos/{owner}/{repo}/rulesets/<id> --method PUT --input -`. Otherwise create it with `gh api repos/{owner}/{repo}/rulesets --method POST --input -`. Never touch a ruleset with another name or one that belongs to an organization. The body comes from stdin; set `required_approving_review_count` to the answer to question 5:

```json
{"name": "base-branch-protection", "target": "branch", "enforcement": "active",
 "bypass_actors": [],
 "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
 "rules": [
   {"type": "deletion"},
   {"type": "non_fast_forward"},
   {"type": "pull_request", "parameters": {
     "required_approving_review_count": 0,
     "dismiss_stale_reviews_on_push": false,
     "require_code_owner_review": false,
     "require_last_push_approval": false,
     "required_review_thread_resolution": false}}]}
```

If a command fails, report it, run no later command that depends on it, and write the policy block only from the state that you read back. Then read the state again with the commands of step 4, and tell the user what it is now. Report anything that did not change.

## Record the policy

Write the policy into the `AGENTS.md` of the project, between markers. Create the file if it is missing.

```text
<!-- git-policy:start -->
merge: squash
squash-message: pr-title-description
sign-off: none
approval: human
<!-- git-policy:end -->
```

- `merge`: the allowed methods, as a list: `squash`, `squash,rebase`, or `merge,squash,rebase`. Take it from the state that you read back.
- `squash-message`: the value of the `gh` flag, taken from the state that you read back:

  | Value | Title | Message |
  |---|---|---|
  | `default` | `COMMIT_OR_PR_TITLE` | `COMMIT_MESSAGES` |
  | `pr-title` | `PR_TITLE` | `BLANK` |
  | `pr-title-commits` | `PR_TITLE` | `COMMIT_MESSAGES` |
  | `pr-title-description` | `PR_TITLE` | `PR_BODY` |

- `sign-off`: `required`, or `none` for "not required".
- `approval`: `human` means a person must approve the merge. `none` means no approval is required, and an agent still merges only when asked.
- Ignore markers inside code fences. If the file does not have exactly one start marker followed by one end marker, stop and show the user. If there is no block, add it at the end of the file after a blank line. Change only the text between the markers.
- Show the user the block, and ask before you write it. Tell them that the file changed. Do not commit it unless they ask. The ruleset blocks direct pushes, so commit it on a branch and open a pull request.
