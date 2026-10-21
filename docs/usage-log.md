# Usage log

One line per job: the date, the job, the model, and what it used. The weekly percentage comes from the app's usage view, and tokens from `tools/usage_scan.py` (list-price weights are relative and unverified). It is read only when planning a week's budget (`CLAUDE.md`, Using tokens well).

| Date | Job | Model | Used |
| --- | --- | --- | --- |
| 20-21 Oct | The week to Wednesday: stairs, walls, fourteen craft studies, the main session | Fable, Opus | the weekly limit to 83%, Fable's to 100%. The main sessions were 54% of usage (mean context 562k, 2,835 requests) and subagents 46%. Each craft study processed 22 to 57 million tokens; its final context was about 450k |
| 22 Oct | The token study | Opus | final context 261k |
