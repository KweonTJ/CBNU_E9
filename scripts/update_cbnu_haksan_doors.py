#!/usr/bin/env python3
"""Generate the composed USD door layout from the canonical doors.json file."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "worlds/cbnu_haksan_1f_corridor/config/doors.json"
DEFAULT_OUTPUT = ROOT / "worlds/cbnu_haksan_1f_corridor/config/doors_layout.usda"
DOOR_REFERENCES = {
    "single": "../../../assets/architecture/doors/wood_door_single.usda",
    "double": "../../../assets/architecture/doors/wood_door_double.usda",
    "double_glass": "../../../assets/architecture/doors/glass_door_double.usda",
    "double_glass_pair": "../../../assets/architecture/doors/glass_door_double_pair.usda",
}
USD_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def usd_number(value: float) -> str:
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return "0" if text in {"", "-0"} else text


def load_doors(path: Path) -> list[dict[str, object]]:
    config = json.loads(path.read_text(encoding="utf-8"))
    data = config.get("doors") if isinstance(config, dict) else None
    if not isinstance(data, list) or not data:
        raise ValueError("doors.json must contain a non-empty doors array")

    seen: set[str] = set()
    for index, door in enumerate(data):
        if not isinstance(door, dict):
            raise ValueError(f"door entry {index} must be an object")

        name = door.get("name")
        door_type = door.get("type")
        position = door.get("position")
        yaw_deg = door.get("yaw_deg")
        if not isinstance(name, str) or not USD_NAME.fullmatch(name):
            raise ValueError(f"door entry {index} has an invalid USD prim name")
        if name in seen:
            raise ValueError(f"duplicate door name: {name}")
        seen.add(name)
        if door_type not in DOOR_REFERENCES:
            raise ValueError(f"{name} has unsupported type: {door_type}")

        if not isinstance(position, list) or len(position) != 3:
            raise ValueError(f"{name}.position must be [x, y, z]")
        values = [*position, yaw_deg]
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in values):
            raise ValueError(f"{name} position and yaw_deg must be numeric")
        if not all(math.isfinite(float(value)) for value in values):
            raise ValueError(f"{name} position and yaw_deg must be finite")

    return data


def render_layout(doors: list[dict[str, object]]) -> str:
    lines = [
        "#usda 1.0",
        "(",
        '    defaultPrim = "Doors"',
        "    metersPerUnit = 1",
        '    upAxis = "Z"',
        ")",
        "",
        'def Xform "Doors"',
        "{",
        '    custom string cbnu:sourceConfig = "doors.json"',
    ]

    for door in doors:
        name = str(door["name"])
        door_type = str(door["type"])
        reference = DOOR_REFERENCES[door_type]
        x, y, z = (float(value) for value in door["position"])
        yaw_deg = float(door["yaw_deg"])
        lines.extend(
            [
                "",
                f'    def Xform "{name}" (',
                f"        prepend references = @{reference}@",
                "    )",
                "    {",
                f'        custom string cbnu:doorType = "{door_type}"',
                '        custom string cbnu:placementSource = "doors.json"',
                f"        double xformOp:rotateZ = {usd_number(yaw_deg)}",
                "        double3 xformOp:translate = "
                f"({usd_number(x)}, {usd_number(y)}, {usd_number(z)})",
                '        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateZ"]',
                "    }",
            ]
        )

    lines.extend(["}", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    doors = load_doors(args.config)
    args.output.write_text(render_layout(doors), encoding="utf-8")
    print(f"wrote {args.output} ({len(doors)} doors)")


if __name__ == "__main__":
    main()
