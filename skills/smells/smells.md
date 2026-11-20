# Smells
Each smell: the rule and its structural fix, then the keep list of legitimate uses that are not findings.

## State and absence

_TypeScript-general._

### Absence without a production meaning [S01]

- Optionality without a real producer is a smell because it encodes an unexplained state and makes every consumer repair the contract.
  - **Fix:** Trace producers and callers; remove absence, normalize it once, or name its actual lifecycle or domain variant.
- **Keep:** Independent missing data, optional filters or callbacks, omitted patch fields meaning unchanged, honest wire types and lookup results at their boundary.

### Fallbacks that invent valid-looking domain states [S02]

- A default for a wiring error, failed read or impossible input is a smell because it turns missing knowledge or failure into apparently valid domain data.
  - **Fix:** Require the missing dependency; model checking and failure separately; reject or normalize foreign inputs at their owner.
- **Keep:** An agreed product default at the input boundary, a real empty result, preserving the last successful result during refresh, and explicitly optional non-production configuration.

### Independent fields that encode one state machine [S04]

- Correlated booleans, optionals or duplicated discriminants are a smell because their Cartesian product allows combinations the domain cannot produce.
  - **Fix:** Enumerate meaningful states and payloads; use one discriminant or real state machine; collapse discriminants that describe the same axis.
- **Keep:** A genuine yes/no fact, independent flags, same-shape scalar states, and a state machine only where transitions actually need one.

### Assertions instead of compiler-proved contracts [S03]

- An assertion that supplies a fact the model cannot prove is a smell because it tells the compiler to trust the author instead of establishing the invariant.
  - **Fix:** Preserve inference, use a typed constructor or decoder, or redesign correlated values so normal narrowing proves access.
- **Ask:** What proves this assertion, and could inference or a discriminant prove it instead?
- **Keep:** An isolated audited brand constructor, a library-declared compile-time type setup such as XState types, or an unavoidable foreign interface assertion after validation; const assertions and satisfies are not unsafe casts.

### Unexplained numerical policy [S26]

- A magic number that determines behavior is a smell because its source, units and owning policy are hidden from the next reader.
  - **Fix:** Trace the requirement or producer, name its domain meaning and units, and put the value with the policy or configuration that actually owns it.
- **Ask:** Where did this value come from, what are its units, and who owns the policy?
- **Keep:** Obvious arithmetic identities, readable scenario values in tests, documented protocol constants and deliberately fixed experimental inputs.

## Ownership and boundaries

_Language-agnostic._

### Multiple authorities for the same decision [S07]

- Copied rules, parallel schemas or independently maintained derived state are a smell because the same fact can acquire conflicting meanings.
  - **Fix:** Choose the owner, derive or project other representations from it, and remove parallel decision logic rather than merely sharing literals.
- **Keep:** Wire and domain types with explicit translation, persisted historical snapshots, independent test oracles, and projections with different declared purposes.

### Transport or implementation vocabulary in the domain [S05]

- Wire codes, sentinels, serialized lists or infrastructure concepts in business decisions are a smell because consumers must know how data arrived instead of what it means.
  - **Fix:** Decode and translate once into domain terms at the adapter; keep domain policy and infrastructure implementation behind their own interfaces.
- **Ask:** Is this business state, or a wire sentinel, serialized list or technology detail?
- **Keep:** Honest wire schemas, raw storage records and adapters; domain-significant provenance; an explicitly lossy final display projection.

### Helpers and utils without a domain owner [S06]

- A helpers or utils module that groups unrelated work by technical role is a smell because it hides ownership and gives the file no reason to stop growing.
  - **Fix:** Move each rule beside the domain concept it implements; extract a module only when it owns a coherent production responsibility.
- **Ask:** Which domain owns this function, and what keeps this file from collecting unrelated work?
- **Keep:** A cohesive genuinely shared utility, such as relative-age formatting; a library-defined helper or named adapter is not wrong merely because of its filename.

### Consumers deciding organization policy [S13]

- A leaf component checking an organization setting or policy kind to do nothing is a smell because policy selection has leaked past the layer that should have chosen the behavior.
  - **Fix:** Resolve policy in its owner and compose the applicable components or provide a behavior contract so consumers need not interpret organization settings.
- **Keep:** The policy-selection boundary itself, presentational conditions on already resolved state, and variants whose real domain payload requires narrowing.

### Callers carrying module-internal orchestration [S29]

- Passing infrastructure through every layer or making callers coordinate delivery internals is a smell because the interface exposes the complexity the module should hide.
  - **Fix:** Design from the consumer intent, acquire dependencies at the composition boundary and put ordering, transport selection and reconciliation behind the owning interface.
