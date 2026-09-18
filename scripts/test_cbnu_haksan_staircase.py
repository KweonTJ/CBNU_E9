#!/usr/bin/env python3
"""Validate the usable stair route, slab opening and expanded enclosure in USD."""

from collections import Counter
from pxr import Usd, UsdGeom, UsdShade


def validate_staircase(stage, source, side='Left'):
    x0,y0 = (15.6392,13.0403) if side == 'Left' else (28.3724,13.2044)
    y1 = y0+3.44
    light_name = 'CeilingLight_16' if side == 'Left' else 'CeilingLight_17'
    side_walls = ('Wall_16','Wall_17') if side == 'Left' else ('Wall_20','Wall_21')
    back_wall = 'Wall_18' if side == 'Left' else 'Wall_22'
    bbox = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_])
    def bounds(path):
        return bbox.ComputeWorldBound(stage.GetPrimAtPath(path)).ComputeAlignedRange()
    root = '/World/Stairs_' + side
    stairs = stage.GetPrimAtPath(root)
    assert stairs and stairs.IsActive()
    assert stage.GetPrimAtPath('/World').GetAttribute('cbnu:interFloorConnectionBuilt').Get() is True
    assert stairs.GetAttribute('cbnu:landingHeight').Get() == 1.6
    assert stairs.GetAttribute('cbnu:risersPerFlight').Get() == 9
    assert abs(stairs.GetAttribute('cbnu:riserHeight').Get() - 3.2/18) < 1e-8
    assert not stage.GetPrimAtPath('/World/Environment/CeilingLights/'+light_name).IsActive()
    assert source.GetPrimAtPath('/World/Environment/CeilingLights/'+light_name).IsActive()
    assert bounds(root+'/HalfLanding').GetMax()[2] == 1.6
    assert abs(bounds(root+'/HalfLanding').GetSize()[1] - 1.2) < 1e-6
    for prim in stairs.GetChildren():
        if prim.IsA(UsdGeom.Cube):
            assert prim.GetAttribute('physics:collisionEnabled').Get() is True
            material, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
            assert material, str(prim.GetPath())

    def mesh_data(path):
        prim = stage.GetPrimAtPath(path)
        mesh = UsdGeom.Mesh(prim)
        points = list(mesh.GetPointsAttr().Get())
        counts = list(mesh.GetFaceVertexCountsAttr().Get())
        indices = list(mesh.GetFaceVertexIndicesAttr().Get())
        edges, faces, cursor = Counter(), [], 0
        for count in counts:
            face = indices[cursor:cursor+count]
            cursor += count
            assert len(set(face)) == count
            for a,b in zip(face,face[1:]+face[:1]):
                edges[tuple(sorted((a,b)))] += 1
            faces.append([points[i] for i in face])
        assert cursor == len(indices)
        assert set(edges.values()) == {2}, path  # Closed manifold, including hole walls.
        assert len(mesh.GetPrim().GetAttribute('primvars:st').Get()) == len(points)
        assert prim.GetAttribute('physics:collisionEnabled').Get() is True
        material, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
        assert material
        return faces

    slab_paths = ('/World/Environment/Floor', '/World/Environment/Ceiling',
                  '/World/Floor_02/Environment/Floor','/World/Floor_02/Environment/Ceiling')
    surfaces = {path: mesh_data(path) for path in slab_paths}
    def covering(path, x, y):
        return [face for face in surfaces[path] if max(p[2] for p in face)-min(p[2] for p in face)<1e-6
                and min(p[0] for p in face)-1e-5 <= x <= max(p[0] for p in face)+1e-5
                and min(p[1] for p in face)-1e-5 <= y <= max(p[1] for p in face)+1e-5]

    route = []
    for flight in (1,2):
        previous = 0 if flight == 1 else 1.6
        lane = .65 if (flight == 1) == (side == 'Left') else 1.85
        for step in range(1,9):
            box = bounds(f'{root}/Flight_{flight}_Step_{step:02d}')
            top = box.GetMax()[2]
            assert abs(top-previous-3.2/18) < 1e-6
            assert abs(box.GetSize()[0]-1.1) < 1e-6
            assert abs(box.GetSize()[1]-.28) < 1e-6
            assert abs(box.GetSize()[2]-.12) < 1e-6
            previous = top
            x,y,_ = box.GetMidpoint()
            expected_y = y0 + ((step-.5)*.28 if flight == 1 else 2.24-(step-.5)*.28)
            assert abs(x-(x0+lane)) < 1e-6 and abs(y-expected_y) < 1e-6, ('stair position',side,flight,step,x,y)
            route.append((x,y,top))
        assert abs((1.6 if flight == 1 else 3.2)-previous-3.2/18) < 1e-6
    route.extend((x0+x,y0+2.84,1.6) for x in (.65,1.25,1.85))
    for x,y,z in route:
        assert not covering(slab_paths[1],x,y), ('ceiling blocks stair',x,y)
        assert not covering(slab_paths[2],x,y), ('upper floor blocks stair',x,y)
        assert covering(slab_paths[0],x,y) and covering(slab_paths[3],x,y)
        assert 6.2-z >= 2.0
        # Guardrails and lighting must not intersect a 2 m high walking centerline.
        for prim in Usd.PrimRange(stairs):
            if prim.IsA(UsdGeom.Boundable):
                obstacle = bbox.ComputeWorldBound(prim).ComputeAlignedRange()
                if obstacle.IsEmpty():
                    continue
                if obstacle.GetMin()[0] < x < obstacle.GetMax()[0] and obstacle.GetMin()[1] < y < obstacle.GetMax()[1]:
                    assert obstacle.GetMax()[2] <= z+1e-6 or obstacle.GetMin()[2] >= z+2, str(prim.GetPath())
    # Upper arrival and lower entry meet the corridor slab, no gap or extra step.
    for x in (x0+.65,x0+1.85):
        assert covering(slab_paths[0],x,y0-.03)
        assert covering(slab_paths[2],x,y0-.03)
    # The space under the upper flight near its entrance is open from the floor.
    under_x, under_y = x0+(1.85 if side == 'Left' else .65),y0+.14
    for prim in Usd.PrimRange(stairs):
        if prim.IsA(UsdGeom.Boundable):
            box = bbox.ComputeWorldBound(prim).ComputeAlignedRange()
            if not box.IsEmpty() and box.GetMin()[0] < under_x < box.GetMax()[0] and box.GetMin()[1] < under_y < box.GetMax()[1]:
                assert box.GetMin()[2] > 2.65, ('under-stair space is filled',str(prim.GetPath()))
    for prefix,z in (('/World/Environment',0),('/World/Floor_02/Environment',3.2)):
        back = bounds(prefix+'/Walls/'+back_wall)
        assert abs(back.GetMin()[1]-y1) < 1e-6
        assert abs(back.GetMin()[2]-z) < 1e-6
        for name in side_walls:
            side_box = bounds(prefix+'/Walls/'+name)
            assert abs(side_box.GetSize()[1]-3.44) < 1e-6
            assert side_box.GetMax()[1] >= back.GetMin()[1]
    upper_light = stage.GetPrimAtPath('/World/Floor_02/Environment/CeilingLights/'+light_name+'/Light')
    light_pos = UsdGeom.Xformable(upper_light).ComputeLocalToWorldTransform(Usd.TimeCode.Default()).ExtractTranslation()
    assert abs(light_pos[1]-(y0+2.84))<1e-6 and abs(light_pos[2]-6.115)<1e-6
    print(f'{side} stairs: PASS; 18 risers of 0.17778 m, 0.28 m treads, 1.6 m U-turn landing, 1.1 m flights; open slabs, open underside, 2 m headroom and static collision verified')
