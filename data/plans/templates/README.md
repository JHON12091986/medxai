# Plan Templates

This directory contains pre-built plan skeletons that `GoalDecomposer` will use to auto-generate plans based on matched triggers.

## Schema

Each JSON file in this directory represents a plan template and follows this schema:

```json
{
  "template_id": "string",
  "name": "string",
  "description": "string",
  "trigger_keywords": ["string"],
  "steps": [
    {
      "step_id": "string",
      "description": "string",
      "tool": "string",
      "args_template": {},
      "depends_on": ["string"],
      "timeout_seconds": 30,
      "success_criteria": "string"
    }
  ]
}
```

- **template_id**: Unique identifier for the template.
- **name**: Human-readable name.
- **description**: Description of what the plan does.
- **trigger_keywords**: A list of words that trigger the selection of this template.
- **steps**: An array of step definitions representing the workflow.
  - **step_id**: Unique identifier for the step within the plan.
  - **description**: Explanation of what this step does.
  - **tool**: The agent tool to be invoked.
  - **args_template**: A key-value mapping of arguments to pass to the tool. Variables can reference previous outputs (e.g., `$step_id.output.key`).
  - **depends_on**: An array of `step_id`s that must complete successfully before this step can begin.
  - **timeout_seconds**: Maximum allowed duration for the step before timing out.
  - **success_criteria**: Natural language description of what constitutes a successful execution of this step.