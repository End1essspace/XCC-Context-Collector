from pathlib import Path

from src.xcc.ignore import ProjectIgnoreMatcher, load_ignore_rules, parse_ignore_rule


def test_parses_comments_negation_and_root_anchoring() -> None:
    assert parse_ignore_rule("") is None
    assert parse_ignore_rule("# comment") is None

    negated = parse_ignore_rule("!generated/keep.py")
    anchored = parse_ignore_rule("/root-only.txt")

    assert negated is not None and negated.negated is True
    assert anchored is not None and anchored.anchored is True


def test_matcher_supports_globs_directory_rules_and_negation() -> None:
    rules = [
        parse_ignore_rule("generated/**"),
        parse_ignore_rule("!generated/keep.py"),
        parse_ignore_rule("*.log"),
        parse_ignore_rule("cache/"),
    ]
    matcher = ProjectIgnoreMatcher([rule for rule in rules if rule is not None])

    assert matcher.is_ignored("generated/output.py") is True
    assert matcher.is_ignored("generated/keep.py") is False
    assert matcher.is_ignored("logs/app.log") is True
    assert matcher.is_ignored("cache/data.json") is True
    assert matcher.is_ignored("cache", is_dir=True) is True
    assert matcher.is_ignored("cache", is_dir=False) is False


def test_xccignore_rules_override_matching_gitignore_rules(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("generated/**\n", encoding="utf-8")
    (tmp_path / ".xccignore").write_text(
        "!generated/keep.py\nprivate/**\n",
        encoding="utf-8",
    )

    matcher = ProjectIgnoreMatcher.from_project_root(tmp_path)

    assert matcher.is_ignored("generated/drop.py") is True
    assert matcher.is_ignored("generated/keep.py") is False
    assert matcher.is_ignored("private/credentials.json") is True


def test_load_ignore_rules_tolerates_missing_file(tmp_path: Path) -> None:
    assert load_ignore_rules(tmp_path / "missing") == []


def test_rules_use_windows_case_insensitive_matching() -> None:
    rule = parse_ignore_rule("Private/**")
    assert rule is not None

    matcher = ProjectIgnoreMatcher([rule])

    assert matcher.is_ignored("private/credentials.json") is True
