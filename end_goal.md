# Pehance – End Goal and Product Direction (Updated July 2025)

Vision
- Help users get great results on the first try by transforming vague ideas into precision-crafted prompts.
- Make enhancement intelligent, proportionate, and safe using multi-model orchestration and anti-over-enhancement methodology.

Strategic pillars
1) Multi-model, intent-aware orchestration
- Primary reasoning: llama-3.3-70b-versatile
- Fast intent classification: llama-3.1-8b-instant
- Safety guardrails: meta-llama/llama-guard-4-12b
- Tiered fallbacks and specialized models (creative, advanced reasoning)
- Model availability endpoint to drive UI and decisions

2) Proportional enhancement (4D methodology)
- DECONSTRUCT → DIAGNOSE → DEVELOP → DELIVER
- Complexity scoring drives enhancement ratio and pathway (clarification/basic/standard/advanced)
- Single vs Multi modes: single returns final output; multi allows clarifications

3) Multimodal and formatting
- Text + image analysis to enrich prompts
- Response formatting layer (rich_text, code_blocks, markdown, plain_text, auto_detect)
- Content format detection to auto-tune how results are presented

4) Professional, accessible UX
- Clear model status, token/cost indicators, and progress visualization
- Accessibility: ARIA live regions, reduced-motion support, keyboard shortcuts
- Quick actions for output (Copy All, Copy as Markdown, Show/Hide code blocks)

5) Data and safety
- Client-side persistence for user preferences
- Server stores enhancement analytics (UUID-based) for improvements; API keys never stored server-side
- Safety guardrails enforced via dedicated safety model pathway

Near-term roadmap (execution track)
- Improve model board UX: collapsible tier groups, richer tooltips, color-blind–friendly palette
- Clarify mode toggle copy: concise descriptors + tooltips for single vs multi
- ImageUpload QoL: paste-from-clipboard in addition to drag & drop
- Performance: graceful handling of LLM rate limits; queueing indicators if needed
- Export: add “Export as Markdown/HTML” download buttons in output area

SDK/Sidecar architecture (parallel track)
- Goal: Real-time assistance wherever users write prompts (browser extension, API service, mobile keyboard)
- Shared core engine powered by the current backend’s agents and routing
- Features
  - Real-time intent detection and quality hints
  - Pattern-based suggestions grounded in aggregated successes
  - Model-aware parameter suggestions
- Privacy: keys remain client-side; server processes enhancement via user-provided or shared keys

Technical architecture (current → future)
- Current stack
  - Frontend: React app (CRA + CRACO + Tailwind)
  - Backend: FastAPI 0.110.x on 0.0.0.0:8001, supervised by supervisor
  - Database: MongoDB via MONGO_URL and DB_NAME
  - Ingress: all backend routes must be prefixed with /api
- Future options (non-breaking migration path)
  - Optional migration of frontend to Next.js with incremental adoption (keeps API contracts unchanged)
  - Add serverless adapters for burst traffic and long-running tasks if needed

Data model & analytics (direction)
- Store prompt enhancement sessions with:
  - id (UUID), original_prompt, enhanced_prompt, mode, enhancement_type, enhancement_ratio, complexity_score, models_used, timestamps
  - multimodal flags and image analysis metadata when applicable
- Token/cost analytics
  - Per-call token estimates (input/output), processing time, model speed
  - Trends over sessions for users (client-side visualizations)

Quality validation
- Automatic sanity checks on response structure
- Anti-over-enhancement guardrails: low-complexity inputs route to clarification/basic enhancement
- User feedback hooks (up/down) planned for prioritization

Business model (direction)
- Freemium: limited daily enhancements; Pro unlocks unlimited + advanced features
- Cost transparency via token analytics and model selection guidance
- Team features later (shared templates, curated best practices)

Deployment strategy (pragmatic)
- Current: running inside Kubernetes with supervisor managing services
- Optional: future microfrontends/Next.js on Vercel for the web UI while keeping backend/API stable

Success metrics
- Enhancement quality: reduced iterations to acceptable results
- Time-to-first-value: seconds to enhanced output across common tasks
- Reliability: % of requests completed within target SLO under rate limiting
- Safety: % of unsafe inputs properly handled by guardrails

Notes
- Do not change protected environment variables or routing rules
- Maintain /api prefix for all backend routes; frontend uses REACT_APP_BACKEND_URL
- Prefer UUIDs in payloads; avoid Mongo ObjectIDs in API responses