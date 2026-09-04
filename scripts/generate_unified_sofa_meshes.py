#!/usr/bin/env python3
"""Generate the single visible render mesh used by the corner and column sofas."""

from __future__ import annotations

import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORNER_ASSET = ROOT / "assets/furniture/sofa_corner.usda"
U_ASSET = ROOT / "assets/furniture/sofa_u_around_2m_column.usda"
BEGIN = "    # BEGIN GENERATED SOFA_UNIFIED\n"
END = "    # END GENERATED SOFA_UNIFIED\n"


CORNER_OUTLINES = {
    "base": [
        (-0.410, -2.710), (0.410, -2.710), (0.410, -0.550),
        (0.427, -0.496), (0.496, -0.427), (0.550, -0.410),
        (2.540, -0.410), (2.540, 0.410), (0.000, 0.410),
        (-0.157, 0.379), (-0.290, 0.290), (-0.379, 0.157),
        (-0.410, 0.000),
    ],
    "seat": [
        (-0.350, -2.710), (0.230, -2.710), (0.230, -0.450),
        (0.247, -0.366), (0.321, -0.294), (0.405, -0.247),
        (0.450, -0.230), (2.540, -0.230), (2.540, 0.350),
        (0.000, 0.350), (-0.134, 0.323), (-0.247, 0.247),
        (-0.323, 0.134), (-0.350, 0.000),
    ],
    "back": [
        (0.250, -2.710), (0.410, -2.710), (0.410, -0.460),
        (0.418, -0.438), (0.438, -0.418), (0.460, -0.410),
        (2.540, -0.410), (2.540, -0.250), (0.460, -0.250),
        (0.416, -0.266), (0.366, -0.316), (0.316, -0.366),
        (0.266, -0.416), (0.250, -0.460),
    ],
}


U_OUTLINES = {
    "base": [
        (-1.250, -1.630), (1.250, -1.630), (1.357, -1.609),
        (1.448, -1.548), (1.509, -1.457), (1.530, -1.350),
        (1.530, 0.750), (0.750, 0.750), (0.750, -0.550),
        (0.735, -0.627), (0.691, -0.691), (0.627, -0.735),
        (0.550, -0.750), (-0.550, -0.750), (-0.627, -0.735),
        (-0.691, -0.691), (-0.735, -0.627), (-0.750, -0.550),
        (-0.750, 0.750), (-1.530, 0.750), (-1.530, -1.350),
        (-1.509, -1.457), (-1.448, -1.548), (-1.357, -1.609),
    ],
    "seat": [
        (-1.250, -1.590), (1.250, -1.590), (1.342, -1.572),
        (1.420, -1.520), (1.472, -1.442), (1.490, -1.350),
        (1.490, 0.700), (0.910, 0.700), (0.910, -0.710),
        (0.895, -0.787), (0.851, -0.851), (0.787, -0.895),
        (0.710, -0.910), (-0.710, -0.910), (-0.787, -0.895),
        (-0.851, -0.851), (-0.895, -0.787), (-0.910, -0.710),
        (-0.910, 0.700), (-1.490, 0.700), (-1.530, -1.350),
        (-1.509, -1.457), (-1.448, -1.548), (-1.357, -1.609),
    ],
    "back": [
        (-0.750, -0.910), (0.750, -0.910), (0.811, -0.898),
        (0.863, -0.853), (0.898, -0.811), (0.910, -0.750),
        (0.910, 0.450), (0.910, 0.750), (0.750, 0.750),
        (0.750, 0.450), (0.750, -0.590),
        (0.738, -0.651), (0.703, -0.703), (0.651, -0.738),
        (0.590, -0.750), (-0.590, -0.750), (-0.651, -0.738),
        (-0.703, -0.703), (-0.738, -0.651), (-0.750, -0.590),
        (-0.750, 0.450), (-0.750, 0.750), (-0.910, 0.750),
        (-0.910, 0.450), (-0.910, -0.750),
        (-0.898, -0.811), (-0.863, -0.853), (-0.811, -0.898),
    ],
}


def contract_toward_origin(value: float, amount: float) -> float:
    if value > 0:
        return value - amount
    if value < 0:
        return value + amount
    return value


