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
DISPLAY_WALL_REFERENCES = {
    "corner": "../../../assets/architecture/digital_display_wall/digital_display_wall_corner.usda",
}
PARTITION_WALL_REFERENCES = {
    "full_height_wood": "../../../assets/architecture/partitions/full_height_wood_partition.usda",
}
COLUMN_DISPLAY_REFERENCE = "../../../assets/architecture/digital_display_wall/digital_display_panel_large_column.usda"
WALL_POSTER_REFERENCES = {
    "gray_horizontal": "../../../assets/architecture/wall_decor/gray_horizontal_poster.usda",
    "gray_horizontal_large": "../../../assets/architecture/wall_decor/gray_horizontal_poster_large.usda",
}
ELEVATOR_DOOR_REFERENCES = {
    "stainless_center_opening": "../../../assets/architecture/elevators/stainless_elevator_door.usda",
}
INFORMATION_BOARD_REFERENCES = {
    "green_mobile": "../../../assets/architecture/signage/green_information_board.usda",
}
USD_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def usd_number(value: float) -> str:
    text = f"{value:.7f}".rstrip("0").rstrip(".")
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
        asset_variant = wall.get("asset_variant")
        position = wall.get("position")
        yaw_deg = wall.get("yaw_deg")
        if not isinstance(name, str) or not USD_NAME.fullmatch(name):
            raise ValueError(f"entry {index} has an invalid USD prim name")
        if name in seen:
            raise ValueError(f"duplicate architectural asset name: {name}")
        seen.add(name)
        if asset_variant not in DISPLAY_WALL_REFERENCES:
            raise ValueError(
                f"{name}.asset_variant must be one of {sorted(DISPLAY_WALL_REFERENCES)}"
            )
        if not isinstance(position, list) or len(position) != 3:
            raise ValueError(f"{name}.position must be [x, y, z]")
        numeric_values = [*position, yaw_deg]
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in numeric_values):
            raise ValueError(f"{name} position and yaw_deg must be numeric")
        if not all(math.isfinite(float(value)) for value in numeric_values):
            raise ValueError(f"{name} position and yaw_deg must be finite")
        for field in (
            "height", "depth", "display_width", "display_height", "mount_clearance",
            "front_display_gap", "side_display_gap", "front_frame_end_margin",
            "side_frame_end_margin", "side_display_center", "side_body_end_margin",
        ):
            value = wall.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or float(value) <= 0:
                raise ValueError(f"{name}.{field} must be positive")
        if wall.get("side_wordmark_text") != "학연산공통기술연구원":
            raise ValueError(f"{name}.side_wordmark_text must match the institute name")
        for field in ("side_wordmark_width", "side_wordmark_height", "side_wordmark_bottom", "side_wordmark_depth"):
            value = wall.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or float(value) <= 0:
                raise ValueError(f"{name}.{field} must be positive")
        if wall.get("side_wordmark_color") != "black":
            raise ValueError(f"{name}.side_wordmark_color must be black")
        if wall.get("side_wordmark_geometry") != "extruded_mesh":
            raise ValueError(f"{name}.side_wordmark_geometry must be extruded_mesh")
        for field in ("front_length", "side_length"):
            value = wall.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or float(value) < 0:
                raise ValueError(f"{name}.{field} must be non-negative")
        for field in ("front_display_count", "side_display_count"):
            value = wall.get(field)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name}.{field} must be a non-negative integer")
        front_present = float(wall["front_length"]) > 0 and int(wall["front_display_count"]) > 0
        side_present = float(wall["side_length"]) > 0 and int(wall["side_display_count"]) > 0
        if not (front_present or side_present):
            raise ValueError(f"{name} must contain at least one display section")
        if (float(wall["front_length"]) > 0) != (int(wall["front_display_count"]) > 0):
            raise ValueError(f"{name} front length/count presence mismatch")
        if (float(wall["side_length"]) > 0) != (int(wall["side_display_count"]) > 0):
            raise ValueError(f"{name} side length/count presence mismatch")
        if asset_variant == "corner" and not (front_present and side_present):
            raise ValueError(f"{name} corner variant requires both sections")
    return walls


