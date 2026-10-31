#!/usr/bin/env python3
"""
Renders the four 1080p@30fps Blender 4.5 EEVEE Next video clips for the
Balanced Ternary CNFET educational video:
  - scene_01_anatomy.mp4      (526 frames, seamless 120-frame harmonic cycle)
  - scene_03_state_minus1.mp4 (471 frames, seamless 120-frame harmonic cycle)
  - scene_04_state_0.mp4      (621 frames, seamless 120-frame harmonic cycle)
  - scene_05_state_plus1.mp4  (456 frames, seamless 120-frame harmonic cycle)
"""

import os
import sys
import math
import subprocess
import bpy
from mathutils import Vector

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from build_ternary_cnfet import build_ternary_cnfet_scene


def set_material_emission(mat, color_rgb, strength):
    if not mat or not mat.use_nodes:
        return
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        return
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*color_rgb, 1.0)
    elif "Emission" in bsdf.inputs:
        bsdf.inputs["Emission"].default_value = (*color_rgb, 1.0)
    if "Emission Strength" in bsdf.inputs:
        bsdf.inputs["Emission Strength"].default_value = strength


def set_label(name, body_text, mat_name):
    obj = bpy.data.objects.get(f"Label_{name}")
    mat = bpy.data.materials.get(mat_name)
    if obj and obj.data:
        obj.data.body = body_text
        if mat:
            obj.data.materials.clear()
            obj.data.materials.append(mat)


