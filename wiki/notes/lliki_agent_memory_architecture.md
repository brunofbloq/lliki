
# lliki-agent-memory: Minimal Architecture (Local, DB-free)

## Components

1. **Markdown Source (`lliki/`)**
   - Plain `.md` files with optional YAML frontmatter:
     ```yaml
     ---
     id: battery-pack-design
     type: module
     tags: [battery, hardware]
     depends_on: [cell-chemistry, thermal-management]
     ---
     ```
   - Links: `[[other-page.md]]`, `[text](other-page.md)`.

2. **Indexer CLI (`lliki-index`)**
   - Language: Rust (recommended) or Python.
   - Responsibilities:
     - Scan `lliki/` for `.md` files.
     - Parse frontmatter + links.
     - Build an in-memory graph:
       - Nodes: `{id, path, title, type, tags}`
       - Edges: `{from_id, to_id, relation}` where `relation` ∈ {`links`, `depends_on`, `refines`, `implements`}.
     - Serialize a compact index file (optional cache):
       - `index.json` or `index.bin` (nodes + edges).
     - Commands:
       - `lliki-index build --root ./lliki --out index.json`
       - `lliki-index update --root ./lliki --index index.json`

3. **Query Server / MCP (`lliki-mcp`)**
   - Runs as:
     - Local CLI: `lliki-query "find modules depending on battery-pack-design"`
     - MCP server for Claude Code / Cursor / other agents.
   - Loads `index.json` into memory at startup.
   - Exposes operations:
     - `list_nodes(filters: {type?, tags?}) -> [Node]`
     - `neighbors(id: string, relation?: string) -> [Node]`
     - `search(query: string, mode: "bm25" | "graph" | "hybrid") -> [Node]`
     - `get_files(ids: [string]) -> [path]`
   - Agents use this to:
     - Read `INDEX.md` (or call `list_nodes(type="index")`).
     - Query graph for relevant modules.
     - Get a minimal set of file paths to read.

4. **Agent Workflows**
   - **Ingest**:
     - On commit or manual run: `lliki-index update`.
     - Optionally run an LLM pass to:
       - Infer `depends_on`, `type`, and tags from content.
       - Detect contradictions/orphans.
   - **Query** (per task):
     - Agent reads `INDEX.md` (or calls `list_nodes(type="index")`).
     - Based on task, calls:
       - `neighbors("battery-pack-design", relation="depends_on")`
       - `search("thermal management for LFP", mode="hybrid")`
     - Receives a short list of file paths; reads only those.
   - **Lint**:
     - Periodic job:
       - Find nodes with no incoming/outgoing edges (orphans).
       - Detect broken links (edges to non-existent nodes).
       - Report conflicting metadata (e.g., same `id` with different types).

## Data Shapes

### Node
```json
{
  "id": "battery-pack-design",
  "path": "modules/battery-pack-design.md",
  "title": "Battery Pack Design",
  "type": "module",
  "tags": ["battery", "hardware"],
  "summary": "One-line description used in index."
}
```

### Edge
```json
{
  "from_id": "thermal-management",
  "to_id": "battery-pack-design",
  "relation": "depends_on"
}
```

### Index File (`index.json`)
```json
{
  "version": 1,
  "updated_at": "2026-09-09T17:53:00Z",
  "nodes": [ /* Node[] */ ],
  "edges": [ /* Edge[] */ ]
}
```

## Example Flows

### Task: “Add a new LFP cell profile”

1. Agent:
   - Calls `list_nodes(type="module", tags=["battery"])`.
   - Gets `battery-pack-design`, `cell-chemistry`, etc.
   - Calls `neighbors("battery-pack-design", relation="depends_on")`.
2. Receives: `cell-chemistry`, `thermal-management`.
3. Reads only:
   - `INDEX.md`
   - `modules/battery-pack-design.md`
   - `modules/cell-chemistry.md`
   - `modules/thermal-management.md`
4. Proposes changes to those files only.

### Task: “Explain how our pack design handles thermal issues”

1. Agent:
   - `search("thermal management pack design", mode="hybrid")`.
2. Gets ranked nodes: `thermal-management`, `battery-pack-design`, maybe `cell-chemistry`.
3. Reads only those files.

## Implementation Notes

- **Rust crates**:
  - `clap` for CLI.
  - `serde` + `serde_json` for data.
  - `petgraph` or custom adjacency lists for graph.
  - `regex` for Markdown link parsing.
- **Optional**:
  - Simple BM25: `tantivy` or `stopword` + custom scorer.
  - Vector search: integrate with local Ollama/embedding model if desired.
- **Deployment**:
  - Single binary: `lliki-agent-memory`.
  - Subcommands: `index`, `query`, `lint`.
  - MCP mode: `lliki-agent-memory mcp --index index.json`.

