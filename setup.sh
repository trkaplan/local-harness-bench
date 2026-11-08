#!/usr/bin/env bash
# Clone and build the four harnesses at the pinned revisions used in the benchmark. Needs node 22+, npm, bun, pnpm, uv.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd); mkdir -p "$ROOT/src"; cd "$ROOT/src"
[ -d pi ] || git clone --depth 1 --branch v1.5.0 https://github.com/earendil-works/pi.git
(cd pi && npm install --ignore-scripts && npm run hydrate:model-data && npm run build:offline)
[ -d opencode ] || git clone --depth 1 --branch v2.2.6 https://github.com/anomalyco/opencode.git
(cd opencode && bun install && cd packages/cli && bun run build --single)
[ -d mini-swe-agent ] || git clone --depth 1 --branch v2.4.6 https://github.com/SWE-agent/mini-swe-agent.git
(cd mini-swe-agent && uv venv && uv pip install -e . mcp)
[ -d deepseek-harness ] || { git clone https://github.com/deepseek-ai/deepseek-harness.git && (cd deepseek-harness && git checkout fcc0ad4); }
(cd deepseek-harness && pnpm install --frozen-lockfile && pnpm run build)
cd "$ROOT/tasks" && uv venv .venv && uv pip install --python .venv/bin/python pytest
echo "done. Point OMLX_URL / OMLX_LOG at your server if it is not oMLX on 127.0.0.1:8018, then: bin/run-one.sh pi a-bugfix 1"
