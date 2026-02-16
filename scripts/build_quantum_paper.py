#!/usr/bin/env python3
"""Build the quantum paper and HAL/arXiv artifacts."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    paper_dir = repo_root / "paper"
    tex_path = paper_dir / "main.tex"
    out_dir = paper_dir / "build"

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Refresh paper assets (figures/tables) using existing pipeline.
    subprocess.run(["make", "paper-assets"], check=True, cwd=repo_root)

    latexmk = shutil.which("latexmk")
    pdflatex = shutil.which("pdflatex")

    if latexmk:
        cmd = [
            latexmk,
            "-pdf",
            "-g",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-outdir={out_dir}",
            tex_path.name,
        ]
        subprocess.run(cmd, check=True, cwd=paper_dir)
    elif pdflatex:
        cmd = [
            pdflatex,
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={out_dir}",
            tex_path.name,
        ]
        subprocess.run(cmd, check=True, cwd=paper_dir)
        subprocess.run([shutil.which("bibtex") or "bibtex", str(out_dir / "main")], check=True, cwd=paper_dir)
        subprocess.run(cmd, check=True, cwd=paper_dir)
        subprocess.run(cmd, check=True, cwd=paper_dir)
    else:
        raise SystemExit("Missing LaTeX tools: latexmk or pdflatex is required.")

    pdf_path = out_dir / "main.pdf"
    if not pdf_path.exists():
        raise SystemExit(f"Build failed: {pdf_path} not found")

    tex = tex_path.read_text()

    def _extract(pattern: str, name: str) -> str:
        m = re.search(pattern, tex, re.S)
        if not m:
            raise SystemExit(f"[build_quantum_paper] ERROR: could not extract {name} from main.tex")
        return m.group(1).strip()

    title = _extract(r"\\title\{(.*?)\}", "title")
    abstract = _extract(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", "abstract")
    if "\n" in abstract or "\r" in abstract:
        raise SystemExit("[build_quantum_paper] ERROR: abstract must be a single paragraph with no line breaks")

    kw_match = re.search(r"\\textbf\{keywords:\}\s*([^\n]+)", tex, re.IGNORECASE)
    if not kw_match:
        raise SystemExit("[build_quantum_paper] ERROR: could not extract keywords line from main.tex")
    keywords_line = kw_match.group(1).strip()
    keywords = [k.strip() for k in keywords_line.split(";") if k.strip()]
    if any(k != k.lower() for k in keywords):
        raise SystemExit("[build_quantum_paper] ERROR: keywords must be lowercase and semicolon-separated")

    author_block = {
        "first_name": "Ioannis",
        "last_name": "Tsiokos",
        "email": "ioannis@automorph.io",
        "orcid": "0009-0009-7659-5964",
        "affiliation": "Automorph Inc., 1207 Delaware Ave #4131, Wilmington, DE 19806, USA",
        "corresponding": True,
    }

    meta = {
        "hal_metadata": {
            "title": title,
            "abstract": abstract,
            "keywords": keywords,
            "language": "en",
            "domain": "quant-ph",
            "license": "CC-BY 4.0",
            "authors": [
                {
                    **author_block,
                    "affiliation_structure": {
                        "name": "Automorph Inc.",
                        "type": "Entreprise",
                        "address": "1207 Delaware Ave #4131, Wilmington, DE 19806",
                        "country": "US",
                    },
                    "role": "author",
                }
            ],
        },
        "researchsquare_metadata": {
            "title": title,
            "abstract": abstract,
            "article_type": "Research Article",
            "subject_areas": [
                "Quantum Physics",
                "Theoretical Physics",
                "Computational Physics",
            ],
            "keywords": keywords,
            "license": "CC-BY 4.0",
            "authors": [author_block],
            "declarations": {
                "competing_interests": "No competing interests declared",
                "funding": "No external funding received",
                "ethics": "Not applicable",
                "data_availability": (
                    "All experimental data are generated deterministically by the included "
                    "Python code with fixed random seeds. No external datasets are required."
                ),
                "code_availability": (
                    "Full source code at https://github.com/ioannist/six-birds-quantum, "
                    "archived on Zenodo (DOI: 10.5281/zenodo.18608833). "
                    "Lean 4 mechanized proofs are included in the lean/ directory."
                ),
                "ai_disclosure": (
                    "Portions of code and manuscript text were drafted with the assistance "
                    "of ChatGPT and Claude Code. All scientific content, experimental design, "
                    "and formal proofs were reviewed, validated, and are the sole responsibility "
                    "of the author."
                ),
            },
        },
    }
    meta_path = out_dir / "metadata.json"
    meta_path.write_text(json.dumps(meta, indent=2))

    short = title.split(":", 1)[0].strip()
    short = re.sub(r"[^A-Za-z0-9]+", "_", short).strip("_")
    hal_pdf_name = f"2026_Tsiokos_{short}_v1.pdf"
    hal_pdf_path = out_dir / hal_pdf_name
    shutil.copy2(pdf_path, hal_pdf_path)

    if shutil.which("pdfinfo"):
        info = subprocess.check_output(["pdfinfo", str(pdf_path)], text=True, errors="ignore")
        m = re.search(r"PDF version:\s*([0-9.]+)", info)
        if m:
            try:
                if float(m.group(1)) < 1.4:
                    raise SystemExit("[build_quantum_paper] ERROR: PDF version is < 1.4.")
            except ValueError:
                pass
        if re.search(r"Encrypted:\s*yes", info, re.IGNORECASE):
            raise SystemExit("[build_quantum_paper] ERROR: PDF is encrypted.")

    size = pdf_path.stat().st_size
    if size > 50 * 1024 * 1024:
        raise SystemExit("[build_quantum_paper] ERROR: PDF exceeds 50MB size limit.")

    if shutil.which("pdffonts"):
        out = subprocess.check_output(["pdffonts", str(pdf_path)], text=True)
        lines = out.strip().splitlines()[2:]
        type3 = []
        not_embedded = []
        for line in lines:
            parts = line.split()
            if len(parts) < 5:
                continue
            if parts[1] == "Type" and len(parts) >= 5:
                ftype = f"{parts[1]} {parts[2]}"
                emb = parts[4]
            else:
                ftype = parts[1]
                emb = parts[3]
            if ftype == "Type 3":
                type3.append(line)
            if emb == "no":
                not_embedded.append(line)
        if not_embedded:
            raise SystemExit("[build_quantum_paper] ERROR: non-embedded fonts detected.")
        if type3:
            raise SystemExit("[build_quantum_paper] ERROR: Type 3 fonts detected.")

    if shutil.which("pdftotext"):
        text = subprocess.check_output(["pdftotext", str(pdf_path), "-"], text=True, errors="ignore")
        if re.search(r"(confidential|draft|do not distribute)", text, re.IGNORECASE):
            raise SystemExit("[build_quantum_paper] ERROR: draft/confidential watermark text detected.")
        page1 = subprocess.check_output(
            ["pdftotext", "-f", "1", "-l", "1", str(pdf_path), "-"],
            text=True,
            errors="ignore",
        )
        if "Automorph Inc." not in page1:
            raise SystemExit("[build_quantum_paper] ERROR: affiliation 'Automorph Inc.' not found on page 1.")

    # Build HAL source zip.
    subprocess.run([str(repo_root / "scripts" / "make_hal_source_zip.sh")], check=True)
    hal_zip = out_dir / "hal_source_upload.zip"
    if hal_zip.exists():
        hal_named = out_dir / f"2026_Tsiokos_{short}_v1_hal_source.zip"
        shutil.copy2(hal_zip, hal_named)

    # Build arXiv source zip.
    subprocess.run([str(repo_root / "scripts" / "package_arxiv.sh")], check=True)
    arxiv_zip = out_dir / "arxiv_source_upload.zip"
    if arxiv_zip.exists():
        arxiv_named = out_dir / f"2026_Tsiokos_{short}_v1_arxiv_source.zip"
        shutil.copy2(arxiv_zip, arxiv_named)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
