# Automation Agents

This project relies on a small set of automation "agents"—CLI tools and CI jobs that keep the codebase healthy. This document explains what each agent does, how to run it locally, and how it is wired into GitHub Actions.

## Formatting Agent (Black)

- **Purpose:** Enforces the project-wide Python style (88-character lines, Python 3.8+ targets).
- **Local command:** `python -m black .`
- **CI hook:** `lint` job → "Run black" step.
- **Tips:**
  - Always run Black before committing to avoid churn in `black --check`.
  - Target the whole repository; the config lives in `pyproject.toml` under `[tool.black]`.

## Import Agent (isort)

- **Purpose:** Normalises import ordering using Black-compatible rules.
- **Local command:** `python -m isort .`
- **CI hook:** `lint` job → "Run isort" step.
- **Tips:**
  - isort shares the 88-character limit (`profile = "black"`).
  - If you only touched a subset of files, limit the path to speed things up.

## Lint Agent (flake8)

- **Purpose:** Static analysis for style and correctness (E/W/F codes).
- **Local command:** `python -m flake8`
- **CI hook:** `lint` job → "Run flake8" step.
- **Config:** Inherits defaults plus the `max-line-length=88` rule from the toolchain.
- **Tips:**
  - Run after Black/isort; most E501 issues disappear once formatting is consistent.
  - Keep migrations and tests in mind—CI checks them too.

## Test Agent (pytest + django CMS matrix)

- **Purpose:** Runs the unit test suite across supported Django/django CMS versions.
- **Local smoke test:**
  ```bash
  export DJANGO_SETTINGS_MODULE=tests.settings
  export PYTHONPATH="$(pwd):$(pwd)/tests"
  python -m pip install -e .
  python -m pip install pytest pytest-django django-mptt
  python -m pytest -q
  ```
- **CI matrix:** `tests` job installs the matrix-defined Django/django CMS pairs (3.2/3.11, 4.2/4.1, 4.2/5.0), plus: `django-filer`, `django-mptt`, `easy-thumbnails`, `django-sekizai`.
- **Special settings:**
  - `tests/settings.py` registers the CMS stack, toggles `CMS_CONFIRM_VERSION4 = True`, and uses an in-memory SQLite DB.
  - Assets rely on Sekizai blocks; ensure `PYTHONPATH` includes `tests/` when running manually.

## CI Agent (GitHub Actions)

- **Workflow file:** `.github/workflows/ci.yml`
- **Jobs:**
  1. `lint` – runs Black/isort/flake8 with Python 3.10.
  2. `tests` – executes the matrix described above after installing gettext.
- **Environment setup:** `DJANGO_SETTINGS_MODULE` and `PYTHONPATH` are exported in the test job so pytest-django finds `tests.settings`.
- **Failure triage:**
  - Formatting failures → re-run Black/isort locally.
  - Import errors (e.g., `ModuleNotFoundError`) → ensure dependencies are in `pyproject.toml` *and* the CI install list.
  - CMS-related errors → adjust `tests/settings.py` to mirror the expected configuration.

## Working With Agents

- Run the Formatting, Import, and Lint agents before pushing. They are fast and prevent CI round-trips.
- Keep dependencies aligned: when you add a package to `pyproject.toml`, update the CI "Install test dependencies" step.
- When troubleshooting Sekizai-heavy templates, render them through the helper wrappers in `tests/test_plugins.py` so `render_block` output is captured.
- The agents follow an "auto-fix, then verify" philosophy—let them modify files, commit the result, and use `pytest` to confirm behaviour.

## Troubleshooting Cheat Sheet

- **`black --check` fails but `black` passes locally** → ensure the same version (CI uses the latest stable release; keep `pip install black` up to date).
- **`pytest` cannot import `tests.settings`** → verify `PYTHONPATH` and the presence of `tests/__init__.py`.
- **`django CMS 4` warnings** → confirm `CMS_CONFIRM_VERSION4 = True` remains in the settings.
- **Sekizai context errors** → use plain dicts or call `.flatten()` only when rendering simple templates; full templates should receive the context object directly.

Stay disciplined with these agents and the CI pipeline will stay green.
