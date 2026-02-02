#!/usr/bin/env python3
"""
Real-time dashboard API for Fullsend agent system.

Subscribes to all fullsend:* Redis channels and exposes:
  GET /api/events     → Recent events across all channels
  GET /api/services   → Service status (last seen timestamps)  
  GET /                → Dashboard HTML

Usage: python dashboard_api.py [--port 8050]
"""

import argparse
import asyncio
import json
import os
import sys
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Redis channels to monitor
CHANNELS = [
    "fullsend:discord_raw",
    "fullsend:to_orchestrator",
    "fullsend:from_orchestrator",
    "fullsend:to_fullsend",
    "fullsend:builder_tasks",
    "fullsend:builder_results",
    "fullsend:experiment_results",
    "fullsend:execute_now",
    "fullsend:metrics",
    "fullsend:schedules",
    "fullsend:llm_calls",  # LLM call start/complete events
]

# Map channels to source service for status tracking
CHANNEL_TO_SERVICE = {
    "fullsend:discord_raw": "discord",
    "fullsend:to_orchestrator": "watcher",  # watcher escalates here
    "fullsend:from_orchestrator": "orchestrator",
    "fullsend:to_fullsend": "orchestrator",
    "fullsend:builder_tasks": "fullsend",
    "fullsend:builder_results": "builder",
    "fullsend:experiment_results": "executor",
    "fullsend:execute_now": "fullsend",
    "fullsend:metrics": "executor",
    "fullsend:schedules": "orchestrator",
}

# All services we track
ALL_SERVICES = [
    "discord",
    "watcher", 
    "orchestrator",
    "executor",
    "redis_agent",
    "fullsend",
    "builder",
    "roundtable",
]

ROOT = Path(__file__).resolve().parent
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")