- **Ask:** Does the caller need this detail, or should the module hide it behind intent?
- **Keep:** Explicit dependency injection at a composition root, a small transparent adapter, ordinary meaningful props and infrastructure-specific callers.

### Broad reads and consumer-side reconstruction [S28]

- Loading a broad collection and rebuilding joins or filters in a consumer is a smell when a domain read can return the needed result because each caller repeats selection and subscription work.
  - **Fix:** Move the owned selection or join into a focused domain read; keep consumers on the supported loaded-query path and verify actual query behavior.
- **Ask:** Can the domain query own this selection instead of every consumer reconstructing it?
- **Keep:** A caller genuinely needs the complete small collection, deliberate terminal presentation projection, and library joins with namespaced rows; select is not categorically forbidden.

### Reimplementing a chosen library contract [S15]

- Handwritten caching, async state, dispatch or framework plumbing is a smell when the installed library already owns that contract because it creates a second lifecycle and weaker guarantees.
  - **Fix:** Read the installed version and use its query keys, invalidation, scopes, field groups, collections or code-generation idiom at an intentional boundary.
- **Keep:** Application-specific policy, adapters for a real library gap, and a narrowly scoped native operation when a broad dependency would add more than it hides.

### Resource cleanup and runtime ownership scattered across callers [S17]

- Manually coordinated listeners, waiters and background workers are a smell because lifecycle invariants depend on unrelated callers remembering every terminal path.
  - **Fix:** Put acquisition, cancellation and finalization behind one scoped owner; make identity updates idempotent at the module that owns identity.
- **Ask:** Who releases every listener, waiter and worker on every terminal path?
- **Keep:** A small correctly paired imperative handle, an application-owned runtime, and an explicit adapter to imperative callers; singleton is not itself forbidden.

## Unneeded code

_Language-agnostic._

### No callers, no producer or unreachable defensive branch [S12]

- Code or guards with no reachable production path are a smell because they preserve unsupported behavior and misstate the actual contract.
  - **Fix:** Trace callers and producers, then delete the implementation, obsolete tests, configuration and references together.
- **Keep:** Real malformed external inputs, legitimate lookup misses, supported entry points and dynamic/framework registrations verified before declaring code unused.

### Speculative complexity or compatibility without a requirement [S27]

- A compatibility bridge, general dependency or feature added for a need nobody has is a smell because it makes the present design serve an unverified future or retired requirement.
  - **Fix:** Check the actual requirement and consumers, remove unnecessary machinery first, then choose the smallest complete design for supported usage.
- **Ask:** Which present user, consumer or compatibility obligation requires this machinery?
- **Keep:** Real external compatibility and OTA/runtime constraints, supported persisted data, a migration with current users, and an actual reusable library need.

## React

_React only._

### Effects that mirror reactive state or replay user intent [S08]

- An effect that copies props or query data into state, or infers an action from that state, is a smell because it creates a second update protocol instead of deriving or handling the event directly.
  - **Fix:** Derive during render; perform user actions in their handler; use the query or form library as the state owner.
- **Keep:** Synchronizing with an external system, a correctly owned subscription with cleanup, or an imperative platform API driven by committed UI state.
- **Recipe**, when a lint error or review flags one of these effects:
  1. Name the value the effect decides and the user action or record lifecycle that owns the decision.
  2. Before editing production code, run the real action and assert the outcome. For a new record's default, invoke creation and read back what it writes before opening the form. Record the actual value, even if the check fails.
  3. Move the decision to its owner: derive a value from current inputs during render, run user-triggered work in its action, and set a record's starting values where the record is created.
  4. Delete the effect once its work has moved. Verify the outcome with a test through the owning action or lifecycle, using the real producer.

### Refs used as a second state store [S09]

- Refs for derived values, cached state or stable data initialization are a smell because mutations bypass React state ownership and obscure what should trigger a render.
  - **Fix:** Use plain derivation or state; keep one authoritative owner and use refs only for imperative handles.
- **Keep:** DOM/native handles and genuinely imperative timer or platform handles; no blanket ban on all mutable references in other libraries.

### Memoization compensating for component structure [S10]

- Memoization added for stability or broad rerenders without a measured need is a smell because it preserves excess ownership and subscription breadth instead of removing their cause.
  - **Fix:** Derive with const and inline handlers; reduce component responsibilities or subscription scope before proposing a measured exception.
- **Keep:** A specific demonstrated expensive computation or required reference-identity contract after discussion; evidence does not support removing every existing memo mechanically.

### Application work owned by a React render lifetime [S16]

- A service or business operation that exists only through component rendering is a smell when its lifetime is application-owned because remounts and profile refreshes become accidental business events.
  - **Fix:** Give startup, identity reconciliation and execution one application-owned module; React presents state and expresses intent through its interface.
