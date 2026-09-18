#!/usr/bin/env python3
"""Draw the generated stair geometry as a cutaway and plan (not a Sim render)."""

import math
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from build_cbnu_haksan_staircase import BAYS, RUN, TREAD, stair_parts, window_parts

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
    fig = plt.figure(figsize=(14,11))
    ax = fig.add_subplot(121,projection='3d')
    def add(center,size,color,alpha=1,angle=0):
        ax.add_collection3d(Poly3DCollection(box_faces(center,size,angle),facecolors=color,
                                           edgecolors='#646864',linewidths=.25,alpha=alpha))
    add(((X0+X1)/2,(Y0+Y1)/2-.25,-.05),(2.9,Y1-Y0+.5,.1),'#c6d8df')
    add(((X0+X1)/2,Y0-.35,3.15),(2.9,.7,.1),'#a4beca',.6)
    add(((X0+X1)/2,Y0-.65,6.16),(1.3,.36,.05),'#ffe074')
    for name,center,size,material,angle in stair_parts(side) + window_parts(side):
        if name.startswith('WindowWall_'):
            continue
        color = '#303e45' if material == 'RailMetal' else '#c5c4b9'
        if 'HalfLanding' in name or name == 'ThirdLevelArrival':
            color = '#d6b875'
        if name == 'WindowGlass':
            color = '#7ac5dc'
        add(center,size,color,alpha=.35 if name == 'WindowGlass' else 1,angle=angle)
    ax.text(entry_x-.5,Y0-.3,.12,'1F entry',fontsize=11,color='#215d74')
    ax.text(X1+.1,Y0-.6,3.4,'2F +3.20 m\nContinue upstairs',fontsize=10,color='#215d74')
    ax.text(X1+.1,Y0-.6,6.5,'3F-height arrival\n+6.40 m',fontsize=10,color='#215d74')
    for z in (1.6,4.8):
        ax.text(X0,Y1+.12,z+.15,f'Turn +{z:.2f} m',fontsize=10,color='#8a6329')
    ax.text(X1+.05,Y0+.9,1.0,'Open\nunderside',fontsize=10,color='#215d74')
    ax.set(xlim=(X0-.3,X1+.8),ylim=(Y0-1.3,Y1+.5),zlim=(-.1,7.7),zlabel='Height [m]')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_box_aspect((3.6,5.2,7.8))
    ax.view_init(elev=22,azim=-116)
    ax.set_title('Stair cutaway with tall window\nOpaque walls and ceiling hidden',fontsize=13)
    plan = fig.add_subplot(122)
    plan.add_patch(Rectangle((X0,Y0),2.5,3.44,facecolor='#edf0ed',edgecolor='#59645f',linewidth=3))
    plan.add_patch(Rectangle((X0,Y0+RUN),2.5,1.2,facecolor='#e8d49e',edgecolor='#79643d'))
    for x in (X0+.1,X0+1.3):
        for step in range(8):
            plan.add_patch(Rectangle((x,Y0+step*TREAD),1.1,TREAD,facecolor='#c5c4b9',edgecolor='#68716b',linewidth=.6))
    plan.annotate('',xy=(entry_x,Y0+RUN+.3),xytext=(entry_x,Y0+.15),arrowprops={'arrowstyle':'->','lw':2.5,'color':'#24657f'})
    plan.annotate('',xy=(exit_x,Y0+.15),xytext=(exit_x,Y0+RUN+.3),arrowprops={'arrowstyle':'->','lw':2.5,'color':'#24657f'})
    plan.annotate('',xy=(exit_x,Y0+RUN+.5),xytext=(entry_x,Y0+RUN+.5),arrowprops={'arrowstyle':'->','lw':2.5,'color':'#24657f','connectionstyle':f'arc3,rad={-.65 if side == "Left" else .65}'})
    plan.plot([(X0+X1)/2-.5,(X0+X1)/2+.5],[Y1+.1,Y1+.1],color='#3197b8',linewidth=5)
    plan.text((X0+X1)/2,Y1+.22,'Window 1.0 × 5.0 m',ha='center',fontsize=11,color='#24788f')
    plan.text((X0+X1)/2,Y1-.2,'Landings +1.60 / +4.80 m',ha='center',fontsize=10)
    plan.text(entry_x,Y0-.23,'1F / 2F ascent',ha='center',fontsize=10)
    plan.text(exit_x,Y0-.23,'2F / 3F arrival',ha='center',fontsize=10)
    plan.text(X0+.65,Y0+RUN/2,'UP',ha='center',color='#24657f',fontsize=12,bbox={'facecolor':'white','alpha':.8,'edgecolor':'none'})
    plan.text(X0+1.85,Y0+RUN/2,'UP',ha='center',color='#24657f',fontsize=12,bbox={'facecolor':'white','alpha':.8,'edgecolor':'none'})
    plan.set(xlim=(X0-.4,X1+.4),ylim=(Y0-.6,Y1+.45),title='Plan — 2.50 × 3.44 m')
    plan.set_aspect('equal')
    plan.axis('off')
    fig.suptitle(f'{side} staircase — continuation to 3F height',fontsize=18)
    fig.text(.5,.06,'36 risers × 0.1778 m  |  tread 0.28 m  |  flight width 1.10 m  |  landing depth 1.20 m',ha='center',fontsize=12)
    fig.text(.5,.025,'Geometry schematic, not an Isaac Sim screenshot. Full third-floor rooms are not included.',ha='center',fontsize=9,color='#53626a')
    fig.tight_layout(rect=(0,.1,1,.95))
    output = ROOT / f'worlds/cbnu_haksan_2f_building/preview_{side.lower()}_staircase.png'
    fig.savefig(output,dpi=160,facecolor='white')
    plt.close(fig)
    print(f'wrote {output}')


if __name__ == '__main__':
    for side in BAYS:
        main(side)
