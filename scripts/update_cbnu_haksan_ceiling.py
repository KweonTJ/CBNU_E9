#!/usr/bin/env python3
"""Generate the composed ceiling-light layout from ceiling.json."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORLD_DIR = ROOT / "worlds/cbnu_haksan_1f_corridor"
DEFAULT_CONFIG = WORLD_DIR / "config/ceiling.json"
DEFAULT_OUTPUT = WORLD_DIR / "config/ceiling_layout.usda"
LIGHT_REFERENCES = {
    "panel": "../../../assets/architecture/ceiling/ceiling_panel_light.usda",
    "large_panel": "../../../assets/architecture/ceiling/ceiling_panel_light_large.usda",
}
USD_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def usd_number(value: float) -> str:
    result = f"{value:.6f}".rstrip("0").rstrip(".")
    return "0" if result in {"", "-0"} else result


def load_lights(path: Path) -> list[dict[str, object]]:
    config = json.loads(path.read_text(encoding="utf-8"))
    lights = config.get("lights") if isinstance(config, dict) else None
    if not isinstance(lights, list) or not lights:
        raise ValueError("ceiling.json must contain a non-empty lights array")

    seen: set[str] = set()
    for index, light in enumerate(lights):
        if not isinstance(light, dict):
            raise ValueError(f"light entry {index} must be an object")
        name = light.get("name")
        position = light.get("position")
        yaw_deg = light.get("yaw_deg")
        light_type = light.get("type", "panel")
        if not isinstance(name, str) or not USD_NAME.fullmatch(name):
            raise ValueError(f"light entry {index} has an invalid USD prim name")
        if name in seen:
            raise ValueError(f"duplicate ceiling light name: {name}")
        seen.add(name)
        if light_type not in LIGHT_REFERENCES:
            raise ValueError(f"{name}.type must be one of {sorted(LIGHT_REFERENCES)}")
        if not isinstance(position, list) or len(position) != 3:
            raise ValueError(f"{name}.position must be [x, y, z]")
        values = [*position, yaw_deg]
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in values):
            raise ValueError(f"{name} position and yaw_deg must be numeric")
        if not all(math.isfinite(float(value)) for value in values):
            raise ValueError(f"{name} position and yaw_deg must be finite")
    return lights


def render_layout(lights: list[dict[str, object]]) -> str:
    lines = [
        "#usda 1.0",
        "(",
        '    defaultPrim = "CeilingLights"',
        "    metersPerUnit = 1",
        '    upAxis = "Z"',
        ")",
        "",
        'def Xform "CeilingLights"',
        "{",
        '    custom string cbnu:sourceConfig = "ceiling.json"',
    ]

    for light in lights:
        x, y, z = (float(value) for value in light["position"])
        yaw_deg = float(light["yaw_deg"])
        light_type = str(light.get("type", "panel"))
        light_reference = LIGHT_REFERENCES[light_type]
        lines.extend(
            [
                "",
                f'    def Xform "{light["name"]}" (',
                f"        prepend references = @{light_reference}@",
                "    )",
                "    {",
                '        custom string cbnu:placementSource = "ceiling.json"',
                f'        custom string cbnu:lightType = "{light_type}"',
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

    lights = load_lights(args.config)
    args.output.write_text(render_layout(lights), encoding="utf-8")
    print(f"wrote {args.output} ({len(lights)} ceiling lights)")


if __name__ == "__main__":
    main()
