# Using the `pwrlab` Node — A Complete Beginner's Guide

Everything here is specific to this machine and this model. Parts 1–3 get you connected
and working; after that, jump to whatever you need.

---

## Contents

- **[Quickstart](#quickstart)** — the whole workflow on one page
- **Part 1 — [What you are working with](#part-1--what-you-are-working-with)**
- **Part 2 — [Connecting to the node](#part-2--connecting-to-the-node)**
- **Part 3 — [Using Claude Code over SSH (Windows)](#part-3--using-claude-code-over-ssh-windows)**
- **Part 4 — [How the model works](#part-4--how-the-model-works)**
- **Part 5 — [How the machine works](#part-5--how-the-machine-works)**
- **Part 6 — [Working in the terminal](#part-6--working-in-the-terminal)**
- **Part 7 — [Where everything lives on this account](#part-7--where-everything-lives-on-this-account)**
- **Part 8 — [tmux: the single most important tool here](#part-8--tmux-the-single-most-important-tool-here)**
- **Part 9 — [Editing files on the node](#part-9--editing-files-on-the-node)**
- **Part 10 — [Moving files between your laptop and the node](#part-10--moving-files-between-your-laptop-and-the-node)**
- **Part 11 — [Running the model](#part-11--running-the-model)**
- **Part 12 — [Changing the scenario](#part-12--changing-the-scenario)**
- **Part 13 — [Watching a run and reading the results](#part-13--watching-a-run-and-reading-the-results)**
- **Part 14 — [Sharing the machine](#part-14--sharing-the-machine)**
- **Part 15 — [Optional: the agentic-optimization framework](#part-15--optional-the-agentic-optimization-framework)**
- **Part 16 — [When things go wrong](#part-16--when-things-go-wrong)**
- **Part 17 — [Cheat sheet](#part-17--cheat-sheet)**

---
# Quickstart

The whole workflow on one page. Every step is explained properly later — Part 11 for
running, Part 8 for tmux, Part 13 for results — but this is what you actually type.

**1. Connect.** Open PowerShell on your laptop:

```bash
ssh taw021@pwrlab.ucsd.edu
```

Enter the password. Nothing appears as you type; that is normal.

**2. Start tmux.** Not optional — without it, closing your laptop kills the run:

```bash
tmux new -s run1
```

**3. Turn on the environment:**

```bash
source ~/AdvAppliedEnergy_Pathways_2025/env.sh
```

Your prompt gains `(.venv)` and you land in `pycode/`.

**4. Choose your scenario** — skip this to run whatever is already set:

```bash
nano -l pycode/testMultiYear.py
```

Lines 34–45. Change only the values to the right of the `=`, and do not touch the spaces at
the start of a line. Save with `Ctrl+O`, `Enter`, then `Ctrl+X`.

**5. Run it:**

```bash
python testMultiYear.py
```

**6. Walk away.** Press `Ctrl+B`, then `D`. The run continues on the node. You can close
PowerShell, shut the laptop, and go home.

**7. Come back whenever:**

```bash
ssh taw021@pwrlab.ucsd.edu
tmux attach -t run1
```

**8. Read the headline results:**

```bash
column -s, -t ~/AdvAppliedEnergy_Pathways_2025/data_res/test_*/stat_national.csv | less -S
```

Arrow keys scroll, `q` quits.

**9. Copy them to your laptop** — run this in PowerShell, *not* while logged into the node:

```bash
scp taw021@pwrlab.ucsd.edu:/home/taw021/AdvAppliedEnergy_Pathways_2025/data_res/test_*/stat_national.csv .
```

> **You can also just ask.** In a Claude Code session (Part 3) you can say what you want
> in plain English — *"set the scenario to 1.5 °C with 7 days, show me the diff, then start
> it in a tmux session called run1"* — and let it do steps 4 and 5 for you. Part 11.5 covers
> this, including the one instruction you must not leave out: **tell it to use tmux**, or
> the run dies when your session ends.

## Three things that will catch you out

> **Re-running the same settings on the same day fails** with
> `FileExistsError: ... /provin_demand_hourly`. The output folder from the previous attempt
> is still there and the scripts will not overwrite it. Delete it first, or change
> `custom_tag` to give the new run its own folder. See Part 16.5.

> **A 7-day run is a smoke test, not a result.** It takes about 30 minutes and cannot see
> seasonal storage or rare stress events, so it systematically under-builds for
> reliability (Part 4.7). A real answer needs `optimization_days = 365`, which takes up to
> ~20 hours.

> **The disk is nearly full** — under 11 GB free, shared with thirteen other people. Every
> run writes several GB to `data_res`. Copy results to your laptop, then delete the folder
> from the node. Check with `df -h /`.

## This install is validated

Running the script **as committed** reproduces the README's published demo figures:

| Decade | Onshore wind | Utility solar | New transmission |
|---|---|---|---|
| 2030 | 610 → **608.9** | 234 → **234.1** | 27 → **27.6** |
| 2040 | 1257 → **1260.9** | 250 → **249.8** | 93 → **92.3** |

Six of six within rounding, covering both structural cases: 2030 solving from real 2020
initial conditions, and 2040 solving from 2030's chained output.

2050 and 2060 solved but their summaries were not captured — the run exhausted the disk
first, which is the hazard Part 14 is about. The comparison above is the check to repeat
after any change to the environment.

> **Run the file as committed when you want to reproduce those numbers.** The published
> demo corresponds to the settings already in `testMultiYear.py` — heat-pump heating, +5%
> demand, `endogenize_firm_capacity = 0`. The different baseline quoted in the model's
> README §5.3 belongs to the *full-year* reproduction runs and produces different
> capacities; substituting it is an easy and confusing mistake to make.

---

# Part 1 — What you are working with

## 1.1 The mental model

You have a laptop. Somewhere in a building at UCSD there is a second computer called
**`pwrlab`**. It has no screen, no keyboard and no mouse attached to it. The only way to
use it is to type text commands at it over the network from your laptop.

That is the whole idea. Your laptop becomes a *window* into the other machine. When you
type `ls` and press Enter, your laptop sends those two letters to `pwrlab`, `pwrlab` runs
the command, and sends the text back for your laptop to display. Nothing is running on
your laptop except the window.

Three things follow from this, and most later confusion traces back to one of them:

1. **Files on your laptop are not on the node, and vice versa.** They are separate
   computers with separate hard drives. Downloading a file "to your computer" while
   connected to the node downloads it *to the node*. Part 10 covers how to move files
   across.
2. **If your laptop loses its network connection, whatever you were running is killed** —
   unless you took the precaution in Part 8. Closing your laptop lid counts. Coffee-shop
   wifi dropping counts. This is the #1 way people lose a 12-hour model run.
3. **Other people are using this machine at the same time as you.** It is a shared lab
   resource. You can see them, they can see you, and you can accidentally bring the
   machine to its knees for everyone. Part 14 covers the etiquette.

## 1.2 Why bother with a remote machine at all?

Because it is enormously more powerful than your laptop:

| | `pwrlab` | A good laptop |
|---|---|---|
| Processor | Intel Xeon Gold 6240 @ 2.60 GHz | Apple M-series / Intel i7 |
| CPU cores | **72** | 8–12 |
| Memory (RAM) | **187 GB** | 16–32 GB |
| Runs 24/7 | Yes | No — it sleeps when you close it |

The energy model you are going to run is a very large linear optimisation problem. A
full-year, four-period scenario can use tens of gigabytes of RAM and run for many hours.
Your laptop cannot do this. `pwrlab` can, and it can keep doing it overnight while you
sleep.

## 1.3 The vital statistics

Keep these somewhere you can find them:

| Thing | Value |
|---|---|
| Machine name (hostname) | `pwrlab` |
| Address you connect to | `pwrlab.ucsd.edu` |
| Its IP address | `169.228.63.79` — only needed if the name ever fails to resolve |
| Operating system | Ubuntu 24.04.4 LTS (a flavour of Linux) |
| Your username | `taw021` |
| Your password | *given to you separately — never put it in a file or an email* |
| Your home folder | `/home/taw021` |
| The model lives in | `/home/taw021/AdvAppliedEnergy_Pathways_2025` |

> **A word on the disk.** The node's main drive is 98 GB and is currently **81% full,
> with about 19 GB free**. That is not much. The model's input data alone is ~7 GB and
> results accumulate with every run. Check free space (Part 17) before large downloads or
> long runs, and delete old results you no longer need. A full disk causes errors for
> every user on the machine, not just you.

---

# Part 2 — Connecting to the node

Connecting is done with a tool called **SSH** (Secure Shell). It is built in to both
macOS and Windows now; you do not need to install anything.

## 2.1 If you are on a Mac

1. Press `Cmd` + `Space` to open Spotlight.
2. Type `Terminal` and press Enter. A window with a text prompt opens.
3. Type this and press Enter:

```bash
ssh taw021@pwrlab.ucsd.edu
```

## 2.2 If you are on Windows

1. Press the `Windows` key, type `PowerShell`, press Enter.
2. Type the same command and press Enter:

```bash
ssh taw021@pwrlab.ucsd.edu
```

(Windows Terminal or PowerShell both work. You do **not** need PuTTY any more, though it
works fine if you prefer a graphical setup.)

## 2.3 What happens on the very first connection

The first time only, you will see:

```
The authenticity of host 'pwrlab.ucsd.edu' can't be established.
ED25519 key fingerprint is SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxx.
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

This is normal. Your computer is saying "I have never met this machine before, is it
really the one you meant?" Type the full word `yes` and press Enter. You will not be
asked again.

## 2.4 The password

Next you will see:

```
taw021@pwrlab.ucsd.edu's password:
```

Type your password and press Enter.

> **Nothing will appear as you type** — no dots, no asterisks, no moving cursor. This is
> deliberate: it hides the length of your password from anyone looking over your shoulder.
> Your keystrokes are registering. Type the password and press Enter as normal.

If you mistype it, you are asked again.

## 2.5 You're in

You will see a wall of Ubuntu welcome text and then a line ending in a `$`:

```
taw021@pwrlab:~$
```

That `$` is the **prompt**. It means "I am ready, type something." You are now typing on
a computer in a machine room, not on your laptop.

## 2.6 Leaving

Type `exit` and press Enter, or press `Ctrl` + `D`. Read Part 8 first though — logging
out kills anything you were running, unless you used tmux.

## 2.7 Optional: set up a key so you stop typing your password

A **key pair** lets your laptop prove who it is automatically, so you are never asked for
the password again. Nothing in this guide requires it — password login works everywhere,
including the Claude Code desktop app — but it is a pleasant quality-of-life improvement
if you connect often.

Run this **on your laptop**, not on the node:

```bash
ssh-keygen -t ed25519
```

Press Enter three times to accept all the defaults. Then install the public half on the
node.

**On Mac or Linux**, there is a command that does it for you:

```bash
ssh-copy-id taw021@pwrlab.ucsd.edu
```

**On Windows there is no `ssh-copy-id`.** Use this instead — it achieves the same thing:

```bash
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh taw021@pwrlab.ucsd.edu "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

Enter your password one final time. From now on `ssh taw021@pwrlab.ucsd.edu` logs you
straight in.

> Once a key is in place, you can point the Claude Code desktop app's **Identity File**
> field (Part 3.2) at it and stop being asked for the password there too.

You can go further and give the machine a nickname. On your laptop, create or edit the
file `~/.ssh/config` and add:

```
Host pwrlab
    HostName pwrlab.ucsd.edu
    User taw021
    ServerAliveInterval 60
```

Now you can connect by just typing `ssh pwrlab`. The `ServerAliveInterval` line is worth
having — it sends a tiny keep-alive signal every 60 seconds so that your connection is
less likely to be dropped for idleness.

---

# Part 3 — Using Claude Code over SSH (Windows)

This is how the account was set up in the first place, and it is the quickest way to get
working on the node. The Claude Code **desktop app** runs on your Windows laptop, connects
to `pwrlab` over SSH, and gives you a chat window, a file editor and a visual diff view —
all operating on files that live on the node.

You describe what you want in plain English; Claude runs the commands on the node.

> **Requirement:** Claude Code needs a **Pro, Max, Team or Enterprise** Claude
> subscription. The free plan does not include it.

## 3.1 Install the desktop app

1. Download the Windows installer:
   **https://claude.ai/api/desktop/win32/x64/setup/latest/redirect**
   (If your laptop has an ARM processor — a Snapdragon-based Surface, for example — use
   the ARM64 installer linked from https://code.claude.com/docs/en/desktop-quickstart.)
2. Run it. You do not need administrator rights.
3. Launch **Claude** from the Start menu and sign in.
4. Click the **Code** tab at the top.

You do **not** need to install Node.js, Python, or the `claude` command separately — the
desktop app contains everything.

## 3.2 Add the node

1. In the **Code** tab, click the **environment dropdown** (it reads **Local** by
   default).
2. Choose **+ Add SSH connection**.
3. Fill in:

   | Field | Value |
   |---|---|
   | **Name** | `pwrlab` — any label you like |
   | **SSH Host** | `taw021@pwrlab.ucsd.edu` |
   | **SSH Port** | `22`, or leave blank |
   | **Identity File** | leave blank |

4. Save, then select **pwrlab** from the dropdown. You will be asked for the account
   password.

That is the whole setup. `pwrlab` now stays in the dropdown for every future session.

> **Leave Identity File blank.** It is for people who log in with an SSH key instead of a
> password. This account uses a password, so there is nothing to put there. If you later
> set up a key (Part 2.7), come back and point this field at it — after that you stop
> being asked for the password.

## 3.3 Start a session

1. Select **pwrlab** from the environment dropdown.
2. When asked for a project folder, enter:
   ```
   /home/taw021/AdvAppliedEnergy_Pathways_2025
   ```
   Note the forward slashes — this is a path on the node, not on your laptop.
3. The first connection takes a minute or two while the app installs Claude Code onto the
   node. On this account that is already done, so it should be quick.
4. Type what you want and press Enter.

From here on, every file Claude reads or writes and every command it runs happens **on
`pwrlab`**, not on your laptop.

That includes running the model itself — editing the scenario, launching the solve,
checking on it, and reading results back. **Part 11.5** covers how to ask for that, and the
one thing the request must include so a long run survives you disconnecting.

Requests that work well:

- *"Change the scenario in testMultiYear.py to the 1.5 °C target with a full 365 days, and
  show me the diff before saving."*
- *"How much free disk space is there, and which result folders are biggest?"*
- *"Read stat_national.csv from the most recent run and tell me the onshore wind capacity
  for each decade."*
- *"The run failed — look at the error and explain what went wrong."*

The **permission mode** selector next to the send button controls how much Claude does
without asking. **Manual** shows you every proposed change and waits for approval — a
sensible default on a shared machine, and easy to relax later.

## 3.4 The one limitation that matters here

> **SSH sessions have no integrated terminal.** The `Ctrl` + `` ` `` terminal pane works
> in local sessions only. There is also no `@mention` file picker.

That matters for this project, because **long model runs must be started inside tmux** — a
tool that keeps work running on the node after you disconnect (Part 8) — and starting it
needs a real terminal.

So use both tools side by side:

| Task | Use |
|---|---|
| Editing scenario settings, reading results, understanding errors, exploring the code | **Claude Code desktop app** |
| Starting a multi-hour run in tmux, watching it with `htop`, reattaching later | **A PowerShell window** running `ssh taw021@pwrlab.ucsd.edu` |

Having both open at once is fine — they are just two connections to the same machine.

## 3.5 If it will not connect

The best diagnostic is to try plain SSH from PowerShell:

```bash
ssh taw021@pwrlab.ucsd.edu
```

If that works, the desktop app should too.

| What you see | Fix |
|---|---|
| `Permission denied` | Wrong password, or wrong username in **SSH Host** — it must be the full `taw021@pwrlab.ucsd.edu` |
| `Connection refused` / `timed out` | Cannot reach the machine — you may need the campus VPN from off-campus |
| `Host key verification failed` | Connect once with plain `ssh` from PowerShell, accept the fingerprint, then retry |
| Cannot find the folder | Path typo — it is `/home/taw021/AdvAppliedEnergy_Pathways_2025`, forward slashes, capitals as shown |
| Clicking **Code** offers an upgrade | Your plan does not include Claude Code |

## 3.6 Using `claude` in a terminal instead

Claude Code is also installed on the node itself (`/usr/bin/claude`). From any PowerShell
SSH session:

```bash
cd ~/AdvAppliedEnergy_Pathways_2025
claude
```

The first time, it prints a URL — open it in your laptop's browser, approve, and paste the
code back. This works fine on a machine with no screen of its own.

| Type | Effect |
|---|---|
| `/help` | List everything available |
| `/clear` | Start a fresh conversation |
| `/model` | Switch model |
| `Esc` | Interrupt Claude mid-response |
| `Ctrl` + `C` twice | Quit |

For a one-off question without starting a session:
```bash
claude -p "summarise the errors in the last 50 lines of my model run"
```

> Claude runs commands as **you** on a **shared machine**. Read what it proposes before
> approving, particularly anything involving `rm`.

## 3.7 Desktop keyboard shortcuts (Windows)

| Keys | Action |
|---|---|
| `Ctrl` + `/` | Show all shortcuts |
| `Ctrl` + `N` | New session |
| `Ctrl` + `Tab` | Next session |
| `Esc` | Stop Claude's current response |
| `Ctrl` + `Shift` + `D` | Toggle the diff pane |
| `Ctrl` + `Shift` + `M` | Permission mode menu |
| `Ctrl` + `;` | Side chat — ask something without derailing the main thread |

---

# Part 4 — How the model works

You can run this model by copying commands. You will get much further if you know what it
is doing, because then the settings mean something, the outputs mean something, and an odd
result looks odd instead of looking like an answer.

## 4.1 The question it answers

> *If China's power sector must hit a given carbon budget by 2060, what is the cheapest
> combination of generation, storage and transmission that keeps the lights on in every
> province in every hour along the way?*

Every word there matters. **Cheapest** — this is a cost-minimisation. **Every province** —
it is spatially resolved, not one national blob. **Every hour** — it checks supply against
demand hour by hour, which is what makes wind and solar hard. **Along the way** — it solves
2030, 2040, 2050 and 2060 in sequence, carrying capacity forward.

## 4.2 What "optimisation" means here

The model is a **linear program**, or LP. An LP has exactly three parts:

1. **Decision variables** — the numbers you are solving for. Here: how much wind to build
   in each place, how much each plant generates in each hour, how much power flows down
   each transmission line.
2. **An objective** — one number to make as small (or large) as possible. Here: total
   system cost.
3. **Constraints** — rules every solution must obey. Here: demand must be met, emissions
   must stay under the cap, you cannot build more wind than the land allows.

"Linear" means every relationship is proportional: twice the wind farm costs twice as much
and generates twice as much. That is a real simplification, and it is what makes a problem
of this size solvable at all.

An LP does not search or guess. Provably, the optimum of a linear program sits at a corner
of the region carved out by the constraints, and the solver navigates to it directly. When
Gurobi reports `Optimal objective`, that is not "the best I found" — it is "no cheaper
solution exists under these constraints." Any result you dislike is therefore an argument
about the constraints or the costs, never about the solver.

## 4.3 The decision variables in this model

Open `pycode/main.py` and search for `addVar` — every one is a quantity the model chooses.
They fall into two groups.

**Investment — what gets built** (one number per place, per technology):

| Variable | What it decides |
|---|---|
| `x_wind[pro][c]`, `x_solar[pro][c]` | What **fraction** of resource cell `c` in province `pro` to develop. Bounded 0 to 1 — you cannot build 150% of a site. |
| `cap_gw[pro][tech]` | Capacity of each firm technology: coal, coal+CCS, CHP+CCS, gas, gas+CCS, nuclear, hydro, BECCS |
| `cap_phs`, `cap_bat`, `cap_lds` | Pumped hydro, batteries, long-duration storage |
| `cap_trans_new[pro]` | New inter-provincial transmission capacity |

**Operation — what happens each hour** (one number per hour, and there are 168 or 8760 of
them):

| Variable | What it decides |
|---|---|
| `load_conv[layer][pro]` | Output of each conventional plant type |
| `inte_wind`, `inte_solar` | Wind and solar actually delivered (the rest is curtailed) |
| `charge_*`, `dischar_*` | Storage charging and discharging |
| `load_trans[(pro1, pro2)]` | Flow on each inter-provincial link |
| `ru`, `rd` | Ramping up and down — how fast plants change output |
| `resv_*` | Reserve capacity held back for contingencies |
| `load_shedding` | Unserved demand — deliberate blackout, priced punitively |

That last one is worth noticing. The model *can* fail to meet demand, at a very high
penalty cost. If your results show load shedding, the system you specified was not
buildable, and the model is telling you so rather than crashing.

## 4.4 The objective: one number, twenty-eight terms

At `main.py:783` the objective is assembled. It is a single sum of about 28 cost
components — annualised capital costs plus running costs:

```python
interProvinModel.setObjective(gp.quicksum(wind_gen_cost) +
                              gp.quicksum(solar_gen_cost) +
                              ...
                              gp.quicksum(spur_cost_wind) +      # line to the wind farm
                              gp.quicksum(trunk_cost) +          # line to the grid
                              gp.quicksum(trans_cost) +          # inter-provincial
                              ...
                              gp.quicksum(coal_cost_var))
```

Two things this tells you:

- **Transmission is costed explicitly and in three pieces** — the spur line from each
  resource cell, the trunk line to the network, and inter-provincial links. This is why
  the model does not simply carpet the windiest province in turbines: getting the power
  out has to pay for itself.
- **Capital costs are annualised.** A wind farm's up-front cost is spread over its life
  using a capital recovery factor (`getCRF` in `callUtility.py`), so that a one-off
  construction cost can be compared against a year of fuel bills in the same units.

## 4.5 The constraint that does the most work

Everything turns on one equation, at `main.py:1004`. For every province and every hour,
what arrives must exactly equal what is demanded:

```
  coal + coal_CCS + CHP_CCS + gas + nuclear + hydro
+ BECCS
+ imports from other provinces × (1 − transmission losses)
+ wind delivered + solar delivered
+ storage discharged × round-trip efficiency
+ load shedding
==
demand in that province in that hour
```

It is an equality, not "greater than or equal". Electricity cannot be stockpiled in the
wires: generation and consumption balance continuously. That single line is the reason
storage and transmission get built at all — they are how the model moves energy across
*time* and across *space* to satisfy an equation that must hold in all 8,760 hours at once.

Other constraints that shape the answer:

- **The emission cap** (`main.py:1277`) reads `data_csv/capacity_assumptions/power_sector_emission_2C.csv`
  or `_15C.csv`. This is the climate target, and it is the constraint your `emission_target`
  setting switches between.
- **Storage must end where it started**: `tot_energy_phs[pro][0] == tot_energy_phs[pro][hour_end]`.
  Without this the model would cheat by starting the week with a full battery it never paid
  for.
- **Policy floors and ceilings** on nuclear, hydro, coal and pumped hydro, from the
  `data_csv/capacity_assumptions/` files — what policy has already committed to, and what
  is physically or politically off the table.
- **Reserves**: spare capacity held each hour against forecast error and outages, which is
  why the model builds more than peak demand.

## 4.6 Why the problem is enormous

Multiply it out. Roughly 30 provinces × 8,760 hours × a few dozen operational variables per
province-hour, plus one variable for every wind and solar resource cell in the country —
and `data_pkl/wind_cell_2015.pkl` alone is 1.1 GB of cells.

That is **millions of variables and millions of constraints**, all coupled: hour 4,000's
battery level depends on hour 3,999's, which depends on what you built in 2030. This is why
the run needs ~10 GB of RAM and why it is on a 187 GB server rather than a laptop.

## 4.7 Why 7 days instead of 365

`optimization_days` controls how many days of the year are actually simulated.
`data_csv/simulation_meta/hour_seed.csv` picks which hours those are — a representative
sample spread across the year rather than one arbitrary week.

The trade-off is honest and worth understanding:

| | 7 days (168 hours) | 365 days (8,760 hours) |
|---|---|---|
| Runtime | ~30 minutes | up to ~20 hours |
| Captures daily cycles | yes | yes |
| Captures seasonal storage | **no** | yes |
| Captures rare stress events | **no** | yes |

A week cannot see a still, cold fortnight in January. Since those events are exactly what
determines how much firm capacity and long-duration storage you need, **7-day results
systematically under-build for reliability**. Use them to check that a run works, not to
draw conclusions.

## 4.8 Why the decades chain

`testMultiYear.py` solves 2030 first, then feeds its answer into 2040 as a starting
condition, and so on. `multiYearAutomation.py` does the plumbing.

This matters because **capacity is sticky**. A wind farm built in 2030 is still standing in
2040; the model cannot un-build it. Each decade's constraints therefore include "at least
as much renewable capacity as last decade left behind" — which is why the answer to "what
should 2060 look like?" depends on what you did in 2030. That path dependence is the point
of the paper.

You can see it in the log at the start of each period:

```
Initial conditions for 2030 -- solar installed GW: 278.19
Initial conditions for 2030 -- wind installed GW: 282.86
```

Those are 2020's real, already-built capacities, and they are where 2030 starts from.

## 4.9 What the solver is doing

At `main.py:347`:

```python
interProvinModel.setParam('Method', 2)      # barrier
interProvinModel.setParam('Crossover', 0)   # skip crossover
```

**Method 2 is the barrier (interior-point) algorithm.** The classic LP algorithm, simplex,
walks along the edges of the feasible region from corner to corner. Barrier instead drives
straight through the middle, approaching the optimum from the inside. On problems with
millions of variables barrier is dramatically faster, and it parallelises across cores
where simplex largely does not.

**Crossover = 0 turns off the clean-up step** that would convert barrier's interior answer
into an exact corner solution. That step is slow and this model does not need the exact
corner — a solution very slightly inside the boundary is fine for capacity planning.

So a healthy run looks like this:

```
Barrier solved model in 70 iterations and 50.72 seconds (61.06 work units)
Optimal objective 1.86776063e+05
```

Iterations in the tens, not thousands. If you ever see iteration counts climbing into the
hundreds with little progress, the problem is badly conditioned — usually a cost or bound
set to an extreme value.

## 4.10 Reading the objective value

`Optimal objective 1.86776063e+05` is the **total annualised system cost** for that decade,
in the model's cost units (hundred million yuan). On its own the number means little. It is
useful **comparatively**: run two scenarios and the difference in objective is the cost of
the policy you changed. That is the single most useful thing the model produces, and it is
why scenarios are always run in pairs.

Two cautions:

- Objectives from different `optimization_days` are **not comparable** — 7 days and 365
  days cost out different amounts of energy.
- A *lower* cost is not automatically a *better* outcome. A cheap run that sheds load, or
  that was given a lax emission cap, is cheap for a reason. Always read `stat_national.csv`
  alongside the objective.

---

# Part 5 — How the machine works

Four ideas explain almost everything you will run into on this node: the filesystem, the
process, memory, and the environment. Each one turns a rule you would otherwise memorise
into something you can reason about.

## 5.1 The filesystem is one tree

Windows has several drives — `C:`, `D:`, a USB stick. Linux has exactly one tree, starting
at `/`, and everything hangs off it. There is no drive letter anywhere.

```
/                     the root of everything
├── home/             all user accounts
│   ├── taw021/       ← you. Written "~" for short.
│   └── someone_else/ ← a colleague. You cannot read this.
├── opt/gurobi1101/   the Gurobi solver, installed for everyone
├── usr/bin/          programs everyone can run: python3, git, tmux, nano
└── tmp/              scratch space, wiped on reboot
```

Two rules follow, and they explain most "Permission denied" messages:

- **You can write inside `/home/taw021` and almost nowhere else.** Not `/usr`, not `/opt`,
  not another person's home. That is not a restriction aimed at you — it is what stops
  fourteen users breaking each other's work.
- **Installing software normally means writing to `/usr`,** which you cannot do. That is
  precisely why this project's Python lives in a folder inside your home directory instead
  (§5.5).

Every file carries an owner and a permission string. In `ls -l`:

```
-rw-rw-r-- 1 taw021 taw021 497 Sep 13 07:04 gurobi.lic
 │└┬┘└┬┘└┬┘  └──┬─┘
 │ │  │  │      └── owner
 │ │  │  └───────── everyone else: read only
 │ │  └──────────── owner's group: read + write
 │ └─────────────── owner: read + write
 └───────────────── "-" = file, "d" = directory
```

## 5.2 A process is a running program

When you type `python testMultiYear.py`, Linux creates a **process**: a copy of the program
with its own memory, its own open files, and a number called a PID. `htop` lists them.

Processes have parents. Your shell is a process; the Python you launch from it is its
child. **This is the whole reason tmux exists**, so it is worth following the chain:

```
sshd (the SSH server)
└── bash (your shell)
    └── python testMultiYear.py (your run)
```

When your connection drops, `sshd` goes away. Linux sends every process in that session a
hang-up signal — `SIGHUP` — and the default response to `SIGHUP` is to die. Your shell
dies, and it takes its children with it. Your twelve-hour run is gone, mid-solve, with
nothing written.

tmux breaks the chain. The tmux **server** is not a child of your SSH session:

```
sshd ──── tmux client ╌╌╌ (detachable link)
                          tmux server ← owned by the system, not your connection
                          └── bash
                              └── python testMultiYear.py
```

Detaching disconnects the client. The server never receives `SIGHUP`, so your run never
notices you left. This is why "always use tmux" is not superstition — it is the one thing
that decouples your work from your network connection.

You can watch this yourself:

```bash
ps -ef --forest | grep -A3 sshd     # see the parent/child chain
ps -eo pid,etime,rss,cmd | grep python
```

## 5.3 Memory is not disk

Two different numbers, constantly confused, and the confusion causes real failures.

| | RAM (memory) | Disk (storage) |
|---|---|---|
| Size here | 187 GB | 98 GB, ~8 GB free |
| Holds | what is running *right now* | files, permanently |
| Emptied when | the process ends | never, until you delete |
| Check with | `free -h` | `df -h /` |

The solver builds the entire LP — millions of variables and constraints — **in RAM**. That
is the ~10 GB you see next to the python process in `htop`. None of it is on disk; if the
process dies, it is simply gone.

When RAM runs out, Linux starts **swapping**: moving memory onto disk to free space. Disk
is thousands of times slower than RAM, so a job that starts swapping does not fail, it
crawls — sometimes by a factor of a hundred. The symptom is distinctive and worth knowing:
in `htop`, CPU drops toward zero while the job is clearly still running. That is a swapping
job, and it is usually faster to kill it and run something smaller.

## 5.4 Cores, and what "shared" really means

This node has **72 cores**. One core runs one thread at a time, so 72 things can genuinely
happen at once. In `htop`, `100%` means one core fully busy — `1600%` means sixteen.

`uptime` gives a **load average**: how many processes wanted CPU over the last 1, 5 and 15
minutes.

```
load average: 0.00, 0.00, 0.00     ← idle, help yourself
load average: 12.4, 11.8, 9.2      ← busy but fine on 72 cores
load average: 68.1, 70.3, 71.5     ← saturated; wait
```

Gurobi's barrier algorithm parallelises well and will take every core it is offered. On a
machine with no scheduler — and this one has none, no Slurm, no queue — nothing stops you
taking all 72 and leaving thirteen colleagues waiting. Part 14 covers how to be a good
neighbour; the point here is that the machine will not stop you, so the judgement is yours.

## 5.5 Why this project has its own private Python

The node's own Python is 3.12. This model needs 3.9 — its pinned `pandas 1.5.3` will not
even build on 3.12. You cannot install Python 3.9 system-wide because you cannot write to
`/usr`.

A **virtual environment** solves this. `.venv/` is an ordinary folder in the project
containing its own Python interpreter and its own packages:

```
.venv/
├── bin/python      ← Python 3.9.25, just for this project
└── lib/python3.9/site-packages/     ← pandas 1.5.3, gurobipy, geopandas...
```

"Activating" it does something almost trivial: it puts `.venv/bin` at the front of your
`PATH`, the list of folders the shell searches for commands. After that, typing `python`
finds `.venv/bin/python` before `/usr/bin/python3`. That is all. Nothing is installed,
nothing global changes, and other users are unaffected.

You can see it directly:

```bash
which python                     # /usr/bin/python3  — before
source ~/AdvAppliedEnergy_Pathways_2025/env.sh
which python                     # .../.venv/bin/python  — after
```

This is also why forgetting to activate gives `ModuleNotFoundError: No module named
'pandas'`. Nothing is broken — you are simply talking to the *other* Python, which has
never heard of this project.

## 5.6 The environment: settings a process inherits

Every process is handed a set of **environment variables** by its parent. `env.sh` sets
three of them, and each fixes a specific failure:

| Variable | What it does | What breaks without it |
|---|---|---|
| `PATH` | Where the shell looks for commands | `python` means 3.12, not 3.9 |
| `PYTHONPATH` | Extra folders Python searches for imports | `ModuleNotFoundError: No module named 'pycode'` — because `plotResult.py` says `from pycode.callUtility import ...` |
| `MPLBACKEND=Agg` | Tells matplotlib to draw to files, not a window | Plotting crashes: there is no screen on a server |
| `GRB_LICENSE_FILE` | Where Gurobi finds its licence | Only needed if the licence is not in `~` |

Inspect them any time:

```bash
echo $PATH
echo $PYTHONPATH
env | sort | less        # everything (q to quit)
```

And the reason you must type `source env.sh` rather than `bash env.sh`: a variable set by a
child process dies with that child. `bash env.sh` would start a new shell, set the
variables there, and exit — taking them with it. `source` runs the commands **in your
current shell**, so the changes stick. That distinction catches everyone once.

---

# Part 6 — Working in the terminal

This part covers the terminal itself. Most of it maps onto things you already do in File
Explorer — opening folders, copying files, checking how much space is left. The difference
is that you type the instruction instead of clicking it.

## 6.1 Reading the prompt

```
taw021@pwrlab:~/AdvAppliedEnergy_Pathways_2025$
│      │       │                              │
│      │       │                              └─ ready for input
│      │       └─ which folder you are currently "in"
│      └─ which machine you are on
└─ who you are
```

The "which folder you are in" part is the one that matters. In a graphical file manager,
the folder you are looking at is obvious because you can see it. In a terminal, you only
have this line to tell you — and commands act on wherever you currently are, so it is
worth a glance before you run something.

The `~` symbol is shorthand for your home folder, `/home/taw021`. So `~/Advanced...`
means `/home/taw021/Advanced...`.

## 6.2 Paths — how to name a location

A path is an address for a file or folder. Folders are separated by forward slashes `/`.

- **Absolute path** — starts at the root of the whole drive with `/`, and is therefore
  unambiguous from anywhere: `/home/taw021/AdvAppliedEnergy_Pathways_2025/pycode/main.py`
- **Relative path** — starts from wherever you currently are: `pycode/main.py`
- `.` means "the folder I'm in right now"
- `..` means "the folder one level up"
- `~` means "my home folder"

When in doubt, use absolute paths. They always work.

## 6.3 The commands you will genuinely use

**Where am I?**
```bash
pwd
```
Prints the working directory. When you are lost, this is the answer.

**What's here?**
```bash
ls
```
Lists files and folders. More useful variants:
```bash
ls -l
```
Long format — shows size, date modified, permissions, one per line.
```bash
ls -lh
```
Same but with human-readable sizes (`4.2G` instead of `4509715660`).
```bash
ls -la
```
Also shows hidden files. On Linux any file whose name starts with a dot is hidden;
configuration files are hidden by convention. `.venv` and `.bashrc` are examples.

**Go somewhere**
```bash
cd AdvAppliedEnergy_Pathways_2025
```
Change directory. Some shortcuts:
```bash
cd ..          # go up one level
cd ~           # go to my home folder
cd             # also goes home (bare cd)
cd -           # go back to where I just was
```

**Look at a file without opening an editor**
```bash
cat notes.txt        # dump the whole file to the screen
head -20 notes.txt   # just the first 20 lines
tail -20 notes.txt   # just the last 20 lines
less notes.txt       # scroll through it: arrows to move, q to quit, /word to search
```
`less` is the right choice for anything long. Remember: **`q` quits**.

**Make a folder**
```bash
mkdir my_new_folder
```

**Copy, move, rename**
```bash
cp source.csv backup.csv          # copy a file
cp -r folder1 folder2             # copy a whole folder (-r = recursive)
mv oldname.csv newname.csv        # rename
mv results.csv ~/archive/         # move into another folder
```
Note there is no separate "rename" command — renaming is just moving something to a new
name in the same place.

**Delete**
```bash
rm unwanted.csv        # delete a file
rm -r unwanted_folder  # delete a folder and everything in it
```

> **`rm` is permanent.** There is no Recycle Bin, no undo, no undelete, and no "are you
> sure?" prompt. Before you press Enter on any `rm` command, read the whole line again.
>
> Never, under any circumstances, type `rm -rf /` or `rm -rf ~`. The first tries to erase
> the entire machine; the second erases everything you own.
>
> A safer habit: run `ls` with the same target first. If `ls ~/data_res/old_run_*` shows
> exactly the things you meant, then `rm -r ~/data_res/old_run_*` is safe.

**How much space is left?**
```bash
df -h /              # free space on the whole drive
du -sh ~/*           # how big is each thing in my home folder
ncdu ~               # interactive space explorer — arrows to navigate, q to quit
```
`ncdu` is excellent for hunting down what is eating your disk.

## 6.4 The four keyboard tricks that change everything

These four do most of the work of making the terminal quick to use.

**1. `Tab` completes what you are typing.**
Type `cd AdvA` and press `Tab` — it fills in the rest of `AdvAppliedEnergy_Pathways_2025/`.
If several things match, press `Tab` twice to see the options. This saves enormous amounts
of typing and, more importantly, **prevents typos in filenames**. Use it constantly.

**2. `↑` and `↓` scroll through your past commands.**
Press up-arrow to bring back the last thing you typed, edit it, press Enter. You almost
never need to retype a long command.

**3. `Ctrl` + `R` searches your history.**
Press `Ctrl+R`, start typing any fragment of a command you ran days ago, and it appears.
Press Enter to run it, or arrow keys to edit it first.

**4. `Ctrl` + `C` stops whatever is running.**
Your emergency brake. If something is spewing text, hanging, or you started it by
mistake, `Ctrl+C` stops it and hands the prompt back.

## 6.5 A few more keys worth knowing

| Keys | What it does |
|---|---|
| `Ctrl` + `C` | Stop the running command |
| `Ctrl` + `D` | Log out / end input |
| `Ctrl` + `L` | Clear the screen (same as typing `clear`) |
| `Ctrl` + `A` | Jump to the start of the line you are typing |
| `Ctrl` + `E` | Jump to the end of the line |
| `Ctrl` + `U` | Delete everything before the cursor |
| `Ctrl` + `K` | Delete everything after the cursor |
| `Ctrl` + `W` | Delete the previous word |
| `Alt`/`Option` + `←` `→` | Move one word at a time |

## 6.6 Getting help on any command

```bash
man ls        # the full manual for ls (press q to quit)
ls --help     # a shorter summary
```

## 6.7 Case and spaces matter

`Data_res` and `data_res` are two different folders on Linux. And a space separates
arguments, so a filename with a space in it must be quoted:

```bash
ls "my results.csv"
```
This is why you should avoid spaces in filenames you create. Use underscores.

---

# Part 7 — Where everything lives on this account

Log in and run `ls ~/AdvAppliedEnergy_Pathways_2025`. Here is what each thing is.

```
/home/taw021/                              ← your home folder ("~")
└── AdvAppliedEnergy_Pathways_2025/        ← the model. Everything happens here.
    │
    ├── env.sh                  ← ⭐ run this before every session (see Part 11)
    ├── README.md               ← the original authors' documentation
    ├── SETUP_ADMIN_REQUEST.md  ← notes on what the admin still needs to do
    ├── requirements-core.txt   ← list of Python packages (solver side)
    ├── requirements-geo.txt    ← list of Python packages (maps and plots)
    │
    ├── .venv/                  ← the private Python installation. Never edit by hand.
    │
    ├── pycode/                 ← ⭐ all the model code, and where you run things from
    │   ├── testMultiYear.py    ← ⭐ the script you will usually run
    │   ├── testSingleYear.py   ←   same, but one period only
    │   ├── main.py             ←   the actual optimisation model
    │   ├── initData.py         ←   prepares input data
    │   ├── clearupData.py      ←   post-processes raw results
    │   ├── multiYearAutomation.py ← chains one decade's output into the next decade's input
    │   ├── callUtility.py      ←   shared helper functions
    │   ├── obtainPrice.py      ←   derives electricity prices from results
    │   └── plotResult.py       ←   draws the maps and charts
    │
    ├── data_csv/               ← small inputs, stored in the repository
    │   ├── capacity_assumptions/   ← how much coal/gas/nuclear/hydro is allowed
    │   ├── cost_assumptions/       ← technology capital and operating costs
    │   ├── demand_assumptions/     ← projected electricity demand by province
    │   ├── geography/              ← provincial and county geography
    │   ├── transmission_assumptions/ ← inter-provincial line capacities
    │   ├── vre_installations/      ← existing wind and solar
    │   ├── vre_potentials/         ← how much wind and solar could be built
    │   ├── simulation_meta/        ← which hours to simulate
    │   └── scen_params_template.json ← default scenario settings
    │
    ├── data_pkl/    ← 3.3 GB of wind/solar resource data, from Zenodo
    ├── data_shp/    ← 42 MB of map shapes, from Zenodo
    ├── data_mat/    ← 868 MB of MATLAB matrices, from Zenodo
    │
    ├── data_res/    ← ⭐ YOUR RESULTS APPEAR HERE, one folder per run
    │
    └── figures_for_papers/ ← the published figures and the notebook that drew them
```

## 7.1 Everything is ready

Nothing is outstanding. For the record, all three of the things that usually block a setup
like this are done:

| | Status |
|---|---|
| **Zenodo input data** | `data_pkl` (3.3 GB), `data_mat` (868 MB), `data_shp` (42 MB) — downloaded and checksum-verified against Zenodo's published MD5 |
| **Python environment** | Python 3.9.25 with every pinned package, in `.venv` |
| **Gurobi licence** | Academic licence installed at `~/gurobi.lic`, valid until **13 September 2027** |

### About the solver licence

Gurobi is the commercial solver that does the actual optimisation, and this model has no
open-source alternative — `main.py` calls `gurobipy` directly. The licence is installed and
working; you do not need to do anything.

Two details worth knowing, because they will matter eventually:

- **It expires on 13 September 2027.** After that, every run stops with
  `GurobiError: License expired` until it is renewed.
- **It is a named-user licence, locked to this machine and this account.** It works for
  `taw021` on `pwrlab` and nowhere else. If a colleague wants to run the model on this
  node under their own account, they need their own key from
  https://www.gurobi.com/academia/academic-program-and-licenses/ — yours will not work for
  them.

The system also has a full Gurobi 11.0.1 installation at `/opt/gurobi1101/`. You do not
need it; the model uses the copy inside `.venv`. If you ever want its command-line tools,
note that they fail with `libgurobi110.so: cannot open shared object file` unless you set:

```bash
export LD_LIBRARY_PATH=/opt/gurobi1101/linux64/lib
```

### The one thing that is tight

**Disk.** Under 9 GB free, shared with thirteen other people. A full four-decade 7-day run
needs upwards of 10 GB of working space, so it does not currently fit — one such run
exhausted the disk on 13 September 2026 and had to be killed. Part 14 covers this;
`SETUP_ADMIN_REQUEST.md` is a ready-made note asking the administrator for a scratch
volume.

## 7.2 What has been set up for you

You do not need to install anything. Already done:

- **Python 3.9.25** in a self-contained "virtual environment" at `.venv`. The system's own
  Python is version 3.12, which is too new for this model's pinned packages, so a private
  3.9 was installed just for this project. It does not interfere with anything else.
- **All required packages**: `numpy`, `pandas`, `scipy`, `gurobipy`, `geopandas`,
  `shapely`, `matplotlib`, `geoplot`, `mapclassify`, `plotly` and a few others.
- **`env.sh`**, a one-line shortcut that switches everything on correctly.

### What a "virtual environment" is, in one paragraph

Different Python projects need different, often conflicting, versions of the same
packages. A virtual environment is a private folder containing one project's own copy of
Python and its own packages, isolated from everything else on the machine. "Activating"
it just means *for this terminal window, the word `python` should mean the one in that
folder*. That is all `env.sh` does. If you forget to activate it, you get the system
Python 3.12, which does not have any of the model's packages, and you get
`ModuleNotFoundError`.

---

# Part 8 — tmux: the single most important tool here

## 8.1 The problem

Part 5.2 explains the mechanism: your run is a child process of your SSH session, so when
the connection ends Linux sends `SIGHUP` down the chain and the run dies with it. This part
is the practical consequence.

Model runs take hours — the quick demo takes about 30 minutes, and a full-year scenario
can take the better part of a day. If you start a run the normal way and then:

- close your laptop, or
- lose wifi for ten seconds, or
- your laptop goes to sleep, or
- you accidentally close the terminal window,

...then your SSH connection ends, and the node kills your run instantly. Hours of
computation, gone, with no partial results.

## 8.2 The solution

**tmux** creates a session that lives *on the node itself*, independent of your
connection. You attach to it to look at it, and detach to walk away. The work keeps
running. You can reconnect from a different computer entirely, days later, and pick up
exactly where you left off.

**Use tmux for every single model run. No exceptions.**

## 8.3 The complete workflow

**Step 1 — connect to the node as usual.**
```bash
ssh taw021@pwrlab.ucsd.edu
```

**Step 2 — start a named session.** Give it a name describing what you're doing:
```bash
tmux new -s modelrun
```
The screen clears and a green status bar appears at the bottom. You are now *inside* the
tmux session.

**Step 3 — start your work.** Anything you like:
```bash
source ~/AdvAppliedEnergy_Pathways_2025/env.sh
python testMultiYear.py
```

**Step 4 — detach and walk away.** Press:

> `Ctrl` + `B`, then release both keys, then press `D`

This is the tmux convention: `Ctrl+B` is the "attention" signal, and the next key is the
actual command. You will see `[detached]` and be back at the ordinary prompt. **Your run
is still going.** You can now safely type `exit`, close your laptop, and go home.

**Step 5 — come back later.** Reconnect by SSH, then:
```bash
tmux attach -t modelrun
```
You are looking at your run again, exactly as you left it, with all the output it has
produced in the meantime.

**Step 6 — when the work is finished**, type `exit` inside the session to close it down.

## 8.4 tmux commands worth knowing

Run these at the ordinary prompt:

```bash
tmux ls                  # list all my sessions and whether they're attached
tmux new -s NAME         # start a new named session
tmux attach -t NAME      # reconnect to a session
tmux attach              # reconnect to the most recent one
tmux kill-session -t NAME  # forcibly end a session
```

And these are pressed *inside* a session, always starting with `Ctrl+B`:

| Press | Then | Result |
|---|---|---|
| `Ctrl+B` | `D` | **Detach** — leave it running, go back to normal prompt |
| `Ctrl+B` | `C` | Create a new window (like a browser tab) |
| `Ctrl+B` | `N` / `P` | Next / previous window |
| `Ctrl+B` | `0`–`9` | Jump straight to window number N |
| `Ctrl+B` | `"` | Split the screen top/bottom |
| `Ctrl+B` | `%` | Split the screen left/right |
| `Ctrl+B` | arrow keys | Move between split panes |
| `Ctrl+B` | `[` | **Scroll mode** — arrows/PageUp to scroll back, `q` to exit |
| `Ctrl+B` | `?` | Show all keybindings |
| `Ctrl+B` | `,` | Rename the current window |

> **The one that catches everyone out:** inside tmux, your mouse scroll wheel may not
> scroll the history. To look back at earlier output, press `Ctrl+B` then `[`, scroll with
> the arrow keys or PageUp, then press `q` to return to normal.

A genuinely useful habit is to split the screen: `Ctrl+B` then `"`, run the model in the
top pane, and run `htop` in the bottom pane to watch CPU and memory as it goes.

## 8.5 The alternative if you forget

If you started a long job *without* tmux and realise your mistake, you can rescue it:
press `Ctrl+Z` to suspend it, then type `bg` to resume it in the background, then
`disown`. This is a patch, not a fix — you lose the ability to see its output. Just use
tmux from the start.

---

# Part 9 — Editing files on the node

To change which scenario the model runs, you have to edit a Python file. There is no
graphical editor on the node, so you use a text editor that runs inside the terminal.
**nano** is the one to use: it lists its own shortcuts along the bottom of the screen.

## 9.1 Using nano

Open a file (it is created if it doesn't exist):
```bash
nano ~/AdvAppliedEnergy_Pathways_2025/pycode/testMultiYear.py
```

You get the file contents and a two-line menu at the bottom. Move around with the **arrow
keys**, type to insert text, `Backspace` to delete.

In nano's menu, `^` means the `Ctrl` key. So `^O` means `Ctrl+O`.

| Keys | What it does |
|---|---|
| `Ctrl` + `O`, then `Enter` | **Save** (it calls this "write out") |
| `Ctrl` + `X` | **Exit** (it will offer to save if you have changes) |
| `Ctrl` + `W` | Search for text — type a word, press Enter |
| `Ctrl` + `\` | Search and replace |
| `Ctrl` + `K` | Cut the current line |
| `Ctrl` + `U` | Paste the cut line |
| `Ctrl` + `_` | Go to a specific line number |
| `Alt` + `N` | Toggle line numbers on (or start nano with `nano -l file` — see below) |
| `Ctrl` + `G` | Help |

**The save-and-quit sequence is `Ctrl+O`, `Enter`, `Ctrl+X`.** You will use it constantly.

Because you will often be told "the error is on line 347", it is worth opening files with
line numbers already switched on:
```bash
nano -l ~/AdvAppliedEnergy_Pathways_2025/pycode/main.py
```
The `-l` flag works on every version of nano. (This node has nano 7.2.)

## 9.2 A warning about Python and indentation

Python uses indentation — the spaces at the start of a line — to decide what belongs
inside what. Changing the leading spaces on a line changes the meaning of the program, and
usually breaks it with an `IndentationError`.

So when you edit the model's settings, **change only the value to the right of the `=`
sign.** Do not add or remove spaces at the beginning of a line, and do not press Tab.

## 9.3 If you would rather not use a terminal editor at all

Two good alternatives:

- **VS Code with the Remote-SSH extension** (free, on your laptop) gives you a completely
  normal graphical editor whose files happen to live on the node. Install VS Code, install
  the "Remote - SSH" extension, press `F1`, choose "Remote-SSH: Connect to Host", enter
  `taw021@pwrlab.ucsd.edu`. This is the most comfortable option by a wide margin.
- **Claude Code** — see Part 3.

---

# Part 10 — Moving files between your laptop and the node

Remember Part 1: these are separate computers. Results you generate on the node stay on
the node until you deliberately copy them across.

**Run all of these commands on your laptop, in a terminal that is *not* logged in to the
node.** They are how your laptop reaches out to the node, so if you are already on the
node they will not work.

## 10.1 scp — copy one thing

The pattern is `scp <from> <to>`, where anything on the node is written as
`taw021@pwrlab.ucsd.edu:/the/path`.

**Node → laptop** (the direction you will use most — fetching results):
```bash
scp taw021@pwrlab.ucsd.edu:/home/taw021/AdvAppliedEnergy_Pathways_2025/data_res/my_run_w2015_s2015/stat_national.csv ~/Downloads/
```

**Laptop → node**:
```bash
scp ~/Documents/new_costs.csv taw021@pwrlab.ucsd.edu:/home/taw021/AdvAppliedEnergy_Pathways_2025/data_csv/cost_assumptions/
```

**A whole folder** — add `-r`:
```bash
scp -r taw021@pwrlab.ucsd.edu:/home/taw021/AdvAppliedEnergy_Pathways_2025/data_res/my_run_w2015_s2015 ~/Downloads/
```

## 10.2 rsync — better for anything large

`rsync` only transfers what has actually changed, and can resume if interrupted. For
multi-gigabyte result folders it is far better than `scp`:

```bash
rsync -avzP taw021@pwrlab.ucsd.edu:/home/taw021/AdvAppliedEnergy_Pathways_2025/data_res/my_run_w2015_s2015 ~/Downloads/
```

The flags mean: `a` preserve everything, `v` tell me what you're doing, `z` compress
during transfer, `P` show a progress bar and allow resuming.

If you set up the `~/.ssh/config` nickname from Part 2.7, all of this gets shorter:
```bash
rsync -avzP pwrlab:~/AdvAppliedEnergy_Pathways_2025/data_res/my_run_w2015_s2015 ~/Downloads/
```

## 10.3 FileZilla — the drag-and-drop option (recommended for Windows)

If you would rather drag files than type paths, **FileZilla** gives you a two-panel window: your laptop's
files on the left, the node's files on the right. You drag files between them. The
original authors' README recommends exactly this approach.

### 10.3.1 Install it

1. Go to **https://filezilla-project.org/download.php?type=client**
2. Download **FileZilla Client** — the free one. You do **not** need FileZilla Pro or
   FileZilla Server.
3. Run the installer.

> **Watch out during installation.** The official FileZilla installer has historically
> bundled optional extra software on some download mirrors. Read each screen and
> **decline any offer to install additional programs, toolbars or "managers"**. Choosing
> the "Custom" install and unticking extras is the safe path. Downloading from the
> official site above rather than a software-aggregator site avoids most of this.

### 10.3.2 Connect with Site Manager

Use Site Manager rather than the Quickconnect bar — it saves your settings so you only do
this once.

1. Open FileZilla.
2. **File → Site Manager** (or `Ctrl` + `S`).
3. Click **New site** and name it `pwrlab`.
4. Fill in the **General** tab:

   | Field | Value |
   |---|---|
   | **Protocol** | `SFTP - SSH File Transfer Protocol` ← **must change this**, it defaults to FTP |
   | **Host** | `pwrlab.ucsd.edu` |
   | **Port** | `22` |
   | **Logon Type** | `Ask for password` (or `Key file` — see below) |
   | **User** | `taw021` |

5. Click **Connect**.

The very first time, a dialog appears saying the host key is unknown. This is the same
"have I met this machine before" check from Part 2.3. Tick **Always trust this host** and
click **OK**.

### 10.3.3 Using an SSH key instead of a password

This is optional — password login works fine. If you set up a key in Part 2.7, you can
have FileZilla use it instead:

1. **Edit → Settings → Connection → SFTP**
2. Click **Add key file...**
3. Browse to `C:\Users\<YourName>\.ssh\id_ed25519` (you may need to change the file-type
   dropdown to **All files** to see it, as it has no extension).
4. FileZilla will say the key is in OpenSSH format and offer to **convert it to PuTTY's
   .ppk format** — say **Yes**. It writes a converted copy and leaves your original alone.
5. Back in Site Manager, set **Logon Type** to `Key file` and point it at the converted
   `.ppk` file.

### 10.3.4 Getting around the two panels

- **Left panel = your Windows laptop.** Top half is the folder tree, bottom half is the
  contents.
- **Right panel = the node.** Same arrangement.
- The box at the top right, **Remote site**, is where you type a path on the node. Paste
  this in and press Enter to land in the project:
  ```
  /home/taw021/AdvAppliedEnergy_Pathways_2025
  ```
- **To download**, drag from right to left — or right-click a file and choose
  **Download**.
- **To upload**, drag from left to right, or right-click → **Upload**.
- Transfers appear in the queue at the bottom. A completed transfer moves to the
  **Successful transfers** tab; anything that fails lands in **Failed transfers**, where
  you can right-click and choose **Reset and requeue** to retry.

### 10.3.5 Fetching your results

This is the job you will do most often:

1. In **Remote site**, go to
   `/home/taw021/AdvAppliedEnergy_Pathways_2025/data_res`
2. Find your run's folder (the newest one — click the **Last modified** column header to
   sort by date).
3. Drag the whole folder to your laptop's Downloads folder on the left.

If you only want the headline numbers, you do not need the whole folder — just grab
`stat_national.csv` and `stat_provincial.csv` from inside it. They are a few kilobytes,
whereas the full folder can be gigabytes.

### 10.3.6 Two things to be careful of

- **Avoid FileZilla's built-in editor for code.** It downloads the file, opens it in
  Notepad, and re-uploads it — and Windows editors can silently add Windows-style line
  endings that break Python. Edit with `nano` on the node (Part 9) or the Claude Code
  desktop app (Part 3) instead.
- **Never drag files into folders you do not recognise.** You can write anywhere under
  `/home/taw021`, and it is easy to drop a folder into the wrong place. Check the
  **Remote site** path before releasing the mouse.

### 10.3.7 If FileZilla is not to your taste

**WinSCP** (https://winscp.net) is a Windows-only alternative that many people prefer. Its
settings are identical: protocol SFTP, host `pwrlab.ucsd.edu`, port 22, user `taw021`. It
has no bundled-software history and offers a Windows-Explorer-style single-panel mode.

## 10.4 One thing to know about archives

The `unzip` command is **not installed** on this node. If you download a `.zip` file
there, extract it with Python instead — it is built in and works identically:

```bash
python3 -m zipfile -e archive.zip destination_folder/
```

To look inside an archive without extracting it:
```bash
python3 -m zipfile -l archive.zip
```

---

# Part 11 — Running the model

## 11.1 What the model actually does

It is a **capacity-expansion optimisation** of China's electricity system. You tell it a
target (say, a carbon budget consistent with 2 °C) and it works out the cheapest
combination of wind farms, solar, storage, nuclear, coal with carbon capture and
transmission lines that meets electricity demand every hour while hitting that target.

It does this decade by decade — 2030, 2040, 2050, 2060 — and **feeds each decade's answer
in as the starting point for the next**, so the capacity built in 2030 still exists in
2040. That chaining is what `testMultiYear.py` is for.

Under the bonnet it builds an enormous system of linear equations and hands it to
**Gurobi**, a commercial solver, which finds the lowest-cost solution.

## 11.2 The two scripts you can run

| Script | What it does | Typical time |
|---|---|---|
| `testMultiYear.py` | All four decades in sequence. **Use this one normally.** | 30 min (demo) to ~20 h (full) |
| `testSingleYear.py` | One decade only. Useful for quick tests. | Proportionally less |

## 11.3 The routine, step by step

Do this every time. It never changes.

**Step 1 — connect**
```bash
ssh taw021@pwrlab.ucsd.edu
```

**Step 2 — start a tmux session** (see Part 8 — do not skip this)
```bash
tmux new -s modelrun
```

**Step 3 — activate the environment**
```bash
source ~/AdvAppliedEnergy_Pathways_2025/env.sh
```
Note the word `source` at the start — it matters, and `bash env.sh` will *not* work. (The
reason: `source` runs the commands in your current shell so the changes stick; running it
as a program would make the changes in a child shell that then exits, taking them with
it.)

You will know it worked because your prompt gains a `(.venv)` prefix and you are moved
into the `pycode` folder:
```
(.venv) taw021@pwrlab:~/AdvAppliedEnergy_Pathways_2025/pycode$
```

**Step 4 — run the model**
```bash
python testMultiYear.py
```

**Step 5 — detach and go away.** Press `Ctrl+B`, then `D`. Come back with
`tmux attach -t modelrun`.

### What `env.sh` is doing for you

Four things, all of which would otherwise be easy to forget:

1. Activates the `.venv` virtual environment, so `python` means Python 3.9 with the right
   packages.
2. Sets `PYTHONPATH` to the project root. This is genuinely necessary — `plotResult.py`
   contains `from pycode.callUtility import ...`, which only resolves if the project root
   is on Python's search path.
3. Sets `MPLBACKEND=Agg`, telling the plotting library not to try to open a window.
   There is no screen on the node, so without this, plotting crashes.
4. Moves you into `pycode/`, which is where the scripts expect to be run from.

## 11.4 Running without typing all that

If you would rather have a single command, add a shortcut. Open your personal settings
file:
```bash
nano ~/.bashrc
```
Go to the very bottom (`Alt`+`/` or just hold the down arrow) and add:
```bash
alias gomodel='source ~/AdvAppliedEnergy_Pathways_2025/env.sh'
alias results='cd ~/AdvAppliedEnergy_Pathways_2025/data_res && ls -lht'
alias freespace='df -h / | tail -1'
```
Save with `Ctrl+O`, `Enter`, then exit with `Ctrl+X`. Apply it:
```bash
source ~/.bashrc
```
Now typing `gomodel` anywhere sets everything up, and `results` jumps to your output
folder with the newest run listed first.

---

## 11.5 Or: ask Claude Code to run it for you

You do not have to drive this by hand. In a Claude Code session (Part 3) you can describe
what you want in English and let it do the editing, launching and checking. This is a
genuinely good use of it — the work is fiddly, repetitive, and easy to get subtly wrong.

### The one instruction you must not omit

**Tell it to launch the run inside tmux.** A command Claude starts is a child of the Claude
session. If that session ends — you close the app, your laptop sleeps, the connection drops
— the run dies with it, exactly as described in Part 5.2. Claude will not do this unless
you ask, so make it part of the request:

> *"Start the run inside a tmux session called `run1` so it survives if I disconnect."*

A request that works well end to end:

> *"In `~/AdvAppliedEnergy_Pathways_2025`, set the scenario in `pycode/testMultiYear.py` to
> the 1.5 °C target with heat-pump heating and 7 optimisation days. Show me the diff before
> you save. Then start the run inside a tmux session called `run1`, and tell me how to check
> on it later."*

Note what that asks for: **the diff before saving**. Scenario parameters are the whole
experiment, and a wrong value discovered eighteen hours into a run costs the run. Read the
diff.

### Other things worth handing to it

| Ask | Why it helps |
|---|---|
| *"Is the run still going, and does it look healthy?"* | It can read `htop`, the log and CPU/memory at once and tell you whether the solver is working or swapping |
| *"The run failed — read the traceback and explain what went wrong."* | Explaining tracebacks and locating the real cause is something it is genuinely good at (Part 16.1) |
| *"Read `stat_national.csv` from the newest run and summarise the capacity mix by decade."* | Saves squinting at a wide CSV in the terminal |
| *"Which result folders are biggest, and which can I safely delete?"* | Disk is tight; it can check `du`, `df` and what has already been copied off |
| *"Compare `stat_national.csv` from these two runs and tell me what the scenario change did."* | The comparison between two runs is the actual output of this model (Part 4.10) |

### Three cautions

> **Claude runs commands as you, on a machine shared with thirteen other people.** Read
> what it proposes before approving, particularly anything with `rm` in it. Start in
> **Manual** permission mode, where it asks before each action.

> **It cannot see the future cost of a long run.** Before approving anything with
> `optimization_days = 365`, remember that is up to ~20 hours of a shared machine. Get it
> right at 7 days first.

> **Check the scenario actually changed.** After it edits `testMultiYear.py`, a quick
> `git diff pycode/testMultiYear.py` shows exactly what moved. This is also how you undo
> it: `git checkout pycode/testMultiYear.py` restores the committed version.

### From the node itself

If you are already in a PowerShell SSH session, you do not need the desktop app —
`claude` is installed on the node:

```bash
cd ~/AdvAppliedEnergy_Pathways_2025
claude
```

The same requests work. This also has the advantage that you are already in a terminal, so
you can start tmux yourself first and run `claude` inside it.

---

# Part 12 — Changing the scenario

## 12.1 Where the settings are

All the knobs are hard-coded near the top of the script, under the comment
`# Step 0: Set parameters (if run locally on your laptop)`. Open it:

```bash
nano ~/AdvAppliedEnergy_Pathways_2025/pycode/testMultiYear.py
```

Around **lines 34–45** you will find:

```python
optimization_days = 7
start_year = 2030
year_count = 4
node = "pc"
emission_target = "2C"
ccs_start_year = 2040
heating_electrification = "heat_pump"
renewable_cost_decline = "baseline"
endogenize_firm_capacity = 0
demand_sensitivity = "p5"
ccs_retrofit_cost = float(3500)
custom_tag = "heat_pump"
```

Change the values to the right of the `=`. Save with `Ctrl+O`, `Enter`, `Ctrl+X`.

> Re-read Part 9.2 before you edit: do **not** change the spaces at the start of a line.

## 12.2 What each setting means

Each of these changes a constraint or a cost in the linear program (Part 4). The
right-hand column says which — worth knowing, because it tells you what a change will
actually do to the answer.

| Setting | Allowed values | Meaning |
|---|---|---|
| `optimization_days` | 5, 10, … 365 | How many days of the year to simulate. **This is the main speed/accuracy dial.** 7 for a quick test; 365 for a real result. |
| `start_year` | 2030, 2040, 2050, 2060 | First decade to solve. |
| `year_count` | 1–4 | How many decades to chain together. |
| `node` | any short text | Just a label that ends up in the output folder name. |
| `emission_target` | `"2C"`, `"15C"` | Carbon budget: 2 °C or 1.5 °C. |
| `ccs_start_year` | 2040, 2050, 2060, 2070 | When carbon capture retrofits become available. Setting 2070 effectively means "never" — that is the no-CCS scenario. |
| `heating_electrification` | `"chp_ccs"`, `"heat_pump"` | How northern China's district heating is decarbonised. |
| `renewable_cost_decline` | `"baseline"`, `"conservative"` | How fast wind/solar/battery costs fall. |
| `endogenize_firm_capacity` | 0, 1 | Whether the model decides how much firm (dispatchable) capacity to build, or takes it as given. |
| `demand_sensitivity` | `"none"`, `"p5"`, `"m5"` | Demand ±5% or unchanged. |
| `ccs_retrofit_cost` | 3500–10000 | Cost of a CCS retrofit (yuan/kW). |
| `custom_tag` | any short text | Another label for the output folder. |

## 12.3 Start small

**Test with `optimization_days = 7` first.** It takes ~30 minutes instead of ~20 hours.
Confirm the numbers look sensible, then change it to 365 and launch the real run. A typo
found eighteen hours into a run costs the entire run.

## 12.4 The published scenarios

The original authors list the exact settings used for each figure in the paper in
`README.md`, section 5.3. Those runs pass parameters on the command line rather than
editing the file — the script has that capability commented out at lines 20–31. For your
purposes, editing the values directly is simpler.

---

# Part 13 — Watching a run and reading the results

## 13.1 Is it still alive?

Attach to your tmux session and look:
```bash
tmux attach -t modelrun
```

Or, from any terminal, check whether the process exists:
```bash
ps aux | grep testMultiYear
```
If you see a line mentioning `python testMultiYear.py`, it is running.

## 13.2 Watching resource usage

```bash
htop
```
An interactive live display of every process. Press `F6` then choose `PERCENT_CPU` to sort
by CPU, or press `u` and pick `taw021` to see only your own processes. **Press `q` to
quit.** `btop` is also installed and is prettier if you prefer it.

What you want to see while the solver is working: one of your processes using several
hundred percent CPU (that is normal — 100% means one core fully busy, so 1600% means
sixteen cores), and a memory figure in the tens of gigabytes.

## 13.3 Watching the disk

```bash
df -h /
```
Run this before starting a long job and occasionally during one. If "Avail" drops below a
couple of gigabytes, stop and clear space.

## 13.4 Where the results go

Everything lands in `data_res/`, in a folder whose name is assembled from your settings.
With `year_count` greater than 1 the pattern is:

```
data_res/test_<MMDD>_<days>days_all_years_<node>_w2015_s2015/
```

So a 7-day, all-decades run with `node = "pc"` started on 14 March gives:
`data_res/test_0314_7days_all_years_pc_w2015_s2015/`

For a single-decade run (`year_count = 1`) the pattern instead includes the year and your
custom tag: `test_<MMDD>_<days>days_<year>only_<node>_<custom_tag>_w2015_s2015`.

Inside that folder:

```
test_0314_7days_all_years_pc_w2015_s2015/
├── stat_national.csv      ← ⭐ the headline summary, all decades side by side
├── stat_provincial.csv    ← the same, broken down by province
├── 2030/
│   ├── inputs/            ← exactly what went in (keep this — it documents the run)
│   ├── outputs/           ← raw solver output
│   └── outputs_processed/ ← tidied-up results and summary_national_2030.csv
├── 2040/  …
├── 2050/  …
└── 2060/  …
```

`stat_national.csv` is what you want 95% of the time. It has one row per quantity and one
column per decade.

## 13.5 Checking the answer is right

The authors give known-good numbers for the 7-day demo run, **as the script is
committed** — do not change the scenario settings if you want to reproduce them. Look at
`stat_national.csv`:

- **Line 19**, onshore wind capacity: should read **610, 1257, 1610, 2369** GW across the
  four decades
- **Line 21**, utility solar capacity: **234, 250, 389, 723** GW
- **Line 29**, new transmission capacity: **27, 93, 67, 151** GW

This install was checked against the first two decades on 13 September 2026 and matched
all six figures within rounding (608.9 / 234.1 / 27.6 and 1260.9 / 249.8 / 92.3). If your
run disagrees, the scenario settings are the first place to look.

To read it on the node:
```bash
column -s, -t ~/AdvAppliedEnergy_Pathways_2025/data_res/YOUR_RUN_FOLDER/stat_national.csv | less -S
```
(`column -s, -t` lines the columns up; `less -S` stops long lines wrapping. Arrow keys to
scroll sideways, `q` to quit.)

If those numbers match, your setup is correct. If they don't, something in the inputs has
changed.

## 13.6 Getting the results onto your laptop

From a terminal **on your laptop** (see Part 10):
```bash
rsync -avzP taw021@pwrlab.ucsd.edu:/home/taw021/AdvAppliedEnergy_Pathways_2025/data_res/YOUR_RUN_FOLDER ~/Downloads/
```
Then open the CSVs in Excel as normal.

## 13.7 Clean up after yourself

Result folders are large and the disk is small. When you are finished with a run, copy it
to your laptop and then delete it from the node:

```bash
du -sh ~/AdvAppliedEnergy_Pathways_2025/data_res/*   # see what each one costs
rm -r ~/AdvAppliedEnergy_Pathways_2025/data_res/old_run_folder
```
Remember `rm` is permanent. Make sure the copy on your laptop opened correctly *first*.

---

# Part 14 — Sharing the machine

There is **no job scheduler** on `pwrlab` — no Slurm, no queue. Nothing stops you from
taking all 72 cores and all 187 GB of RAM. That makes courtesy the only mechanism.

**See who else is here before you start something big:**
```bash
who          # who is logged in
htop         # what they are running, and how hard
uptime       # load average — the three numbers at the end
```

For `uptime`'s load average: the numbers are the average number of processes wanting CPU
over the last 1, 5 and 15 minutes. On a 72-core machine, a load of 10 is quiet and a load
approaching 72 means it is fully committed. If it already reads 60, wait.

**Limit how many cores you take.** Gurobi grabs every core it can by default. The model
already sets some solver options in `pycode/main.py` around line 347:

```python
interProvinModel.setParam('Method', 2)      # barrier algorithm
interProvinModel.setParam('Crossover', 0)   # skip crossover
```

To cap the core count, add one more line directly underneath those:

```python
interProvinModel.setParam('Threads', 16)
```

Edit it with `nano ~/AdvAppliedEnergy_Pathways_2025/pycode/main.py` — press `Ctrl+_` and
type `348` to jump straight there. Sixteen threads is a good neighbourly default and, for
a barrier solve of this size, close to the point of diminishing returns anyway.

> Setting it in the code is the reliable way. Gurobi does not read a `GRB_THREADS`
> environment variable, so `export GRB_THREADS=16` would silently do nothing.

**Lower your priority when the machine is busy.** Prefixing a command with `nice` tells Linux your job is
lower-priority, so other people's work goes first when there is contention. It costs you
very little when the machine is idle:
```bash
nice -n 10 python testMultiYear.py
```

**Watch the disk.** This is the one that actually breaks things for other people. There is
under 20 GB free. Check `df -h /` regularly and delete old runs.

**Never run anything as `sudo`** unless the administrator has explicitly walked you
through it. You do not need root access for any part of this workflow.

---

# Part 15 — Optional: the agentic-optimization framework

Everything so far runs the model **by hand**: you edit a scenario, launch it, wait, read
the CSVs. That is the right approach while you are learning, and for a handful of runs.

`agentic-optimization` is a second tool, installed at `~/agentic-optimization`, that wraps
this model so the workflow can be driven programmatically — or by an LLM agent. It is
entirely optional. Nothing in Parts 1–14 depends on it.

## 15.1 What it actually gives you

Three things that are genuinely tedious to do by hand:

1. **A run record.** Every run writes one `run_record.json` capturing the exact config,
   the solver status, timings and where the outputs went. Three months later you can still
   say precisely what produced a number. Doing this by hand — and keeping it accurate —
   is the part everyone skips.
2. **A per-run workspace.** Instead of editing `testMultiYear.py` and running in place, it
   builds a throwaway directory of **symlinks** to the model and the data, and runs there.
   The model is never modified, `data_res` never collides, and two runs can go at once.
   This is a real improvement on the `FileExistsError` problem in Part 16.5.
3. **A guardrail on what may be changed automatically.** Settings are sorted into tiers:

   | Tier | Meaning | Examples |
   |---|---|---|
   | **A** | numerics — applied automatically | `time_limit`, `threads`, `bar_conv_tol` |
   | **B** | sanctioned modelling parameters — applied, but flagged | `year`, `optimization_days`, `demand_sensitivity`, `ccs_retrofit_cost` |
   | **C** | **relaxes a policy constraint — requires a human** | `emission_target`, `ccs_start_year`, `with_shedding` |

   Tier C is the point of the whole thing. `with_shedding` lets the model drop load, which
   makes almost any infeasible scenario "solve" — the classic way a result quietly stops
   meaning what you think it means. The framework will not apply that on its own.

## 15.2 Does it work here?

Yes — verified on this node on 13 September 2026:

| Check | Result |
|---|---|
| `pytest tests/ --ignore=tests/test_fixtures.py` | **665 passed**, 0 failed |
| `pypsa_toy` smoke test (no licence needed) | OPTIMAL in 4.4 s |
| **Pathways smoke test** — 2060, 5 days, 2 °C | **OPTIMAL in 332 s**, emissions −563.47 Mt exactly at the cap |

The Pathways acceptance test had never been run green before this — the repo says so
outright. It passes.

> **Expect 10 failures in `tests/test_fixtures.py`.** The framework ships adapters for
> three models; only the one we care about, `pathways`, is installed here. The other two
> models' submodules were deliberately not fetched, to save disk on a shared machine, and
> those 10 tests check fixtures belonging to the Indonesia model (`garuda`). They fail with
> `Input data directory not found: .../models/garuda/...`, which is the expected result,
> not a broken install. Everything that touches Pathways passes. Use the `--ignore` form
> above for a clean signal.

## 15.3 Running it

The environment is already installed. Two variables tell it where the model and its data
live:

```bash
cd ~/agentic-optimization
export PATHWAYS_DATA_ROOT=$HOME/AdvAppliedEnergy_Pathways_2025
export PATHWAYS_PYTHON=$HOME/AdvAppliedEnergy_Pathways_2025/.venv/bin/python
```

Check the wiring without solving anything:

```bash
.venv/bin/python examples/pathways/smoke_test.py --dry-run
```

Then run one for real (about 5–6 minutes):

```bash
.venv/bin/python examples/pathways/smoke_test.py --days 5 --run-dir $PWD/runs/my_first_run
```

Results land in `runs/my_first_run/`: `outputs/` for the CSVs, `solver.log` for the full
Gurobi log, `run_record.json` for the provenance.

> Use tmux for this exactly as you would for a direct run (Part 8). It is the same solver
> doing the same work, and it dies the same way if your connection drops.

## 15.4 Two things that will trip you up

Both were found the first time this was run on this node.

> **`--run-dir` must be an absolute path.** A relative one fails instantly with
> `could not read config: No such file or directory`, because the driver runs as a
> subprocess from a different working directory. Use `$PWD/runs/...`, not `runs/...`.

> **A failed run leaves its workspace behind.** On success the framework deletes the
> per-run `workspace/` automatically, leaving a few MB of archived outputs. On failure it
> keeps it for debugging — and that workspace holds the model's per-province hourly CSVs,
> which came to **1.5 GB** for a single failed run here. After any failure, check
> `du -sh ~/agentic-optimization/runs/*` and delete the dead run. On a disk with under
> 10 GB free this matters quickly.

> **Do not go below `optimization_days = 5`.** The shipped `SMOKE_CONFIG` uses 3, and it
> crashes with `KeyError: 0.8134`. The cause is worth understanding, because it is a
> property of the model rather than the framework — see below.

### Why 3 days breaks the model

At `initData.py:387` the model precomputes a cost lookup table across capacity factors:

```python
for i in np.arange(0.0020, 0.8000, 0.0001):
```

Capacity factors from 0.2% up to **80%**. Later, at `initData.py:488`, it looks a cell up
in that table by its capacity factor **averaged over the sampled hours**:

```python
gen_cost = cf_elep[file][CF] * year_cf / CF
```

Over a year, no cell averages above 80%. Over 72 hours, a windy cell easily can — and one
did, at 81.34%, which is not a key in the table. Hence `KeyError: 0.8134`.

This is why the model's own README lists the supported values as "5, 10, ..., 365". Three
days was never a supported configuration. **The framework did nothing wrong; it drove the
model outside a range the model does not defend.** That is a useful thing to have learned
about the model, and a good illustration of why Part 16.1 — reading the traceback rather
than the message — is worth the effort.

## 15.5 Driving it by conversation

The framework ships six agent skills in `.claude/skills/`, which is what makes it more than
a scripting layer. Open a Claude Code session in `~/agentic-optimization` and they become
available:

| Skill | What it does |
|---|---|
| `scenario-builder` | Turns "build a high-solar 2030 case" into a validated config |
| `model-runner` | Executes one config, captures `solver.log`, writes `run_record.json` |
| `run-monitor` | Watches a solve live and decides whether to keep waiting, stop, or abort |
| `log-analyzer` | Diagnoses an INFEASIBLE / errored / time-limited run |
| `output-analyzer` | Sanity-checks a solved run for implausible dispatch, cost or emissions |
| `refiner` | Proposes tier-bounded config changes — and refuses to silently relax a policy constraint |
| `supervisor` | Runs the whole loop until it solves, gets stuck, or hits a Tier-C block |

The difference from Part 11.5 is the guardrail. Asking plain Claude Code to "get this to
solve" invites it to reach for `with_shedding`, which lets the model drop load and makes
almost anything solve. Here that is Tier C: the loop **halts and asks a human**. If you
intend to iterate automatically toward a result, this is the safer place to do it.

## 15.6 When not to bother

If you want to run one scenario and look at the answer, Part 11 is simpler and you should
use it. The framework earns its keep when you are running **many** scenarios, when you
need to defend later exactly what produced a result, or when you want an agent to iterate
without quietly relaxing the constraint the study rests on.

---

# Part 16 — When things go wrong

## 16.1 How to read a Python error

The specific errors below are the ones you are most likely to hit, but you will
eventually hit one that is not listed. Python errors are readable once you know the shape.

```
Traceback (most recent call last):
  File ".../testMultiYear.py", line 185, in <module>
    initCellData(vre=vre, ...)
  File ".../initData.py", line 731, in initCellData
    re_county = gpd.read_file(work_dir + 'data_shp' + dir_flag + 're_county_level.shp')
  File ".../geopandas/io/file.py", line 164, in _is_zip
    parsed = fiona.path.ParsedPath.from_uri(path)
AttributeError: module 'fiona' has no attribute 'path'
```

Three rules:

1. **Read the last line first.** That is the actual error. Everything above it is history.
2. **Read the traceback bottom-up.** The bottom frame is where it broke; each line above is
   what called it. The lowest frame with *your* project path in it — here
   `initData.py, line 731` — is where to look first, because frames below that are inside
   libraries.
3. **The error type tells you the category:**

| Type | Means |
|---|---|
| `ModuleNotFoundError` | A package is missing, or the wrong Python is active |
| `FileNotFoundError` | A data file is missing or a path is wrong |
| `AttributeError` | Something exists but not the piece being asked for — very often a library version mismatch |
| `KeyError` | A name was looked up in a dictionary or dataframe column that does not contain it |
| `MemoryError` | Ran out of RAM (Part 5.3) |
| `IndentationError` / `SyntaxError` | The file was edited badly (Part 9.2) |

The example above was a genuine version mismatch: geopandas called `fiona.path`, which
fiona removed in version 1.10. The fix was pinning `fiona<1.10`. You could not have guessed
that from the message alone — but "AttributeError inside a library I did not write" points
straight at *versions*, which is the useful instinct.

**When you are stuck**, copy the whole traceback into the Claude Code session (Part 3) and
ask what it means. Explaining a traceback and locating the cause is something it does well,
and you will learn the pattern faster by seeing it explained a few times.

## 16.2 `ModuleNotFoundError: No module named 'pandas'`

You forgot to activate the environment. Run:
```bash
source ~/AdvAppliedEnergy_Pathways_2025/env.sh
```
Check your prompt starts with `(.venv)`. This is the single most common error.

## 16.3 `ModuleNotFoundError: No module named 'pycode'`

`PYTHONPATH` is not set — which again means `env.sh` was not sourced, or you activated
`.venv` by hand instead. Use `env.sh`.

## 16.4 `FileNotFoundError: .../data_mat/RegionDemand_Rev2.mat`

A file from the Zenodo input data is missing. That data is already installed, so this
means something has been moved or deleted. Check the three folders are still populated:

```bash
du -sh ~/AdvAppliedEnergy_Pathways_2025/data_{pkl,mat,shp}
```

You should see roughly 3.3G, 868M and 42M. If one is empty, re-download from
https://doi.org/10.5281/zenodo.14907700 — you need the `AdvAppliedEnergy_Pathways_2025.zip`
archive, and only its `data_pkl`, `data_mat` and `data_shp` folders.

## 16.5 `FileExistsError: ... /provin_demand_hourly`

You are re-running with the same settings on the same day, and the previous run's output
folder is still there. The scripts create their folders with `os.mkdir`, which fails if
the folder already exists — they are not designed to resume or overwrite.

Delete the part-finished run and start again:

```bash
rm -r ~/AdvAppliedEnergy_Pathways_2025/data_res/test_<MMDD>_<days>days_all_years_<node>_w2015_s2015
```

Use `ls ~/AdvAppliedEnergy_Pathways_2025/data_res/` first to get the exact folder name.
Changing `custom_tag` or `node` in the script also sidesteps it, by giving the new run a
different folder name — useful when you want to keep the earlier attempt.

## 16.6 `GurobiError: License expired`

Should not happen before **13 September 2027**, which is when the installed licence runs
out. If you see it sooner, check the licence file is still there and readable:

```bash
grep -E "^(TYPE|EXPIRATION|HOSTNAME|USERNAME)" ~/gurobi.lic
```

You should see `TYPE=ACADEMIC`, `EXPIRATION=2027-09-13`, `HOSTNAME=pwrlab`,
`USERNAME=taw021`. If the file is missing, or if `USERNAME` is not the account you are
logged in as, that is the problem — the licence is locked to one user on one machine
(Part 7.1). A renewal or a new key comes from the lab administrator; see
`SETUP_ADMIN_REQUEST.md`.

## 16.7 `command not found: python`

Either you have not sourced `env.sh`, or you are on your own laptop rather than the node.
Check the prompt: it should say `taw021@pwrlab`.

## 16.8 `Permission denied` when writing a file

You are trying to write somewhere outside your home folder. You can only write inside
`/home/taw021`. Check with `pwd`.

## 16.9 `No space left on device`

The disk is full. Run `df -h /`, then `ncdu ~` to find what is using space, and delete old
result folders.

## 16.10 The connection dropped mid-run

If you used tmux: nothing is lost. Reconnect and run `tmux attach -t modelrun`.
If you did not: the run is gone. Start again, with tmux this time.

## 16.11 `IndentationError` or `SyntaxError` after editing

You changed the leading spaces on a line, or introduced a stray character. The error
message names the line number. Open the file, go to that line (`Ctrl+_` in nano), and
compare it with the lines around it — they should line up.

To discard your edits entirely and restore the original file from Git:
```bash
cd ~/AdvAppliedEnergy_Pathways_2025
git checkout pycode/testMultiYear.py
```
This discards *all* your changes to that file, so note down your settings first.

## 16.12 Terminal is spewing text / has frozen

`Ctrl+C` stops the running command. If the display is garbled afterwards, type `reset` and
press Enter. If `Ctrl+C` does nothing and you are in tmux, detach with `Ctrl+B` `D` and
investigate with `htop`.

## 16.13 It is running but seems stuck with no output

Large solves genuinely do go quiet for long stretches. Check `htop`: if your process is
consuming CPU, it is working. If it is using 0% CPU and lots of memory, it may be swapping
— check `free -h`.

---

# Part 17 — Cheat sheet

## Connect

```bash
ssh taw021@pwrlab.ucsd.edu            # from PowerShell on Windows, or Terminal on Mac
exit                                 # log out
```

## Run the model (the whole routine)

```bash
ssh taw021@pwrlab.ucsd.edu
tmux new -s modelrun
source ~/AdvAppliedEnergy_Pathways_2025/env.sh
python testMultiYear.py
# press Ctrl+B then D to detach and walk away
```

## Come back to it

```bash
ssh taw021@pwrlab.ucsd.edu
tmux attach -t modelrun
```

## Getting around

| Command | Meaning |
|---|---|
| `pwd` | Where am I? |
| `ls -lh` | What's here, with sizes |
| `cd folder` / `cd ..` / `cd ~` | Go in / up / home |
| `less file.csv` | Read a file (`q` to quit) |
| `mkdir name` | New folder |
| `cp a b` / `cp -r a b` | Copy file / folder |
| `mv a b` | Move or rename |
| `rm file` / `rm -r folder` | **Delete — permanent, no undo** |
| `df -h /` | Free disk space |
| `du -sh *` | Size of each item here |
| `ncdu ~` | Interactive disk usage browser |

## Keyboard

| Keys | Effect |
|---|---|
| `Tab` | Auto-complete a name |
| `↑` / `↓` | Previous / next command |
| `Ctrl`+`R` | Search command history |
| `Ctrl`+`C` | **Stop what's running** |
| `Ctrl`+`L` | Clear the screen |
| `Ctrl`+`D` | Log out |
| `Ctrl`+`A` / `Ctrl`+`E` | Start / end of line |

## tmux

| Command / Keys | Effect |
|---|---|
| `tmux new -s NAME` | Start a session |
| `tmux ls` | List sessions |
| `tmux attach -t NAME` | Reconnect |
| `Ctrl+B` then `D` | **Detach, leave it running** |
| `Ctrl+B` then `[` | Scroll back (`q` to exit) |
| `Ctrl+B` then `"` | Split screen horizontally |
| `Ctrl+B` then arrows | Move between panes |

## nano

| Keys | Effect |
|---|---|
| `Ctrl`+`O`, `Enter` | Save |
| `Ctrl`+`X` | Exit |
| `Ctrl`+`W` | Search |
| `Ctrl`+`_` | Go to line number |

## Move files (run on your laptop, not the node)

```bash
# fetch results from the node
rsync -avzP taw021@pwrlab.ucsd.edu:/home/taw021/AdvAppliedEnergy_Pathways_2025/data_res/RUN_FOLDER ~/Downloads/

# send a file to the node
scp myfile.csv taw021@pwrlab.ucsd.edu:/home/taw021/AdvAppliedEnergy_Pathways_2025/data_csv/
```

## Move files with a mouse instead (FileZilla)

| Setting | Value |
|---|---|
| Protocol | `SFTP - SSH File Transfer Protocol` (**not** FTP) |
| Host | `pwrlab.ucsd.edu` |
| Port | `22` |
| User | `taw021` |
| Remote site | `/home/taw021/AdvAppliedEnergy_Pathways_2025` |

Drag right-to-left to download, left-to-right to upload. Full walkthrough in Part 10.3.

## Claude Code desktop app (Windows)

| Setting | Value |
|---|---|
| Environment | `+ Add SSH connection` |
| SSH Host | `taw021@pwrlab.ucsd.edu` |
| SSH Port | `22` |
| Identity File | leave blank |
| Project folder | `/home/taw021/AdvAppliedEnergy_Pathways_2025` |

You are prompted for the account password. No integrated terminal in SSH sessions, so
start long runs from a separate PowerShell `ssh` window inside tmux. Full walkthrough in
Part 3.

## Monitor

```bash
htop                    # live CPU and memory (q to quit)
who                     # who else is logged in
uptime                  # load average
df -h /                 # free disk
free -h                 # free memory
ps aux | grep python    # is my run alive?
```

## Model-specific paths

| What | Where |
|---|---|
| Project root | `~/AdvAppliedEnergy_Pathways_2025` |
| Scripts to run | `~/AdvAppliedEnergy_Pathways_2025/pycode/` |
| Scenario settings | `pycode/testMultiYear.py`, lines ~34–45 |
| Results | `~/AdvAppliedEnergy_Pathways_2025/data_res/` |
| Headline summary | `data_res/<run folder>/stat_national.csv` |
| Environment setup | `source ~/AdvAppliedEnergy_Pathways_2025/env.sh` |

## The five rules

1. **Always use tmux for anything that takes more than a minute.**
2. **Always `source env.sh` before running Python.**
3. **Test with `optimization_days = 7` before committing to 365.**
4. **`rm` is permanent. Read the line twice.**
5. **Check `df -h /` — the disk is small and shared.**

---

## Getting help

- **This model:** the authors ask that you contact Zhenhua — `zhenhua at ucsd dot edu`.
- **The original documentation:** `README.md` in the project folder.
- **Outstanding setup issues:** `SETUP_ADMIN_REQUEST.md` in the project folder.
- **Claude Code:** https://code.claude.com/docs
- **Anything Linux:** `man <command>`, or just ask Claude Code — explaining terminal errors
  in plain English is something it is genuinely good at.
