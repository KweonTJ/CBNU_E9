#!/usr/bin/env python3
"""Generate the composed architectural-detail layout from architecture.json."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "worlds/cbnu_haksan_1f_corridor/config/architecture.json"
DEFAULT_OUTPUT = ROOT / "worlds/cbnu_haksan_1f_corridor/config/architecture_layout.usda"
DISPLAY_WALL_REFERENCE = "../../../assets/architecture/digital_display_wall/digital_display_wall_corner.usda"
USD_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def usd_number(value: float) -> str:
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return "0" if text in {"", "-0"} else text


def load_display_walls(path: Path) -> list[dict[str, object]]:
    config = json.loads(path.read_text(encoding="utf-8"))
    walls = config.get("digital_display_walls") if isinstance(config, dict) else None
    if not isinstance(walls, list) or not walls:
        raise ValueError("architecture.json must contain a non-empty digital_display_walls array")

    seen: set[str] = set()
    for index, wall in enumerate(walls):
        if not isinstance(wall, dict):
            raise ValueError(f"digital display wall entry {index} must be an object")
        name = wall.get("name")
        position = wall.get("position")
        yaw_deg = wall.get("yaw_deg")
        if not isinstance(name, str) or not USD_NAME.fullmatch(name):
            raise ValueError(f"entry {index} has an invalid USD prim name")
        if name in seen:
            raise ValueError(f"duplicate architectural asset name: {name}")
        seen.add(name)
        if not isinstance(position, list) or len(position) != 3:
            raise ValueError(f"{name}.position must be [x, y, z]")
        numeric_values = [*position, yaw_deg]
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in numeric_values):
            raise ValueError(f"{name} position and yaw_deg must be numeric")
        if not all(math.isfinite(float(value)) for value in numeric_values):
            raise ValueError(f"{name} position and yaw_deg must be finite")
        for field in (
            "front_length", "side_length", "height", "depth",
            "display_width", "display_height", "mount_clearance",
        ):
            value = wall.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or float(value) <= 0:
                raise ValueError(f"{name}.{field} must be positive")
        for field in ("front_display_count", "side_display_count"):
            value = wall.get(field)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name}.{field} must be a positive integer")
    return walls


def render_layout(walls: list[dict[str, object]]) -> str:
    lines = [
        "#usda 1.0",
        "(",
        '    defaultPrim = "Architecture"',
        "    metersPerUnit = 1",
        '    upAxis = "Z"',
        ")",
        "",
        'def Xform "Architecture"',
        "{",
        '    custom string cbnu:sourceConfig = "architecture.json"',
    ]
    for wall in walls:
        name = str(wall["name"])
        x, y, z = (float(value) for value in wall["position"])
        yaw_deg = float(wall["yaw_deg"])
        lines.extend(
            [
                "",
                f'    def Xform "{name}" (',
                f"        prepend references = @{DISPLAY_WALL_REFERENCE}@",
                "    )",
                "    {",
                '        custom string cbnu:assetType = "digital_display_wall_corner"',
                f'        custom double cbnu:frontLength = {usd_number(float(wall["front_length"]))}',
                f'        custom double cbnu:sideLength = {usd_number(float(wall["side_length"]))}',
                f'        custom double cbnu:displayWidth = {usd_number(float(wall["display_width"]))}',
                f'        custom double cbnu:displayHeight = {usd_number(float(wall["display_height"]))}',
                f'        custom double cbnu:mountClearance = {usd_number(float(wall["mount_clearance"]))}',
                f'        custom int cbnu:frontDisplayCount = {int(wall["front_display_count"])}',
                f'        custom int cbnu:sideDisplayCount = {int(wall["side_display_count"])}',
                f"        double xformOp:rotateZ = {usd_number(yaw_deg)}",
                f"        double3 xformOp:translate = ({usd_number(x)}, {usd_number(y)}, {usd_number(z)})",
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
    walls = load_display_walls(args.config)
    args.output.write_text(render_layout(walls), encoding="utf-8")
    print(f"wrote {args.output} ({len(walls)} architectural assets)")


if __name__ == "__main__":
    main()
