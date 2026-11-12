# Star UML: Use Case Diagram

```mermaid
graph LR
    User((User / Developer))
    
    subgraph AI_Swarm_Platform ["AI Swarm: From Individual to Intelligent Teams"]
        UC1[Submit Project Task & Select Archetype]
        UC2[Configure Technologies & Upload Data]
        UC3[Trigger Autonomous Swarm Orchestration]
        UC4[Monitor Visual Agent Workflow DAG]
        UC5[Inspect Agent State, Inputs & Outputs]
        UC6[Observe Sandbox Testing & Auto-Fix Loops]
        UC7[Browse Generated Multi-File Codebase]
        UC8[Download Project .ZIP Archive]
        UC9[Access Dynamic 22-Section Academic Docs]
        UC10[Query Transparent Legal AI Assistant]
    end

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6
    User --> UC7
    User --> UC8
    User --> UC9
    User --> UC10
```

## Actor Descriptions
- **User / Developer**: Initiates project requests, submits problem statements, selects technological constraints, inspects live multi-agent execution, reviews test reports, and downloads deliverables.

## Primary Use Cases
1. **Submit Project Task**: User defines project scope across ML, Web, Data Analysis, Research, Legal, or General software tasks.
2. **Trigger Swarm Orchestration**: Coordinator Agent classifies problem complexity, decomposes tasks, and activates specialized agents.
3. **Monitor Live DAG**: Displays live pulse animations and real-time state transitions (`WAITING`, `RUNNING`, `COMPLETED`, `FAILED`, `RETRYING`).
4. **Automated Testing & Auto-Fix Loop**: Testing Agent isolates defects in generated code and feeds failure tracebacks back to the Coding Agent for automated remediation.
5. **Transparent Legal AI**: Specialized workflow for fact-issue mapping, statutory retrieval, risk matrix assessment, and mandatory non-advice disclaimers.
