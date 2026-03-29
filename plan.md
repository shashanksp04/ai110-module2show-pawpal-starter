# PawPal+ — Design plan

## Scenario (from README)

A busy pet owner needs help staying consistent with pet care. The app should:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

---

## Main identities (domain model)

These are the core **nouns** for UML and for splitting responsibilities.

**Scope:** Class fields match **`app.py`** demo inputs: owner name, pet name, species, and each task’s title, duration (minutes), and priority.

| Identity | Role | Notes |
|----------|------|--------|
| **Owner** | Person using the app | **Name** — matches `owner_name` in `app.py` |
| **Pet** | Subject of care | **Name**, **species** — matches `pet_name` and `species` in `app.py` |
| **Task** (pet care task) | Unit of work to schedule | **Title**, **duration (minutes)**, **priority** — matches each task dict in `app.py` |
| **Daily plan / schedule** | Output for one day | **Separate type** from the scheduler: the artifact (ordered slots, which task, when) you display. The **Scheduler** creates it; it is not merged into the scheduler class. |
| **Scheduler** | Builds the daily plan | **Its own class**, distinct from **DailyPlan**. It takes an **Owner**, **Pet**, and list of **Tasks** and **produces** a **DailyPlan**. **Reasoning / explanation** (per-task or summary “why”) **lives here** — the scheduler generates it as part of building the plan (explanations may still be stored on the returned plan or alongside it for the UI). |

---

## Core user actions (aligned with `app.py`)

These are the only actions the starter UI exposes. Anything not listed here (e.g. edit/delete tasks, clear list, dates, time budget) is out of scope until **`app.py`** adds controls for it.

### Inputs

1. **Set owner name** — `Owner name` text field (`owner_name`).
2. **Set pet name** — `Pet name` text field (`pet_name`).
3. **Set species** — `Species` select box (`dog` / `cat` / `other`).

### Tasks

4. **Set task fields** — `Task title`, `Duration (minutes)` (1–240), `Priority` (`low` / `medium` / `high`).
5. **Add task** — **`Add task`** appends one task dict `{ title, duration_minutes, priority }` to `st.session_state.tasks`.
6. **See tasks** — If the list is non-empty, **Current tasks:** plus a table; otherwise the **No tasks yet** message.

### Schedule

7. **Generate schedule** — **`Generate schedule`** is the action that should build a plan; the starter only shows a **not implemented** warning until scheduling is wired here and results are displayed.

### Passive (reading only)

- Open **Scenario** or **What you need to build** expanders.

### Mapping to the domain model

| User action | Domain touchpoints |
|-------------|---------------------|
| Set owner name | **`Owner`** |
| Set pet name / species | **`Pet`** |
| Add tasks / see task list | **`Task`** instances (from session task dicts) |
| Generate schedule | **`Scheduler.build_plan`** → **`DailyPlan`** (and **`PlanSlot`** for display) |

---

## Classes: attributes, constructors, getters

Implementation lives in **`models.py`**. Instance data is stored on private attributes (`_name`, etc.); **getters** are `@property` methods except **`DailyPlan.PlanSlot`**, which uses a frozen **`@dataclass`** plus explicit **`get_order`**, **`get_task`**, **`get_explanation`** methods.

### Owner

| Kind | Details |
|------|---------|
| **Constructor** | `__init__(name)` |
| **Attributes** | `name` (`str`) |
| **Getters** | `name` |

### Pet

| Kind | Details |
|------|---------|
| **Constructor** | `__init__(name, species)` |
| **Attributes** | `name` (`str`), `species` (`str`) |
| **Getters** | `name`, `species` |

### Task

| Kind | Details |
|------|---------|
| **Constructor** | `__init__(title, duration_minutes, priority)` |
| **Attributes** | `title` (`str`), `duration_minutes` (`int`), `priority` (`str`) |
| **Getters** | `title`, `duration_minutes`, `priority` |

### DailyPlan

| Kind | Details |
|------|---------|
| **Constructor** | `__init__(pet, slots)` — `slots` is a list of `DailyPlan.PlanSlot` |
| **Attributes** | `pet` (`Pet`), `slots` (list of `PlanSlot`; getter returns a copy) |
| **Getters** | `pet`, `slots` |

#### `DailyPlan.PlanSlot` (nested frozen dataclass)

| Kind | Details |
|------|---------|
| **Fields** | `order` (`int`), `task` (`Task`), `explanation` (`str`) |
| **Getters** | `get_order()`, `get_task()`, `get_explanation()` |

### Scheduler

| Kind | Details |
|------|---------|
| **Constructor** | `__init__()` — no instance fields |
| **Methods** | `build_plan(owner, pet, tasks) -> DailyPlan` — produces the plan and explanations; **stub** currently returns `DailyPlan(pet, [])` until scheduling logic is implemented |
