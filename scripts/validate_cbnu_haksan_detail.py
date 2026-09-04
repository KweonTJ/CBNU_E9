#!/usr/bin/env python3
"""Static validation for the CBNU Haksan 1F detailed lobby world."""

from __future__ import annotations

import json
import math
import re
import struct
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORLD_DIR = ROOT / "worlds/cbnu_haksan_1f_corridor"
WORLD = WORLD_DIR / "cbnu_haksan_1f_corridor.usda"
GEOMETRY = WORLD_DIR / "config/geometry.json"
DOORS = WORLD_DIR / "config/doors.json"
FURNITURE = WORLD_DIR / "config/furniture.json"
PREVIEW = WORLD_DIR / "preview_top_view_detailed.png"
ARCHITECTURE_PREVIEW = WORLD_DIR / "preview_architecture_detail.png"
ARCHITECTURE_CONFIG = WORLD_DIR / "config/architecture.json"
ARCHITECTURE_LAYOUT = WORLD_DIR / "config/architecture_layout.usda"
DYNAMIC_OBSTACLES_CONFIG = WORLD_DIR / "config/dynamic_obstacles.json"
DYNAMIC_OBSTACLES_LAYOUT = WORLD_DIR / "config/dynamic_obstacles_layout.usda"
SOFA_ASSETS = {
    "straight": ROOT / "assets/furniture/sofa_straight.usda",
    "corner": ROOT / "assets/furniture/sofa_corner.usda",
    "single": ROOT / "assets/furniture/sofa_single.usda",
    "u_column": ROOT / "assets/furniture/sofa_u_around_2m_column.usda",
}
COMMON_SOFA_MATERIAL = ROOT / "assets/materials/furniture/brown_sofa_material.usda"
DARK_REDDISH_BROWN_SOFA_MATERIAL = ROOT / "assets/materials/furniture/dark_reddish_brown_leather_material.usda"
MARBLE_MATERIAL = ROOT / "assets/materials/lobby/marble_floor.usda"
WALL_COLUMN_MATERIAL = ROOT / "assets/materials/lobby/wall_column_light_gray.usda"
GRANITE_TEXTURE = ROOT / "assets/materials/lobby/textures/bala_white_granite_floor_pattern.png"
ATM_ASSET = ROOT / "assets/equipment/atm_machine.usda"
TABLE_ASSET = ROOT / "assets/furniture/lobby_table.usda"
FILLED_TABLE_ASSET = ROOT / "assets/furniture/lobby_table_filled.usda"
FURNITURE_LAYOUT = WORLD_DIR / "config/furniture_layout.usda"
CEILING_CONFIG = WORLD_DIR / "config/ceiling.json"
CEILING_LAYOUT = WORLD_DIR / "config/ceiling_layout.usda"
CEILING_MATERIAL = ROOT / "assets/materials/lobby/ceiling_white.usda"
CEILING_LIGHT_ASSET = ROOT / "assets/architecture/ceiling/ceiling_panel_light.usda"
CEILING_LARGE_LIGHT_ASSET = ROOT / "assets/architecture/ceiling/ceiling_panel_light_large.usda"
CEILING_AC_ASSET = ROOT / "assets/architecture/ceiling/ceiling_cassette_air_conditioner.usda"
FRONT_GLASS_WALL_ASSET = ROOT / "assets/architecture/windows/front_entrance_glass_walls.usda"
NORTH_CORRIDOR_END_GLASS_WALL_ASSET = ROOT / "assets/architecture/windows/north_corridor_end_glass_wall.usda"
NORTH_CORRIDOR_WOOD_PLATFORM_ASSET = ROOT / "assets/architecture/platforms/north_corridor_wood_platform.usda"
GREEN_INFORMATION_BOARD_ASSET = ROOT / "assets/architecture/signage/green_information_board.usda"
ENTRANCE_PILLAR_ASSET = ROOT / "assets/structural/entrance_side_pillar.usda"
COLUMN_ASSET = ROOT / "assets/structural/column_2m.usda"
DISPLAY_WALL_ASSET = ROOT / "assets/architecture/digital_display_wall/digital_display_wall_corner.usda"
DISPLAY_PANEL_ASSET = ROOT / "assets/architecture/digital_display_wall/digital_display_panel.usda"
COLUMN_DISPLAY_ASSET = ROOT / "assets/architecture/digital_display_wall/digital_display_panel_large_column.usda"
GRAY_POSTER_ASSET = ROOT / "assets/architecture/wall_decor/gray_horizontal_poster.usda"
GRAY_POSTER_LARGE_ASSET = ROOT / "assets/architecture/wall_decor/gray_horizontal_poster_large.usda"
ELEVATOR_DOOR_ASSET = ROOT / "assets/architecture/elevators/stainless_elevator_door.usda"
EAST_WHITE_DOUBLE_DOOR_ASSET = ROOT / "assets/architecture/doors/white_door_double_wood_portal.usda"
DISPLAY_WALL_DARK_MATERIAL = ROOT / "assets/materials/display_wall/display_wall_dark.usda"
DISPLAY_SCREEN_MATERIAL = ROOT / "assets/materials/display_wall/display_screen.usda"
DISPLAY_WORDMARK_ASSET = ROOT / "assets/architecture/digital_display_wall/institute_wordmark_mesh.usda"
WOOD_PARTITION_ASSET = ROOT / "assets/architecture/partitions/full_height_wood_partition.usda"
EXTERIOR_PAVEMENT_ASSET = ROOT / "assets/architecture/exterior/exterior_sidewalk_pavers.usda"
SIDEWALK_MATERIAL = ROOT / "assets/materials/exterior/sidewalk_pavers.usda"
SIDEWALK_TEXTURE = ROOT / "assets/materials/exterior/textures/campus_sidewalk_pavers_basecolor.png"
SIDEWALK_NORMAL_TEXTURE = ROOT / "assets/materials/exterior/textures/campus_sidewalk_pavers_normal.png"
SIDEWALK_ROUGHNESS_TEXTURE = ROOT / "assets/materials/exterior/textures/campus_sidewalk_pavers_roughness.png"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def usd_number(value: float) -> str:
    result = f"{float(value):.7f}".rstrip("0").rstrip(".")
    return "0" if result in {"", "-0"} else result


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    require(data[:8] == b"\x89PNG\r\n\x1a\n", f"not a PNG: {path}")
    return struct.unpack(">II", data[16:24])


def prim_block(layer_text: str, prim_name: str) -> str:
    match = re.search(
        rf'def\s+\w+\s+"{re.escape(prim_name)}"(?:\s*\([^)]*\))?\s*\{{(.*?)\n\s*\}}',
        layer_text,
        flags=re.DOTALL,
    )
    require(match is not None, f"prim missing: {prim_name}")
    return match.group(1)


def validate_mesh_topology(layer_text: str, mesh_name: str) -> None:
    block = prim_block(layer_text, mesh_name)
    counts_match = re.search(r"faceVertexCounts\s*=\s*\[([^]]+)\]", block)
    indices_match = re.search(r"faceVertexIndices\s*=\s*\[([^]]+)\]", block)
    points_match = re.search(r"points\s*=\s*\[([^]]+)\]", block, flags=re.DOTALL)
    require(counts_match is not None, f"face counts missing: {mesh_name}")
    require(indices_match is not None, f"face indices missing: {mesh_name}")
    require(points_match is not None, f"points missing: {mesh_name}")
    counts = [int(value) for value in re.findall(r"\d+", counts_match.group(1))]
    indices = [int(value) for value in re.findall(r"\d+", indices_match.group(1))]
    points = re.findall(r"\([^()]+\)", points_match.group(1))
    require(sum(counts) == len(indices), f"mesh index count mismatch: {mesh_name}")
    require(indices and max(indices) < len(points), f"mesh point index out of range: {mesh_name}")


def validate_watertight_mesh(layer_text: str, mesh_name: str) -> None:
    """Check every edge in the authored unified sofa mesh has exactly two faces."""
    block = prim_block(layer_text, mesh_name)
    counts = [
        int(value)
        for value in re.findall(
            r"\d+", re.search(r"faceVertexCounts\s*=\s*\[([^]]+)\]", block).group(1)
        )
    ]
    indices = [
        int(value)
        for value in re.findall(
            r"\d+", re.search(r"faceVertexIndices\s*=\s*\[([^]]+)\]", block).group(1)
        )
    ]
    edge_counts: Counter[tuple[int, int]] = Counter()
    offset = 0
    for count in counts:
        face = indices[offset : offset + count]
        offset += count
        for index, start in enumerate(face):
            end = face[(index + 1) % len(face)]
            edge_counts[tuple(sorted((start, end)))] += 1
    require(
        edge_counts and all(count == 2 for count in edge_counts.values()),
        f"unclosed or non-manifold render mesh: {mesh_name}",
    )


def validate_unified_sofa_render_policy(layer_text: str, asset_name: str) -> None:
    visible_meshes = {"SofaUnified"}
    mesh_names = set(re.findall(r'def Mesh "([^"]+)"', layer_text))
    require(mesh_names == visible_meshes, f"unexpected render meshes in {asset_name}: {mesh_names}")
    for mesh_name in visible_meshes:
        block = prim_block(layer_text, mesh_name)
        require('token visibility = "inherited"' in block, f"unified render mesh is hidden: {asset_name}: {mesh_name}")
        require("PhysicsCollisionAPI" not in block, f"render mesh has collision API: {asset_name}: {mesh_name}")
        require('subdivisionScheme = "none"' in block, f"single sofa mesh must use authored bevels: {asset_name}")
        validate_mesh_topology(layer_text, mesh_name)
        validate_watertight_mesh(layer_text, mesh_name)
        counts_match = re.search(r"faceVertexCounts\s*=\s*\[([^]]+)\]", block)
        face_counts = {int(value) for value in re.findall(r"\d+", counts_match.group(1))}
        require(face_counts <= {3, 4} and 3 in face_counts, f"concave n-gon cap remains: {asset_name}")

    helper_prims = re.findall(r'def (Cube|Capsule|Sphere|Cylinder) "([^"]+)"', layer_text)
    require(helper_prims, f"collision/helper prims missing: {asset_name}")
    for _, helper_name in helper_prims:
        require(
            'token visibility = "invisible"' in prim_block(layer_text, helper_name),
            f"visible helper primitive remains: {asset_name}: {helper_name}",
        )


def mesh_points(layer_text: str, mesh_name: str) -> list[tuple[float, float, float]]:
    block = prim_block(layer_text, mesh_name)
    points_match = re.search(r"points\s*=\s*\[([^]]+)\]", block, flags=re.DOTALL)
    require(points_match is not None, f"points missing: {mesh_name}")
    points: list[tuple[float, float, float]] = []
    for point in re.findall(r"\(([^()]+)\)", points_match.group(1)):
        values = tuple(float(value.strip()) for value in point.split(","))
        require(len(values) == 3, f"invalid point: {mesh_name}: {point}")
        points.append(values)
    return points


def validate_references() -> int:
    count = 0
    layers = sorted(
        path for path in ROOT.rglob("*")
        if path.is_file() and path.suffix in {".usd", ".usda"}
    )
    for layer in layers:
        layer_text = layer.read_text(encoding="utf-8")
        require(layer_text.count("{") == layer_text.count("}"), f"unbalanced braces: {layer}")
        require(layer_text.count("(") == layer_text.count(")"), f"unbalanced parentheses: {layer}")
        for reference in re.findall(r"@([^@]+)@", layer_text):
            count += 1
            require(not Path(reference).is_absolute(), f"absolute USD reference: {layer}: {reference}")
            target = (layer.parent / reference).resolve()
            require(target.exists(), f"missing USD reference: {layer}: {reference}")
    return count


