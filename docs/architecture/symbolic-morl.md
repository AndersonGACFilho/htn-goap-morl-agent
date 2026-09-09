# Proposed architecture: MORL-guided HTN method selection

!!! warning "Research proposal — partially scaffolded"
    The runtime now exposes `MethodSelectionStrategy`: DFS preserves domain
    order, while the RL strategy supplies an extension point for application-
    defined ordering. MORL training, preference encoders, vector rewards,
    feasible-method masking, and direct single-choice selection are not yet
    implemented.

## Problem addressed by the architecture

The `Planner` filters methods by preconditions, asks a
`MethodSelectionStrategy` to order the feasible candidates, then recursively
tries them. When a decomposition fails, it backtracks to the next candidate.
The DFS baseline retains declaration order. The heuristic strategy supplies an
executable ranking pattern, and the RL strategy defines an integration point
whose base method intentionally remains unimplemented. Neither supplies MORL
objectives or learned preferences.

The proposal preserves HTN symbolic guarantees and adds a learned decision **only** among methods that are already applicable. Learning therefore prioritizes valid alternatives rather than replacing precondition checks or allowing actions outside the domain.

For general definitions of rewards, returns, preferences, and Pareto trade-offs, see the [MORL learning notes](../annotations/reinforcement-learning/morl.md).

## Target architecture

```mermaid
flowchart LR
    S[Symbolic state<br/>WorldState] --> F[HTN filters methods<br/>by preconditions]
    D[HTN domain] --> F
    F --> M{Feasible methods}
    M --> Q[MORL policy<br/>selects one method]
    W[Preference source / vector w] --> Q
    Q --> P[Planner decomposes<br/>only the selected method]
    P --> A[PrimitiveTask plan]
    A --> E[Environment]
    E --> O[Reward vector r]
    O --> T[MORL training]
    T -. updates .-> Q
```

### Layer responsibilities

| Layer              | Responsibility                                                                   |
|--------------------|----------------------------------------------------------------------------------|
| HTN                | Defines tasks, methods, preconditions, effects, and the decomposition structure. |
| Symbolic filter    | Eliminates methods whose preconditions are not satisfied in `WorldState`.        |
| MORL               | Selects one remaining method according to multiple objectives and preferences.   |
| Executor           | Executes primitive tasks and observes results in the environment.                |
| Training           | Learns method values from vector rewards.                                        |
| Preference source  | Supplies `𝐰` from a profile, game director, rule, or optional learned encoder.   |

## MORL for HTN method selection

The proposed architecture applies MORL at one precise point: a `CompoundTask` has more than one applicable `Method` during planning. The HTN planner first computes:

$$
\mathcal{M}_{\mathrm{valid}}(C_t, WS_t) = \left\{M \in \mathcal{M}(C_t) \mid \operatorname{preconditions}(M, WS_t)\right\}
$$

Here, $WS_t$ is the current symbolic state, $C_t$ is the current compound task, $\mathcal{M}(C_t)$ is the set of methods declared for that task, $M$ is one candidate method, and $\mathcal{M}_{\mathrm{valid}}$ is the subset whose preconditions hold in $WS_t$.

Only then does MORL make one direct selection. A conceptual decision rule is:

$$
M_t^* = \underset{M \in \mathcal{M}_{\mathrm{valid}}(C_t, WS_t)}{\operatorname{arg\,max}}\; u_{\mathbf{w}_t}\!\left(\mathbf{Q}_{\theta}(C_t, WS_t, M,\mathbf{w}_t)\right)
$$

In this equation, $M_t^*$ is the selected method, $\mathbf{Q}_{\theta}(C_t,WS_t,M,\mathbf{w}_t)$ is the estimated vector value of choosing $M$ in symbolic state $WS_t$ for task $C_t$ under the current preference, and $\operatorname{arg\,max}$ returns the candidate with the highest utility under $\mathbf{w}_t$.

`Q` is a vector-valued estimate of the consequence of choosing method `M`, not an authorization to execute an arbitrary primitive action. The planner's feasible-method mask is authoritative: MORL cannot select a method excluded by symbolic preconditions. The online path does not expand or compare partial plans for every candidate: one masked inference selects $M_t^*$, and HTN decomposes only $M_t^*$.