def apply_state_configuration(state_mode, loop_frames=120):
    # 1. Clear shape-key animation data and set exact conduction band barriers
    ec1 = bpy.data.objects.get("Ec1_LowVth_Wide")
    ec2 = bpy.data.objects.get("Ec2_HighVth_Narrow")
    for ec_obj in (ec1, ec2):
        if ec_obj and ec_obj.data and ec_obj.data.shape_keys:
            if ec_obj.data.shape_keys.animation_data:
                ec_obj.data.shape_keys.animation_data_clear()

    sk1_0 = ec1.data.shape_keys.key_blocks["State_0_Mid_Vgs"]
    sk1_1 = ec1.data.shape_keys.key_blocks["State_Plus1_High_Vgs"]
    sk2_0 = ec2.data.shape_keys.key_blocks["State_0_Mid_Vgs"]
    sk2_1 = ec2.data.shape_keys.key_blocks["State_Plus1_High_Vgs"]

    gate_mat = bpy.data.materials.get("Mat_Metal_Gate")

    if state_mode == "STATE_MINUS1":
        sk1_0.value, sk1_1.value = 0.0, 0.0
        sk2_0.value, sk2_1.value = 0.0, 0.0
        set_material_emission(gate_mat, (0.90, 0.46, 0.24), 0.0)
        set_label("SubHeader", "STATE -1 (Vgs = 0.15V < Vth1): BOTH NANOTUBES BLOCKED (OFF)", "Mat_Label_Red")
        set_label("WideCh", "CH1: SWCNT (13,0) d1=1.02nm | Low Vth1=0.42V (OFF)", "Mat_Label_Red")
        set_label("NarrowCh", "CH2: SWCNT (7,0) d2=0.55nm | High Vth2=0.78V (OFF)", "Mat_Label_Red")
        set_label("Band_Ec1", "Ec1 (Low Vth1): High Barrier -> OFF", "Mat_Label_Red")
        set_label("Band_Ec2", "Ec2 (High Vth2): High Barrier -> OFF", "Mat_Label_Red")
        ch1_on, ch2_on = False, False

    elif state_mode in ("STATE_0", "ANATOMY"):
        sk1_0.value, sk1_1.value = 1.0, 0.0
        sk2_0.value, sk2_1.value = 1.0, 0.0
        set_material_emission(gate_mat, (0.20, 0.85, 0.95), 1.4)
        if state_mode == "ANATOMY":
            set_label("SubHeader", "DUAL-CHIRALITY GAA-CNFET: SWCNT (13,0) & SWCNT (7,0) CHANNELS", "Mat_Label_Cyan")
        else:
            set_label("SubHeader", "STATE 0 (Vgs = 0.58V): WIDE TUBE CONDUCTS | NARROW TUBE BLOCKED", "Mat_Label_Cyan")
        set_label("WideCh", "CH1: SWCNT (13,0) d1=1.02nm | Low Vth1=0.42V (ON)", "Mat_Label_Cyan")
        set_label("NarrowCh", "CH2: SWCNT (7,0) d2=0.55nm | High Vth2=0.78V (OFF)", "Mat_Label_Amber")
        set_label("Band_Ec1", "Ec1 (Low Vth1): Barrier Lowered -> ON", "Mat_Label_Cyan")
        set_label("Band_Ec2", "Ec2 (High Vth2): High Barrier -> OFF", "Mat_Label_Amber")
        ch1_on, ch2_on = True, False

    elif state_mode == "STATE_PLUS1":
        sk1_0.value, sk1_1.value = 0.0, 1.0
        sk2_0.value, sk2_1.value = 0.0, 1.0
        set_material_emission(gate_mat, (0.25, 0.98, 0.55), 2.8)
        set_label("SubHeader", "STATE +1 (Vgs = 0.90V >= Vth2): BOTH WIDE & NARROW TUBES CONDUCT", "Mat_Label_Green")
        set_label("WideCh", "CH1: SWCNT (13,0) d1=1.02nm | Low Vth1=0.42V (ON)", "Mat_Label_Cyan")
        set_label("NarrowCh", "CH2: SWCNT (7,0) d2=0.55nm | High Vth2=0.78V (ON)", "Mat_Label_Green")
        set_label("Band_Ec1", "Ec1 (Low Vth1): Barrier Lowered -> ON", "Mat_Label_Cyan")
        set_label("Band_Ec2", "Ec2 (High Vth2): Barrier Lowered -> ON", "Mat_Label_Green")
        ch1_on, ch2_on = True, True

    # 2. Animate continuous cyclic electron transport across 1..loop_frames
    Y_WIDE, Y_NARROW, Z_CH = -1.40, 1.40, 0.95
    num_el = 8
    transit_period = 60.0  # Exact divisor of loop_frames=120

    for idx in range(num_el):
        e1 = bpy.data.objects.get(f"Electron_LowVth_Wide_{idx+1:02d}")
        e2 = bpy.data.objects.get(f"Electron_HighVth_Narrow_{idx+1:02d}")
        ang = idx * (2.0 * math.pi / 4.0)
        y1 = Y_WIDE + 0.14 * math.cos(ang)
        z1 = Z_CH + 0.14 * math.sin(ang)
        y2 = Y_NARROW + 0.06 * math.cos(ang)
        z2 = Z_CH + 0.06 * math.sin(ang)
        x_blocked_base = -4.05 + (idx / (num_el - 1)) * 1.45

        if e1:
            e1.animation_data_clear()
            for fr in range(1, loop_frames + 1):
                if ch1_on:
                    phase = ((idx / num_el) + (fr - 1) / transit_period) % 1.0
                    xp = -4.25 + phase * 8.50
                else:
                    xp = x_blocked_base + 0.06 * math.sin(2.0 * math.pi * (fr - 1) / 60.0 + idx)
                e1.location = (xp, y1, z1)
                e1.keyframe_insert(data_path="location", frame=fr)

        if e2:
            e2.animation_data_clear()
            for fr in range(1, loop_frames + 1):
                if ch2_on:
                    phase = ((idx / num_el) + 0.06 + (fr - 1) / transit_period) % 1.0
                    xp = -4.25 + phase * 8.50
                else:
                    xp = x_blocked_base + 0.05 * math.cos(2.0 * math.pi * (fr - 1) / 60.0 + idx)
                e2.location = (xp, y2, z2)
                e2.keyframe_insert(data_path="location", frame=fr)

    # 3. Seamless harmonic camera orbit across 1..loop_frames
    cam_obj = bpy.data.objects.get("CNFET_Ternary_Camera")
    target_pt = Vector((0.0, -0.45, 0.95))
    radius_xy = 14.78
    if cam_obj:
        cam_obj.animation_data_clear()
        for fr in range(1, loop_frames + 1, 4):
            theta = 2.0 * math.pi * (fr - 1) / loop_frames
            az = math.radians(22.5 + 2.4 * math.sin(theta))
            ze = 7.60 + 0.14 * math.cos(theta)
            loc = Vector((radius_xy * math.sin(az), -radius_xy * math.cos(az), ze))
            rot = (target_pt - loc).to_track_quat('-Z', 'Y').to_euler()
            cam_obj.location = loc
            cam_obj.rotation_euler = rot
            cam_obj.keyframe_insert(data_path="location", frame=fr)
            cam_obj.keyframe_insert(data_path="rotation_euler", frame=fr)


