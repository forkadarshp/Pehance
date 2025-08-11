#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

## user_problem_statement: "Integrate mix of different models rather than just using one static model - llama3-8b-8192. Implement Primary Model: llama-3.3-70b-versatile for better reasoning, Fast Model: llama-3.1-8b-instant for simple intent classification, Safety Model: meta-llama/llama-guard-4-12b for enhanced guardrails. Fix current issue where any question asks follow up (should be single turn default with enhanced prompt output). Add multi turn mode with chat interface toggle. Enhanced responses for basic greetings. Use production grade intent classifer agent prompts."

## backend:
  - task: "Backend regression test run"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
          agent: "main"
          comment: "Executed full backend regression per test_plan: health, status create/list, test-models, enhance (single/multi), format-response, detect-format, process-image, enhance-multimodal (text+image and image-only). All green."

## frontend:
  - task: "Quick actions in EnhancedOutputDisplay (Copy All, Copy as MD, Show/Hide Code) + accessibility tweaks"
    implemented: true
    working: true
    file: "/app/frontend/src/components/EnhancedOutputDisplay.js, /app/frontend/src/components/ProcessingStatus.js, /app/frontend/src/components/CostBar.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: true
          agent: "main"
          comment: "Added Copy All, Copy as Markdown, and expand/hide code blocks. Improved ARIA live regions and reduced-motion respect in ProcessingStatus; added accessible titles in CostBar."

## metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: false

## test_plan:
  current_focus:
    - "Backend regression: /api/ and /api/status health endpoints"
    - "Prompt enhancement: /api/enhance single vs multi mode"
    - "Model availability: /api/test-models"
    - "Response formatting: /api/format-response and /api/detect-format"
    - "Image processing: /api/process-image"
    - "Multimodal enhancement: /api/enhance-multimodal"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

## agent_communication:
  - agent: "main"
    message: "Backend deps installed, services restarted, backend regression run passed for all endpoints. Implemented high-impact UX tweaks: EnhancedOutputDisplay quick actions (Copy All, Copy as MD, Show/Hide Code), ProcessingStatus accessibility and prefers-reduced-motion, CostBar accessibility titles. User will test frontend manually."