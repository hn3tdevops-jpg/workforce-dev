# workforce-dev
A GitHub-first, PythonAnywhere-ready developer hub for the Workforce project. It centralizes docs, progress reports, project dashboards, script catalogs, package validation, file tracking, search, and admin tooling for managing the full Workforce development lifecycle.

## Running Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

CI runs automatically on every push and pull request via GitHub Actions.

## Known Limitations

- **Script execution** is currently stubbed and disabled by default. Setting `DEVHUB_ENABLE_SCRIPT_EXECUTION=true` still returns a "disabled" error — no actual subprocess execution is implemented. All run attempts are audit-logged.
- **Package install** is not implemented. The `DEVHUB_ENABLE_PACKAGE_INSTALL` flag exists for future use but no install route or UI is present.
- **Search** uses SQL `LIKE` queries; no full-text search engine is integrated.
