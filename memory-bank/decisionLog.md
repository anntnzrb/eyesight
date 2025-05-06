# Decision Log

This file records architectural and implementation decisions using a list format.
2025-05-06 01:40:44 - Log of updates made.

*

## Decision

[2025-05-06 02:31:30] - Refactored `eyesight.gemini.session.create_session` to be an asynchronous context manager.

## Rationale

*   The `google-genai` library's `gemini.client.aio.live.connect()` method returns an asynchronous context manager.
*   To correctly use this and resolve Pylance errors ("is not awaitable"), `create_session` must also be an async context manager.
*   This ensures proper resource management for the Gemini API session.

## Implementation Details

*   Added `@asynccontextmanager` decorator from `contextlib` to `create_session`.
*   Modified `create_session` to use `async with ... as session:` and `yield session`.
*   Updated the return type hint of `create_session` to `AsyncIterator[GeminiLiveSession]`.
*   Updated the docstring of `create_session` to reflect its usage as a context manager.
*
*

## Rationale 

*

## Implementation Details

*
