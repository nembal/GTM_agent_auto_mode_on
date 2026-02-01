#!/bin/bash
# Test end-to-end wiring by publishing messages to Redis
# Run this AFTER starting services with run_all.sh
#
# Usage: ./scripts/test_e2e_wiring.sh [test_name]
#   test_name: fullsend | builder | orchestrator | all (default: all)

set -e

REDIS_URL="${REDIS_URL:-redis://localhost:6379}"

# Extract host:port from URL
REDIS_HOST="${REDIS_URL#redis://}"
REDIS_HOST="${REDIS_HOST%/}"

echo "Redis: $REDIS_HOST"
echo ""

# Test 1: Simulate Watcher escalating to Orchestrator
test_watcher_escalation() {
    echo "=== Test 1: Watcher → Orchestrator ==="
    echo "Publishing escalation to fullsend:to_orchestrator..."
    
    redis-cli -u "$REDIS_URL" PUBLISH fullsend:to_orchestrator '{
        "type": "escalation",
        "source": "watcher",
        "priority": "high",
        "original_message": {
            "channel_id": "test-channel",
            "message_id": "test-msg-001",
            "username": "test_user",
            "content": "Test GTM idea: Scrape GitHub stargazers for competitor repos"
        },
        "classification": {
            "action": "escalate",
            "reason": "High-quality GTM idea worth exploring",
            "priority": "high"
        }
    }'
    
    echo "✓ Published! Check orchestrator.log"
    echo ""
}

# Test 2: Simulate Orchestrator dispatching to FULLSEND
test_fullsend_dispatch() {
    echo "=== Test 2: Orchestrator → FULLSEND ==="
    echo "Publishing experiment request to fullsend:to_fullsend..."
    
    redis-cli -u "$REDIS_URL" PUBLISH fullsend:to_fullsend '{
        "type": "experiment_request",
        "idea": {
            "description": "Test experiment: Cold email CTOs who starred competitor repos",
            "target": "CTOs at Series A startups",
            "channel": "email"
        },
        "context": "This is a test request to verify FULLSEND listener is working.",
        "priority": "high",
        "orchestrator_reasoning": "Testing the e2e wiring"
    }'
    
    echo "✓ Published! Check fullsend_listener.log"
    echo ""
}

# Test 3: Simulate Orchestrator requesting a tool from Builder
test_builder_dispatch() {
    echo "=== Test 3: Orchestrator → Builder ==="
    echo "Publishing tool PRD to fullsend:builder_tasks..."
    
    redis-cli -u "$REDIS_URL" PUBLISH fullsend:builder_tasks '{
        "type": "tool_prd",
        "prd": {
            "name": "test_hello_world",
            "description": "Simple test tool that returns hello world",
            "inputs": [],
            "outputs": [{"name": "message", "type": "string"}],
            "requirements": ["Return a dict with message key"]
        },
        "requested_by": "test_script",
        "priority": "low",
        "orchestrator_reasoning": "Testing the Builder listener wiring"
    }'
    
    echo "✓ Published! Check builder_listener.log"
    echo ""
}

# Test 4: Check all services are subscribed
test_subscriptions() {
    echo "=== Test 4: Check Redis Subscriptions ==="
    echo "Running PUBSUB CHANNELS..."
    
    redis-cli -u "$REDIS_URL" PUBSUB CHANNELS "fullsend:*"
    
    echo ""
    echo "Running PUBSUB NUMSUB for key channels..."
    redis-cli -u "$REDIS_URL" PUBSUB NUMSUB \
        fullsend:discord_raw \
        fullsend:to_orchestrator \
        fullsend:from_orchestrator \
        fullsend:to_fullsend \
        fullsend:builder_tasks \
        fullsend:metrics \
        fullsend:execute_now \
        fullsend:schedules
    echo ""
}

# Main
case "${1:-all}" in
    watcher|orchestrator)
        test_watcher_escalation
        ;;
    fullsend)
        test_fullsend_dispatch
        ;;
    builder)
        test_builder_dispatch
        ;;
    subs|subscriptions)
        test_subscriptions
        ;;
    all)
        test_subscriptions
        echo ""
        echo "=== Running All Tests ==="
        echo ""
        test_watcher_escalation
        sleep 2
        test_fullsend_dispatch
        sleep 2
        test_builder_dispatch
        ;;
    *)
        echo "Usage: $0 [test_name]"
        echo ""
        echo "Tests:"
        echo "  watcher     - Test Watcher → Orchestrator escalation"
        echo "  fullsend    - Test Orchestrator → FULLSEND dispatch"
        echo "  builder     - Test Orchestrator → Builder dispatch"
        echo "  subs        - Check Redis subscriptions"
        echo "  all         - Run all tests (default)"
        ;;
esac

echo ""
echo "=== Done ==="
echo "Check logs in .logs/ directory for results"
