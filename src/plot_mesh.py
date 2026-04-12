"""PyVista mesh visualization — FEM voltage field + mesh anatomy.

Renders:
  1. Cross-section voltage slice at nerve midpoint
  2. FEM mesh anatomy with physical groups
  3. 3D clipped mesh with voltage field

Usage:
    python src/plot_mesh.py batches/batch0
    python src/plot_mesh.py batches/batch0 --out outputs/figures/mesh
"""

import numpy as np
import json
import sys
import os
from pathlib import Path

import pyvista as pv
import meshio

pv.OFF_SCREEN = True
pv.global_theme.background = "#1a1a2e"
pv.global_theme.font.color = "white"
pv.global_theme.font.size = 14


def load_geometry(path="data/bovine_geometry.json"):
    with open(path) as f:
        return json.load(f)


def load_volume(batch_dir):
    d = np.load(f"{batch_dir}/volume_field.npz")
    return d["x"], d["y"], d["z"], d["v"], float(d["semi_major"]), float(d["semi_minor"])


def load_gmsh(batch_dir):
    return meshio.read(f"{batch_dir}/gmsh.msh")


def circle_points(cx, cy, r, z=0, n=60):
    t = np.linspace(0, 2 * np.pi, n)
    return np.column_stack([np.full(n, z), cx + r * np.cos(t), cy + r * np.sin(t)])


def add_fascicle_rings(plotter, geom, x_pos, color="lime", opacity=0.8):
    """Add fascicle boundary circles at a given x position."""
    for fg in geom["vagal_fascicles"]:
        pts = circle_points(fg["y_um"], fg["z_um"], fg["diameter_um"] / 2, z=x_pos)
        line = pv.lines_from_points(pts, close=True)
        plotter.add_mesh(line, color=color, line_width=2, opacity=opacity)


def add_nerve_boundary(plotter, sa, sb, x_pos, color="white", opacity=0.4):
    pts = circle_points(0, 0, 1, z=x_pos, n=120)
    pts[:, 1] *= sa
    pts[:, 2] *= sb
    line = pv.lines_from_points(pts, close=True)
    plotter.add_mesh(line, color=color, line_width=2, opacity=opacity)


# ============================================================
# Render 1: Volume cross-section with voltage heatmap
# ============================================================
def render_voltage_crosssection(batch_dir, geom, out_path):
    """Slice the 3D voltage field at nerve midpoint."""
    xs, ys, zs, v, sa, sb = load_volume(batch_dir)

    # Build ImageData
    dx = xs[1] - xs[0] if len(xs) > 1 else 1
    dy = ys[1] - ys[0] if len(ys) > 1 else 1
    dz = zs[1] - zs[0] if len(zs) > 1 else 1

    grid = pv.ImageData(
        dimensions=(len(xs), len(ys), len(zs)),
        spacing=(dx, dy, dz),
        origin=(xs[0], ys[0], zs[0]),
    )

    # Replace NaN with 0 for rendering
    v_clean = np.nan_to_num(v, nan=0.0)
    grid.point_data["Voltage"] = v_clean.ravel(order="F")

    # Slice at midpoint
    mid_x = (xs[0] + xs[-1]) / 2
    cross = grid.slice(normal="x", origin=(mid_x, 0, 0))

    # Sagittal slice (along nerve axis)
    sagittal = grid.slice(normal="z", origin=(mid_x, 0, 0))

    pl = pv.Plotter(shape=(1, 2), window_size=(1800, 800))

    # Left: cross-section
    pl.subplot(0, 0)
    pl.add_text("Cross-section at cuff center", font_size=12)
    pl.add_mesh(cross, scalars="Voltage", cmap="inferno",
                scalar_bar_args=dict(title="V at 1 mA", position_x=0.05, position_y=0.05,
                                     width=0.3, height=0.05, label_font_size=10))
    add_fascicle_rings(pl, geom, mid_x)
    add_nerve_boundary(pl, sa, sb, mid_x)
    pl.camera_position = [(mid_x + 15000, 0, 0), (mid_x, 0, 0), (0, 0, 1)]

    # Right: sagittal
    pl.subplot(0, 1)
    pl.add_text("Sagittal section (z=0)", font_size=12)
    pl.add_mesh(sagittal, scalars="Voltage", cmap="inferno", show_scalar_bar=False)
    pl.camera_position = [(mid_x, 0, 15000), (mid_x, 0, 0), (0, 1, 0)]

    pl.screenshot(out_path)
    pl.close()
    print(f"Saved: {out_path}")