- **Ask:** Would the operation still need to exist if this component never mounted?
- **Keep:** Actual UI state, UI-owned external synchronization, a pure hook adapter, and pure lazy state initialization rather than side-effect-only initializers.

### Flag-driven component variants and nested decisions [S14]

- A component API with many mode props or nested JSX decisions is a smell because it combines distinct responsibilities behind combinations the caller must coordinate.
  - **Fix:** Compose meaningful children or explicit variants; extract named early-return business decisions where composition is not the issue.
- **Ask:** Are these props distinct responsibilities that should be composed rather than combined?
- **Keep:** A simple two-branch display condition, independent presentational props, and real input variants; do not duplicate entire forms for each policy.

### Time or frames used as ordering guarantees [S11]

- Waiting a tick or frame to make a workflow correct is a smell because elapsed time does not prove that navigation, persistence or another prerequisite completed.
  - **Fix:** Fix the router stack or dependency ownership; await an explicit completion contract or transition event.
- **Keep:** Animation and rendering work, documented protocol pacing, real deadlines and retry policy; test clocks that control a genuine time contract.

## Tests

_Defer to the tests skill's guide for the full rules._

### Tests whose passing result is supplied by their own setup [S19]

- A tautological assertion, decision-making mock or permissive infrastructure fake is a smell because the test can pass while the real contract is broken.
  - **Fix:** Use an independent expected result and test the real deciding implementation; use real integration machinery for query, codec or configuration-order risks.
- **Keep:** Typed doubles supplying outcomes of independently proved contracts, call assertions when the call itself is the contract, and disposable catching tests within authorized work.

### Test-only UI identifiers or fake semantics [S18]

- A test ID or harness-only accessibility attribute is a smell because it gives tests an observation channel the real user does not have.
  - **Fix:** Query by real roles and accessible names, labels or visible text; add truthful accessibility when the product needs it.
- **Keep:** Genuine production accessibility, native identity required by the platform, and an existing third-party marker only as a documented constrained fallback.

### Weakening production APIs to satisfy tests [S20]

- An optional input, fallback, exported private helper or alternate entry point added only for a fixture is a smell because test convenience has changed the production contract.
  - **Fix:** Repair setup with contract-valid data or an existing dependency seam; keep required inputs required and test through a reachable public boundary.
- **Ask:** Did a fixture or preview broaden a production contract?
- **Keep:** A real second production entry point adapted to the same contract, dedicated patch inputs, natural injectable collaborators and malformed-input tests at ingestion.

### Coverage repeated at every forwarding layer [S21]

- Tests that replay an already-proved dependency matrix at a forwarding consumer are a smell because test count grows without independent regression protection.
  - **Fix:** Find the deciding owner and existing proof; retain consumer-specific selection, sequencing or presentation tests and integration tests for a named cross-boundary gap.
- **Keep:** Different business risks, meaningful consumer decisions, end-to-end integration gaps and a tiny rule with a real contract; small code is not automatically unworthy of tests.

## Names, comments and docs

_Language-agnostic._

### Names that hide domain meaning or the actor [S22]

- Infrastructure-flavored or vague domain names are a smell because readers cannot tell which entity, actor or state the code represents.
  - **Fix:** Name the actual business concept and actor, keep raw names in adapters and use one domain vocabulary across code and tests.
- **Keep:** Required external field names at the wire boundary, established library vocabulary inside its implementation and distinct terms for genuinely different concepts.

### Comments that narrate syntax, history or process [S24]

- A comment that restates code or cites review history is a smell because it adds a second, easily stale explanation without documenting a standing constraint.
  - **Fix:** Delete it or state the verified rationale, invariant, tradeoff or compatibility constraint that future edits must preserve.
- **Ask:** Does the comment state a verified constraint that the code alone cannot express?
- **Keep:** Non-obvious rationale, truthful public contracts, standing compatibility constraints, and a short docblock on a deep module that explains hidden complexity.

### Stale documentation acting as architecture authority [S25]

- A convention, design artifact or PR description that contradicts the executing system is a smell because agents and reviewers use it to reproduce an obsolete design.
  - **Fix:** Correct or remove obsolete authority when changing the implementation; keep durable contracts and verified current rationale, not every generated design artifact.
- **Ask:** Will an agent following this document recreate the design that the implementation removed?
- **Keep:** Current operational runbooks, authoritative product decisions, useful historical evidence outside source conventions, and deliberately versioned migration documentation.

### Agent-only codes instead of readable explanations [S23]

- A report that uses private case codes or bare function names as its explanation is a communication smell because the reader must reconstruct the agent conversation to understand the claim.
  - **Fix:** Name the behavior, product decision or risk first and append its identifier only for traceability; supply operational context before code names.
- **Keep:** Stable IDs after a descriptive name, exact symbols when discussing their implementation, and compact internal machine-readable keys.