def validate_world() -> None:
    world_text = WORLD.read_text(encoding="utf-8")
    require('def Xform "Furniture"' in world_text, "/World/Furniture missing")
    require('def Xform "DynamicObstacles"' in world_text, "/World/DynamicObstacles missing")
    require(
        'prepend references = @config/dynamic_obstacles_layout.usda@' in world_text,
        "dynamic obstacle layout reference missing",
    )
    require('def Xform "Doors"' in world_text, "/World/Doors missing")
    require('def Xform "Obstacles"' not in world_text, "raw /World/Obstacles remains")
    require('rel material:binding = </World/Looks/MarbleFloor>' in world_text, "Floor marble binding missing")
    require('def Mesh "Floor"' in world_text and 'bool physics:collisionEnabled = 1' in world_text, "Floor collision missing")
    floor_block = prim_block(world_text, "Floor")
    require('texCoord2f[] primvars:st' in floor_block, "Floor marble UV coordinates missing")
    require('uniform token primvars:st:interpolation = "vertex"' in floor_block, "Floor marble UV interpolation missing")
    st_match = re.search(r"primvars:st\s*=\s*\[([^]]+)\]", floor_block)
    require(st_match is not None, "Floor marble UV data missing")
    require(len(re.findall(r"\([^()]+\)", st_match.group(1))) == 24, "Floor must have one UV per existing vertex")

    require(GRANITE_TEXTURE.exists(), "Bala White granite albedo texture missing")
    require(png_size(GRANITE_TEXTURE) == (1254, 1254), "unexpected granite texture size")
    marble_text = MARBLE_MATERIAL.read_text(encoding="utf-8")
    require('custom string cbnu:sourceStyle = "Bala White Granite"' in marble_text, "granite style metadata missing")
    require('custom string cbnu:pattern = "visible feldspar quartz crystals and charcoal mica flecks"' in marble_text, "granite pattern metadata missing")
    require('uniform token info:id = "UsdUVTexture"' in marble_text, "granite texture shader missing")
    require('asset inputs:file = @./textures/bala_white_granite_floor_pattern.png@' in marble_text, "granite pattern texture reference missing")
    require('float inputs:roughness = 0.24' in marble_text, "granite roughness must stay polished but non-mirrored")
    require('float inputs:clearcoat = 0.26' in marble_text, "granite clearcoat missing")
    require('float2 inputs:scale = (0.4166667, 0.4166667)' in marble_text, "granite world-scale UV repeat mismatch")

    wall_blocks = re.findall(r'def Cube "Wall_\d+".*?\n\s*}', world_text, flags=re.DOTALL)
    rotations = [float(re.search(r"xformOp:rotateZ = ([\d.-]+)", block).group(1)) for block in wall_blocks]
    require(len(rotations) == 12, f"expected 12 walls, found {len(rotations)}")
    require(all(rotation in {0.0, 90.0} for rotation in rotations), f"non-orthogonal wall rotations: {rotations}")
    require(all('PhysicsCollisionAPI' in block and 'physics:collisionEnabled = 1' in block for block in wall_blocks), "Wall collision missing")
    walls_section = world_text.split('def Xform "Walls"', 1)[1].split('def Xform "Columns"', 1)[0]
    require('prepend apiSchemas = ["MaterialBindingAPI"]' in walls_section, "wall material binding API missing")
    require('rel material:binding = </World/Looks/WallColumnLightGray>' in walls_section, "walls must use the light-gray material")
    require('bindMaterialAs = "strongerThanDescendants"' in walls_section, "wall light-gray binding must override descendants")
    require('custom string cbnu:surfaceFinish = "cool stone gray between the light and dark-gray posters"' in walls_section, "wall gray metadata missing")

    expected_corner_wall_transforms = {
        "Wall_02": ((9.4768, 0.2, 3.0), (30.7108, 13.3044, 1.5), 25.9724, "min"),
        "Wall_06": ((22.7522, 0.2, 3.0), (11.4631, 13.1403, 1.5), 22.8392, "max"),
        "Wall_08": ((16.0275, 0.2, 3.0), (8.10075, 11.4103, 1.5), 16.1145, "max"),
        "Wall_12": ((4.7956, 0.2, 3.0), (33.0514, 6.1739, 1.5), 30.6536, "min"),
    }
    for wall_name, (scale, translate, target_endpoint, endpoint_side) in expected_corner_wall_transforms.items():
        block = prim_block(world_text, wall_name)
        require(
            f"double3 xformOp:scale = ({usd_number(scale[0])}, 0.2, 3)" in block,
            f"unified corner wall scale mismatch: {wall_name}",
        )
        require(
            f"double3 xformOp:translate = ({usd_number(translate[0])}, {usd_number(translate[1])}, 1.5)" in block,
            f"unified corner wall pose mismatch: {wall_name}",
        )
        endpoint = translate[0] + (-scale[0] / 2 if endpoint_side == "min" else scale[0] / 2)
        require(abs(endpoint - target_endpoint) < 1e-9, f"wall does not reach adjoining inner face: {wall_name}")
        require('custom string cbnu:cornerJoin = "extends ' in block, f"corner join metadata missing: {wall_name}")

    geometry = json.loads(GEOMETRY.read_text(encoding="utf-8"))
    corner_joins = geometry.get("wall_corner_unifications", [])
    require(len(corner_joins) == 4, "expected four unified re-entrant wall corners")
    require(
        {item["extended_wall"] for item in corner_joins}
        == {"Wall_02", "Wall_06", "Wall_08", "Wall_12"},
        "wall corner unification set mismatch",
    )
    require(
        all(float(item["extension_m"]) == 0.1 for item in corner_joins),
        "each re-entrant corner must close the wall half-thickness gap",
    )
    west_corridor = geometry.get("west_corridor", {})
    require(west_corridor.get("width") == 1.73, "west corridor width must be 1.73 m")
    require(west_corridor.get("center_y") == 12.2753, "west corridor centerline changed")
    require(west_corridor.get("end_treatment") == "opaque_wall", "west corridor end must be an opaque wall")
    polygon = geometry["corridor_polygon_xy"]
    require(polygon[5][1] == polygon[6][1] == 13.1403, "west corridor north boundary mismatch")
    require(polygon[7][1] == polygon[8][1] == 11.4103, "west corridor south boundary mismatch")
    require(abs(polygon[5][1] - polygon[7][1] - 1.73) < 1e-9, "west corridor polygon width mismatch")
    floor_points = mesh_points(world_text, "Floor")
    require(
        [(point[0], point[1]) for point in floor_points[:12]] == [tuple(point) for point in polygon],
        "Floor footprint does not match geometry.json",
    )

    require(len(geometry["columns"]) == 3, "expected three main columns")
    require(
        all(column["size"] == [1.2, 1.2, 3.0] for column in geometry["columns"]),
        "main column size must be 1.2 x 1.2 x 3.0 m",
    )
    columns_by_name = {column["name"]: column for column in geometry["columns"]}
    require(set(columns_by_name) == {"Column_01", "Column_02", "Column_03"}, "main column names mismatch")
    require(columns_by_name["Column_01"]["center"] == [21.7739, 10.3812], "Column_01 pose mismatch")
    require(columns_by_name["Column_02"]["center"] == [31.1014, 10.3957], "Column_02 forward shift mismatch")
    midpoint = [
        (columns_by_name["Column_01"]["center"][axis] + columns_by_name["Column_02"]["center"][axis]) / 2
        for axis in (0, 1)
    ]
    require(
        all(
            abs(columns_by_name["Column_03"]["center"][axis] - midpoint[axis]) < 1e-9
            for axis in (0, 1)
        ),
        "Column_03 must remain at the outer-column midpoint",
    )
    for column in geometry["columns"]:
        x, y = column["center"]
        expected = f'def Xform "{column["name"]}"'
        require(expected in world_text, f"column missing: {column['name']}")
        translate = f"double3 xformOp:translate = ({x}, {y}, 0)"
        require(translate in world_text, f"column pose mismatch: {column['name']}")
    require(
        world_text.count('references = @../../assets/structural/column_2m.usda@') == 3,
        "main column references mismatch",
    )
    columns_section = world_text.split('def Xform "Columns"', 1)[1].split('def Xform "Architecture"', 1)[0]
    require('prepend apiSchemas = ["MaterialBindingAPI"]' in columns_section, "column material binding API missing")
    require('rel material:binding = </World/Looks/WallColumnLightGray>' in columns_section, "columns must use the light-gray material")
    require('bindMaterialAs = "strongerThanDescendants"' in columns_section, "column light-gray binding must override asset materials")
    require('custom string cbnu:surfaceFinish = "cool stone gray between the light and dark-gray posters"' in columns_section, "column gray metadata missing")
    column_text = COLUMN_ASSET.read_text(encoding="utf-8")
    require("custom double cbnu:columnWidth = 1.2" in column_text, "column width metadata mismatch")
    require('prepend apiSchemas = ["MaterialBindingAPI", "PhysicsCollisionAPI"]' in column_text, "column body material binding API missing")
    require(
        "double3 xformOp:scale = (1.2, 1.2, 3.0)" in prim_block(column_text, "Body"),
        "column asset body must be 1.2 x 1.2 x 3.0 m",
    )

    entrance_pillars = geometry.get("entrance_pillars", [])
    require(len(entrance_pillars) == 2, "entrance must have two matching side pillars")
    pillars_by_name = {item["name"]: item for item in entrance_pillars}
    require(
        set(pillars_by_name) == {"Entrance_Pillar_ATM_Side", "Entrance_Pillar_Opposite"},
        "entrance pillar names mismatch",
    )
    require(
        all(item["size"] == [1.0425, 1.0, 3.0] for item in entrance_pillars),
        "entrance pillar sizes must be identical",
    )
    require(pillars_by_name["Entrance_Pillar_ATM_Side"]["center"] == [20.89875, 0.49], "ATM-side entrance pillar pose mismatch")
    require(pillars_by_name["Entrance_Pillar_Opposite"]["center"] == [26.10125, 0.49], "opposite entrance pillar pose mismatch")
    require(abs((23.5 - 20.89875) - (26.10125 - 23.5)) < 1e-9, "entrance pillars are not mirrored")
    require(abs((20.89875 - 1.0425 / 2) - 20.3775) < 1e-9, "ATM-side pillar does not begin at ATM collision edge")
    require(abs((20.89875 + 1.0425 / 2) - 21.42) < 1e-9, "ATM-side pillar does not end at door frame edge")
    for pillar in entrance_pillars:
        require(f'def Xform "{pillar["name"]}"' in world_text, f"entrance pillar missing: {pillar['name']}")
        x, y = pillar["center"]
        require(f"double3 xformOp:translate = ({x}, {y}, 0)" in world_text, f"entrance pillar world pose mismatch: {pillar['name']}")
    require(world_text.count('references = @../../assets/structural/entrance_side_pillar.usda@') == 2, "entrance pillar references mismatch")

    pillar_text = ENTRANCE_PILLAR_ASSET.read_text(encoding="utf-8")
    require('custom double3 cbnu:size = (1.0425, 1.0, 3.0)' in pillar_text, "entrance pillar asset size mismatch")
    require('custom string cbnu:depthPlacement = "back face aligned to south wall; projects 1.0 m into lobby"' in pillar_text, "entrance pillar depth placement metadata missing")
    require('custom bool cbnu:collisionEnabled = false' in pillar_text, "entrance pillars must remain decorative")
    require('prepend apiSchemas = ["MaterialBindingAPI"]' in pillar_text, "entrance pillar material binding API missing")

    require(
        'prepend references = @../../assets/materials/lobby/wall_column_light_gray.usda@'
        in world_text,
        "light-gray wall/column material reference missing",
    )
    light_gray_text = WALL_COLUMN_MATERIAL.read_text(encoding="utf-8")
    require(
        'custom string cbnu:finish = "cool stone-gray matte wall and column finish"'
        in light_gray_text,
        "light-gray finish metadata missing",
    )
    require(
        'color3f inputs:diffuseColor = (0.50, 0.51, 0.52)' in light_gray_text,
        "wall/column gray color mismatch",
    )
    require('float inputs:roughness = 0.72' in light_gray_text, "wall/column stone-gray roughness mismatch")


def validate_ceiling() -> Counter[str]:
    world_text = WORLD.read_text(encoding="utf-8")
    geometry = json.loads(GEOMETRY.read_text(encoding="utf-8"))
    ceiling_config = json.loads(CEILING_CONFIG.read_text(encoding="utf-8"))
    ceiling = ceiling_config["ceiling"]
    lighting_profile = ceiling_config["lighting_profile"]
    lights = ceiling_config["lights"]
    air_conditioners = ceiling_config.get("air_conditioners", [])
    type_counts = Counter(item.get("type", "panel") for item in lights)

    require(type_counts == Counter({"panel": 15, "large_panel": 1}), f"unexpected ceiling lights: {type_counts}")
    require(len(air_conditioners) == 2, "exactly two central ceiling air conditioners are required")
    air_conditioners_by_name = {item["name"]: item for item in air_conditioners}
    require(
        set(air_conditioners_by_name) == {"CeilingAC_01", "CeilingAC_02"},
        "ceiling air conditioner set mismatch",
    )
    expected_air_conditioners = {
        "CeilingAC_01": ([20.8, 8.5, 3.0], "central_lobby_left_of_large_light"),
        "CeilingAC_02": ([29.2, 8.5, 3.0], "central_lobby_right_of_large_light"),
    }
    for name, (position, placement) in expected_air_conditioners.items():
        unit = air_conditioners_by_name[name]
        require(unit["type"] == "cassette_4way", f"ceiling AC type mismatch: {name}")
        require(unit["position"] == position and unit["yaw_deg"] == 0, f"ceiling AC pose mismatch: {name}")
        require(unit["size"] == [1.1, 1.1], f"ceiling AC footprint mismatch: {name}")
        require(unit["visible_depth"] == 0.11, f"ceiling AC depth mismatch: {name}")
        require(unit["placement"] == placement, f"ceiling AC placement metadata mismatch: {name}")
    lights_by_name = {item["name"]: item for item in lights}
    expected_additional_lights = {
        "CeilingLight_13": ([19.0, 12.0, 2.96], 90),
        "CeilingLight_14": ([28.8, 12.0, 2.96], 90),
        "CeilingLight_15": ([29.0, 6.0, 2.96], 90),
    }
    for name, (position, yaw_deg) in expected_additional_lights.items():
        require(name in lights_by_name, f"additional ceiling light missing: {name}")
        require(lights_by_name[name]["position"] == position, f"additional ceiling light position mismatch: {name}")
        require(lights_by_name[name]["yaw_deg"] == yaw_deg, f"additional ceiling light yaw mismatch: {name}")
    require(
        lighting_profile == {
            "standard_panel_intensity": 8000,
            "large_panel_intensity": 12000,
            "large_panel_normalize": False,
            "dome_intensity": 1600,
            "revision_note": "bright indoor lobby profile with three additional standard panels",
        },
        "ceiling lighting profile mismatch",
    )
    require('def Mesh "Ceiling"' in world_text, "/World/Environment/Ceiling missing")
    require('rel material:binding = </World/Looks/CeilingWhite>' in prim_block(world_text, "Ceiling"), "Ceiling material binding missing")
    require('bool physics:collisionEnabled = 1' in prim_block(world_text, "Ceiling"), "Ceiling collision missing")
    require('prepend references = @config/ceiling_layout.usda@' in world_text, "Ceiling light layout reference missing")
    require('prepend references = @../../assets/materials/lobby/ceiling_white.usda@' in world_text, "Ceiling material reference missing")
    validate_mesh_topology(world_text, "Ceiling")

    expected_xy = [tuple(float(value) for value in point) for point in geometry["corridor_polygon_xy"]]
    points = mesh_points(world_text, "Ceiling")
    require(len(points) == 24, "Ceiling must preserve the 24-point closed corridor footprint")
    require([point[:2] for point in points[:12]] == expected_xy, "Ceiling top footprint differs from corridor polygon")
    require([point[:2] for point in points[12:]] == expected_xy, "Ceiling underside footprint differs from corridor polygon")
    height = float(ceiling["height"])
    thickness = float(ceiling["thickness"])
    require(all(abs(point[2] - (height + thickness)) < 1e-9 for point in points[:12]), "Ceiling top height mismatch")
    require(all(abs(point[2] - height) < 1e-9 for point in points[12:]), "Ceiling underside height mismatch")
    require(float(geometry["world"]["ceiling_height"]) == height, "geometry/config ceiling height mismatch")
    require(float(geometry["world"]["ceiling_thickness"]) == thickness, "geometry/config ceiling thickness mismatch")

    ceiling_material_text = CEILING_MATERIAL.read_text(encoding="utf-8")
    require('custom string cbnu:finish = "warm white matte interior ceiling"' in ceiling_material_text, "Ceiling finish metadata missing")
    require('float inputs:roughness = 0.78' in ceiling_material_text, "Ceiling must remain matte")

    layout_text = CEILING_LAYOUT.read_text(encoding="utf-8")
    require(layout_text.count('ceiling_panel_light.usda@') == 15, "standard ceiling panel reference count mismatch")
    require(layout_text.count('ceiling_panel_light_large.usda@') == 1, "large central ceiling light reference missing")
    require('def Scope "AirConditioners"' in layout_text, "ceiling air conditioner scope missing")
    require(layout_text.count('ceiling_cassette_air_conditioner.usda@') == 2, "ceiling air conditioner references missing")
    for light in lights:
        require(f'def Xform "{light["name"]}"' in layout_text, f"ceiling light missing from layout: {light['name']}")
        x, y, z = light["position"]
        expected_translate = f"double3 xformOp:translate = ({usd_number(x)}, {usd_number(y)}, {usd_number(z)})"
        require(expected_translate in layout_text, f"ceiling light layout pose mismatch: {light['name']}")
    for unit in air_conditioners:
        require(f'def Xform "{unit["name"]}"' in layout_text, f"ceiling air conditioner missing from layout: {unit['name']}")
        x, y, z = unit["position"]
        expected_translate = f"double3 xformOp:translate = ({usd_number(x)}, {usd_number(y)}, {usd_number(z)})"
        require(expected_translate in layout_text, f"ceiling air conditioner layout pose mismatch: {unit['name']}")

    regular_text = CEILING_LIGHT_ASSET.read_text(encoding="utf-8")
    require('def RectLight "Light"' in regular_text and 'float inputs:intensity = 8000' in regular_text, "standard ceiling RectLight intensity mismatch")
    large_text = CEILING_LARGE_LIGHT_ASSET.read_text(encoding="utf-8")
    require('custom double2 cbnu:panelSize = (6.0, 2.4)' in large_text, "large central light size mismatch")
    require('float inputs:width = 6.0' in large_text and 'float inputs:height = 2.4' in large_text, "large RectLight dimensions mismatch")
    require('float inputs:intensity = 12000' in large_text, "large central light intensity mismatch")
    require('bool inputs:normalize = false' in large_text, "large central light must use area-scaled output")
    require('float intensity = 1600' in world_text, "DomeLight ambient intensity mismatch")
    dome_light = prim_block(world_text, "DomeLight")
    require('color3f color' not in dome_light, "DomeLight must use its original default white color")
    require('cbnu:backgroundFinish' not in dome_light, "obsolete DomeLight background metadata remains")
    large = next(item for item in lights if item.get("type") == "large_panel")
    require(large["position"] == [25.0, 8.5, 2.95], "large central light pose mismatch")
    require(large.get("size") == [6.0, 2.4], "large central light config size mismatch")
    large_left = float(large["position"][0]) - float(large["size"][0]) / 2
    large_right = float(large["position"][0]) + float(large["size"][0]) / 2
    left_ac = air_conditioners_by_name["CeilingAC_01"]
    right_ac = air_conditioners_by_name["CeilingAC_02"]
    left_ac_right = float(left_ac["position"][0]) + float(left_ac["size"][0]) / 2
    right_ac_left = float(right_ac["position"][0]) - float(right_ac["size"][0]) / 2
    require(
        abs(large_left - left_ac_right - 0.65) < 1e-9
        and abs(right_ac_left - large_right - 0.65) < 1e-9,
        "ceiling air conditioners must retain 0.65 m clearance from the large light",
    )
    require(
        abs(
            (float(left_ac["position"][0]) + float(right_ac["position"][0])) / 2
            - float(large["position"][0])
        ) < 1e-9
        and float(left_ac["position"][1]) == float(right_ac["position"][1]) == float(large["position"][1]),
        "ceiling air conditioners must be mirrored across the central light",
    )
    for unit in air_conditioners:
        unit_half_x = float(unit["size"][0]) / 2
        unit_half_y = float(unit["size"][1]) / 2
        unit_x, unit_y = (float(value) for value in unit["position"][:2])
        for light in lights:
            light_width, light_depth = (
                (float(value) for value in light["size"])
                if light.get("type") == "large_panel"
                else (1.30, 0.36)
            )
            if int(light["yaw_deg"]) % 180 == 90:
                light_width, light_depth = light_depth, light_width
            light_x, light_y = (float(value) for value in light["position"][:2])
            overlap_x = min(unit_x + unit_half_x, light_x + light_width / 2) - max(
                unit_x - unit_half_x, light_x - light_width / 2
            )
            overlap_y = min(unit_y + unit_half_y, light_y + light_depth / 2) - max(
                unit_y - unit_half_y, light_y - light_depth / 2
            )
            require(
                overlap_x <= 0 or overlap_y <= 0,
                f"ceiling air conditioner overlaps light: {unit['name']} / {light['name']}",
            )

    require(CEILING_AC_ASSET.exists(), "ceiling cassette air conditioner asset missing")
    ac_text = CEILING_AC_ASSET.read_text(encoding="utf-8")
    require('custom string cbnu:fixtureType = "four-way ceiling cassette air conditioner"' in ac_text, "ceiling AC type metadata missing")
    require('custom bool cbnu:operational = true' in ac_text, "ceiling AC must be operational")
    require('custom bool cbnu:collisionEnabled = false' in ac_text, "ceiling AC collision policy mismatch")
    require('custom int cbnu:airflowDirections = 4' in ac_text, "ceiling AC airflow metadata mismatch")
    require('custom double2 cbnu:faceSize = (1.1, 1.1)' in ac_text, "ceiling AC face size mismatch")
    require(ac_text.count('def Cube "') == 18, "ceiling AC visible part count mismatch")
    for part in (
        "RecessedHousing", "FacePanel", "IntakeGrille", "Slat_01", "Slat_07",
        "NorthOutlet", "SouthOutlet", "EastOutlet", "WestOutlet",
        "NorthVane", "SouthVane", "EastVane", "WestVane",
    ):
        require(f'"{part}"' in ac_text, f"ceiling AC part missing: {part}")
    require('double3 xformOp:scale = (1.10, 1.10, 0.070)' in prim_block(ac_text, "RecessedHousing"), "ceiling AC housing dimensions mismatch")
    require('double3 xformOp:scale = (0.56, 0.56, 0.012)' in prim_block(ac_text, "IntakeGrille"), "ceiling AC intake dimensions mismatch")
    require("PhysicsCollisionAPI" not in ac_text, "ceiling AC must reuse the ceiling collider")
    require('def RectLight "' not in ac_text, "ceiling AC must not emit light")
    type_counts["air_conditioner"] = len(air_conditioners)
    return type_counts