```mermaid
flowchart LR
    S[Symbolic state and context] --> F[HTN computes feasible methods]
    T[Current CompoundTask] --> F
    F --> M[Validity mask]
    G[Game / AI director / profile / rule] --> P[Preference vector w]
    S --> W[Optional preference encoder]
    W --> P[Preference vector w]
    M --> Q[MORL method-value estimates]
    P --> Q
    Q --> C[Select one valid Method M*]
    C --> D[Decompose only M*]
    D --> E[Primitive-task execution]
    E --> R[Vector reward and next state]
```

This separation preserves two different guarantees:

- **HTN validity:** the selected method satisfies the domain's hard symbolic conditions.
- **MORL adaptation:** among valid methods, the choice reflects the current objective trade-off.

## State changes and rewards

The symbolic state `WS` contains relevant facts about the agent and the world. Rewards evaluate interaction outcomes according to the objectives defined for the experiment. When successive states contain enough information to determine this signal, we can write:

$$
\mathbf{r}_t = f(WS_t, WS_{t+1}).
$$

This notation allows state comparisons without requiring an explicit delta.

- **Numerical variables:** $\Delta x_t=x_{t+1}-x_t$.
- **World state:** $\Delta WS_t$ denotes changes in relevant variables, not general dictionary subtraction.
- **Boolean and categorical facts:** use comparisons appropriate to their types.
- **Delta-only reward:** $\mathbf{r}_t=g(\Delta WS_t)$ assumes those changes alone determine the reward.

A reward can also occur without a change in `WS`, such as a penalty for elapsed time.

### Primitive effects and environment dynamics

A method defines a decomposition into tasks. Its primitive tasks declare symbolic effects; the method does not directly apply a separate world-state effect.

World-state changes can reflect two sources:

- **Agent actions:** movement, resource consumption, item collection, and other effects of executing primitive tasks.
- **Environment dynamics:** attacks, hazards, regeneration, elapsed time, and other events affecting the agent or world.

Rewards evaluate the outcome of this interaction, including effects the agent suffers from the environment.
They are not restricted to effects directly produced by its own actions.

### Planning versus execution

| Stage | State used | Effects included |
|---|---|---|
| Planning | A simulated copy of `WS` | Declared primitive effects and any environmental effects explicitly represented by the planning model. |
| Execution | Observed `WS`, updated through sensors | Actual action outcomes and environmental effects captured by the observations. |

This gives two distinct quantities:

$$
\Delta WS_{\mathrm{predicted}}
\qquad\text{and}\qquad
\Delta WS_{\mathrm{observed}}.
$$

- **Predicted changes** describe what the model expects to happen.
- **Observed changes** describe what happened and was captured in `WS`.
- Failed actions, external events, or an incomplete model can make them differ.

The current planner applies declared primitive-task effects to a state copy.
Predicting additional environmental effects requires explicitly modeling them; it is not an existing general environment simulator.
At runtime, concrete actions change the environment and sensors refresh the symbolic state.

### Example: crossing a hazardous area

1. A method decomposes the crossing into primitive tasks.
2. During planning, the model can predict energy consumption and health loss **if both effects are modeled**.
3. During execution, movement consumes energy and the hazard may cause actual damage.
4. Sensors update the observed state with the available facts.
5. Selected observed deltas form the reward vector, for example $[\Delta H_t,\Delta E_t,-\Delta T_t]^{\mathsf T}$.
6. Training assigns the resulting experience to the method decision under the chosen credit-assignment protocol.

The method can therefore learn a lower value for exposing the agent to danger even when its primitive tasks do not declare health loss as a direct symbolic effect.
This learns the consequences of interaction; it does not establish that every external event was caused by the method.

### Using predicted and observed changes

- Use predicted changes to reason about modeled consequences during planning.
- Use observed changes to construct rewards from executed experience.
- If simulated rollouts are used for training, identify their transitions and rewards as model-generated experience.
- Do not count both the predicted effect and its observed realization as two separate outcomes of the same execution.

This distinction does not require expanding all candidate methods during online MORL selection.
The proposed normal path still selects one applicable method and decomposes that choice.

### Net change versus consumption

Choose the signal that matches the objective:

