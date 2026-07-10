from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import yaml


ASSET_SCHEMAS = {
    "task": Path("schemas/analysis-task.schema.yaml"),
    "skill": Path("skills/schemas/analysis-skill.schema.yaml"),
    "metric": Path("metrics/schemas/metric.schema.yaml"),
    "evaluation": Path("evaluation/schemas/evaluation.schema.yaml"),
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML object at the root")
    return data


def write_yaml(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=False)


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "analysis-task"


def split_csv(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def init_workspace(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    dirs = [
        "docs",
        "projects",
        "knowledge",
        "skills",
        "skills/schemas",
        "metrics",
        "metrics/schemas",
        "evaluation",
        "evaluation/schemas",
        "templates",
        "schemas",
        "tools",
    ]
    for item in dirs:
        (root / item).mkdir(parents=True, exist_ok=True)
    print(f"Initialized workspace directories under {root}")
    return 0


def new_task(args: argparse.Namespace) -> int:
    root = repo_root()
    template_path = root / "templates" / "analysis-task.yaml"
    task = load_yaml(template_path)

    markets = split_csv(args.markets)
    hs_codes = split_csv(args.hs_codes) if args.hs_codes else []
    title = args.title or f"{args.product} export opportunity scan"
    today = dt.date.today().isoformat()
    slug = args.slug or f"{today}-{slugify(args.product)}-{slugify(markets[0] if markets else 'market')}"

    task["task_id"] = f"task-{slug}"
    task["title"] = title
    task["decision_question"] = args.question or task["decision_question"]
    task["subject"]["product"] = args.product
    task["subject"]["supply_chain"] = args.supply_chain
    task["subject"]["target_markets"] = markets
    if args.industry_cluster:
        task["subject"]["industry_cluster"] = args.industry_cluster
    if hs_codes:
        task["subject"]["hs_codes"] = hs_codes
    task["business_context"]["user_type"] = args.user_type
    task["business_context"]["objective"] = args.objective

    project_dir = root / "projects" / slug
    output_path = project_dir / "task.yaml"
    if output_path.exists() and not args.force:
        print(f"Refusing to overwrite existing task: {output_path}", file=sys.stderr)
        print("Use --force to overwrite.", file=sys.stderr)
        return 2

    write_yaml(output_path, task)
    for subdir in ["analysis", "report", "review", "extracted-assets"]:
        (project_dir / subdir).mkdir(parents=True, exist_ok=True)
    print(output_path)
    return 0


def expected_type_name(schema_type: str) -> Tuple[type, ...]:
    mapping = {
        "object": (dict,),
        "array": (list,),
        "string": (str,),
        "boolean": (bool,),
        "number": (int, float),
        "integer": (int,),
    }
    return mapping.get(schema_type, (object,))


def validate_node(data: Any, schema: Dict[str, Any], path: str = "$") -> List[str]:
    errors: List[str] = []
    schema_type = schema.get("type")
    if schema_type:
        expected = expected_type_name(schema_type)
        if not isinstance(data, expected) or (schema_type == "number" and isinstance(data, bool)):
            errors.append(f"{path}: expected {schema_type}, got {type(data).__name__}")
            return errors

    if schema_type == "object":
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        for key in required:
            if key not in data:
                errors.append(f"{path}: missing required key '{key}'")
        if schema.get("additionalProperties") is False:
            for key in data:
                if key not in properties:
                    errors.append(f"{path}: unexpected key '{key}'")
        for key, child_schema in properties.items():
            if key in data:
                errors.extend(validate_node(data[key], child_schema, f"{path}.{key}"))

    if schema_type == "array":
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(data):
                errors.extend(validate_node(item, item_schema, f"{path}[{index}]"))

    return errors


def validate_asset(args: argparse.Namespace) -> int:
    root = repo_root()
    asset_path = Path(args.path)
    if not asset_path.is_absolute():
        asset_path = root / asset_path

    if args.schema:
        schema_path = Path(args.schema)
        if not schema_path.is_absolute():
            schema_path = root / schema_path
    else:
        schema_path = root / ASSET_SCHEMAS[args.kind]

    data = load_yaml(asset_path)
    schema = load_yaml(schema_path)
    errors = validate_node(data, schema)
    if errors:
        print(f"{asset_path} failed validation against {schema_path}:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"{asset_path} is valid against {schema_path}")
    return 0


def iter_assets(root: Path, patterns: Iterable[str]) -> Iterable[Path]:
    for pattern in patterns:
        yield from sorted(root.glob(pattern))


def list_assets(args: argparse.Namespace) -> int:
    root = repo_root()
    patterns = {
        "task": ["projects/*/task.yaml", "templates/analysis-task.yaml"],
        "skill": ["skills/*.yaml"],
        "metric": ["metrics/*.yaml"],
        "evaluation": ["evaluation/*.yaml"],
    }
    selected = [args.kind] if args.kind != "all" else ["task", "skill", "metric", "evaluation"]
    for kind in selected:
        print(f"{kind}:")
        for path in iter_assets(root, patterns[kind]):
            print(f"  - {path.relative_to(root)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cbi",
        description="Analysis Workspace CLI for cross-border decision intelligence.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create standard workspace directories.")
    init_parser.add_argument("--root", default=".", help="Workspace root to initialize.")
    init_parser.set_defaults(func=init_workspace)

    task_parser = subparsers.add_parser("new-task", help="Create a project task from the analysis template.")
    task_parser.add_argument("--product", required=True, help="Product category to analyze.")
    task_parser.add_argument("--supply-chain", required=True, help="Origin supply chain or industry cluster.")
    task_parser.add_argument("--markets", required=True, help="Comma-separated target markets.")
    task_parser.add_argument("--title", help="Task title.")
    task_parser.add_argument("--question", help="Decision question.")
    task_parser.add_argument("--industry-cluster", help="Industry cluster description.")
    task_parser.add_argument("--hs-codes", default="", help="Comma-separated HS code assumptions.")
    task_parser.add_argument("--user-type", default="factory or export company", help="Primary user type.")
    task_parser.add_argument("--objective", default="Find export markets worth testing in the next 3-6 months.")
    task_parser.add_argument("--slug", help="Project folder slug.")
    task_parser.add_argument("--force", action="store_true", help="Overwrite an existing task.yaml.")
    task_parser.set_defaults(func=new_task)

    validate_parser = subparsers.add_parser("validate", help="Validate a YAML asset with a workspace schema.")
    validate_parser.add_argument("path", help="Path to the YAML asset.")
    validate_parser.add_argument("--kind", choices=sorted(ASSET_SCHEMAS), default="task")
    validate_parser.add_argument("--schema", help="Optional explicit schema path.")
    validate_parser.set_defaults(func=validate_asset)

    list_parser = subparsers.add_parser("list", help="List workspace assets.")
    list_parser.add_argument("--kind", choices=["all", "task", "skill", "metric", "evaluation"], default="all")
    list_parser.set_defaults(func=list_assets)

    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
