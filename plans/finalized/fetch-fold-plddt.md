# Plan: `fetch_fold` — AlphaFold / ESMFold fetcher with pLDDT coloring + legend

Tags: structure, visualization, alphafold, esmfold, plddt, network, stdlib-only

## Goal

One command. User gives a UniProt accession **or** a raw amino-acid sequence.
Plugin downloads the predicted model (AlphaFold DB for accessions, ESMFold for
sequences), loads it, colors by pLDDT (red = low → dark blue = high) and shows a
legend. A second, reusable command does only the coloring, for models the user
loaded themselves.

## Commands

| Command        | Package                     | Args                                                          |
|----------------|-----------------------------|---------------------------------------------------------------|
| `fetch_fold`   | `extensions/structure/`     | `query, name=None, source=auto\|alphafold\|esmfold, color=1, legend=1` |
| `color_plddt`  | `extensions/visualization/` | `selection=all, legend=1, palette=af\|gradient`               |

`fetch_fold` calls `color_plddt` at the end; no shared state beyond that.

## Data sources (stdlib `urllib` only, same pattern as `fetch_uniprot._http_json`)

- **AlphaFold DB**: `GET https://alphafold.ebi.ac.uk/api/prediction/{acc}` → JSON list,
  take `[0]["pdbUrl"]`, download text. 404 ⇒ not in AFDB.
- **ESMFold**: `POST https://api.esmatlas.com/foldSequence/v1/pdb/` with the raw sequence
  as body → PDB text. Limit ~400 aa; log a warning above that and let the API error.
- **Fallback** (one line): accession not in AFDB ⇒ fetch FASTA from
  `https://rest.uniprot.org/uniprotkb/{acc}.fasta`, strip header, send to ESMFold.

Query detection: matches UniProt regex
`^([OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2})$` ⇒ accession;
else all chars in `ACDEFGHIKLMNPQRSTVWY` (after stripping whitespace, uppercase) ⇒ sequence;
else error via `plog`. `source=` overrides detection.

Load with `cmd.read_pdbstr(text, name)`; name defaults to `AF_{acc}` / `ESM_{sha1[:6]}`.
Both services store pLDDT in the B-factor column, so no parsing needed.

## Coloring + legend (native PyMOL, no deps)

- `gradient` (optional, continuous):
  `cmd.spectrum("b", "red_yellow_blue", sel, minimum=0, maximum=100)`; PyMOL's
  built-in `blue` is already the dark end. If a darker top is wanted, `cmd.set_color`
  a custom color and use it in the spectrum palette string (custom names are accepted).
- `af` palette (default, chosen after review: linear 0-100 hides the 50-90 band): the standard AlphaFold 4 bins via `cmd.color` on `b<50`, `b<70`, `b<90`,
  rest (orange `#FF7D45`, yellow `#FFDB13`, light blue `#65CBF3`, dark blue `#0053D6`).
- **Legend** (`AF_pLDDT_legend`, deleted/recreated on each call, `legend=0` skips it):
  - `gradient`: `cmd.ramp_new(..., [0, 50, 100], [red, yellow, blue])` color bar.
  - `af`: PyMOL's ramp legend only prints min/max as `%0.3f`, so bin labels are
    impossible there. Instead: four `cmd.pseudoatom` spheres beside the model
    (right of `get_extent`), colored per bin, labelled `<50`, `50-70`, `70-90`,
    `90-100`. Rotates with the scene; appears in ray-traced output.

## Steps

1. `extensions/visualization/plddt.py`: `color_plddt(selection="all", legend=1, palette="gradient")`.
   Returns the number of atoms colored (`cmd.count_atoms`). Google-style docstring per template.
2. `extensions/structure/fetch_fold.py`: `_is_accession`, `_is_sequence`, `_fetch_alphafold(acc)`,
   `_fetch_esmfold(seq)`, `_uniprot_fasta(acc)`, public `fetch_fold(...)`. Returns the object
   name or `None`. Reuse `_http_json` from `fetch_uniprot` (import it; add a sibling
   `_http_text` there for plain-text bodies).
3. Register both in the category `__init__.py` files with category, description, examples,
   tags, see_also (`fetch_fold` ↔ `color_plddt` ↔ `fetch_by_uniprot`). Autocompletion:
   `color_plddt` arg 0 → `completers.object_name`.
4. Tests: `tests/test_structure/test_fetch_fold.py` (detection regex, mocked `urlopen`
   returning AFDB JSON / PDB text / 404 → ESMFold fallback, asserts `cmd.read_pdbstr` called)
   and `tests/test_visualization/test_plddt.py` (spectrum + ramp_new called with 0–100 range,
   `legend=0` skips ramp). Mocked `pymol.cmd` from `conftest.py`.
5. Docs: add both commands to `docs/commands/structure.md` and `docs/commands/visualization.md`.
6. `ruff check . && ruff format .`, `pytest tests/`, bump patch version in `pyproject.toml`,
   move this plan to `plans/finalized/`.

## Expected outputs

- `fetch_fold P04637` → loads `AF_P04637`, colored red→dark blue by pLDDT, legend bar visible.
- `fetch_fold MKTAYIAKQRQISFVKSHFSRQ...` → ESMFold model `ESM_xxxxxx`, same coloring.
- `color_plddt my_af_model` → recolors any user-loaded prediction.
- No new dependencies; works on bare PyMOL. Network errors surface as one `plog` error, not a traceback.

## Skipped (ponytail)

- GUI dialog — add only if users ask; the command takes a paste directly.
- Caching downloads to disk — PyMOL's own `fetch_path` cache is not used by these APIs; add if re-fetching gets annoying.
- Batch input (multiple accessions) — `fetch_fold` in a loop covers it.
- PAE (predicted aligned error) plots — separate feature, separate plan.
