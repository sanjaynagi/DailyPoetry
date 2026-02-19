### Project management
	•	For any sigificant work create a plan.md and discuss this with the user to achieve alignment before starting work. This should include a clear definition of the problem, proposed solution, and success criteria.
	•	Maintain a timestamped worklog in strict reverse chronological order.

### Engineering principles
•	Use discernment and good judgement to write code that is correct, maintainable, and efficient, while avoiding unnecessary complexity or over-engineering.
•	Prioritize semantic correctness, well-defined invariants, and clear error handling over micro-optimizations or clever tricks.
•	Maintain inter-linked docstrings and use comments where they add context and explanation, but avoid redundant or obvious comments that do not enhance understanding.
•	Structure code to be modular, with coherent responsibilities, good separation of concerns, and an architecture that can be extended without large-scale rewrites.
•	Apply DRY carefully: factor out shared logic when it improves clarity and maintenance, but avoid over-abstraction or generic frameworks that obscure intent.
•	Aim for readable, explicit code with simple control flow and minimal “magic”; prefer straightforward implementations to compact but opaque idioms.
•	Consider algorithmic time and memory complexity when choosing data structures and approaches, especially for code on critical paths or large problem sizes.
•	Keep implementations concise but not cryptic; remove dead or unused code and avoid unnecessary indirection.
•	For tests, prefer simple, direct assertions that fail fast; test code should not be defensive, over-general, or attempt to mask or recover from failures.
•	For APIs and function interfaces prefer defined contracts with clear error states over flexible but loosely defined behavior that attempts to infer intent or handle edge cases implicitly.
•	Where there is likely to be a long running process and it can be parallelised use multiprocessing with queues to distribute work across all available CPU cores.