def configure_and_render_clip(clip_filename, remotion_filename, target_frames, state_mode):
    loop_frames = 120
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = loop_frames

    try:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        scene.render.engine = 'BLENDER_EEVEE'

    if hasattr(scene, "eevee"):
        if hasattr(scene.eevee, "taa_render_samples"):
            scene.eevee.taa_render_samples = 8
        if hasattr(scene.eevee, "use_raytracing"):
            scene.eevee.use_raytracing = False

    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.fps = 30
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.ffmpeg_preset = 'GOOD'

    apply_state_configuration(state_mode, loop_frames=loop_frames)

    clips_dir = os.path.join(PROJECT_ROOT, "video", "blender_clips")
    remotion_media_dir = os.path.join(PROJECT_ROOT, "remotion-video", "public", "media")
    os.makedirs(clips_dir, exist_ok=True)
    os.makedirs(remotion_media_dir, exist_ok=True)

    out_path = os.path.join(clips_dir, clip_filename)
    scene.render.filepath = out_path
    print(f"[Setun-CNFET] Rendering base loop {clip_filename} ({loop_frames} frames, mode={state_mode})...")
    bpy.ops.render.render(animation=True)

    dst_path = os.path.join(remotion_media_dir, remotion_filename)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-stream_loop",
            "6",
            "-i",
            out_path,
            "-frames:v",
            str(target_frames),
            "-c:v",
            "libx265",
            "-crf",
            "20",
            "-preset",
            "medium",
            "-pix_fmt",
            "yuv420p",
            "-tag:v",
            "hvc1",
            dst_path,
        ],
        check=True,
    )
    print(f"[Setun-CNFET] Expanded seamless clip to {target_frames} frames at {dst_path}")


def main():
    blend_path = os.path.join(PROJECT_ROOT, "blend", "cnfet_ternary_threshold.blend")
    build_ternary_cnfet_scene(blend_path)

    if "--preview" in sys.argv:
        scene = bpy.context.scene
        if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
            scene.eevee.taa_render_samples = 8
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        scene.render.image_settings.file_format = 'PNG'
        renders_dir = os.path.join(PROJECT_ROOT, "renders")
        os.makedirs(renders_dir, exist_ok=True)

        apply_state_configuration("STATE_0", loop_frames=120)
        scene.frame_set(25)
        scene.render.filepath = os.path.join(renders_dir, "preview_state0.png")
        bpy.ops.render.render(write_still=True)

        apply_state_configuration("STATE_PLUS1", loop_frames=120)
        scene.frame_set(25)
        scene.render.filepath = os.path.join(renders_dir, "preview_state_plus1.png")
        bpy.ops.render.render(write_still=True)
        return

    configure_and_render_clip("blender_anatomy.mp4", "scene_01_anatomy.mp4", 526, "ANATOMY")
    configure_and_render_clip("blender_state_minus1.mp4", "scene_03_state_minus1.mp4", 471, "STATE_MINUS1")
    configure_and_render_clip("blender_state_0.mp4", "scene_04_state_0.mp4", 621, "STATE_0")
    configure_and_render_clip("blender_state_plus1.mp4", "scene_05_state_plus1.mp4", 456, "STATE_PLUS1")

    build_ternary_cnfet_scene(blend_path)
    print("[Setun-CNFET] All 4 Blender clips rendered and .blend updated.")


if __name__ == "__main__":
    main()
