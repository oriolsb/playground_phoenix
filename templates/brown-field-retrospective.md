# Brown Field Retrospective

An ice breaker. The retrospective is a conversation first. Use this
template only if your group needs a gentle push to find its own
questions, or to keep notes.

Group:
Date:

## 1. Share-out summary

### Primitive grades from step 3 and step 7

| Primitive | Grade in step 3: strong, partial, or absent | Grade in step 7 | Evidence |
| --- | --- | --- | --- |
| Specification | | | |
| Evaluation | | | |
| Context Boundary | | | |
| Provenance | | | |

### The three questions, in step 3 and step 7

| Question | Step 3: yes or no, and the evidence | Step 7 |
| --- | --- | --- |
| Can you merge an agent's change without reading every line? | | |
| Can an agent implement a change from one prompt? | | |
| Can you release the change without anyone watching production? | | |

### The archaeology of step 1

| Items on the list | Known | Unknown | Wrong |
| --- | --- | --- | --- |
| | | | |

### Decisions that nobody wrote down

| Decision | How you found it: the archaeology, play, code, or failed test | Decision record or source tag |
| --- | --- | --- |
| | | |

### Regeneration in step 7

| Item | Result |
| --- | --- |
| In the regeneration folder, before the agent runs, `pytest` fails with an `ImportError`: yes or no | |
| Files that the agent opened | |
| Tests that passed | |
| Tests that failed | |
| Knowledge that each failure showed | |
| Boundary terms with more than one meaning | |

### The one-prompt rewrite of step 1

| Item | Result |
| --- | --- |
| Would you merge it after the 5-minute reading? Why? | |
| Tests that failed on the rewrite | |
| Changes that the reading did not see | |
| Tests that failed because the rewrite moved a boundary name | |
| Did the agent check its own work? Where is that check now? | |

## 2. Lessons

1. Which decisions did you find that nobody wrote down? How did you find
   them? Did the archaeology list them? Did you play the game, read the
   code, or see a test fail?
2. Which primitive was the most difficult to recover from the code? Why?
3. Which rules were not possible to reach from outside? Which seams did
   you add?
4. Did the regenerated code pass your tests? And the one-prompt rewrite?
   What did each failure show? What did your reading of the rewrite tell
   you, and what did the tests tell you?
5. Which of the three questions moved toward yes today? Which one is
   still a no, and what would change it?
6. Which was easier: to write the primitives before the code (green
   field), or to recover them from code that exists (brown field)? What
   did each one cost?

## 3. Apply it in your team

| Question | Answer |
| --- | --- |
| Which component in your team does someone want to rewrite? Ask an agent to list its scars, and mark them. How long is the unknown column? | |
| Which system in your team is most similar to this brown field? It works, but it has no written primitives. | |
| Which knowledge in that system exists only in the code, or only in the memory of one person? | |
| What is the smallest first step for that system: a contract, characterization tests, or decision records? | |
| Where does your team keep decision records that you write after the code? | |
| How does your team add seams to legacy code, and keep the behavior the same? | |
| An AI coding agent changes legacy code. Which checks must pass before the change can merge? | |

## 4. What will you try?

What will you try in your team? One sentence is enough. You choose the
practice, its owner, and its start date at the workshop close, on day 3.
