# AGENTS.md: Technical Guide for Autonomous Agents & Contributors

This document instructs autonomous coding agents, researchers, and educators on how to operate, reproduce, verify, and extend the **Ternary CNFET 3D Visualization** repository (`Tryquetra/ternary-cnfet-3d`).

---

## 1. Educational Purpose & Core Mission

The objective of this project is to provide an anatomically and physically accurate 3D visualization of **Carbon Nanotube Field-Effect Transistors (CNFETs)** in **Blender 4.5 LTS**, illustrating:
1. **Gate-All-Around (GAA) Nanotube Architecture:** Coaxial high-k dielectric ($\text{HfO}_2$) and metal gate electrode around semiconducting Single-Walled Carbon Nanotubes (SWCNTs) over a $\text{SiO}_2 / \text{Si}$ substrate.
2. **Ballistic Charge Transport:** Scatter-free electron motion from Source to Drain modulated by the gate-Controlled conduction band barrier $E_C(x)$.
3. **Balanced Ternary Threshold Modulation ($V_{th} \propto 1/d_{\text{CNT}}$):** How placing two SWCNTs of different chiral diameters ($d_1 = 1.02\text{ nm}$ and $d_2 = 0.55\text{ nm}$) under a shared gate bus produces three discrete conduction states ($\{-1, 0, +1\}$) without resistive dividers.

---

## 2. Physical & Mathematical Invariants

Any agent modifying or extending the geometry or animations in [`scripts/build_ternary_cnfet.py`](scripts/build_ternary_cnfet.py) must preserve these mathematical invariants:

### A. Zigzag $(n, 0)$ Carbon Nanotube Lattice Exactness
* **Physical Diameter:**
  $$d_{\text{CNT}} = \frac{\sqrt{3} a_{\text{CC}}}{\pi} n \approx 0.0783 \cdot n\text{ (nm)}, \qquad a_{\text{CC}} = 0.142\text{ nm}$$
* **3D Cylinder Bond Scaling:** For a visual cylinder of radius $R$ and circumferential index $n$, the uniform 3D bond length $b$ that guarantees every carbon atom has exactly three nearest neighbors at $120^\circ$ is:
  $$b = \frac{4R}{\sqrt{3}} \sin\left(\frac{\pi}{2n}\right)$$
  The axial period is $3b$, with sub-rings offset by $0.5b$ and $1.5b$ along the $X$ axis and $\Delta\theta = \pi / n$ around the circumference.

### B. Bandgap and Threshold Voltage Scaling
* **Bandgap Energy:**
  $$E_g \approx \frac{0.84\text{ eV}}{d_{\text{CNT}}\text{ (nm)}}$$
* **Threshold Voltage:**
  $$V_{th} \approx \frac{0.43\text{ V}}{d_{\text{CNT}}\text{ (nm)}}$$
* **Channel Parameters in the Reference Scene:**
  * **Channel 1 (Front, Low $V_{th1}$):** Zigzag `(13,0)`, $d_1 = 1.02\text{ nm}$, $V_{th1} \approx 0.42\text{ V}$, visual radius $R_1 = 0.56\text{ m}$ ($n_{\text{mesh}} = 11$, 726 atoms, 1078 covalent $\sigma$ bonds).
  * **Channel 2 (Rear, High $V_{th2}$):** Zigzag `(7,0)`, $d_2 = 0.55\text{ nm}$, $V_{th2} \approx 0.78\text{ V}$, visual radius $R_2 = 0.32\text{ m}$ ($n_{\text{mesh}} = 7$, 518 atoms, 770 covalent $\sigma$ bonds).

### C. Three-State Balanced Ternary Timeline (Frames 1 to 180)
* **Frames 1 to 45 (State `-1`, $V_{GS} < 0.42\text{ V}$):** Both $E_{C1}$ and $E_{C2}$ potential barriers are raised; electrons in both tubes remain confined at the Source.
* **Frames 65 to 115 (State `0`, $0.42\text{ V} \le V_{GS} < 0.78\text{ V}$):** The $E_{C1}$ barrier drops and cyan electrons traverse the wide `(13,0)` tube ballistically; the $E_{C2}$ barrier remains high, blocking amber electrons in the narrow `(7,0)` tube. **Frame 85 is the default saved frame** because it captures selective conduction in a single still image.
* **Frames 135 to 180 (State `+1`, $V_{GS} \ge 0.78\text{ V}$):** Both $E_{C1}$ and $E_{C2}$ barriers drop; both channels conduct simultaneously toward the Drain.

---

## 3. Scene Collection Architecture

All objects in [`blend/cnfet_ternary_threshold.blend`](blend/cnfet_ternary_threshold.blend) must be linked to one of the seven structured collections:

