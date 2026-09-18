#!/usr/bin/env python3
"""Verify composed two-floor geometry, material remapping and shared physics."""

from pathlib import Path
from pxr import Usd, UsdGeom, UsdShade

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'worlds/cbnu_haksan_1f_corridor/cbnu_haksan_1f_corridor.usda'
WORLD = ROOT / 'worlds/cbnu_haksan_2f_building/cbnu_haksan_2f_building.usda'


def main():
    source = Usd.Stage.Open(str(SOURCE))
    stage = Usd.Stage.Open(str(WORLD))
    assert source and stage
    for reference in stage.GetRootLayer().GetExternalReferences():
        assert (WORLD.parent / reference).resolve().is_file(), reference
    world = stage.GetPrimAtPath('/World')
    assert world.GetAttribute('cbnu:floorCount').Get() == 2
    offset = world.GetAttribute('cbnu:floorToFloorHeight').Get()
    assert abs(offset - 3.2) < 1e-6
    active = list(stage.Traverse())
    assert sum(p.GetTypeName() == 'PhysicsScene' for p in active) == 1
    assert sum(p.GetTypeName() == 'DomeLight' for p in active) == 1
    assert sum(p.GetTypeName() == 'RectLight' for p in active) == 36
    assert sum('PhysicsRigidBodyAPI' in p.GetAppliedSchemas() for p in active) == 32
    assert not stage.GetPrimAtPath('/World/Floor_02/Environment/ExteriorSidewalkPavers').IsActive()
    assert stage.GetPrimAtPath('/World/Environment/ExteriorSidewalkPavers').IsActive()

    source_bounds = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_])
    bounds = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_])
    verified = 0
    for prim in source.Traverse():
        path = str(prim.GetPath())
        if not path.startswith('/World/') or path.startswith('/World/Environment/ExteriorSidewalkPavers'):
            continue
        if path in ('/World/PhysicsScene', '/World/DomeLight'):
            continue
        upper = stage.GetPrimAtPath(path.replace('/World/', '/World/Floor_02/', 1))
        lower = stage.GetPrimAtPath(path)
        assert upper.IsValid() and upper.IsActive() and upper.IsLoaded(), path
        assert lower.IsValid() and upper.GetTypeName() == lower.GetTypeName() == prim.GetTypeName(), path
        assert set(upper.GetAppliedSchemas()) == set(prim.GetAppliedSchemas()), path
        if prim.IsA(UsdGeom.Boundable):
            original = source_bounds.ComputeWorldBound(prim).ComputeAlignedRange()
            if original.IsEmpty():
                continue
            for target, dz in ((lower, 0), (upper, offset)):
                box = bounds.ComputeWorldBound(target).ComputeAlignedRange()
                for expected, actual in ((original.GetMin(), box.GetMin()), (original.GetMax(), box.GetMax())):
                    assert all(abs(actual[i] - expected[i] - (dz if i == 2 else 0)) < 1e-5 for i in range(3)), path
            if prim.HasAPI(UsdShade.MaterialBindingAPI):
                material, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
                if material:
                    upper_material, _ = UsdShade.MaterialBindingAPI(upper).ComputeBoundMaterial()
                    expected_path = str(material.GetPath()).replace('/World/', '/World/Floor_02/', 1)
                    assert upper_material and str(upper_material.GetPath()) == expected_path, path
            else:
                # Legacy source assets author direct bindings without applying the API.
                for relationship in prim.GetRelationships():
                    if relationship.GetName().startswith('material:binding'):
                        expected = [str(p).replace('/World/', '/World/Floor_02/', 1) for p in relationship.GetTargets()]
                        actual = [str(p) for p in upper.GetRelationship(relationship.GetName()).GetTargets()]
                        assert actual == expected and all(stage.GetPrimAtPath(p).IsValid() for p in actual), path
            verified += 1

    lower_ceiling = bounds.ComputeWorldBound(stage.GetPrimAtPath('/World/Environment/Ceiling')).ComputeAlignedRange()
    upper_floor = bounds.ComputeWorldBound(stage.GetPrimAtPath('/World/Floor_02/Environment/Floor')).ComputeAlignedRange()
    assert abs(lower_ceiling.GetMax()[2] - upper_floor.GetMin()[2]) < 1e-6, 'inter-floor slabs must meet without overlap/gap'
    assert abs(upper_floor.GetMax()[2] - 3.2) < 1e-6
    bands = stage.GetPrimAtPath('/World/InterFloorBand').GetChildren()
    assert len(bands) == len(stage.GetPrimAtPath('/World/Environment/Walls').GetChildren()) == 22
    for band in bands:
        assert band.GetAttribute('physics:collisionEnabled').Get() is True
        box = bounds.ComputeWorldBound(band).ComputeAlignedRange()
        assert abs(box.GetMin()[2]-3.0) < 1e-6 and abs(box.GetMax()[2]-3.2) < 1e-6
        material, _ = UsdShade.MaterialBindingAPI(band).ComputeBoundMaterial()
        assert material and str(material.GetPath()) == '/World/Looks/WallColumnLightGray'
    for name in ('CeilingLight_16', 'CeilingLight_17'):
        light = stage.GetPrimAtPath(f'/World/Floor_02/Environment/CeilingLights/{name}/Light')
        assert light.GetAttribute('inputs:intensity').Get() == 8000
        matrix = UsdGeom.Xformable(light).ComputeLocalToWorldTransform(Usd.TimeCode.Default())
        assert abs(matrix.ExtractTranslation()[2] - 6.115) < 1e-6
    print(f'CBNU Haksan two-floor Stage: PASS; matched geometry/materials for {verified} boundable prims per floor')
    print('clear height 3 m per floor; 2F walking surface 3.2 m; roof 6.3 m; touching floor/ceiling slabs; 22 wall bands')
    print('one PhysicsScene, one DomeLight, 36 panel lights, 32 rigid parcels; exterior pavement only at ground level')
    print('Both display-end rooms and their lights are present on both floors. Inter-floor stairs/elevator motion are not implemented.')


if __name__ == '__main__':
    main()