def load_column_displays(path: Path) -> list[dict[str, object]]:
    config = json.loads(path.read_text(encoding="utf-8"))
    displays = config.get("column_displays") if isinstance(config, dict) else None
    if not isinstance(displays, list) or not displays:
        raise ValueError("architecture.json must contain a non-empty column_displays array")

    seen: set[str] = set()
    for index, display in enumerate(displays):
        if not isinstance(display, dict):
            raise ValueError(f"column display entry {index} must be an object")
        name = display.get("name")
        position = display.get("position")
        yaw_deg = display.get("yaw_deg")
        if not isinstance(name, str) or not USD_NAME.fullmatch(name):
            raise ValueError(f"column display entry {index} has an invalid USD prim name")
        if name in seen:
            raise ValueError(f"duplicate column display name: {name}")
        seen.add(name)
        if display.get("asset_variant") != "large_column":
            raise ValueError(f"{name}.asset_variant must be large_column")
        if display.get("reference_prim") != "Column_03":
            raise ValueError(f"{name} must remain mounted on Column_03")
        if not isinstance(position, list) or len(position) != 3:
            raise ValueError(f"{name}.position must be [x, y, z]")
        numeric_values = [*position, yaw_deg]
        if any(
            isinstance(value, bool) or not isinstance(value, (int, float))
            for value in numeric_values
        ) or not all(math.isfinite(float(value)) for value in numeric_values):
            raise ValueError(f"{name} position and yaw_deg must be finite numbers")
        for field in ("width", "height", "depth"):
            value = display.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or float(value) <= 0:
                raise ValueError(f"{name}.{field} must be positive")
        if display.get("facing") != "-Y_toward_main_entrance":
            raise ValueError(f"{name} must face the main south entrance")
    return displays


def load_partition_walls(path: Path) -> list[dict[str, object]]:
    config = json.loads(path.read_text(encoding="utf-8"))
    partitions = config.get("partition_walls") if isinstance(config, dict) else None
    if not isinstance(partitions, list) or not partitions:
        raise ValueError("architecture.json must contain a non-empty partition_walls array")

    seen: set[str] = set()
    for index, partition in enumerate(partitions):
        if not isinstance(partition, dict):
            raise ValueError(f"partition wall entry {index} must be an object")
        name = partition.get("name")
        position = partition.get("position")
        yaw_deg = partition.get("yaw_deg")
        if not isinstance(name, str) or not USD_NAME.fullmatch(name):
            raise ValueError(f"partition wall entry {index} has an invalid USD prim name")
        if name in seen:
            raise ValueError(f"duplicate partition wall name: {name}")
        seen.add(name)
        if partition.get("asset_variant") not in PARTITION_WALL_REFERENCES:
            raise ValueError(
                f"{name}.asset_variant must be one of {sorted(PARTITION_WALL_REFERENCES)}"
            )
        if not isinstance(position, list) or len(position) != 3:
            raise ValueError(f"{name}.position must be [x, y, z]")
        numeric_values = [*position, yaw_deg]
        if any(
            isinstance(value, bool) or not isinstance(value, (int, float))
            for value in numeric_values
        ) or not all(math.isfinite(float(value)) for value in numeric_values):
            raise ValueError(f"{name} position and yaw_deg must be finite numbers")
        for field in ("thickness", "length", "height"):
            value = partition.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or float(value) <= 0:
                raise ValueError(f"{name}.{field} must be positive")
        if partition.get("reference_from") != "DigitalDisplayWall_01":
            raise ValueError(f"{name} must start at DigitalDisplayWall_01")
        if partition.get("reference_to") != "NorthCorridorEndGlassWall/RightFrame":
            raise ValueError(f"{name} must terminate at the north glass RightFrame")
        if partition.get("facing") != "-X_into_north_corridor":
            raise ValueError(f"{name} must face -X into the north corridor")
    return partitions


