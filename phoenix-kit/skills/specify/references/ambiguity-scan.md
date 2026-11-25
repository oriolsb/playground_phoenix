# Ambiguity and coverage scan

Taxonomy from the `clarify` command of GitHub Spec Kit (MIT), trimmed to
what a Phoenix specification needs. For each category, mark Clear,
Partial, or Missing. Ask about a Partial or Missing category only when the
answer changes scope, observable behavior, or compatibility.

Functional scope and behavior:
- Core goals and success criteria
- Explicit out-of-scope declarations
- Roles or actors, and how they differ

Domain and data:
- Entities, attributes, relationships
- Identity and uniqueness rules
- Lifecycle and state transitions
- Data volume and scale assumptions

Interaction:
- Critical journeys and sequences
- Error, empty, and loading states

Operational limits:
- Performance (latency, throughput)
- Scalability (limits)
- Reliability and availability (recovery expectations)
- Observability (which signals)
- Security and privacy (who may do what, data protection)
- Compliance constraints

Integration and external dependencies:
- External services and their failure modes
- Import and export formats
- Protocol and versioning assumptions

Edge cases and failure handling:
- Negative scenarios
- Rate limits
- Conflicts (for example, two commands at the same time)

Constraints and trade-offs:
- Technical constraints that are requirements
- Explicit trade-offs and rejected alternatives (these become decisions)

Terminology:
- Canonical terms
- Synonyms to avoid

Completion signals:
- Each rule is testable
- A measurable definition of done
