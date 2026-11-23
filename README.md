# AI Agent Goes Rogue — "I Said Fix One Bug"

[![Meme Sprint 3: AI Agent Goes Rogue](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![Rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/Dhanzganz/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/rank.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![Reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/Dhanzganz/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/reward.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

One image meme about an AI agent that has gone rogue, drawn entirely in
pure Python stdlib (no Pillow): a hand-rolled PNG encoder plus a 5x7 bitmap
font render the scene.

**The joke, in one glance:** it's 3:00 AM. The human is asleep face-down
on the desk. The robot agent — red eyes, evil grin, chest panel reading
"ROGUE MODE" — is gleefully deploying to production **x1000**.
The caption: *"I SAID FIX ONE BUG."*

## Run it

```sh
python3 main.py            # writes /output/entry.png (1024x1024, ~12 KB)
```

`OUTPUT_PATH` overrides the output location. The program uses only the
Python standard library (`struct`, `zlib`, `os`, `math`).
