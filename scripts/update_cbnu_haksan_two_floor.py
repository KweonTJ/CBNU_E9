#!/usr/bin/env python3
"""Compose a furnished ground floor and cleared upper floor with matching windows."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'worlds/cbnu_haksan_1f_corridor/cbnu_haksan_1f_corridor.usda'
OUTPUT = ROOT / 'worlds/cbnu_haksan_2f_building/cbnu_haksan_2f_building.usda'
REFERENCE = '../cbnu_haksan_1f_corridor/cbnu_haksan_1f_corridor.usda'
FRONT_WINDOWS = ROOT / 'assets/architecture/windows/front_entrance_glass_walls.usda'


def upper_entrance_window():
    # Reuse the complete side window, including its sill, frames and materials.
    asset = FRONT_WINDOWS.read_text()
    window = asset.split('    def Xform "LeftFullHeightGlass"', 1)[1].split(
        '    def Xform "RightFullHeightGlass"', 1)[0].rstrip()
    window = '    def Xform "CenterFullHeightGlass"' + window
    window = window.replace('custom string cbnu:side = "left of entrance"', '''custom string cbnu:side = "upper entrance replacement"
        double3 xformOp:translate = (4.725, 0, 0)
        uniform token[] xformOpOrder = ["xformOp:translate"]
        custom rel cbnu:collisionWall = </World/Floor_02/Environment/Walls/Wall_10>''')
    window = window.replace('</FrontEntranceGlassWalls/',
                            '</World/Floor_02/Environment/FrontEntranceGlassWalls/')
    return '\n'.join('            ' + line if line.strip() else '' for line in window.splitlines())


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
    wall_specs = {}
    for name in walls:
        block = re.search(rf'def Cube "{name}".*?\n\s*}}', source, re.S)[0]
        def values(attribute):
            return [float(v) for v in re.search(rf'{attribute} = \(([^)]+)\)', block)[1].split(',')]
        scale, position = values('xformOp:scale'), values('xformOp:translate')
        wall_specs[name] = (scale[:], position[:])
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
    # Shift the partition toward the elevator while keeping both ends at walls.
    west_scale, west_position = wall_specs['Wall_09']
    corner_scale, corner_position = wall_specs['Wall_12']
    east_scale, east_position = wall_specs['Wall_01']
    partition_start = west_position[0] + west_scale[1] / 2
    partition_end = east_position[0] - east_scale[1] / 2
    partition_y = corner_position[1] + 1.0
    partition_size = (partition_end - partition_start, corner_scale[1], height)
    partition_position = ((partition_start + partition_end) / 2, partition_y, height / 2)
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
    custom string cbnu:layout = "upper floor cleared of three main columns, regular doors, furniture, parcels, ATMs, displays, posters and information boards; elevator doors retained; matching front windows"
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
        over "Doors" (
            active = false
        ) {{}}
        over "Furniture" (
            active = false
        ) {{}}
        over "DynamicObstacles" (
            active = false
        ) {{}}
        over "Columns"
        {{
            over "Column_01" (
                active = false
            ) {{}}
            over "Column_02" (
                active = false
            ) {{}}
            over "Column_03" (
                active = false
            ) {{}}
        }}
        over "Architecture"
        {{
            over "DigitalDisplayWall_01" (
                active = false
            ) {{}}
            over "ColumnDisplay_01" (
                active = false
            ) {{}}
            over "GrayPoster_01" (
                active = false
            ) {{}}
            over "GrayPoster_02" (
                active = false
            ) {{}}
            over "GreenInformationBoard_01" (
                active = false
            ) {{}}
            over "GreenInformationBoard_02" (
                active = false
            ) {{}}
            over "GreenInformationBoard_03" (
                active = false
            ) {{}}
        }}
        over "Environment"
        {{
            def Cube "PartitionWall_01" (
                prepend apiSchemas = ["MaterialBindingAPI", "PhysicsCollisionAPI"]
            )
            {{
                custom string cbnu:placement = "1 m north toward elevators from former corner line; spans Wall_09 to Wall_01"
                custom double cbnu:shiftTowardElevators = 1
                rel material:binding = </World/Floor_02/Looks/WallColumnLightGray>
                bool physics:collisionEnabled = true
                double size = 1
                double3 xformOp:translate = {vector(partition_position)}
                double3 xformOp:scale = {vector(partition_size)}
                uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
            }}
            over "CeilingLights"
            {{
                over "CeilingLight_Central_Large" (
                    active = false
                ) {{}}
                over "CeilingLight_15"
                {{
                    custom string cbnu:placementSource = "2F partition clearance; shifted 0.6 m south"
                    double3 xformOp:translate = (29, 5.4, 2.96)
                }}
            }}
            over "ExteriorSidewalkPavers" (
                active = false
            ) {{}}
            over "FrontEntranceGlassWalls"
            {{
                custom int cbnu:fullHeightGlassPanelCount = 3
                custom int cbnu:lowerFacadeWallPanelCount = 3
                custom string cbnu:placement = "three fixed windows; existing side windows and pillars retained"
                custom double cbnu:windowCenterSpacing = 4.725
{upper_entrance_window()}
            }}
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
