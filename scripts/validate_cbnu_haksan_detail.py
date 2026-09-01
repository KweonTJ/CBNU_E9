#!/usr/bin/env python3
"""Static validation for the CBNU Haksan 1F detailed lobby world."""

from __future__ import annotations

import json
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
SOFA_ASSETS = {
    "straight": ROOT / "assets/furniture/sofa_straight.usda",
    "corner": ROOT / "assets/furniture/sofa_corner.usda",
    "single": ROOT / "assets/furniture/sofa_single.usda",
    "u_column": ROOT / "assets/furniture/sofa_u_around_2m_column.usda",
}
COMMON_SOFA_MATERIAL = ROOT / "assets/materials/furniture/brown_sofa_material.usda"
MARBLE_MATERIAL = ROOT / "assets/materials/lobby/marble_floor.usda"
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
FRONT_GLASS_WALL_ASSET = ROOT / "assets/architecture/windows/front_entrance_glass_walls.usda"
CORRIDOR_END_GLASS_WALL_ASSET = ROOT / "assets/architecture/windows/corridor_end_glass_wall.usda"
NORTH_CORRIDOR_END_GLASS_WALL_ASSET = ROOT / "assets/architecture/windows/north_corridor_end_glass_wall.usda"
ENTRANCE_PILLAR_ASSET = ROOT / "assets/structural/entrance_side_pillar.usda"
COLUMN_ASSET = ROOT / "assets/structural/column_2m.usda"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


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

    geometry = json.loads(GEOMETRY.read_text(encoding="utf-8"))
    require(len(geometry["columns"]) == 2, "expected two main columns")
    require(
        all(column["size"] == [1.5, 1.5, 3.0] for column in geometry["columns"]),
        "main column size must be 1.5 x 1.5 x 3.0 m",
    )
    for column in geometry["columns"]:
        x, y = column["center"]
        expected = f'def Xform "{column["name"]}"'
        require(expected in world_text, f"column missing: {column['name']}")
        translate = f"double3 xformOp:translate = ({x}, {y}, 0)"
        require(translate in world_text, f"column pose mismatch: {column['name']}")
    require(
        world_text.count('references = @../../assets/structural/column_2m.usda@') == 2,
        "main column references mismatch",
    )
    column_text = COLUMN_ASSET.read_text(encoding="utf-8")
    require("custom double cbnu:columnWidth = 1.5" in column_text, "column width metadata mismatch")
    require(
        "double3 xformOp:scale = (1.5, 1.5, 3.0)" in prim_block(column_text, "Body"),
        "column asset body must be 1.5 x 1.5 x 3.0 m",
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


def validate_ceiling() -> Counter[str]:
    world_text = WORLD.read_text(encoding="utf-8")
    geometry = json.loads(GEOMETRY.read_text(encoding="utf-8"))
    ceiling_config = json.loads(CEILING_CONFIG.read_text(encoding="utf-8"))
    ceiling = ceiling_config["ceiling"]
    lighting_profile = ceiling_config["lighting_profile"]
    lights = ceiling_config["lights"]
    type_counts = Counter(item.get("type", "panel") for item in lights)

    require(type_counts == Counter({"panel": 12, "large_panel": 1}), f"unexpected ceiling lights: {type_counts}")
    require(
        lighting_profile == {
            "standard_panel_intensity": 8000,
            "large_panel_intensity": 12000,
            "large_panel_normalize": False,
            "dome_intensity": 1600,
            "revision_note": "bright indoor lobby profile after GUI darkness review",
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
    require(layout_text.count('ceiling_panel_light.usda@') == 12, "standard ceiling panel reference count mismatch")
    require(layout_text.count('ceiling_panel_light_large.usda@') == 1, "large central ceiling light reference missing")
    for light in lights:
        require(f'def Xform "{light["name"]}"' in layout_text, f"ceiling light missing from layout: {light['name']}")

    regular_text = CEILING_LIGHT_ASSET.read_text(encoding="utf-8")
    require('def RectLight "Light"' in regular_text and 'float inputs:intensity = 8000' in regular_text, "standard ceiling RectLight intensity mismatch")
    large_text = CEILING_LARGE_LIGHT_ASSET.read_text(encoding="utf-8")
    require('custom double2 cbnu:panelSize = (6.0, 2.4)' in large_text, "large central light size mismatch")
    require('float inputs:width = 6.0' in large_text and 'float inputs:height = 2.4' in large_text, "large RectLight dimensions mismatch")
    require('float inputs:intensity = 12000' in large_text, "large central light intensity mismatch")
    require('bool inputs:normalize = false' in large_text, "large central light must use area-scaled output")
    require('float intensity = 1600' in world_text, "DomeLight ambient intensity mismatch")
    large = next(item for item in lights if item.get("type") == "large_panel")
    require(large["position"] == [25.0, 8.5, 2.95], "large central light pose mismatch")
    require(large.get("size") == [6.0, 2.4], "large central light config size mismatch")
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
    require('custom double2 cbnu:eachGlassPanelSize = (4.85, 2.82)' in glass_text, "full-height glass panel size mismatch")
    require('def Xform "LeftFullHeightGlass"' in glass_text, "left full-height glass panel missing")
    require('def Xform "RightFullHeightGlass"' in glass_text, "right full-height glass panel missing")
    require(glass_text.count('def Cube "GlassPanel"') == 2, "exactly two full-height glass panes are required")
    require('float inputs:opacity = 0.13' in glass_text, "full-height glass transparency missing")
    require('float inputs:opacityThreshold = 0' in glass_text, "full-height glass blend threshold missing")
    require('custom bool cbnu:collisionEnabled = false' in glass_text, "decorative glass must not add collision")


def validate_corridor_end_glass_wall() -> None:
    world_text = WORLD.read_text(encoding="utf-8")
    require('def Xform "WestCorridorEndGlassWall"' in world_text, "west corridor end glass wall prim missing")
    require(
        'prepend references = @../../assets/architecture/windows/corridor_end_glass_wall.usda@' in world_text,
        "west corridor end glass wall reference missing",
    )
    glass_root = prim_block(world_text, "WestCorridorEndGlassWall")
    require('double xformOp:rotateZ = 90' in glass_root, "west corridor glass rotation mismatch")
    require('double3 xformOp:translate = (0.17, 12.2753, 0)' in glass_root, "west corridor glass pose mismatch")
    wall_07 = prim_block(world_text, "Wall_07")
    require('token visibility = "invisible"' in wall_07, "opaque Wall_07 visual must be hidden behind glazing")
    require('bool physics:collisionEnabled = 1' in wall_07, "Wall_07 collision must remain enabled")
    require('double3 xformOp:scale = (1.855, 0.2, 3)' in wall_07, "Wall_07 geometry changed")

    glass_text = CORRIDOR_END_GLASS_WALL_ASSET.read_text(encoding="utf-8")
    require('custom double2 cbnu:glassPanelSize = (1.655, 2.82)' in glass_text, "west corridor glass size mismatch")
    require(glass_text.count('def Cube "GlassPanel"') == 1, "west corridor must use one full-height glass pane")
    require('float inputs:opacity = 0.13' in glass_text, "west corridor glass transparency missing")
    require('custom bool cbnu:collisionEnabled = false' in glass_text, "decorative west glass must not add collision")


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
    require(glass_text.count('def Cube "GlassPanel"') == 1, "north corridor must use one full-height glass pane")
    require('float inputs:opacity = 0.13' in glass_text, "north corridor glass transparency missing")
    require('custom bool cbnu:collisionEnabled = false' in glass_text, "decorative north glass must not add collision")


def validate_doors() -> Counter[str]:
    doors = json.loads(DOORS.read_text(encoding="utf-8"))["doors"]
    counts = Counter(item["type"] for item in doors)
    require(counts == Counter({"double": 4, "single": 3, "double_glass_pair": 1}), f"unexpected door counts: {counts}")
    single = (ROOT / "assets/architecture/doors/wood_door_single.usda").read_text(encoding="utf-8")
    double = (ROOT / "assets/architecture/doors/wood_door_double.usda").read_text(encoding="utf-8")
    require('"DoorLeaf"' in single, "single door leaf missing")
    require('"LeftDoor"' in double and '"RightDoor"' in double, "double door must contain two leaves")
    glass = (ROOT / "assets/architecture/doors/glass_door_double.usda").read_text(encoding="utf-8")
    require('custom int cbnu:doorLeafCount = 2' in glass, "glass door leaf count missing")
    require('def Xform "LeftDoor"' in glass and 'def Xform "RightDoor"' in glass, "glass door must contain two leaves")
    require(glass.count('def Cube "GlassPanel"') == 2, "glass door must contain two glass panels")
    require('float inputs:opacity = 0.16' in glass, "glass door transparency missing")
    require('float inputs:opacityThreshold = 0' in glass, "glass blend threshold missing")
    require(glass.count('def Cube "MidRail"') == 2, "glass door visual mid rails missing")
    pair = (ROOT / "assets/architecture/doors/glass_door_double_pair.usda").read_text(encoding="utf-8")
    require('custom int cbnu:doubleDoorSetCount = 2' in pair, "two double-glass sets are required")
    require('custom int cbnu:doorLeafCount = 4' in pair, "double-glass pair must contain four leaves")
    require('custom double cbnu:gapBetweenSets = 0.44' in pair, "double-glass set gap mismatch")
    require('custom bool cbnu:centralGlassInfill = true' in pair, "central fixed glass infill flag missing")
    require('custom double cbnu:centralGlassInfillWidth = 0.42' in pair, "central fixed glass infill width mismatch")
    require('def Xform "CentralGlassInfill"' in pair, "central fixed glass infill prim missing")
    require('double3 xformOp:scale = (0.42, 0.012, 2.10)' in pair, "central fixed glass panel size mismatch")
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
    for name, expected_position in expected_wall_attached_positions.items():
        actual_position = tuple(float(value) for value in sofas_by_name[name]["position"][:2])
        require(
            all(abs(actual - expected) < 1e-6 for actual, expected in zip(actual_position, expected_position)),
            f"wall contact position mismatch: {name}: {actual_position}",
        )
    require(sofas_by_name["Sofa_02"]["yaw_deg"] == 270, "Sofa_02 must face west into the lobby")

    fixtures_by_name = {item["name"]: item for item in fixtures}
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
    require("custom bool cbnu:continuousJunctions = true" in corner_text, "corner sofa continuous-junction metadata missing")
    require(
        'custom string cbnu:surfaceConstruction = "one beveled SofaUnified render mesh with non-overlapping base, seat and back topology"' in corner_text,
        "corner unified render-mesh metadata missing",
    )
    validate_unified_sofa_render_policy(corner_text, "sofa_corner.usda")
    corner_points = mesh_points(corner_text, "SofaUnified")
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
    require("custom bool cbnu:continuousJunctions = true" in u_text, "U sofa continuous-junction metadata missing")
    require(
        'custom string cbnu:surfaceConstruction = "one beveled SofaUnified render mesh with non-overlapping base, seat and back topology"' in u_text,
        "U unified render-mesh metadata missing",
    )
    require("custom double cbnu:columnClearance = 0" in u_text, "U sofa must touch Column_02")
    require("custom double cbnu:columnWidth = 1.5" in u_text, "U sofa column width metadata mismatch")
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
    require('double3 xformOp:translate = (-1.150000, -0.450000, 0.230000)' in u_text, "U sofa left base pose mismatch")
    require('double3 xformOp:translate = (1.150000, -0.450000, 0.230000)' in u_text, "U sofa right base pose mismatch")
    require('double3 xformOp:translate = (0, -1.200000, 0.230000)' in u_text, "U sofa bottom base pose mismatch")
    for contact_point in (
        "(0.7500, 0.4500, 0.4250)", "(-0.7500, 0.4500, 0.4250)",
        "(0.5900, -0.7500, 0.4250)", "(-0.5900, -0.7500, 0.4250)",
    ):
        require(contact_point in u_text, f"U sofa/column contact point missing: {contact_point}")
    sofa_points = mesh_points(u_text, "SofaUnified")
    require(max(point[2] for point in sofa_points if abs(point[1] - 0.75) < 1e-6) <= 0.58, "U sofa open-end backrest still protrudes")
    require(u_text.count('def Cylinder "') == 6, "U sofa helper-foot count changed")
    return type_counts, placement_counts, facing_counts, fixture_counts


def main() -> None:
    validate_world()
    ceiling_light_counts = validate_ceiling()
    validate_front_glass_walls()
    validate_corridor_end_glass_wall()
    validate_north_corridor_end_glass_wall()
    door_counts = validate_doors()
    type_counts, placement_counts, facing_counts, fixture_counts = validate_sofas()
    reference_count = validate_references()
    width, height = png_size(PREVIEW)

    print("CBNU Haksan detailed lobby validation: PASS")
    print(
        f"doors: single wood={door_counts['single']}, double wood={door_counts['double']}, "
        f"double glass sets={2 * door_counts['double_glass_pair']} "
        "(four transparent leaves + one central fixed glass panel)"
    )
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
    print("main columns: 2 x 1.5 x 1.5 x 3.0 m; original centers retained")
    print("U sofa column contact: clearance=0 at x=+-0.75 m and y=-0.75 m")
    print("floor material: Bala White polished granite with visible feldspar/quartz/mica pattern, 2.4 m repeat")
    print("ceiling: corridor-matched footprint, underside=3.0 m, thickness=0.1 m, collision enabled")
    print(
        f"ceiling lights: standard panels={ceiling_light_counts['panel']}, "
        f"large central panel={ceiling_light_counts['large_panel']} (6.0 x 2.4 m)"
    )
    print("front entrance glazing: two 4.85 x 2.82 m full-height panels; Wall_10 collider unchanged")
    print("west corridor end glazing: one 1.655 x 2.82 m full-height panel; Wall_07 collider unchanged")
    print("north corridor end glazing: one 3.1332 x 2.82 m full-height panel; Wall_04 collider unchanged")
    print(f"USD references: {reference_count} relative and resolved")
    print(f"preview: {width}x{height}")


if __name__ == "__main__":
    main()
