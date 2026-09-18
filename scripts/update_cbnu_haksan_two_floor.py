#!/usr/bin/env python3
"""Compose two identical lobby floors while retaining the editable 1F source."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'worlds/cbnu_haksan_1f_corridor/cbnu_haksan_1f_corridor.usda'
OUTPUT = ROOT / 'worlds/cbnu_haksan_2f_building/cbnu_haksan_2f_building.usda'
REFERENCE = '../cbnu_haksan_1f_corridor/cbnu_haksan_1f_corridor.usda'


def number(value):
    return f'{value:.7f}'.rstrip('0').rstrip('.') if value else '0'


def vector(values):
    return '(' + ', '.join(number(v) for v in values) + ')'


def main():
    geometry = json.loads((SOURCE.parent / 'config/geometry.json').read_text())
    height = geometry['world']['wall_height']
    ceiling_height = geometry['world']['ceiling_height']
    assert height == ceiling_height, 'Wall/ceiling heights must match before stacking'
    band_height = geometry['world']['ceiling_thickness'] + geometry['world']['floor_thickness']
    floor_offset = height + band_height
    source = SOURCE.read_text()
    walls = re.findall(r'def Cube "(Wall_\d+)".*?\n\s*}', source, re.S)
    if not walls:
        raise ValueError('No source walls found')
    bands = []
    for name in walls:
        block = re.search(rf'def Cube "{name}".*?\n\s*}}', source, re.S)[0]
        def values(attribute):
            return [float(v) for v in re.search(rf'{attribute} = \(([^)]+)\)', block)[1].split(',')]
        scale, position = values('xformOp:scale'), values('xformOp:translate')
        scale[2], position[2] = band_height, height + band_height / 2
        rotation = float(re.search(r'xformOp:rotateZ = ([\d.-]+)', block)[1])
        bands.append(f'''        def Cube "{name}" (
            prepend apiSchemas = ["PhysicsCollisionAPI"]
        )
        {{
            double size = 1
            bool physics:collisionEnabled = true
            double3 xformOp:translate = {vector(position)}
            double xformOp:rotateZ = {number(rotation)}
            double3 xformOp:scale = {vector(scale)}
            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateZ", "xformOp:scale"]
        }}''')
    result = f'''#usda 1.0
(
    defaultPrim = "World"
    metersPerUnit = 1
    upAxis = "Z"
    customLayerData = {{
        string generator = "scripts/update_cbnu_haksan_two_floor.py"
        dictionary cameraSettings = {{
            dictionary Perspective = {{
                double3 position = (43, -16, 15)
                double3 target = (24, 10, 3)
            }}
        }}
    }}
)

def Xform "World" (
    prepend references = @{REFERENCE}@</World>
)
{{
    custom int cbnu:floorCount = 2
    custom double cbnu:floorToFloorHeight = {number(floor_offset)}
    custom double cbnu:clearFloorHeight = {number(height)}
    custom string cbnu:layout = "same lobby layout on both floors"
    custom bool cbnu:interFloorConnectionBuilt = false

    def Xform "Floor_02" (
        prepend references = @{REFERENCE}@</World>
    )
    {{
        custom int cbnu:floorNumber = 2
        double3 xformOp:translate = (0, 0, {number(floor_offset)})
        uniform token[] xformOpOrder = ["xformOp:translate"]

        over "PhysicsScene" (
            active = false
        ) {{}}
        over "DomeLight" (
            active = false
        ) {{}}
        over "Environment"
        {{
            over "ExteriorSidewalkPavers" (
                active = false
            ) {{}}
        }}
    }}

    def Xform "InterFloorBand" (
        prepend apiSchemas = ["MaterialBindingAPI"]
    )
    {{
        custom double cbnu:height = {number(band_height)}
        rel material:binding = </World/Looks/WallColumnLightGray>
{chr(10).join(bands)}
    }}
}}
'''
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(result)
    print(f'wrote {OUTPUT}: 2 floors, {floor_offset:g} m floor spacing, {len(bands)} connecting wall bands')


if __name__ == '__main__':
    main()