# The authored source outline above fits the previous 1.5 m column. Contract
# every non-zero XY boundary by 0.15 m so the active opening fits a 1.2 m
# column while preserving the upholstery thickness and rounded corner samples.
U_OUTLINES = {
    region: [
        (contract_toward_origin(x, 0.15), contract_toward_origin(y, 0.15))
        for x, y in outline
    ]
    for region, outline in U_OUTLINES.items()
}


def signed_area(points: list[tuple[float, float]]) -> float:
    return 0.5 * sum(
        x1 * y2 - x2 * y1
        for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1])
    )


def inset_polygon(points: list[tuple[float, float]], distance: float) -> list[tuple[float, float]]:
    """Return a small mitered inset used only for the upholstery bevel rings."""
    orientation = 1.0 if signed_area(points) > 0 else -1.0
    shifted_lines: list[tuple[tuple[float, float], tuple[float, float]]] = []
    for p1, p2 in zip(points, points[1:] + points[:1]):
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        length = math.hypot(dx, dy)
        if length < 1e-9:
            raise ValueError("zero-length polygon edge")
        nx = orientation * -dy / length
        ny = orientation * dx / length
        shifted_lines.append(
            ((p1[0] + nx * distance, p1[1] + ny * distance), (dx, dy))
        )

    result: list[tuple[float, float]] = []
    for index in range(len(points)):
        (ax, ay), (adx, ady) = shifted_lines[index - 1]
        (bx, by), (bdx, bdy) = shifted_lines[index]
        denominator = adx * bdy - ady * bdx
        if abs(denominator) < 1e-9:
            result.append(((ax + bx) * 0.5, (ay + by) * 0.5))
            continue
        t = ((bx - ax) * bdy - (by - ay) * bdx) / denominator
        px, py = ax + t * adx, ay + t * ady
        # Limit an acute-corner miter so a bevel cannot form a visual spike.
        ox, oy = points[index]
        offset_length = math.hypot(px - ox, py - oy)
        max_miter = distance * 3.0
        if offset_length > max_miter:
            scale = max_miter / offset_length
            px, py = ox + (px - ox) * scale, oy + (py - oy) * scale
        result.append((px, py))
    return result


def triangulate_polygon(points: list[tuple[float, float]]) -> list[tuple[int, int, int]]:
    """Ear-clip a simple XY polygon so Hydra never guesses a concave n-gon cap."""
    vertex_indices = list(range(len(points)))
    if signed_area(points) < 0:
        vertex_indices.reverse()

    def cross(a, b, c) -> float:
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def inside_triangle(point, a, b, c) -> bool:
        epsilon = 1e-10
        return (
            cross(a, b, point) >= -epsilon
            and cross(b, c, point) >= -epsilon
            and cross(c, a, point) >= -epsilon
        )

    triangles: list[tuple[int, int, int]] = []
    guard = 0
    while len(vertex_indices) > 3:
        clipped = False
        for offset, current in enumerate(vertex_indices):
            previous = vertex_indices[offset - 1]
            following = vertex_indices[(offset + 1) % len(vertex_indices)]
            a, b, c = points[previous], points[current], points[following]
            if cross(a, b, c) <= 1e-10:
                continue
            if any(
                inside_triangle(points[candidate], a, b, c)
                for candidate in vertex_indices
                if candidate not in {previous, current, following}
            ):
                continue
            triangles.append((previous, current, following))
            del vertex_indices[offset]
            clipped = True
            break
        guard += 1
        if not clipped or guard > len(points) * len(points):
            raise ValueError("failed to triangulate sofa footprint")
    triangles.append(tuple(vertex_indices))
    return triangles


