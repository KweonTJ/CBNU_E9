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


def validate_references() -> int:
    count = 0
    for layer in sorted(ROOT.rglob("*.usd*")):
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
    for column in geometry["columns"]:
        x, y = column["center"]
        expected = f'def Xform "{column["name"]}"'
        require(expected in world_text, f"column missing: {column['name']}")
        translate = f"double3 xformOp:translate = ({x}, {y}, 0)"
        require(translate in world_text, f"column pose mismatch: {column['name']}")


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
        fixture_counts == Counter({"lobby_table_filled": 3, "atm": 1}),
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
    require('def Xform "ATM_01"' in layout_text and 'def Xform "Sofa_04"' not in layout_text, "ATM layout replacement missing")
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
        "corner": (
            "BaseUpholsteryUnified", "SeatCushionUnified", "BackCushionUnified",
        ),
        "u_column": (
            "LeftBench", "RightBench", "BottomBench",
            "LeftBackSupport", "RightBackSupport", "BottomBackSupport",
            "BaseUpholsteryUnified", "SeatCushionUnified", "BackCushionUnified",
            "LeftFrontFoot", "RightFrontFoot", "BottomLeftFoot", "BottomRightFoot",
        ),
    }
    for sofa_type, asset in SOFA_ASSETS.items():
        text = asset.read_text(encoding="utf-8")
        require("@../materials/furniture/brown_sofa_material.usda@" in text, f"brown material reference missing: {asset.name}")
        require("NavyFabric" not in text and "CharcoalFabric" not in text, f"legacy non-brown material remains: {asset.name}")
        require("custom bool cbnu:hasArmrests = false" in text, f"armless metadata missing: {asset.name}")
        require("custom string cbnu:cushionStyle" in text and "soft overstuffed rounded cushions" in text, f"soft cushion metadata missing: {asset.name}")
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
    require('custom string cbnu:surfaceConstruction = "single unified base, seat and back meshes"' in corner_text, "corner unified-surface metadata missing")
    for mesh_name in ("BaseUpholsteryUnified", "SeatCushionUnified", "BackCushionUnified"):
        validate_mesh_topology(corner_text, mesh_name)
    for mesh_name in ("SeatCushionUnified", "BackCushionUnified"):
        require('subdivisionScheme = "catmullClark"' in prim_block(corner_text, mesh_name), f"corner cushion is not smoothly subdivided: {mesh_name}")
    for plush_name in (
        "LongSeatPlush", "ReturnSeatPlush", "SeatPlushJunction",
        "LongBackPlush", "ReturnBackPlush", "BackPlushJunction",
    ):
        require('visibility = "invisible"' in prim_block(corner_text, plush_name), f"overlapping corner plush overlay remains visible: {plush_name}")
    for hidden_name in (
        "CornerBase", "LongBase", "ReturnBase", "LongBack", "ReturnBack",
        "LongSeatContinuous", "ReturnSeatContinuous",
        "LongBackCushionContinuous", "ReturnBackCushionContinuous",
        "SeatCornerBlend", "BackCornerBlend",
    ):
        require('visibility = "invisible"' in prim_block(corner_text, hidden_name), f"legacy corner module remains visible: {hidden_name}")

    u_text = SOFA_ASSETS["u_column"].read_text(encoding="utf-8")
    require("custom bool cbnu:continuousJunctions = true" in u_text, "U sofa continuous-junction metadata missing")
    require('custom string cbnu:surfaceConstruction = "single unified base, seat and back meshes"' in u_text, "U unified-surface metadata missing")
    require("custom double cbnu:columnClearance = 0" in u_text, "U sofa must touch Column_02")
    for mesh_name in ("BaseUpholsteryUnified", "SeatCushionUnified", "BackCushionUnified"):
        validate_mesh_topology(u_text, mesh_name)
    for mesh_name in ("SeatCushionUnified", "BackCushionUnified"):
        require('subdivisionScheme = "catmullClark"' in prim_block(u_text, mesh_name), f"U cushion is not smoothly subdivided: {mesh_name}")
    for plush_name in (
        "LeftSeatPlush", "RightSeatPlush", "BottomSeatPlush",
        "LeftSeatPlushJunction", "RightSeatPlushJunction",
        "LeftBackPlush", "RightBackPlush", "BottomBackPlush",
        "LeftBackPlushJunction", "RightBackPlushJunction",
    ):
        require('visibility = "invisible"' in prim_block(u_text, plush_name), f"overlapping U plush overlay remains visible: {plush_name}")
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
    require('double3 xformOp:translate = (-1.400000, -0.450000, 0.230000)' in u_text, "U sofa left base pose mismatch")
    require('double3 xformOp:translate = (1.400000, -0.450000, 0.230000)' in u_text, "U sofa right base pose mismatch")
    require('double3 xformOp:translate = (0, -1.450000, 0.230000)' in u_text, "U sofa bottom base pose mismatch")
    for contact_point in (
        "(1.000, 1.000, 0.46)", "(-1.000, 1.000, 0.46)",
        "(0.840, -1.000, 0.46)", "(-0.840, -1.000, 0.46)",
    ):
        require(contact_point in u_text, f"U sofa/column contact point missing: {contact_point}")
    require(u_text.count('def Cylinder "') == 6, "U sofa must have six visible feet")
    return type_counts, placement_counts, facing_counts, fixture_counts


def main() -> None:
    validate_world()
    door_counts = validate_doors()
    type_counts, placement_counts, facing_counts, fixture_counts = validate_sofas()
    reference_count = validate_references()
    width, height = png_size(PREVIEW)

    print("CBNU Haksan detailed lobby validation: PASS")
    print(
        f"doors: single wood={door_counts['single']}, double wood={door_counts['double']}, "
        f"double glass sets={2 * door_counts['double_glass_pair']} (four transparent leaves)"
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
    print("sofa junctions: corner/U use single Catmull-Clark seat/back surfaces; overlapping capsule blends hidden")
    print("table fit: all 3 use filled bases; Table_01/02 match paired sofa widths and Table_03 matches former Sofa_01 footprint (1.6232 x 0.82 m)")
    print("U sofa column contact: clearance=0 at x=+-1.0 m and y=-1.0 m")
    print("floor material: Bala White polished granite with visible feldspar/quartz/mica pattern, 2.4 m repeat")
    print(f"USD references: {reference_count} relative and resolved")
    print(f"preview: {width}x{height}")


if __name__ == "__main__":
    main()
