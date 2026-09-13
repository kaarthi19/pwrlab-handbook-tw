# Admin request — AdvAppliedEnergy_Pathways_2025

**Repo:** https://github.com/Power-Lab/AdvAppliedEnergy_Pathways_2025
**Node:** `pwrlab.ucsd.edu` (169.228.63.79) — Ubuntu 24.04.4 LTS, 72 × Xeon Gold 6240, 187 GB RAM
**Installed at:** `/home/taw021/AdvAppliedEnergy_Pathways_2025` (user `taw021`)
**Status:** Fully operational and validated. The Gurobi licence is installed and working
(academic, expires 2027-09-13), the Zenodo inputs are in place, and the model reproduces
the README's published demo figures. The only outstanding item is disk space — see
Action 2.

---

## What is already done (no admin action needed)

The full Python stack was installed rootlessly and is confirmed working — the model runs
through data initialization and stops only at the missing Zenodo inputs.

- `uv` 0.12.10 → `~/.local/bin/uv`
- CPython 3.9.25 (uv-managed standalone build; system Python is 3.12, which cannot build the pinned `pandas==1.5.3`)
- venv at `AdvAppliedEnergy_Pathways_2025/.venv`
- All packages installed from manylinux wheels — **no GDAL/PROJ/GEOS system libraries were required.**

Two pins from the README needed correction:

| README pin | Installed | Reason |
|---|---|---|
| `geopandas=0.12.3` | `geopandas==0.12.2` | 0.12.3 was never published to PyPI |
| (not listed) | `pypinyin`, `python-Levenshtein`, `pyparsing` | imported at module level by `pycode/callUtility.py` but absent from README §2.2 |

Note also that `geopandas`/`shapely` are **not** optional even for solver-only runs:
`pycode/callUtility.py` imports them at module scope and every other module imports
`callUtility`. `matplotlib`/`geoplot`/`mapclassify` are likewise pulled in because
`testMultiYear.py` imports `plotResult.py`.

---

## Action 1 — Gurobi licence: resolved

A licence was activated on 2026-09-13 and is working. No action needed; recorded for
awareness.

| Field | Value |
|---|---|
| Licence ID | 2863658 |
| Type | `ACADEMIC` |
| Host | `pwrlab` |
| User | `taw021` |
| Expires | **2027-09-13** |
| File | `/home/taw021/gurobi.lic` |

Note the system also has a full Gurobi 11.0.1 at `/opt/gurobi1101/`. Its `gurobi_cl`
fails with `error while loading shared libraries: libgurobi110.so` unless
`LD_LIBRARY_PATH=/opt/gurobi1101/linux64/lib` is set — worth adding to
`/etc/profile.d/` if anyone is expected to use the command-line tools. The model itself
does not need this: it uses the pip `gurobipy` in the project venv, which bundles its own
library.

> **This is a named-user licence, locked to `HOSTNAME=pwrlab` and `USERNAME=taw021`.**
> Other accounts on this node cannot use it — each person needs their own key. If the lab
> expects several people to run this model here, a **WLS (Web License Service)** or
> floating licence would be the better arrangement.

## Action 2 — Zenodo inputs: done, but disk is tight

The model inputs are downloaded, checksum-verified against Zenodo's published MD5, and in
place. No action needed — recorded here for awareness.

| Folder | Size | Files |
|---|---|---|
| `data_pkl` | 3.3 GB | 18 |
| `data_mat` | 868 MB | 21,514 |
| `data_shp` | 42 MB | 116 |

Only the three data folders were extracted; the Zenodo archive also contains a full copy
of the Git repository, which was deliberately not unpacked over the working checkout. The
2.3 GB zip was deleted after extraction. `outputs.zip` (2.2 GB, the paper's published
results) was **not** downloaded — it is only needed to reproduce the paper's figures.

**The disk is now the thing to watch:**

```
/dev/mapper/ubuntu--vg-ubuntu--lv   98G   85G  8.4G  91% /
```

Under 9 GB free on a shared node, and `data_res` grows with every run. **This is no longer
hypothetical: on 2026-09-13 a single 7-day, four-period validation run exhausted the disk
part-way through and had to be killed.** That run began with 9.7 GB free, so a complete
four-decade 7-day run needs upwards of 10 GB of working space — and a full-year run needs
far more.

This is now the one thing blocking routine use of the model on this node. A scratch or
data volume mounted for `data_res` is the clean fix. Failing that, users must copy results
off and delete them after every single run, and a full-year scenario is simply not
runnable here.

## Action 3 — Optional: compute headroom

`pwrlab` has 72 cores and 187 GB of RAM, comfortably above the README's reference machine
(32 cores / 256 GB), so full-year runs should beat the quoted timings on CPU — though RAM
is the tighter constraint of the two.

- Demo run (7 days × 4 periods): ~30 min on 10 cores.
- Full-year run (365 days × 4 periods): **up to 20 hours** per scenario on the reference
  machine. The reproduction set in README §5.3 is 13 such scenarios.

There is **no scheduler on this node** — no Slurm, no queue — so nothing prevents one user
taking all 72 cores and exhausting RAM for everyone else. If full-scenario sweeps are
going to run here, a scheduler or an agreed core cap is worth setting up. In the meantime
the user guide (`docs/NODE_GUIDE.md`, Part 12) documents capping Gurobi with
`setParam('Threads', N)` and using `nice`.

---

## How to run once the above is resolved

```bash
source /home/taw021/AdvAppliedEnergy_Pathways_2025/env.sh
python testMultiYear.py
```

`env.sh` activates the venv, sets `PYTHONPATH` to the repo root (required — `plotResult.py`
uses `from pycode.callUtility import ...`), sets `MPLBACKEND=Agg` for headless operation,
and cd's into `pycode/`.

Expected sanity check in `data_res/test_<date>_7days_all_years_pc_*/stat_national.csv`:
onshore wind 610 / 1257 / 1610 / 2369 GW across the four decades.
