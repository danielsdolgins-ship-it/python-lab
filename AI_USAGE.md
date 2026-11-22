# AI Usage Disclosure

<!--
Fill in this file before you submit. Submissions without it are not graded.
If you used no AI tools, delete everything below and write only:
No AI tools were used.
-->

## Tools used

- Tool and version (e.g. ChatGPT GPT-5, Claude, GitHub Copilot): ChatGPT

## Conversation links

- Link 1: https://chatgpt.com/share/6b02dd2c-e394-83ed-aa02-fde7a2835c0c

## What I used them for

- For strucuring and validating query options, and also for normalizing single vs list query inputs (query.py)
- For structuring main, exit codes and removing the errors.log file handler (flight_parser.py)

## Which parts of the code were AI-generated or substantially AI-assisted

| File | Function or part | How (generated / modified / explained) |
| --- | --- | --- |
| query.py | run_query and run querries | modified and explained |
| flight_parser.py | flight_parser and finally handler in main | modified and explained |
## Key prompts

1. how do i handle exit codes 0, 1, 2 and close errors.log handler in a finally block?
2. i need for invalid queries to still exit 0, bad cli args exit 2 and file, json, runtime errors to exit 1. also flags are -i, -d, -j, -a, -o, -q, -r, main returns the code and logger uses this %(asctime)s %(levelname)s %(message)s with datefmt="%Y-%m-%d %H:%M:%S

## What I changed or verified myself

I used the suggestions to fit requirements for CLI flags, log formatting, errors.log placement, and exit codes
