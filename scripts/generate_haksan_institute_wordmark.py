#!/usr/bin/env python3
"""Generate solid black Hangul geometry for the five-screen wall wordmark."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = (
    ROOT
    / "assets/architecture/digital_display_wall/institute_wordmark_mesh.usda"
)
FONT = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
FONT_INDEX_KOREAN = 1
TEXT = "학연산공통기술연구원"
CANVAS_SIZE = (1200, 128)
MAX_TEXT_SIZE = (1120, 96)
WIDTH_M = 3.6
HEIGHT_M = 0.38
FRONT_Y_M = -0.020
BACK_Y_M = -0.004


def fitted_font(draw: ImageDraw.ImageDraw) -> ImageFont.FreeTypeFont:
    for size in range(122, 31, -2):
        font = ImageFont.truetype(str(FONT), size=size, index=FONT_INDEX_KOREAN)
        left, top, right, bottom = draw.textbbox((0, 0), TEXT, font=font)
        if right - left <= MAX_TEXT_SIZE[0] and bottom - top <= MAX_TEXT_SIZE[1]:
            return font
    raise RuntimeError("unable to fit the institute wordmark on the mesh canvas")


def horizontal_runs(mask: Image.Image, row: int) -> list[tuple[int, int]]:
    pixels = mask.load()
    width = mask.width
    runs: list[tuple[int, int]] = []
    start: int | None = None
    for column in range(width):
        filled = pixels[column, row] >= 96
        if filled and start is None:
            start = column
        elif not filled and start is not None:
            runs.append((start, column))
            start = None
    if start is not None:
        runs.append((start, width))
    return runs


def merged_run_rectangles(mask: Image.Image) -> list[tuple[int, int, int, int]]:
    rectangles: list[tuple[int, int, int, int]] = []
    active: dict[tuple[int, int], int] = {}
    for row in range(mask.height):
        runs = horizontal_runs(mask, row)
        next_active: dict[tuple[int, int], int] = {}
        for run in runs:
            next_active[run] = active.get(run, row)
        for run, start_row in active.items():
            if run not in next_active:
                rectangles.append((run[0], run[1], start_row, row))
        active = next_active
    for run, start_row in active.items():
        rectangles.append((run[0], run[1], start_row, mask.height))
    return rectangles


def create_mask() -> Image.Image:
    mask = Image.new("L", CANVAS_SIZE, 0)
    draw = ImageDraw.Draw(mask)
    font = fitted_font(draw)
    left, top, right, bottom = draw.textbbox((0, 0), TEXT, font=font)
    x = (CANVAS_SIZE[0] - (right - left)) / 2 - left
    y = (CANVAS_SIZE[1] - (bottom - top)) / 2 - top
    draw.text((x, y), TEXT, font=font, fill=255)
    return mask


def mesh_arrays(
    rectangles: list[tuple[int, int, int, int]],
) -> tuple[list[tuple[float, float, float]], list[int], list[int]]:
    points: list[tuple[float, float, float]] = []
    counts: list[int] = []
    indices: list[int] = []
    width_px, height_px = CANVAS_SIZE

    for x0_px, x1_px, y0_px, y1_px in rectangles:
        x0 = -WIDTH_M / 2 + WIDTH_M * x0_px / width_px
        x1 = -WIDTH_M / 2 + WIDTH_M * x1_px / width_px
        z0 = HEIGHT_M * (height_px - y1_px) / height_px
        z1 = HEIGHT_M * (height_px - y0_px) / height_px
        start = len(points)
        points.extend(
            [
                (x0, FRONT_Y_M, z0),
                (x1, FRONT_Y_M, z0),
                (x1, FRONT_Y_M, z1),
                (x0, FRONT_Y_M, z1),
                (x0, BACK_Y_M, z0),
                (x1, BACK_Y_M, z0),
                (x1, BACK_Y_M, z1),
                (x0, BACK_Y_M, z1),
            ]
        )
        faces = (
            (0, 1, 2, 3),
            (4, 7, 6, 5),
            (0, 4, 5, 1),
            (3, 2, 6, 7),
            (0, 3, 7, 4),
            (1, 5, 6, 2),
        )
        for face in faces:
            counts.append(4)
            indices.extend(start + index for index in face)
    return points, counts, indices


def wrapped(values: list[str], indent: str, per_line: int) -> str:
    return ",\n".join(
        indent + ", ".join(values[index : index + per_line])
        for index in range(0, len(values), per_line)
    )


def main() -> None:
    if not FONT.exists():
        raise FileNotFoundError(f"required Korean font is missing: {FONT}")

    rectangles = merged_run_rectangles(create_mask())
    points, counts, indices = mesh_arrays(rectangles)
    point_values = [f"({x:.6f}, {y:.6f}, {z:.6f})" for x, y, z in points]
    content = f'''#usda 1.0
(
    defaultPrim = "InstituteWordmarkText"
    metersPerUnit = 1
    upAxis = "Z"
)

def Xform "InstituteWordmarkText" (
    kind = "component"
)
{{
    custom string cbnu:content = "{TEXT}"
    custom string cbnu:construction = "solid black extruded Hangul glyph mesh"
    custom double cbnu:width = {WIDTH_M}
    custom double cbnu:height = {HEIGHT_M}
    custom double cbnu:depth = {BACK_Y_M - FRONT_Y_M}
    custom int cbnu:glyphRunBoxCount = {len(rectangles)}
    custom bool cbnu:collisionEnabled = false

    def Material "BlackLettering"
    {{
        token outputs:surface.connect = </InstituteWordmarkText/BlackLettering/PreviewSurface.outputs:surface>

        def Shader "PreviewSurface"
        {{
            uniform token info:id = "UsdPreviewSurface"
            color3f inputs:diffuseColor = (0.003, 0.003, 0.003)
            float inputs:metallic = 0.02
            float inputs:roughness = 0.52
            color3f inputs:specularColor = (0.08, 0.08, 0.08)
            token outputs:surface
        }}
    }}

    def Mesh "GlyphMesh" (
        prepend apiSchemas = ["MaterialBindingAPI"]
    )
    {{
        bool doubleSided = true
        float3[] extent = [(-1.8, -0.020, 0), (1.8, -0.004, 0.38)]
        int[] faceVertexCounts = [
{wrapped([str(value) for value in counts], "            ", 24)}
        ]
        int[] faceVertexIndices = [
{wrapped([str(value) for value in indices], "            ", 24)}
        ]
        rel material:binding = </InstituteWordmarkText/BlackLettering>
        point3f[] points = [
{wrapped(point_values, "            ", 4)}
        ]
        float3[] primvars:displayColor = [(0.003, 0.003, 0.003)]
        uniform token subdivisionScheme = "none"
    }}
}}
'''
    OUTPUT.write_text(content, encoding="utf-8")
    print(
        f"wrote {OUTPUT} ({len(rectangles)} extruded run boxes, "
        f"{len(points)} points, {len(counts)} faces)"
    )


if __name__ == "__main__":
    main()
