# Planner and agent

## Recursive planning and backtracking

`Planner.build_plan()` starts from a copy of `world_state_copy` and traverses the `Domain` root tasks. For each task, `recursive_planning()` returns either a pair of `(planned_tasks, simulated_state)` or `None`.

```mermaid
flowchart TD
    A[Task] --> B{PrimitiveTask?}
    B -->|yes| C{Valid preconditions?}
    C -->|no| X[branch failure]
    C -->|yes| D[appends task and applies effects\nto a copy]
    B -->|no| E{CompoundTask?}
    E -->|yes| F[filters feasible methods]
    F --> G[for each method, in order]
    G --> H[plans subtasks recursively]
    H -->|any failure| G
    H -->|success| I[returns first valid branch]
    E -->|no| X
```

Backtracking occurs at the method level: if any subtask in a decomposition fails, that branch copy is discarded and the next feasible method is tested. The first method that produces all subtasks is chosen.

!!! warning "Order matters"
    Feasible methods are attempted in declaration order. The planner does not calculate cost or search for the shortest solution; the domain author's priority determines the choice.

## Planner state

`update_world_state()` replaces the snapshot with an observed copy and clears `_current_plan`. `build_plan()` uses a new local list; the plan being executed belongs to the `Agent`, so a sensor update does not automatically erase it.

## `Agent` state machine

```mermaid
stateDiagram-v2
    [*] --> Decide
    Decide --> Plan: empty or invalid plan
    Decide --> Execute: valid current plan
    Plan --> NoPlan: empty build_plan()
    Plan --> Execute: plan created
    Execute --> Execute: RUNNING
    Execute --> Decide: SUCCESS (removes task)
    Execute --> Plan: FAILURE (clears plan)
    NoPlan --> [*]
```

Each `tick(world)` can rebuild a plan and execute one action. `AgentTickResult` returns the task name, status, whether replanning occurred, newly created plan names, the remaining plan, and an optional message.

## Lazy replanning

A sensor update marks `_world_state_changed`, but does not immediately destroy the plan. Before replanning, `_is_plan_still_valid()` simulates the remaining primitive tasks from the current observation:

1. checks the task's preconditions;
2. applies its effects to the copy;
3. proceeds to the next task.

This allows a future action to depend on an effect from an earlier action that is still in the plan. A `ValueError` in a condition or effect safely invalidates the plan.

## Action statuses

| Status    | Effect on the plan                                         |
|-----------|------------------------------------------------------------|
| `RUNNING` | keeps the current task for the next tick                   |
| `SUCCESS` | removes the current task                                   |
| `FAILURE` | discards the entire plan; the next tick will plan again    |

An unexpected non-primitive task is removed and reported in a message. This is a defensive mechanism: in normal operation, the planner already returns only primitive leaves.