def load_wall_posters(path: Path) -> list[dict[str, object]]:
    config = json.loads(path.read_text(encoding="utf-8"))
    posters = config.get("wall_posters") if isinstance(config, dict) else None
    if not isinstance(posters, list) or not posters:
        raise ValueError("architecture.json must contain a non-empty wall_posters array")

    seen: set[str] = set()
    for index, poster in enumerate(posters):
        if not isinstance(poster, dict):
            raise ValueError(f"wall poster entry {index} must be an object")
        name = poster.get("name")
        position = poster.get("position")
        yaw_deg = poster.get("yaw_deg")
        if not isinstance(name, str) or not USD_NAME.fullmatch(name):
            raise ValueError(f"wall poster entry {index} has an invalid USD prim name")
        if name in seen:
            raise ValueError(f"duplicate wall poster name: {name}")
        seen.add(name)
        if poster.get("asset_variant") not in WALL_POSTER_REFERENCES:
            raise ValueError(
                f"{name}.asset_variant must be one of {sorted(WALL_POSTER_REFERENCES)}"
            )
        reference_wall = poster.get("reference_wall")
        if reference_wall not in {"Wall_06", "Wall_11"}:
            raise ValueError(f"{name}.reference_wall must be Wall_06 or Wall_11")
        reference_door = poster.get("reference_door")
        if reference_wall == "Wall_11" and reference_door != "Door_Single_04":
            raise ValueError(f"{name} on Wall_11 must remain relative to Door_Single_04")
        if reference_wall == "Wall_06" and reference_door is not None:
            raise ValueError(f"{name} on Wall_06 must not reference a door")
        if not isinstance(position, list) or len(position) != 3:
            raise ValueError(f"{name}.position must be [x, y, z]")
        numeric_values = [*position, yaw_deg]
        if any(
            isinstance(value, bool) or not isinstance(value, (int, float))
            for value in numeric_values
        ) or not all(math.isfinite(float(value)) for value in numeric_values):
            raise ValueError(f"{name} position and yaw_deg must be finite numbers")
        for field in ("width", "height", "depth"):
            value = poster.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or float(value) <= 0:
                raise ValueError(f"{name}.{field} must be positive")
        if float(poster["width"]) <= float(poster["height"]):
            raise ValueError(f"{name} must remain wider than it is tall")
        expected_facing = {
            "gray_horizontal": "-X_into_lobby",
            "gray_horizontal_large": "-Y_into_lobby",
        }[str(poster["asset_variant"])]
        if poster.get("facing") != expected_facing:
            raise ValueError(f"{name} facing must be {expected_facing}")
        if poster.get("asset_variant") == "gray_horizontal_large":
            if poster.get("return_wall") != "Wall_05":
                raise ValueError(f"{name}.return_wall must be Wall_05")
            if poster.get("reference_elevator") != "ElevatorDoor_01":
                raise ValueError(f"{name}.reference_elevator must be ElevatorDoor_01")
            if poster.get("return_facing") != "+X_into_north_corridor":
                raise ValueError(f"{name}.return_facing must face +X into the north corridor")
            return_length = poster.get("return_length")
            if (
                isinstance(return_length, bool)
                or not isinstance(return_length, (int, float))
                or not math.isfinite(float(return_length))
                or float(return_length) <= 0
            ):
                raise ValueError(f"{name}.return_length must be positive")
    return posters


def load_elevator_doors(path: Path) -> list[dict[str, object]]:
    config = json.loads(path.read_text(encoding="utf-8"))
    doors = config.get("elevator_doors") if isinstance(config, dict) else None
    if not isinstance(doors, list) or not doors:
        raise ValueError("architecture.json must contain a non-empty elevator_doors array")

    seen: set[str] = set()
    for index, door in enumerate(doors):
        if not isinstance(door, dict):
            raise ValueError(f"elevator door entry {index} must be an object")
        name = door.get("name")
        position = door.get("position")
        yaw_deg = door.get("yaw_deg")
        if not isinstance(name, str) or not USD_NAME.fullmatch(name):
            raise ValueError(f"elevator door entry {index} has an invalid USD prim name")
        if name in seen:
            raise ValueError(f"duplicate elevator door name: {name}")
        seen.add(name)
        if door.get("asset_variant") not in ELEVATOR_DOOR_REFERENCES:
            raise ValueError(
                f"{name}.asset_variant must be one of {sorted(ELEVATOR_DOOR_REFERENCES)}"
            )
        if door.get("reference_wall") != "Wall_05":
            raise ValueError(f"{name} must remain on Wall_05")
        if not isinstance(position, list) or len(position) != 3:
            raise ValueError(f"{name}.position must be [x, y, z]")
        numeric_values = [*position, yaw_deg]
        if any(
            isinstance(value, bool) or not isinstance(value, (int, float))
            for value in numeric_values
        ) or not all(math.isfinite(float(value)) for value in numeric_values):
            raise ValueError(f"{name} position and yaw_deg must be finite numbers")
        for field in ("width", "height", "depth"):
            value = door.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or float(value) <= 0:
                raise ValueError(f"{name}.{field} must be positive")
        if door.get("facing") != "+X_into_north_corridor":
            raise ValueError(f"{name} must face +X into the north corridor")
        if door.get("service_state") != "operational" or door.get("door_state") != "closed":
            raise ValueError(f"{name} must describe an operational elevator with closed doors")
    return doors