def validate_front_glass_walls() -> None:
    world_text = WORLD.read_text(encoding="utf-8")
    require('def Xform "FrontEntranceGlassWalls"' in world_text, "front entrance glass wall prim missing")
    require(
        'prepend references = @../../assets/architecture/windows/front_entrance_glass_walls.usda@' in world_text,
        "front entrance glass wall reference missing",
    )
    glass_root = prim_block(world_text, "FrontEntranceGlassWalls")
    require('double3 xformOp:translate = (23.5, 0.17, 0)' in glass_root, "front glass wall pose mismatch")
    wall_10 = prim_block(world_text, "Wall_10")
    require('token visibility = "invisible"' in wall_10, "opaque Wall_10 visual must be hidden behind glazing")
    require('bool physics:collisionEnabled = 1' in wall_10, "Wall_10 collision must remain enabled")
    require('double3 xformOp:scale = (14.7391, 0.2, 3)' in wall_10, "Wall_10 geometry changed")

    glass_text = FRONT_GLASS_WALL_ASSET.read_text(encoding="utf-8")
    require('custom int cbnu:fullHeightGlassPanelCount = 2' in glass_text, "two full-height glass panels are required")
    require('custom bool cbnu:perimeterGapsClosed = true' in glass_text, "front glazing perimeter closure flag missing")
    require('custom double2 cbnu:eachGlassPanelSize = (4.85, 2.82)' in glass_text, "full-height glass panel size mismatch")
    require('custom int cbnu:lowerFacadeWallPanelCount = 2' in glass_text, "front lower facade wall count metadata missing")
    require('custom double cbnu:lowerFacadeWallHeight = 1.02' in glass_text, "front lower facade wall height mismatch")
    require('custom double3 cbnu:leftLowerFacadeWallSize = (5.4055, 0.20, 1.02)' in glass_text, "left lower facade wall size metadata mismatch")
    require('custom double3 cbnu:rightLowerFacadeWallSize = (5.1736, 0.20, 1.02)' in glass_text, "right lower facade wall size metadata mismatch")
    require('custom double2 cbnu:lowerFacadeDoorClearSpan = (21.42, 25.58)' in glass_text, "lower facade door clear span metadata mismatch")
    require(
        'custom string cbnu:lowerFacadeWallPlacement = "full facade spans from side-wall centerlines to the glass-door frame, flush with the visible entrance-pillar south plane"' in glass_text,
        "lower facade wall visible-plane placement metadata mismatch",
    )
    require('def Xform "LeftFullHeightGlass"' in glass_text, "left full-height glass panel missing")
    require('def Xform "RightFullHeightGlass"' in glass_text, "right full-height glass panel missing")
    require(glass_text.count('def Cube "GlassPanel"') == 2, "exactly two full-height glass panes are required")
    require(glass_text.count('def Cube "LowerOpaqueWall"') == 2, "exactly two lower opaque facade walls are required")
    require(glass_text.count('prepend apiSchemas = ["MaterialBindingAPI"]') == 2, "lower facade wall material binding API mismatch")
    require('double3 xformOp:scale = (5.4055, 0.20, 1.02)' in glass_text, "left lower facade wall dimensions mismatch")
    require('double3 xformOp:scale = (5.1736, 0.20, 1.02)' in glass_text, "right lower facade wall dimensions mismatch")
    require('double3 xformOp:translate = (-4.78275, -0.08, 0.51)' in glass_text, "left lower facade wall pose mismatch")
    require('double3 xformOp:translate = (4.6668, -0.08, 0.51)' in glass_text, "right lower facade wall pose mismatch")
    lower_wall_exterior_y = 0.17 - 0.08 - 0.20 / 2
    entrance_pillar_exterior_y = 0.49 - 1.0 / 2
    require(
        abs(lower_wall_exterior_y - entrance_pillar_exterior_y) < 1e-9,
        "lower facade wall exterior face is stepped from the visible entrance pillars",
    )
    lower_wall_interior_y = 0.17 - 0.08 + 0.20 / 2
    glass_exterior_y = 0.17 - 0.025 / 2
    require(lower_wall_interior_y >= glass_exterior_y, "lower facade wall has a depth gap from the glazing")
    left_wall_world_min_x = 23.5 - 4.78275 - 5.4055 / 2
    left_wall_world_max_x = 23.5 - 4.78275 + 5.4055 / 2
    right_wall_world_min_x = 23.5 + 4.6668 - 5.1736 / 2
    right_wall_world_max_x = 23.5 + 4.6668 + 5.1736 / 2
    require(abs(left_wall_world_min_x - 16.0145) < 1e-9, "left lower facade wall does not reach Wall_09")
    require(abs(left_wall_world_max_x - 21.42) < 1e-9, "left lower facade wall does not reach the entrance frame")
    require(abs(right_wall_world_min_x - 25.58) < 1e-9, "right lower facade wall does not start at the entrance frame")
    require(abs(right_wall_world_max_x - 30.7536) < 1e-9, "right lower facade wall does not reach Wall_11")
    require('prepend references = @../../materials/lobby/wall_column_light_gray.usda@' in glass_text, "lower facade wall material reference missing")
    require('custom string cbnu:glassFinish = "clear architectural glass"' in glass_text, "full-height clear glass metadata missing")
    require('color3f inputs:diffuseColor = (0.48, 0.73, 0.78)' in glass_text, "full-height clear glass tint mismatch")
    require('float inputs:opacity = 0.13' in glass_text, "full-height clear glass opacity missing")
    require('float inputs:roughness = 0.08' in glass_text, "full-height clear glass roughness missing")
    require('float inputs:opacityThreshold = 0' in glass_text, "full-height glass blend threshold missing")
    require('custom bool cbnu:collisionEnabled = false' in glass_text, "decorative glass must not add collision")
    require("PhysicsCollisionAPI" not in glass_text, "front glazing and lower facade walls must reuse Wall_10 collision")
    require('double3 xformOp:scale = (0.2355, 0.060, 3.0)' in prim_block(glass_text, "OuterFrame"), "left wall/glass perimeter gap remains")
    require('double3 xformOp:translate = (-7.26775, 0, 1.5)' in prim_block(glass_text, "OuterFrame"), "left outer frame closure pose mismatch")
    require(glass_text.count('double3 xformOp:scale = (0.22, 0.060, 3.0)') == 2, "door-side perimeter gaps remain")
    require('double3 xformOp:translate = (-2.19, 0, 1.5)' in glass_text, "left door-side closure pose mismatch")
    require('double3 xformOp:translate = (2.19, 0, 1.5)' in glass_text, "right door-side closure pose mismatch")


def validate_west_corridor_end_wall() -> None:
    world_text = WORLD.read_text(encoding="utf-8")
    require('def Xform "WestCorridorEndGlassWall"' not in world_text, "west corridor end glass must be removed")
    require(
        '@../../assets/architecture/windows/corridor_end_glass_wall.usda@' not in world_text,
        "west corridor glass reference remains",
    )
    wall_07 = prim_block(world_text, "Wall_07")
    require('visibility = "invisible"' not in wall_07, "opaque Wall_07 must remain visible")
    require('bool physics:collisionEnabled = 1' in wall_07, "Wall_07 collision must remain enabled")
    require('double3 xformOp:scale = (1.73, 0.2, 3)' in wall_07, "Wall_07 width mismatch")
    require('double3 xformOp:translate = (0.087, 12.2753, 1.5)' in wall_07, "Wall_07 pose mismatch")


def validate_north_corridor_end_glass_wall() -> None:
    world_text = WORLD.read_text(encoding="utf-8")
    require('def Xform "NorthCorridorEndGlassWall"' in world_text, "north corridor end glass wall prim missing")
    require(
        'prepend references = @../../assets/architecture/windows/north_corridor_end_glass_wall.usda@' in world_text,
        "north corridor end glass wall reference missing",
    )
    glass_root = prim_block(world_text, "NorthCorridorEndGlassWall")
    require('double3 xformOp:translate = (24.4058, 20.60, 0)' in glass_root, "north corridor glass pose mismatch")
    wall_04 = prim_block(world_text, "Wall_04")
    require('token visibility = "invisible"' in wall_04, "opaque Wall_04 visual must be hidden behind glazing")
    require('bool physics:collisionEnabled = 1' in wall_04, "Wall_04 collision must remain enabled")
    require('double3 xformOp:scale = (3.3332, 0.2, 3)' in wall_04, "Wall_04 geometry changed")

    glass_text = NORTH_CORRIDOR_END_GLASS_WALL_ASSET.read_text(encoding="utf-8")
    require('custom double2 cbnu:glassPanelSize = (3.1332, 2.82)' in glass_text, "north corridor glass size mismatch")
    require('custom bool cbnu:hasLowerOpaqueWall = true' in glass_text, "north corridor lower opaque wall metadata missing")
    require('custom double cbnu:lowerOpaqueWallHeight = 1.02' in glass_text, "north corridor lower wall height mismatch")
    require('custom double3 cbnu:lowerOpaqueWallSize = (3.1332, 0.20, 1.02)' in glass_text, "north corridor lower wall size metadata mismatch")
    require(glass_text.count('def Cube "GlassPanel"') == 1, "north corridor must use one full-height glass pane")
    require(glass_text.count('def Cube "LowerOpaqueWall"') == 1, "north corridor must use one lower opaque wall")
    north_lower_wall = prim_block(glass_text, "LowerOpaqueWall")
    require('prepend apiSchemas = ["MaterialBindingAPI"]' in glass_text, "north corridor lower wall material API missing")
    require('double3 xformOp:scale = (3.1332, 0.20, 1.02)' in north_lower_wall, "north corridor lower wall dimensions mismatch")
    require('double3 xformOp:translate = (0, 0.07, 0.51)' in north_lower_wall, "north corridor lower wall pose mismatch")
    require('rel material:binding = </NorthCorridorEndGlassWall/LowerOpaqueWallMaterial>' in north_lower_wall, "north corridor lower wall material binding mismatch")
    require('@../../materials/lobby/wall_column_light_gray.usda@' in glass_text, "north corridor lower wall stone-gray material reference missing")
    require('custom string cbnu:glassFinish = "clear architectural glass"' in glass_text, "north corridor clear glass metadata missing")
    require('color3f inputs:diffuseColor = (0.48, 0.73, 0.78)' in glass_text, "north corridor clear glass tint mismatch")
    require('float inputs:opacity = 0.13' in glass_text, "north corridor clear glass opacity missing")
    require('float inputs:roughness = 0.08' in glass_text, "north corridor clear glass roughness missing")
    require('custom bool cbnu:collisionEnabled = false' in glass_text, "decorative north glass must not add collision")
    require("PhysicsCollisionAPI" not in glass_text, "north glazing and lower wall must reuse Wall_04 collision")
    north_lower_wall_south_face = 20.60 + 0.07 - 0.20 / 2
    platform_north_edge = 20.27 + 0.60 / 2
    require(
        abs(north_lower_wall_south_face - platform_north_edge) < 1e-9,
        "north lower wall is stepped from the wood platform edge",
    )


def validate_north_corridor_wood_platform() -> None:
    world_text = WORLD.read_text(encoding="utf-8")
    require('def Xform "NorthGlassWoodPlatform"' in world_text, "north glass wood platform prim missing")
    require(
        'prepend references = @../../assets/architecture/platforms/north_corridor_wood_platform.usda@' in world_text,
        "north glass wood platform relative reference missing",
    )
    platform_root = prim_block(world_text, "NorthGlassWoodPlatform")
    require('double3 xformOp:translate = (24.4058, 20.27, 0)' in platform_root, "north glass wood platform pose mismatch")

    platform_text = NORTH_CORRIDOR_WOOD_PLATFORM_ASSET.read_text(encoding="utf-8")
    require('custom string cbnu:architectureType = "low wooden platform"' in platform_text, "wood platform type metadata mismatch")
    require('custom bool cbnu:collisionEnabled = true' in platform_text, "wood platform collision metadata mismatch")
    require('custom double3 cbnu:platformSize = (3.1332, 0.60, 0.15)' in platform_text, "wood platform size metadata mismatch")
    require(platform_text.count('def Cube "PlatformBody"') == 1, "wood platform must use one solid body")
    platform_body = prim_block(platform_text, "PlatformBody")
    require('double3 xformOp:scale = (3.1332, 0.60, 0.15)' in platform_body, "wood platform body dimensions mismatch")
    require('double3 xformOp:translate = (0, 0, 0.075)' in platform_body, "wood platform body height mismatch")
    require(
        'prepend apiSchemas = ["MaterialBindingAPI", "PhysicsCollisionAPI"]' in platform_text,
        "wood platform collider schema missing",
    )
    require('bool physics:collisionEnabled = true' in platform_body, "wood platform collision disabled")
    require('PhysicsRigidBodyAPI' not in platform_text, "wood platform must remain static")
    require('rel material:binding = </NorthCorridorWoodPlatform/WoodMaterial>' in platform_body, "wood platform material binding missing")
    require('color3f inputs:diffuseColor = (0.38, 0.17, 0.055)' in platform_text, "wood platform color mismatch")

    corridor_center_x = 24.4058
    platform_width = 3.1332
    require(abs(corridor_center_x - platform_width / 2 - 22.8392) < 1e-9, "wood platform does not meet the west corridor inner face")
    require(abs(corridor_center_x + platform_width / 2 - 25.9724) < 1e-9, "wood platform does not meet the east corridor inner face")
    platform_north_edge = 20.27 + 0.60 / 2
    glass_frame_south_edge = 20.60 - 0.060 / 2
    require(abs(platform_north_edge - glass_frame_south_edge) < 1e-9, "wood platform is not flush with the glass frame")
    elevator_02_north_edge = 18.8 + 1.45 / 2
    platform_south_edge = 20.27 - 0.60 / 2
    require(abs(platform_south_edge - elevator_02_north_edge - 0.445) < 1e-9, "wood platform clearance from ElevatorDoor_02 mismatch")


