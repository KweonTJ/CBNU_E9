#!/usr/bin/env python3
"""Generate the dynamic parcel-pile USD layout from dynamic_obstacles.json."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORLD_DIR = ROOT / "worlds/cbnu_haksan_1f_corridor"
DEFAULT_CONFIG = WORLD_DIR / "config/dynamic_obstacles.json"
DEFAULT_OUTPUT = WORLD_DIR / "config/dynamic_obstacles_layout.usda"
USD_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
MATERIAL_VARIANTS = {
    "kraft_light": (0.62, 0.39, 0.18),
    "kraft_medium": (0.50, 0.29, 0.12),
    "kraft_dark": (0.38, 0.20, 0.075),
}


def usd_number(value: float) -> str:
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return "0" if text in {"", "-0"} else text


def validate_number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def load_config(
    config_path: Path,
) -> tuple[list[dict[str, object]], bool, list[dict[str, object]]]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("dynamic_obstacles.json must contain an object")
    groups = config.get("groups")
    boxes = config.get("boxes")
    starts_asleep = config.get("starts_asleep", True)
    if not isinstance(groups, list) or not groups:
        raise ValueError("dynamic_obstacles.json groups must be a non-empty array")
    group_names: set[str] = set()
    for index, group in enumerate(groups):
        if not isinstance(group, dict):
            raise ValueError(f"group {index} must be an object")
        name = group.get("name")
        if not isinstance(name, str) or not USD_NAME.fullmatch(name):
            raise ValueError(f"group {index} has an invalid USD name")
        if name in group_names:
            raise ValueError(f"duplicate parcel group name: {name}")
        group_names.add(name)
        reference_prim = group.get("reference_prim")
        placement = group.get("placement")
        if not isinstance(reference_prim, str) or not USD_NAME.fullmatch(reference_prim):
            raise ValueError(f"{name}.reference_prim must be a valid prim name")
        if not isinstance(placement, str) or not placement:
            raise ValueError(f"{name}.placement must be a non-empty string")
    groups_by_name = {str(group["name"]): group for group in groups}
    table_group = groups_by_name.get("ParcelPile_Table_03", {})
    entrance_group = groups_by_name.get("ParcelCluster_MainEntrance", {})
    if table_group.get("reference_prim") != "Table_03":
        raise ValueError("parcel pile must remain anchored to Table_03")
    if table_group.get("front_direction") != "+X":
        raise ValueError("Table_03 front direction must be +X")
    if validate_number(
        table_group.get("minimum_clearance_m"),
        "ParcelPile_Table_03.minimum_clearance_m",
    ) <= 0:
        raise ValueError("ParcelPile_Table_03.minimum_clearance_m must be positive")
    if entrance_group.get("reference_prim") != "Door_Double_05":
        raise ValueError("entrance parcel cluster must remain anchored to Door_Double_05")
    if entrance_group.get("placement") != "inside_main_entrance_right":
        raise ValueError("entrance parcel cluster placement mismatch")
    validate_number(
        entrance_group.get("clear_path_x_max"),
        "ParcelCluster_MainEntrance.clear_path_x_max",
    )
    if not isinstance(starts_asleep, bool):
        raise ValueError("starts_asleep must be boolean")
    if not isinstance(boxes, list) or not boxes:
        raise ValueError("dynamic_obstacles.json boxes must be a non-empty array")

    seen: set[str] = set()
    sizes: set[tuple[float, float, float]] = set()
    supports: dict[str, dict[str, object]] = {}
    for index, box in enumerate(boxes):
        if not isinstance(box, dict):
            raise ValueError(f"box {index} must be an object")
        name = box.get("name")
        if not isinstance(name, str) or not USD_NAME.fullmatch(name):
            raise ValueError(f"box {index} has an invalid USD prim name")
        if name in seen:
            raise ValueError(f"duplicate parcel box name: {name}")
        seen.add(name)
        group_name = box.get("group")
        if group_name not in group_names:
            raise ValueError(f"{name} references unknown group: {group_name}")

        position = box.get("position")
        size = box.get("size")
        if not isinstance(position, list) or len(position) != 3:
            raise ValueError(f"{name}.position must be [x, y, z]")
        if not isinstance(size, list) or len(size) != 3:
            raise ValueError(f"{name}.size must be [width, depth, height]")
        position_values = tuple(
            validate_number(value, f"{name}.position.{axis}")
            for axis, value in zip("xyz", position)
        )
        size_values = tuple(
            validate_number(value, f"{name}.size.{axis}")
            for axis, value in zip("xyz", size)
        )
        if any(value <= 0 for value in size_values):
            raise ValueError(f"{name}.size values must be positive")
        if size_values in sizes:
            raise ValueError(f"all parcel boxes must have distinct sizes: {name}")
        sizes.add(size_values)
        validate_number(box.get("yaw_deg"), f"{name}.yaw_deg")
        if validate_number(box.get("mass_kg"), f"{name}.mass_kg") <= 0:
            raise ValueError(f"{name}.mass_kg must be positive")
        level = box.get("stack_level")
        if isinstance(level, bool) or not isinstance(level, int) or level < 1:
            raise ValueError(f"{name}.stack_level must be a positive integer")
        if box.get("material_variant") not in MATERIAL_VARIANTS:
            raise ValueError(f"{name} has an unsupported material_variant")

        support_name = box.get("support")
        height = size_values[2]
        if support_name == "floor":
            expected_z = height / 2
            if level != 1:
                raise ValueError(f"{name} floor-supported box must be stack_level 1")
        elif isinstance(support_name, str) and support_name in supports:
            support = supports[support_name]
            if support.get("group") != group_name:
                raise ValueError(f"{name} cannot stack across parcel groups")
            support_position = tuple(float(value) for value in support["position"])
            support_size = tuple(float(value) for value in support["size"])
            expected_z = support_position[2] + support_size[2] / 2 + height / 2
            if level != int(support["stack_level"]) + 1:
                raise ValueError(f"{name}.stack_level does not follow {support_name}")
            if abs(position_values[0] - support_position[0]) > 1e-9 or abs(
                position_values[1] - support_position[1]
            ) > 1e-9:
                raise ValueError(f"{name} must be centered on its support {support_name}")
            if size_values[0] >= support_size[0] or size_values[1] >= support_size[1]:
                raise ValueError(f"{name} must fit inside its support {support_name}")
        else:
            raise ValueError(f"{name} references an unknown or later support: {support_name}")
        if abs(position_values[2] - expected_z) > 1e-9:
            raise ValueError(f"{name}.position.z must touch its support at {expected_z}")
        supports[name] = box

    return groups, starts_asleep, boxes


def render_material(name: str, color: tuple[float, float, float]) -> list[str]:
    r, g, b = (usd_number(value) for value in color)
    return [
        f'        def Material "{name}"',
        "        {",
        f"            token outputs:surface.connect = </DynamicObstacles/Looks/{name}/PreviewSurface.outputs:surface>",
        '            def Shader "PreviewSurface"',
        "            {",
        '                uniform token info:id = "UsdPreviewSurface"',
        f"                color3f inputs:diffuseColor = ({r}, {g}, {b})",
        "                float inputs:metallic = 0",
        "                float inputs:roughness = 0.78",
        "                token outputs:surface",
        "            }",
        "        }",
        "",
    ]


def render_layout(
    groups: list[dict[str, object]], starts_asleep: bool, boxes: list[dict[str, object]]
) -> str:
    groups_by_name = {str(group["name"]): group for group in groups}
    table_group = groups_by_name["ParcelPile_Table_03"]
    entrance_group = groups_by_name["ParcelCluster_MainEntrance"]
    group_names = ", ".join(f'"{group["name"]}"' for group in groups)
    lines = [
        "#usda 1.0",
        "(",
        '    defaultPrim = "DynamicObstacles"',
        "    metersPerUnit = 1",
        '    upAxis = "Z"',
        ")",
        "",
        'def Xform "DynamicObstacles"',
        "{",
        '    custom string cbnu:sourceConfig = "dynamic_obstacles.json"',
        f"    custom string[] cbnu:groupNames = [{group_names}]",
        f"    custom int cbnu:groupCount = {len(groups)}",
        f"    custom double cbnu:minimumTableClearance = {usd_number(float(table_group['minimum_clearance_m']))}",
        f"    custom double cbnu:entranceClearPathXMax = {usd_number(float(entrance_group['clear_path_x_max']))}",
        f"    custom int cbnu:boxCount = {len(boxes)}",
        "",
        '    def Scope "Looks"',
        "    {",
    ]
    for variant, color in MATERIAL_VARIANTS.items():
        material_name = "Cardboard" + "".join(part.title() for part in variant.split("_"))
        lines.extend(render_material(material_name, color))
    lines.extend(
        [
            '        def Material "PackingTape"',
            "        {",
            "            token outputs:surface.connect = </DynamicObstacles/Looks/PackingTape/PreviewSurface.outputs:surface>",
            '            def Shader "PreviewSurface"',
            "            {",
            '                uniform token info:id = "UsdPreviewSurface"',
            "                color3f inputs:diffuseColor = (0.76, 0.58, 0.25)",
            "                float inputs:metallic = 0",
            "                float inputs:roughness = 0.42",
            "                token outputs:surface",
            "            }",
            "        }",
            "",
            '        def Material "ShippingLabel"',
            "        {",
            "            token outputs:surface.connect = </DynamicObstacles/Looks/ShippingLabel/PreviewSurface.outputs:surface>",
            '            def Shader "PreviewSurface"',
            "            {",
            '                uniform token info:id = "UsdPreviewSurface"',
            "                color3f inputs:diffuseColor = (0.88, 0.86, 0.76)",
            "                float inputs:metallic = 0",
            "                float inputs:roughness = 0.60",
            "                token outputs:surface",
            "            }",
            "        }",
            "    }",
        ]
    )

    for box in boxes:
        name = str(box["name"])
        x, y, z = (float(value) for value in box["position"])
        width, depth, height = (float(value) for value in box["size"])
        yaw = float(box["yaw_deg"])
        mass = float(box["mass_kg"])
        level = int(box["stack_level"])
        group_name = str(box["group"])
        support = str(box["support"])
        material_name = "Cardboard" + "".join(
            part.title() for part in str(box["material_variant"]).split("_")
        )
        tape_width = min(0.11, width * 0.22)
        label_width = min(0.22, width * 0.34)
        label_depth = min(0.16, depth * 0.30)
        lines.extend(
            [
                "",
                f'    def Xform "{name}" (',
                '        prepend apiSchemas = ["PhysicsRigidBodyAPI", "PhysicsMassAPI"]',
                "    )",
                "    {",
                '        custom string cbnu:semanticClass = "dynamic_parcel_box"',
                f'        custom string cbnu:group = "{group_name}"',
                f"        custom int cbnu:stackLevel = {level}",
                f'        custom string cbnu:support = "{support}"',
                f"        bool physics:startsAsleep = {str(starts_asleep).lower()}",
                "        bool physics:kinematicEnabled = false",
                "        bool physics:rigidBodyEnabled = true",
                f"        float physics:mass = {usd_number(mass)}",
                f"        double xformOp:rotateZ = {usd_number(yaw)}",
                f"        double3 xformOp:translate = ({usd_number(x)}, {usd_number(y)}, {usd_number(z)})",
                '        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateZ"]',
                "",
                '        def Cube "Body" (',
                '            prepend apiSchemas = ["MaterialBindingAPI", "PhysicsCollisionAPI"]',
                "        )",
                "        {",
                f"            rel material:binding = </DynamicObstacles/Looks/{material_name}>",
                "            bool physics:collisionEnabled = true",
                "            double size = 1",
                f"            double3 xformOp:scale = ({usd_number(width)}, {usd_number(depth)}, {usd_number(height)})",
                '            uniform token[] xformOpOrder = ["xformOp:scale"]',
                "        }",
                "",
                '        def Cube "TopTape"',
                "        {",
                "            rel material:binding = </DynamicObstacles/Looks/PackingTape>",
                "            double size = 1",
                f"            double3 xformOp:scale = ({usd_number(tape_width)}, {usd_number(depth + 0.01)}, 0.006)",
                f"            double3 xformOp:translate = (0, 0, {usd_number(height / 2 + 0.003)})",
                '            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]',
                "        }",
                "",
                '        def Cube "FrontTape"',
                "        {",
                "            rel material:binding = </DynamicObstacles/Looks/PackingTape>",
                "            double size = 1",
                f"            double3 xformOp:scale = ({usd_number(tape_width)}, 0.006, {usd_number(height + 0.006)})",
                f"            double3 xformOp:translate = (0, {usd_number(-depth / 2 - 0.003)}, 0)",
                '            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]',
                "        }",
                "",
                '        def Cube "ShippingLabel"',
                "        {",
                "            rel material:binding = </DynamicObstacles/Looks/ShippingLabel>",
                "            double size = 1",
                f"            double3 xformOp:scale = ({usd_number(label_width)}, {usd_number(label_depth)}, 0.004)",
                f"            double3 xformOp:translate = ({usd_number(width * 0.16)}, {usd_number(-depth * 0.12)}, {usd_number(height / 2 + 0.006)})",
                '            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]',
                "        }",
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

    groups, starts_asleep, boxes = load_config(args.config)
    args.output.write_text(
        render_layout(groups, starts_asleep, boxes), encoding="utf-8"
    )
    print(f"wrote {args.output} ({len(boxes)} dynamic parcel boxes)")


if __name__ == "__main__":
    main()