This keeps everything:
- Local (no cloud, no DB server).
- File-backed (Markdown is source of truth).
- Fast and token-efficient for LLM agents.


The “perfect” addition to **lliki** as a final product is a **lightweight, local agent-memory layer that turns your Markdown wiki into a typed, queryable knowledge graph without requiring an external database**. [github](https://github.com/zby/commonplace/blob/main/kb/agent-memory-systems/reviews/basic-memory.md)

In practice, that means adding three capabilities on top of your current Markdown-only setup:

## 1. Typed knowledge graph over Markdown (no DB)

Instead of treating lliki as just a folder of files, add a layer that:

- Parses each `.md` file’s **frontmatter** and **links** (`[[...]]`, `[...](...)`).
- Extracts **entities** (modules, concepts, decisions, playbooks) and **relations** (depends-on, refines, implements). [gist.github](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2)
- Builds an **in-memory graph** (e.g., with Rust or Python + NetworkX) that lives alongside the files. 

This graph is:

- **Local and file-backed**: Markdown remains the source of truth; the graph is a derived, ephemeral index. [github](https://github.com/zby/commonplace/blob/main/kb/agent-memory-systems/reviews/basic-memory.md)
- **Queryable**: Agents can ask “what modules depend on battery-pack-design?” and get a precise subgraph instead of scanning everything. [gist.github](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2)

## 2. Triple-stream retrieval: BM25 + vectors + graph

To make lliki genuinely useful for agents (and not just humans), add:

- **BM25 keyword search** over file contents.
- **Vector embeddings** for semantic search (optional, local models like Ollama).
- **Graph traversal** for entity-aware navigation. [gist.github](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2)

Combined, this gives you the same “triple-stream” pattern used by production agent-memory systems, but still **zero external DB** if you keep embeddings/graph in simple local files or in-memory structures. [aitoolly](https://aitoolly.com/product/agentmemory)

## 3. Agent workflows: ingest, query, lint

Wrap the above in three clear operations, exactly as in Karpathy’s LLM Wiki pattern:

- **Ingest**: When you add/update Markdown (or raw sources), a small CLI/agent:
  - Updates the index and graph incrementally.
  - Flags contradictions or outdated pages. [blog.starmorph](https://blog.starmorph.com/blog/karpathy-llm-wiki-knowledge-base-guide)
- **Query**: Agents (Claude Code, Cursor, etc.) use a CLI/MCP server to:
  - Read `INDEX.md` → query the graph → fetch only the relevant pages.
  - Avoid re-discovering the repo each task. [blog.starmorph](https://blog.starmorph.com/blog/karpathy-llm-wiki-knowledge-base-guide)
- **Lint**: Periodic health checks that:
  - Detect orphan pages, broken links, and conflicting statements.
  - Suggest merges or updates. [blog.starmorph](https://blog.starmorph.com/blog/karpathy-llm-wiki-knowledge-base-guide)

## What this turns lliki into

With these additions, lliki becomes:

- A **local-first, agent-operated knowledge base**: Markdown you own, plus a live graph your agents understand. [github](https://github.com/zby/commonplace/blob/main/kb/agent-memory-systems/reviews/basic-memory.md)
- A **token-efficient context engine**: Agents read a tiny index + targeted pages instead of exploring the whole repo. [particula](https://particula.tech/blog/karpathy-llm-wiki-compiled-knowledge-vs-rag)
- A **compounding artifact**: Knowledge accumulates and stays consistent over time, instead of being re-derived every session. [aaronfulkerson](https://aaronfulkerson.com/2026/04/12/karpathys-pattern-for-an-llm-wiki-in-production/)


## What it includes

A runnable, DB-free starter implementation --- It builds a JSON graph from Markdown frontmatter and links, then supports local CLI search and neighbor queries.


- **`lliki build <root> --out .lliki-index.json`**  
  Scans your Markdown wiki, parses frontmatter + links, and builds a JSON graph (nodes + edges). [gist.github](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2)

- **`lliki search "query" --index .lliki-index.json`**  
  Simple keyword search over titles, summaries, and tags.

- **`lliki neighbors <id> --relation depends_on --index .lliki-index.json`**  
  Returns directly connected nodes (e.g., modules a page depends on). [gist.github](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2)

## How to use

1. Unzip `lliki-agent-memory-python-mvp.zip` somewhere.
2. Inside that folder:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```
3. Point it at your wiki:
   ```bash
   lliki build /path/to/lliki --out .lliki-index.json
   lliki search "LFP thermal hardware" --index .lliki-index.json
   lliki neighbors battery-pack-design --relation depends_on --index .lliki-index.json
   ```

Markdown remains the source of truth; `.lliki-index.json` is just a disposable cache you can regenerate whenever the wiki changes. 