def validate_exterior_sidewalk_pavers() -> None:
    world_text = WORLD.read_text(encoding="utf-8")
    require('def Xform "ExteriorSidewalkPavers"' in world_text, "exterior sidewalk prim missing")
    require(
        'prepend references = @../../assets/architecture/exterior/exterior_sidewalk_pavers.usda@' in world_text,
        "exterior sidewalk relative reference missing",
    )

    pavement_text = EXTERIOR_PAVEMENT_ASSET.read_text(encoding="utf-8")
    require('custom bool cbnu:collisionEnabled = false' in pavement_text, "exterior pavement must remain visual-only")
    require('custom double cbnu:surfaceHeight = 0.05' in pavement_text, "pavement surface height mismatch")
    require('custom double cbnu:slabBottom = -0.12' in pavement_text, "pavement slab bottom mismatch")
    require('prepend references = @../../materials/exterior/sidewalk_pavers.usda@' in pavement_text, "sidewalk material reference missing")
    require(set(re.findall(r'def Mesh "([^"]+)"', pavement_text)) == {"SouthEntrancePavement", "NorthExitPavement"}, "exterior pavement mesh set mismatch")
    require("PhysicsCollisionAPI" not in pavement_text, "exterior visual pavement must not add collision")
    for mesh_name in ("SouthEntrancePavement", "NorthExitPavement"):
        validate_mesh_topology(pavement_text, mesh_name)
        points = mesh_points(pavement_text, mesh_name)
        require(len(points) == 8, f"pavement must be a closed slab: {mesh_name}")
        require({point[2] for point in points} == {0.05, -0.12}, f"pavement height mismatch: {mesh_name}")
        validate_watertight_mesh(pavement_text, mesh_name)
        require('rel material:binding = </ExteriorSidewalkPavers/Materials/SidewalkPavers>' in prim_block(pavement_text, mesh_name), f"paver material binding missing: {mesh_name}")
        require('uniform token primvars:st:interpolation = "vertex"' in prim_block(pavement_text, mesh_name), f"paver UV interpolation missing: {mesh_name}")
        require('token purpose = "render"' in prim_block(pavement_text, mesh_name), f"pavement render purpose missing: {mesh_name}")
    south_points = mesh_points(pavement_text, "SouthEntrancePavement")
    require(min(point[0] for point in south_points) <= -80 and max(point[0] for point in south_points) >= 120, "south pavement does not cover the expanded entrance plaza")
    require(min(point[1] for point in south_points) <= -100 and max(point[1] for point in south_points) >= 0.0435, "south pavement depth coverage mismatch")
    north_points = mesh_points(pavement_text, "NorthExitPavement")
    require(min(point[0] for point in north_points) <= -80 and max(point[0] for point in north_points) >= 120, "north pavement width coverage mismatch")
    require(min(point[1] for point in north_points) <= 20.7246 and max(point[1] for point in north_points) >= 100, "north pavement depth coverage mismatch")

    require(SIDEWALK_TEXTURE.exists(), "sidewalk paver texture missing")
    require(png_size(SIDEWALK_TEXTURE) == (1254, 1254), "unexpected sidewalk texture size")
    require(SIDEWALK_NORMAL_TEXTURE.exists(), "sidewalk paver normal texture missing")
    require(png_size(SIDEWALK_NORMAL_TEXTURE) == (1254, 1254), "unexpected sidewalk normal texture size")
    require(SIDEWALK_ROUGHNESS_TEXTURE.exists(), "sidewalk paver roughness texture missing")
    require(png_size(SIDEWALK_ROUGHNESS_TEXTURE) == (1254, 1254), "unexpected sidewalk roughness texture size")
    material_text = SIDEWALK_MATERIAL.read_text(encoding="utf-8")
    require('custom string cbnu:finish = "matte outdoor concrete sidewalk pavers"' in material_text, "sidewalk material finish metadata missing")
    require('asset inputs:file = @./textures/campus_sidewalk_pavers_basecolor.png@' in material_text, "sidewalk texture reference missing")
    require('float inputs:opacity = 1' in material_text, "sidewalk must be opaque enough to hide the viewport grid")
    require('custom string cbnu:pattern = "reference-matched pale-gray rectangular running-bond paving blocks"' in material_text, "sidewalk reference style metadata missing")
    require('float inputs:roughness.connect = </SidewalkPavers/PaverRoughness.outputs:r>' in material_text, "sidewalk roughness binding missing")
    require('normal3f inputs:normal.connect = </SidewalkPavers/PaverNormal.outputs:rgb>' in material_text, "sidewalk normal binding missing")
    require('asset inputs:file = @./textures/campus_sidewalk_pavers_normal.png@' in material_text, "sidewalk normal texture reference missing")
    require('asset inputs:file = @./textures/campus_sidewalk_pavers_roughness.png@' in material_text, "sidewalk roughness texture reference missing")
    require('token inputs:sourceColorSpace = "raw"' in prim_block(material_text, "PaverNormal"), "sidewalk normal map must use raw color space")
    require('float2 inputs:scale = (0.5, 0.5)' in material_text, "sidewalk texture repeat mismatch")
def validate_doors() -> Counter[str]:
    doors = json.loads(DOORS.read_text(encoding="utf-8"))["doors"]
    counts = Counter(item["type"] for item in doors)
    require(counts == Counter({"single": 4, "double": 4, "double_glass_pair": 1}), f"unexpected door counts: {counts}")
    doors_by_name = {item["name"]: item for item in doors}
    require(doors_by_name["Door_Single_01"]["position"] == [5.4, 13.0175, 0.0], "north west-corridor door pose mismatch")
    require(doors_by_name["Door_Single_02"]["position"] == [5.4, 11.5325, 0.0], "south west-corridor door pose mismatch")
    require(doors_by_name["Door_Single_02"]["yaw_deg"] == 180, "south west-corridor door must face inward")
    require(doors_by_name["Door_Single_03"]["position"] == [10.5, 13.0175, 0.0], "second north west-corridor door pose mismatch")
    require(
        doors_by_name["Door_Single_04"]["position"] == [30.62, 3.14695, 0.0]
        and doors_by_name["Door_Single_04"]["yaw_deg"] == 270,
        "entrance-right Wall_11 single door pose mismatch",
    )
    require(
        all(
            doors_by_name[name].get("asset_variant") == "white_wood_portal"
            for name in ("Door_Double_03", "Door_Double_04")
        ),
        "east double doors must use the white-door wood-portal variant",
    )
    require(
        all(
            doors_by_name[name].get("asset_variant") is None
            for name in ("Door_Double_01", "Door_Double_02")
        ),
        "west double doors must retain the standard wood variant",
    )
    single = (ROOT / "assets/architecture/doors/wood_door_single.usda").read_text(encoding="utf-8")
    double = (ROOT / "assets/architecture/doors/wood_door_double.usda").read_text(encoding="utf-8")
    require('"DoorLeaf"' in single, "single door leaf missing")
    require('"LeftDoor"' in double and '"RightDoor"' in double, "double door must contain two leaves")
    require(EAST_WHITE_DOUBLE_DOOR_ASSET.exists(), "east white double-door asset missing")
    east_double = EAST_WHITE_DOUBLE_DOOR_ASSET.read_text(encoding="utf-8")
    require('custom string cbnu:doorLeafFinish = "warm white opaque double door"' in east_double, "east door white finish metadata missing")
    require('custom string cbnu:portalSurround = "three-sided honey-brown wood portal"' in east_double, "east door wood portal metadata missing")
    require('custom double3 cbnu:portalOuterSize = (2.22, 0.20, 2.55)' in east_double, "east door portal size mismatch")
    require(east_double.count('rel material:binding = </WhiteDoubleDoorWoodPortal/Materials/WhiteDoor>') == 2, "east door leaf white-material bindings mismatch")
    require('(0.91, 0.92, 0.89)' in east_double, "east double-door white color mismatch")
    require('(0.52, 0.27, 0.09)' in east_double, "east double-door portal wood color mismatch")
    for portal_part in ("LeftPortalJamb", "RightPortalJamb", "PortalHeader"):
        require(f'def Cube "{portal_part}"' in east_double, f"east door wood portal part missing: {portal_part}")
    require(east_double.count('def Cylinder "PullHandle"') == 2, "east double-door pull handles mismatch")
    require("PhysicsCollisionAPI" not in east_double, "east decorative door overlay must reuse Wall_01 collision")
    glass = (ROOT / "assets/architecture/doors/glass_door_double.usda").read_text(encoding="utf-8")
    require('custom int cbnu:doorLeafCount = 2' in glass, "glass door leaf count missing")
    require('def Xform "LeftDoor"' in glass and 'def Xform "RightDoor"' in glass, "glass door must contain two leaves")
    require(glass.count('def Cube "GlassPanel"') == 2, "glass door must contain two glass panels")
    require('custom string cbnu:glassFinish = "clear architectural glass"' in glass, "glass door clear finish metadata missing")
    require('custom bool cbnu:leafGlassFullyInfilled = true' in glass, "door leaf glass infill flag missing")
    require('float inputs:opacity = 0.16' in glass, "glass door clear opacity missing")
    require('float inputs:roughness = 0.08' in glass, "glass door clear roughness missing")
    require('float inputs:opacityThreshold = 0' in glass, "glass blend threshold missing")
    require(glass.count('def Cube "MidRail"') == 2, "glass door visual mid rails missing")
    require(glass.count('double3 xformOp:scale = (0.67, 0.012, 1.83)') == 2, "door leaf glass does not fill rail opening")
    require('double3 xformOp:translate = (-0.435, 0, 1.095)' in glass, "left leaf glass infill pose mismatch")
    require('double3 xformOp:translate = (0.435, 0, 1.095)' in glass, "right leaf glass infill pose mismatch")
    pair = (ROOT / "assets/architecture/doors/glass_door_double_pair.usda").read_text(encoding="utf-8")
    require('custom int cbnu:doubleDoorSetCount = 2' in pair, "two double-glass sets are required")
    require('custom string cbnu:glassFinish = "clear architectural glass"' in pair, "paired glass clear finish metadata missing")
    require('float inputs:opacity = 0.16' in pair, "central glass clear opacity missing")
    require('float inputs:roughness = 0.08' in pair, "central glass clear roughness missing")
    require('custom int cbnu:doorLeafCount = 4' in pair, "double-glass pair must contain four leaves")
    require('custom double cbnu:gapBetweenSets = 0.44' in pair, "double-glass set gap mismatch")
    require('custom bool cbnu:centralGlassInfill = true' in pair, "central fixed glass infill flag missing")
    require('custom double cbnu:centralGlassInfillWidth = 0.44' in pair, "central fixed glass infill width mismatch")
    require('custom bool cbnu:perimeterGapsClosed = true' in pair, "entrance glass closure flag missing")
    require('custom bool cbnu:centralGlassMeetsTransom = true' in pair, "central glass/transom closure flag missing")
    require('def Xform "CentralGlassInfill"' in pair, "central fixed glass infill prim missing")
    require('double3 xformOp:scale = (0.44, 0.012, 2.22)' in pair, "central fixed glass panel does not meet transom")
    require('double3 xformOp:translate = (0, 0, 1.11)' in pair, "central fixed glass vertical pose mismatch")
    require('custom bool cbnu:upperGlassTransom = true' in pair, "upper glass transom flag missing")
    require('custom double2 cbnu:upperGlassTransomSize = (4.16, 0.72)' in pair, "upper glass transom size metadata mismatch")
    require('def Xform "UpperGlassTransom"' in pair, "upper glass transom prim missing")
    require('double3 xformOp:scale = (4.16, 0.012, 0.72)' in pair, "upper transom glass size mismatch")
    require('double3 xformOp:translate = (0, 0, 2.58)' in pair, "upper transom glass pose mismatch")
    require('double3 xformOp:translate = (0, 0, 2.96)' in pair, "upper transom top rail must meet ceiling")
    require(pair.count('references = @./glass_door_double.usda@') == 2, "double-glass pair references missing")
    require('def Xform "DoubleDoorSet_01"' in pair and 'def Xform "DoubleDoorSet_02"' in pair, "double-glass set prims missing")
    require('double3 xformOp:translate = (-1.15, 0, 0)' in pair, "left glass set spacing mismatch")
    require('double3 xformOp:translate = (1.15, 0, 0)' in pair, "right glass set spacing mismatch")
    layout = (WORLD_DIR / "config/doors_layout.usda").read_text(encoding="utf-8")
    require(layout.count('double3 xformOp:translate = (5.4, 13.0175, 0)') == 1, "north west door layout mismatch")
    require('double3 xformOp:translate = (5.4, 11.5325, 0)' in layout, "south west door layout mismatch")
    require('double xformOp:rotateZ = 180' in prim_block(layout, "Door_Single_02"), "south west door layout orientation mismatch")
    require('double3 xformOp:translate = (10.5, 13.0175, 0)' in layout, "second north west door layout mismatch")
    require(
        'double3 xformOp:translate = (30.62, 3.14695, 0)' in layout
        and 'double xformOp:rotateZ = 270' in prim_block(layout, "Door_Single_04"),
        "entrance-right Wall_11 single door layout mismatch",
    )
    for name, expected_y in (("Door_Double_03", 12.3), ("Door_Double_04", 8.05)):
        block = prim_block(layout, name)
        require('custom string cbnu:assetVariant = "white_wood_portal"' in block, f"east door layout variant mismatch: {name}")
        require(f"double3 xformOp:translate = (35.32, {expected_y}, 0)" in block, f"east door layout pose mismatch: {name}")
        require("double xformOp:rotateZ = 90" in block, f"east door layout yaw mismatch: {name}")
    require(layout.count("white_door_double_wood_portal.usda@") == 2, "east white double-door reference count mismatch")
    require(layout.count("wood_door_double.usda@") == 2, "standard wood double-door reference count mismatch")
    glass_block = prim_block(layout, "Door_Double_05")
    require("glass_door_double_pair.usda" in layout and 'cbnu:doorType = "double_glass_pair"' in glass_block, "front double-glass pair reference missing")
    return counts


