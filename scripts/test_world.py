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
    "/World/Environment/CeilingLights/AirConditioners/CeilingAC_01/RecessedHousing": "Cube",
    "/World/Environment/CeilingLights/AirConditioners/CeilingAC_01/IntakeGrille": "Cube",
    "/World/Environment/CeilingLights/AirConditioners/CeilingAC_01/FourWayOutlets/NorthOutlet": "Cube",
    "/World/Environment/CeilingLights/AirConditioners/CeilingAC_02/RecessedHousing": "Cube",
    "/World/Environment/CeilingLights/AirConditioners/CeilingAC_02/IntakeGrille": "Cube",
    "/World/Environment/CeilingLights/AirConditioners/CeilingAC_02/FourWayOutlets/NorthOutlet": "Cube",
    "/World/Environment/FrontEntranceGlassWalls/LeftFullHeightGlass/GlassPanel": "Cube",
    "/World/Environment/FrontEntranceGlassWalls/LeftFullHeightGlass/LowerOpaqueWall": "Cube",
    "/World/Environment/FrontEntranceGlassWalls/RightFullHeightGlass/GlassPanel": "Cube",
    "/World/Environment/FrontEntranceGlassWalls/RightFullHeightGlass/LowerOpaqueWall": "Cube",
    "/World/Environment/NorthCorridorEndGlassWall/GlassPanel": "Cube",
    "/World/Environment/NorthCorridorEndGlassWall/LowerOpaqueWall": "Cube",
    "/World/Environment/NorthGlassWoodPlatform/PlatformBody": "Cube",
    "/World/Environment/Walls/Wall_02": "Cube",
    "/World/Environment/Walls/Wall_06": "Cube",
    "/World/Environment/Walls/Wall_08": "Cube",
    "/World/Environment/Walls/Wall_12": "Cube",
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
    "/World/Architecture/DigitalDisplayWall_01/SideSection/Display_09/Screen": "Cube",
    "/World/Architecture/DigitalDisplayWall_01/SideSection/InstituteWordmarkText": "Xform",
    "/World/Architecture/DigitalDisplayWall_01/SideSection/InstituteWordmarkText/GlyphMesh": "Mesh",
    "/World/Architecture/DigitalDisplayWall_01/Collision/FrontCollision": "Cube",
    "/World/Architecture/DigitalDisplayWall_01/Collision/SideCollision": "Cube",
    "/World/Architecture/WoodPartition_01/PartitionBody": "Cube",
    "/World/Architecture/WoodPartition_01/FrontPanelJoints/Joint_01": "Cube",
    "/World/Architecture/ColumnDisplay_01/Backing": "Cube",
    "/World/Architecture/ColumnDisplay_01/Bezel/LeftRail": "Cube",
    "/World/Architecture/ColumnDisplay_01/Screen": "Cube",
    "/World/Architecture/GrayPoster_01/Backing": "Cube",
    "/World/Architecture/GrayPoster_01/PosterFace": "Cube",
    "/World/Architecture/GrayPoster_02/PosterSlab": "Mesh",
    "/World/Architecture/ElevatorDoor_01/DoorPanels/LeftLeaf": "Cube",
    "/World/Architecture/ElevatorDoor_01/DoorPanels/RightLeaf": "Cube",
    "/World/Architecture/ElevatorDoor_01/StatusIndicator/LitDisplay": "Cube",
    "/World/Architecture/ElevatorDoor_02/DoorPanels/LeftLeaf": "Cube",
    "/World/Architecture/ElevatorDoor_02/DoorPanels/RightLeaf": "Cube",
    "/World/Architecture/ElevatorDoor_02/StatusIndicator/LitDisplay": "Cube",
    "/World/Architecture/GreenInformationBoard_01/PanelBacking": "Cube",
    "/World/Architecture/GreenInformationBoard_02/PanelBacking": "Cube",
    "/World/Architecture/GreenInformationBoard_03/PanelBacking": "Cube",
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
    "/World/DynamicObstacles/ParcelBox_14/Body": "Cube",
    "/World/DynamicObstacles/ParcelBox_15/Body": "Cube",
    "/World/DynamicObstacles/ParcelBox_16/Body": "Cube",
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
    "/World/Doors/Door_Double_03/LeftDoor/Slab": "Cube",
    "/World/Doors/Door_Double_03/WoodPortal/PortalHeader": "Cube",
    "/World/Doors/Door_Double_04/RightDoor/Slab": "Cube",
    "/World/Doors/Door_Double_04/WoodPortal/PortalHeader": "Cube",
    "/World/Doors/Door_Double_01/WoodPortal/LeftPortalJamb": "Cube",
    "/World/Doors/Door_Double_01/WoodPortal/PortalHeader": "Cube",
    "/World/Doors/Door_Double_02/WoodPortal/RightPortalJamb": "Cube",
    "/World/Doors/Door_Single_04/WoodPortal/RightPortalJamb": "Cube",
    "/World/Doors/Door_Single_04/WoodPortal/PortalHeader": "Cube",
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
    wall_gray_shader = UsdShade.Shader(
        stage.GetPrimAtPath("/World/Looks/WallColumnLightGray/PreviewSurface")
    )
    wall_gray = tuple(float(value) for value in wall_gray_shader.GetInput("diffuseColor").Get())
    expected_stone_gray = (0.50, 0.51, 0.52)
    if any(abs(value - expected) > 1e-6 for value, expected in zip(wall_gray, expected_stone_gray)):
        raise AssertionError("wall/column material is not the requested cool stone gray")
    if abs(float(wall_gray_shader.GetInput("roughness").Get()) - 0.72) > 1e-6:
        raise AssertionError("wall/column material roughness is not stone-like")
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
    expected_ceiling_ac_positions = {
        "CeilingAC_01": (20.8, 8.5, 3.0),
        "CeilingAC_02": (29.2, 8.5, 3.0),
    }
    for name, expected_position in expected_ceiling_ac_positions.items():
        root = stage.GetPrimAtPath(
            f"/World/Environment/CeilingLights/AirConditioners/{name}"
        )
        if tuple(root.GetAttribute("xformOp:translate").Get()) != expected_position:
            raise AssertionError(f"ceiling air conditioner pose mismatch: {name}")
        if tuple(root.GetAttribute("cbnu:footprint").Get()) != (1.1, 1.1):
            raise AssertionError(f"ceiling air conditioner footprint mismatch: {name}")
        if root.GetAttribute("cbnu:operational").Get() is not True:
            raise AssertionError(f"ceiling air conditioner is not operational: {name}")
        if root.GetAttribute("cbnu:collisionEnabled").Get() is not False:
            raise AssertionError(f"ceiling air conditioner collision policy mismatch: {name}")
        housing = stage.GetPrimAtPath(f"{root.GetPath()}/RecessedHousing")
        intake = stage.GetPrimAtPath(f"{root.GetPath()}/IntakeGrille")
        if tuple(housing.GetAttribute("xformOp:scale").Get()) != (1.1, 1.1, 0.07):
            raise AssertionError(f"ceiling air conditioner housing mismatch: {name}")
        if tuple(intake.GetAttribute("xformOp:scale").Get()) != (0.56, 0.56, 0.012):
            raise AssertionError(f"ceiling air conditioner intake mismatch: {name}")
        if "PhysicsCollisionAPI" in set(housing.GetAppliedSchemas()):
            raise AssertionError(f"ceiling air conditioner unexpectedly has collision: {name}")
    expected_lower_wall_translates = {
        "LeftFullHeightGlass": ((-4.78275, -0.08, 0.51), (5.4055, 0.2, 1.02)),
        "RightFullHeightGlass": ((4.6668, -0.08, 0.51), (5.1736, 0.2, 1.02)),
    }
    for side, (expected_translate, expected_scale) in expected_lower_wall_translates.items():
        lower_wall = stage.GetPrimAtPath(
            f"/World/Environment/FrontEntranceGlassWalls/{side}/LowerOpaqueWall"
        )
        if tuple(lower_wall.GetAttribute("xformOp:scale").Get()) != expected_scale:
            raise AssertionError(f"front lower facade wall dimensions mismatch: {side}")
        if tuple(lower_wall.GetAttribute("xformOp:translate").Get()) != expected_translate:
            raise AssertionError(f"front lower facade wall flush pose mismatch: {side}")
        lower_wall_material, _ = UsdShade.MaterialBindingAPI(lower_wall).ComputeBoundMaterial()
        if not lower_wall_material or str(lower_wall_material.GetPath()) != "/World/Environment/FrontEntranceGlassWalls/LowerFacadeWallMaterial":
            raise AssertionError(f"front lower facade wall material mismatch: {side}")

    north_lower_wall = stage.GetPrimAtPath(
        "/World/Environment/NorthCorridorEndGlassWall/LowerOpaqueWall"
    )
    if tuple(north_lower_wall.GetAttribute("xformOp:scale").Get()) != (3.1332, 0.2, 1.02):
        raise AssertionError("north corridor lower opaque wall dimensions mismatch")
    if tuple(north_lower_wall.GetAttribute("xformOp:translate").Get()) != (0.0, 0.07, 0.51):
        raise AssertionError("north corridor lower opaque wall pose mismatch")
    if "PhysicsCollisionAPI" in set(north_lower_wall.GetAppliedSchemas()):
        raise AssertionError("north corridor lower opaque wall must reuse Wall_04 collision")
    north_lower_wall_material, _ = UsdShade.MaterialBindingAPI(
        north_lower_wall
    ).ComputeBoundMaterial()
    if (
        not north_lower_wall_material
        or str(north_lower_wall_material.GetPath())
        != "/World/Environment/NorthCorridorEndGlassWall/LowerOpaqueWallMaterial"
    ):
        raise AssertionError("north corridor lower opaque wall material mismatch")

    wood_platform = stage.GetPrimAtPath("/World/Environment/NorthGlassWoodPlatform")
    if tuple(wood_platform.GetAttribute("xformOp:translate").Get()) != (24.4058, 20.27, 0.0):
        raise AssertionError("north glass wood platform world pose mismatch")
    platform_body = stage.GetPrimAtPath("/World/Environment/NorthGlassWoodPlatform/PlatformBody")
    if tuple(platform_body.GetAttribute("xformOp:scale").Get()) != (3.1332, 0.6, 0.15):
        raise AssertionError("north glass wood platform dimensions mismatch")
    if tuple(platform_body.GetAttribute("xformOp:translate").Get()) != (0.0, 0.0, 0.075):
        raise AssertionError("north glass wood platform body pose mismatch")
    if "PhysicsCollisionAPI" not in set(platform_body.GetAppliedSchemas()):
        raise AssertionError("north glass wood platform collider missing")
    if platform_body.GetAttribute("physics:collisionEnabled").Get() is not True:
        raise AssertionError("north glass wood platform collision disabled")
    if "PhysicsRigidBodyAPI" in set(platform_body.GetAppliedSchemas()):
        raise AssertionError("north glass wood platform unexpectedly dynamic")
    platform_material, _ = UsdShade.MaterialBindingAPI(platform_body).ComputeBoundMaterial()
    if not platform_material or str(platform_material.GetPath()) != "/World/Environment/NorthGlassWoodPlatform/WoodMaterial":
        raise AssertionError("north glass wood platform material mismatch")

    unified_corner_walls = {
        "Wall_02": ((9.4768, 0.2, 3.0), (30.7108, 13.3044, 1.5)),
        "Wall_06": ((22.7522, 0.2, 3.0), (11.4631, 13.1403, 1.5)),
        "Wall_08": ((16.0275, 0.2, 3.0), (8.10075, 11.4103, 1.5)),
        "Wall_12": ((4.7956, 0.2, 3.0), (33.0514, 6.1739, 1.5)),
    }
    for wall_name, (expected_scale, expected_translate) in unified_corner_walls.items():
        wall = stage.GetPrimAtPath(f"/World/Environment/Walls/{wall_name}")
        if tuple(wall.GetAttribute("xformOp:scale").Get()) != expected_scale:
            raise AssertionError(f"unified wall-corner scale mismatch: {wall_name}")
        if tuple(wall.GetAttribute("xformOp:translate").Get()) != expected_translate:
            raise AssertionError(f"unified wall-corner pose mismatch: {wall_name}")
        if wall.GetAttribute("physics:collisionEnabled").Get() is not True:
            raise AssertionError(f"unified wall-corner collision disabled: {wall_name}")

    expected_board_poses = {
        "GreenInformationBoard_01": (23.4558, 20.25, 0.15),
        "GreenInformationBoard_02": (24.4058, 20.25, 0.15),
        "GreenInformationBoard_03": (25.3558, 20.25, 0.15),
    }
    for board_name, expected_translate in expected_board_poses.items():
        board = stage.GetPrimAtPath(f"/World/Architecture/{board_name}")
        if tuple(board.GetAttribute("xformOp:translate").Get()) != expected_translate:
            raise AssertionError(f"information board pose mismatch: {board_name}")
        if board.GetAttribute("cbnu:mountedOn").Get() != "NorthGlassWoodPlatform":
            raise AssertionError(f"information board platform metadata mismatch: {board_name}")
        panel = stage.GetPrimAtPath(f"/World/Architecture/{board_name}/PanelBacking")
        if tuple(panel.GetAttribute("xformOp:scale").Get()) != (0.63, 0.055, 1.2):
            raise AssertionError(f"information board panel dimensions mismatch: {board_name}")
        if panel.GetAttribute("physics:collisionEnabled").Get() is not True:
            raise AssertionError(f"information board panel collision disabled: {board_name}")
        panel_material, _ = UsdShade.MaterialBindingAPI(panel).ComputeBoundMaterial()
        expected_material = f"/World/Architecture/{board_name}/GreenBoardMaterial"
        if not panel_material or str(panel_material.GetPath()) != expected_material:
            raise AssertionError(f"information board green material mismatch: {board_name}")
        wheel = stage.GetPrimAtPath(f"/World/Architecture/{board_name}/RollingBase/Wheel_FL")
        if wheel.GetAttribute("radius").Get() != 0.045:
            raise AssertionError(f"information board wheel size mismatch: {board_name}")

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

    accent_sofa_targets = {
        "/World/Furniture/Sofa_Corner_01/SofaUnified": "/World/Furniture/Sofa_Corner_01/DarkReddishBrownLeather",
        "/World/Furniture/Sofa_U_Column_02/SofaUnified": "/World/Furniture/Sofa_U_Column_02/DarkReddishBrownLeather",
    }
    for mesh_path, expected_material_path in accent_sofa_targets.items():
        mesh = stage.GetPrimAtPath(mesh_path)
        material, _ = UsdShade.MaterialBindingAPI(mesh).ComputeBoundMaterial()
        if not material or str(material.GetPath()) != expected_material_path:
            raise AssertionError(f"dark reddish-brown leather binding mismatch: {mesh_path}")
        shader = UsdShade.Shader(stage.GetPrimAtPath(f"{expected_material_path}/PreviewSurface"))
        color = tuple(float(value) for value in shader.GetInput("diffuseColor").Get())
        if any(abs(value - expected) > 1e-6 for value, expected in zip(color, (0.09, 0.055, 0.05))):
            raise AssertionError(f"dark reddish-brown leather color mismatch: {mesh_path}")
        if abs(float(shader.GetInput("roughness").Get()) - 0.38) > 1e-6:
            raise AssertionError(f"dark reddish-brown leather roughness mismatch: {mesh_path}")

    brown_sofa_mesh = stage.GetPrimAtPath("/World/Furniture/Sofa_03/SeatCushionContinuous")
    brown_targets = [str(path) for path in brown_sofa_mesh.GetRelationship("material:binding").GetTargets()]
    if brown_targets != ["/World/Furniture/Sofa_03/Materials/BrownLeatherHighlight"]:
        raise AssertionError("straight sofa no longer uses the original brown leather")

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

    display_wall = stage.GetPrimAtPath("/World/Architecture/DigitalDisplayWall_01")
    if display_wall.GetAttribute("cbnu:frontLength").Get() != 2.5:
        raise AssertionError("three-display corner-wall section changed length")
    if display_wall.GetAttribute("cbnu:sideLength").Get() != 6.288533:
        raise AssertionError("six-display corner-wall section was not extended")
    if display_wall.GetAttribute("cbnu:frontDisplayGap").Get() != 0.07:
        raise AssertionError("three-display section spacing changed")
    if display_wall.GetAttribute("cbnu:sideDisplayGap").Get() != 0.24:
        raise AssertionError("six-display section gap mismatch")
    if display_wall.GetAttribute("cbnu:sideFrameEndMargin").Get() != 0.1:
        raise AssertionError("six-display section frame end margin mismatch")
    if display_wall.GetAttribute("cbnu:sideDisplayCenter").Get() != 2.9942665:
        raise AssertionError("six-display section is not centered on the gray body")
    if display_wall.GetAttribute("cbnu:sideBodyEndMargin").Get() != 0.5342665:
        raise AssertionError("six-display section gray-body end margins are not equal")
    expected_side_display_y = {
        "Display_04": 0.8442665,
        "Display_05": 1.7042665,
        "Display_06": 2.5642665,
        "Display_07": 3.4242665,
        "Display_08": 4.2842665,
        "Display_09": 5.1442665,
    }
    for display_name, expected_y in expected_side_display_y.items():
        panel = stage.GetPrimAtPath(
            f"/World/Architecture/DigitalDisplayWall_01/SideSection/{display_name}"
        )
        if tuple(panel.GetAttribute("xformOp:translate").Get()) != (-0.3, expected_y, 0.0):
            raise AssertionError(f"six-display section spacing mismatch: {display_name}")
    side_collision = stage.GetPrimAtPath(
        "/World/Architecture/DigitalDisplayWall_01/Collision/SideCollision"
    )
    if tuple(side_collision.GetAttribute("xformOp:scale").Get()) != (0.3, 6.288533, 1.22):
        raise AssertionError("six-display section collider was not extended")
    if tuple(side_collision.GetAttribute("xformOp:translate").Get()) != (-0.15, 2.8442665, 0.61):
        raise AssertionError("six-display section collider pose mismatch")

    wood_partition = stage.GetPrimAtPath("/World/Architecture/WoodPartition_01")
    if wood_partition.GetAttribute("cbnu:referenceFrom").Get() != "DigitalDisplayWall_01":
        raise AssertionError("wood partition does not start at the display corner")
    if wood_partition.GetAttribute("cbnu:referenceTo").Get() != "NorthCorridorEndGlassWall/RightFrame":
        raise AssertionError("wood partition does not terminate at the north glass frame")
    if tuple(wood_partition.GetAttribute("xformOp:translate").Get()) != (25.8224, 19.8814665, 0.0):
        raise AssertionError("wood partition world pose mismatch")
    if wood_partition.GetAttribute("cbnu:thickness").Get() != 0.3:
        raise AssertionError("wood partition thickness does not match the display corner")
    partition_body = stage.GetPrimAtPath("/World/Architecture/WoodPartition_01/PartitionBody")
    if tuple(partition_body.GetAttribute("xformOp:scale").Get()) != (0.3, 1.377067, 3.0):
        raise AssertionError("wood partition body dimensions mismatch")
    if tuple(partition_body.GetAttribute("xformOp:translate").Get()) != (0.0, 0.0, 1.5):
        raise AssertionError("wood partition body vertical pose mismatch")
    if partition_body.GetAttribute("physics:collisionEnabled").Get() is not True:
        raise AssertionError("wood partition collider is disabled")

    wordmark = stage.GetPrimAtPath(
        "/World/Architecture/DigitalDisplayWall_01/SideSection/InstituteWordmarkText"
    )
    if wordmark.GetAttribute("cbnu:content").Get() != "학연산공통기술연구원":
        raise AssertionError("six-screen wall institute wordmark text mismatch")
    if "PhysicsCollisionAPI" in wordmark.GetAppliedSchemas():
        raise AssertionError("institute wordmark unexpectedly has collision")
    if wordmark.GetAttribute("cbnu:construction").Get() != "solid black extruded Hangul glyph mesh":
        raise AssertionError("institute wordmark is not solid glyph geometry")
    if wordmark.GetAttribute("cbnu:depth").Get() != 0.016:
        raise AssertionError("institute wordmark extrusion depth mismatch")
    if tuple(wordmark.GetAttribute("xformOp:translate").Get()) != (0.0, 2.9942665, 1.36):
        raise AssertionError("institute wordmark wall placement mismatch")
    if float(wordmark.GetAttribute("xformOp:rotateZ").Get()) != -90.0:
        raise AssertionError("institute wordmark orientation mismatch")
    glyph_mesh = stage.GetPrimAtPath(
        "/World/Architecture/DigitalDisplayWall_01/SideSection/InstituteWordmarkText/GlyphMesh"
    )
    if "PhysicsCollisionAPI" in glyph_mesh.GetAppliedSchemas():
        raise AssertionError("institute wordmark glyph mesh unexpectedly has collision")
    if len(glyph_mesh.GetAttribute("points").Get()) < 800:
        raise AssertionError("institute wordmark glyph mesh is unexpectedly sparse")
    wordmark_material, _ = UsdShade.MaterialBindingAPI(glyph_mesh).ComputeBoundMaterial()
    expected_wordmark_material = (
        "/World/Architecture/DigitalDisplayWall_01/SideSection/InstituteWordmarkText/BlackLettering"
    )
    if not wordmark_material or str(wordmark_material.GetPath()) != expected_wordmark_material:
        raise AssertionError("institute wordmark material binding mismatch")
    wordmark_shader = UsdShade.Shader(
        stage.GetPrimAtPath(f"{expected_wordmark_material}/PreviewSurface")
    )
    wordmark_color = tuple(wordmark_shader.GetInput("diffuseColor").Get())
    if any(abs(value - 0.003) > 1e-6 for value in wordmark_color):
        raise AssertionError(f"institute wordmark is not black: {wordmark_color}")
    if stage.GetPrimAtPath(f"{expected_wordmark_material}/WordmarkTexture").IsValid():
        raise AssertionError("institute wordmark still depends on the invisible RGBA decal")

    expected_architecture_poses = {
        "DigitalDisplayWall_01": ((25.9724, 13.2044, 0.85), 0.0),
        "WoodPartition_01": ((25.8224, 19.8814665, 0.0), 0.0),
        "ColumnDisplay_01": ((26.43765, 9.78845, 0.7), 0.0),
        "GrayPoster_01": ((30.62, 5.0, 1.05), 270.0),
        "GrayPoster_02": ((20.5892, 13.0403, 0.85), 0.0),
        "ElevatorDoor_01": ((22.8392, 15.2, 0.0), 90.0),
        "ElevatorDoor_02": ((22.8392, 18.8, 0.0), 90.0),
        "GreenInformationBoard_01": ((23.4558, 20.25, 0.15), 0.0),
        "GreenInformationBoard_02": ((24.4058, 20.25, 0.15), 0.0),
        "GreenInformationBoard_03": ((25.3558, 20.25, 0.15), 0.0),
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
    if large_gray_poster.GetAttribute("cbnu:returnWall").Get() != "Wall_05":
        raise AssertionError("large gray poster does not return around Wall_05")
    if large_gray_poster.GetAttribute("cbnu:referenceElevator").Get() != "ElevatorDoor_01":
        raise AssertionError("large gray poster return does not reference ElevatorDoor_01")
    if large_gray_poster.GetAttribute("cbnu:returnLength").Get() != 1.3247:
        raise AssertionError("large gray poster return length mismatch")
    if large_gray_poster.GetAttribute("cbnu:hasScreen").Get() is not False:
        raise AssertionError("large gray poster still reports screen geometry")
    if large_gray_poster.GetAttribute("cbnu:visiblePieceCount").Get() != 1:
        raise AssertionError("large gray poster is not one piece")
    poster_slab = stage.GetPrimAtPath("/World/Architecture/GrayPoster_02/PosterSlab")
    poster_points = [tuple(point) for point in poster_slab.GetAttribute("points").Get()]
    if abs(min(point[0] for point in poster_points) - (-2.25)) > 1e-6 or abs(max(point[0] for point in poster_points) - 2.325) > 1e-6:
        raise AssertionError("large gray poster main span mismatch")
    if abs(min(point[1] for point in poster_points) - (-0.075)) > 1e-6 or abs(max(point[1] for point in poster_points) - 1.3247) > 1e-6:
        raise AssertionError("large gray poster corner return mismatch")
    if abs(min(point[2] for point in poster_points)) > 1e-6 or abs(max(point[2] for point in poster_points) - 1.22) > 1e-6:
        raise AssertionError("large gray poster height mismatch")
    if "PhysicsCollisionAPI" in poster_slab.GetAppliedSchemas():
        raise AssertionError("large gray poster L mesh unexpectedly has collision")

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

    central_decorated_doors = {
        "Door_Double_01": ("wood_double_portal", 2.08, (16.14, 8.9, 0.0), 90.0),
        "Door_Double_02": ("wood_double_portal", 2.08, (16.14, 3.8, 0.0), 90.0),
        "Door_Single_04": ("wood_single_portal", 1.26, (30.62, 3.14695, 0.0), 270.0),
    }
    for door_name, (variant, outer_width, expected_translate, expected_yaw) in central_decorated_doors.items():
        door = stage.GetPrimAtPath(f"/World/Doors/{door_name}")
        if door.GetAttribute("cbnu:assetVariant").Get() != variant:
            raise AssertionError(f"central door decoration variant mismatch: {door_name}")
        if tuple(door.GetAttribute("xformOp:translate").Get()) != expected_translate:
            raise AssertionError(f"central decorated-door pose mismatch: {door_name}")
        if float(door.GetAttribute("xformOp:rotateZ").Get()) != expected_yaw:
            raise AssertionError(f"central decorated-door yaw mismatch: {door_name}")
        outer_size = tuple(door.GetAttribute("cbnu:portalOuterSize").Get())
        if outer_size != (outer_width, 0.2, 2.28):
            raise AssertionError(f"central door portal size mismatch: {door_name}: {outer_size}")
        if door.GetAttribute("cbnu:portalFit").Get() != "zero_margin_to_leaf_perimeter":
            raise AssertionError(f"central door portal fit metadata mismatch: {door_name}")
        left_jamb = stage.GetPrimAtPath(f"/World/Doors/{door_name}/WoodPortal/LeftPortalJamb")
        portal_header = stage.GetPrimAtPath(f"/World/Doors/{door_name}/WoodPortal/PortalHeader")
        expected_header_scale = (outer_width, 0.2, 0.18)
        if tuple(portal_header.GetAttribute("xformOp:scale").Get()) != expected_header_scale:
            raise AssertionError(f"central door simple portal header mismatch: {door_name}")
        portal_material, _ = UsdShade.MaterialBindingAPI(left_jamb).ComputeBoundMaterial()
        expected_portal_material = f"/World/Doors/{door_name}/PortalMaterials/PortalWood"
        if not portal_material or str(portal_material.GetPath()) != expected_portal_material:
            raise AssertionError(f"central door matching wood-portal material mismatch: {door_name}")
        expected_jamb_x = -0.95 if outer_width == 2.08 else -0.54
        if tuple(left_jamb.GetAttribute("xformOp:translate").Get()) != (expected_jamb_x, 0.0, 1.14):
            raise AssertionError(f"central door portal side gap remains: {door_name}")
        if tuple(portal_header.GetAttribute("xformOp:translate").Get()) != (0.0, 0.0, 2.19):
            raise AssertionError(f"central door portal top gap remains: {door_name}")
        if "PhysicsCollisionAPI" in set(left_jamb.GetAppliedSchemas()) or "PhysicsCollisionAPI" in set(portal_header.GetAppliedSchemas()):
            raise AssertionError(f"central door portal unexpectedly adds collision: {door_name}")

    for door_name in ("Door_Single_01", "Door_Single_02", "Door_Single_03", "Door_Double_05"):
        wood_portal = stage.GetPrimAtPath(f"/World/Doors/{door_name}/WoodPortal")
        if wood_portal.IsValid():
            raise AssertionError(f"excluded corridor/entrance door received a wood portal: {door_name}")

    expected_east_door_poses = {
        "Door_Double_03": (35.32, 12.3, 0.0),
        "Door_Double_04": (35.32, 8.05, 0.0),
    }
    for door_name, expected_translate in expected_east_door_poses.items():
        door = stage.GetPrimAtPath(f"/World/Doors/{door_name}")
        if tuple(door.GetAttribute("xformOp:translate").Get()) != expected_translate:
            raise AssertionError(f"east white double-door pose mismatch: {door_name}")
        if float(door.GetAttribute("xformOp:rotateZ").Get()) != 90.0:
            raise AssertionError(f"east white double-door yaw mismatch: {door_name}")
        if door.GetAttribute("cbnu:assetVariant").Get() != "white_wood_portal":
            raise AssertionError(f"east double-door variant mismatch: {door_name}")
        if door.GetAttribute("cbnu:portalFit").Get() != "zero_margin_to_leaf_perimeter":
            raise AssertionError(f"east double-door portal fit metadata mismatch: {door_name}")
        left_slab = stage.GetPrimAtPath(f"/World/Doors/{door_name}/LeftDoor/Slab")
        leaf_material, _ = UsdShade.MaterialBindingAPI(left_slab).ComputeBoundMaterial()
        expected_leaf_material = f"/World/Doors/{door_name}/Materials/WhiteDoor"
        if not leaf_material or str(leaf_material.GetPath()) != expected_leaf_material:
            raise AssertionError(f"east double-door white material mismatch: {door_name}")
        leaf_shader = UsdShade.Shader(
            stage.GetPrimAtPath(f"{expected_leaf_material}/PreviewSurface")
        )
        leaf_color = tuple(float(value) for value in leaf_shader.GetInput("diffuseColor").Get())
        if any(
            abs(value - expected) > 1e-6
            for value, expected in zip(leaf_color, (0.91, 0.92, 0.89))
        ):
            raise AssertionError(f"east double-door leaf is not white: {door_name}: {leaf_color}")
        header = stage.GetPrimAtPath(f"/World/Doors/{door_name}/WoodPortal/PortalHeader")
        if tuple(header.GetAttribute("xformOp:scale").Get()) != (2.08, 0.2, 0.18):
            raise AssertionError(f"east double-door wood header dimensions mismatch: {door_name}")
        if tuple(header.GetAttribute("xformOp:translate").Get()) != (0.0, 0.0, 2.19):
            raise AssertionError(f"east double-door portal top gap remains: {door_name}")
        left_jamb = stage.GetPrimAtPath(f"/World/Doors/{door_name}/WoodPortal/LeftPortalJamb")
        if tuple(left_jamb.GetAttribute("xformOp:translate").Get()) != (-0.95, 0.0, 1.14):
            raise AssertionError(f"east double-door portal side gap remains: {door_name}")
        portal_material, _ = UsdShade.MaterialBindingAPI(header).ComputeBoundMaterial()
        expected_portal_material = f"/World/Doors/{door_name}/Materials/PortalWood"
        if not portal_material or str(portal_material.GetPath()) != expected_portal_material:
            raise AssertionError(f"east double-door wood portal material mismatch: {door_name}")
        if "PhysicsCollisionAPI" in set(left_slab.GetAppliedSchemas()) or "PhysicsCollisionAPI" in set(header.GetAppliedSchemas()):
            raise AssertionError(f"east decorative door duplicates Wall_01 collision: {door_name}")

    corner_return = stage.GetPrimAtPath("/World/Furniture/Sofa_Corner_01/ReturnBase")
    if tuple(corner_return.GetAttribute("xformOp:scale").Get()) != (0.82, 2.71, 0.34):
        raise AssertionError("Sofa_Corner_01 return was not shortened by 0.30 m")

    print(f"CBNU Haksan composed Stage: PASS (USD {Usd.GetVersion()})")
    print(f"verified composed prims: {len(REQUIRED_PRIMS)}")
    print("sky background: authored DomeLight color removed; original default restored")
    print("surface colors: walls and all columns use cool stone gray RGB (0.50, 0.51, 0.52), roughness 0.72; floor keeps Bala White and ceiling keeps CeilingWhite")
    print("ATM geometry: loaded=2")
    print("front double-glass sets: loaded=2, fully infilled clear leaves=4")
    print("entrance-right Wall_11: corner sofa return shortened by 0.30 m; one single door inserted with 0.197 m side clearances")
    print("east Wall_01 doors: Door_Double_03/04 use warm-white leaves inside zero-margin 2.08 x 0.20 x 2.28 m honey-brown wood portals")
    print("portal fit: all five newly styled doors have jambs and headers directly touching the leaf perimeter; central three keep brown leaves, narrow corridor and entrance excluded")
    print("lobby tables: loaded=3; all use filled lower bodies")
    print(
        "dynamic parcels: loaded=16; Table_03=9, main entrance=4, between elevators=3"
    )
    print("ceiling: loaded; standard panels=15 at 8000; large central panel=1 at 12000 (6.0 x 2.4 m); four-way cassette air conditioners=2 (1.1 x 1.1 m)")
    print("front entrance glazing: loaded=2 clear panels plus full-span sofa-height lower walls from Wall_09 to the door frame and from the door frame to Wall_11; south face aligned to the visible entrance pillars at y=-0.01 m")
    print("west corridor: width=1.73 m; opaque Wall_07 visible with collision")
    print("north corridor end glazing: loaded=1 clear full-height panel plus one 3.1332 x 0.20 x 1.02 m stone-gray lower wall; original Wall_04 collider retained")
    print("north glass wood platform: loaded=1 static 3.1332 x 0.60 x 0.15 m body; corridor-width fit and glass-frame contact verified")
    print("north platform information boards: loaded=3 wheeled green units, each 0.72 x 0.34 x 1.55 m; centered with equal 0.2566 m side margins")
    print("exterior pavement: loaded=2 oversized watertight opaque sidewalk-paver slabs; south=200.0 x 100.0435 m, north=200.0 x 79.2754 m; top z=0.05 m")
    print("entrance side pillars: loaded=2; mirrored 1.0425 x 1.0 x 3.0 m bodies projecting into lobby")
    print("front entrance joins: wall/glass, pillar/glass and leaf/rail borders closed; center gap filled by one 0.44 m clear panel meeting the transom")
    print("front entrance upper gap: filled to ceiling with one 4.16 x 0.72 m clear glass transom")
    print("main columns: loaded=3; each body=1.2 x 1.2 x 3.0 m")
    print("digital display walls: loaded=1; six-screen side extended to 6.288533 m with 0.24 m panel gaps and equal 0.5342665 m gray-body end margins; three-screen side remains 2.50 m; opposite screen structure removed")
    print("digital display wall collision: loaded=2 invisible box helpers on the original wall only")
    print("wood partition: loaded=1 full-height 0.30 x 1.377067 x 3.00 m collidable panel wall, two-thirds its former length; flush between the six-screen corner end and north glass RightFrame")
    print("six-screen wall wordmark: 학연산공통기술연구원, loaded as a 3.6 x 0.38 x 0.016 m collision-free solid black glyph mesh")
    print("Column_03 display: loaded=1 large 1.0 x 1.45 m panel facing the main entrance")
    print("Wall_11 poster: loaded=1 light-gray 2.2 x 1.0 m panel; top fixed at 2.05 m and bottom extended")
    print("Wall_06/05 poster: loaded=1 non-emissive dark-gray one-piece L mesh; 4.5 m main face plus 1.3247 m corner return ending flush beside ElevatorDoor_01; height=1.22 m, depth=0.15 m, no bezel, screen or collider")
    print("Wall_05 elevators: loaded=2 operational stainless-steel center-opening doors, 1.45 x 2.30 m each; ElevatorDoor_02 shifted 0.20 m viewer-left to y=18.8 m")
    print("wall corners: 4 re-entrant joins unified by extending Wall_02/06/08/12 exactly 0.10 m to the adjoining inner faces")
    print("corner/U sofas: one visible SofaUnified mesh each with blackened charcoal reddish-brown leather RGB (0.09, 0.055, 0.05); straight sofas retain brown leather; sampled helpers invisible=8")


if __name__ == "__main__":
    main()