def load_information_boards(path: Path) -> list[dict[str, object]]:
    config = json.loads(path.read_text(encoding="utf-8"))
    boards = config.get("information_boards") if isinstance(config, dict) else None
    if not isinstance(boards, list) or len(boards) != 3:
        raise ValueError("architecture.json must contain exactly three information boards")

    seen: set[str] = set()
    for index, board in enumerate(boards):
        if not isinstance(board, dict):
            raise ValueError(f"information board entry {index} must be an object")
        name = board.get("name")
        position = board.get("position")
        yaw_deg = board.get("yaw_deg")
        if not isinstance(name, str) or not USD_NAME.fullmatch(name):
            raise ValueError(f"information board entry {index} has an invalid USD prim name")
        if name in seen:
            raise ValueError(f"duplicate information board name: {name}")
        seen.add(name)
        if board.get("asset_variant") not in INFORMATION_BOARD_REFERENCES:
            raise ValueError(
                f"{name}.asset_variant must be one of {sorted(INFORMATION_BOARD_REFERENCES)}"
            )
        if not isinstance(position, list) or len(position) != 3:
            raise ValueError(f"{name}.position must be [x, y, z]")
        numeric_values = [*position, yaw_deg]
        if any(
            isinstance(value, bool) or not isinstance(value, (int, float))
            for value in numeric_values
        ) or not all(math.isfinite(float(value)) for value in numeric_values):
            raise ValueError(f"{name} position and yaw_deg must be finite numbers")
        for field in ("width", "depth", "height"):
            value = board.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or float(value) <= 0:
                raise ValueError(f"{name}.{field} must be positive")
        if board.get("facing") != "-Y_into_north_corridor":
            raise ValueError(f"{name} must face -Y into the north corridor")
        if board.get("mounted_on") != "NorthGlassWoodPlatform":
            raise ValueError(f"{name} must stand on NorthGlassWoodPlatform")
    return boards


