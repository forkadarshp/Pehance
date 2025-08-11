# Pehance – Current Setup (July 2025)

This document captures the live, production setup of Pehance in this environment. It reflects the working codebase (React frontend + FastAPI backend + MongoDB) and the multi‑model, multi‑agent enhancement pipeline currently deployed under supervisor in Kubernetes.

Summary of capabilities
- Multi-model orchestration with intent-aware routing
  - Primary reasoning model: llama-3.3-70b-versatile
  - Fast classifier model: llama-3.1-8b-instant (simple intents)
  - Safety guardrails: meta-llama/llama-guard-4-12b
  - Additional specialized/alternate models per tier with availability checks
- Anti-over-enhancement 4D methodology
  - Deconstruct → Diagnose → Develop → Deliver with complexity scoring and proportional enhancement
  - Single mode: always returns an enhanced prompt (no follow-ups)
  - Multi mode: allows conversational clarifications when needed
- Endpoints for text and multimodal
  - /api/enhance (text)
  - /api/enhance-multimodal (text + image)
  - /api/process-image (image analysis)
  - /api/format-response (rich_text, code_blocks, markdown, plain_text, auto_detect)
  - /api/detect-format (format detection)
  - /api/test-models (model availability + tier summary)
- Professional UI and UX
  - Theme toggle, model preference selector, cost/token bar, model status board, processing status, enhanced output display
  - New quick actions: Copy All, Copy as Markdown, Show/Hide code blocks
  - Accessibility improvements and reduced-motion support

Architecture & routing
- Services
  - Frontend: React app (Create React App + CRACO + Tailwind CSS), served via supervisor
  - Backend: FastAPI on 0.0.0.0:8001 (do not change), served via supervisor
  - Database: MongoDB, accessed from backend via MONGO_URL
- Kubernetes ingress rules
  - All backend API routes must be prefixed with /api
  - Frontend routes (no /api prefix) resolve to port 3000
- Environment variables (do not change existing .env)
  - Frontend/.env
    - REACT_APP_BACKEND_URL = External URL used by the frontend for all API calls (must include /api in requests)
  - Backend/.env
    - MONGO_URL = Mongo connection string
    - DB_NAME = Mongo database name
    - GROQ_API_KEY = Key for Groq model access

Directory layout
- /app/backend: FastAPI app
- /app/frontend: React app
- /app/test_result.md: Central testing state and protocol

Install dependencies
- Backend: pip install -r /app/backend/requirements.txt
- Frontend: cd /app/frontend && yarn install --frozen-lockfile

Service control (supervisor)
- Restart all: sudo supervisorctl restart all
- Restart backend only: sudo supervisorctl restart backend
- Restart frontend only: sudo supervisorctl restart frontend
- Check status: sudo supervisorctl status

Logs
- Backend: tail -n 200 /var/log/supervisor/backend.err.log
- Frontend: tail -n 200 /var/log/supervisor/frontend.err.log

Critical URL rules
- Never hardcode backend URLs or ports in code
- Frontend must use process.env.REACT_APP_BACKEND_URL
- Backend must use os.environ.get('MONGO_URL') and DB_NAME for DB access
- All backend routes must start with /api

API overview (contracts)
- GET /api/
  - Returns { message: "Hello World" }
- POST /api/status → { client_name } → 200 with { id, client_name, timestamp }
- GET /api/status → 200 with list of status checks
- GET /api/test-models → 200 with { success, models, summary, timestamp }
- POST /api/enhance → { prompt: string, mode: "single"|"multi", preferred_format?: string }
  - 400 if prompt empty
  - Success: { enhanced_prompt, agent_results, mode, enhancement_type, enhancement_ratio, complexity_score, models_used, ... }
- POST /api/enhance-multimodal → { prompt?: string, image_data?: base64, mode, preferred_format }
  - 400 if both prompt and image_data missing
  - Success: as above + agent_results.image_analysis + agent_results.multimodal flag
- POST /api/process-image → { image_data: base64, analysis_type?: "comprehensive"|"text_extraction"|"quick_description" }
  - Success: { success, description, extracted_text?, analysis, suggestions[] }
- POST /api/format-response → { content, target_format: one of formats, enhance_quality?: boolean }
  - Success: { formatted_content, detected_format, metadata, code_blocks[] }
- POST /api/detect-format → { content }
  - Success: { detected_format, confidence, suggestions }

Frontend UX components (key)
- ModelSelector: model preference (fast, balanced, reasoning, specialized, safety)
- CostBar: token estimates, throughput, and model chips used
- ModelStatusBoard: per-model availability with tiers and features
- ProcessingStatus: step progress, model names, reduced motion if requested
- EnhancedOutputDisplay: copy actions, format selector, code block expansion
- ImageUpload: drag & drop, preview, remove; validated image processing

Testing protocol (MANDATORY)
- Always update /app/test_result.md before calling the testing agent
  - Set needs_retesting where applicable
  - Update test_plan.current_focus to drive test coverage
- Use deep_testing_backend_v2 to test backend after any backend change
- Only run deep_testing_frontend_v2 with explicit user approval

Notes & limitations
- External LLM rate limiting can impact response times; retries are handled and requests eventually succeed
- Mongo ObjectIDs are not used directly in API responses to avoid serialization issues; UUIDs are used where needed

Do not modify
- Any existing .env values
- Internal backend binding (0.0.0.0:8001)
- /api prefix requirement for backend routes