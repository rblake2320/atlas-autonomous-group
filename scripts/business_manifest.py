from __future__ import annotations

from business_lib import MANIFEST, OWNER_EVIDENCE, now


def build_manifest() -> str:
    files = sorted(p.name for p in OWNER_EVIDENCE.glob("*") if p.is_file())
    lines = ["# Delivery Manifest", "", f"Updated: {now()}", "", "## Delivered"]
    if files:
        lines.extend(f"- {name}" for name in files)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    MANIFEST.write_text(build_manifest(), encoding="utf-8")
    print(MANIFEST)