| Objective                   | Reward                  | Meaning                                       |
|-----------------------------|-------------------------|-----------------------------------------------|
| Improve net energy balance  | $E_{t+1}-E_t$           | Penalize net loss and reward recovery.        |
| Minimize energy consumption | $-c_t$, with $c_t\geq0$ | Penalize the energy consumed during the step. |

Consumption and recovery can cancel out in the delta.
Similarly, losing five health points and recovering five produces zero net change despite the damage received.

When symbolic states do not preserve the necessary events, the environment should provide those signals directly, such as damage received, resources consumed, or mission completion. The formulation $f(WS_t,WS_{t+1})$ is therefore one possible representation, not an architectural requirement. Observed changes may also include events external to the agent; they do not, by themselves, establish that the method caused the entire outcome.

### Task reward versus shaping

Defining a reward from a transition does not automatically constitute *reward shaping*.

- **Task reward:** defines the objective being optimized.
- **Shaping:** adds an auxiliary signal to the task reward and should be identified separately.

Even when rewards come directly from the environment, choosing objectives and scales remains part of the experimental design.

During execution, per-step signals are accumulated over the decision interval, as described in the credit-assignment section below.
Comparing only the initial and final states of the decomposition may lose intermediate events.

| Symbol | Role |
|---|---|
| $\Delta WS$ | Observed state changes. |
| $\mathbf r_t$ | Per-objective feedback. |
| $\mathbf R_{\mathrm{method}}$ | Accumulated signals for the method decision. |
| $\mathbf Q$ | Expected return including continuation. |
| $\mathbf w$ | Preferences used to evaluate vector values. |

Weights do not redefine the observed rewards.

### Using state deltas as the reward vector

State deltas can explicitly define the reward vector when net changes represent the intended objectives. For example, select health $H$, energy $E$, and elapsed time $T$ from `WS`:

$$
\mathbf r_t=[H_{t+1}-H_t,\ E_{t+1}-E_t,\ -(T_{t+1}-T_t)]^{\mathsf T}.
$$

This definition:

- Rewards health and energy recovery.
- Penalizes health and energy loss.
- Penalizes elapsed time.

It is a valid task-reward definition, not automatically reward shaping.
It optimizes **net changes**: if consumption and recovery cancel, their net contribution is zero.

Without discounting, accumulated deltas telescope:

$$
\sum_{t=0}^{N-1}(H_{t+1}-H_t)=H_N-H_0.
$$

With discounting, the timing of changes also affects return.

### Preference weights

The preference vector determines how relevant each component is:

$$
\mathbf w_t\in[0,1]^d,\qquad\sum_i w_{i,t}=1,\qquad
u_t=\mathbf w_t^{\mathsf T}\mathbf r_t=\sum_i w_{i,t}r_{i,t}.
$$

For the order `[health, energy, time]`:

| Weights | Interpretation |
|---|---|
| `[0.7, 0.2, 0.1]` | Prioritize health while retaining energy and time. |
| `[1, 0, 0]` | Consider health alone: a **one-hot** preference vector. |

Intermediate weights allow mixed preferences.

**Worked example:**

$$
\mathbf r_t=[-2,-3,-1]^{\mathsf T},\qquad
\mathbf w_t=[0.7,0.2,0.1]^{\mathsf T}
$$

$$
u_t=0.7(-2)+0.2(-3)+0.1(-1)=-2.1.
$$

- **Signs:** define whether an increase is desirable for each component.
- **Scales:** document and, where needed, normalize component magnitudes so that they do not obscure the intended priorities.

**Deltas express outcomes; weights express priorities.**
The dot product returns a scalar, rather than an elementwise weighted vector.

### Weighting rewards versus values

- $\mathbf w_j^{\mathsf T}\mathbf R_{\mathrm{method}}$: evaluates the accumulated interval reward under the preference at selection.
- $\mathbf w_j^{\mathsf T}\mathbf Q$: evaluates expected return including continuation.

If preferences change within an interval, distinguish two criteria:

1. Weight each step with its own $\mathbf w_t$.
2. Weight the entire interval with the selection preference $\mathbf w_j$.

These are different objectives; the experiment must specify which is used.

## Intuition behind the learning cycle

