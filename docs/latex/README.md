# LaTeX sources

Store LaTeX source files for the research plan, papers, and generated academic artifacts in this directory.

## Requirements

The project expects a LaTeX distribution with `latexmk` and `pdflatex`. The current development environment provides them through MiKTeX.

## Build a document

From the repository root, compile a source file such as `docs/latex/plan.tex` with:

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=docs/latex/build docs/latex/plan.tex
```

The generated PDF and auxiliary files are written to `docs/latex/build/`. Replace `plan.tex` with the source file you want to compile.

`latexmk` automatically runs LaTeX the required number of times. It also runs BibTeX when it detects a traditional bibliography.

## Use Biber with `biblatex`

For documents that use `biblatex` and `biber`, run:

```powershell
latexmk -pdf -use-biber -interaction=nonstopmode -halt-on-error -outdir=docs/latex/build docs/latex/plan.tex
```

## Alternative manual build

If `latexmk` is unavailable, run `pdflatex` manually from the `docs/latex/` directory:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error plan.tex
bibtex plan
pdflatex -interaction=nonstopmode -halt-on-error plan.tex
pdflatex -interaction=nonstopmode -halt-on-error plan.tex
```

Use `biber plan` instead of `bibtex plan` when the document uses `biblatex`.

## Clean generated files

Remove auxiliary LaTeX files while keeping the PDF:

```powershell
latexmk -c -outdir=docs/latex/build docs/latex/plan.tex
```

Use `latexmk -C` only when you also want to remove the generated PDF.
