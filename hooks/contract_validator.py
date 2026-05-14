"""
hooks/contract_validator.py

Pre-analysis hook — runs before /analyze-contract begins.
Validates the input file is readable and meets minimum content requirements.
Fails fast with a clear error rather than letting the pipeline run on garbage input.
"""

import sys
import os


def validate_contract(contract_path: str) -> bool:
    if not os.path.exists(contract_path):
        print(f"[validator] ERROR: File not found — {contract_path}", file=sys.stderr)
        return False

    size_bytes = os.path.getsize(contract_path)
    if size_bytes < 1000:
        print(f"[validator] ERROR: File too small ({size_bytes} bytes) — likely not a real contract.", file=sys.stderr)
        return False

    if size_bytes > 50_000_000:
        print(f"[validator] ERROR: File too large ({size_bytes / 1e6:.1f} MB) — split document before analysis.", file=sys.stderr)
        return False

    ext = os.path.splitext(contract_path)[1].lower()
    if ext not in [".pdf", ".txt", ".docx"]:
        print(f"[validator] ERROR: Unsupported file type '{ext}'. Supported: .pdf, .txt, .docx", file=sys.stderr)
        return False

    print(f"[validator] ✓ Contract validated — {contract_path} ({size_bytes / 1024:.1f} KB)", file=sys.stderr)
    return True


if __name__ == "__main__":
    contract_path = sys.argv[1] if len(sys.argv) > 1 else ""
    if not validate_contract(contract_path):
        sys.exit(1)
