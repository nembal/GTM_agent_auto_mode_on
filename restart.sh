#!/bin/bash
# restart.sh - Reset Fullsend to a clean slate
#
# Usage:
#   ./restart.sh              # Full reset (interactive)
#   ./restart.sh --force      # Full reset (no prompts)
#   ./restart.sh --soft       # Keep product context, reset everything else
#   ./restart.sh --help       # Show help

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Core tools that should NOT be deleted (base infrastructure)
CORE_TOOLS=(
    "__init__.py"
    "browserbase.py"
    "register.py"
)

show_help() {
    echo "Fullsend Restart Script"
    echo ""
    echo "Resets the agent to a clean slate - clears agent-built tools,"
    echo "experiments, context, and Redis state."
    echo ""
    echo "Usage:"
    echo "  ./restart.sh              Full reset (interactive)"
    echo "  ./restart.sh --force      Full reset (no prompts)"
    echo "  ./restart.sh --soft       Keep product context, reset everything else"
    echo "  ./restart.sh --help       Show this help"
    echo ""
    echo "What gets reset:"
    echo "  - context/*.md            → Reset to templates"
    echo "  - tools/*.py              → Keep only core tools"
    echo "  - services/fullsend/experiments/exp_*.yaml, *_README.md"
    echo "  - services/fullsend/experiments/run_*.py, publish_*.py, store_*.py"
    echo "  - services/fullsend/experiments/list_sourcing_guide.md"
    echo "  - services/fullsend/tool_requests/*.yaml"
    echo "  - services/builder/requests/current_prd.yaml"
    echo "  - Redis fullsend:* keys   → Flushed"
    echo "  - .logs/*                 → Cleared"
    echo ""
    echo "What is preserved:"
    echo "  - tools/browserbase.py, register.py (core infra)"
    echo "  - services/fullsend/experiments/examples/"
    echo "  - All prompts and templates"
    echo "  - .env and configuration"
}

