"""Fail publishing if internal Keeper working documents enter the public repository."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ALLOWED_DOCS = {"CANON_PUBLIC_RELEASE_LOG.md"}
if DOCS.exists():
    found = {p.name for p in DOCS.iterdir()}
    assert found <= ALLOWED_DOCS, (
        "Unexpected documents in public repository: " + ", ".join(sorted(found - ALLOWED_DOCS))
    )
for dirname in ("keeper", "private", "dm-notes", "master-canon"):
    assert not (ROOT / dirname).exists(), "Private materials directory in public source: " + dirname
for pdf in ROOT.rglob("*.pdf"):
    if pdf.is_relative_to(ROOT / "_site"):
        continue
    raise AssertionError("PDF source requires explicit publication review: " + str(pdf.relative_to(ROOT)))
print("Public source boundary: no private documentation or Keeper PDF sources included.")
