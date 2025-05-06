# Decision Log

This file records architectural and implementation decisions using a list format.
2025-05-05 20:45:59 - Log of updates made.

*

* [2025-05-05 20:46:15] - Prefer functional programming approaches over iterative ones. Utilize `functools` and `itertools` where appropriate.
* [2025-05-05 20:47:11] - Prefer concise, simplified, and idiomatic code. Prioritize minimizing lines of code, even if it slightly reduces readability, as less code is easier to maintain.
* [2025-05-05 20:48:13] - Prioritize using the latest available language features, especially if they improve developer experience or code quality.
* [2025-05-05 20:49:06] - Prefer single, well-formatted print statements (e.g., f-strings, multi-line strings) over multiple print calls, especially for structured output like menus.
* [2025-05-05 20:50:01] - Aim to keep individual source files under 500 lines. Favor strong modularization and clear interfaces/connections between modules.
* [2025-05-05 20:50:42] - Strictly adhere to the principle of Low Coupling, High Cohesion (LCHC) in all design decisions. Modules should be independent and focused.
* [2025-05-05 20:52:02] - Strictly prioritize using external, up-to-date documentation sources (e.g., via available tools/MCPs) over internal knowledge when researching APIs, libraries, or language features.
* [2025-05-05 20:53:04] - Use `uv` exclusively for Python execution (`uv run ...`) and dependency management (`uv add ...`). Do not use `python`, `pip`, or `venv` directly.
* [2025-05-05 21:32:59] - Avoid over-commenting code. Only include comments that are strictly necessary, e.g., for complex algorithms or explaining external context. Unnecessary comments add noise.
## Decision

*

## Rationale

*

## Implementation Details

*