| Collection Name | Purpose & Contained Objects |
| :--- | :--- |
| `01_Substrate` | `Si_Substrate_Wafer` ($Z \in [-1.1, -0.4]$) and `SiO2_Buried_Oxide` ($Z \in [-0.4, 0.0]$). |
| `02_SWCNT_Wide_LowVth` | `SWCNT_Wide_13_0_Atoms` and `SWCNT_Wide_13_0_Bonds` centered at $Y = -1.40, Z = 0.95$. |
| `03_SWCNT_Narrow_HighVth` | `SWCNT_Narrow_7_0_Atoms` and `SWCNT_Narrow_7_0_Bonds` centered at $Y = +1.40, Z = 0.95$. |
| `04_Electrodes_Shared` | `Electrode_Source_Shared` ($X = -4.85$) and `Electrode_Drain_Shared` ($X = +4.85$) in $\text{Pd}/\text{Au}$. |
| `05_Dual_Gate_Stack` | Cutaway sleeves `HfO2_Wide_Channel`, `Gate_Metal_Wide`, `HfO2_Narrow_Channel`, `Gate_Metal_Narrow`, and `Shared_Gate_Bus_Vgs`. |
| `06_Ternary_Carriers_Bands` | `Electron_LowVth_Wide_01..08`, `Electron_HighVth_Narrow_01..08`, and Shape-Keyed band ribbons `Ec1_LowVth_Wide` and `Ec2_HighVth_Narrow`. |
| `07_Studio_Annotations` | `CNFET_Ternary_Camera`, 3-point Area lights (`Key_Light_Warm`, `Rim_Light_Cool`, `Fill_Light_Soft`), 3D text labels, and leader lines. |

---

## 4. Operational Workflow for Agents

### A. Rebuilding the Scene via CLI
Agents can regenerate [`blend/cnfet_ternary_threshold.blend`](blend/cnfet_ternary_threshold.blend) deterministically without manual GUI interaction:

```bash
blender --background --python scripts/build_ternary_cnfet.py
```

Or inside an interactive Python call:

```python
import sys
sys.path.append("/home/robson/coding/ternary-cnfet-3d/scripts")
import build_ternary_cnfet
build_ternary_cnfet.build_ternary_cnfet_scene("/home/robson/coding/ternary-cnfet-3d/blend/cnfet_ternary_threshold.blend")
```

### B. Live Inspection via Blender MCP (`mcp-for-blender`)
When connected to a live Blender 4.5 session via MCP:
1. **Verify Engine Compatibility:** Always ensure `bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'` before capturing viewport renders with `look(mode="camera", shading="rendered")`.
2. **Visual Verification of Framing & Typography:** After modifying any 3D label or camera transform, call `look(mode="camera", shading="rendered", max_size=1024)` and inspect the resulting PNG to verify that:
   * No 3D text label is clipped by the camera frustum.
   * No 3D text label overlaps with the conduction band ribbons (`Ec1`, `Ec2`) or obscures the nanotube cutaway.
3. **Multi-State Animation Verification:** Use `look(mode="frames", frames=[20, 85, 160], view="camera", shading="rendered")` to validate States `-1`, `0`, and `+1` in a single contact sheet.

---

## 5. Roadmap for Educational Improvements

Agents tasked with expanding this educational repository should prioritize these high-impact modules:

1. **Standard Ternary Inverter (STI) Circuit Cell (`scripts/build_ternary_sti_gate.py`):**
   * Construct a complete 6-CNFET complementary ternary inverter combining p-type and n-type SWCNTs of diameters $d_1 = 1.02\text{ nm}$ and $d_2 = 0.55\text{ nm}$, showing the voltage transfer characteristic (VTC) curve with stable middle-level plateau at $V_{DD}/2$ (or $0\text{ V}$ in balanced rails $\{-V_{DD}, 0, +V_{DD}\}$).
2. **Interactive Classroom Sliders (Blender Custom Properties & Drivers):**
   * Attach a custom property `V_GS` (ranging from $-0.5\text{ V}$ to $+1.0\text{ V}$) on a central controller Empty, driving the `Ec1` and `Ec2` Shape Keys, gate emission intensity, and electron velocities in real time as an instructor drags the slider.
3. **NEGF / Poisson Electrostatic Potential Volume:**
   * Add a semi-transparent volumetric shader or colour-mapped potential surface around the GAA cutaway showing the radial potential distribution $\Phi(r, x)$ inside the $\text{HfO}_2$ dielectric layer.
4. **WebGL / glTF Interactive Export & MP4 Render Pipeline:**
   * Add a script (`scripts/render_animation.py`) that renders frames 1 to 180 into a 60 FPS MP4 video and exports a baked `.glb` model for browser-based 3D embedding.

---

## 6. Contribution & Style Rules

1. **Synchronized Code and Binary Assets:** Never modify [`blend/cnfet_ternary_threshold.blend`](blend/cnfet_ternary_threshold.blend) manually without porting the exact changes back into [`scripts/build_ternary_cnfet.py`](scripts/build_ternary_cnfet.py) and updating the PNG renders in [`renders/`](renders/).
2. **Blender 4.5 Principled BSDF Compatibility:** Always check input socket names dynamically (`"Transmission Weight"` vs. `"Transmission"`, `"Emission Color"` vs. `"Emission"`) to maintain compatibility across Blender 4.x releases.
3. **Language & Formatting:** Maintain all documentation, code comments, and 3D scene annotations in clear American English. Avoid em-dashes or en-dashes in prose and keep mathematical formulas formatted in LaTeX (`$...$` and `$$...$$`).
