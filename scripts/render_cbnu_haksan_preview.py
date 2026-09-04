#!/usr/bin/env python3
"""Render a deterministic top-view diagram for the CBNU Haksan detailed world."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patches, transforms
from matplotlib.lines import Line2D

sys.dont_write_bytecode = True
from generate_unified_sofa_meshes import CORNER_OUTLINES, U_OUTLINES


ROOT = Path(__file__).resolve().parents[1]
WORLD_DIR = ROOT / "worlds/cbnu_haksan_1f_corridor"
GEOMETRY_PATH = WORLD_DIR / "config/geometry.json"
DOORS_PATH = WORLD_DIR / "config/doors.json"
FURNITURE_PATH = WORLD_DIR / "config/furniture.json"
CEILING_PATH = WORLD_DIR / "config/ceiling.json"
ARCHITECTURE_PATH = WORLD_DIR / "config/architecture.json"
DYNAMIC_OBSTACLES_PATH = WORLD_DIR / "config/dynamic_obstacles.json"
OUTPUT_PATH = WORLD_DIR / "preview_top_view_detailed.png"
ARCHITECTURE_OUTPUT_PATH = WORLD_DIR / "preview_architecture_detail.png"
GRANITE_TEXTURE_PATH = ROOT / "assets/materials/lobby/textures/bala_white_granite_floor_pattern.png"
GRANITE_REPEAT_METERS = 2.4


def add_centered_rectangle(
    axis,
    center: tuple[float, float],
    width: float,
    depth: float,
    *,
    facecolor: str,
    edgecolor: str,
    linewidth: float = 1.2,
    angle_deg: float = 0,
    alpha: float = 1,
    zorder: int = 3,
    hatch: str | None = None,
    linestyle: str = "solid",
):
    rectangle = patches.Rectangle(
        (-width / 2, -depth / 2),
        width,
        depth,
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=linewidth,
        alpha=alpha,
        zorder=zorder,
        hatch=hatch,
        linestyle=linestyle,
    )
    rectangle.set_transform(
        transforms.Affine2D().rotate_deg(angle_deg).translate(*center) + axis.transData
    )
    axis.add_patch(rectangle)
    return rectangle


def add_centered_rounded_rectangle(
    axis,
    center: tuple[float, float],
    width: float,
    depth: float,
    *,
    facecolor: str,
    edgecolor: str,
    linewidth: float = 1.2,
    angle_deg: float = 0,
    zorder: int = 3,
    hatch: str | None = None,
    linestyle: str = "solid",
):
    rounded = patches.FancyBboxPatch(
        (-width / 2, -depth / 2),
        width,
        depth,
        boxstyle=patches.BoxStyle.Round(
            pad=0,
            rounding_size=min(width, depth) * 0.22,
        ),
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=linewidth,
        zorder=zorder,
        hatch=hatch,
        linestyle=linestyle,
    )
    rounded.set_transform(
        transforms.Affine2D().rotate_deg(angle_deg).translate(*center) + axis.transData
    )
    axis.add_patch(rounded)
    return rounded


def add_transformed_polygon(
    axis,
    center: tuple[float, float],
    points: list[tuple[float, float]],
    *,
    facecolor: str,
    edgecolor: str,
    angle_deg: float = 0,
    linewidth: float = 1.2,
    zorder: int = 3,
    hatch: str | None = None,
    linestyle: str = "solid",
):
    polygon = patches.Polygon(
        points,
        closed=True,
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=linewidth,
        zorder=zorder,
        hatch=hatch,
        linestyle=linestyle,
    )
    polygon.set_transform(
        transforms.Affine2D().rotate_deg(angle_deg).translate(*center) + axis.transData
    )
    axis.add_patch(polygon)
    return polygon


def transform_local_point(
    center: tuple[float, float], local_point: tuple[float, float], angle_deg: float
) -> tuple[float, float]:
    angle = math.radians(angle_deg)
    cosine = math.cos(angle)
    sine = math.sin(angle)
    local_x, local_y = local_point
    return (
        center[0] + local_x * cosine - local_y * sine,
        center[1] + local_x * sine + local_y * cosine,
    )


def main() -> None:
    geometry = json.loads(GEOMETRY_PATH.read_text(encoding="utf-8"))
    doors = json.loads(DOORS_PATH.read_text(encoding="utf-8"))["doors"]
    furniture = json.loads(FURNITURE_PATH.read_text(encoding="utf-8"))
    ceiling = json.loads(CEILING_PATH.read_text(encoding="utf-8"))
    architecture = json.loads(ARCHITECTURE_PATH.read_text(encoding="utf-8"))
    dynamic_obstacles = json.loads(
        DYNAMIC_OBSTACLES_PATH.read_text(encoding="utf-8")
    )
    sofas = furniture["sofas"]
    fixtures = furniture.get("fixtures", [])
    ceiling_lights = ceiling["lights"]
    display_walls = architecture["digital_display_walls"]
    column_displays = architecture.get("column_displays", [])
    wall_posters = architecture.get("wall_posters", [])
    elevator_doors = architecture.get("elevator_doors", [])
    parcel_boxes = dynamic_obstacles["boxes"]
    polygon = np.asarray(geometry["corridor_polygon_xy"], dtype=float)

    fig, axis = plt.subplots(figsize=(15, 9.5))
    floor = patches.Polygon(
        polygon,
        closed=True,
        facecolor="#f1eee6",
        edgecolor="#252525",
        linewidth=2.3,
        zorder=1,
        label="Corridor / marble lobby floor",
    )
    axis.add_patch(floor)

    granite_texture = plt.imread(GRANITE_TEXTURE_PATH)
    min_x, min_y = polygon.min(axis=0)
    max_x, max_y = polygon.max(axis=0)
    start_x = math.floor(min_x / GRANITE_REPEAT_METERS) * GRANITE_REPEAT_METERS
    start_y = math.floor(min_y / GRANITE_REPEAT_METERS) * GRANITE_REPEAT_METERS
    for tile_x in np.arange(start_x, max_x, GRANITE_REPEAT_METERS):
        for tile_y in np.arange(start_y, max_y, GRANITE_REPEAT_METERS):
            granite_tile = axis.imshow(
                granite_texture,
                extent=(
                    tile_x,
                    tile_x + GRANITE_REPEAT_METERS,
                    tile_y,
                    tile_y + GRANITE_REPEAT_METERS,
                ),
                origin="upper",
                interpolation="bilinear",
                zorder=2,
            )
            granite_tile.set_clip_path(floor)
    floor_outline = patches.Polygon(
        polygon,
        closed=True,
        facecolor="none",
        edgecolor="#252525",
        linewidth=2.3,
        zorder=3,
    )
    axis.add_patch(floor_outline)

    # The ceiling surface has the same footprint as the floor, so the cutaway
    # plan only overlays its light fixtures instead of hiding the room below.
    for light in ceiling_lights:
        x, y, _ = light["position"]
        yaw_deg = float(light["yaw_deg"])
        is_large = light.get("type", "panel") == "large_panel"
        width, depth = light.get("size", [1.2, 0.3])
        add_centered_rounded_rectangle(
            axis,
            (float(x), float(y)),
            float(width),
            float(depth),
            facecolor="#fff2ad" if is_large else "#fff7cf",
            edgecolor="#d39b28" if is_large else "#c8ad64",
            linewidth=2.0 if is_large else 0.8,
            angle_deg=yaw_deg,
            zorder=4,
        )
        if is_large:
            axis.text(
                float(x), float(y), "CENTRAL 6.0 × 2.4 m",
                color="#76510a", fontsize=7.5, fontweight="bold",
                ha="center", va="center", zorder=5,
            )

    for center_x in (18.775, 28.225):
        add_centered_rectangle(
            axis,
            (center_x, 0.17),
            4.85,
            0.10,
            facecolor="#8ed7e5",
            edgecolor="#1f6978",
            linewidth=1.5,
            alpha=0.72,
            zorder=5,
        )
    add_centered_rectangle(
        axis,
        (24.4058, 20.60),
        3.1332,
        0.10,
        facecolor="#8ed7e5",
        edgecolor="#1f6978",
        linewidth=1.5,
        alpha=0.72,
        zorder=5,
    )

    for column in geometry["columns"]:
        center = tuple(column["center"])
        add_centered_rectangle(
            axis,
            center,
            float(column["size"][0]),
            float(column["size"][1]),
            facecolor="#8f918f",
            edgecolor="#6f6d67",
            linewidth=1.5,
            zorder=4,
        )
        axis.text(*center, column["name"], ha="center", va="center", fontsize=8, zorder=6)

    for pillar in geometry.get("entrance_pillars", []):
        center = tuple(pillar["center"])
        add_centered_rectangle(
            axis,
            center,
            float(pillar["size"][0]),
            float(pillar["size"][1]),
            facecolor="#8f918f",
            edgecolor="#6f6d67",
            linewidth=1.1,
            zorder=7,
        )

    columns_by_name = {item["name"]: item for item in geometry["columns"]}
    for sofa in sofas:
        sofa_type = sofa["type"]
        placement = sofa["placement"]
        facing = sofa["facing"]
        placement_code = "WA" if placement == "wall_attached" else "CA"
        placement_hatch = "///" if placement == "wall_attached" else "xx"
        placement_linestyle = "solid" if placement == "wall_attached" else "dashdot"
        direction_color = "#8b2515" if facing == "wall" else "#2d6b4f"
        if sofa_type == "straight":
            x, y, _ = sofa["position"]
            length = 2.0 * float(sofa["length_scale"])
            yaw_deg = float(sofa["yaw_deg"])
            add_centered_rounded_rectangle(
                axis,
                (float(x), float(y)),
                length,
                0.82,
                facecolor="#7b4528",
                edgecolor="#4b2614",
                angle_deg=yaw_deg,
                zorder=5,
                hatch=placement_hatch,
                linestyle=placement_linestyle,
            )
            add_centered_rounded_rectangle(
                axis,
                (float(x), float(y)),
                max(length - 0.08, 0.35),
                0.54,
                facecolor="#a8643a",
                edgecolor="#65351d",
                linewidth=0.8,
                angle_deg=yaw_deg,
                zorder=6,
            )
            back_center = transform_local_point(
                (float(x), float(y)), (0, 0.33), yaw_deg
            )
            add_centered_rectangle(
                axis,
                back_center,
                max(length - 0.12, 0.30),
                0.12,
                facecolor="#4a2514",
                edgecolor="#2a130a",
                linewidth=0.7,
                angle_deg=yaw_deg,
                zorder=7,
            )
            front_tip = transform_local_point(
                (float(x), float(y)), (0, -0.62), yaw_deg
            )
            axis.annotate(
                "",
                xy=front_tip,
                xytext=(float(x), float(y)),
                arrowprops={"arrowstyle": "->", "color": direction_color, "lw": 1.3},
                zorder=9,
            )
            axis.text(
                float(x), float(y), placement_code,
                color="white", fontsize=6.2, fontweight="bold",
                ha="center", va="center", zorder=10,
            )
        elif sofa_type == "single":
            x, y, _ = sofa["position"]
            yaw_deg = float(sofa["yaw_deg"])
            add_centered_rounded_rectangle(
                axis,
                (float(x), float(y)),
                1.02,
                0.82,
                facecolor="#9b5c35",
                edgecolor="#4b2614",
                angle_deg=yaw_deg,
                zorder=5,
                hatch=placement_hatch,
                linestyle=placement_linestyle,
            )
            add_centered_rounded_rectangle(
                axis,
                (float(x), float(y)),
                0.94,
                0.54,
                facecolor="#bd7a4c",
                edgecolor="#65351d",
                linewidth=0.8,
                angle_deg=yaw_deg,
                zorder=6,
            )
            back_center = transform_local_point(
                (float(x), float(y)), (0, 0.32), yaw_deg
            )
            add_centered_rectangle(
                axis,
                back_center,
                0.92,
                0.12,
                facecolor="#4a2514",
                edgecolor="#2a130a",
                linewidth=0.7,
                angle_deg=yaw_deg,
                zorder=7,
            )
            front_tip = transform_local_point(
                (float(x), float(y)), (0, -0.62), yaw_deg
            )
            axis.annotate(
                "",
                xy=front_tip,
                xytext=(float(x), float(y)),
                arrowprops={"arrowstyle": "->", "color": direction_color, "lw": 1.3},
                zorder=9,
            )
            axis.text(
                float(x), float(y), placement_code,
                color="white", fontsize=6.2, fontweight="bold",
                ha="center", va="center", zorder=10,
            )
        elif sofa_type == "corner":
            x, y, _ = sofa["position"]
            add_transformed_polygon(
                axis,
                (float(x), float(y)),
                CORNER_OUTLINES["base"],
                facecolor="#6d3b22",
                edgecolor="#3b1d0f",
                angle_deg=float(sofa["yaw_deg"]),
                linewidth=1.4,
                zorder=5,
                hatch=placement_hatch,
                linestyle=placement_linestyle,
            )
            corner_center = (float(x), float(y))
            corner_yaw = float(sofa["yaw_deg"])
            add_transformed_polygon(
                axis,
                corner_center,
                CORNER_OUTLINES["seat"],
                facecolor="#a8643a",
                edgecolor="#65351d",
                linewidth=0.6,
                angle_deg=corner_yaw,
                zorder=6,
            )
            add_transformed_polygon(
                axis,
                corner_center,
                CORNER_OUTLINES["back"],
                facecolor="#442111",
                edgecolor="#442111",
                linewidth=0.3,
                angle_deg=corner_yaw,
                zorder=7,
            )
            for local_start, local_end in (
                ((1.25, 0.02), (1.25, 0.68)),
                ((-0.02, -1.42), (-0.68, -1.42)),
            ):
                arrow_start = transform_local_point(corner_center, local_start, corner_yaw)
                arrow_end = transform_local_point(corner_center, local_end, corner_yaw)
                axis.annotate(
                    "",
                    xy=arrow_end,
                    xytext=arrow_start,
                    arrowprops={"arrowstyle": "->", "color": direction_color, "lw": 1.3},
                    zorder=9,
                )
            axis.text(
                *transform_local_point(corner_center, (0.70, -0.72), corner_yaw),
                placement_code,
                color="white", fontsize=6.2, fontweight="bold",
                ha="center", va="center", zorder=10,
            )
        elif sofa_type == "u_column":
            sofa_geometry = geometry["sofa"]
            sofa_x, sofa_y = columns_by_name[sofa["column"]]["center"]
            sofa_width = float(sofa_geometry["outer_width"])
            sofa_depth = float(sofa_geometry["outer_depth"])
            sofa_thickness = float(sofa_geometry["thickness"])
            sofa_center_y = sofa_y + float(sofa_geometry["top_y_relative_to_column_center"]) - sofa_depth / 2
            add_transformed_polygon(
                axis,
                (sofa_x, sofa_y),
                U_OUTLINES["base"],
                facecolor="#754126",
                edgecolor="#3d1f10",
                zorder=5,
                hatch=placement_hatch,
                linestyle=placement_linestyle,
            )

            # Render the unified U-shaped upholstery as a lighter seat surface,
            # a continuous dark column-side back and outward-facing arrows.
            left_seat_x = sofa_x - 1.15
            right_seat_x = sofa_x + 1.15
            bottom_seat_y = sofa_y - 1.25
            add_transformed_polygon(
                axis,
                (sofa_x, sofa_y),
                U_OUTLINES["seat"],
                facecolor="#a8643a",
                edgecolor="#65351d",
                linewidth=0.6,
                zorder=6,
            )
            add_transformed_polygon(
                axis,
                (sofa_x, sofa_y),
                U_OUTLINES["back"],
                facecolor="#442111",
                edgecolor="#442111",
                linewidth=0.3,
                zorder=7,
            )
            for arrow_start, arrow_end in (
                ((left_seat_x, sofa_y - 0.20), (sofa_x - 1.95, sofa_y - 0.20)),
                ((right_seat_x, sofa_y - 0.20), (sofa_x + 1.95, sofa_y - 0.20)),
                ((sofa_x, bottom_seat_y), (sofa_x, sofa_y - 2.05)),
            ):
                axis.annotate(
                    "",
                    xy=arrow_end,
                    xytext=arrow_start,
                    arrowprops={"arrowstyle": "->", "color": direction_color, "lw": 1.3},
                    zorder=9,
                )
            axis.text(
                sofa_x,
                sofa_center_y - sofa_depth / 2 + sofa_thickness / 2,
                placement_code,
                color="white", fontsize=6.2, fontweight="bold",
                ha="center", va="center", zorder=10,
            )

    for fixture in fixtures:
        x, y, _ = fixture["position"]
        center = (float(x), float(y))
        yaw_deg = float(fixture["yaw_deg"])
        if fixture["type"] == "atm":
            add_centered_rectangle(
                axis,
                center,
                0.90,
                0.58,
                facecolor="#252b31",
                edgecolor="#11161a",
                linewidth=1.3,
                angle_deg=yaw_deg,
                zorder=7,
            )
            screen_center = transform_local_point(center, (0, -0.22), yaw_deg)
            add_centered_rectangle(
                axis,
                screen_center,
                0.52,
                0.08,
                facecolor="#0a7898",
                edgecolor="#073d51",
                linewidth=0.8,
                angle_deg=yaw_deg,
                zorder=8,
            )
            axis.text(*center, "ATM", color="white", fontsize=6.5,
                      fontweight="bold", ha="center", va="center", zorder=10)
        elif fixture["type"] in {"lobby_table", "lobby_table_filled"}:
            width = 2.0 * float(fixture["length_scale"])
            depth = 1.36 * float(fixture.get("depth_scale", 1.0))
            add_centered_rounded_rectangle(
                axis,
                center,
                width,
                depth,
                facecolor="#4b2412" if fixture["type"] == "lobby_table_filled" else "#63351d",
                edgecolor="#28160d",
                linewidth=1.2,
                angle_deg=yaw_deg,
                zorder=7,
            )
            axis.text(*center, fixture["name"].replace("Table_", "T"),
                      color="white", fontsize=6.2, fontweight="bold",
                      ha="center", va="center", zorder=10)

    parcel_colors = {
        "kraft_light": "#b87837",
        "kraft_medium": "#8f4f20",
        "kraft_dark": "#653313",
    }
    for parcel in sorted(parcel_boxes, key=lambda item: int(item["stack_level"])):
        x, y, _ = parcel["position"]
        width, depth, _ = parcel["size"]
        yaw_deg = float(parcel["yaw_deg"])
        level = int(parcel["stack_level"])
        center = (float(x), float(y))
        add_centered_rectangle(
            axis,
            center,
            float(width),
            float(depth),
            facecolor=parcel_colors[parcel["material_variant"]],
            edgecolor="#42200d",
            linewidth=1.0 + 0.25 * level,
            angle_deg=yaw_deg,
            zorder=10 + level,
        )
        add_centered_rectangle(
            axis,
            center,
            min(0.11, float(width) * 0.22),
            float(depth) + 0.01,
            facecolor="#c8a35e",
            edgecolor="#8f6f32",
            linewidth=0.35,
            angle_deg=yaw_deg,
            zorder=11 + level,
        )
        axis.text(
            *center,
            parcel["name"].replace("ParcelBox_", "P"),
            color="white",
            fontsize=5.4,
            fontweight="bold",
            ha="center",
            va="center",
            zorder=12 + level,
        )

    for display_wall in display_walls:
        origin = tuple(float(value) for value in display_wall["position"][:2])
        yaw_deg = float(display_wall["yaw_deg"])
        asset_variant = str(display_wall.get("asset_variant", "corner"))
        front_length = float(display_wall["front_length"])
        side_length = float(display_wall["side_length"])
        depth = float(display_wall["depth"])
        local_outline = [
            (-depth, -depth),
            (front_length - depth, -depth),
            (front_length - depth, 0),
            (0, 0),
            (0, side_length - depth),
            (-depth, side_length - depth),
        ]
        add_transformed_polygon(
            axis,
            origin,
            local_outline,
            facecolor="#323941",
            edgecolor="#080b0e",
            angle_deg=yaw_deg,
            linewidth=2.0,
            zorder=9,
        )

        front_count = int(display_wall["front_display_count"])
        front_centers = (
            np.linspace(0.31, front_length - depth - 0.41, front_count)
            if front_count > 0
            else []
        )
        for index, local_x in enumerate(front_centers, start=1):
            screen_center = transform_local_point(origin, (float(local_x), -depth - 0.04), yaw_deg)
            add_centered_rectangle(
                axis,
                screen_center,
                0.54,
                0.07,
                facecolor="#174a64",
                edgecolor="#03121c",
                linewidth=0.8,
                angle_deg=yaw_deg,
                zorder=10,
            )
            axis.text(*screen_center, f"F{index}", color="white", fontsize=5.5,
                      ha="center", va="center", zorder=11)

        side_count = int(display_wall["side_display_count"])
        side_end = side_length - depth - 0.57
        side_centers = np.linspace(0.57, side_end, side_count) if side_count > 0 else []
        for offset, local_y in enumerate(side_centers, start=1):
            screen_center = transform_local_point(origin, (-depth - 0.04, float(local_y)), yaw_deg)
            add_centered_rectangle(
                axis,
                screen_center,
                0.54,
                0.07,
                facecolor="#15545b",
                edgecolor="#03121c",
                linewidth=0.8,
                angle_deg=yaw_deg - 90,
                zorder=10,
            )
            axis.text(*screen_center, f"S{offset}", color="white", fontsize=5.5,
                      ha="center", va="center", zorder=11)

        section_arrows = []
        if front_count > 0:
            section_arrows.append(
                (
                    transform_local_point(origin, (front_length * 0.5 - depth, -depth - 0.12), yaw_deg),
                    transform_local_point(origin, (front_length * 0.5 - depth, -depth - 0.82), yaw_deg),
                    f"RIGHT ×{front_count}",
                )
            )
        if side_count > 0:
            side_midpoint = side_length * 0.5 - depth
            section_arrows.append(
                (
                    transform_local_point(origin, (-depth - 0.12, side_midpoint), yaw_deg),
                    transform_local_point(origin, (-depth - 0.82, side_midpoint), yaw_deg),
                    f"LEFT ×{side_count}",
                )
            )
        for start, end, label in section_arrows:
            axis.annotate(
                label,
                xy=end,
                xytext=start,
                color="#7c2caa",
                fontsize=7,
                fontweight="bold",
                ha="center",
                arrowprops={"arrowstyle": "->", "color": "#7c2caa", "lw": 1.8},
                zorder=12,
            )

    for column_display in column_displays:
        origin = tuple(float(value) for value in column_display["position"][:2])
        yaw_deg = float(column_display["yaw_deg"])
        width = float(column_display["width"])
        depth = float(column_display["depth"])
        body_center = transform_local_point(origin, (0, -depth / 2), yaw_deg)
        add_centered_rectangle(
            axis,
            body_center,
            width,
            depth,
            facecolor="#174a64",
            edgecolor="#03121c",
            linewidth=1.4,
            angle_deg=yaw_deg,
            zorder=11,
        )
        axis.text(
            *body_center,
            "BIG",
            color="white",
            fontsize=5.5,
            fontweight="bold",
            ha="center",
            va="center",
            zorder=12,
        )
        facing_end = transform_local_point(origin, (0, -0.65), yaw_deg)
        axis.annotate(
            "ENTRANCE",
            xy=facing_end,
            xytext=origin,
            color="#0a7898",
            fontsize=6,
            fontweight="bold",
            ha="center",
            arrowprops={"arrowstyle": "->", "color": "#0a7898", "lw": 1.5},
            zorder=12,
        )

    for poster in wall_posters:
        origin = tuple(float(value) for value in poster["position"][:2])
        yaw_deg = float(poster["yaw_deg"])
        width = float(poster["width"])
        depth = float(poster["depth"])
        is_large_dark_poster = poster.get("asset_variant") == "gray_horizontal_large"
        body_center = transform_local_point(origin, (0, -depth / 2), yaw_deg)
        add_centered_rectangle(
            axis,
            body_center,
            width,
            depth,
            facecolor="#575c61" if is_large_dark_poster else "#b3b8bd",
            edgecolor="#2f3336" if is_large_dark_poster else "#7a7f84",
            linewidth=1.4,
            angle_deg=yaw_deg,
            zorder=11,
        )
        label_center = transform_local_point(origin, (0, -0.22), yaw_deg)
        axis.text(
            *label_center,
            "DARK GRAY POSTER" if is_large_dark_poster else "GRAY POSTER",
            color="white" if is_large_dark_poster else "#4d5155",
            fontsize=6,
            fontweight="bold",
            ha="center",
            va="center",
            rotation=yaw_deg,
            zorder=12,
        )

    for index, elevator_door in enumerate(elevator_doors, start=1):
        origin = tuple(float(value) for value in elevator_door["position"][:2])
        yaw_deg = float(elevator_door["yaw_deg"])
        width = float(elevator_door["width"])
        depth = float(elevator_door["depth"])
        body_center = transform_local_point(origin, (0, -depth / 2), yaw_deg)
        add_centered_rectangle(
            axis,
            body_center,
            width + 0.22,
            depth + 0.04,
            facecolor="#454a4e",
            edgecolor="#171a1c",
            linewidth=1.5,
            angle_deg=yaw_deg,
            zorder=10,
        )
        add_centered_rectangle(
            axis,
            body_center,
            width,
            depth,
            facecolor="#9ca4aa",
            edgecolor="#30363a",
            linewidth=1.0,
            angle_deg=yaw_deg,
            zorder=11,
        )
        label_center = transform_local_point(origin, (0, -0.28), yaw_deg)
        axis.text(
            *label_center,
            f"ELEV {index}",
            color="#24282b",
            fontsize=5.8,
            fontweight="bold",
            ha="center",
            va="center",
            rotation=yaw_deg,
            zorder=12,
        )

    single_index = 0
    double_index = 0
    glass_index = 0
    for door in doors:
        x, y, _ = door["position"]
        yaw_deg = float(door["yaw_deg"])
        door_type = door["type"]
        if door_type == "single":
            single_index += 1
            frame_width = 1.06
            label = f"S{single_index}"
            frame_color = "#4f2a17"
        elif door_type == "double":
            double_index += 1
            frame_width = 1.86
            label = f"D{double_index}"
            frame_color = "#351a0d"
        elif door_type == "double_glass":
            double_index += 1
            glass_index += 1
            frame_width = 1.86
            label = f"G{glass_index}"
            frame_color = "#163b48"
        else:
            first_glass_index = glass_index + 1
            double_index += 2
            glass_index += 2
            frame_width = 1.86
            label = f"G{first_glass_index}+G{glass_index}"
            frame_color = "#163b48"
        if door_type == "double_glass_pair":
            frame_centers = [
                transform_local_point((float(x), float(y)), (offset, 0), yaw_deg)
                for offset in (-1.15, 1.15)
            ]
        else:
            frame_centers = [(float(x), float(y))]
        for frame_center in frame_centers:
            add_centered_rectangle(
                axis,
                frame_center,
                frame_width,
                0.18,
                facecolor=frame_color,
                edgecolor="#2c160c",
                linewidth=1.1,
                angle_deg=yaw_deg,
                zorder=7,
            )
        if door_type == "single":
            leaf_centers = [(float(x), float(y))]
        elif door_type in {"double", "double_glass"}:
            angle = math.radians(yaw_deg)
            offset_x = 0.435 * math.cos(angle)
            offset_y = 0.435 * math.sin(angle)
            leaf_centers = [
                (float(x) - offset_x, float(y) - offset_y),
                (float(x) + offset_x, float(y) + offset_y),
            ]
        else:
            leaf_centers = [
                transform_local_point((float(x), float(y)), (offset, 0), yaw_deg)
                for offset in (-1.585, -0.715, 0.715, 1.585)
            ]
        for leaf_center in leaf_centers:
            add_centered_rectangle(
                axis,
                leaf_center,
                0.90 if door_type == "single" else 0.85,
                0.11,
                facecolor="#b8e5ed" if door_type in {"double_glass", "double_glass_pair"} else "#a9632f",
                edgecolor="#397a8d" if door_type in {"double_glass", "double_glass_pair"} else "#5a2b12",
                linewidth=0.9,
                angle_deg=yaw_deg,
                zorder=8,
            )
        if door_type == "double_glass_pair":
            add_centered_rectangle(
                axis,
                (float(x), float(y)),
                0.42,
                0.11,
                facecolor="#c8edf2",
                edgecolor="#397a8d",
                linewidth=0.8,
                angle_deg=yaw_deg,
                zorder=8,
            )
        axis.text(float(x), float(y) + 0.34, label, fontsize=7, ha="center", zorder=9)

    legend_handles = [
        patches.Patch(facecolor="#dddcd8", edgecolor="#7a7975", label="Bala White polished granite floor"),
        patches.Patch(facecolor="#fff7cf", edgecolor="#c8ad64", label="Recessed ceiling LED panel"),
        patches.Patch(facecolor="#fff2ad", edgecolor="#d39b28", linewidth=2, label="Large central ceiling light"),
        patches.Patch(facecolor="#8ed7e5", edgecolor="#1f6978", label="Full-height entrance glass wall"),
        patches.Patch(facecolor="#8f918f", edgecolor="#4f514f", label="Medium gray 1.2 m column"),
        patches.Patch(facecolor="#8f918f", edgecolor="#4f514f", label="Medium gray entrance pillar"),
        patches.Patch(facecolor="#7b4528", edgecolor="#4b2614", label="Straight armless sofa"),
        patches.Patch(facecolor="#9b5c35", edgecolor="#4b2614", label="Single armless sofa"),
        patches.Patch(facecolor="#6d3b22", edgecolor="#3b1d0f", label="Continuous L sofa"),
        patches.Patch(facecolor="#754126", edgecolor="#3d1f10", label="Cushioned open-top U sofa"),
        patches.Patch(facecolor="#63351d", edgecolor="#28160d", label="Sofa-width lobby table"),
        patches.Patch(facecolor="#8f4f20", edgecolor="#42200d", label="Dynamic mixed-size parcel pile"),
        patches.Patch(facecolor="#252b31", edgecolor="#0a7898", label="Bank ATM"),
        patches.Patch(facecolor="#323941", edgecolor="#080b0e", label="Compact floating display wall (L5+R3)"),
        patches.Patch(facecolor="#174a64", edgecolor="#03121c", label="Large Column 3 display facing entrance"),
        patches.Patch(facecolor="#b3b8bd", edgecolor="#7a7f84", label="Long horizontal light-gray wall poster"),
        patches.Patch(facecolor="#575c61", edgecolor="#2f3336", label="One-piece dark-gray wall poster"),
        patches.Patch(facecolor="#9ca4aa", edgecolor="#30363a", label="Operational stainless-steel elevator door"),
        patches.Patch(facecolor="#7b4528", edgecolor="#4b2614", hatch="///", label="WA: wall attached"),
        patches.Patch(facecolor="#754126", edgecolor="#3d1f10", hatch="xx", label="CA: Column 2 attached"),
        Line2D([0], [0], color="#8b2515", marker=">", label="Seat faces wall"),
        Line2D([0], [0], color="#2d6b4f", marker=">", label="Seat faces lobby / outward"),
        patches.Patch(facecolor="#a9632f", edgecolor="#4f2a17", label="Single wood door"),
        patches.Patch(facecolor="#a9632f", edgecolor="#351a0d", linewidth=2, label="Double wood door"),
        patches.Patch(facecolor="#77b8c8", edgecolor="#163b48", linewidth=2, label="Double glass door"),
    ]
    axis.legend(handles=legend_handles, loc="lower left", framealpha=0.95)
    axis.set_title("CBNU Haksan 1F Corridor — Indoor Lobby with Dynamic Parcel Obstacles")
    axis.set_xlabel("X [m]")
    axis.set_ylabel("Y [m]")
    axis.set_xlim(-1, 36.5)
    axis.set_ylim(-1, 21.8)
    axis.set_aspect("equal", adjustable="box")
    axis.grid(True, alpha=0.22, linewidth=0.7)
    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=150, facecolor="white")
    fig.savefig(ARCHITECTURE_OUTPUT_PATH, dpi=150, facecolor="white")
    plt.close(fig)
    print(
        f"wrote {OUTPUT_PATH} "
        f"({single_index} single doors, {double_index} double doors including {glass_index} glass, "
        f"{len(sofas)} sofas, {len(fixtures)} fixtures, {len(ceiling_lights)} ceiling lights, "
        f"{len(display_walls)} digital display walls, {len(column_displays)} column display, "
        f"{len(wall_posters)} wall poster, {len(elevator_doors)} elevator doors, "
        f"{len(parcel_boxes)} dynamic parcel boxes)\n"
        f"wrote {ARCHITECTURE_OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