log_step() {
    echo -e "${BLUE}→${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}!${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

is_core_tool() {
    local tool="$1"
    for core in "${CORE_TOOLS[@]}"; do
        if [[ "$tool" == "$core" ]]; then
            return 0
        fi
    done
    return 1
}

reset_context() {
    local soft_mode=$1
    log_step "Resetting context files..."
    
    if [[ "$soft_mode" == "true" ]]; then
        log_warn "Soft mode: keeping product_context.md"
        cp context/templates/learnings.md context/learnings.md
        cp context/templates/worklist.md context/worklist.md
    else
        cp context/templates/product_context.md context/product_context.md
        cp context/templates/learnings.md context/learnings.md
        cp context/templates/worklist.md context/worklist.md
    fi
    log_success "Context reset"
}

reset_tools() {
    log_step "Removing agent-built tools..."
    local removed=0
    
    for tool in tools/*.py; do
        basename=$(basename "$tool")
        if ! is_core_tool "$basename"; then
            rm "$tool"
            echo "  Removed: $basename"
            ((removed++)) || true
        fi
    done
    
    if [[ $removed -eq 0 ]]; then
        log_success "No agent-built tools to remove"
    else
        log_success "Removed $removed agent-built tool(s)"
    fi
}

reset_experiments() {
    log_step "Clearing experiments..."
    local removed=0
    
    # Remove experiment files (not in examples/)
    for f in services/fullsend/experiments/exp_*.yaml services/fullsend/experiments/exp_*_README.md; do
        if [[ -f "$f" ]]; then
            rm "$f"
            echo "  Removed: $(basename "$f")"
            ((removed++)) || true
        fi
    done
    
    # Remove SUMMARY files
    for f in services/fullsend/experiments/SUMMARY_*.md; do
        if [[ -f "$f" ]]; then
            rm "$f"
            ((removed++)) || true
        fi
    done
    
    # Remove generated guide files
    for f in services/fullsend/experiments/list_sourcing_guide.md; do
        if [[ -f "$f" ]]; then
            rm "$f"
            echo "  Removed: $(basename "$f")"
            ((removed++)) || true
        fi
    done
    
    # Remove generated Python scripts in experiments (not examples)
    for f in services/fullsend/experiments/run_*.py services/fullsend/experiments/publish_experiment.py services/fullsend/experiments/store_learning.py; do
        if [[ -f "$f" ]]; then
            rm "$f"
            echo "  Removed: $(basename "$f")"
            ((removed++)) || true
        fi
    done
    
    # Remove tool requests
    for f in services/fullsend/experiments/tool_requests/req_*.yaml; do
        if [[ -f "$f" && ! "$f" =~ "examples" ]]; then
            rm "$f"
            ((removed++)) || true
        fi
    done
    
    # Remove top-level tool_requests
    for f in services/fullsend/tool_requests/req_*.yaml; do
        if [[ -f "$f" ]]; then
            rm "$f"
            ((removed++)) || true
        fi
    done
    
    # Remove generated scripts in fullsend root
    for f in services/fullsend/publish_experiment.py services/fullsend/store_learning.py; do
        if [[ -f "$f" ]]; then
            rm "$f"
            echo "  Removed: $(basename "$f")"
            ((removed++)) || true
        fi
    done
    
    if [[ $removed -eq 0 ]]; then
        log_success "No experiments to clear"
    else
        log_success "Cleared $removed experiment file(s)"
    fi
}

reset_builder() {
    log_step "Resetting builder requests..."
    
    # Reset current_prd.yaml to empty
    cat > services/builder/requests/current_prd.yaml << 'EOF'
# Builder PRD
# This file will be populated when the Orchestrator requests a new tool.
EOF
    
    log_success "Builder reset"
}

reset_fullsend_request() {
    log_step "Resetting FULLSEND request..."
    
    cat > services/fullsend/requests/current.md << 'EOF'
# Current FULLSEND Request

_No active request. Waiting for Orchestrator dispatch._
EOF
    
    log_success "FULLSEND request reset"
}

reset_redis() {
    log_step "Flushing Redis fullsend:* keys..."
    
    if command -v redis-cli &> /dev/null; then
        # Check if Redis is running
        if redis-cli ping &> /dev/null; then
            # Delete all fullsend:* keys
            keys=$(redis-cli keys "fullsend:*" 2>/dev/null || echo "")
            if [[ -n "$keys" ]]; then
                echo "$keys" | xargs redis-cli del > /dev/null 2>&1 || true
                log_success "Redis keys flushed"
            else
                log_success "No Redis keys to flush"
            fi
            
            # Also clear tool registry
            redis-cli del "tools:registry" > /dev/null 2>&1 || true
        else
            log_warn "Redis not running, skipping"
        fi
    else
        log_warn "redis-cli not found, skipping Redis flush"
    fi
}

reset_logs() {
    log_step "Clearing logs..."
    
    if [[ -d ".logs" ]]; then
        rm -f .logs/*.log
        log_success "Logs cleared"
    else
        mkdir -p .logs
        log_success "Logs directory created"
    fi
}

reset_status_files() {
    log_step "Resetting status files..."
    
    # Reset FULLSEND status
    if [[ -d "services/fullsend/status" ]]; then
        rm -f services/fullsend/status/session_*.md
        cat > services/fullsend/status/STATUS.md << 'EOF'
# FULLSEND Status

## Current State
Ready for new requests.

## Recent Activity
_No recent activity._
EOF
        cat > services/fullsend/status/TASKS.md << 'EOF'
# FULLSEND Tasks

_No active tasks._
EOF
    fi
    
    # Reset Builder status
    if [[ -d "services/builder/status" ]]; then
        cat > services/builder/status/STATUS.md << 'EOF'
# Builder Status

## Current State
Ready for PRD requests.

## Recent Builds
_No recent builds._
EOF
        cat > services/builder/status/TASKS.md << 'EOF'
# Builder Tasks

_No active tasks._
EOF
    fi
    
    log_success "Status files reset"
}

# Parse arguments
FORCE=false
SOFT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE=true
            shift
            ;;
        --soft)
            SOFT=true
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main
echo ""
echo "╔══════════════════════════════════════╗"
echo "║       FULLSEND RESTART               ║"
echo "╚══════════════════════════════════════╝"
echo ""

if [[ "$SOFT" == "true" ]]; then
    echo -e "${YELLOW}Soft reset mode:${NC} Keeping product_context.md"
    echo ""
fi

if [[ "$FORCE" != "true" ]]; then
    echo "This will reset Fullsend to a clean slate:"
    echo "  • Clear agent-built tools"
    echo "  • Clear all experiments"
    echo "  • Reset context files"
    echo "  • Flush Redis state"
    echo "  • Clear logs"
    echo ""
    read -p "Continue? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
    echo ""
fi

# Run all reset functions
reset_context "$SOFT"
reset_tools
reset_experiments
reset_builder
reset_fullsend_request
reset_redis
reset_logs
reset_status_files

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}  Fullsend reset complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit context/product_context.md with your product"
echo "  2. Start services: ./run_all.sh"
echo "  3. Open dashboard: http://127.0.0.1:8050/"
echo ""
