from pathlib import Path

from cbi.cli import ASSET_SCHEMAS, load_yaml, repo_root, validate_node


def test_example_assets_validate() -> None:
    root = repo_root()
    examples = {
        "task": root / "templates" / "analysis-task.yaml",
        "skill": root / "skills" / "market-opportunity-analysis.yaml",
        "metric": root / "metrics" / "market-opportunity-score.yaml",
        "evaluation": root / "evaluation" / "source-and-logic-review.yaml",
    }
    for kind, path in examples.items():
        schema = load_yaml(root / ASSET_SCHEMAS[kind])
        data = load_yaml(Path(path))
        assert validate_node(data, schema) == []
