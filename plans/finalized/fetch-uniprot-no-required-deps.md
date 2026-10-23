# Plan: make `fetch_by_uniprot` / `list_uniprot_structures` dependency-free

Tags: structure, fetch_uniprot, optional-dependencies, biopython, requests

## Current state

- **Biopython is already optional.** It is used only by `_search_biopython`, the 3rd and
  last fallback (RCSB GraphQL → UniProt REST → Biopython ExPASy). Without it, that one
  step fails and gets skipped.
- **`requests` is what's actually required.** Both commands stop at the top with
  "requests is required" if it's missing, so nothing runs.
- Things that are wrong right now:
  - When Biopython is missing, `_search_biopython` logs an **error**,
    "install pymolish[biopython] to use fetch_by_uniprot". It logs this even when the
    first search step already succeeded, and the message suggests the command needs
    Biopython, which it doesn't.
  - The Biopython step adds nothing. `ExPASy.get_sprot_raw` calls
    `rest.uniprot.org`, the same data source as step 2 (UniProt REST). If step 2 fails,
    step 3 almost certainly fails too.

## What gets skipped without each package (today)

| Missing     | Effect                                                                    |
|-------------|---------------------------------------------------------------------------|
| biopython   | Only the 3rd fallback (ExPASy). That fallback repeats step 2, so nothing is lost. |
| requests    | Everything: both commands exit with an error before searching.            |

## Steps

1. Replace `requests` with stdlib `urllib.request` + `json` in `_search_rcsb_graphql`,
   `_search_uniprot_rest` and the details loop of `list_uniprot_structures`. Add one small
   `_http_json(url, payload=None, timeout=30)` helper to the module.
2. Keep `_search_biopython` as an optional last fallback: when Biopython is missing, log an info note ("biopython not installed - skipping ExPASy fallback") and return `[]`. (User decision.)
   RCSB GraphQL → UniProt REST.
   - Alternative if we want to keep it: keep the function, but on `ImportError` return
     `[]` with a `verbose`-only "biopython not installed, skipping ExPASy fallback" log
     instead of an error.
3. Remove the `requests` import guards at the top of both public commands.
4. Update the docstrings: drop "Requires requests / biopython".
5. `structure/__init__.py`: drop "(requires requests)" from both descriptions.
6. `pyproject.toml`: remove `requests` from the `biopython` and `all` extras, since nothing
   uses it any more.
7. `tests/test_optional_dependencies.py`: remove the two uniprot cases from the
   "cannot run" list. Add a check that, with every extra blocked, `fetch_by_uniprot`
   reaches the network layer (mock `urllib.request.urlopen`) instead of exiting early.
8. Docs: `docs/commands/structure.md` and the README extras lines (remove `requests`).
9. Bump the patch version in `pyproject.toml` and `src/pymolish/__init__.py`, run
   `ruff` + `pytest`, commit, and move this plan to `plans/finalized/`.

## Expected outputs

- Both commands work on a bare PyMOL install with no extras.
- Biopython stays an optional extra, used only by `search_sequence`.
- No misleading "install biopython" error during a successful fetch.
- Tests pass, docs match the code, version bumped.
