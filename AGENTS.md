# AGENTS.md for rtcc

@../../py/CLAUDE.md

Random triangles on concentric circles: the probability that three points, one
uniform on each of three concentric circles of radii `r1`, `r2`, `r3`, form an
obtuse triangle. `src/rtcc` is the reference implementation and CLI;
`paper/paper.qmd` is the preprint.

**Tech stack:** Python >= 3.11, uv, ruff, pytest, NumPy, SciPy, matplotlib,
Quarto, LaTeX.

## Layout

```
src/rtcc/obtuse.py   # exact probabilities (quadrature) and Monte Carlo
src/rtcc/cli.py      # `rtcc R1 R2 R3 [--simulate N]`
tests/               # closed-form checks and simulation agreement
paper/paper.qmd      # preprint, full proofs (Quarto, jupyter engine)
paper/short/         # second write-up, untracked; see below
```

There are two write-ups, deliberately different articles rather than long and
short cuts of one. `paper/paper.qmd` carries the proofs. The second is a shorter
narrative version built in a journal's own LaTeX template, so it is plain LaTeX
with figures generated separately by `paper/short/figures.py`. Numbers quoted
in the LaTeX version are hard-coded and come from `rtcc`; if the implementation
ever changes, re-check them.

## Commands

```bash
uv sync
uv run ruff check . && uv run pytest   # quality gate
uv run rtcc 1 2 3 --simulate 1000000
uv run quarto render paper/paper.qmd

cd paper/short                         # second write-up, if present
uv run python figures.py               # regenerate fig1/fig2 (PDF + EPS)
pdflatex random-triangles && bibtex random-triangles && pdflatex random-triangles
```

## arXiv submission

`paper/arxiv-submission.tar.gz` is the upload bundle, gitignored and
regenerable: `paper.tex` plus `arxiv.sty`, `orcidlink.sty`, and the figure PDFs
under `paper_files/figure-pdf/`. Rebuild it after any render that adds or
renames a figure, and diff the file list against what `paper.tex` actually
includes. An earlier bundle silently shipped four of the five figures because it
predated one of them, which would have failed the build on arXiv rather than
locally.

```bash
uv run quarto render paper/paper.qmd            # refreshes paper.tex
cd paper && COPYFILE_DISABLE=1 tar czf arxiv-submission.tar.gz \
  paper.tex arxiv.sty orcidlink.sty paper_files/figure-pdf/*.pdf
```

Test it by unpacking into an empty directory and compiling there, not in
`paper/`, so a missing file cannot be masked by one already sitting next to it.
It compiles under both `pdflatex` and `lualatex`. Quarto inlines the references
as a `CSLReferences` block, so no `.bib` ships and arXiv never runs BibTeX.

Form metadata: primary `math.PR`, with `math.HO` and `math.MG` as plausible
cross-lists; MSC codes are printed in the paper itself. The abstract is about
1300 characters against a 1920 limit and pastes in unmodified, light TeX
included.

A first submission may need an endorsement for the primary category, though an
institutional address often carries one automatically; check before going
looking for an endorser, and do not request a code until one is lined up, since
codes expire. Endorsement certifies that the submitter is a legitimate
researcher, not that the work is correct.

## Notes

- **`paper/short/` is untracked on purpose.** It is under anonymous review,
  and this repository is public under the author's name, so committing the
  blinded manuscript would identify its author. It is gitignored as a directory;
  a fresh clone will not have it and the second build above will not run. Remove
  the `.gitignore` entry once the review concludes. Do not commit it before
  then, and keep venue names out of tracked files until then as well.
- The directory is called `short` rather than anything venue-specific because
  `.gitignore` has to name it in a tracked file. A referee reading the public
  repository worked the venue out from a code comment in `paper.qmd` that named
  the old path; that route is closed and should stay closed. When referring to
  the second write-up in a tracked file, call it the companion write-up.
- **The second write-up produces two PDFs from one source.** The journal asks for
  a manuscript with author details and an anonymous one. Do not keep two copies;
  identifying material is guarded by `\ifshowauthor` and selected at build time:

  ```bash
  cd paper/short
  pdflatex -jobname=random-triangles-anon random-triangles
  bibtex   random-triangles-anon
  pdflatex -jobname=random-triangles-author "\def\showauthor{}\input{random-triangles}"
  bibtex   random-triangles-author
  ```

  Run each to convergence and run `bibtex` on each jobname; the two builds cite
  different versions of the companion-preprint entry (`preprint` withholds the
  author, `preprintnamed` does not), so they need separate `.aux` files.

  Guarded by the flag: author block, acknowledgment of the author's advisor,
  repository URL, and the choice of preprint citation. The biography block is
  guarded too but still commented, because it has no text yet.

  After any edit, confirm the split still holds. The anonymous build must
  contain none of `Greenwell`, `Cincinnati`, `ucmail`, `Harry Khamis`,
  `github.com`; the author build must contain all of them and must not contain
  `Author withheld`.

  The `arXiv:XXXX.XXXXX` placeholder is in both and stays until the identifier
  exists. The two Khamis citations are live in both write-ups: citing published
  work is not self-identifying, and only naming the man as an advisor would be.
  In particular, posting the preprint supplies a real identifier and with it the
  temptation to fill that placeholder in. Do not: the citation would lead a
  referee to a preprint carrying the author's name. The identifier goes in with
  the other three restorations, not before.
- Both write-ups import `rtcc`, the Quarto chunks in `paper.qmd` and
  `figures.py`, so both build only inside the project environment (`uv run`).
- The LaTeX build must run from `paper/short/`: it resolves its style file and
  `fig1`/`fig2` relative to the working directory. That directory carries its own
  copies of the journal's class, theorem, and bibliography style files, which
  should not be edited. Their filenames name the venue, which is why they stay
  inside the untracked directory and are not listed here.
- `pdflatex` prints `(\end occurred inside a group at level 1)` on every build.
  It comes from an unclosed `flushright` in the journal's style file, is present
  in their own shipped template log, and does not affect output. Leave it.
- BibTeX scans `.bib` files for entry markers regardless of leading percent
  signs, so a commented-out spare entry is read as a duplicate. Do not park one
  in `references.bib`.
- Radii are unitless: only their ratios matter, so `rtcc 1 2 3` and
  `rtcc 2 4 6` agree.
- `p_vertex` returns zero to quadrature precision, not exactly zero, when
  `rk**2 >= ri**2 + rj**2`. Tests compare against a tolerance.
- **Both write-ups carry a generative-AI disclosure**, naming `claude-opus-5`
  and `gpt-5.6-sol` with what each was used for. It sits before the references
  in the preprint and before the bibliography in the second write-up, and it is
  deliberately *not* guarded by `\ifshowauthor`: it identifies nobody and
  referees should see it.

  The disclosure is a statement of research integrity, so it has to keep pace
  with what actually happens. If the division of labour changes, update the
  wording to match rather than leaving it stale, and do not narrow it to sound
  better than the record supports. The repository is the record.
