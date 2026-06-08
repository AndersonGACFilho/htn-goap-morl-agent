# Hierarchical Task Network - HTN

> Hierarchical Task Network planning is an AI planning technique where abstract goals are broken down into structured
> tasks and eventually into concrete actions that an agent can execute.

## Concepts

### Task

A **task** represents something that the planner must accomplish.

Tasks are usually defined by:

* **Name**
  * Identifier of the task.
  * Example: `AttackEnemy`, `PatrolArea`, `FindWeapon`.

* **Parameters**
  * Values required by the task.
  * Example: `AttackEnemy(enemy)`, `MoveTo(location)`.

* **Constraints / Preconditions**
  * Conditions that must be true for the task to be valid.
  * Example: the enemy must be visible before attacking.

* **Result / Effects**
  * Expected changes after the task is executed.
  * Example: after `ReloadWeapon`, the weapon has ammo.

## Task Types

### Primitive Task

A **primitive task** is an atomic, concrete action that can be executed directly by the agent.

Examples:

```text
MoveTo(position)
ReloadWeapon()
OpenDoor(door)
Attack(enemy)
````

Primitive tasks are usually connected to actual game actions, animation commands, behavior tree nodes, or gameplay systems.

### Compound Task

A **compound task** is an abstract task that cannot be executed directly.

Instead, it must be decomposed into smaller subtasks using a **method**.

Examples:

```text
SurviveNight()
EscapeMansion()
DefeatEnemy(enemy)
FindSafeRoute(destination)
```

A compound task may be decomposed into:

* primitive tasks;
* other compound tasks;
* a sequence of both.

Example:

```text
EscapeMansion()
  -> FindExit()
  -> AvoidEnemies()
  -> MoveTo(exit)
  -> OpenDoor(exit)
```

## HTN Planning Flow

```mermaid
flowchart TD
    A[Objective / Goal] --> B[Compound Task]

    B --> C{Choose Method}

    C --> D[Method A]
    C --> E[Method B]
    C --> F[Method C]

    D --> G[Check Preconditions]
    E --> H[Check Preconditions]
    F --> I[Check Preconditions]

    G --> J[Decompose into Subtasks]
    H --> K[Decompose into Subtasks]
    I --> L[Decompose into Subtasks]

    J --> M[Primitive Task]
    J --> N[Compound Subtask]

    K --> O[Primitive Task]
    K --> P[Primitive Task]

    L --> Q[Compound Subtask]
    L --> R[Primitive Task]

    N --> S{Choose Method}
    Q --> T{Choose Method}

    S --> U[More Subtasks]
    T --> V[More Subtasks]

    U --> W[Primitive Task]
    V --> X[Primitive Task]

    M --> Y[Final Plan]
    O --> Y
    P --> Y
    R --> Y
    W --> Y
    X --> Y

    Y --> Z[Agent Executes Actions]
```
Example version using your `DefeatEnemy(enemy)` idea:
```mermaid
flowchart TD
    A[Goal: DefeatEnemy enemy] --> B[Compound Task: DefeatEnemy enemy]

    B --> C{Available Method?}

    C -->|Enemy is close + has melee weapon| D[Method: MeleeAttack]
    C -->|Enemy is far + has ranged weapon + has ammo| E[Method: RangedAttack]
    C -->|No valid attack method| F[Method: PrepareForCombat]

    D --> D1[MoveTo enemy]
    D1 --> D2[Attack enemy]

    E --> E1[AimAt enemy]
    E1 --> E2[Shoot enemy]

    F --> F1[FindWeapon]
    F1 --> F2[ReloadWeapon]
    F2 --> B

    D2 --> G[Plan Complete]
    E2 --> G

    G --> H[Agent Executes Primitive Actions]
```

## Method

A **method** defines one possible way to decompose a compound task into subtasks.

Example:

```text
Task: DefeatEnemy(enemy)

Method: MeleeAttack
Preconditions:
  - enemy is close
  - agent has melee weapon

Subtasks:
  - MoveTo(enemy)
  - Attack(enemy)
```

Another method for the same task:

```text
Task: DefeatEnemy(enemy)

Method: RangedAttack
Preconditions:
  - enemy is far
  - agent has ranged weapon
  - weapon has ammo

Subtasks:
  - AimAt(enemy)
  - Shoot(enemy)
```

## Plan

A **plan** is the final sequence of primitive tasks generated after all compound tasks have been decomposed.

Example:

```text
MoveTo(weapon)
PickUp(weapon)
MoveTo(enemy)
Attack(enemy)
EscapeArea()
```

## Summary

| Concept             | Meaning                                                 |
|---------------------|---------------------------------------------------------|
| **Task**            | Something the agent needs to accomplish                 |
| **Primitive Task**  | A concrete action executable by the agent               |
| **Compound Task**   | An abstract task that must be decomposed                |
| **Method**          | A rule that explains how to decompose a compound task   |
| **Plan**            | Final ordered sequence of executable primitive actions  |
