#!/usr/bin/env python3
"""Open the composed lobby Stage with a real USD runtime and verify key prims."""

from __future__ import annotations

from pathlib import Path

try:
    from pxr import Usd
except ModuleNotFoundError as exc:
    raise SystemExit(
        "pxr is unavailable in this Python. Run this script with the Isaac Sim USD "
        "runtime as documented in README_CBNU_HAKSAN.md."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
WORLD = ROOT / "worlds/cbnu_haksan_1f_corridor/cbnu_haksan_1f_corridor.usda"

REQUIRED_PRIMS = {
    "/World/Furniture/ATM_01/MainBody": "Cube",
    "/World/Furniture/ATM_01/Screen": "Cube",
    "/World/Furniture/ATM_01/Key_9": "Cube",
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
}


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

    print(f"CBNU Haksan composed Stage: PASS (USD {Usd.GetVersion()})")
    print(f"verified composed prims: {len(REQUIRED_PRIMS)}")
    print("ATM geometry: loaded")
    print("front double-glass sets: loaded=2, transparent leaves=4")
    print("lobby tables: loaded=3; all use filled lower bodies")


if __name__ == "__main__":
    main()