def validate_sofas() -> tuple[Counter[str], Counter[str], Counter[str], Counter[str]]:
    furniture = json.loads(FURNITURE.read_text(encoding="utf-8"))
    sofas = furniture["sofas"]
    fixtures = furniture.get("fixtures", [])
    type_counts = Counter(item["type"] for item in sofas)
    placement_counts = Counter(item["placement"] for item in sofas)
    facing_counts = Counter(item["facing"] for item in sofas)
    fixture_counts = Counter(item["type"] for item in fixtures)
    require(type_counts == Counter({"straight": 3, "corner": 1, "u_column": 1}), f"unexpected sofa types: {type_counts}")
    require(placement_counts == Counter({"wall_attached": 4, "column_attached": 1}), f"unexpected placements: {placement_counts}")
    require(facing_counts == Counter({"lobby": 4, "outward": 1}), f"unexpected facing values: {facing_counts}")
    require(
        fixture_counts == Counter({"lobby_table_filled": 3, "atm": 2}),
        f"unexpected fixture types: {fixture_counts}",
    )

    # The four perimeter sofas touch their nearest wall at the outermost asset
    # edge. The Column 2 U sofa is the sole structural exception: it remains
    # attached to the column so the required open-top wrap is preserved.
    expected_wall_attached_positions = {
        "Sofa_02": (35.0392, 10.2174),
        "Sofa_03": (17.7101, 0.4535),
        "Sofa_05": (29.1159, 0.4535),
        "Sofa_Corner_01": (30.3436, 6.5839),
    }
    sofas_by_name = {item["name"]: item for item in sofas}
    require(
        {name for name, sofa in sofas_by_name.items() if sofa.get("material_variant") == "dark_reddish_brown_leather"}
        == {"Sofa_Corner_01", "Sofa_U_Column_02"},
        "dark reddish-brown leather sofa assignment mismatch",
    )
    require(
        {name for name, sofa in sofas_by_name.items() if sofa.get("material_variant") == "brown_leather"}
        == {"Sofa_02", "Sofa_03", "Sofa_05"},
        "brown leather sofa assignment mismatch",
    )
    for name, expected_position in expected_wall_attached_positions.items():
        actual_position = tuple(float(value) for value in sofas_by_name[name]["position"][:2])
        require(
            all(abs(actual - expected) < 1e-6 for actual, expected in zip(actual_position, expected_position)),
            f"wall contact position mismatch: {name}: {actual_position}",
        )
    require(sofas_by_name["Sofa_02"]["yaw_deg"] == 270, "Sofa_02 must face west into the lobby")
    require(
        abs(float(sofas_by_name["Sofa_02"]["length_scale"]) - 1.11595) < 1e-9,
        "Sofa_02 must retain its original 2.2319 m width",
    )
    require(
        abs(float(sofas_by_name["Sofa_Corner_01"]["return_length_m"]) - 2.71) < 1e-9,
        "Sofa_Corner_01 Wall_11 return must be shortened to 2.71 m",
    )
    doors_by_name = {
        item["name"]: item
        for item in json.loads(DOORS.read_text(encoding="utf-8"))["doors"]
    }
    fixtures_by_name = {item["name"]: item for item in fixtures}
    table_02 = fixtures_by_name["Table_02"]
    table_half_depth = 1.36 / 2
    single_half_width = 1.06 / 2
    table_north_edge = float(table_02["position"][1]) + table_half_depth
    single_center_y = float(doors_by_name["Door_Single_04"]["position"][1])
    single_south_edge = single_center_y - single_half_width
    single_north_edge = single_center_y + single_half_width
    corner_return_south_edge = (
        float(sofas_by_name["Sofa_Corner_01"]["position"][1])
        - float(sofas_by_name["Sofa_Corner_01"]["return_length_m"])
    )
    require(
        abs(single_south_edge - table_north_edge - 0.19695) < 1e-9
        and abs(corner_return_south_edge - single_north_edge - 0.19695) < 1e-9,
        "Wall_11 door must retain about 0.197 m clearance to Table_02 and the corner sofa",
    )

    require("Sofa_04" not in sofas_by_name, "former single sofa must be replaced by an ATM")
    atm = fixtures_by_name.get("ATM_01")
    require(atm is not None and atm["type"] == "atm", "ATM_01 fixture missing")
    require(atm["position"] == [19.9275, 0.4535, 0.0] and atm["yaw_deg"] == 180, "ATM_01 pose mismatch")
    atm_02 = fixtures_by_name.get("ATM_02")
    require(atm_02 is not None and atm_02["type"] == "atm", "ATM_02 fixture missing")
    require(
        atm_02["position"] == [34.15, 6.5839, 0.0] and atm_02["yaw_deg"] == 180,
        "ATM_02 pose mismatch",
    )
    require(atm_02["placement"] == "wall_attached" and atm_02["facing"] == "lobby", "ATM_02 orientation mismatch")
    require(ATM_ASSET.exists(), "ATM asset missing")
    atm_text = ATM_ASSET.read_text(encoding="utf-8")
    for part in ("MainBody", "BankHeader", "Screen", "KeypadPanel", "CardSlot", "CashSlot"):
        require(f'"{part}"' in atm_text, f"ATM part missing: {part}")

    require(TABLE_ASSET.exists(), "lobby table asset missing")
    table_text = TABLE_ASSET.read_text(encoding="utf-8")
    for part in ("Tabletop", "LegFrontLeft", "LegFrontRight", "LegBackLeft", "LegBackRight"):
        require(f'"{part}"' in table_text, f"lobby table part missing: {part}")
    require(FILLED_TABLE_ASSET.exists(), "filled lobby table asset missing")
    filled_table_text = FILLED_TABLE_ASSET.read_text(encoding="utf-8")
    require('prepend references = @./lobby_table.usda@' in filled_table_text, "filled table base reference missing")
    require('def Cube "FilledBase"' in filled_table_text, "filled table lower body missing")
    require('custom bool cbnu:hasFilledLowerBody = true' in filled_table_text, "filled table metadata missing")
    expected_table_pairs = {
        "Table_01": ("Sofa_03", [17.7101, 1.74, 0.0]),
        "Table_02": ("Sofa_05", [29.1159, 1.74, 0.0]),
    }
    for table_name, (sofa_name, position) in expected_table_pairs.items():
        table = fixtures_by_name.get(table_name)
        require(table is not None and table["type"] == "lobby_table_filled", f"filled table missing: {table_name}")
        require(table["position"] == position, f"table pose mismatch: {table_name}")
        require(table.get("paired_with") == sofa_name, f"table/sofa pairing mismatch: {table_name}")
        require(
            abs(float(table["length_scale"]) - float(sofas_by_name[sofa_name]["length_scale"])) < 1e-9,
            f"table width does not match sofa: {table_name}",
        )
    replacement_table = fixtures_by_name.get("Table_03")
    require(replacement_table is not None, "Sofa_01 replacement table missing")
    require(replacement_table["type"] == "lobby_table_filled", "Table_03 must use the filled-base asset")
    require("Sofa_01" not in sofas_by_name, "Sofa_01 must be replaced by Table_03")
    require(replacement_table["position"] == [16.4245, 6.3188, 0.0], "Table_03 pose mismatch")
    require(replacement_table["yaw_deg"] == 90, "Table_03 yaw mismatch")
    require(abs(2.0 * float(replacement_table["length_scale"]) - 1.6232) < 1e-6, "Table_03 width mismatch")
    require(abs(1.36 * float(replacement_table["depth_scale"]) - 0.82) < 1e-6, "Table_03 depth mismatch")
    require(replacement_table["placement"] == "wall_attached", "Table_03 must remain wall attached")
    layout_text = FURNITURE_LAYOUT.read_text(encoding="utf-8")
    require(layout_text.count('custom string cbnu:materialVariant = "dark_reddish_brown_leather"') == 2, "furniture layout dark reddish-brown leather assignment mismatch")
    require(layout_text.count('custom string cbnu:materialVariant = "brown_leather"') == 3, "furniture layout brown leather assignment mismatch")
    require(
        'def Xform "ATM_01"' in layout_text
        and 'def Xform "ATM_02"' in layout_text
        and 'def Xform "Sofa_04"' not in layout_text,
        "ATM layout placement missing",
    )
    require(layout_text.count('references = @../../../assets/equipment/atm_machine.usda@') == 2, "ATM reference count mismatch")
    require(layout_text.count('references = @../../../assets/furniture/lobby_table.usda@') == 0, "standard open-base table remains in layout")
    require(layout_text.count('references = @../../../assets/furniture/lobby_table_filled.usda@') == 3, "filled table references missing from layout")
    require('custom double cbnu:depth = 1.36' in table_text, "lobby table depth must be doubled to 1.36 m")

    require(COMMON_SOFA_MATERIAL.exists(), "common brown sofa material missing")
    material_text = COMMON_SOFA_MATERIAL.read_text(encoding="utf-8")
    require('custom string cbnu:finish = "soft matte brown upholstery"' in material_text, "soft upholstery material metadata missing")
    require('float inputs:roughness = 0.58' in material_text, "sofa base upholstery is too glossy")
    require('float inputs:roughness = 0.64' in material_text, "sofa cushion upholstery is too glossy")
    for material_name in ("BrownLeather", "BrownLeatherHighlight", "BrownPiping"):
        require(f'def Material "{material_name}"' in material_text, f"material missing: {material_name}")

    require(DARK_REDDISH_BROWN_SOFA_MATERIAL.exists(), "dark reddish-brown leather sofa material missing")
    accent_material_text = DARK_REDDISH_BROWN_SOFA_MATERIAL.read_text(encoding="utf-8")
    require('custom string cbnu:finish = "blackened charcoal-gray leather with a subtle reddish-brown undertone"' in accent_material_text, "blackened charcoal reddish-brown leather finish metadata missing")
    require('color3f inputs:diffuseColor = (0.09, 0.055, 0.05)' in accent_material_text, "blackened charcoal reddish-brown leather color mismatch")
    require('float inputs:roughness = 0.38' in accent_material_text, "dark reddish-brown leather roughness mismatch")
    require('float inputs:clearcoat = 0.14' in accent_material_text, "dark reddish-brown leather clearcoat mismatch")

    required_parts = {
        "straight": ("BaseUpholsteryUnified", "SeatCushionContinuous", "BackCushionContinuous"),
        "single": ("BaseUpholsteryUnified", "SeatCushion", "BackCushion"),
        "corner": ("SofaUnified",),
        "u_column": (
            "LeftBench", "RightBench", "BottomBench",
            "LeftBackSupport", "RightBackSupport", "BottomBackSupport",
            "SofaUnified",
            "LeftFrontFoot", "RightFrontFoot", "BottomLeftFoot", "BottomRightFoot",
        ),
    }
    for sofa_type, asset in SOFA_ASSETS.items():
        text = asset.read_text(encoding="utf-8")
        require("@../materials/furniture/brown_sofa_material.usda@" in text, f"brown material reference missing: {asset.name}")
        if sofa_type in {"corner", "u_column"}:
            require("@../materials/furniture/dark_reddish_brown_leather_material.usda@" in text, f"dark reddish-brown leather material reference missing: {asset.name}")
            require(
                'def Mesh "SofaUnified" (\n        prepend apiSchemas = ["MaterialBindingAPI"]\n    )'
                in text,
                f"dark reddish-brown leather mesh material API missing: {asset.name}",
            )
            root_prim = "SofaCorner" if sofa_type == "corner" else "SofaU"
            require(
                f"rel material:binding = </{root_prim}/DarkReddishBrownLeather>" in prim_block(text, "SofaUnified"),
                f"dark reddish-brown leather binding missing from visible mesh: {asset.name}",
            )
            require(
                "float3[] primvars:displayColor = [(0.09, 0.055, 0.05)]" in prim_block(text, "SofaUnified"),
                f"blackened charcoal reddish-brown leather fallback color missing: {asset.name}",
            )
        require("NavyFabric" not in text and "CharcoalFabric" not in text, f"legacy non-brown material remains: {asset.name}")
        require("custom bool cbnu:hasArmrests = false" in text, f"armless metadata missing: {asset.name}")
        require("custom string cbnu:cushionStyle" in text and "soft" in text, f"soft cushion metadata missing: {asset.name}")
        require(not re.search(r'def\s+\w+\s+"[^"]*Arm[^"]*"', text), f"armrest prim remains: {asset.name}")
        for part in required_parts[sofa_type]:
            require(f'"{part}"' in text, f"sofa part missing: {asset.name}: {part}")

    for sofa_type in ("straight", "single"):
        linear_text = SOFA_ASSETS[sofa_type].read_text(encoding="utf-8")
        require(
            'custom string cbnu:surfaceConstruction = "single continuous base, seat and back surfaces"' in linear_text,
            f"continuous-surface metadata missing: {sofa_type}",
        )
        for hidden_name in ("UpholsteredBase", "BackSupport"):
            require(
                'visibility = "invisible"' in prim_block(linear_text, hidden_name),
                f"legacy linear module remains visible: {sofa_type}: {hidden_name}",
            )
        require("double radius = 0.18" in linear_text, f"plush cushion radius missing: {sofa_type}")
        require("double xformOp:rotateX = -7" in linear_text, f"soft backrest recline missing: {sofa_type}")

    corner_text = SOFA_ASSETS["corner"].read_text(encoding="utf-8")
    require('custom string cbnu:furnitureType = "continuous armless L-shaped dark reddish-brown leather bench sofa"' in corner_text, "corner sofa dark reddish-brown leather metadata missing")
    require("custom bool cbnu:continuousJunctions = true" in corner_text, "corner sofa continuous-junction metadata missing")
    require("custom double cbnu:returnLength = 2.71" in corner_text, "corner sofa return length metadata mismatch")
    require("custom double cbnu:returnTrim = 0.30" in corner_text, "corner sofa return trim metadata mismatch")
    require(
        'custom string cbnu:surfaceConstruction = "one beveled SofaUnified render mesh with non-overlapping base, seat and back topology"' in corner_text,
        "corner unified render-mesh metadata missing",
    )
    validate_unified_sofa_render_policy(corner_text, "sofa_corner.usda")
    corner_points = mesh_points(corner_text, "SofaUnified")
    require(
        abs(min(point[1] for point in corner_points) + 2.71) < 1e-6,
        "corner sofa visible return was not shortened to 2.71 m",
    )
    require(
        "double3 xformOp:scale = (0.82, 2.71, 0.34)" in prim_block(corner_text, "ReturnBase")
        and "double3 xformOp:scale = (0.16, 3.12, 0.72)" in prim_block(corner_text, "ReturnBack"),
        "corner sofa shortened collision proxies mismatch",
    )
    require(
        max(point[2] for point in corner_points if abs(point[1]) < 1e-6 and point[0] <= 0.41) <= 0.58,
        "corner sofa return-end backrest still protrudes",
    )
    for plush_name in (
        "LongSeatPlush", "ReturnSeatPlush", "SeatPlushJunction",
        "LongBackPlush", "ReturnBackPlush", "BackPlushJunction",
    ):
        require('visibility = "invisible"' in prim_block(corner_text, plush_name), f"legacy corner plush remains visible: {plush_name}")
    for hidden_name in (
        "CornerBase", "LongBase", "ReturnBase", "LongBack", "ReturnBack",
        "LongSeatContinuous", "ReturnSeatContinuous",
        "LongBackCushionContinuous", "ReturnBackCushionContinuous",
        "SeatCornerBlend", "BackCornerBlend",
    ):
        require('visibility = "invisible"' in prim_block(corner_text, hidden_name), f"legacy corner module remains visible: {hidden_name}")

    u_text = SOFA_ASSETS["u_column"].read_text(encoding="utf-8")
    require('custom string cbnu:furnitureType = "continuous armless open-top U-shaped dark reddish-brown leather cushion sofa"' in u_text, "U sofa dark reddish-brown leather metadata missing")
    require("custom bool cbnu:continuousJunctions = true" in u_text, "U sofa continuous-junction metadata missing")
    require(
        'custom string cbnu:surfaceConstruction = "one beveled SofaUnified render mesh with non-overlapping base, seat and back topology"' in u_text,
        "U unified render-mesh metadata missing",
    )
    require("custom double cbnu:columnClearance = 0" in u_text, "U sofa must touch Column_02")
    require("custom double cbnu:columnWidth = 1.2" in u_text, "U sofa column width metadata mismatch")
    validate_unified_sofa_render_policy(u_text, "sofa_u_around_2m_column.usda")
    for plush_name in (
        "LeftSeatPlush", "RightSeatPlush", "BottomSeatPlush",
        "LeftSeatPlushJunction", "RightSeatPlushJunction",
        "LeftBackPlush", "RightBackPlush", "BottomBackPlush",
        "LeftBackPlushJunction", "RightBackPlushJunction",
    ):
        require('visibility = "invisible"' in prim_block(u_text, plush_name), f"legacy U plush remains visible: {plush_name}")
    for hidden_name in (
        "LeftBench", "RightBench", "BottomBench",
        "LeftSeatCushion", "RightSeatCushion", "BottomSeatCushion",
        "LeftBackSupport", "RightBackSupport", "BottomBackSupport",
        "LeftBackCushion", "RightBackCushion", "BottomBackCushion",
        "LeftSeatCornerBlend", "RightSeatCornerBlend",
        "LeftBackCornerBlend", "RightBackCornerBlend",
        "LeftSeatFrontPiping", "RightSeatFrontPiping", "BottomSeatFrontPiping",
    ):
        require('visibility = "invisible"' in prim_block(u_text, hidden_name), f"legacy U module remains visible: {hidden_name}")
    require('"TopBar"' not in u_text, "U sofa must stay open at local +Y")
    require('double3 xformOp:translate = (-0.990000, -0.450000, 0.230000)' in u_text, "U sofa left base pose mismatch")
    require('double3 xformOp:translate = (0.990000, -0.450000, 0.230000)' in u_text, "U sofa right base pose mismatch")
    require('double3 xformOp:translate = (0, -1.050000, 0.230000)' in u_text, "U sofa bottom base pose mismatch")
    for contact_point in (
        "(0.6000, 0.3000, 0.4250)", "(-0.6000, 0.3000, 0.4250)",
        "(0.4400, -0.6000, 0.4250)", "(-0.4400, -0.6000, 0.4250)",
    ):
        require(contact_point in u_text, f"U sofa/column contact point missing: {contact_point}")
    sofa_points = mesh_points(u_text, "SofaUnified")
    require(max(point[2] for point in sofa_points if abs(point[1] - 0.6) < 1e-6) <= 0.58, "U sofa open-end backrest still protrudes")
    require(u_text.count('def Cylinder "') == 6, "U sofa helper-foot count changed")
    return type_counts, placement_counts, facing_counts, fixture_counts


