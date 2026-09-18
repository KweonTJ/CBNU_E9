#!/usr/bin/env python3
"""Generate mirrored two-flight stairs and non-destructive building overrides."""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'worlds/cbnu_haksan_2f_building/config/staircases.usda'
X0, X1 = 15.6392, 18.1392
Y0 = 13.0403
RISE = 3.2 / 18
TREAD = .28
RUN = 8 * TREAD
LANDING_DEPTH = 1.2
Y1 = Y0 + RUN + LANDING_DEPTH
OPENING = (X0, X1, Y0, Y1)
BAYS = {'Left': OPENING, 'Right': (28.3724,30.8724,13.2044,16.6444)}


def n(v):
    return f'{v:.8f}'.rstrip('0').rstrip('.') if v else '0'


def vec(values):
    return '(' + ', '.join(n(v) for v in values) + ')'


def footprint():
    geometry = json.loads((ROOT / 'worlds/cbnu_haksan_1f_corridor/config/geometry.json').read_text())
    return [(x, Y1 + .1 if abs(y - 15.1403) < 1e-6 else 16.7444 if abs(y-15.3044)<1e-6 else y)
            for x, y in geometry['corridor_polygon_xy']]


def inside(x, y, polygon):
    result = False
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        if (a[1] > y) != (b[1] > y):
            crossing = a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
            if x < crossing:
                result = not result
    return result


def slab_mesh(polygon, z0, z1, hole=False):
    """Closed, welded orthogonal slab; omit the stairwell from both surfaces."""
    xs = sorted(set(x for x, _ in polygon) | {x for b in BAYS.values() for x in b[:2]})
    ys = sorted(set(y for _, y in polygon) | {y for b in BAYS.values() for y in b[2:]})
    cells = set()
    for i in range(len(xs)-1):
        for j in range(len(ys)-1):
            x, y = (xs[i]+xs[i+1])/2, (ys[j]+ys[j+1])/2
            if inside(x, y, polygon) and not (hole and any(a<x<b and c<y<d for a,b,c,d in BAYS.values())):
                cells.add((i, j))
    points, lookup, faces = [], {}, []
    def face(vertices):
        indices = []
        for vertex in vertices:
            if vertex not in lookup:
                lookup[vertex] = len(points)
                points.append(vertex)
            indices.append(lookup[vertex])
        faces.append(indices)
    for i, j in sorted(cells):
        a,b,c,d = (xs[i],ys[j]), (xs[i+1],ys[j]), (xs[i+1],ys[j+1]), (xs[i],ys[j+1])
        top = [(*p,z1) for p in (a,b,c,d)]
        bottom = [(*p,z0) for p in (a,b,c,d)]
        face(top)
        face(bottom[::-1])
        for k, neighbor in enumerate(((i,j-1),(i+1,j),(i,j+1),(i-1,j))):
            if neighbor not in cells:
                m = (k+1)%4
                face([bottom[k],bottom[m],top[m],top[k]])
    return points, faces


def slab_override(name, polygon, z0, z1, hole=False):
    points, faces = slab_mesh(polygon, z0, z1, hole)
    return f'''over "{name}"
{{
    point3f[] points = [{', '.join(vec(p) for p in points)}]
    int[] faceVertexCounts = [{', '.join('4' for _ in faces)}]
    int[] faceVertexIndices = [{', '.join(str(i) for face in faces for i in face)}]
    texCoord2f[] primvars:st = [{', '.join(vec(p[:2]) for p in points)}]
    uniform token primvars:st:interpolation = "vertex"
    uniform token subdivisionScheme = "none"
    custom bool cbnu:stairOpening = {'true' if hole else 'false'}
}}'''


def cube(name, center, size, material='StairStone', rotate_x=0):
    return f'''def Cube "{name}" (
    prepend apiSchemas = ["MaterialBindingAPI", "PhysicsCollisionAPI"]
)
{{
    double size = 1
    bool physics:collisionEnabled = true
    rel material:binding = </World/Stairs_Left/{material}>
    double3 xformOp:translate = {vec(center)}
    double xformOp:rotateX = {n(rotate_x)}
    double3 xformOp:scale = {vec(size)}
    uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateX", "xformOp:scale"]
}}'''


