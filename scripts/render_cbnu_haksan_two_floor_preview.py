#!/usr/bin/env python3
"""Draw a structural cutaway from the source footprint and composed floor spacing."""

import json
import re
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from update_cbnu_haksan_two_floor import CORRIDOR_LIGHT_POSITIONS, CORRIDOR_LIGHT_YAWS
from build_cbnu_haksan_staircase import footprint, slab_mesh, stair_parts, BAYS
from render_cbnu_haksan_staircase import box_faces

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'worlds/cbnu_haksan_1f_corridor'
OUTPUT = ROOT / 'worlds/cbnu_haksan_2f_building'


def main():
    geometry = json.loads((SOURCE / 'config/geometry.json').read_text())
    lights = json.loads((SOURCE / 'config/ceiling.json').read_text())['lights']
    polygon = np.array(footprint())
    stage_text = (OUTPUT / 'cbnu_haksan_2f_building.usda').read_text()
    offset = float(re.search(r'cbnu:floorToFloorHeight = ([\d.]+)', stage_text)[1])
    height = geometry['world']['wall_height']
    partition_block = re.search(r'def Cube "PartitionWall_01".*?\n\s*}', stage_text, re.S)[0]
    def partition_vector(attribute):
        return np.array([float(v) for v in re.search(attribute + r' = \(([^)]+)\)', partition_block)[1].split(',')])
    partition_center = partition_vector('xformOp:translate')
    partition_size = partition_vector('xformOp:scale')
    px,py,pz = partition_center
    pw,pd,ph = partition_size
    previous_y = float(re.search(r'cbnu:previousCenterY = ([\d.]+)', partition_block)[1])
    moved = py - previous_y
    fig = plt.figure(figsize=(14, 7.5))
    axis = fig.add_subplot(121, projection='3d')
    for index, z in enumerate((0, offset)):
        color = ('#8bbaca', '#e2b478')[index]
        points, faces = slab_mesh(footprint(),z-.1,z,hole=index == 1)
        floor = [[points[i] for i in face] for face in faces if all(abs(points[i][2]-z)<1e-6 for i in face)]
        axis.add_collection3d(Poly3DCollection(floor, facecolors=color, edgecolors='#334a59', alpha=.72, linewidths=1))
        wall_faces = []
        for i,(x,y) in enumerate(polygon):
            nx,ny = polygon[(i+1)%len(polygon)]
            wall_faces.append([(x,y,z),(nx,ny,z),(nx,ny,z+height),(x,y,z+height)])
        axis.add_collection3d(Poly3DCollection(wall_faces, facecolors='#b4bac1', edgecolors='#727d87', alpha=.13, linewidths=.4))
        for xmin,xmax,ymin,ymax in BAYS.values():
            axis.plot([xmin,xmax,xmax,xmin,xmin],[ymin,ymin,ymax,ymax,ymin],[z+.03]*5,color='#167a54',linewidth=1.6)
        floor_lights = lights + ([{'name': name, 'position': position, 'yaw_deg': CORRIDOR_LIGHT_YAWS[name]}
                                  for name, position in CORRIDOR_LIGHT_POSITIONS.items()] if index == 1 else [])
        for light in floor_lights:
            if index == 0 and light['name'] in ('CeilingLight_16', 'CeilingLight_17'):
                continue
            if index == 1 and light['name'] == 'CeilingLight_Central_Large':
                continue
            x,y,lz = light['position']
            if index == 1 and light['name'] == 'CeilingLight_16':
                y = 15.8803
            if index == 1 and light['name'] == 'CeilingLight_17':
                y = 16.0444
            if index == 1 and light['name'] == 'CeilingLight_15':
                y = 5.4
            if index == 1 and light['name'] == 'CeilingLight_09':
                y = 9.5
            if index == 1 and light['name'] in ('CeilingLight_12', 'CeilingLight_13', 'CeilingLight_14'):
                y = 12.25
            w,d = light.get('size',[1.2,.3])
            if light['yaw_deg'] == 90:
                w,d = d,w
            panel = [[(x-w/2,y-d/2,z+lz),(x+w/2,y-d/2,z+lz),(x+w/2,y+d/2,z+lz),(x-w/2,y+d/2,z+lz)]]
            axis.add_collection3d(Poly3DCollection(panel, facecolors='#fff19d',edgecolors='#bfa959',linewidths=.3))
        axis.text(36.3, 8, z+1.3, f'{index+1}F', fontsize=13, fontweight='bold')
    for side in BAYS:
        for name,center,size,material,angle in stair_parts(side):
            if material == 'StairStone':
                axis.add_collection3d(Poly3DCollection(box_faces(center,size,angle),facecolors='#c5c4b9',edgecolors='#666666',linewidths=.2))
    partition_face = [[(px-pw/2,py,offset),(px+pw/2,py,offset),
                       (px+pw/2,py,offset+ph),(px-pw/2,py,offset+ph)]]
    axis.add_collection3d(Poly3DCollection(partition_face, facecolors='#a6a6a6',edgecolors='#555555',linewidths=1))
    def facade_panel(xmin, xmax, zmin, zmax, color, y=.17):
        face = [[(xmin,y,offset+zmin),(xmax,y,offset+zmin),
                 (xmax,y,offset+zmax),(xmin,y,offset+zmax)]]
        axis.add_collection3d(Poly3DCollection(face, facecolors=color, edgecolors='#555555', linewidths=.6))
    for center in (18.775,23.5,28.225):
        facade_panel(center-2.425,center+2.425,1.02,2.9,'#a9dce4')
    facade_panel(16.0145,30.7536,0,1.02,'#b8b8b8',y=-.01)
    for xmin,xmax in ((20.3775,21.42),(25.58,26.6225)):
        facade_panel(xmin,xmax,0,3,'#8c8e88',y=-.01)
    axis.set(xlim=(0,38),ylim=(0,22),zlim=(-.1,6.7),xlabel='X [m]',ylabel='Y [m]',zlabel='Z [m]')
    axis.set_box_aspect((36,21,14))
    axis.view_init(elev=24,azim=-62)
    axis.set_title('Same footprint on both floors\nStructural cutaway; ceilings hidden')
    section = fig.add_subplot(122)
    for z,color,label in [(0,'#8bbaca','1F'),(offset,'#e2b478','2F')]:
        section.add_patch(Rectangle((0,z),5,height,facecolor=color,alpha=.22,edgecolor='#34495a',linewidth=2))
        section.add_patch(Rectangle((0,z-.1),5,.1,facecolor='#76818c'))
        section.add_patch(Rectangle((0,z+height),5,.1,facecolor='#d8dce0',edgecolor='#77808b',linewidth=.5))
        section.text(2.5,z+1.65,f'{label} — clear height 3.0 m',ha='center',fontsize=12,fontweight='bold')
        description = '21 lights; corridor lighting reinforced; furniture cleared' if z == offset else '16 ceiling lights + 2 stair landing lights'
        section.text(2.5,z+1.1,description,ha='center',fontsize=9)
        if z == offset:
            section.text(2.5,z+.65,'Matching front window; existing window spacing',ha='center',fontsize=9)
            section.text(2.5,z+.3,'Partition flush with corridor corner; AC units removed',ha='center',fontsize=9)
        section.text(5.2,z,f'Floor z={z:g} m',va='center',fontsize=10)
    section.annotate('Ceiling + floor slabs: 0.2 m',xy=(2.5,3.1),xytext=(2.5,2.45),ha='center',fontsize=10,arrowprops={'arrowstyle':'->'})
    section.text(5.2,offset+height+.1,'Roof z=6.3 m',va='center',fontsize=10)
    section.set(xlim=(-.2,7.4),ylim=(-.35,6.8),ylabel='Height [m]',title='Vertical section')
    section.set_xticks([])
    section.spines[['top','right','bottom']].set_visible(False)
    section.grid(axis='y',alpha=.15)
    fig.suptitle('CBNU Haksan — two-floor building',fontsize=17)
    fig.text(.5,.025,'Geometry schematic, not an Isaac Sim render. Both stairs connect floors through landings at z=1.6 m.',ha='center',fontsize=9,color='#475463')
    fig.tight_layout(rect=(0,.05,1,.94))
    path=OUTPUT / 'preview_two_floor_structure.png'
    fig.savefig(path,dpi=150,facecolor='white')
    plt.close(fig)
    print(f'wrote {path}')
    fig, plan = plt.subplots(figsize=(10,9))
    plan.fill(polygon[:,0],polygon[:,1],color='#edf0f2',edgecolor='#626b72',linewidth=3)
    for X0,X1,Y0,Y1 in BAYS.values():
        plan.add_patch(Rectangle((X0,Y0),X1-X0,Y1-Y0,facecolor='#e8d49e',edgecolor='#79643d'))
        plan.text((X0+X1)/2,(Y0+Y1)/2,'U-turn\nstairs',ha='center',va='center',fontsize=10)
    plan.add_patch(Rectangle((px-pw/2,py-pd/2),pw,pd,facecolor='#c34436',edgecolor='#a33228',zorder=4))
    plan.annotate('East wall connection',xy=(px+pw/2,py),xytext=(33,3.5),ha='center',arrowprops={'arrowstyle':'->'},fontsize=10)
    plan.annotate('West corridor corner',xy=(px-pw/2,py),xytext=(18.4,7),ha='center',arrowprops={'arrowstyle':'->'},fontsize=10)
    plan.plot([px-pw/2,px+pw/2],[previous_y,previous_y],linestyle='--',color='#8a8a8a',linewidth=1.5)
    plan.annotate(f'{moved:.2f} m toward elevators',xy=(px,py),xytext=(px,py-2.8),ha='center',arrowprops={'arrowstyle':'->'},fontsize=10)
    plan.text(px,py+1.8,f'New partition {pw:.2f} m | height {ph:g} m',ha='center',color='#a33228',fontsize=11)
    for index,(name,(x,y,_)) in enumerate(CORRIDOR_LIGHT_POSITIONS.items()):
        width, depth = (.3,1.2) if CORRIDOR_LIGHT_YAWS[name] == 90 else (1.2,.3)
        plan.add_patch(Rectangle((x-width/2,y-depth/2),width,depth,facecolor='#ffe074',edgecolor='#7e6621',zorder=5,
                                 label='4 added ceiling panels' if index == 0 else None))
    plan.legend(loc='upper right',fontsize=9)
    for index, cx in enumerate((18.775,23.5,28.225)):
        plan.plot([cx-2.425,cx+2.425],[.17,.17],color='#3b9fae',linewidth=4)
    plan.text(24.4,18,'Elevator corridor',ha='center',rotation=90,fontsize=10)
    plan.set(xlim=(14.5,36),ylim=(-1,22),xlabel='X [m]',ylabel='Y [m]',title='2F — partition aligned with west corridor corner')
    plan.set_aspect('equal')
    plan.grid(alpha=.18)
    fig.tight_layout()
    plan_path = OUTPUT / 'preview_upper_partition.png'
    fig.savefig(plan_path,dpi=150,facecolor='white')
    plt.close(fig)
    print(f'wrote {plan_path}')


if __name__ == '__main__':
    main()