@dataclass
class EventBuffer:
    """Thread-safe ring buffer for recent events."""
    
    max_size: int = 100
    events: deque = field(default_factory=lambda: deque(maxlen=100))
    service_last_seen: dict = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)
    redis_connected: bool = False
    redis_last_error: str = ""
    redis_reconnect_count: int = 0
    
    def add_event(self, channel: str, data: dict) -> None:
        """Add an event and update service last-seen time."""
        event = {
            "channel": channel,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        with self.lock:
            self.events.append(event)
            
            # Determine source service from message content first, then channel
            source = data.get("source", "")
            msg_type = data.get("type", "")
            
            # Check explicit source field
            if source in ALL_SERVICES:
                self.service_last_seen[source] = time.time()
            
            # Check message type for service attribution
            if msg_type == "watcher_response" or source == "watcher":
                self.service_last_seen["watcher"] = time.time()
            elif msg_type == "escalation" and source == "watcher":
                self.service_last_seen["watcher"] = time.time()
            elif "redis_agent" in msg_type or source == "redis_agent":
                self.service_last_seen["redis_agent"] = time.time()
            elif "roundtable" in msg_type or source == "roundtable":
                self.service_last_seen["roundtable"] = time.time()
            elif source == "fullsend":
                self.service_last_seen["fullsend"] = time.time()
            elif source == "builder":
                self.service_last_seen["builder"] = time.time()
            elif source == "orchestrator":
                self.service_last_seen["orchestrator"] = time.time()
            
            # Fall back to channel-based detection if no source identified
            if not source and msg_type not in ("watcher_response", "escalation"):
                service = CHANNEL_TO_SERVICE.get(channel)
                if service:
                    self.service_last_seen[service] = time.time()
    
    def get_events(self, limit: int = 50) -> list[dict]:
        """Get recent events, newest first."""
        with self.lock:
            events = list(self.events)
        return list(reversed(events))[:limit]
    
    def get_service_status(self) -> dict[str, dict]:
        """Get status for all services."""
        now = time.time()
        with self.lock:
            last_seen = dict(self.service_last_seen)
        
        result = {}
        for service in ALL_SERVICES:
            seen = last_seen.get(service)
            if seen:
                ago = now - seen
                result[service] = {
                    "status": "active" if ago < 30 else "idle",
                    "last_seen": ago,
                    "last_seen_formatted": _format_ago(ago),
                }
            else:
                result[service] = {
                    "status": "unknown",
                    "last_seen": None,
                    "last_seen_formatted": "never",
                }
        return result
    
    def get_redis_health(self) -> dict:
        """Get Redis connection health."""
        return {
            "connected": self.redis_connected,
            "last_error": self.redis_last_error,
            "reconnect_count": self.redis_reconnect_count,
        }


def _format_ago(seconds: float) -> str:
    """Format seconds ago as human readable."""
    if seconds < 60:
        return f"{int(seconds)}s ago"
    elif seconds < 3600:
        return f"{int(seconds/60)}m ago"
    else:
        return f"{int(seconds/3600)}h ago"


# Global event buffer
event_buffer = EventBuffer()


def run_redis_subscriber():
    """Background thread that subscribes to Redis channels."""
    try:
        import redis
    except ImportError:
        print("Redis not available, running in demo mode", file=sys.stderr)
        event_buffer.redis_last_error = "redis library not installed"
        return
    
    def subscribe_loop():
        while True:
            try:
                r = redis.from_url(REDIS_URL, decode_responses=True)
                pubsub = r.pubsub()
                
                # Subscribe to all channels
                for channel in CHANNELS:
                    pubsub.subscribe(channel)
                print(f"Subscribed to {len(CHANNELS)} Redis channels")
                
                # Mark connected
                event_buffer.redis_connected = True
                event_buffer.redis_last_error = ""
                
                # Listen for messages
                for message in pubsub.listen():
                    if message["type"] == "message":
                        try:
                            data = json.loads(message["data"])
                        except json.JSONDecodeError:
                            data = {"raw": message["data"]}
                        event_buffer.add_event(message["channel"], data)
                        
            except redis.ConnectionError as e:
                event_buffer.redis_connected = False
                event_buffer.redis_last_error = str(e)
                event_buffer.redis_reconnect_count += 1
                print(f"Redis connection error: {e}, retrying in 5s...")
                time.sleep(5)
            except Exception as e:
                event_buffer.redis_connected = False
                event_buffer.redis_last_error = str(e)
                event_buffer.redis_reconnect_count += 1
                print(f"Redis subscriber error: {e}, retrying in 5s...")
                time.sleep(5)
    
    thread = threading.Thread(target=subscribe_loop, daemon=True)
    thread.start()


def create_app():
    """Create Flask app with API endpoints."""
    try:
        from flask import Flask, jsonify, send_from_directory, request, Response
    except ImportError:
        print("Install Flask: pip install flask", file=sys.stderr)
        sys.exit(1)
    
    app = Flask(__name__)
    
    @app.route("/api/events")
    def api_events():
        """Get recent events across all channels."""
        limit = request.args.get("limit", 50, type=int)
        return jsonify({
            "events": event_buffer.get_events(limit),
            "count": len(event_buffer.events),
        })
    
    @app.route("/api/services")
    def api_services():
        """Get service status."""
        return jsonify({
            "services": event_buffer.get_service_status(),
        })
    
    @app.route("/api/health")
    def api_health():
        """Get Redis connection health."""
        health = event_buffer.get_redis_health()
        return jsonify(health)
    
    @app.route("/api/stream")
    def api_stream():
        """Server-Sent Events stream for real-time updates."""
        def generate():
            last_count = 0
            while True:
                # Check for new events
                current_count = len(event_buffer.events)
                if current_count != last_count:
                    # Send new events
                    events = event_buffer.get_events(10)
                    health = event_buffer.get_redis_health()
                    services = event_buffer.get_service_status()
                    data = json.dumps({
                        "events": events,
                        "health": health,
                        "services": services,
                    })
                    yield f"data: {data}\n\n"
                    last_count = current_count
                else:
                    # Send heartbeat every 2s even if no new events
                    health = event_buffer.get_redis_health()
                    services = event_buffer.get_service_status()
                    data = json.dumps({
                        "events": [],
                        "health": health,
                        "services": services,
                        "heartbeat": True,
                    })
                    yield f"data: {data}\n\n"
                time.sleep(1)  # Check every 1s for lower latency
        
        return Response(generate(), mimetype="text/event-stream")
    
    @app.route("/api/inject", methods=["POST"])
    def api_inject():
        """Inject a test event (for testing without Redis)."""
        data = request.get_json() or {}
        channel = data.get("channel", "fullsend:test")
        payload = data.get("payload", {"type": "test"})
        event_buffer.add_event(channel, payload)
        return jsonify({"ok": True})
    
    @app.route("/")
    def index():
        return send_from_directory(ROOT, "realtime_dashboard.html")
    
    @app.route("/<path:filename>")
    def static_files(filename):
        return send_from_directory(ROOT, filename)
    
    return app


def main():
    parser = argparse.ArgumentParser(description="Real-time dashboard API")
    parser.add_argument("--port", type=int, default=8050)
    parser.add_argument("--host", type=str, default="127.0.0.1")
    args = parser.parse_args()
    
    # Start Redis subscriber in background
    run_redis_subscriber()
    
    # Start Flask
    app = create_app()
    print(f"\n  Dashboard: http://{args.host}:{args.port}/")
    print(f"  API:       http://{args.host}:{args.port}/api/events")
    print(f"  Services:  http://{args.host}:{args.port}/api/services\n")
    app.run(host=args.host, port=args.port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