The central idea is that HTN determines which methods are applicable, MORL learns their consequences and selects according to preferences, and execution produces experience that can update those estimates during training. State changes $\Delta WS$ remain useful observations for defining reward components, such as net energy loss, without requiring every reward to be a delta.

The conceptual cycle is:

1. **Filter:** HTN identifies applicable methods.
2. **Select:** MORL chooses according to preferences.
3. **Decompose:** HTN expands the selected method into subtasks.
4. **Execute:** primitive tasks produce transitions and reward signals.
5. **Learn:** training updates value estimates and assigns credit to earlier choices.

This describes the learning cycle. At deployment, the proposed online selector uses learned estimates; online selection does not itself require parameter updates.

A shorthand such as $Q(M)\approx R_M+\gamma\,\text{continuation value}$ communicates immediate reward plus future consequences. It is an intuitive summary rather than a complete update rule: the formal model conditions values on the compound task, state, method, and preferences, accumulates rewards over the decision interval, and discounts continuation by $\gamma^k$ for an interval of $k$ primitive steps. Here, $R_M$ denotes a scalarized interval reward only for this shorthand; the model preserves the underlying reward vector.

“Propagating backward” means assigning credit to earlier choices from their observed consequences. A temporal update alone does not specify how credit is distributed between parent methods and the methods selected for their compound subtasks. That requires explicit decision boundaries, hierarchical context, and a credit-assignment protocol; it does not mean mechanically copying the same reward to every ancestor.

In this interpretation, $\Delta WS$ is an observed state change, reward evaluates outcomes according to objectives, and $Q$ estimates the value of a choice including future consequences. This intuition motivates the architecture without imposing reward shaping or replacing its formal specification.

## Preferences and context change

The preference vector $\mathbf{w}_t$ describes what matters now. It may change because an ally becomes vulnerable, resources become scarce, or a game-design profile changes. This differs from changing environment dynamics: preferences can change even when transition dynamics are stationary.

Preference generation is deliberately separate from MORL method selection. Fixed profiles and explicit rules are interpretable baselines. A relational graph encoder or deep-learning encoder may infer $\mathbf{w}_t$ from state and context, but it must use the same HTN mask and MORL interface as every other encoder. See [preference-weight generation](preference-weight-generation.md).

## Learning transition and credit assignment

Method selection is temporally extended. A transition starts when MORL selects a valid method. The experimental protocol must choose its endpoint: the next method-selection point, decomposition completion, replanning, or episode termination. These boundaries are alternatives to specify, not interchangeable definitions. The method-level reward is the discounted accumulation of primitive-step rewards during that interval:

$$
\mathbf{R}_{\mathrm{method}} = \sum_{i=0}^{k-1}\gamma^i\mathbf{r}_{t+i}
$$

Here, $\mathbf{R}_{\mathrm{method}}$ is the vector return assigned to one method-selection decision, $i$ indexes primitive steps after selection, $k$ is the number of executed primitive steps before control returns, and $\gamma \in [0,1]$ is the discount factor.

This is a semi-MDP-style transition. It avoids assigning all credit to one primitive action when the learned decision was instead a hierarchical decomposition choice. The same temporal boundary connects the design to [RL with Options](../annotations/reinforcement-learning/rl-with-options.md).

## Current strategy interface and proposed MORL integration

Today, `CompoundTask.get_feasible_methods(world_state)` returns applicable
methods, and the planner passes them to `strategy.order_methods(methods,
world_state)`. `RLBasedSearchStrategy` retains an RL-agent reference, but its
base ordering method raises `NotImplementedError`; a concrete subclass must
define the policy or value-function interface. It still relies on ordinary
planner backtracking.

The proposed evolution is to select one method directly at each HTN decision
point. The policy receives the feasible-method mask, evaluates the alternatives
in one inference, and decomposes only the selected method in the normal online
path:

```mermaid
flowchart TD
    A[CompoundTask] --> B[get_feasible_methods]
    B --> C{Are there feasible methods?}
    C -->|no| X[branch failure]
    C -->|yes - current baseline| O[declaration order]
    C -->|yes - future architecture| Q[MORL selects M*]
    O --> T[try decomposition]
    Q --> T[decompose only M*]
    T -->|decomposition failure| N[mask M* and select again]
    N --> Q
    T -->|success| P[return plan]
```

