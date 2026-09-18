#!/usr/bin/env python3
"""Draw the generated stair geometry as a cutaway and plan (not a Sim render)."""

import math
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from build_cbnu_haksan_staircase import BAYS, RUN, TREAD, stair_parts

ROOT = Path(__file__).resolve().parents[1]


def box_faces(center,size,angle=0):
    points = np.array([(x,y,z) for x in (-.5,.5) for y in (-.5,.5) for z in (-.5,.5)]) * np.array(size)
    c,s = math.cos(math.radians(angle)),math.sin(math.radians(angle))
    rotation = np.array(((1,0,0),(0,c,-s),(0,s,c)))
    points = points @ rotation.T + np.array(center)
    return [[points[i] for i in face] for face in ((0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3))]


def main(side='Left'):
    X0, X1, Y0, Y1 = BAYS[side]
    entry_x = X0 + (.65 if side == 'Left' else 1.85)
    exit_x = X0 + (1.85 if side == 'Left' else .65)
    fig = plt.figure(figsize=(14,9))
    ax = fig.add_subplot(121,projection='3d')
    def add(center,size,color,alpha=1,angle=0):
        ax.add_collection3d(Poly3DCollection(box_faces(center,size,angle),facecolors=color,
                                           edgecolors='#646864',linewidths=.25,alpha=alpha))
    add(((X0+X1)/2,(Y0+Y1)/2-.25,-.05),(2.9,Y1-Y0+.5,.1),'#c6d8df')
    add(((X0+X1)/2,Y0-.35,3.15),(2.9,.7,.1),'#a4beca',.6)
    for name,center,size,material,angle in stair_parts(side):
        color = '#303e45' if material == 'RailMetal' else '#c5c4b9'
        if name == 'HalfLanding':
            color = '#d6b875'
        add(center,size,color,angle=angle)
    ax.text(entry_x-.5,Y0-.3,.12,'1F entry',fontsize=11,color='#215d74')
    ax.text(exit_x-.3,Y0-.6,3.4,'2F exit  +3.20 m',fontsize=11,color='#215d74')
    ax.text(X0,Y1+.12,1.75,'180° turn at +1.60 m',fontsize=11,color='#8a6329')
    ax.text(X1+.05,Y0+.9,1.0,'Open\nunderside',fontsize=10,color='#215d74')
    ax.set(xlim=(X0-.3,X1+.6),ylim=(Y0-.75,Y1+.5),zlim=(-.1,4.6),zlabel='Height [m]')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_box_aspect((3.4,4.4,4.7))
    ax.view_init(elev=22,azim=-116)
    ax.set_title('Stair geometry cutaway\nWalls and ceiling hidden',fontsize=13)
    plan = fig.add_subplot(122)
    plan.add_patch(Rectangle((X0,Y0),2.5,3.44,facecolor='#edf0ed',edgecolor='#59645f',linewidth=3))
    plan.add_patch(Rectangle((X0,Y0+RUN),2.5,1.2,facecolor='#e8d49e',edgecolor='#79643d'))
    for x in (X0+.1,X0+1.3):
        for step in range(8):
            plan.add_patch(Rectangle((x,Y0+step*TREAD),1.1,TREAD,facecolor='#c5c4b9',edgecolor='#68716b',linewidth=.6))
    plan.annotate('',xy=(entry_x,Y0+RUN+.3),xytext=(entry_x,Y0+.15),arrowprops={'arrowstyle':'->','lw':2.5,'color':'#24657f'})
    plan.annotate('',xy=(exit_x,Y0+.15),xytext=(exit_x,Y0+RUN+.3),arrowprops={'arrowstyle':'->','lw':2.5,'color':'#24657f'})
    plan.annotate('',xy=(exit_x,Y0+RUN+.5),xytext=(entry_x,Y0+RUN+.5),arrowprops={'arrowstyle':'->','lw':2.5,'color':'#24657f','connectionstyle':f'arc3,rad={-.65 if side == "Left" else .65}'})
    plan.text((X0+X1)/2,Y1-.2,'Landing +1.60 m',ha='center',fontsize=12)
    plan.text(entry_x,Y0-.23,'1F entrance',ha='center',fontsize=11)
    plan.text(exit_x,Y0-.23,'2F arrival',ha='center',fontsize=11)
    plan.text(X0+.65,Y0+RUN/2,'UP',ha='center',color='#24657f',fontsize=12,bbox={'facecolor':'white','alpha':.8,'edgecolor':'none'})
    plan.text(X0+1.85,Y0+RUN/2,'UP',ha='center',color='#24657f',fontsize=12,bbox={'facecolor':'white','alpha':.8,'edgecolor':'none'})
    plan.set(xlim=(X0-.4,X1+.4),ylim=(Y0-.6,Y1+.45),title='Plan — 2.50 × 3.44 m')
    plan.set_aspect('equal')
    plan.axis('off')
    fig.suptitle(f'{side} staircase — turn between floors',fontsize=18)
    fig.text(.5,.06,'18 risers × 0.1778 m  |  tread 0.28 m  |  flight width 1.10 m  |  landing depth 1.20 m',ha='center',fontsize=12)
    fig.text(.5,.025,'Generated geometry schematic, not an Isaac Sim screenshot. 1F ceiling and 2F slab are open above the stairs.',ha='center',fontsize=9,color='#53626a')
    fig.tight_layout(rect=(0,.1,1,.95))
    output = ROOT / f'worlds/cbnu_haksan_2f_building/preview_{side.lower()}_staircase.png'
    fig.savefig(output,dpi=160,facecolor='white')
    plt.close(fig)
    print(f'wrote {output}')


if __name__ == '__main__':
    for side in BAYS:
        main(side)