# ============================================================
# Render 2: Mesh anatomy with physical groups
# ============================================================
def render_mesh_anatomy(batch_dir, geom, out_path):
    """Show FEM mesh with physical groups colored."""
    m = load_gmsh(batch_dir)
    sa = geom["nerve"]["semi_major_um"]
    sb = geom["nerve"]["semi_minor_um"]

    # NRV physical group IDs (from our inspection):
    # Triangles: perineurium surfaces = 11,13,15,17,19,21; outer = 1,3; electrode = 201
    # Tetra: endoneurium = 10,12,14,...; epineurium = 0; outer = 2

    # Collect all triangles with their physical IDs
    tri_cells = []
    tri_phys = []
    tetra_cells = []
    tetra_phys = []

    for i, cell_block in enumerate(m.cells):
        phys = m.cell_data["gmsh:physical"][i] if "gmsh:physical" in m.cell_data else np.zeros(len(cell_block.data))
        if cell_block.type == "triangle":
            tri_cells.append(cell_block.data)
            tri_phys.append(phys)
        elif cell_block.type == "tetra":
            tetra_cells.append(cell_block.data)
            tetra_phys.append(phys)

    pl = pv.Plotter(window_size=(1200, 900))
    pl.add_text("FEM Mesh Anatomy — Physical Groups", font_size=14)

    # Color map for physical groups
    group_colors = {
        "perineurium": "#4CAF50",
        "electrode": "#FF5252",
        "outer": "rgba(255,255,255,0.2)",
    }

    perineurium_ids = {11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33}
    electrode_ids = {201, 203, 205}

    for cells_arr, phys_arr in zip(tri_cells, tri_phys):
        phys_val = int(phys_arr[0]) if len(phys_arr) > 0 else 0

        # Build PyVista surface
        n_tri = len(cells_arr)
        faces = np.column_stack([np.full(n_tri, 3), cells_arr]).ravel()
        surf = pv.PolyData(m.points, faces=faces)

        if phys_val in perineurium_ids:
            pl.add_mesh(surf, color="#4CAF50", opacity=0.7, line_width=1,
                       style="wireframe", label="Perineurium")
        elif phys_val in electrode_ids:
            pl.add_mesh(surf, color="#FF5252", opacity=0.9,
                       label="Electrode")
        elif phys_val == 1:
            pl.add_mesh(surf, color="white", opacity=0.05,
                       style="wireframe", label="Outer boundary")

    # Show tetrahedra as clipped volume
    if tetra_cells:
        all_tetra = np.concatenate(tetra_cells)
        n_tet = len(all_tetra)
        tet_conn = np.column_stack([np.full(n_tet, 4), all_tetra]).ravel()
        cell_types = np.full(n_tet, pv.CellType.TETRA)
        ugrid = pv.UnstructuredGrid(tet_conn, cell_types, m.points)

        # Clip to show cross-section
        mid_x = (m.points[:, 0].min() + m.points[:, 0].max()) / 2
        clipped = ugrid.clip(normal="x", origin=(mid_x, 0, 0))
        pl.add_mesh(clipped, color="gray", opacity=0.15, style="wireframe",
                   line_width=0.5, label="Mesh elements")

    add_nerve_boundary(pl, sa, sb, mid_x if tetra_cells else 5000)
    pl.add_legend(bcolor=(0.1, 0.1, 0.15), face=None)
    pl.camera_position = [(mid_x + 12000, 5000, 5000), (mid_x, 0, 0), (0, 0, 1)]

    pl.screenshot(out_path)
    pl.close()
    print(f"Saved: {out_path}")