def render_layout(
    walls: list[dict[str, object]],
    partition_walls: list[dict[str, object]],
    column_displays: list[dict[str, object]],
    wall_posters: list[dict[str, object]],
    elevator_doors: list[dict[str, object]],
    information_boards: list[dict[str, object]],
) -> str:
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
        asset_variant = str(wall["asset_variant"])
        display_wall_reference = DISPLAY_WALL_REFERENCES[asset_variant]
        x, y, z = (float(value) for value in wall["position"])
        yaw_deg = float(wall["yaw_deg"])
        lines.extend(
            [
                "",
                f'    def Xform "{name}" (',
                f"        prepend references = @{display_wall_reference}@",
                "    )",
                "    {",
                f'        custom string cbnu:assetVariant = "{asset_variant}"',
                f'        custom double cbnu:frontLength = {usd_number(float(wall["front_length"]))}',
                f'        custom double cbnu:sideLength = {usd_number(float(wall["side_length"]))}',
                f'        custom double cbnu:displayWidth = {usd_number(float(wall["display_width"]))}',
                f'        custom double cbnu:displayHeight = {usd_number(float(wall["display_height"]))}',
                f'        custom double cbnu:frontDisplayGap = {usd_number(float(wall["front_display_gap"]))}',
                f'        custom double cbnu:sideDisplayGap = {usd_number(float(wall["side_display_gap"]))}',
                f'        custom double cbnu:sideDisplayCenter = {usd_number(float(wall["side_display_center"]))}',
                f'        custom double cbnu:sideBodyEndMargin = {usd_number(float(wall["side_body_end_margin"]))}',
                f'        custom double cbnu:frontFrameEndMargin = {usd_number(float(wall["front_frame_end_margin"]))}',
                f'        custom double cbnu:sideFrameEndMargin = {usd_number(float(wall["side_frame_end_margin"]))}',
                f'        custom double cbnu:mountClearance = {usd_number(float(wall["mount_clearance"]))}',
                f'        custom int cbnu:frontDisplayCount = {int(wall["front_display_count"])}',
                f'        custom int cbnu:sideDisplayCount = {int(wall["side_display_count"])}',
                f'        custom string cbnu:sideWordmarkText = "{wall["side_wordmark_text"]}"',
                f'        custom double cbnu:sideWordmarkWidth = {usd_number(float(wall["side_wordmark_width"]))}',
                f'        custom double cbnu:sideWordmarkHeight = {usd_number(float(wall["side_wordmark_height"]))}',
                f'        custom double cbnu:sideWordmarkBottom = {usd_number(float(wall["side_wordmark_bottom"]))}',
                f'        custom double cbnu:sideWordmarkDepth = {usd_number(float(wall["side_wordmark_depth"]))}',
                f'        custom string cbnu:sideWordmarkColor = "{wall["side_wordmark_color"]}"',
                f'        custom string cbnu:sideWordmarkGeometry = "{wall["side_wordmark_geometry"]}"',
                f"        double xformOp:rotateZ = {usd_number(yaw_deg)}",
                f"        double3 xformOp:translate = ({usd_number(x)}, {usd_number(y)}, {usd_number(z)})",
                '        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateZ"]',
                "    }",
            ]
        )
    for partition in partition_walls:
        name = str(partition["name"])
        reference = PARTITION_WALL_REFERENCES[str(partition["asset_variant"])]
        x, y, z = (float(value) for value in partition["position"])
        yaw_deg = float(partition["yaw_deg"])
        lines.extend(
            [
                "",
                f'    def Xform "{name}" (',
                f"        prepend references = @{reference}@",
                "    )",
                "    {",
                f'        custom string cbnu:assetVariant = "{partition["asset_variant"]}"',
                f'        custom string cbnu:referenceFrom = "{partition["reference_from"]}"',
                f'        custom string cbnu:referenceTo = "{partition["reference_to"]}"',
                f'        custom string cbnu:facing = "{partition["facing"]}"',
                f'        custom double cbnu:thickness = {usd_number(float(partition["thickness"]))}',
                f'        custom double cbnu:length = {usd_number(float(partition["length"]))}',
                f'        custom double cbnu:height = {usd_number(float(partition["height"]))}',
                f"        double xformOp:rotateZ = {usd_number(yaw_deg)}",
                f"        double3 xformOp:translate = ({usd_number(x)}, {usd_number(y)}, {usd_number(z)})",
                '        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateZ"]',
                "    }",
            ]
        )
    for display in column_displays:
        name = str(display["name"])
        x, y, z = (float(value) for value in display["position"])
        yaw_deg = float(display["yaw_deg"])
        lines.extend(
            [
                "",
                f'    def Xform "{name}" (',
                f"        prepend references = @{COLUMN_DISPLAY_REFERENCE}@",
                "    )",
                "    {",
                '        custom string cbnu:assetVariant = "large_column"',
                f'        custom string cbnu:referencePrim = "{display["reference_prim"]}"',
                f'        custom string cbnu:facing = "{display["facing"]}"',
                f'        custom double cbnu:width = {usd_number(float(display["width"]))}',
                f'        custom double cbnu:height = {usd_number(float(display["height"]))}',
                f'        custom double cbnu:depth = {usd_number(float(display["depth"]))}',
                f"        double xformOp:rotateZ = {usd_number(yaw_deg)}",
                f"        double3 xformOp:translate = ({usd_number(x)}, {usd_number(y)}, {usd_number(z)})",
                '        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateZ"]',
                "    }",
            ]
        )
    for poster in wall_posters:
        name = str(poster["name"])
        reference = WALL_POSTER_REFERENCES[str(poster["asset_variant"])]
        x, y, z = (float(value) for value in poster["position"])
        yaw_deg = float(poster["yaw_deg"])
        lines.extend(
            [
                "",
                f'    def Xform "{name}" (',
                f"        prepend references = @{reference}@",
                "    )",
                "    {",
                f'        custom string cbnu:assetVariant = "{poster["asset_variant"]}"',
                f'        custom string cbnu:referenceWall = "{poster["reference_wall"]}"',
            ]
        )
        if poster.get("reference_door") is not None:
            lines.append(
                f'        custom string cbnu:referenceDoor = "{poster["reference_door"]}"'
            )
        if poster.get("return_wall") is not None:
            lines.extend(
                [
                    f'        custom string cbnu:returnWall = "{poster["return_wall"]}"',
                    f'        custom string cbnu:referenceElevator = "{poster["reference_elevator"]}"',
                    f'        custom string cbnu:returnFacing = "{poster["return_facing"]}"',
                    f'        custom double cbnu:returnLength = {usd_number(float(poster["return_length"]))}',
                ]
            )
        lines.extend(
            [
                f'        custom string cbnu:facing = "{poster["facing"]}"',
                f'        custom double cbnu:width = {usd_number(float(poster["width"]))}',
                f'        custom double cbnu:height = {usd_number(float(poster["height"]))}',
                f'        custom double cbnu:depth = {usd_number(float(poster["depth"]))}',
                f"        double xformOp:rotateZ = {usd_number(yaw_deg)}",
                f"        double3 xformOp:translate = ({usd_number(x)}, {usd_number(y)}, {usd_number(z)})",
                '        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateZ"]',
                "    }",
            ]
        )
    for door in elevator_doors:
        name = str(door["name"])
        reference = ELEVATOR_DOOR_REFERENCES[str(door["asset_variant"])]
        x, y, z = (float(value) for value in door["position"])
        yaw_deg = float(door["yaw_deg"])
        lines.extend(
            [
                "",
                f'    def Xform "{name}" (',
                f"        prepend references = @{reference}@",
                "    )",
                "    {",
                f'        custom string cbnu:assetVariant = "{door["asset_variant"]}"',
                f'        custom string cbnu:referenceWall = "{door["reference_wall"]}"',
                f'        custom string cbnu:facing = "{door["facing"]}"',
                f'        custom string cbnu:serviceState = "{door["service_state"]}"',
                f'        custom string cbnu:doorState = "{door["door_state"]}"',
                f'        custom double cbnu:width = {usd_number(float(door["width"]))}',
                f'        custom double cbnu:height = {usd_number(float(door["height"]))}',
                f'        custom double cbnu:depth = {usd_number(float(door["depth"]))}',
                f"        double xformOp:rotateZ = {usd_number(yaw_deg)}",
                f"        double3 xformOp:translate = ({usd_number(x)}, {usd_number(y)}, {usd_number(z)})",
                '        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateZ"]',
                "    }",
            ]
        )
    for board in information_boards:
        name = str(board["name"])
        reference = INFORMATION_BOARD_REFERENCES[str(board["asset_variant"])]
        x, y, z = (float(value) for value in board["position"])
        yaw_deg = float(board["yaw_deg"])
        lines.extend(
            [
                "",
                f'    def Xform "{name}" (',
                f"        prepend references = @{reference}@",
                "    )",
                "    {",
                f'        custom string cbnu:assetVariant = "{board["asset_variant"]}"',
                f'        custom string cbnu:mountedOn = "{board["mounted_on"]}"',
                f'        custom string cbnu:facing = "{board["facing"]}"',
                f'        custom double cbnu:width = {usd_number(float(board["width"]))}',
                f'        custom double cbnu:depth = {usd_number(float(board["depth"]))}',
                f'        custom double cbnu:height = {usd_number(float(board["height"]))}',
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
    partition_walls = load_partition_walls(args.config)
    column_displays = load_column_displays(args.config)
    wall_posters = load_wall_posters(args.config)
    elevator_doors = load_elevator_doors(args.config)
    information_boards = load_information_boards(args.config)
    args.output.write_text(
        render_layout(
            walls,
            partition_walls,
            column_displays,
            wall_posters,
            elevator_doors,
            information_boards,
        ),
        encoding="utf-8",
    )
    print(
        f"wrote {args.output} "
        f"({len(walls)} display walls, {len(partition_walls)} partition walls, "
        f"{len(column_displays)} column displays, "
        f"{len(wall_posters)} wall posters, {len(elevator_doors)} elevator doors, "
        f"{len(information_boards)} information boards)"
    )


if __name__ == "__main__":
    main()
