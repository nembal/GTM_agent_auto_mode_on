# Fullsend Architecture Diagrams

Official Mermaid diagrams for the Fullsend GTM Agent system architecture.

---

## System Layer Overview

```mermaid
flowchart TB
    subgraph human["🧑 HUMAN LAYER"]
        Users[Discord Users]
        Bot[Discord Bot]
        Dashboard[Web Dashboard]
    end

    subgraph gateway["🚪 GATEWAY LAYER"]
        Discord[Discord Service<br/><i>Python daemon</i>]
    end

    subgraph filter["🔍 FILTER LAYER"]
        Watcher[Watcher<br/><i>Gemini Flash</i>]
    end

    subgraph brain["🧠 BRAIN LAYER"]
        Orchestrator[Orchestrator<br/><i>Claude Opus + thinking</i>]
        FULLSEND[FULLSEND Agent<br/><i>Claude Code</i>]
        Builder[Builder Agent<br/><i>Claude Code</i>]
        Roundtable[Roundtable<br/><i>Multi-agent debate</i>]
    end

    subgraph execution["⚙️ EXECUTION LAYER"]
        Executor[Executor<br/><i>Worker pool</i>]
        ToolRegistry[Tool Registry<br/><i>Redis keys</i>]
    end

    subgraph monitoring["📊 MONITORING LAYER"]
        RedisAgent[Redis Agent<br/><i>Gemini Flash</i>]
    end

    subgraph infra["💾 INFRASTRUCTURE"]
        Redis[(Redis<br/>Pub/Sub + Keys)]
    end

    Users <--> Bot
    Bot <--> Dashboard
    Bot <--> Discord
    Dashboard <--> Discord
    
    Discord <--> Watcher
    Watcher <--> Orchestrator
    
    Orchestrator --> FULLSEND
    Orchestrator --> Builder
    Orchestrator --> Roundtable
    FULLSEND --> Builder
    
    FULLSEND --> Executor
    Builder --> ToolRegistry
    Executor <--> ToolRegistry
    
    Executor --> RedisAgent
    RedisAgent --> Orchestrator
    
    Discord <--> Redis
    Watcher <--> Redis
    Orchestrator <--> Redis
    FULLSEND <--> Redis
    Builder <--> Redis
    Executor <--> Redis
    RedisAgent <--> Redis
```

---

## Redis Pub/Sub Channel Flow

```mermaid
flowchart TB
    subgraph input["Input"]
        User[User on Discord]
    end
    
    subgraph services["Services"]
        Discord[Discord]
        Watcher[Watcher]
        Orchestrator[Orchestrator]
        FULLSEND[FULLSEND Listener]
        Builder[Builder Listener]
        Executor[Executor]
        RedisAgent[Redis Agent]
    end
    
    User -->|message| Discord
    Discord -->|discord_raw| Watcher
    Watcher -->|to_orchestrator| Orchestrator
    Watcher -->|from_orchestrator| Discord
    Orchestrator -->|from_orchestrator| Discord
    Orchestrator -->|to_fullsend| FULLSEND
    Orchestrator -->|builder_tasks| Builder
    FULLSEND -->|builder_tasks| Builder
    FULLSEND -->|execute_now| Executor
    Builder -->|builder_results| FULLSEND
    Executor -->|metrics| RedisAgent
    Executor -->|experiment_results| FULLSEND
    RedisAgent -->|to_orchestrator| Orchestrator
    FULLSEND -->|to_orchestrator| Orchestrator
    Builder -->|to_orchestrator| Orchestrator
    Discord -->|reply| User
```

---

## Detailed Pub/Sub Wiring

```mermaid
flowchart LR
    subgraph publishers["PUBLISHERS"]
        D1[Discord]
        W1[Watcher]
        O1[Orchestrator]
        F1[FULLSEND]
        B1[Builder]
        E1[Executor]
        R1[Redis Agent]
    end

    subgraph channels["REDIS CHANNELS<br/><i>fullsend:*</i>"]
        CH1[discord_raw]
        CH2[to_orchestrator]
        CH3[from_orchestrator]
        CH4[to_fullsend]
        CH5[builder_tasks]
        CH6[builder_results]
        CH7[execute_now]
        CH8[experiment_results]
        CH9[metrics]
        CH10[schedules]
    end

    subgraph subscribers["SUBSCRIBERS"]
        D2[Discord]
        W2[Watcher]
        O2[Orchestrator]
        F2[FULLSEND Listener]
        B2[Builder Listener]
        E2[Executor]
        R2[Redis Agent]
    end

    %% Publishers to Channels
    D1 --> CH1
    W1 --> CH2
    W1 --> CH3
    O1 --> CH3
    O1 --> CH4
    O1 --> CH5
    F1 --> CH2
    F1 --> CH5
    F1 --> CH7
    F1 --> CH10
    B1 --> CH2
    B1 --> CH6
    E1 --> CH8
    E1 --> CH9
    R1 --> CH2

    %% Channels to Subscribers
    CH1 --> W2
    CH2 --> O2
    CH3 --> D2
    CH4 --> F2
    CH5 --> B2
    CH6 --> F2
    CH7 --> E2
    CH8 --> F2
    CH9 --> R2
    CH10 --> E2
```

---

## Message Flow Patterns

### Simple Question (Watcher Handles)

```mermaid
sequenceDiagram
    participant User
    participant Discord
    participant Watcher
    
    User->>Discord: "What's the status?"
    Discord->>Watcher: discord_raw
    Note over Watcher: Classifies as simple query
    Watcher->>Discord: from_orchestrator
    Discord->>User: Status response
```

