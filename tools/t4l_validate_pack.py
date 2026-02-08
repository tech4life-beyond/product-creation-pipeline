#!/usr/bin/env python3
"""Validate Tech4Life Product Pack structure and metadata."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml


PRODUCT_ID_PATTERN = re.compile(r"^T4L-TOIL-\d{3}-[A-Z0-9]+$")
PRODUCT_ID_TOKEN = re.compile(r"T4L-TOIL-[A-Z0-9-]+")
LEGACY_ID_PATTERN = re.compile(r"T4L-20\d{2}-\d{3}")
DATE_TOKEN_PATTERN = re.compile(r"\b\d{1,4}[-/]\d{1,2}[-/]\d{1,4}\b")
VALID_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass
class RuleItem:
    rule_id: str
    description: str
    paths: list[str]


@dataclass
class PackIssue:
    message: str


@dataclass
class PackResult:
    name: str
    path: Path
    issues: list[PackIssue]


def load_rules(rules_path: Path) -> tuple[list[RuleItem], list[RuleItem]]:
    data = yaml.safe_load(rules_path.read_text()) or {}
    required = [
        RuleItem(
            rule_id=item.get("id", ""),
            description=item.get("description", ""),
            paths=item.get("paths", []),
        )
        for item in data.get("required", [])
    ]
    optional = [
        RuleItem(
            rule_id=item.get("id", ""),
            description=item.get("description", ""),
            paths=item.get("paths", []),
        )
        for item in data.get("optional", [])
    ]
    return required, optional


def discover_packs(base_path: Path) -> list[Path]:
    packs: list[Path] = []
    for entry in sorted(base_path.iterdir()):
        if entry.is_dir() and (entry / "README.md").is_file():
            packs.append(entry)
    return packs


def has_match(pack_path: Path, patterns: Iterable[str]) -> bool:
    for pattern in patterns:
        if any(pack_path.glob(pattern)):
            return True
    return False


def extract_product_id(readme_path: Path) -> str | None:
    text = readme_path.read_text(errors="ignore")
    match = PRODUCT_ID_TOKEN.search(text)
    if not match:
        return None
    return match.group(0)


def validate_product_id(product_id: str | None) -> str | None:
    if not product_id:
        return "Missing Product ID (no T4L-TOIL- token found in README)."
    if not PRODUCT_ID_PATTERN.match(product_id):
        return f"Invalid Product ID format: {product_id}"
    return None


def find_invalid_dates(text: str) -> list[str]:
    invalid: list[str] = []
    for token in DATE_TOKEN_PATTERN.findall(text):
        if not VALID_DATE_PATTERN.match(token):
            invalid.append(token)
    return invalid


def validate_dates_in_files(files: Iterable[Path]) -> list[str]:
    issues: list[str] = []
    for file_path in files:
        text = file_path.read_text(errors="ignore")
        invalid = find_invalid_dates(text)
        if invalid:
            issues.append(
                f"Invalid date format in {file_path}: {', '.join(sorted(set(invalid)))}"
            )
    return issues


def legacy_id_issues(files: Iterable[Path]) -> list[str]:
    issues: list[str] = []
    for file_path in files:
        for line_number, line in enumerate(
            file_path.read_text(errors="ignore").splitlines(), start=1
        ):
            if LEGACY_ID_PATTERN.search(line):
                lowered = line.lower()
                if "legacy id" not in lowered and "legacy ids" not in lowered:
                    issues.append(
                        f"Legacy ID detected in {file_path}:{line_number} -> {line.strip()}"
                    )
    return issues


def validate_pack(pack_path: Path, required_rules: list[RuleItem]) -> PackResult:
    issues: list[PackIssue] = []

    for rule in required_rules:
        if not has_match(pack_path, rule.paths):
            description = rule.description or rule.rule_id
            issues.append(PackIssue(f"Missing required item: {description}"))

    readme_path = pack_path / "README.md"
    product_id = extract_product_id(readme_path)
    product_id_issue = validate_product_id(product_id)
    if product_id_issue:
        issues.append(PackIssue(product_id_issue))

    date_targets: list[Path] = []
    for directory in (pack_path / "01-toil-registration", pack_path / "06-product-release"):
        if directory.exists():
            date_targets.extend(directory.rglob("*.md"))
    for issue in validate_dates_in_files(date_targets):
        issues.append(PackIssue(issue))

    all_docs = list(pack_path.rglob("*.md"))
    for issue in legacy_id_issues(all_docs):
        issues.append(PackIssue(issue))

    return PackResult(name=pack_path.name, path=pack_path, issues=issues)


def parse_args() -> argparse.Namespace:
    default_path = (Path(__file__).resolve().parent.parent / ".." / "products").resolve()
    default_rules = Path(__file__).resolve().parent.parent / "rules" / "product_pack_rules.yml"
    parser = argparse.ArgumentParser(description="Validate Tech4Life Product Packs.")
    parser.add_argument(
        "path",
        nargs="?",
        default=default_path,
        type=Path,
        help="Path to Product Packs directory (default: ../products)",
    )
    parser.add_argument(
        "--rules",
        type=Path,
        default=default_rules,
        help="Path to product pack rules YAML.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    base_path: Path = args.path
    rules_path: Path = args.rules

    if not rules_path.is_file():
        print(f"Rules file not found: {rules_path}")
        return 2

    if not base_path.exists():
        print(f"Pack root not found: {base_path}")
        return 2

    required_rules, _ = load_rules(rules_path)
    packs = discover_packs(base_path)

    if not packs:
        print(f"No product packs found in {base_path}")
        return 0

    results = [validate_pack(pack_path, required_rules) for pack_path in packs]
    total_issues = sum(len(result.issues) for result in results)

    print("Product Pack Validation Report")
    print("=" * 32)
    for result in results:
        print(f"\nPack: {result.name}")
        if result.issues:
            for issue in result.issues:
                print(f"  - {issue.message}")
        else:
            print("  - OK")

    print("\nSummary")
    print("=" * 7)
    print(f"Packs checked: {len(results)}")
    print(f"Issues found: {total_issues}")

    return 1 if total_issues else 0


if __name__ == "__main__":
    sys.exit(main())
