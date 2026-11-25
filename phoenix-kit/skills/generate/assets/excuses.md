# Generate — the excuses, and what to do instead

Each row is an excuse that an agent gave, or nearly gave, in the
end-to-end runs of this kit. The form comes from the rationalization
tables of obra/superpowers (MIT): name the excuse, give the reason, give
the action.

| Excuse | Why it fails | Do this |
| --- | --- | --- |
| "The removal touched only the unit's files, so I judged it the unit's hole and proceeded." (an end-to-end run, word for word) | The person who removed the unit knows what it should break. A judgement of the cause replaces their decision. | Stop. Report the checker output. The person decides. |
| "The cause looks harmless." | Harmless to whom? A wrong cause here regenerates the wrong unit. | Stop, as above. |
| "The approval line is there, so the suite is approved." | The line may predate the last change to the suite. | Run `check approval verify`. Its result decides. |
| "The test is wrong; a small edit makes it match the rule." | An approved test is part of the oracle. Editing it changes the oracle. | Report a specification failure, with the test and the rule. |
| "The suite passed, so the rules are met." | The suite proves only what it checks. Two end-to-end runs had wrong code that passed every test. | Run the rule review of step 7. |
| "The reviewer says the suite passed with this bug; I fix the code and move on." | The fix is right, but the suite still has the gap. | Fix the code and report the gap as an Evaluation gap with its rule ID. |
| "I updated the files." | Memory is not evidence. | Report the command output that shows it. |

Red flags in your own reasoning: "I judged", "harmless", "probably",
"should pass", "small edit", "just this once". When one appears, run the
check that decides the question, and report its output.
