Surveyed: 2026-11-03
Next due: 2026-12-01

# Tools for Claude worth using in ReaderWrangler — survey

_Skills, plugins, tool servers and agent-driven CLI tools appear faster than Claude's training data keeps up with, so
this survey is re-run every 4 weeks (Ron, 2026-11-03). The two lines above are the reminder's only state: the
`survey-check.py` hook (local tooling) raises a refresh once "Next due" is reached; `/tool-survey` re-runs it; "not now"
moves "Next due". Installing anything is Ron's call — read it and pin an exact version first._

**First run, 2026-11-03** — written by a research agent; Claude spot-checked the key claims against primary sources:
Playwright's own advice to prefer its command-line tool over its tool server for coding agents (consistent across
sources), the `page.screencast` video recording added in 1.59 (its release notes), Chrome DevTools MCP's two privacy
switches (its official repo), and Earshot (its repo: ~3.8k stars, version 0.4, MIT, Gemini upload only with your own
key plus `--yes-upload`, ~1.1 GB of models on first use; its creation date isn't shown there — UNVERIFIED). Anything
the agent couldn't confirm is marked UNVERIFIED below.

---


# Tools that extend Claude Code: a survey for ReaderWrangler

## Summary: top recommendations

1. **Browser driver: Playwright CLI + its skills** (`@playwright/cli` 0.1.23, Microsoft). It covers real clicks, drags, keys and hover, plus screenshots, traces and **video** (`video-start`, chapters, action overlays). Microsoft now recommends it over its own Playwright MCP for coding agents because it uses fewer tokens. **USE NOW.**
2. **Scripted video takes: Playwright (Python) 1.64.1 `page.screencast`.** It records WebM with chapter cards, HTML overlays, an animated cursor and an fps setting, and it can drive the installed Edge (`channel="msedge"`). This is the cleanest way to make sizzle-reel takes, and it runs in Python. **USE WHEN** shooting the reel.
3. **Accessibility: axe-core 4.14 through `@axe-core/playwright`**, run from the same driver. It is local, free and open source (MPL-2.0), and finds about 57% of WCAG issues automatically by the vendor's own claim. Keyboard focus order still needs scripted Tab walks plus screenshots. **USE NOW** as part of the driver.
4. **Code quality on the 20k-line file:** ESLint 10.14 with `no-use-before-define` + `eslint-plugin-react-hooks` 7.1.1, run from the commit hooks. This catches the "name read before it's declared" class from TODO e0e3c05. Add the official **typescript-lsp** plugin so the agent gets go-to-definition and find-references in a 20k-line file. **USE NOW.**
5. **Video assembly: Remotion 4.0.540 + its official skills, or plain FFmpeg 9.0.2.** Remotion is free for individuals. A local CLI render sends no telemetry unless a license key is set, but browser-side rendering always reports. **Earshot** (sound timing, CPU-only) is three weeks old with hype-level stars, so vet it and pin a commit. **USE WHEN** making the reel.
6. **Chrome DevTools MCP 1.12.0** adds Lighthouse audits, performance traces and a screencast. Google usage statistics are **on by default**, and performance tools send URLs to the CrUX API. Start it with `--no-usage-statistics --no-performance-crux`. **USE WHEN** working on load-time or performance.
7. **Cloudflare's official `cloudflare/skills`** (wrangler, workers-best-practices, durable-objects…) plus the local Workers Vitest plugin. Take the skills, not the remote account MCP. Turn off Wrangler telemetry. **USE WHEN** doing the relay worker release.
8. **One caution applies to every agent tool:** whatever the agent sees (screenshots, page snapshots, console output) goes to Anthropic as part of the conversation. Drive the app only with the **demo library**, never Ron's real library or an amazon.com tab.

---

## 1. Browser automation and testing an agent can drive

| Tool | What it does | Maturity | License | Data off the PC | Windows footprint | Verdict |
|---|---|---|---|---|---|---|
| **Playwright CLI + skills**: https://github.com/microsoft/playwright-cli (npm `@playwright/cli`) | A shell command set (`open`, `click`, `drag`, `hover`, `press`, `mousemove/down/up/wheel`, `snapshot`, `screenshot --hires`, `pdf`, `tracing-start/stop`, `video-start --cursor --fps=60`, `video-chapter`, `video-show-actions`, `video-stop`, `recording-start` to write Playwright code). `playwright-cli install --skills` drops a SKILL.md (plus a video-recording guide) into `.claude/skills`. `show` opens a dashboard where you can watch or take over a background session. | npm package first published 2026-01-26; latest **0.1.23 (2026-10-31)**; repo ~14.9k stars, pushed today. Still 0.x. | Apache-2.0 | No telemetry is documented. Snapshots and screenshots go to the model you use. Browsers download from Microsoft's CDN unless you use installed Edge or Chrome. | Node 18+, a global npm install, browser binaries (or the installed Edge/Chrome channel). Headless by default, `--headed` to watch; named sessions; profiles live in memory unless `--persistent`. | **USE NOW**: the "browser driver" in the order of work. It uses fewer tokens than MCP, records video, and drag/hover/keys are first-class. Pin the exact version. |
| **Playwright library (Python)**: https://playwright.dev/python/docs/api/class-screencast (PyPI `playwright`) | The full scripting library. `page.screencast.start(path, size, fps)` plus `show_chapter`, `show_overlay(html)` and `show_actions(cursor=…, style=…)` produce narrated, annotated WebM takes. `recordVideo` and tracing are also available. | Screencast API added in **v1.59 (Apr 2026)**; fps and style in v1.64; latest **1.64.1 (14 Oct 2026)**; v1.64 switched video to VP9 and is tested against Edge 155. Very mature project. | Apache-2.0 | No telemetry is documented. | `pip install playwright==1.64.1`; `playwright install` or use `channel="msedge"`. | **USE WHEN** shooting sizzle-reel takes or writing repeatable test scripts. It is Python (Ron's preference) and deterministic: the scripted take is the source of truth, not the agent's improvisation. |
| **Playwright MCP**: https://github.com/microsoft/playwright-mcp | The same engine exposed as MCP tools, driven by accessibility snapshots. Opt-in `--caps=devtools` adds `browser_start_video/stop_video`, tracing, chapters and overlays; `vision` adds coordinate mouse; `pdf` adds PDF save. | Since Mar 2025; **v0.0.84 (31 Oct 2026)**; ~39k stars. | Apache-2.0 | No telemetry is documented. The README says it "is **not** a security boundary". | `claude mcp add playwright npx @playwright/mcp@<pinned>` | **SKIP** while the CLI exists. Its own README now recommends the CLI for coding agents. Keep it as a fallback if the CLI skill misbehaves. |
| **Chrome DevTools MCP**: https://github.com/ChromeDevTools/chrome-devtools-mcp | Google's agent bridge to a live Chrome. 10 input tools (click, drag, hover, press_key, type_text, fill_form, upload_file…), screenshot/snapshot, console with source-mapped stacks, network, performance traces with insights, **`lighthouse_audit`**, and **`screencast_start/stop`** (built in, no ffmpeg needed, since v1.11). Also available as a CLI and as a Claude Code plugin. | Since Sep 2025; **v1.12.0 (22 Oct 2026)**; ~54.7k stars; very active. | Apache-2.0 | **Yes, by default.** Google usage statistics are on (`--no-usage-statistics` or `CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS`). Performance tools send trace URLs to Google's CrUX API (`--no-performance-crux`). An npm update check runs (`CHROME_DEVTOOLS_MCP_NO_UPDATE_CHECKS`). | Node LTS + npm + stable Chrome. | **USE WHEN** chasing load-time or performance (the "faster loading" TODO) or running a Lighthouse pass. Always start it with the opt-out flags. Use Playwright for everyday driving. |
| **Claude in Chrome** (`claude --chrome`): https://code.claude.com/docs/en/chrome | Anthropic's extension. It acts in Ron's **real** Chrome or Edge profile with his sign-ins: clicks, typing, console reading, GIF recording, screenshots to disk. | Shipping; extension 1.0.36+; Windows supported (named-pipe caveats). | Proprietary (Anthropic) | It goes through Anthropic's bridge (`bridge.claudeusercontent.com`). Recordings capture everything visible, including signed-in account details. | Browser extension + native messaging host. | **SKIP for RW testing.** It shares the profile that is signed in to Amazon and holds the real library, which conflicts with the privacy rules. Fine for one-off non-RW web chores. |
| **agent-browser** (Vercel Labs): https://github.com/vercel-labs/agent-browser | A Rust CLI over the Chrome DevTools Protocol with compact `@e1`-style element refs, plus `screenshot` and `record` commands. Native Windows x64 binary. | ~45k stars, 790 commits; release dates not shown; recording details and telemetry **UNVERIFIED** (README is silent). | Apache-2.0 | Telemetry not mentioned; optional cloud-browser providers. | npm + downloads Chrome for Testing. | **WATCH**: it overlaps Playwright CLI and adds nothing RW needs. The star count reads like hype relative to its documentation. |
| **Anthropic `webapp-testing` skill**: https://github.com/anthropics/skills/tree/main/skills/webapp-testing | Teaches Claude to write Python Playwright scripts (reconnaissance first, then action) plus a `with_server.py` helper that starts and stops your dev server around a test. | In the official skills repo (~187k stars repo-wide). | Apache-2.0 (per-skill LICENSE.txt) | None beyond the model. | Python Playwright. | **SKIP as a dependency**. The Playwright CLI skill supersedes it. The `with_server.py` pattern is worth copying into RW's driver: start `serve.py`, run, tear down. |

**Notes**
- "CLI killed MCP" posts are mostly an echo of Microsoft's own token-cost argument. The argument is sound for coding agents, but MCP still suits long exploratory sessions.
- For the Delete-key fix (TODO "The Delete key deletes the folder you're in…"), Playwright gives real `keydown`/`keyup` events. Synthetic `dispatchEvent` would not reproduce the actual browser key path.

## 2. Video assembly and sound (20–30 s sizzle reel)

| Tool | What it does | Maturity | License | Data off the PC | Windows footprint | Verdict |
|---|---|---|---|---|---|---|
| **Remotion** + **Remotion Agent Skills**: https://www.remotion.dev/docs/ai/skills (skills in `remotion-dev/remotion/packages/skills`) | Video written as React components and rendered to MP4. The skills (`/remotion-best-practices`, plus render, captions and Mediabunny media skills…) teach Claude the framework. Install: `npx skills add remotion-dev/skills`. | Mature (v4 line); **4.0.540, published ~2026-11-02** (npm). License "will change in Remotion 5.0" (details not published). | Remotion License: **free for individuals**, non-profits, and for-profits with ≤3 employees; others need a paid Company License. | **CLI/server-side rendering sends telemetry only when a `licenseKey` is set. Client-side (in-browser) rendering always sends events** (IP, still/video, domain). No video content is sent, per its docs. | Node + npm project, plus a headless Chrome Remotion downloads. Heavyweight for 25 s. | **USE WHEN** the reel needs animated titles, zooms or captions over the Playwright takes. Render with the CLI and no key. Fits RW's React skills. For a simple cut, FFmpeg alone may be enough, so decide after the takes exist. |
| **FFmpeg 9.0.2** ("Lei", 2026-09-18): https://ffmpeg.org/download.html; Windows builds from https://www.gyan.dev/ffmpeg/builds/ or BtbN | Trimming, concatenating, crossfades, the WebM→MP4 conversion (the Playwright guide doesn't cover it), music ducking, burned-in captions (libass). Claude drives it well with no extra skill. | Decades mature. | LGPL/GPL (build-dependent) | None. | A single folder of exes on PATH. Needed by Earshot and whisper.cpp anyway. | **USE WHEN** assembling the reel. Pin a specific gyan.dev release build, not "git master". |
| **claude-code-video-toolkit** (Digital Samba): https://github.com/digitalsamba/claude-code-video-toolkit | A Claude Code workspace: Remotion + FFmpeg + Playwright-recording + MoviePy skills, `/video`, `/record-demo`, `/generate-voiceover` commands, templates (product-demo…). | Created 2025-12-09; ~2.4k stars; pushed today; no tagged releases. | MIT | **Leans on cloud**: ElevenLabs (voice and music), Modal/RunPod cloud GPU tools, R2, YouTube upload. A no-key local hello-world render works. | Node 22+, uv/Python, optional FFmpeg. | **WATCH / borrow ideas** (its product-demo template and `/record-demo` flow). Don't adopt it wholesale: it is cloud-first, and RW needs one 25 s reel, not a pipeline. (The similarly named `wilwaldon/Claude-Code-Video-Toolkit` is only a link list.) |
| **Earshot**: https://github.com/Leonxlnx/earshot | "Ears for coding agents": a CLI, Python API and MCP server that describes and ranks audio (local CLAP + AST AudioSet models, loudness/timing/spectra), checks sound against video timing, and makes SFX from code (`forge`) or from a shipped bank of 252 sounds (`sfx`, `kit`). | **Created 2026-10-15**; v0.4.0 on 2026-10-22; 40 commits; ~3.75k stars in under 3 weeks (hype signal); last push 2026-10-22. | MIT code; CLAP Apache-2.0, AST BSD-3. License of the shipped sound bank **UNVERIFIED**. | Local by default. **The `llm` command uploads audio to Google Gemini**, but only with your own key **and** `--yes-upload`. The first run downloads ~1.1 GB of models from Hugging Face; `EARSHOT_OFFLINE=1` afterwards. | git clone + venv + CPU PyTorch + ffmpeg; ~1.1 GB model cache. Windows paths shown in its docs but not explicitly claimed as supported. | **USE WHEN** syncing music hits to cuts, as the TODO note already plans. Vet it first, pin a commit hash, never set a Gemini key. It is young enough that it could stall. |
| **whisper.cpp**: https://github.com/ggml-org/whisper.cpp (or via Remotion's `@remotion/install-whisper-cpp`) | Local speech-to-text with experimental word timestamps (`-ml 1`). Remotion's wrapper turns the output into a `captions.json` for animated captions. | ~54.9k stars; **v1.9.5 (6 Oct 2026)**. Windows prebuilt x64 zip **UNVERIFIED** (assets not visible); building with MSVC is supported. | MIT | None (models download once). | Small binary + a model file. | **USE WHEN** the reel has a voice-over. A music-only reel with typed titles needs no transcription, so this is likely **not needed**. |
| **faster-whisper**: https://github.com/SYSTRAN/faster-whisper | A Python Whisper with `word_timestamps=True`; its GPU path needs CUDA/cuDNN. | ~26.5k stars. | MIT | Model download from Hugging Face on first run. | Python + CTranslate2. | **SKIP**: whisper.cpp (or nothing) covers RW's needs. |
| **Music and SFX sources**: Pixabay https://pixabay.com/service/license-summary/ and Freesound https://freesound.org/help/faq/ | Pixabay: free commercial use, no attribution required; can't redistribute stand-alone or use in trademarks. Freesound: a per-sound **CC0 / CC-BY / CC-BY-NC** license with a search filter. | — | As stated per item. | Download only. | — | **USE WHEN**. Prefer **Freesound CC0** (or CC-BY with a credits line) and record each track's URL and license in the repo. On Pixabay, YouTube Content ID false-claims on its music are a commonly reported nuisance (**UNVERIFIED**; the license summary doesn't address it). Avoid CC-BY-NC. |

## 3. Accessibility checking an agent can run

| Tool | What it does | Maturity | License | Data off the PC | Footprint | Verdict |
|---|---|---|---|---|---|---|
| **axe-core 4.14.0** + **`@axe-core/playwright` 4.14.0**: https://github.com/dequelabs/axe-core | A rules engine injected into the page: contrast, names/labels, ARIA, landmarks. Reports "incomplete" items for manual review. Its own claim: finds "on average 57% of WCAG issues". | Industry standard; 4.14.0 released 5 Oct 2026; ~7.7k stars. | MPL-2.0 | None documented; runs in the page. | Small npm packages, or inject the axe.min.js file from Python Playwright. | **USE NOW**. Add an "axe pass" to the browser driver over each main screen and dialog: library, book dialog, menus, Relay Setup, phone view. |
| **Keyboard-focus checks (scripted with Playwright)** | Tab/Shift+Tab walks that screenshot focus rings and assert focus order and Esc behavior. This fits the overlay system's Esc and fence rules. | — | — | None. | — | **USE NOW**. No tool automates focus order well (axe and Lighthouse both leave it to manual review), so script it. |
| **Lighthouse 13.6.0** (2026-10-27): https://github.com/GoogleChrome/lighthouse | Accessibility, performance and best-practice scores. Its accessibility audits are weighted by axe impact and link to axe-core 4.11 rules (axe underneath). Reachable as `lighthouse_audit` in Chrome DevTools MCP or as its own CLI. | Very mature. | Apache-2.0 | The CLI has an opt-in `--enable-error-reporting` flag (error reporting is off in the Node module). Details of what it sends are **UNVERIFIED**. | npm CLI, or none if used through DevTools MCP. | **USE WHEN** doing performance or a pre-launch audit. For accessibility it mostly repeats axe, but gives a score Ron can track. |
| **Deque Axe MCP Server**: https://www.deque.com/blog/axe-devtools-for-web-now-includes-axe-mcp-server-for-earlier-fixes-and-faster-delivery/ | An agent tool that tests, suggests and validates fixes through "a direct connection to the Axe Platform". | GA Feb 2026 (vendor post). | Commercial; part of the paid Axe DevTools for Web bundle. | Connects to Deque's platform; what is sent is **UNVERIFIED**. | — | **SKIP**: paid, cloud-tied, and free axe-core covers RW. |

## 4. Screenshots and user-guide generation

| Tool | What it does | Verdict |
|---|---|---|
| **Playwright** (CLI `screenshot --hires`, or a Python script) + **`screencast.show_overlay(html)`** / injected CSS callouts | Element or full-page shots at 2× scale. Annotate by injecting an overlay (arrows, numbered badges, a highlight ring) before the shot, which keeps annotations in code and re-shootable each release. `playwright-cli show --annotate` is a human UI-review mode. | **USE WHEN** writing the user guide. Keep one Python "shot list" script so every guide image regenerates from the demo library after UI changes. This is the mechanism that keeps docs from going stale. |
| **shot-scraper**: https://github.com/simonw/shot-scraper (Apache-2.0, ~2.6k stars) | A Playwright-based screenshot CLI: `--javascript` before the shot, `--selector` + `--padding` crops, `--retina`, multi-shot files, video recording. | **SKIP**: it is a thin layer over Playwright, which RW will already have. It would be useful only if a no-code YAML shot list were wanted. |
| **Chrome DevTools MCP** `take_screenshot` / **Claude in Chrome** saves screenshots to disk | Ad-hoc screenshots. | Ad-hoc only; not reproducible enough for a guide. |

## 5. Code quality on a 20k-line single JS file

| Tool | What it does | Maturity | License | Data off the PC | Verdict |
|---|---|---|---|---|---|
| **ESLint 10.14.0** (2026-10-30): https://eslint.org, rule **`no-use-before-define`** https://eslint.org/docs/latest/rules/no-use-before-define | Flags same-scope `let`/`const` reads before declaration (the temporal dead zone). Per the rule's definition this covers a hook dependency array that names a later `const`, but test that case on RW's file first: the docs don't show it. Also `no-undef` and `no-unused-vars` for dead locals. | Very mature. | MIT | None. | **USE NOW** as a commit-hook check (the chokepoint for TODO e0e3c05). Needs a JSX parser config; RW already installs `@babel/core` + `@babel/preset-react` for check-names. Expect a large first-run backlog, so use a ratchet (no new warnings) rather than fixing all at once. |
| **`eslint-plugin-react-hooks` 7.1.1**: https://www.npmjs.com/package/eslint-plugin-react-hooks | `rules-of-hooks`, `exhaustive-deps`, and (in recent majors) React Compiler-derived rules. | Official React team. | MIT | None. | **USE NOW**, alongside ESLint. The compiler-derived rules' exact names in 7.x are **UNVERIFIED**; check the README when pinning. |
| **ESLint MCP** (`@eslint/mcp`): https://eslint.org/docs/latest/use/mcp | Lets the agent lint and explain via MCP. The docs cover VS Code, Cursor and Windsurf only, not Claude Code. | Official. | MIT | None. | **SKIP**: Claude can run `npx eslint` directly, and the commit hook is the real enforcement. |
| **typescript-lsp plugin** (official): https://github.com/anthropics/claude-plugins-official/tree/main/plugins/typescript-lsp | Gives Claude Code go-to-definition, find-references and diagnostics for `.js/.jsx/.ts`. | In Anthropic's official plugin directory. | Apache-2.0 | None. | **USE NOW**. In a 20k-line file, find-references beats grep for "who calls this". Needs `npm i -g typescript-language-server typescript` (pin versions). |
| **ast-grep 0.51.1** (2026-11-02): https://github.com/ast-grep/ast-grep, plus the experimental **ast-grep MCP** https://github.com/ast-grep/ast-grep-mcp | Structural search and rewrite by syntax pattern (e.g. "every `useEffect` whose deps include X", "every `setState` call inside handler Y"). The MCP adds `find_code`, `find_code_by_rule`, `dump_syntax_tree`. | CLI mature; MCP labeled "experimental", ~486 stars. | MIT | None. | **USE WHEN** lifting pieces out of the giant component (the seam map in commit a03450e) or doing class-of-sites combs. It makes `/sitemap`'s "two pivots" more mechanical than grep. Use the CLI; skip the MCP. |
| **code-modernization plugin** (official): https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-modernization | Assess, map, extract business rules, approve a brief, then rebuild module by module with a per-module verdict. Never edits the original source. | Official. | Apache-2.0 | None beyond the model. **Some steps start dozens to hundreds of agents** (its README). | **WATCH**: built for legacy-system migrations. Its `modernize-map` might help draw seams, but the cost is out of proportion for "lift pieces out as work touches them". |
| **knip**: https://github.com/webpro-nl/knip | Finds unused files, exports and dependencies (has `@knip/mcp`). | ~12.6k stars. | ISC | None. | **SKIP for now**: RW has no exports or modules graph to prune. Revisit after the build step and module split. |

## 6. Cloudflare Workers, bookmarklets and extensions

| Tool | What it does | License | Data off the PC | Verdict |
|---|---|---|---|---|
| **Cloudflare Skills** (official): https://github.com/cloudflare/skills | 19 skills (wrangler, workers-best-practices, workers-profiling, durable-objects, web-perf…). The Claude Code plugin (`/plugin marketplace add cloudflare/skills`) **also registers Cloudflare's remote API MCP server**. ~3.3k stars. | Apache-2.0 | The skills are local text. The bundled MCP server talks to Cloudflare's API on your account (OAuth). | **USE WHEN** doing "Relay worker: one release of changes". Install the `wrangler` and `workers-best-practices` skills by copying folders or `npx skills add`, not the plugin with its account MCP, so deploys stay Ron's manual, asked-each-time step. |
| **Workers Vitest plugin** (`@cloudflare/vitest-plugin`, successor to `vitest-pool-workers`): https://developers.cloudflare.com/workers/testing/vitest-integration/ | Runs tests inside the Workers runtime locally (Miniflare), with isolated storage per test file. | MIT/Apache (workers-sdk) | None (local). | **USE WHEN** in the relay release. It would let the nightly-cleanup and signed-write rules be tested locally against KV instead of on the dev relay. KV-specific details are **UNVERIFIED** from that page. |
| **Wrangler telemetry**: https://github.com/cloudflare/workers-sdk/blob/main/packages/wrangler/telemetry.md | Wrangler sends usage metrics (command, OS, whether an AI agent ran it, IP). | — | **Yes, apparently on by default.** | Opt out once: `npx wrangler telemetry disable`, or `WRANGLER_SEND_METRICS=false` / `DO_NOT_TRACK=1`. |
| **Cloudflare MCP servers**: https://github.com/cloudflare/mcp-server-cloudflare | Hosted MCPs (API, docs, browser rendering…). Many older ones (bindings, observability, builds) are now marked deprecated in favor of the single API server. | Apache-2.0 | Remote, on Cloudflare. | **SKIP**, except perhaps the docs server (`docs.mcp.cloudflare.com`), which sends only search queries. |
| **Bookmarklets / extensions** | Nothing notable found that targets bookmarklets specifically. Playwright can test the fetcher's parsing against **saved, private local fixture pages** (kept with the TODO notes, never in the repo), never live amazon.com. | — | — | No new tool needed. Note it for the fetcher tests. |

## 7. Official Anthropic skills and plugins a solo developer might miss

Sources: https://github.com/anthropics/skills (19 skills) and https://github.com/anthropics/claude-plugins-official (~40 first-party plugins under `/plugins`).

| Item | What it does | Data off the PC | Verdict |
|---|---|---|---|
| **typescript-lsp** | See section 5. | None | **USE NOW** |
| **hookify** | `/hookify <rule>` (or with no argument, it proposes rules from what you corrected in the conversation). It writes markdown rules (`.claude/hookify.<name>.local.md`) that warn on or block bash, file edits, prompts or stop events. | None | **WATCH**. RW already has hand-built hooks with a single-source checklist. Hookify could be a quick way to try a new rule before writing a real hook, but don't run both systems for the same rule. |
| **security-guidance** | Three layers: regex warnings on ~25 risky patterns (raw `innerHTML`, hardcoded secrets…), an **LLM review of every turn's diff** (Stop hook), and an agentic review on `git commit`. Each layer has an off switch. | Diffs go to your configured model endpoint, the same place as normal use. | **USE WHEN** the relay or crypto work is active, perhaps with only the pattern rules on (`ENABLE_CODE_SECURITY_REVIEW=0`). The per-turn LLM review costs usage on every turn. |
| **claude-md-management** | `claude-md-improver` audits CLAUDE.md against the code; `/revise-claude-md` captures session lessons into it. | None | **WATCH**. RW's PM → PRINCIPLES → memory pipeline is more deliberate. An occasional audit could catch stale CLAUDE.md lines. |
| **frontend-design** (skill and plugin), **skill-creator**, **mcp-builder**, **webapp-testing** | Design guidance for UI, a skill authoring and eval kit, an MCP-server scaffolder, a Playwright testing skill. | None | skill-creator is already available in this session. frontend-design is **WATCH** (RW's look is settled). webapp-testing: see section 1. |
| **Built-ins already present**: `/code-review`, `/simplify`, `/security-review`, `/sitemap` (RW's own) | — | — | Already available. No install needed. |

---

## Sources

- https://github.com/microsoft/playwright-mcp
- https://github.com/microsoft/playwright-mcp/releases
- https://api.github.com/repos/microsoft/playwright-mcp
- https://github.com/microsoft/playwright-cli
- https://api.github.com/repos/microsoft/playwright-cli
- https://registry.npmjs.org/@playwright/cli
- https://playwright.dev/agent-cli/skills
- https://raw.githubusercontent.com/microsoft/playwright-cli/main/skills/playwright-cli/references/video-recording.md
- https://github.com/microsoft/playwright/releases
- https://playwright.dev/docs/api/class-screencast
- https://playwright.dev/python/docs/api/class-screencast
- https://pypi.org/pypi/playwright/json
- https://github.com/ChromeDevTools/chrome-devtools-mcp
- https://github.com/ChromeDevTools/chrome-devtools-mcp/releases
- https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/tool-reference.md
- https://api.github.com/repos/ChromeDevTools/chrome-devtools-mcp
- https://code.claude.com/docs/en/chrome
- https://github.com/vercel-labs/agent-browser
- https://raw.githubusercontent.com/vercel-labs/agent-browser/main/README.md
- https://github.com/anthropics/skills
- https://github.com/anthropics/skills/tree/main/skills
- https://raw.githubusercontent.com/anthropics/skills/main/skills/webapp-testing/SKILL.md
- https://github.com/anthropics/claude-plugins-official
- https://github.com/anthropics/claude-plugins-official/tree/main/plugins
- https://github.com/anthropics/claude-plugins-official/tree/main/plugins/typescript-lsp
- https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-modernization
- https://github.com/anthropics/claude-plugins-official/tree/main/plugins/security-guidance
- https://github.com/anthropics/claude-plugins-official/tree/main/plugins/hookify
- https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-md-management
- https://www.remotion.dev/docs/ai/skills
- https://github.com/remotion-dev/remotion/blob/main/LICENSE.md
- https://github.com/remotion-dev/remotion/releases
- https://registry.npmjs.org/remotion/latest
- https://www.remotion.dev/docs/telemetry
- https://www.remotion.dev/docs/install-whisper-cpp/
- https://github.com/digitalsamba/claude-code-video-toolkit
- https://api.github.com/repos/digitalsamba/claude-code-video-toolkit
- https://github.com/Leonxlnx/earshot
- https://github.com/Leonxlnx/earshot/commits/main
- https://api.github.com/repos/Leonxlnx/earshot
- https://github.com/ggml-org/whisper.cpp
- https://github.com/ggml-org/whisper.cpp/releases
- https://github.com/SYSTRAN/faster-whisper
- https://ffmpeg.org/download.html
- https://pixabay.com/service/license-summary/
- https://freesound.org/help/faq/
- https://github.com/dequelabs/axe-core
- https://github.com/dequelabs/axe-core/releases
- https://registry.npmjs.org/@axe-core/playwright/latest
- https://github.com/GoogleChrome/lighthouse/releases
- https://github.com/GoogleChrome/lighthouse/blob/main/docs/readme.md
- https://developer.chrome.com/docs/lighthouse/accessibility/scoring
- https://www.deque.com/blog/axe-devtools-for-web-now-includes-axe-mcp-server-for-earlier-fixes-and-faster-delivery/
- https://github.com/simonw/shot-scraper
- https://shot-scraper.datasette.io/en/stable/screenshots.html
- https://eslint.org/docs/latest/use/mcp
- https://eslint.org/docs/latest/rules/no-use-before-define
- https://github.com/eslint/eslint/releases
- https://registry.npmjs.org/eslint-plugin-react-hooks/latest
- https://github.com/ast-grep/ast-grep-mcp
- https://github.com/ast-grep/ast-grep/releases
- https://github.com/webpro-nl/knip
- https://github.com/cloudflare/skills
- https://developers.cloudflare.com/workers/testing/vitest-integration/
- https://github.com/cloudflare/workers-sdk/blob/main/packages/wrangler/telemetry.md
- https://github.com/cloudflare/mcp-server-cloudflare