def add_beveled_shell(
    points_out: list[tuple[float, float, float]],
    counts_out: list[int],
    indices_out: list[int],
    outline: list[tuple[float, float]],
    z_min: float,
    z_max: float,
    bevel_xy: float,
    bevel_z: float,
    taper_mode: str | None = None,
) -> None:
    inset = inset_polygon(outline, bevel_xy)
    top_heights = []
    for x_value, y_value in outline:
        if taper_mode == "u_open_end" and y_value > 0.30:
            ratio = min((y_value - 0.30) / 0.30, 1.0)
            top_heights.append(z_max + ratio * (0.58 - z_max))
        elif taper_mode == "corner_return_end" and x_value <= 0.41 and y_value > -0.30:
            ratio = min((y_value + 0.30) / 0.30, 1.0)
            top_heights.append(z_max + ratio * (0.58 - z_max))
        else:
            top_heights.append(z_max)
    rings = (
        [(x, y, z_min) for x, y in inset],
        [(x, y, z_min + bevel_z) for x, y in outline],
        [(x, y, top_heights[index] - bevel_z) for index, (x, y) in enumerate(outline)],
        [(x, y, top_heights[index]) for index, (x, y) in enumerate(inset)],
    )
    start = len(points_out)
    count = len(outline)
    for ring in rings:
        points_out.extend(ring)

    cap_triangles = triangulate_polygon(inset)
    for first, second, third in cap_triangles:
        counts_out.append(3)
        indices_out.extend((start + third, start + second, start + first))
    for first, second, third in cap_triangles:
        counts_out.append(3)
        indices_out.extend(
            (start + 3 * count + first, start + 3 * count + second, start + 3 * count + third)
        )
    for ring_index in range(3):
        lower = start + ring_index * count
        upper = lower + count
        for index in range(count):
            next_index = (index + 1) % count
            counts_out.append(4)
            indices_out.extend(
                (lower + index, lower + next_index, upper + next_index, upper + index)
            )


def wrap_values(values: list[int], indent: str, width: int = 16) -> str:
    lines = []
    for start in range(0, len(values), width):
        lines.append(indent + ", ".join(str(value) for value in values[start : start + width]))
    return ",\n".join(lines)


def build_mesh(
    outlines: dict[str, list[tuple[float, float]]],
    root_prim: str,
    taper_mode: str | None = None,
) -> str:
    points: list[tuple[float, float, float]] = []
    counts: list[int] = []
    indices: list[int] = []
    # The three upholstery regions touch at their boundaries but never overlap.
    # They are authored as topology inside one render Mesh prim.
    add_beveled_shell(points, counts, indices, outlines["base"], 0.08, 0.37, 0.025, 0.035)
    add_beveled_shell(points, counts, indices, outlines["seat"], 0.37, 0.58, 0.030, 0.045)
    add_beveled_shell(
        points, counts, indices, outlines["back"], 0.37, 0.98, 0.020, 0.055,
        taper_mode=taper_mode,
    )

    point_lines = []
    for start in range(0, len(points), 4):
        row = points[start : start + 4]
        point_lines.append(
            "            " + ", ".join(f"({x:.4f}, {y:.4f}, {z:.4f})" for x, y, z in row)
        )
    return (
        BEGIN
        + '    def Mesh "SofaUnified" (\n'
        + '        prepend apiSchemas = ["MaterialBindingAPI"]\n'
        + '    )\n'
        + "    {\n"
        + '        token visibility = "inherited"\n'
        + "        bool doubleSided = true\n"
        + "        int[] faceVertexCounts = [\n"
        + wrap_values(counts, "            ")
        + "\n        ]\n"
        + "        int[] faceVertexIndices = [\n"
        + wrap_values(indices, "            ")
        + "\n        ]\n"
        + f"        rel material:binding = </{root_prim}/DarkReddishBrownLeather>\n"
        + "        point3f[] points = [\n"
        + ",\n".join(point_lines)
        + "\n        ]\n"
        + "        float3[] primvars:displayColor = [(0.09, 0.055, 0.05)]\n"
        + '        uniform token subdivisionScheme = "none"\n'
        + "    }\n"
        + END
    )


def replace_render_mesh(path: Path, mesh_text: str, first_run_end_prim: str) -> None:
    source = path.read_text(encoding="utf-8")
    if BEGIN in source:
        pattern = re.escape(BEGIN) + r".*?" + re.escape(END)
    else:
        pattern = (
            r'    def Mesh "BaseUpholsteryUnified".*?'
            + rf'(?=    def Capsule "{re.escape(first_run_end_prim)}")'
        )
    updated, replacements = re.subn(pattern, mesh_text, source, count=1, flags=re.DOTALL)
    if replacements != 1:
        raise RuntimeError(f"could not locate render mesh block in {path}")
    path.write_text(updated, encoding="utf-8")


def main() -> None:
    replace_render_mesh(
        CORNER_ASSET,
        build_mesh(CORNER_OUTLINES, "SofaCorner"),
        "LongSeatPlush",
    )
    replace_render_mesh(
        U_ASSET,
        build_mesh(U_OUTLINES, "SofaU", taper_mode="u_open_end"),
        "LeftSeatPlush",
    )
    print(f"generated: {CORNER_ASSET.relative_to(ROOT)}")
    print(f"generated: {U_ASSET.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