# ============================================================
# Render 3: Clipped mesh with voltage field overlay
# ============================================================
def render_mesh_with_voltage(batch_dir, geom, out_path):
    """Clipped tetrahedral mesh colored by interpolated voltage."""
    m = load_gmsh(batch_dir)
    xs, ys, zs, v, sa, sb = load_volume(batch_dir)

    # Build tetra mesh
    tetra_cells = []
    for cell_block in m.cells:
        if cell_block.type == "tetra":
            tetra_cells.append(cell_block.data)

    if not tetra_cells:
        print("No tetrahedra found")
        return

    all_tetra = np.concatenate(tetra_cells)
    n_tet = len(all_tetra)
    tet_conn = np.column_stack([np.full(n_tet, 4), all_tetra]).ravel()
    cell_types = np.full(n_tet, pv.CellType.TETRA)
    ugrid = pv.UnstructuredGrid(tet_conn, cell_types, m.points)

    # Interpolate voltage from volume grid onto mesh vertices
    dx = xs[1] - xs[0] if len(xs) > 1 else 1
    dy = ys[1] - ys[0] if len(ys) > 1 else 1
    dz = zs[1] - zs[0] if len(zs) > 1 else 1
    vol_grid = pv.ImageData(
        dimensions=(len(xs), len(ys), len(zs)),
        spacing=(dx, dy, dz),
        origin=(xs[0], ys[0], zs[0]),
    )
    v_clean = np.nan_to_num(v, nan=0.0)
    vol_grid.point_data["Voltage"] = v_clean.ravel(order="F")

    # Sample volume field at mesh points
    sampled = ugrid.sample(vol_grid)

    # Clip at midpoint
    mid_x = (m.points[:, 0].min() + m.points[:, 0].max()) / 2
    clipped = sampled.clip(normal="x", origin=(mid_x, 0, 0))

    # Extract perineurium surfaces for overlay
    peri_ids = {11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33}
    peri_surfs = []
    for i, cell_block in enumerate(m.cells):
        if cell_block.type == "triangle":
            phys = m.cell_data["gmsh:physical"][i]
            if len(phys) > 0 and int(phys[0]) in peri_ids:
                n_tri = len(cell_block.data)
                faces = np.column_stack([np.full(n_tri, 3), cell_block.data]).ravel()
                peri_surfs.append(pv.PolyData(m.points, faces=faces))

    pl = pv.Plotter(window_size=(1400, 1000))
    pl.add_text("FEM Mesh — Voltage Field on Tetrahedral Elements", font_size=13)

    pl.add_mesh(clipped, scalars="Voltage", cmap="inferno", opacity=0.9,
                scalar_bar_args=dict(title="V at 1 mA", position_x=0.82, position_y=0.3,
                                     width=0.12, height=0.4, label_font_size=10))

    # Perineurium wireframe
    for surf in peri_surfs:
        clipped_peri = surf.clip(normal="x", origin=(mid_x, 0, 0))
        if clipped_peri.n_points > 0:
            pl.add_mesh(clipped_peri, color="#4CAF50", line_width=2,
                       style="wireframe", opacity=0.8)

    add_nerve_boundary(pl, sa, sb, mid_x)
    pl.camera_position = [(mid_x + 15000, 4000, 4000), (mid_x, 0, 0), (0, 0, 1)]

    pl.screenshot(out_path)
    pl.close()
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    batch_dir = sys.argv[1] if len(sys.argv) > 1 else "batches/batch0"
    out_dir = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] != "--out" else None

    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out_dir = sys.argv[i + 1]

    if out_dir is None:
        out_dir = f"outputs/figures/{Path(batch_dir).name}_mesh"
    os.makedirs(out_dir, exist_ok=True)

    geom = load_geometry()

    if Path(f"{batch_dir}/volume_field.npz").exists():
        render_voltage_crosssection(batch_dir, geom, f"{out_dir}/voltage_crosssection.png")
    else:
        print(f"No volume_field.npz in {batch_dir}, skipping voltage renders")

    if Path(f"{batch_dir}/gmsh.msh").exists():
        render_mesh_anatomy(batch_dir, geom, f"{out_dir}/mesh_anatomy.png")
        if Path(f"{batch_dir}/volume_field.npz").exists():
            render_mesh_with_voltage(batch_dir, geom, f"{out_dir}/mesh_voltage.png")
    else:
        print(f"No gmsh.msh in {batch_dir}, skipping mesh renders")

    print(f"All renders saved to {out_dir}/")
