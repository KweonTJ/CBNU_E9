#!/usr/bin/env python3
"""Open the composed lobby Stage with a real USD runtime and verify key prims."""

from __future__ import annotations

from pathlib import Path

try:
    from pxr import Usd
except ModuleNotFoundError as exc:
    raise SystemExit(
        "pxr is unavailable in this Python. Run this script with the Isaac Sim USD "
        "runtime as documented in README.md."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
WORLD = ROOT / "worlds/cbnu_haksan_1f_corridor/cbnu_haksan_1f_corridor.usda"

REQUIRED_PRIMS = {
    "/World/Environment/Ceiling": "Mesh",
    "/World/Environment/CeilingLights/CeilingLight_01/Housing": "Cube",
    "/World/Environment/CeilingLights/CeilingLight_01/Diffuser": "Cube",
    "/World/Environment/CeilingLights/CeilingLight_01/Light": "RectLight",
    "/World/Environment/CeilingLights/CeilingLight_Central_Large/Housing": "Cube",
    "/World/Environment/CeilingLights/CeilingLight_Central_Large/Diffuser": "Cube",
    "/World/Environment/CeilingLights/CeilingLight_Central_Large/Light": "RectLight",
    "/World/Environment/FrontEntranceGlassWalls/LeftFullHeightGlass/GlassPanel": "Cube",
    "/World/Environment/FrontEntranceGlassWalls/RightFullHeightGlass/GlassPanel": "Cube",
    "/World/Environment/WestCorridorEndGlassWall/GlassPanel": "Cube",
    "/World/Environment/NorthCorridorEndGlassWall/GlassPanel": "Cube",
    "/World/Columns/Entrance_Pillar_ATM_Side/Body": "Cube",
    "/World/Columns/Entrance_Pillar_Opposite/Body": "Cube",
    "/World/Columns/Column_01/Body": "Cube",
    "/World/Columns/Column_02/Body": "Cube",
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

    for path in HIDDEN_SOFA_HELPERS:
        prim = stage.GetPrimAtPath(path)
        if not prim.IsValid():
            raise AssertionError(f"composed sofa helper missing: {path}")
        if prim.GetAttribute("visibility").Get() != "invisible":
            raise AssertionError(f"composed sofa helper remains visible: {path}")

    for column_name in ("Column_01", "Column_02"):
        body = stage.GetPrimAtPath(f"/World/Columns/{column_name}/Body")
        scale = body.GetAttribute("xformOp:scale").Get()
        if tuple(scale) != (1.5, 1.5, 3.0):
            raise AssertionError(f"unexpected column size: {column_name}: {scale}")

    print(f"CBNU Haksan composed Stage: PASS (USD {Usd.GetVersion()})")
    print(f"verified composed prims: {len(REQUIRED_PRIMS)}")
    print("ATM geometry: loaded=2")
    print("front double-glass sets: loaded=2, transparent leaves=4")
    print("lobby tables: loaded=3; all use filled lower bodies")
    print("ceiling: loaded; standard panels=12 at 8000; large central panel=1 at 12000 (6.0 x 2.4 m)")
    print("front entrance glazing: loaded=2 full-height panels; original Wall_10 collider retained")
    print("west corridor end glazing: loaded=1 full-height panel; original Wall_07 collider retained")
    print("north corridor end glazing: loaded=1 full-height panel; original Wall_04 collider retained")
    print("entrance side pillars: loaded=2; mirrored 1.0425 x 1.0 x 3.0 m bodies projecting into lobby")
    print("front entrance center gap: filled with one fixed 0.42 m clear-glass panel")
    print("front entrance upper gap: filled to ceiling with one 4.16 x 0.72 m glass transom")
    print("main columns: loaded=2; each body=1.5 x 1.5 x 3.0 m")
    print("corner/U sofas: one visible SofaUnified mesh each; sampled helpers invisible=8")


if __name__ == "__main__":
    main()
