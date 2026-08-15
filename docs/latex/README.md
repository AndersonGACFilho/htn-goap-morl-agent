# LaTeX sources

Store LaTeX source files for the research plan, papers, and generated academic artifacts in this directory.

## Requirements

The project expects a LaTeX distribution with `latexmk` and `pdflatex`. The current development environment provides them through MiKTeX.

## Build a document

From the repository root, compile the research-plan source with:

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=docs/latex/build docs/latex/main.tex
```

The generated PDF and auxiliary files are written to `docs/latex/build/`. Replace `main.tex` with the source file you want to compile.

If the current directory is already `docs/latex/`, use relative paths instead:

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

`latexmk` automatically runs LaTeX the required number of times. It also runs BibTeX when it detects a traditional bibliography.

## Use Biber with `biblatex`

For documents that use `biblatex` and `biber`, run:

```powershell
latexmk -pdf -use-biber -interaction=nonstopmode -halt-on-error -outdir=docs/latex/build docs/latex/main.tex
```

## Alternative manual build

If `latexmk` is unavailable, run `pdflatex` manually from the `docs/latex/` directory:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Use `biber main` instead of `bibtex main` when the document uses `biblatex`.

## Clean generated files

Remove auxiliary LaTeX files while keeping the PDF:

```powershell
latexmk -c -outdir=docs/latex/build docs/latex/main.tex
```

Use `latexmk -C` only when you also want to remove the generated PDF.
