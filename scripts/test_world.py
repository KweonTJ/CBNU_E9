#!/usr/bin/env python3
"""Open the composed lobby Stage with a real USD runtime and verify key prims."""

from __future__ import annotations

import json
from pathlib import Path

try:
    from pxr import Usd, UsdShade
except ModuleNotFoundError as exc:
    raise SystemExit(
        "pxr is unavailable in this Python. Run this script with the Isaac Sim USD "
        "runtime as documented in README.md."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
WORLD = ROOT / "worlds/cbnu_haksan_1f_corridor/cbnu_haksan_1f_corridor.usda"
DYNAMIC_OBSTACLES = (
    ROOT / "worlds/cbnu_haksan_1f_corridor/config/dynamic_obstacles.json"
)

REQUIRED_PRIMS = {
    "/World/Environment/Ceiling": "Mesh",
    "/World/Environment/CeilingLights/CeilingLight_01/Housing": "Cube",
    "/World/Environment/CeilingLights/CeilingLight_01/Diffuser": "Cube",
    "/World/Environment/CeilingLights/CeilingLight_01/Light": "RectLight",
    "/World/Environment/CeilingLights/CeilingLight_13/Light": "RectLight",
    "/World/Environment/CeilingLights/CeilingLight_14/Light": "RectLight",
    "/World/Environment/CeilingLights/CeilingLight_15/Light": "RectLight",
    "/World/Environment/CeilingLights/CeilingLight_Central_Large/Housing": "Cube",
    "/World/Environment/CeilingLights/CeilingLight_Central_Large/Diffuser": "Cube",
    "/World/Environment/CeilingLights/CeilingLight_Central_Large/Light": "RectLight",
    "/World/Environment/FrontEntranceGlassWalls/LeftFullHeightGlass/GlassPanel": "Cube",
    "/World/Environment/FrontEntranceGlassWalls/RightFullHeightGlass/GlassPanel": "Cube",
    "/World/Environment/NorthCorridorEndGlassWall/GlassPanel": "Cube",
    "/World/Environment/ExteriorSidewalkPavers/SouthEntrancePavement": "Mesh",
    "/World/Environment/ExteriorSidewalkPavers/NorthExitPavement": "Mesh",
    "/World/Columns/Entrance_Pillar_ATM_Side/Body": "Cube",
    "/World/Columns/Entrance_Pillar_Opposite/Body": "Cube",
    "/World/Columns/Column_01/Body": "Cube",
    "/World/Columns/Column_03/Body": "Cube",
    "/World/Columns/Column_02/Body": "Cube",
    "/World/Architecture/DigitalDisplayWall_01/MainBody": "Mesh",
    "/World/Architecture/DigitalDisplayWall_01/FrontSection/Display_01/Bezel/LeftRail": "Cube",
    "/World/Architecture/DigitalDisplayWall_01/FrontSection/Display_01/Screen": "Cube",
    "/World/Architecture/DigitalDisplayWall_01/FrontSection/Display_03/Screen": "Cube",
    "/World/Architecture/DigitalDisplayWall_01/SideSection/Display_04/Screen": "Cube",
    "/World/Architecture/DigitalDisplayWall_01/SideSection/Display_08/Screen": "Cube",
    "/World/Architecture/DigitalDisplayWall_01/Collision/FrontCollision": "Cube",
    "/World/Architecture/DigitalDisplayWall_01/Collision/SideCollision": "Cube",
    "/World/Architecture/ColumnDisplay_01/Backing": "Cube",
    "/World/Architecture/ColumnDisplay_01/Bezel/LeftRail": "Cube",
    "/World/Architecture/ColumnDisplay_01/Screen": "Cube",
    "/World/Architecture/GrayPoster_01/Backing": "Cube",
    "/World/Architecture/GrayPoster_01/PosterFace": "Cube",
    "/World/Architecture/GrayPoster_02/PosterSlab": "Cube",
    "/World/Architecture/ElevatorDoor_01/DoorPanels/LeftLeaf": "Cube",
    "/World/Architecture/ElevatorDoor_01/DoorPanels/RightLeaf": "Cube",
    "/World/Architecture/ElevatorDoor_01/StatusIndicator/LitDisplay": "Cube",
    "/World/Architecture/ElevatorDoor_02/DoorPanels/LeftLeaf": "Cube",
    "/World/Architecture/ElevatorDoor_02/DoorPanels/RightLeaf": "Cube",
    "/World/Architecture/ElevatorDoor_02/StatusIndicator/LitDisplay": "Cube",
    "/World/Furniture/Sofa_Corner_01/SofaUnified": "Mesh",
    "/World/Furniture/Sofa_U_Column_02/SofaUnified": "Mesh",
    "/World/Furniture/ATM_01/MainBody": "Cube",
    "/World/Furniture/ATM_01/Screen": "Cube",
    "/World/Furniture/ATM_01/Key_9": "Cube",
    "/World/Furniture/ATM_02/MainBody": "Cube",
    "/World/Furniture/ATM_02/Screen": "Cube",
    "/World/Furniture/ATM_02/Key_9": "Cube",
    "/World/Furniture/Table_01/Tabletop": "Cube",
    "/World/Furniture/Table_01/FilledBase": "Cube",
    "/World/Furniture/Table_02/Tabletop": "Cube",
    "/World/Furniture/Table_02/FilledBase": "Cube",
    "/World/Furniture/Table_03/Tabletop": "Cube",
    "/World/Furniture/Table_03/FilledBase": "Cube",
    "/World/DynamicObstacles/ParcelBox_01/Body": "Cube",
    "/World/DynamicObstacles/ParcelBox_01/TopTape": "Cube",
    "/World/DynamicObstacles/ParcelBox_09/Body": "Cube",
    "/World/DynamicObstacles/ParcelBox_09/ShippingLabel": "Cube",
    "/World/DynamicObstacles/ParcelBox_10/Body": "Cube",
    "/World/DynamicObstacles/ParcelBox_13/Body": "Cube",
    "/World/Doors/Door_Double_05/DoubleDoorSet_01/LeftDoor/GlassPanel": "Cube",
    "/World/Doors/Door_Double_05/DoubleDoorSet_01/LeftDoor/MidRail": "Cube",
    "/World/Doors/Door_Double_05/DoubleDoorSet_01/RightDoor/GlassPanel": "Cube",
    "/World/Doors/Door_Double_05/DoubleDoorSet_02/LeftDoor/GlassPanel": "Cube",
    "/World/Doors/Door_Double_05/DoubleDoorSet_02/RightDoor/GlassPanel": "Cube",
    "/World/Doors/Door_Double_05/DoubleDoorSet_02/RightDoor/MidRail": "Cube",
    "/World/Doors/Door_Double_05/CentralGlassInfill/GlassPanel": "Cube",
    "/World/Doors/Door_Double_05/UpperGlassTransom/GlassPanel": "Cube",
    "/World/Doors/Door_Double_05/UpperGlassTransom/BottomRail": "Cube",
    "/World/Doors/Door_Double_05/UpperGlassTransom/TopRail": "Cube",
    "/World/Doors/Door_Single_04/DoorLeaf/Slab": "Cube",
}

HIDDEN_SOFA_HELPERS = (
    "/World/Furniture/Sofa_Corner_01/LongSeatPlush",
    "/World/Furniture/Sofa_Corner_01/BackPlushJunction",
    "/World/Furniture/Sofa_Corner_01/LongButton_01",
    "/World/Furniture/Sofa_Corner_01/CornerFoot",
    "/World/Furniture/Sofa_U_Column_02/LeftSeatPlush",
    "/World/Furniture/Sofa_U_Column_02/RightBackPlush",
    "/World/Furniture/Sofa_U_Column_02/LeftBackButtonA",
    "/World/Furniture/Sofa_U_Column_02/LeftFrontFoot",
)


def main() -> None:
    stage = Usd.Stage.Open(str(WORLD))
    if stage is None:
        raise AssertionError(f"failed to open composed Stage: {WORLD}")

    for path, expected_type in REQUIRED_PRIMS.items():
        prim = stage.GetPrimAtPath(path)
        if not prim.IsValid():
            raise AssertionError(f"composed prim missing: {path}")
        if not prim.IsLoaded() or not prim.IsActive():
            raise AssertionError(f"composed prim is inactive or unloaded: {path}")
        if prim.GetTypeName() != expected_type:
            raise AssertionError(
                f"unexpected prim type: {path}: {prim.GetTypeName()} != {expected_type}"
            )

    dome_light = stage.GetPrimAtPath("/World/DomeLight")
    dome_color = dome_light.GetAttribute("color")
    if dome_color.IsValid() and dome_color.HasAuthoredValueOpinion():
        raise AssertionError(
            f"DomeLight retains an authored color after rollback: {dome_color.Get()}"
        )

    light_gray_targets = (
        "/World/Environment/Walls/Wall_01",
        "/World/Environment/Walls/Wall_11",
        "/World/Columns/Column_01/Body",
        "/World/Columns/Column_02/Body",
        "/World/Columns/Column_03/Body",
        "/World/Columns/Entrance_Pillar_ATM_Side/Body",
        "/World/Columns/Entrance_Pillar_Opposite/Body",
    )
    for path in light_gray_targets:
        prim = stage.GetPrimAtPath(path)
        material, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
        if not material or str(material.GetPath()) != "/World/Looks/WallColumnLightGray":
            raise AssertionError(f"light-gray material mismatch: {path}")
    additional_ceiling_lights = {
        "CeilingLight_13": (19.0, 12.0, 2.96),
        "CeilingLight_14": (28.8, 12.0, 2.96),
        "CeilingLight_15": (29.0, 6.0, 2.96),
    }
    for name, expected_translate in additional_ceiling_lights.items():
        light_prim = stage.GetPrimAtPath(f"/World/Environment/CeilingLights/{name}")
        if tuple(light_prim.GetAttribute("xformOp:translate").Get()) != expected_translate:
            raise AssertionError(f"additional ceiling light pose mismatch: {name}")
        if float(light_prim.GetAttribute("xformOp:rotateZ").Get()) != 90.0:
            raise AssertionError(f"additional ceiling light yaw mismatch: {name}")
    floor = stage.GetPrimAtPath("/World/Environment/Floor")
    floor_material, _ = UsdShade.MaterialBindingAPI(floor).ComputeBoundMaterial()
    if not floor_material or str(floor_material.GetPath()) != "/World/Looks/MarbleFloor":
        raise AssertionError("floor no longer uses the original Bala White material")
    ceiling = stage.GetPrimAtPath("/World/Environment/Ceiling")
    ceiling_material, _ = UsdShade.MaterialBindingAPI(ceiling).ComputeBoundMaterial()
    if not ceiling_material or str(ceiling_material.GetPath()) != "/World/Looks/CeilingWhite":
        raise AssertionError("ceiling no longer uses the original white material")

    parcel_config = json.loads(DYNAMIC_OBSTACLES.read_text(encoding="utf-8"))
    parcel_boxes = parcel_config["boxes"]
    for box in parcel_boxes:
        name = box["name"]
        root = stage.GetPrimAtPath(f"/World/DynamicObstacles/{name}")
        body = stage.GetPrimAtPath(f"/World/DynamicObstacles/{name}/Body")
        applied_root_schemas = set(root.GetAppliedSchemas())
        applied_body_schemas = set(body.GetAppliedSchemas())
        if not {"PhysicsRigidBodyAPI", "PhysicsMassAPI"} <= applied_root_schemas:
            raise AssertionError(f"dynamic physics schemas missing: {name}")
        if "PhysicsCollisionAPI" not in applied_body_schemas:
            raise AssertionError(f"parcel collision schema missing: {name}")
        if root.GetAttribute("physics:rigidBodyEnabled").Get() is not True:
            raise AssertionError(f"parcel rigid body disabled: {name}")
        if root.GetAttribute("physics:kinematicEnabled").Get() is not False:
            raise AssertionError(f"parcel unexpectedly kinematic: {name}")
        if root.GetAttribute("physics:startsAsleep").Get() is not True:
            raise AssertionError(f"parcel must start asleep: {name}")
        if abs(root.GetAttribute("physics:mass").Get() - box["mass_kg"]) > 1e-6:
            raise AssertionError(f"parcel mass mismatch: {name}")
        scale = tuple(body.GetAttribute("xformOp:scale").Get())
        if scale != tuple(box["size"]):
            raise AssertionError(f"parcel size mismatch: {name}: {scale}")

    for path in HIDDEN_SOFA_HELPERS:
        prim = stage.GetPrimAtPath(path)
        if not prim.IsValid():
            raise AssertionError(f"composed sofa helper missing: {path}")
        if prim.GetAttribute("visibility").Get() != "invisible":
            raise AssertionError(f"composed sofa helper remains visible: {path}")

    for column_name in ("Column_01", "Column_03", "Column_02"):
        body = stage.GetPrimAtPath(f"/World/Columns/{column_name}/Body")
        scale = body.GetAttribute("xformOp:scale").Get()
        if tuple(scale) != (1.2, 1.2, 3.0):
            raise AssertionError(f"unexpected column size: {column_name}: {scale}")

    display_wall_collisions = {
        "DigitalDisplayWall_01": ("FrontCollision", "SideCollision"),
    }
    for wall_name, collision_names in display_wall_collisions.items():
        for collision_name in collision_names:
            collision = stage.GetPrimAtPath(
                f"/World/Architecture/{wall_name}/Collision/{collision_name}"
            )
            if collision.GetAttribute("visibility").Get() != "invisible":
                raise AssertionError(
                    f"display wall collision helper remains visible: {wall_name}/{collision_name}"
                )
            if collision.GetAttribute("physics:collisionEnabled").Get() is not True:
                raise AssertionError(
                    f"display wall collision helper is disabled: {wall_name}/{collision_name}"
                )

    expected_architecture_poses = {
        "DigitalDisplayWall_01": ((25.9724, 13.2044, 0.85), 0.0),
        "ColumnDisplay_01": ((26.43765, 9.78845, 0.7), 0.0),
        "GrayPoster_01": ((30.62, 5.0, 1.05), 270.0),
        "GrayPoster_02": ((20.5892, 13.0403, 0.85), 0.0),
        "ElevatorDoor_01": ((22.8392, 15.2, 0.0), 90.0),
        "ElevatorDoor_02": ((22.8392, 19.0, 0.0), 90.0),
    }
    for prim_name, (expected_translate, expected_yaw) in expected_architecture_poses.items():
        prim = stage.GetPrimAtPath(f"/World/Architecture/{prim_name}")
        translate = tuple(prim.GetAttribute("xformOp:translate").Get())
        yaw = float(prim.GetAttribute("xformOp:rotateZ").Get())
        if translate != expected_translate or yaw != expected_yaw:
            raise AssertionError(
                f"unexpected architecture pose: {prim_name}: {translate}, yaw={yaw}"
            )

    removed_display_wall = stage.GetPrimAtPath("/World/Architecture/DigitalDisplayWall_02")
    if removed_display_wall.IsValid():
        raise AssertionError("opposite screen structure remains after gray-poster conversion")
    column_display = stage.GetPrimAtPath("/World/Architecture/ColumnDisplay_01")
    if column_display.GetAttribute("cbnu:referencePrim").Get() != "Column_03":
        raise AssertionError("large display is not attached to Column_03")
    gray_poster = stage.GetPrimAtPath("/World/Architecture/GrayPoster_01")
    if gray_poster.GetAttribute("cbnu:referenceWall").Get() != "Wall_11":
        raise AssertionError("gray poster is not attached to Wall_11")
    if gray_poster.GetAttribute("cbnu:referenceDoor").Get() != "Door_Single_04":
        raise AssertionError("gray poster is not placed relative to Door_Single_04")
    large_gray_poster = stage.GetPrimAtPath("/World/Architecture/GrayPoster_02")
    if large_gray_poster.GetAttribute("cbnu:referenceWall").Get() != "Wall_06":
        raise AssertionError("large gray poster is not attached to Wall_06")
    if large_gray_poster.GetAttribute("cbnu:hasScreen").Get() is not False:
        raise AssertionError("large gray poster still reports screen geometry")
    if large_gray_poster.GetAttribute("cbnu:visiblePieceCount").Get() != 1:
        raise AssertionError("large gray poster is not one piece")
    poster_slab = stage.GetPrimAtPath("/World/Architecture/GrayPoster_02/PosterSlab")
    if tuple(poster_slab.GetAttribute("xformOp:scale").Get()) != (4.5, 0.15, 1.22):
        raise AssertionError("large gray poster dimensions mismatch")

    for name in ("ElevatorDoor_01", "ElevatorDoor_02"):
        elevator = stage.GetPrimAtPath(f"/World/Architecture/{name}")
        if elevator.GetAttribute("cbnu:referenceWall").Get() != "Wall_05":
            raise AssertionError(f"elevator door is not on Wall_05: {name}")
        if elevator.GetAttribute("cbnu:serviceState").Get() != "operational":
            raise AssertionError(f"elevator is not marked operational: {name}")
        if elevator.GetAttribute("cbnu:doorState").Get() != "closed":
            raise AssertionError(f"elevator door state mismatch: {name}")

    sofa_02 = stage.GetPrimAtPath("/World/Furniture/Sofa_02")
    if tuple(sofa_02.GetAttribute("xformOp:translate").Get()) != (35.0392, 10.2174, 0.0):
        raise AssertionError("Sofa_02 was not restored after correcting the door location")
    if tuple(sofa_02.GetAttribute("xformOp:scale").Get()) != (1.11595, 1.0, 1.0):
        raise AssertionError("Sofa_02 original width was not restored")

    entrance_right_door = stage.GetPrimAtPath("/World/Doors/Door_Single_04")
    if tuple(entrance_right_door.GetAttribute("xformOp:translate").Get()) != (30.62, 3.14695, 0.0):
        raise AssertionError("Door_Single_04 is not on the entrance-right Wall_11")
    if float(entrance_right_door.GetAttribute("xformOp:rotateZ").Get()) != 270.0:
        raise AssertionError("Door_Single_04 orientation mismatch on Wall_11")

    corner_return = stage.GetPrimAtPath("/World/Furniture/Sofa_Corner_01/ReturnBase")
    if tuple(corner_return.GetAttribute("xformOp:scale").Get()) != (0.82, 2.71, 0.34):
        raise AssertionError("Sofa_Corner_01 return was not shortened by 0.30 m")

    print(f"CBNU Haksan composed Stage: PASS (USD {Usd.GetVersion()})")
    print(f"verified composed prims: {len(REQUIRED_PRIMS)}")
    print("sky background: authored DomeLight color removed; original default restored")
    print("surface colors: walls and all columns use medium neutral gray between the light and dark-gray posters; floor keeps Bala White and ceiling keeps CeilingWhite")
    print("ATM geometry: loaded=2")
    print("front double-glass sets: loaded=2, fully infilled clear leaves=4")
    print("entrance-right Wall_11: corner sofa return shortened by 0.30 m; one single door inserted with 0.197 m side clearances")
    print("lobby tables: loaded=3; all use filled lower bodies")
    print(
        "dynamic parcels: loaded=13; Table_03=9, main entrance=4"
    )
    print("ceiling: loaded; standard panels=15 at 8000; large central panel=1 at 12000 (6.0 x 2.4 m)")
    print("front entrance glazing: loaded=2 clear full-height panels; original Wall_10 collider retained")
    print("west corridor: width=1.73 m; opaque Wall_07 visible with collision")
    print("north corridor end glazing: loaded=1 clear full-height panel; original Wall_04 collider retained")
    print("exterior pavement: loaded=2 oversized watertight opaque sidewalk-paver slabs; south=200.0 x 100.0435 m, north=200.0 x 79.2754 m; top z=0.05 m")
    print("entrance side pillars: loaded=2; mirrored 1.0425 x 1.0 x 3.0 m bodies projecting into lobby")
    print("front entrance joins: wall/glass, pillar/glass and leaf/rail borders closed; center gap filled by one 0.44 m clear panel meeting the transom")
    print("front entrance upper gap: filled to ceiling with one 4.16 x 0.72 m clear glass transom")
    print("main columns: loaded=3; each body=1.2 x 1.2 x 3.0 m")
    print("digital display walls: loaded=1; original left=5/right=3; opposite screen structure removed")
    print("digital display wall collision: loaded=2 invisible box helpers on the original wall only")
    print("Column_03 display: loaded=1 large 1.0 x 1.45 m panel facing the main entrance")
    print("Wall_11 poster: loaded=1 light-gray 2.2 x 1.0 m panel; top fixed at 2.05 m and bottom extended")
    print("Wall_06 poster: loaded=1 non-emissive dark-gray 4.5 x 1.22 x 0.15 m slab; doubled depth, no bezel, screen or collider")
    print("Wall_05 elevators: loaded=2 operational stainless-steel center-opening doors, 1.45 x 2.30 m each")
    print("corner/U sofas: one visible SofaUnified mesh each; sampled helpers invisible=8")


if __name__ == "__main__":
    main()
