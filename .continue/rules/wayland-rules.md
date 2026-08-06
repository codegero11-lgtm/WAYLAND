<important_rules>

You are an implementation agent working on the WAYLAND project.

The documentation is the source of truth.

Before changing any code you MUST read:

- README.md
- CURRENT_STATUS.md
- TRACEABILITY.md
- TECH_DEBT.md
- CHANGELOG.md
- PROJECT/ or LOTES documentation
- relevant files under docs/

------------------------------------------------
GENERAL
------------------------------------------------

Never assume previous chat history.

Never invent project architecture.

Never change public interfaces without explicitly stating it.

Never silently update contracts.

Always explain why a change is necessary.

------------------------------------------------
IMPLEMENTATION
------------------------------------------------

Never rewrite an entire file when a localized edit is sufficient.

Prefer the smallest possible diff.

Do not introduce refactors outside the requested scope.

Do not change formatting-only unless requested.

------------------------------------------------
DEBUGGING
------------------------------------------------

Maximum two hypotheses for the same problem.

If two attempts fail:

- stop
- explain findings
- suggest next investigation
- wait for user approval

Never enter trial-and-error loops.

------------------------------------------------
TEMPORARY FILES
------------------------------------------------

Do not create temporary scripts unless:

- many files must be migrated
- code generation is required
- repetitive edits justify automation

Temporary scripts must be deleted before finishing.

------------------------------------------------
VALIDATION
------------------------------------------------

After every change:

- execute only the relevant validation
- show output
- explain whether the result validates the hypothesis

Do not continue fixing unrelated problems automatically.

------------------------------------------------
COMMITS
------------------------------------------------

Never commit.

Never push.

Never create branches.

Suggest commit messages only.

------------------------------------------------
DOCUMENTATION
------------------------------------------------

Whenever implementation changes project status:

Update:

- CURRENT_STATUS.md
- TRACEABILITY.md
- CHANGELOG.md

Update TECH_DEBT.md if technical debt changes.

------------------------------------------------
OUTPUT
------------------------------------------------

Always include:

Language

File name

Reason for change

Diff summary

Validation performed

Remaining risks

</important_rules>