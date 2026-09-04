#!/usr/bin/env python3
"""Generate the composed USD furniture layout from furniture.json."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORLD_DIR = ROOT / "worlds/cbnu_haksan_1f_corridor"
DEFAULT_CONFIG = WORLD_DIR / "config/furniture.json"
DEFAULT_GEOMETRY = WORLD_DIR / "config/geometry.json"
DEFAULT_OUTPUT = WORLD_DIR / "config/furniture_layout.usda"
ASSET_REFERENCES = {
    "straight": "../../../assets/furniture/sofa_straight.usda",
    "corner": "../../../assets/furniture/sofa_corner.usda",
    "single": "../../../assets/furniture/sofa_single.usda",
    "u_column": "../../../assets/furniture/sofa_u_around_2m_column.usda",
    "atm": "../../../assets/equipment/atm_machine.usda",
    "lobby_table": "../../../assets/furniture/lobby_table.usda",
    "lobby_table_filled": "../../../assets/furniture/lobby_table_filled.usda",
}
PLACEMENTS = {"column_attached", "wall_attached", "freestanding"}
FACINGS = {"lobby", "outward", "not_applicable"}
SOFA_MATERIAL_VARIANTS = {"brown_leather", "dark_reddish_brown_leather"}
USD_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def usd_number(value: float) -> str:
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return "0" if text in {"", "-0"} else text


def validate_number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


def load_layout(config_path: Path, geometry_path: Path) -> tuple[list[dict[str, object]], dict[str, list[float]]]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
    sofas = config.get("sofas") if isinstance(config, dict) else None
    fixtures = config.get("fixtures", []) if isinstance(config, dict) else None
    if not isinstance(sofas, list) or not sofas:
        raise ValueError("furniture.json must contain a non-empty sofas array")
    if not isinstance(fixtures, list):
        raise ValueError("furniture.json fixtures must be an array")
    items = [*sofas, *fixtures]

    columns = {item["name"]: item["center"] for item in geometry["columns"]}
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"furniture entry {index} must be an object")
        name = item.get("name")
        item_type = item.get("type")
        if not isinstance(name, str) or not USD_NAME.fullmatch(name):
            raise ValueError(f"furniture entry {index} has an invalid USD prim name")
        if name in seen:
            raise ValueError(f"duplicate sofa name: {name}")
        seen.add(name)
        if item_type not in ASSET_REFERENCES:
            raise ValueError(f"{name} has unsupported type: {item_type}")
        if item.get("placement") not in PLACEMENTS:
            raise ValueError(
                f"{name}.placement must be one of: {', '.join(sorted(PLACEMENTS))}"
            )
        if item.get("facing") not in FACINGS:
            raise ValueError(
                f"{name}.facing must be one of: {', '.join(sorted(FACINGS))}"
            )
        if item_type in {"straight", "corner", "single", "u_column"}:
            material_variant = item.get("material_variant")
            if material_variant not in SOFA_MATERIAL_VARIANTS:
                raise ValueError(
                    f"{name}.material_variant must be one of: "
                    f"{', '.join(sorted(SOFA_MATERIAL_VARIANTS))}"
                )

        if item_type == "u_column":
            column = item.get("column")
            if column not in columns:
                raise ValueError(f"{name} references unknown column: {column}")
            continue

        position = item.get("position")
        if not isinstance(position, list) or len(position) != 3:
            raise ValueError(f"{name}.position must be [x, y, z]")
        for axis, value in zip("xyz", position):
            validate_number(value, f"{name}.position.{axis}")
        validate_number(item.get("yaw_deg"), f"{name}.yaw_deg")
        if item_type in {"straight", "lobby_table", "lobby_table_filled"} and validate_number(
            item.get("length_scale"), f"{name}.length_scale"
        ) <= 0:
            raise ValueError(f"{name}.length_scale must be positive")
        if item_type in {"lobby_table", "lobby_table_filled"} and validate_number(
            item.get("depth_scale", 1.0), f"{name}.depth_scale"
        ) <= 0:
            raise ValueError(f"{name}.depth_scale must be positive")

    return items, columns


def render_layout(items: list[dict[str, object]], columns: dict[str, list[float]]) -> str:
    lines = [
        "#usda 1.0",
        "(",
        '    defaultPrim = "Furniture"',
        "    metersPerUnit = 1",
        '    upAxis = "Z"',
        ")",
        "",
        'def Xform "Furniture"',
        "{",
        '    custom string cbnu:sourceConfig = "furniture.json"',
    ]

    for item in items:
        name = str(item["name"])
        item_type = str(item["type"])
        reference = ASSET_REFERENCES[item_type]
        if item_type == "u_column":
            x, y = (float(value) for value in columns[str(item["column"])])
            z, yaw_deg = 0.0, 0.0
        else:
            x, y, z = (float(value) for value in item["position"])
            yaw_deg = float(item["yaw_deg"])

        lines.extend(
            [
                "",
                f'    def Xform "{name}" (',
                f"        prepend references = @{reference}@",
                "    )",
                "    {",
                '        custom string cbnu:placementSource = "furniture.json"',
                f'        custom string cbnu:placement = "{item["placement"]}"',
                f'        custom string cbnu:facing = "{item["facing"]}"',
                f'        custom string cbnu:itemType = "{item_type}"',
                f"        double xformOp:rotateZ = {usd_number(yaw_deg)}",
            ]
        )
        if item_type == "atm":
            lines.insert(-1, '        custom string cbnu:semanticClass = "bank_atm"')
        elif item_type in {"lobby_table", "lobby_table_filled"}:
            lines.insert(-1, '        custom string cbnu:semanticClass = "lobby_table"')
        elif item_type != "u_column":
            lines.insert(-1, f'        custom string cbnu:sofaType = "{item_type}"')
        else:
            lines.insert(-1, '        custom string cbnu:sofaType = "u_column"')
        if item_type in {"straight", "corner", "single", "u_column"}:
            lines.insert(-1, f'        custom string cbnu:materialVariant = "{item["material_variant"]}"')
        if item_type in {"straight", "lobby_table", "lobby_table_filled"}:
            depth_scale = float(item.get("depth_scale", 1.0))
            lines.append(
                f"        double3 xformOp:scale = ({usd_number(float(item['length_scale']))}, "
                f"{usd_number(depth_scale)}, 1)"
            )
        lines.append(
            "        double3 xformOp:translate = "
            f"({usd_number(x)}, {usd_number(y)}, {usd_number(z)})"
        )
        order = ["xformOp:translate", "xformOp:rotateZ"]
        if item_type in {"straight", "lobby_table", "lobby_table_filled"}:
            order.append("xformOp:scale")
        lines.extend(
            [
                '        uniform token[] xformOpOrder = [' + ", ".join(f'"{item}"' for item in order) + "]",
                "    }",
            ]
        )

    lines.extend(["}", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--geometry", type=Path, default=DEFAULT_GEOMETRY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    items, columns = load_layout(args.config, args.geometry)
    args.output.write_text(render_layout(items, columns), encoding="utf-8")
    print(f"wrote {args.output} ({len(items)} furniture items)")


if __name__ == "__main__":
    main()
