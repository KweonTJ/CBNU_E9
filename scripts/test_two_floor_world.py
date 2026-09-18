#!/usr/bin/env python3
"""Verify composed two-floor geometry, material remapping and shared physics."""

from pathlib import Path
from pxr import Usd, UsdGeom, UsdShade
from test_cbnu_haksan_staircase import validate_staircase

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
    assert sum(p.GetTypeName() == 'RectLight' for p in active) == 39
    assert sum('PhysicsRigidBodyAPI' in p.GetAppliedSchemas() for p in active) == 16
    removed = ('/World/Doors', '/World/Furniture', '/World/DynamicObstacles',
               '/World/Environment/CeilingLights/CeilingLight_Central_Large',
               '/World/Environment/CeilingLights/AirConditioners',
               '/World/Columns/Column_01', '/World/Columns/Column_02', '/World/Columns/Column_03',
               '/World/Architecture/DigitalDisplayWall_01', '/World/Architecture/ColumnDisplay_01',
               '/World/Architecture/GrayPoster_01', '/World/Architecture/GrayPoster_02',
               '/World/Architecture/GreenInformationBoard_01', '/World/Architecture/GreenInformationBoard_02',
               '/World/Architecture/GreenInformationBoard_03')
    for path in removed:
        upper_path = path.replace('/World/', '/World/Floor_02/', 1)
        assert stage.GetPrimAtPath(path).IsActive(), path
        assert not stage.GetPrimAtPath(upper_path).IsActive(), upper_path
        assert not any(str(p.GetPath()) == upper_path or str(p.GetPath()).startswith(upper_path + '/') for p in active)
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
        if path in ('/World/Environment/Floor', '/World/Environment/Ceiling',
                    '/World/Environment/Walls/Wall_16', '/World/Environment/Walls/Wall_17', '/World/Environment/Walls/Wall_18',
                    '/World/Environment/Walls/Wall_20', '/World/Environment/Walls/Wall_21', '/World/Environment/Walls/Wall_22'):
            continue  # Stair extension and opening checked independently below.
        if any(path == '/World/Environment/CeilingLights/'+name or path.startswith('/World/Environment/CeilingLights/'+name+'/') for name in ('CeilingLight_16','CeilingLight_17')):
            continue  # Removed below the opening and moved above the stair landing.
        upper = stage.GetPrimAtPath(path.replace('/World/', '/World/Floor_02/', 1))
        lower = stage.GetPrimAtPath(path)
        # Removed upper-floor objects remain intact on the ground floor.
        if any(path == root or path.startswith(root + '/') for root in removed):
            assert lower.IsValid() and lower.IsActive() and lower.IsLoaded(), path
            if prim.IsA(UsdGeom.Boundable):
                original = source_bounds.ComputeWorldBound(prim).ComputeAlignedRange()
                actual = bounds.ComputeWorldBound(lower).ComputeAlignedRange()
                assert original == actual, path
            continue
        assert upper.IsValid() and upper.IsActive() and upper.IsLoaded(), path
        assert lower.IsValid() and upper.GetTypeName() == lower.GetTypeName() == prim.GetTypeName(), path
        assert set(upper.GetAppliedSchemas()) == set(prim.GetAppliedSchemas()), path
        if prim.IsA(UsdGeom.Boundable):
            original = source_bounds.ComputeWorldBound(prim).ComputeAlignedRange()
            if original.IsEmpty():
                continue
            for target, dz in ((lower, 0), (upper, offset)):
                box = bounds.ComputeWorldBound(target).ComputeAlignedRange()
                dy = -.6 if dz and path.startswith('/World/Environment/CeilingLights/CeilingLight_15/') else 0
                if dz and path.startswith('/World/Environment/CeilingLights/CeilingLight_09/'):
                    dy = .5
                if dz and any(path.startswith('/World/Environment/CeilingLights/' + name + '/') for name in ('CeilingLight_12', 'CeilingLight_13', 'CeilingLight_14')):
                    dy = .25
                for expected, actual in ((original.GetMin(), box.GetMin()), (original.GetMax(), box.GetMax())):
                    assert all(abs(actual[i] - expected[i] - (dz if i == 2 else dy if i == 1 else 0)) < 1e-5 for i in range(3)), path
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

    assert not stage.GetPrimAtPath('/World/Floor_02/Environment/FrontEntranceInfillWall')
    facade = '/World/Floor_02/Environment/FrontEntranceGlassWalls'
    window = stage.GetPrimAtPath(facade + '/CenterFullHeightGlass')
    glass = stage.GetPrimAtPath(facade + '/CenterFullHeightGlass/GlassPanel')
    assert UsdGeom.Imageable(glass).ComputeVisibility() != UsdGeom.Tokens.invisible
    box = bounds.ComputeWorldBound(glass).ComputeAlignedRange()
    for expected, actual in (((21.075, .1575, 3.29), box.GetMin()), ((25.925, .1825, 6.11), box.GetMax())):
        assert all(abs(actual[i] - expected[i]) < 1e-5 for i in range(3))
    centers = []
    for name in ('LeftFullHeightGlass', 'CenterFullHeightGlass', 'RightFullHeightGlass'):
        pane = stage.GetPrimAtPath(facade + '/' + name + '/GlassPanel')
        pane_box = bounds.ComputeWorldBound(pane).ComputeAlignedRange()
        assert pane.GetAttribute('xformOp:scale').Get() == glass.GetAttribute('xformOp:scale').Get()
        assert pane.GetRelationship('material:binding').GetTargets() == glass.GetRelationship('material:binding').GetTargets()
        centers.append(pane_box.GetMidpoint()[0])
    assert all(abs(centers[i+1] - centers[i] - 4.725) < 1e-6 for i in range(2))
    # Matching full-width panes extend into the retained opaque pillars.
    # Ensure pane intersections are completely concealed within those pillars.
    for side_name, pillar_name in (('LeftFullHeightGlass', 'Entrance_Pillar_ATM_Side'),
                                   ('RightFullHeightGlass', 'Entrance_Pillar_Opposite')):
        side_box = bounds.ComputeWorldBound(stage.GetPrimAtPath(facade + '/' + side_name + '/GlassPanel')).ComputeAlignedRange()
        pillar_box = bounds.ComputeWorldBound(stage.GetPrimAtPath('/World/Floor_02/Columns/' + pillar_name + '/Body')).ComputeAlignedRange()
        for axis in range(3):
            overlap_min = max(box.GetMin()[axis], side_box.GetMin()[axis])
            overlap_max = min(box.GetMax()[axis], side_box.GetMax()[axis])
            assert overlap_min <= overlap_max
            assert pillar_box.GetMin()[axis] <= overlap_min and overlap_max <= pillar_box.GetMax()[axis]
    for part in window.GetChildren():
        side = stage.GetPrimAtPath(facade + '/LeftFullHeightGlass/' + part.GetName())
        assert part.GetAttribute('xformOp:scale').Get() == side.GetAttribute('xformOp:scale').Get()
        assert part.GetRelationship('material:binding').GetTargets() == side.GetRelationship('material:binding').GetTargets()
        assert all(stage.GetPrimAtPath(p).IsValid() for p in part.GetRelationship('material:binding').GetTargets())
    collider = stage.GetPrimAtPath(window.GetRelationship('cbnu:collisionWall').GetTargets()[0])
    assert collider.IsActive() and collider.GetAttribute('physics:collisionEnabled').Get()
    collision_box = bounds.ComputeWorldBound(collider).ComputeAlignedRange()
    for axis in (0, 2):
        assert collision_box.GetMin()[axis] <= box.GetMin()[axis] + 1e-6
        assert collision_box.GetMax()[axis] >= box.GetMax()[axis] - 1e-6
    # Existing facade collider runs parallel just behind the decorative glass.
    assert abs(collision_box.GetMidpoint()[1] - box.GetMidpoint()[1]) < .2

    lower_ceiling = bounds.ComputeWorldBound(stage.GetPrimAtPath('/World/Environment/Ceiling')).ComputeAlignedRange()
    upper_floor = bounds.ComputeWorldBound(stage.GetPrimAtPath('/World/Floor_02/Environment/Floor')).ComputeAlignedRange()
    assert abs(lower_ceiling.GetMax()[2] - upper_floor.GetMin()[2]) < 1e-6, 'inter-floor slabs must meet without overlap/gap'
    assert abs(upper_floor.GetMax()[2] - 3.2) < 1e-6
    partition = stage.GetPrimAtPath('/World/Floor_02/Environment/PartitionWall_01')
    assert not stage.GetPrimAtPath('/World/Environment/PartitionWall_01')
    assert partition.GetAttribute('physics:collisionEnabled').Get() is True
    assert 'PhysicsCollisionAPI' in partition.GetAppliedSchemas()
    assert UsdGeom.Imageable(partition).ComputeVisibility() != UsdGeom.Tokens.invisible
    partition_box = bounds.ComputeWorldBound(partition).ComputeAlignedRange()
    west_box = bounds.ComputeWorldBound(stage.GetPrimAtPath('/World/Floor_02/Environment/Walls/Wall_08')).ComputeAlignedRange()
    east_box = bounds.ComputeWorldBound(stage.GetPrimAtPath('/World/Floor_02/Environment/Walls/Wall_01')).ComputeAlignedRange()
    assert abs(partition_box.GetMin()[0] - west_box.GetMax()[0]) < 1e-6
    assert abs(partition_box.GetMax()[0] - east_box.GetMin()[0]) < 1e-6
    for axis in (1, 2):
        assert abs(partition_box.GetMin()[axis] - west_box.GetMin()[axis]) < 1e-6
        assert abs(partition_box.GetMax()[axis] - west_box.GetMax()[axis]) < 1e-6
    for side_box in (west_box, east_box):
        assert side_box.GetMin()[1] <= partition_box.GetMin()[1] + 1e-6
        assert side_box.GetMax()[1] >= partition_box.GetMax()[1] - 1e-6
    assert abs(partition_box.GetMin()[2] - upper_floor.GetMax()[2]) < 1e-6
    ceiling_box = bounds.ComputeWorldBound(stage.GetPrimAtPath('/World/Floor_02/Environment/Ceiling')).ComputeAlignedRange()
    assert abs(partition_box.GetMax()[2] - ceiling_box.GetMin()[2]) < 1e-6
    material, _ = UsdShade.MaterialBindingAPI(partition).ComputeBoundMaterial()
    assert material and str(material.GetPath()) == '/World/Floor_02/Looks/WallColumnLightGray'
    for fixture in stage.GetPrimAtPath('/World/Floor_02/Environment/CeilingLights').GetChildren():
        fixture_box = bounds.ComputeWorldBound(fixture).ComputeAlignedRange()
        if not fixture_box.IsEmpty():
            assert any(fixture_box.GetMax()[i] <= partition_box.GetMin()[i] or fixture_box.GetMin()[i] >= partition_box.GetMax()[i] for i in range(3)), str(fixture.GetPath())
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
    for name in ('CeilingLight_04', 'CeilingLight_05', 'CeilingLight_12', 'CeilingLight_13', 'CeilingLight_14'):
        lower_light = stage.GetPrimAtPath(f'/World/Environment/CeilingLights/{name}/Light')
        upper_light = stage.GetPrimAtPath(f'/World/Floor_02/Environment/CeilingLights/{name}/Light')
        assert lower_light.GetAttribute('inputs:intensity').Get() == 8000
        assert upper_light.GetAttribute('inputs:intensity').Get() == 12000
    for name, x in (('CeilingLight_18', 21.5), ('CeilingLight_19', 24.0), ('CeilingLight_20', 26.5), ('CeilingLight_21', 30.8)):
        assert not stage.GetPrimAtPath(f'/World/Environment/CeilingLights/{name}')
        fixture = stage.GetPrimAtPath(f'/World/Floor_02/Environment/CeilingLights/{name}')
        light = stage.GetPrimAtPath(str(fixture.GetPath()) + '/Light')
        assert fixture.IsActive() and fixture.IsLoaded()
        assert light.GetAttribute('inputs:intensity').Get() == 12000
        assert light.GetAttribute('inputs:normalize').Get() is True
        matrix = UsdGeom.Xformable(light).ComputeLocalToWorldTransform(Usd.TimeCode.Default())
        for actual, expected in zip(matrix.ExtractTranslation(), (x, 12.2753, 6.115)):
            assert abs(actual - expected) < 1e-6
        assert matrix.TransformDir((0, 0, -1))[2] < -.999
        fixture_box = bounds.ComputeWorldBound(fixture).ComputeAlignedRange()
        expected_yaw = 0 if name == 'CeilingLight_21' else 90
        assert fixture.GetAttribute('xformOp:rotateZ').Get() == expected_yaw
        housing_box = bounds.ComputeWorldBound(fixture.GetChild('Housing')).ComputeAlignedRange()
        expected_xy = (1.3, .36) if expected_yaw == 0 else (.36, 1.3)
        assert all(abs(housing_box.GetSize()[i] - expected_xy[i]) < 1e-6 for i in (0, 1))
        assert fixture_box.GetMin()[1] > partition_box.GetMax()[1]
        assert fixture_box.GetMax()[1] < 13.0403
        for part in ('Housing', 'Diffuser'):
            targets = fixture.GetChild(part).GetRelationship('material:binding').GetTargets()
            assert targets and all(stage.GetPrimAtPath(p).IsValid() for p in targets)
    print(f'CBNU Haksan two-floor Stage: PASS; matched geometry/materials for {verified} shared boundable prims per floor')
    print('Upper entrance: matching 4.85 x 2.82 m fixed glass, same sill/frames; equal 4.725 m center spacing; existing side windows/pillars and ground entrance unchanged')
    print('clear height 3 m per floor; 2F walking surface 3.2 m; roof 6.3 m; touching floor/ceiling slabs; 22 wall bands')
    print('one PhysicsScene, one DomeLight, 39 panel lights (16 ground, 21 upper, 2 landings); upper large light removed; 16 rigid parcels on ground floor only')
    print('2F corridor: four added downward panels, five existing corridor/elevator panels boosted from 8000 to 12000; both stairwell lights adapted')
    print('Upper-floor regular doors, seating, tables, ATMs and parcels removed; both elevator doors restored; ground-floor objects preserved')
    print('Upper-floor corner/column displays, both gray posters and all three information boards removed with their frames and bases')
    print('Three upper-floor main columns removed, including collision; ground-floor columns and entrance-side pillars retained')
    print('2F partition centerline y=11.4103 continues Wall_08 with no corner offset; 19.2347 x 0.2 x 3 m; wall/floor/ceiling joints and fixture clearances verified')
    print('Both bays extended for mirrored two-flight stairs. Elevator motion is not implemented.')
    validate_staircase(stage, source)
    validate_staircase(stage, source, 'Right')


if __name__ == '__main__':
    main()
