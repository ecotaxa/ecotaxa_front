# Python tests of the GUI (`appli/gui`)

These tests need no database and no back-end. Every back-end call is mocked.

```bash
# from the repo root
venv/bin/pip install -r QA/py/requirements-test.txt
venv/bin/pytest QA/py                               # whole suite, a few seconds
venv/bin/pytest QA/py --cov=appli/gui --cov-report=term-missing
```

## How it works

- **Configuration:** the app reads `QA/py/conftest_config.cfg` through `ECOTAXA_FRONT_CONFIG`, so `config/config.cfg` is not needed.
- **Generated client:** `tests/fakes.py` `FakeBackend` replaces every generated API class (`to_back.ecotaxa_cli_py.api.*`) with a strict mock. A call that the test did not set up with `backend.on(Api, "method", returns=... | raises=... | side_effect=...)` fails the test, with the call in the message.
- **Raw `requests` calls** (project and collection lists, uploads): register them on `backend.requests`, which is a `responses.RequestsMock`.
- **Network guard:** any real TCP connection fails the test.
- **Users:** the fixtures `anon_client`, `user_client`, `admin_client` and `users_admin_client` log in through the real `user_loader`. They differ only in the `can_do` rights.
- **Page data:** `fakes.populate(backend)` sets up plausible answers for the read calls of most pages (project 1, collection 1, user/guest/organization 3).

## Layout

- `tests/unit/`: the helpers (utils, commontools, formulae, files, jobs, organizations, JSON renderers).
- `tests/routes/test_auth_matrix.py`: who may open every `appli.gui` route. A new route must be added to `PUBLIC`, `ADMIN` or `APP_ADMIN`, or be login-protected.
- `tests/routes/test_*.py`: what the pages render and what the forms send to the back-end.

Tests marked `xfail(strict=True)` are known bugs. Once a bug is fixed, its test passes, `strict` turns that into a failure, and the marker must be removed.
