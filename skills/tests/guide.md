# Testing guide

Tests protect supported behaviour, survive implementation changes, and fail for a reason a maintainer can read. Coverage and mutation scores are diagnostics, not targets.

## How to use this guide

Rules `G01`-`G12` are stable IDs: cite them in findings and contributions. Read the guide fully once per audit, then work test by test from the [self-audit](#8-self-audit).

| You are... | Do |
| --- | --- |
| Auditing or improving tests | Follow [the audit phase](audit.md): apply section 8 to the scoped tests and the production behaviour they touch. |
| Designing tests | Agree the public contract first; choose coverage by ownership (G03), not by file or layer count. |
| Fixing a failure | Decide whether production behaviour, the expectation, or setup is wrong before changing an assertion. A green suite is not permission to weaken a contract. |
| Disagreeing with a rule | Follow the disagreement branch in [the audit phase](audit.md). Evidence can narrow a rule; a wrong rule is corrected, not obeyed. |

This file is the authoritative testing ruleset. Personal learning ledgers, contribution records, and historical archives are optional evidence, not additional rules or routine audit context. Use them only when supplied by the user for a matching disagreement or provenance question.

## 0. Why a test persists

### G12: Persist only contract tests

A **catching test** checks a change while it is being made. Use it freely during implementation, then delete it. A **contract test** keeps an agreed decision out of reach of whoever changes the code next. Persist a test only when all three hold:

1. **Outside authority:** the expected value comes from someone other than the implementer: an external system, recorded production data, or an owner's product decision (G04). A value copied from the code's own output only detects change.
2. **Protected:** the implementer may not change it. A failure is a question for the authority, not a bug in the test.
3. **Worth the ruling:** a failure should force a decision from the authority. If nobody would need to decide, it is not a contract.

Each contract test names its authority. What the test protects is the authority's cases and expected values, not the file: setup and fixture code is ordinary implementation. Whoever implements the code under test never supplies an expected value; a value with no authority behind it is not a contract value, whatever file it sits in. When a feature is retired, delete its contract tests with it. When code is rewritten, move only the external data the tests rely on. A test that fails G12 is deleted after use; G01-G11 then do not apply to it.

## 1. Behaviour and ownership

### G01: Prove a supported contract, not an implementation transcript

For each test, name a plausible production regression and the observable assertion that detects it. Observables: a return value, public error, rendered state, persisted result, emitted intent, or contractual boundary payload.

A **mirror** reproduces the algorithm to calculate its expectation, or asserts a sequence of internal calls without an independent contract. Calling a selector with chosen inputs and asserting an independently derived result is not a mirror.

**Double-change smell:** a behaviour-preserving refactor that forces an expectation change suggests the expectation encodes mechanism. This is diagnostic, not proof. Deliberate public API changes legitimately update tests.

Assert meaningful results. "Does not throw" or "was called" earns its place only when non-failure or occurrence is itself the contract and the scenario reaches that path.

### G02: Test through a natural, reachable public boundary

A **seam** is the natural public boundary where behaviour is observed.

Exercise domain rules through the real public domain API, and reach code only through it: exporting a private helper, adding a test-only entry point, grepping source text, or forcing production into a different abstraction is not a test boundary.

Extract a helper only for a coherent production responsibility or interface benefit; branch count and difficulty writing a test are clues, not refactoring instructions. Use an existing selector's `resultFunc` when isolating its pure projection is the intended seam; leave ordinary functions as functions rather than converting them to selectors for tests.

Validate **reachability**: a component test represents states the real navigation, provider, or state machine can produce. Test a mounted transition when it differs from initial render. Keep intentionally supported fallback states even when the common path avoids them.

When an internal structure is genuinely load-bearing, first test its consequence, such as work completing without deadlock. Prefer that to asserting its shape, such as "uses separate worker objects". A structural assertion is a last resort for a named risk with no reliable behavioural observation; state its coupling and limitation. Source shape alone is not regression proof.

### G03: Coverage follows contract ownership and marginal proof

Before adding or retaining coverage, fill the ownership table:

| Behaviour | Owning boundary | Existing proof | Consumer adds | Integration risk |
| --- | --- | --- | --- | --- |
| Rule or outcome | Public API deciding it | Actual test location, not assumed coverage | Decision beyond forwarding | Risk isolated contracts cannot prove |

- **Owner:** test application-owned decisions and outputs here, with real implementations.
- **Consumer:** mock independently proved contracts and test the consumer's additional decision: selection, presentation, error mapping, sequencing policy, or enrichment.
- **Pure forwarding:** usually no further test. Returning a canned mock result is not independent proof.
- **Integration:** use real collaborators for a named gap, such as ORM query semantics, codec compatibility, dependency injection resolution, or boundary translation. Leave the full domain matrix to its owner.

**Locating the owner:**

- Inspect claimed dependency coverage before deleting a consumer's only protection.
- A schema's validation belongs where that schema is configured and applied; downstream layers inherit it rather than each repeating its rejection matrix.
- TypeScript is erased: untrusted runtime input still needs validation and evidence at its owner.
- A database constraint replaces application duplication only when it really enforces the requirement and the boundary's configuration is proved.
- Reassess ownership after moving or consolidating logic. When consumers mock a shared utility, its decisions need real proof elsewhere. Keeping both a direct and a higher-level matrix is a decision, not a default: existing real public-boundary tests may already cover the shared contract.

**Size is not value.** A one-row truth table, simple mapping, or one-line guard can implement a valuable application contract; many branches guarantee nothing. Ask the **counterfactual**: what independent protection remains if this test disappears?

**Case selection.** Separate tests for distinct business risks even when they traverse the same branch; combine assertions that explain one coherent proposition. Start from the positive result the caller needs, then add negative cases only for separate supported risks. Keep result-level protection rather than replacing it with incidental exclusions.

For a cohesive public read contract, first consider one representative exact-result case: a discriminating fixture (for example out-of-order, gapped, deleted, and foreign records together) whose expected result independently exposes the related failures without reproducing the algorithm in the expectation. Retain further cases only for distinct scenarios, risks, or diagnostic needs, not one per internal layer. This does not apply when the combined fixture masks a failure, a distinct transition or rejection needs its own setup, or diagnosing separate business risks becomes harder. Real database coverage still requires a named query or translation risk, not merely a database source.

## 2. Assertions

### G04: Make the oracle independent, specific, and scoped

The **oracle** is the expected result. It derives from the contract and deliberate fixtures, not from the system under test or a copy of its algorithm. Use an exact expected object when all its fields form the contract; use a focused match when unrelated fields may evolve.

- **Numbers:** exact results for exact arithmetic. For floating point, choose tolerance from the domain's precision requirement, not a universal epsilon. Distinguish dependency conversion constants from application-owned unit selection, rounding, or conversion policy.
- **Errors:** assert the claimed error code, type, or message detail, rather than merely "throws" or "failed". Leave stack traces and incidental wording unlocked.
- **Writes:** meaningful persisted or outbound payloads, not only call counts.
- **Reads:** supply scenario data and assert the owned result. Assert read arguments when request selection is itself the contract; a canned result alone does not prove query correctness.
- **Order:** assert order, deduplication, or permutation invariance when consumers depend on it. Assert the contract, not the internal sorting, hashing, or traversal technique.
- **Scope:** a local boundary promise does not justify a global ban on every similar call or field.

**Negative assertions need a live scenario.** Supply gating inputs at the current boundary and show the action reached the gate; with the prerequisite absent, "nothing happened" passes **vacuously**.

When unsupported behaviour is removed, delete its obsolete proof rather than flipping "happens" to "does not happen". Retain an absence test only for a durable supported invariant, such as preventing duplicate billing.

```text
Weak:   attempt submission without a loaded form; assert no save
Strong: load a valid form with an expired approval; submit;
        assert the approval error and no save
```

## 3. Dependencies and test doubles

### G05: Mock contracts; do not simulate what the test needs to discover

For catching tests, any double that speeds up validation is fine. The remaining rules in this section govern contract tests.

Keep the system under test real. Choose real collaborators or doubles by risk, rather than a blanket "mock every sibling" or "mock nothing" policy.

- Real deterministic domain code when proving its decisions.
- Doubles for independently tested dependencies when isolating a consumer decision.
- Native/platform APIs and generated/external codecs are reasonable isolation boundaries; prove relevant compatibility separately when the application relies on it.

**Doubles supply outcomes, not decision logic.** A domain mock returns a risk decision; it does not reproduce the scoring formula. A passive stub usually needs no tests. A stateful fake or simulator that makes decisions needs evidence for those behaviours, or it becomes an untested second implementation.

**Doubles honour real signatures.** Prefer typed dependency factories and narrow interfaces; a required constructor change updates setup honestly. Positional `undefined` padding, casts through `any`/`never`, and invented methods silence types rather than satisfy them. Use a framework testing module when container resolution or lifecycle is the risk; manual construction suffices for ordinary class behaviour.

Use narrow, typed operation contracts and dependency injection where they serve a production responsibility. A double supplies an outcome without recreating endpoint dispatch or domain decisions. This does not require replacing a suitable generic client or extracting an interface solely for tests.

**Module mocks stay visible** near imports and follow the runner's hoisting rules. Declare per-test outcomes in the scenario, not in a hidden shared implementation.

### G06: Match fidelity to the integration risk

Ask: **could this fake accept an operation the real dependency would reject or interpret differently?** If yes, a passing isolated test cannot establish that contract.

ORM mocks that accept arbitrary query objects do not prove query semantics. Use a real database/repository test for filters, joins, constraints, and mapping whose correctness depends on that machinery; consumer tests can then mock the proved repository contract without repeating its matrix.

Captured production data improves input realism; it does not prove a simulator's sequencing, timing, or error behaviour. Assess **data fidelity** and **behavioural fidelity** separately. Use focused recorded fixtures or real boundary tests where that distinction matters.

## 4. Production contracts

### G07: Push invalid states left without inventing test-only states

Prefer types and API design for statically knowable distinctions: branded IDs, discriminated states, named parameters, and constructors that establish invariants. Keep runtime checks at untrusted boundaries and test application-owned enforcement there.

A required production input stays required when a fixture, demo, or isolated render struggles with it. Identify the real producer, caller, meaning of absence, and owning boundary; repair setup with contract-valid data or a compatible dependency mock, and preserve the behaviour test.

An assertion cast is not proof of a domain value. Construct valid values through supported factories or constructors. Test malformed representations at their real ingestion boundary, not by casting impossible states into unrelated consumers.

Remove runtime coverage only when enforcement has actually moved to types or another proved boundary. A handwritten runtime enum list or mirrored schema is still executable logic; a type annotation does not guarantee it stays aligned.

## 5. Names, structure, and fixtures

### G08: Make the scenario and failure reason readable

**Contract-sentence naming.** Read the full `describe` and `it` path aloud. It forms one precise contract sentence. Use domain vocabulary and identify **owner, role, and instance** when nouns could refer to different entities or moments. Lead with the distinguishing outcome. Titles carry the proposition, not "works", framework mechanics, dash annotations, or implementation details.

```text
Account contact address
  when the owner has approved a newer address
    uses the newer address for delivery
```

Name only what the fixture encodes. Put a non-obvious business rationale in a short comment when naming and data cannot explain it.

**Grouping.** Group by public behaviour, with affirmation/rejection contexts or discriminated variants where they clarify policy. Put shared conditions in nested `describe` blocks when they clarify several cases; use broader parents when siblings prove independent behaviours. Test counts and nesting depth follow the behaviour, with no arbitrary thresholds.

**Tables** suit independent cases with genuinely shared setup, action, and assertion; give each row a diagnostic name. Prefer explicit scenarios for async workflows and state transitions. A table is defensible there only if isolation and failure diagnosis remain equally clear. Shared implementation paths do not make distinct business propositions interchangeable.

**Fixtures.** Keep scenario-defining data beside the test. Shared `beforeEach` establishes the neutral environment, not hidden business variants. Use local setup factories for per-test isolation and explicit returned collaborators; they do not guarantee garbage collection.

Start with inline data. Extract a typed override factory when repeated valid boilerplate obscures scenarios: minimal valid defaults plus explicit overrides, rather than many scenario-specific factories. The field that distinguishes success from failure stays visible in the test, and partial data is completed honestly rather than cast into a complete domain object.

## 6. Asynchronous behaviour

### G09: Prove ordering and lifecycle, not incidental timing

Prefer controllable events, deferred promises, and observable states over sleeps. Test ordering when it protects a contract: releasing a resource after failure, cancelling superseded work, withholding a write until acknowledgement.

Use fake timers when the code and harness can advance all relevant clocks and scheduling. They do not universally stop async progress; mixed real I/O and virtual time can deadlock or mislead. Where the integration requires real scheduling, use short real-time budgets with adequate margin, clean up handles, and assert outcomes rather than exact elapsed milliseconds.

A timeout test reaches the waiting state and pins the timeout failure, rather than passing on an unrelated setup error. Configure only values that define the scenario. An injected clock or configurable timeout needs a legitimate interface responsibility; a public timing knob added solely for tests is a test-only state (G07).

## 7. UI, observability, and dependency assumptions

### G10: Observe the contract of the boundary you are testing

**UI:** query by role and accessible name, then labels, visible text, or other user-observable semantics. Assert a visual cue's semantic state when that represents the contract; pin pixel values or styling classes only when the visual property is the requirement.

Product UI carries genuine accessibility and production state, not `data-testid` attributes, hidden elements, test-only IDs, harness-only semantic attributes, or misleading ARIA semantics added for tests. An existing third-party marker may be a constrained fallback where no meaningful query exists; document the limitation rather than multiplying markers.

**Trigger-driven adapters:** test owned input translation, edge detection, deduplication, and release/cleanup through observable effects. An adapter that only forwards an event remains subject to G03; its architectural position does not earn it a test.

**Telemetry:** test application-owned operational, product, or privacy decisions and their meaningful payloads. These include when an incident is reported, what context is attached, and what sensitive data is excluded. "Logger was called" or "instrumentation exists" is not enough, and lower-layer error matrices are not re-proved just to show reporting.

**Failure ownership:** malformed transport representation, domain errors, workflow states, form validation, and persistence failures have different owners. Test the owned public failure precisely, then application-owned enrichment or reporting once. Follow the project's error model rather than imposing a new architecture through tests.

**Dependency assumptions:** separate application regression coverage from **probes** of a library or platform assumption. A probe documents an upgrade-sensitive fact and states the assumption, relevant version/environment, and when to rerun it. A skipped or manual probe is optional, not silent proof. Application-owned algorithm selection, configuration, or translation still needs normal regression coverage.

## 8. Self-audit

Answer for each scoped test. Done when every item has an answer grounded in inspected code, and item 12 names a counterexample or reports none. This is a self-audit, not a requirement to narrate every passing test.

0. **Persistence:** is this a contract test under G12? Name its authority. Otherwise delete it after use and skip the remaining items. (G12)
1. **Contract:** what supported observable behaviour does this protect? (G01)
2. **Reachability:** can a real caller produce the fixture and reach this public seam? (G02, G07)
3. **Ownership:** where is the decision made; what existing test already proves it; what does this test add? For a cohesive read contract, is there one representative exact-result case before split cases? (G03)
4. **Counterfactual:** name a plausible regression and show exactly which assertion would fail. If unexecuted, label it hypothetical. (G01, G04)
5. **Oracle:** are the expectation and negative-test prerequisites independent and meaningful? (G04)
6. **Fidelity:** could a double accept something the real dependency rejects; does it duplicate production logic? (G05, G06)
7. **Contract integrity:** did test convenience widen a production API or bypass an invariant? (G07)
8. **Readability:** do the full title and visible fixture describe one coherent proposition and its distinct risk? (G08)
9. **Lifecycle:** are ordering, timers, cancellation, and cleanup controlled at the appropriate seam? (G09)
10. **Boundary:** is the observation a real UI, operational, or dependency contract rather than framework mechanics? (G10)
11. **Verification:** what actually ran, what failed before, and what passed after? (G11)
12. **Challenge:** would applying a guide rule remove unique protection, force unsupported design, or create redundant/brittle tests? Name the counterexample or report no evidenced challenge. Use the audit phase's evidenced-disagreement branch. A learning records evidence and is never invented to fill a quota.

A test may earn its place despite a heuristic. Explain the concrete risk and tradeoff rather than counting branches, layers, assertions, or cases.

## 9. Implementation and verification

### G11: Agree the contract, then test in vertical slices

Before writing a test, record the public seams under test and obtain the user's confirmation unless those seams are already approved in the active contract. Temporary catching tests stay within the approved scope. Explicit authorization for a bounded experiment permits its stated seam and scope. A new seam, protected expected value, or public interface returns for a ruling.

TDD runs **caller contract, one test, observed failure, minimum implementation, observed pass, refactor**, one vertical slice at a time; a horizontal batch of speculative tests waits until the API and behaviour are deliberate.

Every test written while coding is a catching test unless it qualifies under G12. Delete catching tests after validation. Only contract tests are committed. Refactor while green without changing approved behaviour, interfaces, or protected expectations.

A test added during review or a later approved TDD case may already pass because the behaviour exists. Keep it only for independent contract value under G12. Report it as already-green regression coverage, not a red-green cycle. Never fabricate failure evidence or change correct production code to manufacture red.

Before quality rewrites, run the relevant baseline; if it fails, identify and report the failure before unrelated test cleanup. After changes, run focused validation and relevant type checks, expanding to integration or broader tests when changed boundaries justify it. State commands, results, and anything not run.

Reapply section 8 after fixing a finding. Improving a test means more useful proof or less unnecessary coupling. A pass or a higher score alone does not establish improvement.