This is not a depth-first search over a MORL-ranked list. During normal operation, the loop runs once: filter, infer, select $M^*$, and decompose $M^*$. If that decomposition fails, the planner temporarily masks $M^*$ and invokes the same MORL selector over the remaining candidates. This **method fallback** is failure recovery, not the expected decision path.

Three cases remain deliberately separate:

1. A method with unsatisfied preconditions is excluded before MORL and never needs fallback.
2. A locally valid method whose subtasks cannot be decomposed triggers method fallback at the same `CompoundTask`.
3. A world change during primitive execution invalidates the current plan and triggers replanning from the current `WorldState`, rather than backtracking over an obsolete planning state.

When the state and preference vector have not changed, the implementation may reuse the values from the first inference, mask the failed method, and take a new `argmax`. If either changes, it runs a new inference.

## Experimental questions

### Main learned baseline: scalar Deep RL

The evaluation will compare preference-conditioned MORL against a scalar Deep RL baseline for HTN method selection based on **Bahrami (2025)**, discussed in the [bibliography](../reference/bibliography.md).
Implementation details and any adaptations to the experimental domain will be documented explicitly.

| Approach | Learning objective |
|---|---|
| Scalar Deep RL baseline | Estimate scalar method values under a declared reward scalarization. |
| Proposed preference-conditioned MORL | Estimate vector method values and select according to the supplied preferences. |

MORL may also use deep neural networks. The comparison concerns scalar learning versus preference-conditioned multi-objective learning, rather than shallow versus deep models.

For a controlled comparison:

- Use the same HTN domain, applicability rules, observations, and evaluation scenarios.
- Define the scalar baseline's reward weights and report whether separate models are trained for different preferences.
- Report both per-model and total training budgets, along with comparable tuning budgets and model capacity where feasible.
- Evaluate task performance, utility, generalization to held-out preferences, adaptation after preference changes, and computational cost.
- Distinguish an adaptation of the published approach from an exact reproduction.

### Additional baselines and ablations

The evaluation will retain symbolic baselines and distinguish the following effects:

| Comparison                                               | Isolates                                             |
|----------------------------------------------------------|------------------------------------------------------|
| Fixed HTN order vs. MORL with fixed $\mathbf{w}$         | Learned direct selection among valid methods.        |
| Fixed $\mathbf{w}$ vs. dynamic rule-based $\mathbf{w}_t$ | Adaptation to changing preferences.                  |
| Rules vs. graph/deep encoder                             | Value of structured or learned preference inference. |
| MORL with and without HTN mask in a safe test setting    | Value of symbolic validity filtering.                |

Useful metrics include vector return, utility under held-out preferences, task success, invalid-method selection rate, decomposition-fallback rate, adaptation latency, method-switch stability, and normal-path planning-time latency.

## Technical roadmap

1. **HTN strategy baseline — available:** DFS and heuristic ordering can be instrumented now; the RL ordering hook is ready for a concrete implementation and the same instrumentation.
2. **Multi-objective environment — future:** define the components of `r` and how each episode records returns.
3. **HTN–MORL integration — future:** introduce a preference-conditioned, single-choice selector for feasible methods, plus MORL-guided method fallback after decomposition failure.
4. **Training — future:** learn a policy/value during a pre-deployment training phase that estimates the trade-off for each feasible method; online use is one masked inference at a decision point.
5. **Preference sources — experimental track:** compare game/director inputs, fixed profiles, rules, relational graphs, and deep learning under the same MORL interface.
6. **Experimental comparison — future:** compare MORL with the scalar Deep RL baseline based on Bahrami (2025), alongside symbolic baselines and ablations; report plan validity, fallback rate, replanning, vector return, preference adaptation, and decision cost.

## Implications for GridWorld

The current GridWorld is a good initial environment because it already has high-level alternatives: when the door is closed, the domain must ensure it has a key, open the door, and reach the goal. To experiment with MORL in practice, it will be necessary to add genuinely competing alternatives and rewards with more than one objective; in the current domain, method order is mainly a fixed execution rule.

See the [preference-weight generation](preference-weight-generation.md), [planner and agent guide](../framework/planning-runtime.md), and [domain, actions, and navigation](../grid-world/domain-and-actions.md).
