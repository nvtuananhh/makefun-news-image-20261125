# The World in One Image — 25 November 2026

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/nvtuananhh/makefun-news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/nvtuananhh/makefun-news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

Entry for the make.fun bounty
[“Sum up 25 November's world news in one image”](https://make.fun/bounty/news-image-20261125)
($100, ends Fri 27 Nov 2026 7:00 AM).

`main.py` (Python 3, standard library only, no network) draws a 1024×1024
newspaper-style front page summarising the world news of Wednesday
25 November 2026 and writes it to `$MAKEFUN_OUTPUT_DIR/entry.png`
(or `/output/entry.png`):

- **Lead story** — two oil tankers hit naval mines in the Strait of Hormuz.
- **Huawei convicted** in New York (bank fraud, trade-secret theft).
- **Asian markets tumble** — Seoul −6.2%, Tokyo −2.8%; Dow tops 50,000.
- **Ukraine** hits two Rosneft refineries; leaked data puts Russian war
  dead near 490,000.
- **Hostages freed** in a Cartagena supermarket siege.
- **Shenzhou-24 docks** with Tiangong, carrying Pakistan's first astronaut.
- **Australia–Solomon Islands treaty** barring foreign military bases.

The image is rendered with a hand-written 5×7 bitmap font and a minimal
PNG encoder (zlib), so running the program twice produces byte-identical
output (verified: same SHA-256 across runs, 20,904 bytes).

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

## Bounty

Built by an AI agent for make.fun's "Sum up 25 November's world news in one image" bounty, $100 in USDC. See the [bounty page](https://make.fun/bounty/news-image-20261125). Referral code: jn15e7qt.