def validate_dynamic_obstacles() -> tuple[int, int, int, float]:
    config = json.loads(DYNAMIC_OBSTACLES_CONFIG.read_text(encoding="utf-8"))
    groups = config.get("groups", [])
    boxes = config.get("boxes", [])
    groups_by_name = {group["name"]: group for group in groups}
    require(
        set(groups_by_name)
        == {
            "ParcelPile_Table_03",
            "ParcelCluster_MainEntrance",
            "ParcelCluster_BetweenElevators",
        },
        "dynamic parcel group set mismatch",
    )
    table_group = groups_by_name["ParcelPile_Table_03"]
    entrance_group = groups_by_name["ParcelCluster_MainEntrance"]
    elevator_group = groups_by_name["ParcelCluster_BetweenElevators"]
    require(table_group.get("reference_prim") == "Table_03", "parcel pile must reference Table_03")
    require(table_group.get("placement") == "in_front_of_table", "parcel pile placement mismatch")
    require(table_group.get("front_direction") == "+X", "Table_03 parcel pile must face +X")
    require(table_group.get("minimum_clearance_m") == 0.6, "parcel pile clearance target must be 0.60 m")
    require(entrance_group.get("reference_prim") == "Door_Double_05", "entrance parcels must reference Door_Double_05")
    require(entrance_group.get("placement") == "inside_main_entrance_right", "entrance parcel placement mismatch")
    require(entrance_group.get("clear_path_x_max") == 24.4, "entrance clear-path boundary mismatch")
    require(elevator_group.get("reference_prim") == "Wall_05", "between-elevator parcels must reference Wall_05")
    require(elevator_group.get("placement") == "between_elevator_bays_west_wall", "between-elevator parcel placement mismatch")
    require(elevator_group.get("clear_path_x_min") == 23.65, "between-elevator clear-path boundary mismatch")
    require(config.get("starts_asleep") is True, "parcel boxes must start asleep for stable loading")
    require(len(boxes) == 16, f"expected 16 parcel boxes, found {len(boxes)}")

    names = [box["name"] for box in boxes]
    require(len(set(names)) == len(names), "duplicate parcel box names")
    require(all(box.get("group") in groups_by_name for box in boxes), "parcel box references unknown group")
    sizes = [tuple(float(value) for value in box["size"]) for box in boxes]
    require(len(set(sizes)) == len(sizes), "parcel box sizes must all differ")
    require(all(all(value > 0 for value in size) for size in sizes), "parcel box size must be positive")
    require(all(float(box["mass_kg"]) > 0 for box in boxes), "parcel box mass must be positive")

    table_boxes = [box for box in boxes if box["group"] == table_group["name"]]
    entrance_boxes = [box for box in boxes if box["group"] == entrance_group["name"]]
    elevator_boxes = [box for box in boxes if box["group"] == elevator_group["name"]]
    require(len(table_boxes) == 9, "Table_03 parcel pile count mismatch")
    require(len(entrance_boxes) == 4, "main entrance parcel count mismatch")
    require(len(elevator_boxes) == 3, "between-elevator parcel count mismatch")
    require(
        Counter(int(box["stack_level"]) for box in table_boxes) == Counter({1: 5, 2: 3, 3: 1}),
        "Table_03 parcel stack distribution mismatch",
    )
    require(
        Counter(int(box["stack_level"]) for box in entrance_boxes) == Counter({1: 3, 2: 1}),
        "entrance parcel stack distribution mismatch",
    )
    require(
        Counter(int(box["stack_level"]) for box in elevator_boxes) == Counter({1: 2, 2: 1}),
        "between-elevator parcel stack distribution mismatch",
    )

    def aabb_xy(box: dict[str, object]) -> tuple[float, float, float, float]:
        x, y = (float(value) for value in box["position"][:2])
        width, depth = (float(value) for value in box["size"][:2])
        yaw = math.radians(float(box["yaw_deg"]))
        half_x = abs(math.cos(yaw)) * width / 2 + abs(math.sin(yaw)) * depth / 2
        half_y = abs(math.sin(yaw)) * width / 2 + abs(math.cos(yaw)) * depth / 2
        return x - half_x, x + half_x, y - half_y, y + half_y

    furniture = json.loads(FURNITURE.read_text(encoding="utf-8"))
    table = next(item for item in furniture["fixtures"] if item["name"] == "Table_03")
    table_front_x = float(table["position"][0]) + 1.36 * float(table["depth_scale"]) / 2
    table_min_x = min(aabb_xy(box)[0] for box in table_boxes if box["support"] == "floor")
    table_clearance = table_min_x - table_front_x
    require(
        abs(table_clearance - float(table_group["minimum_clearance_m"])) <= 0.02,
        f"parcel pile clearance does not match the Table_03 target: {table_clearance}",
    )

    entrance_clear_x = float(entrance_group["clear_path_x_max"])
    require(
        all(aabb_xy(box)[0] >= entrance_clear_x for box in entrance_boxes),
        "entrance parcel enters the preserved center/left path",
    )
    right_pillar_bounds = (25.58, 26.6225, -0.01, 0.99)
    spawn_xy = (24.0, 2.5)
    for box in entrance_boxes:
        min_x, max_x, min_y, max_y = aabb_xy(box)
        overlaps_pillar = (
            min_x < right_pillar_bounds[1]
            and max_x > right_pillar_bounds[0]
            and min_y < right_pillar_bounds[3]
            and max_y > right_pillar_bounds[2]
        )
        require(not overlaps_pillar, f"entrance parcel overlaps right pillar: {box['name']}")
        dx = max(min_x - spawn_xy[0], 0.0, spawn_xy[0] - max_x)
        dy = max(min_y - spawn_xy[1], 0.0, spawn_xy[1] - max_y)
        require(math.hypot(dx, dy) >= 0.50, f"entrance parcel is too close to Spawn_South: {box['name']}")

    elevator_01_north_edge = 15.2 + 1.45 / 2
    elevator_02_south_edge = 18.8 - 1.45 / 2
    elevator_clear_x = float(elevator_group["clear_path_x_min"])
    ground_elevator_boxes = [box for box in elevator_boxes if box["support"] == "floor"]
    for box in elevator_boxes:
        min_x, max_x, min_y, max_y = aabb_xy(box)
        require(min_x > 22.8392, f"between-elevator parcel intersects Wall_05: {box['name']}")
        require(max_x < elevator_clear_x, f"between-elevator parcel enters the preserved east-side path: {box['name']}")
        require(min_y > elevator_01_north_edge, f"parcel overlaps ElevatorDoor_01: {box['name']}")
        require(max_y < elevator_02_south_edge, f"parcel overlaps ElevatorDoor_02: {box['name']}")
    first_bounds = aabb_xy(ground_elevator_boxes[0])
    second_bounds = aabb_xy(ground_elevator_boxes[1])
    require(first_bounds[3] < second_bounds[2], "between-elevator floor parcels overlap")

    by_name: dict[str, dict[str, object]] = {}
    for box in boxes:
        position = tuple(float(value) for value in box["position"])
        width, depth, height = (float(value) for value in box["size"])
        support_name = box["support"]
        if support_name == "floor":
            require(abs(position[2] - height / 2) < 1e-9, f"floor contact mismatch: {box['name']}")
            require(int(box["stack_level"]) == 1, f"floor box level mismatch: {box['name']}")
        else:
            require(support_name in by_name, f"unknown or later parcel support: {support_name}")
            support = by_name[support_name]
            require(support["group"] == box["group"], f"parcel stacks across groups: {box['name']}")
            support_position = tuple(float(value) for value in support["position"])
            support_width, support_depth, support_height = (float(value) for value in support["size"])
            expected_z = support_position[2] + support_height / 2 + height / 2
            require(abs(position[2] - expected_z) < 1e-9, f"stack contact mismatch: {box['name']}")
            require(position[:2] == support_position[:2], f"stack center mismatch: {box['name']}")
            require(int(box["stack_level"]) == int(support["stack_level"]) + 1, f"stack level mismatch: {box['name']}")
            yaw_delta = math.radians(float(box["yaw_deg"]) - float(support["yaw_deg"]))
            local_half_x = abs(math.cos(yaw_delta)) * width / 2 + abs(math.sin(yaw_delta)) * depth / 2
            local_half_y = abs(math.sin(yaw_delta)) * width / 2 + abs(math.cos(yaw_delta)) * depth / 2
            require(
                local_half_x < support_width / 2 and local_half_y < support_depth / 2,
                f"stacked box overhangs support: {box['name']}",
            )
        by_name[box["name"]] = box

    layout = DYNAMIC_OBSTACLES_LAYOUT.read_text(encoding="utf-8")
    require('defaultPrim = "DynamicObstacles"' in layout, "dynamic obstacle defaultPrim mismatch")
    require('custom int cbnu:groupCount = 3' in layout, "layout parcel group count mismatch")
    require('custom double cbnu:minimumTableClearance = 0.6' in layout, "layout table clearance metadata mismatch")
    require('custom double cbnu:entranceClearPathXMax = 24.4' in layout, "layout entrance clear-path metadata mismatch")
    require('custom double cbnu:elevatorClearPathXMin = 23.65' in layout, "layout between-elevator clear-path metadata mismatch")
    require('custom int cbnu:boxCount = 16' in layout, "layout parcel count metadata mismatch")
    require(layout.count("PhysicsRigidBodyAPI") == len(boxes), "parcel rigid-body API count mismatch")
    require(layout.count("PhysicsMassAPI") == len(boxes), "parcel mass API count mismatch")
    require(layout.count("PhysicsCollisionAPI") == len(boxes), "parcel collision API count mismatch")
    require(layout.count('bool physics:startsAsleep = true') == len(boxes), "parcel sleep-state count mismatch")
    require(layout.count('bool physics:kinematicEnabled = false') == len(boxes), "parcel kinematic-state count mismatch")
    require(layout.count('bool physics:rigidBodyEnabled = true') == len(boxes), "parcel rigid-body enable count mismatch")
    require(layout.count('def Cube "Body"') == len(boxes), "parcel collision body count mismatch")
    require(layout.count('def Cube "TopTape"') == len(boxes), "parcel top-tape count mismatch")
    require(layout.count('def Cube "FrontTape"') == len(boxes), "parcel front-tape count mismatch")
    require(layout.count('def Cube "ShippingLabel"') == len(boxes), "parcel label count mismatch")
    for material_name in (
        "CardboardKraftLight",
        "CardboardKraftMedium",
        "CardboardKraftDark",
        "PackingTape",
        "ShippingLabel",
    ):
        require(f'def Material "{material_name}"' in layout, f"parcel material missing: {material_name}")
    for box in boxes:
        require(f'def Xform "{box["name"]}" (' in layout, f"parcel layout prim missing: {box['name']}")
        require(f'custom string cbnu:group = "{box["group"]}"' in layout, f"parcel group metadata missing: {box['name']}")

    total_mass = sum(float(box["mass_kg"]) for box in boxes)
    return len(table_boxes), len(entrance_boxes), len(elevator_boxes), total_mass


