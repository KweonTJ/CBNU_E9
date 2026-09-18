#!/usr/bin/env python3
"""Draw a structural cutaway from the source footprint and composed floor spacing."""

import json
import re
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'worlds/cbnu_haksan_1f_corridor'
OUTPUT = ROOT / 'worlds/cbnu_haksan_2f_building'


def main():
    geometry = json.loads((SOURCE / 'config/geometry.json').read_text())
    lights = json.loads((SOURCE / 'config/ceiling.json').read_text())['lights']
    polygon = np.array(geometry['corridor_polygon_xy'])
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
    fig = plt.figure(figsize=(14, 7.5))
    axis = fig.add_subplot(121, projection='3d')
    for index, z in enumerate((0, offset)):
        color = ('#8bbaca', '#e2b478')[index]
        floor = [[(x,y,z) for x,y in polygon]]
        axis.add_collection3d(Poly3DCollection(floor, facecolors=color, edgecolors='#334a59', alpha=.72, linewidths=1))
        wall_faces = []
        for i,(x,y) in enumerate(polygon):
            nx,ny = polygon[(i+1)%len(polygon)]
            wall_faces.append([(x,y,z),(nx,ny,z),(nx,ny,z+height),(x,y,z+height)])
        axis.add_collection3d(Poly3DCollection(wall_faces, facecolors='#b4bac1', edgecolors='#727d87', alpha=.13, linewidths=.4))
        for bay in geometry['display_end_bays']:
            xmin,xmax,ymin,ymax = bay['clear_bounds_xy']
            axis.plot([xmin,xmax,xmax,xmin,xmin],[ymin,ymin,ymax,ymax,ymin],[z+.03]*5,color='#167a54',linewidth=1.6)
        for light in lights:
            if index == 1 and light['name'] == 'CeilingLight_Central_Large':
                continue
            x,y,lz = light['position']
            if index == 1 and light['name'] == 'CeilingLight_15':
                y = 5.4
            w,d = light.get('size',[1.2,.3])
            if light['yaw_deg'] == 90:
                w,d = d,w
            panel = [[(x-w/2,y-d/2,z+lz),(x+w/2,y-d/2,z+lz),(x+w/2,y+d/2,z+lz),(x-w/2,y+d/2,z+lz)]]
            axis.add_collection3d(Poly3DCollection(panel, facecolors='#fff19d',edgecolors='#bfa959',linewidths=.3))
        axis.text(36.3, 8, z+1.3, f'{index+1}F', fontsize=13, fontweight='bold')
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
        description = '17 lights; elevator doors restored; furniture cleared' if z == offset else 'Original rooms, furniture and 18 lights'
        section.text(2.5,z+1.1,description,ha='center',fontsize=9)
        if z == offset:
            section.text(2.5,z+.65,'Matching front window; existing window spacing',ha='center',fontsize=9)
            section.text(2.5,z+.3,f'Partition: {pw:.2f} m long; shifted 1 m toward elevators',ha='center',fontsize=9)
        section.text(5.2,z,f'Floor z={z:g} m',va='center',fontsize=10)
    section.annotate('Ceiling + floor slabs: 0.2 m',xy=(2.5,3.1),xytext=(2.5,2.45),ha='center',fontsize=10,arrowprops={'arrowstyle':'->'})
    section.text(5.2,offset+height+.1,'Roof z=6.3 m',va='center',fontsize=10)
    section.set(xlim=(-.2,7.4),ylim=(-.35,6.8),ylabel='Height [m]',title='Vertical section')
    section.set_xticks([])
    section.spines[['top','right','bottom']].set_visible(False)
    section.grid(axis='y',alpha=.15)
    fig.suptitle('CBNU Haksan — two-floor building',fontsize=17)
    fig.text(.5,.025,'Geometry schematic, not an Isaac Sim render. Floor access stairs/elevator motion are not added.',ha='center',fontsize=9,color='#475463')
    fig.tight_layout(rect=(0,.05,1,.94))
    path=OUTPUT / 'preview_two_floor_structure.png'
    fig.savefig(path,dpi=150,facecolor='white')
    plt.close(fig)
    print(f'wrote {path}')
    fig, plan = plt.subplots(figsize=(10,9))
    plan.fill(polygon[:,0],polygon[:,1],color='#edf0f2',edgecolor='#626b72',linewidth=3)
    plan.add_patch(Rectangle((px-pw/2,py-pd/2),pw,pd,facecolor='#c34436',edgecolor='#a33228',zorder=4))
    plan.annotate('East wall connection',xy=(px+pw/2,py),xytext=(33,3.5),ha='center',arrowprops={'arrowstyle':'->'},fontsize=10)
    plan.annotate('Opposite wall',xy=(px-pw/2,py),xytext=(18.2,3.5),ha='center',arrowprops={'arrowstyle':'->'},fontsize=10)
    plan.plot([px-pw/2,30.6536],[py-1,py-1],linestyle='--',color='#8a8a8a',linewidth=1.5)
    plan.annotate('1 m toward elevators',xy=(px,py),xytext=(px,py-2.4),ha='center',arrowprops={'arrowstyle':'->'},fontsize=10)
    plan.text(px,py+1.2,f'New partition {pw:.2f} m | height {ph:g} m',ha='center',color='#a33228',fontsize=11)
    for index, cx in enumerate((18.775,23.5,28.225)):
        plan.plot([cx-2.425,cx+2.425],[.17,.17],color='#3b9fae',linewidth=4)
    plan.text(24.4,18,'Elevator corridor',ha='center',rotation=90,fontsize=10)
    plan.set(xlim=(14.5,36),ylim=(-1,22),xlabel='X [m]',ylabel='Y [m]',title='2F — partition moved toward elevator corridor')
    plan.set_aspect('equal')
    plan.grid(alpha=.18)
    fig.tight_layout()
    plan_path = OUTPUT / 'preview_upper_partition.png'
    fig.savefig(plan_path,dpi=150,facecolor='white')
    plt.close(fig)
    print(f'wrote {plan_path}')


if __name__ == '__main__':
    main()
