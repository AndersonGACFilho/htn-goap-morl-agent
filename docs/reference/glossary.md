# Concepts and glossary

| Term                 | Meaning in this project                                                                                |
|----------------------|--------------------------------------------------------------------------------------------------------|
| HTN                  | A planning technique that decomposes abstract tasks into subtasks until primitive actions are reached. |
| Domain               | An ordered collection of root tasks that the planner must satisfy.                                     |
| Primitive task       | An executable leaf with an action, preconditions, and effects.                                         |
| Compound task        | An abstract goal decomposed by alternative methods.                                                    |
| Method               | A decomposition rule: preconditions plus an ordered list of subtasks.                                  |
| Precondition         | A fact that must be true in the symbolic state for a branch to be applicable.                          |
| Effect               | A symbolic transformation used only to predict state during planning or validation.                    |
| Symbolic state       | `WorldState`, the planner's view of the world.                                                         |
| Concrete environment | The system that actually changes, such as `GridWorldEnv`.                                              |
| Sensor               | An adapter that observes the concrete world and updates the symbolic state.                            |
| Tick                 | One iteration of agent execution; at most one current action advances.                                 |
| Backtracking         | Trying the next method when the current decomposition fails.                                           |
| Lazy replanning      | Rebuilding only when no plan exists or validation of the remaining plan fails.                         |
| BFS                  | Breadth-first search; in GridWorld, it finds routes with the fewest moves.                             |

## Module reference

| Path                       | Contents                              |
|----------------------------|---------------------------------------|
| `htn.world`                | Symbolic state and world abstractions |
| `htn.tasks`                | HTN domain language                   |
| `htn.planner`              | Recursive planning                    |
| `htn.agent`                | Running plan and replanning           |
| `htn.sensors`              | Observation and notification          |
| `htn.actions`              | Action and status contract            |
| `htn.pathfinding`          | Generic pathfinding contract          |
| `htn._examples.grid_world` | End-to-end demonstration              |