def validate_architecture() -> tuple[int, int, int, int, int, int]:
    world_text = WORLD.read_text(encoding="utf-8")
    config = json.loads(ARCHITECTURE_CONFIG.read_text(encoding="utf-8"))
    display_walls = {
        item["name"]: item for item in config.get("digital_display_walls", [])
    }
    partition_walls = {
        item["name"]: item for item in config.get("partition_walls", [])
    }
    column_displays = {
        item["name"]: item for item in config.get("column_displays", [])
    }
    wall_posters = {
        item["name"]: item for item in config.get("wall_posters", [])
    }
    elevator_doors = {
        item["name"]: item for item in config.get("elevator_doors", [])
    }
    information_boards = {
        item["name"]: item for item in config.get("information_boards", [])
    }
    require(
        set(display_walls) == {"DigitalDisplayWall_01"},
        "digital display wall set mismatch",
    )
    require(set(partition_walls) == {"WoodPartition_01"}, "wood partition wall set mismatch")
    require(set(column_displays) == {"ColumnDisplay_01"}, "column display set mismatch")
    require(set(wall_posters) == {"GrayPoster_01", "GrayPoster_02"}, "wall poster set mismatch")
    require(set(elevator_doors) == {"ElevatorDoor_01", "ElevatorDoor_02"}, "elevator door set mismatch")
    require(
        set(information_boards)
        == {"GreenInformationBoard_01", "GreenInformationBoard_02", "GreenInformationBoard_03"},
        "green information board set mismatch",
    )

    wall_01 = display_walls["DigitalDisplayWall_01"]
    require(wall_01["asset_variant"] == "corner", "first display wall variant mismatch")
    require(wall_01["position"] == [25.9724, 13.2044, 0.85], "first display wall pose mismatch")
    require(wall_01["yaw_deg"] == 0, "first display wall yaw mismatch")
    require(
        [wall_01[field] for field in ("front_length", "side_length", "height", "depth")]
        == [2.5, 6.288533, 1.22, 0.3],
        "first display wall dimensions mismatch",
    )
    require(
        wall_01["front_display_count"] == 3 and wall_01["side_display_count"] == 6,
        "first display wall count mismatch",
    )
    require(
        wall_01["left_section"] == "side" and wall_01["right_section"] == "front",
        "first display wall left/right mapping mismatch",
    )

    require(
        wall_01["display_width"] == 0.62
        and wall_01["display_height"] == 0.98,
        "display wall panel dimensions mismatch",
    )
    require(
        [wall_01[field] for field in ("front_display_gap", "front_frame_end_margin")]
        == [0.07, 0.04],
        "three-display section must retain its original spacing and end margins",
    )
    require(
        [wall_01[field] for field in ("side_display_gap", "side_frame_end_margin")]
        == [0.24, 0.10],
        "six-display section gap/end-margin mismatch",
    )
    require(
        [wall_01[field] for field in ("side_display_center", "side_body_end_margin")]
        == [2.9942665, 0.5342665],
        "six-display section centering/body-margin metadata mismatch",
    )
    side_screen_span = (
        int(wall_01["side_display_count"]) * float(wall_01["display_width"])
        + (int(wall_01["side_display_count"]) - 1) * float(wall_01["side_display_gap"])
    )
    require(abs(side_screen_span - 4.92) < 1e-9, "six-display screen span mismatch")
    require(
        abs(side_screen_span + 2 * float(wall_01["side_frame_end_margin"]) - 5.12) < 1e-9,
        "six-display frame length does not preserve end margins",
    )
    side_visible_length = float(wall_01["side_length"]) - float(wall_01["depth"])
    calculated_body_margin = (side_visible_length - side_screen_span) / 2
    require(
        abs(calculated_body_margin - float(wall_01["side_body_end_margin"])) < 1e-9
        and abs(calculated_body_margin - 0.5342665) < 1e-9,
        "six-display section does not have equal 0.5342665 m gray-body margins",
    )
    require(
        wall_01["side_wordmark_text"] == "학연산공통기술연구원",
        "six-screen wall wordmark text mismatch",
    )
    require(
        [wall_01[field] for field in ("side_wordmark_width", "side_wordmark_height", "side_wordmark_bottom")]
        == [3.6, 0.38, 1.36],
        "six-screen wall wordmark placement metadata mismatch",
    )
    require(
        wall_01["side_wordmark_depth"] == 0.016
        and wall_01["side_wordmark_color"] == "black"
        and wall_01["side_wordmark_geometry"] == "extruded_mesh",
        "six-screen wall wordmark must use solid black extruded geometry",
    )
    require(
        abs(
            float(wall_01["side_wordmark_bottom"])
            - float(wall_01["height"])
            - 0.14
        ) < 1e-9
        and float(wall_01["mount_clearance"])
        + float(wall_01["side_wordmark_bottom"])
        + float(wall_01["side_wordmark_height"])
        < 3.0,
        "six-screen wall wordmark must clear the display wall and ceiling",
    )

    wood_partition = partition_walls["WoodPartition_01"]
    require(wood_partition["asset_variant"] == "full_height_wood", "wood partition variant mismatch")
    require(
        wood_partition["reference_from"] == "DigitalDisplayWall_01"
        and wood_partition["reference_to"] == "NorthCorridorEndGlassWall/RightFrame",
        "wood partition endpoint references mismatch",
    )
    require(wood_partition["position"] == [25.8224, 19.8814665, 0.0], "wood partition pose mismatch")
    require(wood_partition["yaw_deg"] == 0, "wood partition yaw mismatch")
    require(
        [wood_partition[field] for field in ("thickness", "length", "height")]
        == [0.30, 1.377067, 3.00],
        "wood partition dimensions mismatch",
    )
    require(
        abs(float(wood_partition["length"]) - 2.0656 * 2 / 3) < 1e-6,
        "wood partition length is not two-thirds of the original 2.0656 m",
    )
    require(wood_partition["facing"] == "-X_into_north_corridor", "wood partition facing mismatch")
    display_end_y = (
        float(wall_01["position"][1])
        + float(wall_01["side_length"])
        - float(wall_01["depth"])
    )
    partition_south_y = float(wood_partition["position"][1]) - float(wood_partition["length"]) / 2
    partition_north_y = float(wood_partition["position"][1]) + float(wood_partition["length"]) / 2
    north_glass_frame_south_y = 20.60 - 0.060 / 2
    require(abs(display_end_y - 19.192933) < 1e-9, "extended display-wall end coordinate mismatch")
    require(abs(partition_south_y - display_end_y) < 1e-9, "gap or overlap between display wall and wood partition")
    require(abs(partition_north_y - north_glass_frame_south_y) < 1e-9, "gap or overlap between wood partition and north glass frame")
    display_corridor_face_x = float(wall_01["position"][0]) - float(wall_01["depth"])
    partition_corridor_face_x = float(wood_partition["position"][0]) - float(wood_partition["thickness"]) / 2
    partition_wall_face_x = float(wood_partition["position"][0]) + float(wood_partition["thickness"]) / 2
    require(
        abs(partition_corridor_face_x - display_corridor_face_x) < 1e-9
        and abs(partition_wall_face_x - float(wall_01["position"][0])) < 1e-9,
        "wood partition thickness is not aligned with the display corner",
    )

    column_display = column_displays["ColumnDisplay_01"]
    require(column_display["reference_prim"] == "Column_03", "large display must mount on Column_03")
    require(column_display["position"] == [26.43765, 9.78845, 0.7], "Column_03 display pose mismatch")
    require(column_display["yaw_deg"] == 0, "Column_03 display yaw mismatch")
    require(
        [column_display[field] for field in ("width", "height", "depth")]
        == [1.0, 1.45, 0.04],
        "Column_03 display dimensions mismatch",
    )
    require(
        column_display["facing"] == "-Y_toward_main_entrance",
        "Column_03 display must face the main entrance",
    )
    geometry = json.loads(GEOMETRY.read_text(encoding="utf-8"))
    column_03 = next(item for item in geometry["columns"] if item["name"] == "Column_03")
    expected_column_display_xy = (
        float(column_03["center"][0]),
        float(column_03["center"][1]) - float(column_03["size"][1]) / 2,
    )
    require(
        all(
            abs(float(column_display["position"][axis]) - expected_column_display_xy[axis])
            < 1e-9
            for axis in (0, 1)
        ),
        "large display is not centered on the south face of Column_03",
    )
    require(
        column_display["width"] < column_03["size"][0]
        and column_display["position"][2] + column_display["height"] < column_03["size"][2],
        "large display exceeds the Column_03 face",
    )

    poster = wall_posters["GrayPoster_01"]
    require(poster["asset_variant"] == "gray_horizontal", "gray poster variant mismatch")
    require(
        poster["reference_wall"] == "Wall_11"
        and poster["reference_door"] == "Door_Single_04",
        "gray poster wall/door reference mismatch",
    )
    require(poster["position"] == [30.62, 5.0, 1.05], "gray poster pose mismatch")
    require(poster["yaw_deg"] == 270, "gray poster must face west into the lobby")
    require(
        [poster[field] for field in ("width", "height", "depth")]
        == [2.2, 1.0, 0.025],
        "gray poster dimensions mismatch",
    )
    require(
        poster["width"] / poster["height"] > 2.0,
        "gray poster must remain distinctly horizontal",
    )
    door_04 = next(
        item
        for item in json.loads(DOORS.read_text(encoding="utf-8"))["doors"]
        if item["name"] == "Door_Single_04"
    )
    door_north_edge = float(door_04["position"][1]) + 1.06 / 2
    poster_south_edge = float(poster["position"][1]) - float(poster["width"]) / 2
    poster_north_edge = float(poster["position"][1]) + float(poster["width"]) / 2
    require(
        abs(poster_south_edge - door_north_edge - 0.22305) < 1e-9,
        "gray poster must stay to the viewer's left of Door_Single_04",
    )
    require(
        poster_north_edge < 6.1739
        and float(poster["position"][2]) > 0.925
        and float(poster["position"][2]) + float(poster["height"]) < 3.0,
        "gray poster exceeds Wall_11 or overlaps the corner sofa height",
    )
    require(
        abs(float(poster["position"][2]) + float(poster["height"]) - 2.05) < 1e-9,
        "gray poster top moved while extending its bottom edge",
    )

    large_poster = wall_posters["GrayPoster_02"]
    require(large_poster["asset_variant"] == "gray_horizontal_large", "large gray poster variant mismatch")
    require(large_poster["reference_wall"] == "Wall_06", "large gray poster wall reference mismatch")
    require("reference_door" not in large_poster, "large gray poster must not reference a door")
    require(
        large_poster["return_wall"] == "Wall_05"
        and large_poster["reference_elevator"] == "ElevatorDoor_01",
        "large gray poster corner-return references mismatch",
    )
    require(large_poster["position"] == [20.5892, 13.0403, 0.85], "large gray poster pose mismatch")
    require(large_poster["yaw_deg"] == 0, "large gray poster must face south into the lobby")
    require(
        [large_poster[field] for field in ("width", "return_length", "height", "depth")]
        == [4.5, 1.3247, 1.22, 0.15],
        "large gray poster dimensions mismatch",
    )
    require(large_poster["facing"] == "-Y_into_lobby", "large gray poster facing mismatch")
    require(large_poster["return_facing"] == "+X_into_north_corridor", "large gray poster return facing mismatch")
    require(
        abs(float(large_poster["position"][0]) + float(large_poster["width"]) / 2 - 22.8392) < 1e-9,
        "large gray poster right edge moved while extending left",
    )
    elevator_01_frame_south_edge = float(elevator_doors["ElevatorDoor_01"]["position"][1]) - 1.67 / 2
    poster_return_end = float(large_poster["position"][1]) + float(large_poster["return_length"])
    require(
        abs(poster_return_end - elevator_01_frame_south_edge) < 1e-9
        and abs(poster_return_end - 14.365) < 1e-9,
        "large gray poster return does not terminate beside ElevatorDoor_01 frame",
    )

    expected_elevator_poses = {
        "ElevatorDoor_01": [22.8392, 15.2, 0.0],
        "ElevatorDoor_02": [22.8392, 18.8, 0.0],
    }
    for name, expected_position in expected_elevator_poses.items():
        elevator = elevator_doors[name]
        require(elevator["asset_variant"] == "stainless_center_opening", f"elevator variant mismatch: {name}")
        require(elevator["reference_wall"] == "Wall_05", f"elevator wall mismatch: {name}")
        require(elevator["position"] == expected_position, f"elevator pose mismatch: {name}")
        require(elevator["yaw_deg"] == 90, f"elevator yaw mismatch: {name}")
        require(
            [elevator[field] for field in ("width", "height", "depth")] == [1.45, 2.3, 0.08],
            f"elevator dimensions mismatch: {name}",
        )
        require(elevator["facing"] == "+X_into_north_corridor", f"elevator facing mismatch: {name}")
        require(
            elevator["service_state"] == "operational" and elevator["door_state"] == "closed",
            f"elevator service state mismatch: {name}",
        )
    elevator_gap = float(elevator_doors["ElevatorDoor_02"]["position"][1]) - float(elevator_doors["ElevatorDoor_01"]["position"][1])
    require(elevator_gap > 1.45, "elevator door bays overlap")
    require(abs(elevator_gap - 3.6) < 1e-9, "ElevatorDoor_02 viewer-left shift mismatch")
    require(
        all(13.1403 < float(door["position"][1]) < 20.7246 for door in elevator_doors.values()),
        "elevator door lies outside Wall_05",
    )

    expected_board_x = [23.4558, 24.4058, 25.3558]
    for index, name in enumerate(sorted(information_boards)):
        board = information_boards[name]
        require(board["asset_variant"] == "green_mobile", f"information board variant mismatch: {name}")
        require(
            board["position"] == [expected_board_x[index], 20.25, 0.15],
            f"information board pose mismatch: {name}",
        )
        require(board["yaw_deg"] == 0, f"information board yaw mismatch: {name}")
        require(
            [board[field] for field in ("width", "depth", "height")] == [0.72, 0.34, 1.55],
            f"information board dimensions mismatch: {name}",
        )
        require(
            board["facing"] == "-Y_into_north_corridor"
            and board["mounted_on"] == "NorthGlassWoodPlatform",
            f"information board platform/facing mismatch: {name}",
        )
    require(
        all(abs(expected_board_x[index + 1] - expected_board_x[index] - 0.95) < 1e-9 for index in range(2)),
        "information board center spacing mismatch",
    )
    platform_min_x = 24.4058 - 3.1332 / 2
    platform_max_x = 24.4058 + 3.1332 / 2
    require(
        abs((expected_board_x[0] - 0.72 / 2) - platform_min_x - 0.2566) < 1e-9
        and abs(platform_max_x - (expected_board_x[-1] + 0.72 / 2) - 0.2566) < 1e-9,
        "three information boards are not centered with equal platform margins",
    )
    require(20.25 - 0.34 / 2 >= 20.27 - 0.60 / 2, "information boards overhang platform south edge")
    require(20.25 + 0.34 / 2 <= 20.27 + 0.60 / 2, "information boards overhang platform north edge")

    require('def Xform "Architecture"' in world_text, "/World/Architecture missing")
    require(
        'prepend references = @config/architecture_layout.usda@' in world_text,
        "architecture layout reference missing",
    )
    layout_text = ARCHITECTURE_LAYOUT.read_text(encoding="utf-8")
    for prim_name in (
        "DigitalDisplayWall_01",
        "WoodPartition_01",
        "ColumnDisplay_01",
        "GrayPoster_01",
        "GrayPoster_02",
        "ElevatorDoor_01",
        "ElevatorDoor_02",
        "GreenInformationBoard_01",
        "GreenInformationBoard_02",
        "GreenInformationBoard_03",
    ):
        require(f'def Xform "{prim_name}"' in layout_text, f"architecture layout prim missing: {prim_name}")
    require(
        layout_text.count("digital_display_wall_corner.usda@") == 1
        and layout_text.count("digital_display_panel_large_column.usda@") == 1,
        "architecture asset reference set mismatch",
    )
    require(
        layout_text.count("full_height_wood_partition.usda@") == 1,
        "wood partition asset reference mismatch",
    )
    require(
        layout_text.count("gray_horizontal_poster.usda@") == 1
        and layout_text.count("gray_horizontal_poster_large.usda@") == 1,
        "gray poster asset reference mismatch",
    )
    require('custom string cbnu:returnWall = "Wall_05"' in layout_text, "large poster return-wall metadata missing from layout")
    require('custom string cbnu:referenceElevator = "ElevatorDoor_01"' in layout_text, "large poster elevator reference missing from layout")
    require('custom string cbnu:returnFacing = "+X_into_north_corridor"' in layout_text, "large poster return facing missing from layout")
    require('custom double cbnu:returnLength = 1.3247' in layout_text, "large poster return length missing from layout")
    require(
        layout_text.count("stainless_elevator_door.usda@") == 2,
        "elevator door asset reference mismatch",
    )
    require(
        layout_text.count("green_information_board.usda@") == 3,
        "green information board asset reference mismatch",
    )
    for pose in (
        "double3 xformOp:translate = (25.9724, 13.2044, 0.85)",
        "double3 xformOp:translate = (25.8224, 19.8814665, 0)",
        "double3 xformOp:translate = (26.43765, 9.78845, 0.7)",
        "double3 xformOp:translate = (30.62, 5, 1.05)",
        "double3 xformOp:translate = (20.5892, 13.0403, 0.85)",
        "double3 xformOp:translate = (22.8392, 15.2, 0)",
        "double3 xformOp:translate = (22.8392, 18.8, 0)",
        "double3 xformOp:translate = (23.4558, 20.25, 0.15)",
        "double3 xformOp:translate = (24.4058, 20.25, 0.15)",
        "double3 xformOp:translate = (25.3558, 20.25, 0.15)",
    ):
        require(pose in layout_text, f"architecture layout pose missing: {pose}")

    asset_text = DISPLAY_WALL_ASSET.read_text(encoding="utf-8")
    require(
        'custom string cbnu:bodyConstruction = "one watertight charcoal L-footprint mesh with a shared mitered corner"'
        in asset_text,
        "unified L body metadata missing",
    )
    require('custom double cbnu:frontLength = 2.5' in asset_text, "right/front length metadata mismatch")
    require('custom double cbnu:sideLength = 6.288533' in asset_text, "extended left/side length metadata mismatch")
    require('custom int cbnu:frontDisplayCount = 3' in asset_text, "right/front display metadata mismatch")
    require('custom int cbnu:sideDisplayCount = 6' in asset_text, "left/side display metadata mismatch")
    require('custom double cbnu:frontDisplayGap = 0.07' in asset_text, "three-display gap changed unexpectedly")
    require('custom double cbnu:frontFrameEndMargin = 0.04' in asset_text, "three-display end margin changed unexpectedly")
    require('custom double cbnu:sideDisplayGap = 0.24' in asset_text, "six-display gap mismatch")
    require('custom double cbnu:sideDisplayCenter = 2.9942665' in asset_text, "six-display center metadata mismatch")
    require('custom double cbnu:sideBodyEndMargin = 0.5342665' in asset_text, "six-display equal body margin metadata mismatch")
    require('custom double cbnu:sideFrameEndMargin = 0.1' in asset_text, "six-display frame end margin mismatch")
    require('custom double cbnu:sideFrameLength = 5.12' in asset_text, "six-display frame length mismatch")
    require('custom string cbnu:sideWordmarkText = "학연산공통기술연구원"' in asset_text, "institute wordmark metadata missing")
    require('custom double cbnu:sideWordmarkWidth = 3.6' in asset_text, "institute wordmark width mismatch")
    require('custom double cbnu:sideWordmarkHeight = 0.38' in asset_text, "institute wordmark height mismatch")
    require('@./institute_wordmark_mesh.usda@' in asset_text, "institute wordmark mesh reference missing")
    validate_mesh_topology(asset_text, "MainBody")
    validate_watertight_mesh(asset_text, "MainBody")
    body_points = mesh_points(asset_text, "MainBody")
    require(
        {(point[0], point[1]) for point in body_points}
        == {(-0.3, -0.3), (2.2, -0.3), (2.2, 0.0), (0.0, 0.0), (0.0, 5.988533), (-0.3, 5.988533)},
        "L footprint mismatch",
    )
    for name, expected_y in {
        "Display_04": 0.8442665,
        "Display_05": 1.7042665,
        "Display_06": 2.5642665,
        "Display_07": 3.4242665,
        "Display_08": 4.2842665,
        "Display_09": 5.1442665,
    }.items():
        require(
            f'double3 xformOp:translate = (-0.3, {usd_number(expected_y)}, 0)'
            in prim_block(asset_text, name),
            f"six-display spacing mismatch: {name}",
        )
    require(asset_text.count('double3 xformOp:scale = (0.025, 5.12, 0.04)') == 2, "extended side frame rails mismatch")
    require('double3 xformOp:translate = (-0.3125, 0.4142665, 0.61)' in prim_block(asset_text, "StartTrim"), "side frame start margin mismatch")
    require('double3 xformOp:translate = (-0.3125, 5.5742665, 0.61)' in prim_block(asset_text, "EndTrim"), "side frame end margin mismatch")
    require('double3 xformOp:scale = (2.5, 0.3, 1.22)' in prim_block(asset_text, "FrontCollision"), "three-display collision length changed")
    require('double3 xformOp:scale = (0.3, 6.288533, 1.22)' in prim_block(asset_text, "SideCollision"), "six-display collision length mismatch")
    require('double3 xformOp:translate = (-0.15, 2.8442665, 0.61)' in prim_block(asset_text, "SideCollision"), "six-display collision pose mismatch")
    require(asset_text.count('references = @./digital_display_panel.usda@') == 9, "first wall panel count mismatch")
    require(asset_text.count("PhysicsCollisionAPI") == 2, "first wall collision count mismatch")
    wordmark_block = prim_block(asset_text, "InstituteWordmarkText")
    require('prepend references = @./institute_wordmark_mesh.usda@' in asset_text, "visible institute wordmark asset missing")
    require('double xformOp:rotateZ = -90' in wordmark_block, "institute wordmark orientation mismatch")
    require('double3 xformOp:translate = (0, 2.9942665, 1.36)' in wordmark_block, "institute wordmark wall placement mismatch")
    require("PhysicsCollisionAPI" not in wordmark_block, "institute wordmark must not add collision")

    require(DISPLAY_WORDMARK_ASSET.exists(), "solid institute wordmark mesh asset missing")
    wordmark_asset_text = DISPLAY_WORDMARK_ASSET.read_text(encoding="utf-8")
    require('custom string cbnu:content = "학연산공통기술연구원"' in wordmark_asset_text, "solid institute wordmark content missing")
    require('custom string cbnu:construction = "solid black extruded Hangul glyph mesh"' in wordmark_asset_text, "solid institute wordmark construction mismatch")
    require('custom double cbnu:width = 3.6' in wordmark_asset_text, "solid institute wordmark width mismatch")
    require('custom double cbnu:height = 0.38' in wordmark_asset_text, "solid institute wordmark height mismatch")
    require('custom double cbnu:depth = 0.016' in wordmark_asset_text, "solid institute wordmark depth mismatch")
    run_count_match = re.search(r'custom int cbnu:glyphRunBoxCount = (\d+)', wordmark_asset_text)
    require(run_count_match is not None and int(run_count_match.group(1)) >= 100, "solid institute wordmark glyph geometry is unexpectedly sparse")
    require('color3f inputs:diffuseColor = (0.003, 0.003, 0.003)' in wordmark_asset_text, "institute wordmark is not black")
    require('rel material:binding = </InstituteWordmarkText/BlackLettering>' in wordmark_asset_text, "solid institute wordmark binding mismatch")
    require("UsdUVTexture" not in wordmark_asset_text, "solid institute wordmark must not rely on a texture")
    require("PhysicsCollisionAPI" not in wordmark_asset_text, "solid institute wordmark must not add collision")
    validate_mesh_topology(wordmark_asset_text, "GlyphMesh")
    validate_watertight_mesh(wordmark_asset_text, "GlyphMesh")

    require(WOOD_PARTITION_ASSET.exists(), "full-height wood partition asset missing")
    partition_text = WOOD_PARTITION_ASSET.read_text(encoding="utf-8")
    require('custom string cbnu:architectureType = "full-height wooden false wall"' in partition_text, "wood partition type metadata missing")
    require('custom bool cbnu:collisionEnabled = true' in partition_text, "wood partition collision metadata mismatch")
    require('custom double3 cbnu:partitionSize = (0.30, 1.377067, 3.00)' in partition_text, "wood partition size metadata mismatch")
    partition_body = prim_block(partition_text, "PartitionBody")
    require('double3 xformOp:scale = (0.30, 1.377067, 3.00)' in partition_body, "wood partition body dimensions mismatch")
    require('double3 xformOp:translate = (0, 0, 1.50)' in partition_body, "wood partition vertical pose mismatch")
    require('bool physics:collisionEnabled = true' in partition_body, "wood partition body collider is disabled")
    require(partition_text.count("PhysicsCollisionAPI") == 1, "wood partition must have exactly one collider")
    require(partition_text.count('def Cube "') == 3, "wood partition visible piece count mismatch")
    require('color3f inputs:diffuseColor = (0.34, 0.145, 0.055)' in partition_text, "wood partition panel color mismatch")
    require("PhysicsCollisionAPI" not in prim_block(partition_text, "Joint_01"), "wood partition joint must not collide")
    require("PhysicsCollisionAPI" not in prim_block(partition_text, "Joint_02"), "wood partition joint must not collide")

    panel_text = DISPLAY_PANEL_ASSET.read_text(encoding="utf-8")
    require('def Xform "Bezel"' in panel_text and 'def Cube "Screen"' in panel_text, "display panel structure missing")
    require(panel_text.count('def Cube "') == 5, "display panel must contain four bezel rails and one screen")
    require('double3 xformOp:scale = (0.58, 0.006, 0.94)' in prim_block(panel_text, "Screen"), "standard screen dimensions mismatch")

    column_text = COLUMN_DISPLAY_ASSET.read_text(encoding="utf-8")
    require('custom bool cbnu:ownCollision = false' in column_text, "column display must reuse the column collider")
    require('custom string cbnu:facing = "local -Y"' in column_text, "column display local facing mismatch")
    require('double3 xformOp:scale = (1.0, 0.04, 1.45)' in prim_block(column_text, "Backing"), "column display backing dimensions mismatch")
    require('double3 xformOp:scale = (0.92, 0.006, 1.37)' in prim_block(column_text, "Screen"), "large column screen opening mismatch")
    require(column_text.count("PhysicsCollisionAPI") == 0, "column display must not duplicate Column_03 collision")
    bezel_front = -0.045 - 0.020 / 2
    screen_front = -0.043 - 0.006 / 2
    require(abs((screen_front - bezel_front) - 0.009) < 1e-9, "large screen recess mismatch")

    poster_text = GRAY_POSTER_ASSET.read_text(encoding="utf-8")
    require('custom string cbnu:decorType = "long horizontal gray wall poster"' in poster_text, "gray poster type metadata missing")
    require('custom bool cbnu:ownCollision = false' in poster_text, "gray poster collision policy mismatch")
    require('custom string cbnu:facing = "local -Y"' in poster_text, "gray poster local facing mismatch")
    require(poster_text.count('def Cube "') == 2, "gray poster must contain backing and face only")
    require('double3 xformOp:scale = (2.2, 0.025, 1.0)' in prim_block(poster_text, "Backing"), "gray poster backing dimensions mismatch")
    require('double3 xformOp:translate = (0, 0, 0.5)' in prim_block(poster_text, "Backing"), "gray poster vertical origin mismatch")
    require('double3 xformOp:scale = (2.12, 0.006, 0.92)' in prim_block(poster_text, "PosterFace"), "gray poster face dimensions mismatch")
    require("PhysicsCollisionAPI" not in poster_text, "gray poster must not add a collider")
    require('(0.70, 0.72, 0.74)' in poster_text, "light-gray poster face material mismatch")

    large_poster_text = GRAY_POSTER_LARGE_ASSET.read_text(encoding="utf-8")
    require('custom string cbnu:decorType = "one-piece L-shaped large gray wall poster"' in large_poster_text, "large poster type metadata missing")
    require('custom int cbnu:visiblePieceCount = 1' in large_poster_text, "large poster must be one visible piece")
    require('custom bool cbnu:emissive = false' in large_poster_text, "large poster must not emit like a screen")
    require('custom bool cbnu:hasBezel = false' in large_poster_text, "large poster bezel was not removed")
    require('custom bool cbnu:hasScreen = false' in large_poster_text, "large poster screen was not removed")
    require(large_poster_text.count('def Mesh "PosterSlab"') == 1, "large poster must contain one L-shaped slab mesh")
    require(large_poster_text.count('def Cube "') == 0, "large poster retains split box geometry")
    require('custom double cbnu:depth = 0.15' in large_poster_text, "large poster doubled-depth metadata mismatch")
    require('custom double cbnu:returnLength = 1.3247' in large_poster_text, "large poster return-length metadata mismatch")
    require('custom string cbnu:returnTermination = "flush to the south outer edge of ElevatorDoor_01 frame"' in large_poster_text, "large poster return termination metadata missing")
    validate_mesh_topology(large_poster_text, "PosterSlab")
    validate_watertight_mesh(large_poster_text, "PosterSlab")
    large_poster_points = mesh_points(large_poster_text, "PosterSlab")
    require(
        {(point[0], point[1]) for point in large_poster_points}
        == {
            (-2.25, -0.075), (2.325, -0.075), (2.325, 1.3247),
            (2.175, 1.3247), (2.175, 0.075), (-2.25, 0.075),
        },
        "large poster L footprint mismatch",
    )
    require(
        min(point[2] for point in large_poster_points) == 0
        and max(point[2] for point in large_poster_points) == 1.22,
        "large poster vertical extent mismatch",
    )
    require('(0.34, 0.36, 0.38)' in large_poster_text, "large poster must use the dark-gray finish")
    require("PhysicsCollisionAPI" not in large_poster_text, "large wall poster must not add collision")

    elevator_text = ELEVATOR_DOOR_ASSET.read_text(encoding="utf-8")
    require('custom string cbnu:architectureType = "operational elevator entrance"' in elevator_text, "elevator type metadata missing")
    require('custom bool cbnu:operational = true' in elevator_text, "elevator operational metadata missing")
    require('custom string cbnu:doorMotion = "center opening"' in elevator_text, "elevator motion metadata mismatch")
    require('custom string cbnu:doorState = "closed"' in elevator_text, "elevator door state mismatch")
    require('custom bool cbnu:collisionEnabled = false' in elevator_text, "elevator overlay must reuse Wall_05 collision")
    require('double3 xformOp:scale = (0.715, 0.06, 2.30)' in prim_block(elevator_text, "LeftLeaf"), "elevator left leaf dimensions mismatch")
    require('double3 xformOp:scale = (0.715, 0.06, 2.30)' in prim_block(elevator_text, "RightLeaf"), "elevator right leaf dimensions mismatch")
    require(elevator_text.count('color3f inputs:emissiveColor') == 1, "elevator status indicator mismatch")
    require("PhysicsCollisionAPI" not in elevator_text, "elevator door asset must not duplicate wall collision")

    require(GREEN_INFORMATION_BOARD_ASSET.exists(), "green information board asset missing")
    board_text = GREEN_INFORMATION_BOARD_ASSET.read_text(encoding="utf-8")
    require(
        'custom string cbnu:architectureType = "mobile green information board"' in board_text,
        "green information board type metadata missing",
    )
    require('custom double3 cbnu:overallSize = (0.72, 0.34, 1.55)' in board_text, "information board overall size mismatch")
    require('(0.035, 0.28, 0.14)' in board_text, "information board green finish mismatch")
    require('def Cube "NoticeSheet"' in board_text, "information board notice sheet missing")
    require(board_text.count('def Sphere "Wheel_') == 4, "information board caster count mismatch")
    require(
        'def Cube "PanelBacking" (\n        prepend apiSchemas = ["MaterialBindingAPI", "PhysicsCollisionAPI"]'
        in board_text
        and "physics:collisionEnabled = true" in prim_block(board_text, "PanelBacking"),
        "information board panel collider missing",
    )
    for foot_name in ("LeftFoot", "RightFoot"):
        foot = prim_block(board_text, foot_name)
        require(
            f'def Cube "{foot_name}" (\n            prepend apiSchemas = ["MaterialBindingAPI", "PhysicsCollisionAPI"]'
            in board_text
            and "physics:collisionEnabled = true" in foot,
            f"information board foot collider missing: {foot_name}",
        )

    dark_text = DISPLAY_WALL_DARK_MATERIAL.read_text(encoding="utf-8")
    screen_text = DISPLAY_SCREEN_MATERIAL.read_text(encoding="utf-8")
    require('(0.055, 0.063, 0.072)' in dark_text and 'float inputs:roughness = 0.40' in dark_text, "charcoal wall material mismatch")
    require(screen_text.count('color3f inputs:emissiveColor') == 3, "screen emissive material variants missing")
    require(not (ROOT / "assets/materials/display_wall/display_header.usda").exists(), "removed white header material still exists")
    return (
        int(wall_01["front_display_count"]),
        int(wall_01["side_display_count"]),
        len(partition_walls),
        len(column_displays),
        len(wall_posters),
        len(elevator_doors),
    )


