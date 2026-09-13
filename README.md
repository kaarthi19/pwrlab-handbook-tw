# The pwrlab Handbook

A complete guide to using the **pwrlab** compute node and running the
[AdvAppliedEnergy_Pathways_2025](https://github.com/Power-Lab/AdvAppliedEnergy_Pathways_2025)
model — China's provincial-resolution, hourly capacity-expansion LP.

Written for someone with no prior Linux, terminal or remote-server experience. It both
**teaches** (how the optimisation works, how the machine works) and **dictates** (the exact
commands to type).

## Read it

| | |
|---|---|
| **[docs/NODE_GUIDE.md](docs/NODE_GUIDE.md)** | The source. GitHub renders it directly — start here. |
| **[Read it on the web](https://kaarthi19.github.io/pwrlab-handbook-tw/)** | Published via GitHub Pages. |
| **[docs/index.html](docs/index.html)** | The same page as a self-contained single file. No JavaScript, no CDN — download it and it works offline, forever. |

## What's in it

- **Quickstart** — the nine commands, on one page
- **Parts 1–3** — the node, connecting over SSH from Windows, using Claude Code
- **Parts 4–5** — *how the model works* (the LP, its variables, the binding constraint) and
  *how the machine works* (processes and `SIGHUP`, RAM vs disk, virtualenvs)
- **Parts 6–14** — the terminal, tmux, editing, file transfer, running, scenarios, results,
  sharing the machine
- **Part 15** — the optional [agentic-optimization](https://github.com/Power-Lab/agentic-optimization) framework
- **Parts 16–17** — reading errors, and a cheat sheet

## Setup files

`setup/` holds what makes the model run on the node:

| File | Purpose |
|---|---|
| `env.sh` | Activates the venv, sets `PYTHONPATH` and `MPLBACKEND`, cd's to `pycode/` |
| `requirements-core.txt` | Solver and data stack, pinned |
| `requirements-geo.txt` | Geospatial and plotting stack, with two corrections to the model's README pins |
| `SETUP_ADMIN_REQUEST.md` | Standing note to the sysadmin — currently: disk space |

Two pins in the model's own README are wrong and are corrected here: `geopandas 0.12.3`
was never published to PyPI (use `0.12.2`), and `fiona` must be `<1.10` because 1.10
removed `fiona.path`, which geopandas 0.12.x still calls.

## Validation

Run as committed, the model reproduces the published demo figures:

| Decade | Onshore wind | Utility solar | New transmission |
|---|---|---|---|
| 2030 | 610 → **608.9** | 234 → **234.1** | 27 → **27.6** |
| 2040 | 1257 → **1260.9** | 250 → **249.8** | 93 → **92.3** |

## Rebuilding the HTML

`docs/index.html` is generated from the markdown. After editing the guide:

```bash
pip install markdown
python docs/build_standalone.py
```

The markdown is the single source of truth; `docs/index.html` is a build artifact, and
`docs/style.css` holds the styling. The build needs no network and no JavaScript — the
published page is plain pre-rendered HTML.

## Published

GitHub Pages serves `docs/` on the `main` branch:
**https://kaarthi19.github.io/pwrlab-handbook-tw/**

`docs/.nojekyll` stops Jekyll from reprocessing the pre-rendered HTML.
