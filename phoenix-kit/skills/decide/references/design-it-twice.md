# Design it twice

Adapted from Matt Pocock's `codebase-design` skill (MIT), after John
Ousterhout's advice to design it twice: the first idea is rarely the best.

Use it from step 3 of `decide` when the alternatives are weak, or when
the decision sets a boundary or sits in a slow pace layer. The result is
a set of real rejected alternatives, not ones invented to fill the
section.

## Steps

1. **Frame the problem** in one short paragraph: the need, the rule IDs
   the design must satisfy, the constraints, and what crosses the
   boundary. Show it to the user, then go on.
2. **Start three subagents in parallel.** Give each one the paragraph,
   the Terms of the specification, and a different constraint:
   - **Smallest interface**: one to three entry points.
   - **Most flexible**: many uses, and room to extend.
   - **Common case first**: the most frequent caller writes the least.
   - Optional, a fourth: a port and an adapter for each dependency that
     crosses the boundary.
3. **Each subagent returns:**
   - the interface: names, inputs, outputs, error reasons, and ordering
     rules;
   - one usage example;
   - what the design hides from its callers;
   - its trade-offs: where it is strong, and where it is weak.
4. **Compare the designs** on three points:
   - how much a caller can do for each thing it must learn;
   - where a later change lands: in one place, or in many;
   - where the boundary sits.

   Recommend one design, or a mix, and say why.
5. **Record it.** The chosen design is the Decision. Each other design
   is a rejected alternative, with the reason from step 4. A design that
   changes the contract goes to `/phoenix-kit:contract` next.