def stair_parts(side='Left'):
    parts = []
    for flight in (0, 1):
        x = X0 + (.65 if flight == 0 else 1.85)
        centers = []
        for step in range(1, 9):
            y = Y0 + ((step-.5)*TREAD if flight == 0 else RUN-(step-.5)*TREAD)
            top = (step if flight == 0 else step+9)*RISE
            parts.append((f'Flight_{flight+1}_Step_{step:02d}',(x,y,top-.06),(1.1,TREAD,.12),'StairStone',0))
            front = y-TREAD/2+.0175 if flight == 0 else y+TREAD/2-.0175
            parts.append((f'Riser_{flight+1}_{step:02d}',(x,front,top-RISE/2),(1.1,.035,RISE),'StairStone',0))
            centers.append((y,top))
        # Two sloping stringers support the treads without filling the space below.
        ya,za = centers[0]
        yb,zb = centers[-1]
        if ya > yb:
            ya,yb,za,zb = yb,ya,zb,za
        slope = math.degrees(math.atan2(zb-za,yb-ya))
        for edge in (-1,1):
            parts.append((f'Stringer_{flight}_{edge+1}',(x+edge*.42,(ya+yb)/2,(za+zb)/2-.15),
                          (.10,math.hypot(yb-ya,zb-za)+.38,.16),'StairStone',slope))
        # Rails sit inside tread edges, with a clear width of approximately 1 m.
        for edge in (-1, 1):
            rail_x = x + edge*.505
            for step in (0,2,4,7):
                y,top = centers[step]
                parts.append((f'Post_{flight}_{edge+1}_{step}',(rail_x,y,top+.475),(.04,.04,.95),'RailMetal',0))
            ya,za = centers[0]
            yb,zb = centers[-1]
            if ya > yb:
                ya,yb,za,zb = yb,ya,zb,za
            slope = math.degrees(math.atan2(zb-za,yb-ya))
            parts.append((f'Handrail_{flight}_{edge+1}',(rail_x,(ya+yb)/2,(za+zb)/2+.95),
                          (.045,math.hypot(yb-ya,zb-za)+.08,.045),'RailMetal',slope))
    parts.append(('HalfLanding',((X0+X1)/2,Y0+RUN+.6,1.51),(2.5,1.2,.18),'StairStone',0))
    parts.append(('UpperExitRiser',(X0+1.85,Y0-.0175,3.2-RISE/2),(1.1,.035,RISE),'StairStone',0))
    # Guard the lower flight opening at the upper-floor edge, keeping the exit open.
    for index,x in enumerate((X0+.035,X0+.635,X0+1.255)):
        parts.append((f'UpperGuardPost_{index}',(x,Y0-.035,3.725),(.04,.04,1.05),'RailMetal',0))
    for index,z in enumerate((3.725,4.25)):
        parts.append((f'UpperGuardRail_{index}',(X0+.645,Y0-.035,z),(1.26,.045,.045),'RailMetal',0))
    if side == 'Right':
        rx0,rx1,ry0,_ = BAYS['Right']
        parts = [(name,(rx1-(center[0]-X0),center[1]+ry0-Y0,center[2]),size,material,angle)
                 for name,center,size,material,angle in parts]
    return parts


def wall_overrides(z, thickness):
    result = []
    for side,wall_ids in (('Left',(16,17,18)),('Right',(20,21,22))):
        x0,x1,y0,y1 = BAYS[side]
        length = y1-y0
        y = (y1+y0)/2+.1
        for number,x in ((wall_ids[0],x0-.1),(wall_ids[1],x1+.1)):
            result.append(f'''over "Wall_{number}"
{{
    double3 xformOp:translate = {vec((x,y,z))}
    double3 xformOp:scale = {vec((length,.2,thickness))}
}}''')
        result.append(f'''over "Wall_{wall_ids[2]}"
{{
    double3 xformOp:translate = {vec(((x0+x1)/2,y1+.1,z))}
}}''')
    return '\n'.join(result)


def material(name, color, roughness, metallic=0):
    return f'''def Material "{name}"
{{
    token outputs:surface.connect = </World/Stairs_Left/{name}/Surface.outputs:surface>
    def Shader "Surface"
    {{
        uniform token info:id = "UsdPreviewSurface"
        color3f inputs:diffuseColor = {vec(color)}
        float inputs:roughness = {roughness}
        float inputs:metallic = {metallic}
        token outputs:surface
    }}
}}'''


def stair_root(side):
    x0,x1,y0,y1 = BAYS[side]
    result = f'''def Xform "Stairs_{side}"
    {{
        custom double cbnu:floorToFloorHeight = 3.2
        custom double cbnu:landingHeight = 1.6
        custom int cbnu:risersPerFlight = 9
        custom double cbnu:riserHeight = {n(RISE)}
        custom double cbnu:treadDepth = .28
        custom double cbnu:flightWidth = 1.1
        custom double4 cbnu:clearBoundsXY = {vec(BAYS[side])}
{material('StairStone',(.60,.61,.59),.8)}
{material('RailMetal',(.20,.22,.23),.32,.7)}
{chr(10).join(cube(*part) for part in stair_parts(side))}
        def Xform "LandingLight" (
            prepend references = @../../../assets/architecture/ceiling/ceiling_panel_light.usda@
        )
        {{
            double3 xformOp:translate = {vec(((x0+x1)/2,y1,2.7))}
            double xformOp:rotateX = -90
            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateX"]
            over "Light"
            {{
                float inputs:intensity = 8000
            }}
        }}
    }}'''
    return result.replace('/World/Stairs_Left/',f'/World/Stairs_{side}/')


def build():
    polygon = footprint()
    layer = f'''#usda 1.0
(defaultPrim = "World")
over "World"
{{
    over "Environment"
    {{
{slab_override('Floor',polygon,-.1,0)}
{slab_override('Ceiling',polygon,3,3.1,True)}
        over "Walls"
        {{
{wall_overrides(1.5,3)}
        }}
        over "CeilingLights"
        {{
            over "CeilingLight_16" (active = false) {{}}
            over "CeilingLight_17" (active = false) {{}}
        }}
    }}
    over "Floor_02"
    {{
        over "Environment"
        {{
{slab_override('Floor',polygon,-.1,0,True)}
{slab_override('Ceiling',polygon,3,3.1)}
            over "Walls"
            {{
{wall_overrides(1.5,3)}
            }}
            over "CeilingLights"
            {{
                over "CeilingLight_16"
                {{
                    double3 xformOp:translate = {vec(((X0+X1)/2,Y0+RUN+.6,2.96))}
                }}
                over "CeilingLight_17"
                {{
                    double3 xformOp:translate = (29.6224, 16.0444, 2.96)
                }}
            }}
        }}
    }}
    over "InterFloorBand"
    {{
{wall_overrides(3.1,.2)}
    }}
{stair_root('Left')}
{stair_root('Right')}
}}
'''
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(layer)
    print(f'wrote {OUTPUT}: mirrored stairs, 18 risers each, landings 1.6 m, openings 2.5 x 3.44 m')


if __name__ == '__main__':
    build()