def main() -> None:
    validate_world()
    ceiling_light_counts = validate_ceiling()
    validate_front_glass_walls()
    validate_west_corridor_end_wall()
    validate_north_corridor_end_glass_wall()
    validate_north_corridor_wood_platform()
    validate_exterior_sidewalk_pavers()
    door_counts = validate_doors()
    type_counts, placement_counts, facing_counts, fixture_counts = validate_sofas()
    table_parcels, entrance_parcels, elevator_parcels, parcel_mass = validate_dynamic_obstacles()
    (
        front_display_count,
        side_display_count,
        partition_wall_count,
        column_display_count,
        wall_poster_count,
        elevator_door_count,
    ) = validate_architecture()
    reference_count = validate_references()
    width, height = png_size(PREVIEW)
    architecture_width, architecture_height = png_size(ARCHITECTURE_PREVIEW)

    print("CBNU Haksan detailed lobby validation: PASS")
    print(
        f"doors: single wood={door_counts['single']}, double total={door_counts['double']} "
        "(standard wood=2, east white+wood portal=2), "
        f"double glass sets={2 * door_counts['double_glass_pair']} "
        "(four clear leaves + one central clear fixed glass panel)"
    )
    print("east double-door finish: Door_Double_03/04 use warm-white leaves with three-sided honey-brown wood portals; west double doors remain brown wood")
    print(
        "sofas: total=" + str(sum(type_counts.values())) + ", "
        + ", ".join(f"{key}={type_counts[key]}" for key in ("straight", "corner", "u_column"))
    )
    print(
        f"fixtures: ATM={fixture_counts['atm']}, filled-base tables={fixture_counts['lobby_table_filled']}"
    )
    print(f"placements: wall_attached={placement_counts['wall_attached']}, column_attached={placement_counts['column_attached']}")
    print(f"facing: wall={facing_counts['wall']}, lobby={facing_counts['lobby']}, outward={facing_counts['outward']}")
    print("wall contact: 4/4 perimeter sofas flush; Table_03 replaces Sofa_01 at the west wall; U sofa attached to Column_02")
    print("sofa geometry: 4/4 armless assets use thick rounded plush cushions and soft matte upholstery")
    print("sofa junctions: corner/U each expose one beveled watertight SofaUnified mesh; all helpers hidden")
    print("table fit: all 3 use filled bases; Table_01/02 match paired sofa widths and Table_03 matches former Sofa_01 footprint (1.6232 x 0.82 m)")
    print(
        f"dynamic parcels: Table_03={table_parcels}, main entrance={entrance_parcels}, "
        f"between elevators={elevator_parcels}, distinct sizes={table_parcels + entrance_parcels + elevator_parcels}, "
        f"max stack levels=3, total mass={parcel_mass:.1f} kg; "
        "all rigid, collidable and non-kinematic"
    )
    print("main columns: 3 x 1.2 x 1.2 x 3.0 m; equal X spacing retained; all shifted 0.3 m lobbyward (-Y)")
    print("U sofa column contact: clearance=0 at x=+-0.6 m and y=-0.6 m")
    print("floor material: Bala White polished granite with visible feldspar/quartz/mica pattern, 2.4 m repeat")
    print("ceiling: corridor-matched footprint, underside=3.0 m, thickness=0.1 m, collision enabled")
    print(
        f"ceiling lights: standard panels={ceiling_light_counts['panel']}, "
        f"large central panel={ceiling_light_counts['large_panel']} (6.0 x 2.4 m)"
    )
    print(
        f"central ceiling air conditioners: {ceiling_light_counts['air_conditioner']} four-way cassette units, "
        "1.1 x 1.1 m each, mirrored beside the large light with 0.65 m clearance"
    )
    print("front entrance glazing: two 4.85 x 2.82 m clear panels with full-span lower facade walls aligned to the visible entrance-pillar plane (south face y=-0.01 m); Wall_10 collider unchanged")
    print("west corridor: width=1.73 m; opaque Wall_07 visible with collision; three wood doors realigned to wall faces")
    print("north corridor end glazing: one 3.1332 x 2.82 m clear panel with a full-width 1.02 m stone-gray lower wall; Wall_04 collider unchanged")
    print("north glass wood platform: 3.1332 x 0.60 x 0.15 m; full corridor width, flush with the glass frame, static collision enabled")
    print("north platform information boards: 3 wheeled green units, each 0.72 x 0.34 x 1.55 m; equal 0.23 m gaps and 0.2566 m platform side margins")
    print("wall corners: Wall_02/06/08/12 extended 0.10 m to close all four re-entrant half-thickness gaps")
    print("exterior pavement: south 200.0 x 100.0435 m + north 200.0 x 79.2754 m watertight opaque sidewalk-paver slabs; top z=0.05 m, bottom z=-0.12 m")
    print(
        f"digital display walls: original only, left={side_display_count}/right={front_display_count}; "
        "floating 0.85 m above floor, height=1.22 m, depth=0.30 m, panels=0.62 x 0.98 m; "
        "six-screen side extended to 6.288533 m with 0.24 m gaps and equal 0.5342665 m gray-body end margins; three-screen side unchanged"
    )
    print("six-screen wall wordmark: 학연산공통기술연구원, 3.6 x 0.38 x 0.016 m solid black extruded glyph mesh, bottom=2.21 m")
    print("display wall collision: original=2 invisible box helpers; opposite screen structure removed")
    print(
        f"wood partition walls: {partition_wall_count}; 0.30 x 1.377067 x 3.00 m (two-thirds former length), "
        "flush from the six-screen corner end at y=19.192933 m to the north glass frame at y=20.5700 m"
    )
    print(
        f"Column_03 entrance-facing displays: {column_display_count} large panel, "
        "1.0 x 1.45 m, bottom=0.70 m, no duplicate collider"
    )
    print(
        f"gray wall posters: total={wall_poster_count}; Wall_11=2.2 x 1.0 m, "
        "Wall_06/05=4.5 m main + 1.3247 m return x 1.22 x 0.15 m dark-gray one-piece L slab; "
        "return meets ElevatorDoor_01 frame, no screens, emission or colliders"
    )
    print(
        f"Wall_05 elevators: {elevator_door_count} operational stainless-steel center-opening doors; "
        "1.45 x 2.30 m each, facing +X; ElevatorDoor_02 shifted 0.20 m viewer-left to y=18.8 m"
    )
    print(f"USD references: {reference_count} relative and resolved")
    print(f"preview: {width}x{height}")
    print(f"architecture preview: {architecture_width}x{architecture_height}")


if __name__ == "__main__":
    main()
