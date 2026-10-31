#!/usr/bin/env python3
"""
Procedural 3D Generator for Balanced Ternary CNFET Threshold Comparison in Blender 4.5+
Builds two parallel Single-Walled Carbon Nanotubes:
  - Channel 1: Zigzag (13,0), d1 = 1.02 nm -> Low Threshold Vth1 = 0.42 V
  - Channel 2: Zigzag (7,0),  d2 = 0.55 nm -> High Threshold Vth2 = 0.78 V
Includes shared Source/Drain (Pd/Au), cutaway Gate-All-Around (HfO2 + Metal Gate),
ballistic electron carriers, and animated 3D conduction band profiles (Ec1, Ec2)
across all three balanced ternary states (-1, 0, +1).
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix


def build_ternary_cnfet_scene(output_blend_path=None):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    for curve in list(bpy.data.curves):
        if curve.users == 0:
            bpy.data.curves.remove(curve)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)

    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 180
    try:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        scene.render.engine = 'BLENDER_EEVEE'

    col_names = [
        "01_Substrate",
        "02_SWCNT_Wide_LowVth",
        "03_SWCNT_Narrow_HighVth",
        "04_Electrodes_Shared",
        "05_Dual_Gate_Stack",
        "06_Ternary_Carriers_Bands",
        "07_Studio_Annotations",
    ]
    cols = {}
    for name in col_names:
        c = bpy.data.collections.new(name)
        scene.collection.children.link(c)
        cols[name] = c

    def link_to_col(obj, col_name):
        for c in list(obj.users_collection):
            c.objects.unlink(obj)
        cols[col_name].objects.link(obj)

    def make_material(name, base_color, metallic=0.0, roughness=0.2, transmission=0.0, ior=1.5, emission_color=None, emission_strength=0.0, alpha=1.0):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF") or nodes.new(type="ShaderNodeBsdfPrincipled")
        bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["IOR"].default_value = ior
        if "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = transmission
        elif "Transmission" in bsdf.inputs:
            bsdf.inputs["Transmission"].default_value = transmission
        if emission_color and emission_strength > 0.0:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = (*emission_color, 1.0)
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = (*emission_color, 1.0)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
        if alpha < 1.0:
            bsdf.inputs["Alpha"].default_value = alpha
            if hasattr(mat, "blend_method"):
                mat.blend_method = 'BLEND'
        return mat

    mats = {
        "Mat_Si_Substrate": make_material("Mat_Si_Substrate", (0.04, 0.05, 0.07), metallic=0.45, roughness=0.20),
        "Mat_SiO2_Oxide": make_material("Mat_SiO2_Oxide", (0.11, 0.16, 0.25), metallic=0.1, roughness=0.14),
        "Mat_Carbon_Atom_Wide": make_material("Mat_Carbon_Atom_Wide", (0.12, 0.16, 0.22), metallic=0.82, roughness=0.20),
        "Mat_Carbon_Bond_Wide": make_material("Mat_Carbon_Bond_Wide", (0.30, 0.45, 0.58), metallic=0.70, roughness=0.24),
        "Mat_Carbon_Atom_Narrow": make_material("Mat_Carbon_Atom_Narrow", (0.18, 0.13, 0.16), metallic=0.82, roughness=0.20),
        "Mat_Carbon_Bond_Narrow": make_material("Mat_Carbon_Bond_Narrow", (0.55, 0.36, 0.44), metallic=0.70, roughness=0.24),
        "Mat_Pd_Au_Electrode": make_material("Mat_Pd_Au_Electrode", (0.94, 0.76, 0.36), metallic=1.0, roughness=0.26),
        "Mat_HfO2_Dielectric": make_material("Mat_HfO2_Dielectric", (0.15, 0.82, 0.96), metallic=0.0, roughness=0.06, transmission=0.88, ior=1.90, alpha=0.38),
        "Mat_Metal_Gate": make_material("Mat_Metal_Gate", (0.90, 0.46, 0.24), metallic=1.0, roughness=0.22),
        "Mat_Carrier_LowVth": make_material("Mat_Carrier_LowVth", (0.0, 0.95, 0.85), roughness=0.05, emission_color=(0.0, 0.95, 0.85), emission_strength=18.0),
        "Mat_Carrier_HighVth": make_material("Mat_Carrier_HighVth", (1.0, 0.55, 0.10), roughness=0.05, emission_color=(1.0, 0.50, 0.08), emission_strength=18.0),
        "Mat_Band_LowVth": make_material("Mat_Band_LowVth", (0.0, 0.95, 0.75), roughness=0.15, emission_color=(0.0, 0.92, 0.72), emission_strength=6.5),
        "Mat_Band_HighVth": make_material("Mat_Band_HighVth", (1.0, 0.32, 0.52), roughness=0.15, emission_color=(1.0, 0.28, 0.48), emission_strength=6.5),
        "Mat_Label_White": make_material("Mat_Label_White", (0.96, 0.98, 1.0), roughness=0.2, emission_color=(0.95, 0.98, 1.0), emission_strength=3.2),
        "Mat_Label_Cyan": make_material("Mat_Label_Cyan", (0.20, 0.98, 0.88), roughness=0.2, emission_color=(0.20, 0.98, 0.88), emission_strength=4.0),
        "Mat_Label_Amber": make_material("Mat_Label_Amber", (1.0, 0.68, 0.22), roughness=0.2, emission_color=(1.0, 0.65, 0.20), emission_strength=4.0),
        "Mat_Label_Green": make_material("Mat_Label_Green", (0.18, 0.95, 0.45), roughness=0.2, emission_color=(0.18, 0.95, 0.45), emission_strength=4.0),
        "Mat_Label_Red": make_material("Mat_Label_Red", (1.0, 0.28, 0.42), roughness=0.2, emission_color=(1.0, 0.28, 0.42), emission_strength=4.0),
        "Mat_Label_Backplate": make_material("Mat_Label_Backplate", (0.015, 0.022, 0.038), metallic=0.1, roughness=0.85),
        "Mat_Leader_Line": make_material("Mat_Leader_Line", (0.60, 0.78, 0.96), roughness=0.2, emission_color=(0.60, 0.78, 0.96), emission_strength=2.2),
    }

    # 1. Substrate
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, -0.75))
    si_base = bpy.context.active_object
    si_base.name = "Si_Substrate_Wafer"
    si_base.scale = (14.4, 9.6, 0.7)
    bpy.ops.object.transform_apply(scale=True)
    bev_si = si_base.modifiers.new(name="Bevel", type='BEVEL')
    bev_si.width = 0.06
    bev_si.segments = 3
    si_base.data.materials.append(mats["Mat_Si_Substrate"])
    link_to_col(si_base, "01_Substrate")

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, -0.20))
    sio2_box = bpy.context.active_object
    sio2_box.name = "SiO2_Buried_Oxide"
    sio2_box.scale = (14.4, 9.6, 0.4)
    bpy.ops.object.transform_apply(scale=True)
    bev_ox = sio2_box.modifiers.new(name="Bevel", type='BEVEL')
    bev_ox.width = 0.04
    bev_ox.segments = 3
    sio2_box.data.materials.append(mats["Mat_SiO2_Oxide"])
    link_to_col(sio2_box, "01_Substrate")

    # 2. SWCNT Channels
    def build_swcnt_channel(prefix, n_hex, radius, y_center, z_center, atom_mat, bond_mat, col_name):
        bond_len = (4.0 * radius / math.sqrt(3.0)) * math.sin(math.pi / (2.0 * n_hex))
        x_start, x_end = -4.5, 4.5
        period_x = 1.5 * bond_len
        num_hp = int((x_end - x_start) / period_x)

        atom_positions = []
        for hp in range(num_hp + 1):
            x_base = x_start + hp * period_x
            off1 = 0.0 if (hp % 2 == 0) else (math.pi / n_hex)
            for k in range(n_hex):
                ang = k * (2.0 * math.pi / n_hex) + off1
                atom_positions.append(Vector((x_base, y_center + radius * math.cos(ang), z_center + radius * math.sin(ang))))
            x_sub = x_base + 0.5 * bond_len
            if x_sub <= x_end + 0.01:
                off2 = (math.pi / n_hex) if (hp % 2 == 0) else 0.0
                for k in range(n_hex):
                    ang = k * (2.0 * math.pi / n_hex) + off2
                    atom_positions.append(Vector((x_sub, y_center + radius * math.cos(ang), z_center + radius * math.sin(ang))))

        bonds = []
        num_atoms = len(atom_positions)
        min_d, max_d = 0.78 * bond_len, 1.22 * bond_len
        for i in range(num_atoms):
            p1 = atom_positions[i]
            for j in range(i + 1, min(num_atoms, i + 3 * n_hex)):
                p2 = atom_positions[j]
                if min_d <= (p1 - p2).length <= max_d:
                    bonds.append((i, j))

        bm_a = bmesh.new()
        atom_r = 0.054 if radius > 0.4 else 0.044
        for pos in atom_positions:
            bmesh.ops.create_icosphere(bm_a, subdivisions=2, radius=atom_r, matrix=Matrix.Translation(pos))
        m_a = bpy.data.meshes.new(f"{prefix}_Atoms_Mesh")
        bm_a.to_mesh(m_a)
        bm_a.free()
        for p in m_a.polygons:
            p.use_smooth = True
        obj_a = bpy.data.objects.new(f"{prefix}_Atoms", m_a)
        scene.collection.objects.link(obj_a)
        obj_a.data.materials.append(atom_mat)
        link_to_col(obj_a, col_name)

        bm_b = bmesh.new()
        z_ax = Vector((0, 0, 1))
        bond_r = 0.021 if radius > 0.4 else 0.017
        for i, j in bonds:
            p1, p2 = atom_positions[i], atom_positions[j]
            vec = p2 - p1
            rot_q = z_ax.rotation_difference(vec.normalized())
            xform = Matrix.Translation(0.5 * (p1 + p2)) @ rot_q.to_matrix().to_4x4()
            bmesh.ops.create_cone(bm_b, cap_ends=False, segments=8, radius1=bond_r, radius2=bond_r, depth=vec.length, matrix=xform)
        m_b = bpy.data.meshes.new(f"{prefix}_Bonds_Mesh")
        bm_b.to_mesh(m_b)
        bm_b.free()
        for p in m_b.polygons:
            p.use_smooth = True
        obj_b = bpy.data.objects.new(f"{prefix}_Bonds", m_b)
        scene.collection.objects.link(obj_b)
        obj_b.data.materials.append(bond_mat)
        link_to_col(obj_b, col_name)

    Y_WIDE = -1.40
    Y_NARROW = 1.40
    Z_CH = 0.95

    build_swcnt_channel("SWCNT_Wide_13_0", 11, 0.56, Y_WIDE, Z_CH, mats["Mat_Carbon_Atom_Wide"], mats["Mat_Carbon_Bond_Wide"], "02_SWCNT_Wide_LowVth")
    build_swcnt_channel("SWCNT_Narrow_7_0", 7, 0.32, Y_NARROW, Z_CH, mats["Mat_Carbon_Atom_Narrow"], mats["Mat_Carbon_Bond_Narrow"], "03_SWCNT_Narrow_HighVth")

    # 3. Electrodes
    for name, x_c in (("Electrode_Source_Shared", -4.85), ("Electrode_Drain_Shared", 4.85)):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_c, 0.0, 0.90))
        el = bpy.context.active_object
        el.name = name
        el.scale = (2.1, 5.4, 1.80)
        bpy.ops.object.transform_apply(scale=True)
        bev = el.modifiers.new(name="Bevel", type='BEVEL')
        bev.width = 0.07
        bev.segments = 3
        el.data.materials.append(mats["Mat_Pd_Au_Electrode"])
        link_to_col(el, "04_Electrodes_Shared")

    # 4. Gate Stack
    def create_cutaway_sleeve(name, y_c, z_c, r_in, r_out, x_half, ang0_deg, ang1_deg, mat, segs=56):
        bm = bmesh.new()
        a0, a1 = math.radians(ang0_deg), math.radians(ang1_deg)
        da = (a1 - a0) / segs
        rings = []
        for xp in (-x_half, x_half):
            iv, ov = [], []
            for s in range(segs + 1):
                a = a0 + s * da
                ca, sa = math.cos(a), math.sin(a)
                iv.append(bm.verts.new((xp, y_c + r_in * ca, z_c + r_in * sa)))
                ov.append(bm.verts.new((xp, y_c + r_out * ca, z_c + r_out * sa)))
            rings.append((iv, ov))
        (in_L, out_L), (in_R, out_R) = rings
        for s in range(segs):
            bm.faces.new((out_L[s], out_R[s], out_R[s+1], out_L[s+1]))
            bm.faces.new((in_L[s+1], in_R[s+1], in_R[s], in_L[s]))
            bm.faces.new((in_L[s], out_L[s], out_L[s+1], in_L[s+1]))
            bm.faces.new((out_R[s], in_R[s], in_R[s+1], out_R[s+1]))
        bm.faces.new((in_L[0], in_R[0], out_R[0], out_L[0]))
        bm.faces.new((out_L[-1], out_R[-1], in_R[-1], in_L[-1]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        m = bpy.data.meshes.new(name + "_Mesh")
        bm.to_mesh(m)
        bm.free()
        obj = bpy.data.objects.new(name, m)
        scene.collection.objects.link(obj)
        obj.data.materials.append(mat)
        bev = obj.modifiers.new(name="Bevel", type='BEVEL')
        bev.width = 0.012
        bev.segments = 2
        bev.limit_method = 'ANGLE'
        link_to_col(obj, "05_Dual_Gate_Stack")

    create_cutaway_sleeve("HfO2_Wide_Channel", Y_WIDE, Z_CH, 0.62, 0.88, 2.15, 195.0, 445.0, mats["Mat_HfO2_Dielectric"])
    create_cutaway_sleeve("Gate_Metal_Wide", Y_WIDE, Z_CH, 0.885, 1.14, 1.45, 195.0, 445.0, mats["Mat_Metal_Gate"])
    create_cutaway_sleeve("HfO2_Narrow_Channel", Y_NARROW, Z_CH, 0.38, 0.68, 2.15, 195.0, 445.0, mats["Mat_HfO2_Dielectric"])
    create_cutaway_sleeve("Gate_Metal_Narrow", Y_NARROW, Z_CH, 0.685, 0.94, 1.45, 195.0, 445.0, mats["Mat_Metal_Gate"])

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.25, 0.22))
    gate_bus = bpy.context.active_object
    gate_bus.name = "Shared_Gate_Bus_Vgs"
    gate_bus.scale = (2.4, 4.2, 0.44)
    bpy.ops.object.transform_apply(scale=True)
    bev_gb = gate_bus.modifiers.new(name="Bevel", type='BEVEL')
    bev_gb.width = 0.04
    bev_gb.segments = 2
    gate_bus.data.materials.append(mats["Mat_Metal_Gate"])
    link_to_col(gate_bus, "05_Dual_Gate_Stack")

    # 5. Carriers & Conduction Band Curves
    num_el = 8
    for idx in range(num_el):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, radius=0.11, location=(0, Y_WIDE, Z_CH))
        e1 = bpy.context.active_object
        e1.name = f"Electron_LowVth_Wide_{idx+1:02d}"
        for p in e1.data.polygons:
            p.use_smooth = True
        e1.data.materials.append(mats["Mat_Carrier_LowVth"])
        link_to_col(e1, "06_Ternary_Carriers_Bands")

        ang = idx * (2.0 * math.pi / 4.0)
        y1 = Y_WIDE + 0.14 * math.cos(ang)
        z1 = Z_CH + 0.14 * math.sin(ang)
        x_blocked = -4.05 + (idx / (num_el - 1)) * 1.55
        x_stream_mid = -3.35 + (idx / (num_el - 1)) * 6.70
        x_stream_end = -2.20 + (idx / (num_el - 1)) * 6.20

        for fr, xp in ((1, x_blocked), (45, x_blocked + 0.08), (85, x_stream_mid), (115, x_stream_end), (155, x_stream_mid), (180, x_stream_end)):
            scene.frame_set(fr)
            e1.location = (xp, y1, z1)
            e1.keyframe_insert(data_path="location", frame=fr)

        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, radius=0.085, location=(0, Y_NARROW, Z_CH))
        e2 = bpy.context.active_object
        e2.name = f"Electron_HighVth_Narrow_{idx+1:02d}"
        for p in e2.data.polygons:
            p.use_smooth = True
        e2.data.materials.append(mats["Mat_Carrier_HighVth"])
        link_to_col(e2, "06_Ternary_Carriers_Bands")

        y2 = Y_NARROW + 0.06 * math.cos(ang)
        z2 = Z_CH + 0.06 * math.sin(ang)
        for fr, xp in ((1, x_blocked), (45, x_blocked + 0.05), (85, x_blocked + 0.10), (115, x_blocked + 0.12), (155, x_stream_mid), (180, x_stream_end)):
            scene.frame_set(fr)
            e2.location = (xp, y2, z2)
            e2.keyframe_insert(data_path="location", frame=fr)

    def smooth_step(t):
        t = max(0.0, min(1.0, t))
        return t * t * (3.0 - 2.0 * t)

    def calc_ec_z(x, barrier_h):
        up = smooth_step((x + 2.2) / 1.05)
        dn = 1.0 - smooth_step((x - 1.15) / 1.05)
        gate_env = up * dn
        drain_drop = smooth_step((x - 1.2) / 1.5) * 0.26
        return 0.40 - drain_drop + barrier_h * gate_env

    def create_ec_band_curve(name, y_pos, h_off, h_mid, h_on, mat):
        num_pts = 80
        x_vals = [-4.0 + (8.0 * i / (num_pts - 1)) for i in range(num_pts)]
        bm = bmesh.new()
        r_tube = 0.052
        n_c = 12
        rings = []
        for x in x_vals:
            z0 = calc_ec_z(x, h_off)
            ring = []
            for c in range(n_c):
                a = c * (2.0 * math.pi / n_c)
                ring.append(bm.verts.new((x, y_pos + r_tube * math.cos(a), z0 + r_tube * math.sin(a))))
            rings.append(ring)
        for i in range(num_pts - 1):
            r1, r2 = rings[i], rings[i + 1]
            for c in range(n_c):
                cn = (c + 1) % n_c
                bm.faces.new((r1[c], r2[c], r2[cn], r1[cn]))
        m = bpy.data.meshes.new(name + "_Mesh")
        bm.to_mesh(m)
        bm.free()
        for p in m.polygons:
            p.use_smooth = True
        obj = bpy.data.objects.new(name, m)
        scene.collection.objects.link(obj)
        obj.data.materials.append(mat)
        link_to_col(obj, "06_Ternary_Carriers_Bands")

        obj.shape_key_add(name="Basis_State_Minus1")
        sk_state0 = obj.shape_key_add(name="State_0_Mid_Vgs")
        sk_state1 = obj.shape_key_add(name="State_Plus1_High_Vgs")

        for i, x in enumerate(x_vals):
            zm = calc_ec_z(x, h_mid)
            zp = calc_ec_z(x, h_on)
            for c in range(n_c):
                idx = i * n_c + c
                a = c * (2.0 * math.pi / n_c)
                sk_state0.data[idx].co = Vector((x, y_pos + r_tube * math.cos(a), zm + r_tube * math.sin(a)))
                sk_state1.data[idx].co = Vector((x, y_pos + r_tube * math.cos(a), zp + r_tube * math.sin(a)))

        for fr, v0, v1 in ((1, 0.0, 0.0), (45, 0.0, 0.0), (70, 1.0, 0.0), (115, 1.0, 0.0), (140, 0.0, 1.0), (180, 0.0, 1.0)):
            sk_state0.value = v0
            sk_state0.keyframe_insert(data_path="value", frame=fr)
            sk_state1.value = v1
            sk_state1.keyframe_insert(data_path="value", frame=fr)

    create_ec_band_curve("Ec1_LowVth_Wide", -3.45, 0.78, 0.12, 0.05, mats["Mat_Band_LowVth"])
    create_ec_band_curve("Ec2_HighVth_Narrow", -2.85, 1.35, 0.92, 0.14, mats["Mat_Band_HighVth"])

    # 6. Camera, Lights, and Annotations
    cam_data = bpy.data.cameras.new(name="CNFET_Ternary_Camera")
    cam_data.lens = 35.0
    cam_obj = bpy.data.objects.new("CNFET_Ternary_Camera", cam_data)
    scene.collection.objects.link(cam_obj)
    cam_obj.location = Vector((5.8, -13.6, 7.6))
    target_pt = Vector((0.0, -0.45, 0.95))
    cam_obj.rotation_euler = (target_pt - cam_obj.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cam_obj
    link_to_col(cam_obj, "07_Studio_Annotations")

    def add_light(name, loc, energy, color, size):
        ld = bpy.data.lights.new(name=name, type='AREA')
        ld.energy = energy
        ld.color = color
        ld.size = size
        lo = bpy.data.objects.new(name, ld)
        scene.collection.objects.link(lo)
        lo.location = Vector(loc)
        lo.rotation_euler = (Vector((0, 0, 0.9)) - lo.location).to_track_quat('-Z', 'Y').to_euler()
        link_to_col(lo, "07_Studio_Annotations")

    add_light("Key_Light_Warm", (7.0, -8.5, 8.5), 900.0, (1.0, 0.96, 0.90), 6.0)
    add_light("Rim_Light_Cool", (-7.0, 7.5, 6.5), 650.0, (0.65, 0.88, 1.0), 5.5)
    add_light("Fill_Light_Soft", (-7.0, -8.5, 5.0), 500.0, (0.90, 0.95, 1.0), 6.5)

    if not scene.world:
        scene.world = bpy.data.worlds.new("CNFET_Ternary_World")
    scene.world.use_nodes = True
    bg_node = scene.world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs[0].default_value = (0.032, 0.045, 0.070, 1.0)
        bg_node.inputs[1].default_value = 1.35

    cam_rot = cam_obj.rotation_euler

    def add_annotation(label_id, text_str, text_pos, anchor_pos=None, size=0.23, mat_name="Mat_Label_White"):
        fc = bpy.data.curves.new(type="FONT", name=f"Font_{label_id}")
        fc.body = text_str
        fc.size = size
        fc.extrude = 0.012
        fc.align_x = 'CENTER'
        fc.align_y = 'BOTTOM'
        tobj = bpy.data.objects.new(f"Label_{label_id}", fc)
        cols["07_Studio_Annotations"].objects.link(tobj)
        tobj.location = Vector(text_pos)
        tobj.rotation_euler = cam_rot
        tobj.data.materials.append(mats[mat_name])

        if anchor_pos is not None:
            p1 = Vector(text_pos) - Vector((0, 0, 0.05))
            p2 = Vector(anchor_pos)
            vec = p2 - p1
            if vec.length > 0.05:
                bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.012, depth=vec.length, location=0.5 * (p1 + p2))
                lobj = bpy.context.active_object
                lobj.name = f"Leader_{label_id}"
                lobj.rotation_mode = 'QUATERNION'
                lobj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(vec.normalized())
                lobj.rotation_mode = 'XYZ'
                lobj.data.materials.append(mats["Mat_Leader_Line"])
                link_to_col(lobj, "07_Studio_Annotations")

                bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.035, location=p2)
                tip = bpy.context.active_object
                tip.name = f"Tip_{label_id}"
                tip.data.materials.append(mats["Mat_Leader_Line"])
                link_to_col(tip, "07_Studio_Annotations")

    add_annotation("Header", "TERNARY CNFET THRESHOLD: Vth = 0.43V / d_CNT", (0.0, 1.5, 4.25), None, size=0.28, mat_name="Mat_Label_White")
    add_annotation("SubHeader", "STATE 0 (Vth1 < Vgs < Vth2): WIDE TUBE CONDUCTS | NARROW TUBE BLOCKED", (0.0, 1.5, 3.80), None, size=0.20, mat_name="Mat_Label_Cyan")
    add_annotation("Source", "SOURCE (Pd/Au)", (-5.15, -0.2, 2.45), (-4.95, -0.2, 1.80), size=0.23)
    add_annotation("Drain", "DRAIN (Pd/Au)", (5.05, -0.2, 2.45), (4.95, -0.2, 1.80), size=0.23)
    add_annotation("WideCh", "CH1: SWCNT (13,0) d1=1.02nm | Low Vth1=0.42V (ON)", (2.75, -1.40, 3.32), (2.45, -1.40, 1.52), size=0.185, mat_name="Mat_Label_Cyan")
    add_annotation("NarrowCh", "CH2: SWCNT (7,0) d2=0.55nm | High Vth2=0.78V (OFF)", (-1.75, 1.40, 2.85), (-1.25, 1.40, 1.65), size=0.185, mat_name="Mat_Label_Amber")
    add_annotation("Band_Ec1", "Ec1 (Low Vth1): Barrier Lowered -> ON", (-2.35, -4.25, 0.14), None, size=0.175, mat_name="Mat_Label_Cyan")
    add_annotation("Band_Ec2", "Ec2 (High Vth2): High Barrier -> OFF", (0.85, -4.35, 0.08), None, size=0.175, mat_name="Mat_Label_Amber")

    scene.frame_set(85)
    if output_blend_path:
        bpy.ops.wm.save_as_mainfile(filepath=output_blend_path)


if __name__ == "__main__":
    build_ternary_cnfet_scene()
