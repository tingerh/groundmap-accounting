# GroundMap Enterprise WeChat Bot

Read-only enterprise WeChat client for GroundMap. It accepts text questions from an explicit user allowlist, calls the debug console SSE API, returns only the final answer and references, and records per-user query history in a local SQLite database.

## Query consistency

- The bot sends the same provider, model, mode, workspace, and tool budget fields as a fresh debug-console query.
- It intentionally does not provide a bot-specific system prompt or perform its own retrieval. The shared `/api/chat` route owns query planning, retrieval, citation validation, and answer generation.
- The console displays the full event stream; the bot extracts and sends only the final `【ANSWER】` section. Presentation differs, but the evidence and reasoning pipeline are shared.
- A console conversation with prior messages can produce a context-dependent answer. Compare channels using a fresh console conversation and the same mode when validating consistency.

## Shared answer cache

- Standalone questions use the shared debug-console answer cache before starting a model call.
- A cached answer is reused only when text similarity is at least 80% and accounting contrast terms, negations, and numbers remain compatible.
- Follow-up messages with conversation history are never cached because their meaning depends on earlier turns.
- Cache entries are isolated by provider, model, mode, workspace, and Git version, and expire after 30 days. A new repository commit invalidates older entries conservatively.
- Prefix a standalone question with `/refresh` to bypass the cache and generate a new answer.

## Security boundary

- The bot is an external client under `tools/`; it does not read or edit Markdown directly.
- Credentials belong only in `.env.local`, which is ignored by Git.
- Query history is operational data under `data/`, also ignored by Git.
- User IDs are stored as SHA-256 hashes in SQLite.
- An empty allowlist denies all users.
- Reset any secret that has been pasted into chat, email, tickets, or logs before use.

## Setup

1. In enterprise WeChat, create an API-mode intelligent bot using the long-connection option.
2. Reset the bot secret if it has ever been disclosed.
3. Create the local configuration:

   ```powershell
   Copy-Item .env.example .env.local
   ```

4. Edit `.env.local` locally and provide the new bot ID, new secret, and comma-separated test user IDs.
   A tester can send `/whoami` to the bot to obtain their own enterprise WeChat user ID without calling the model.
5. Install dependencies from the repository virtual environment:

   ```powershell
   ..\..\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

6. Start the GroundMap web service and debug console, then start the bot:

   ```powershell
   ..\..\.venv\Scripts\python.exe main.py
   ```

## Multiple enterprises

Each enterprise must create its own API-mode bot and provide its own bot ID and secret. Reuse the code and GroundMap service, not another enterprise's credentials.

1. Create a local ignored configuration directory and copy the template once per enterprise:

   ```powershell
   New-Item -ItemType Directory -Force instances
   Copy-Item .env.example instances\company-a.env
   Copy-Item .env.example instances\company-b.env
   ```

2. Give every instance a distinct `WECOM_HISTORY_DB`, for example `data/company-a-query-history.db` and `data/company-b-query-history.db`.
3. Validate each configuration without connecting:

   ```powershell
   ..\..\.venv\Scripts\python.exe main.py --config instances\company-a.env --check
   ..\..\.venv\Scripts\python.exe main.py --config instances\company-b.env --check
   ```

4. Start one long-running process per enterprise:

   ```powershell
   ..\..\.venv\Scripts\python.exe main.py --config instances\company-a.env
   ..\..\.venv\Scripts\python.exe main.py --config instances\company-b.env
   ```

The `instances/` directory is ignored by Git because it contains credentials. User IDs and allowlists are enterprise-specific; collect them again with `/whoami` in each enterprise.

## References

Until `PUBLIC_KB_BASE_URL` points to an authenticated URL that testers can reach, replies include reference titles without clickable links. Never set this to `localhost` for remote testers.

## Test scope

The first release supports text questions only. It deliberately excludes file upload, Wiki editing, administrative operations, and viewing another user's history.