### Strategic Question (Orchestrator Handles)

```mermaid
sequenceDiagram
    participant User
    participant Discord
    participant Watcher
    participant Orchestrator
    
    User->>Discord: "Should we try LinkedIn ads?"
    Discord->>Watcher: discord_raw
    Note over Watcher: Classifies as escalation
    Watcher->>Orchestrator: to_orchestrator
    Note over Orchestrator: Thinks with context
    Orchestrator->>Discord: from_orchestrator
    Discord->>User: Strategic response
```

### Full Experiment Loop

```mermaid
sequenceDiagram
    participant Orchestrator
    participant FULLSEND
    participant Builder
    participant Executor
    participant RedisAgent
    
    Orchestrator->>FULLSEND: to_fullsend (design experiment)
    Note over FULLSEND: Designs experiment spec
    
    alt Needs new tool
        FULLSEND->>Builder: builder_tasks (PRD)
        Note over Builder: Builds tool
        Builder->>FULLSEND: builder_results
    end
    
    FULLSEND->>Executor: execute_now
    Note over Executor: Runs experiment
    Executor->>RedisAgent: metrics
    Executor->>FULLSEND: experiment_results
    
    Note over RedisAgent: Monitors thresholds
    RedisAgent->>Orchestrator: to_orchestrator (alert)
```

### Error Recovery Flow

```mermaid
sequenceDiagram
    participant Executor
    participant FULLSEND
    participant Builder
    participant Orchestrator
    
    Executor->>FULLSEND: experiment_results [ERROR: ToolNotFound]
    Note over FULLSEND: Detects missing tool
    FULLSEND->>Builder: builder_tasks (PRD for missing tool)
    Note over Builder: Builds the tool
    Builder->>FULLSEND: builder_results [success]
    FULLSEND->>Executor: execute_now (retry)
    Note over Executor: Runs successfully
    Executor->>FULLSEND: experiment_results [success]
    FULLSEND->>Orchestrator: to_orchestrator (experiment complete)
```

---

## Experiment Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> draft: FULLSEND designs
    draft --> ready: Design complete
    ready --> running: Cron triggers
    running --> run: Success
    running --> failed: Error
    run --> ready: Recurring
    run --> archived: One-time complete
    failed --> ready: After fix
    failed --> archived: Abandoned
    archived --> [*]
```

---

## Tool Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> building: PRD received
    building --> active: Build complete
    active --> broken: Execution error
    broken --> active: Fixed
    active --> deprecated: Replaced
    deprecated --> [*]
```

---

## Service Startup Modes

```mermaid
flowchart LR
    subgraph daemons["Always On (Daemons)"]
        D[Discord Service]
        W[Watcher]
        O[Orchestrator]
        RA[Redis Agent]
    end

    subgraph triggered["On-Demand (Triggered)"]
        F[FULLSEND]
        B[Builder]
        RT[Roundtable]
    end

    subgraph scheduled["Scheduled (Cron)"]
        E[Executor]
    end

    O -->|to_fullsend| F
    O -->|builder_tasks| B
    O -->|direct call| RT
    Redis[(Redis schedules)] -->|cron trigger| E
```

---

## Component Summary

| # | Component | Runtime | Model | Role |
|---|-----------|---------|-------|------|
| 1 | Discord Service | Python daemon | None | Front door — bot + dashboard |
| 2 | Watcher | API agent | Gemini Flash | Receptionist — filters noise |
| 3 | Orchestrator | Python daemon | Claude Opus (thinking) | Manager — context-rich decisions |
| 4 | FULLSEND Listener | Python daemon | None | Bridge — Redis → Claude Code |
| 5 | FULLSEND Agent | Claude Code | Claude Sonnet/Opus | Brain — designs experiments |
| 6 | Builder Listener | Python daemon | None | Bridge — Redis → Claude Code |
| 7 | Builder Agent | Claude Code | Claude Sonnet/Opus | Constructor — builds tools |
| 8 | Executor | Worker pool | None | Runner — executes experiments |
| 9 | Redis Agent | API agent | Gemini Flash | Analyst — monitors metrics |
| 10 | Redis | Infrastructure | N/A | Memory — pub/sub + state |
| 11 | Roundtable | Python script | Mixed | Council — AI debate for ideas |

---

## Channel Reference

| Channel | Purpose | Publishers | Subscribers |
|---------|---------|------------|-------------|
| `fullsend:discord_raw` | Raw Discord messages | Discord | Watcher |
| `fullsend:to_orchestrator` | Escalations, alerts | Watcher, Redis Agent, FULLSEND, Builder | Orchestrator |
| `fullsend:from_orchestrator` | Responses to Discord | Orchestrator, Watcher | Discord |
| `fullsend:to_fullsend` | Experiment requests | Orchestrator | FULLSEND Listener |
| `fullsend:builder_tasks` | Tool PRDs | Orchestrator, FULLSEND | Builder Listener |
| `fullsend:builder_results` | Build completions | Builder | FULLSEND Listener |
| `fullsend:execute_now` | Trigger execution | FULLSEND | Executor |
| `fullsend:experiment_results` | Run outcomes | Executor | FULLSEND Listener |
| `fullsend:metrics` | Real-time metrics | Executor | Redis Agent |
| `fullsend:schedules` | Schedule updates | FULLSEND | Executor |
