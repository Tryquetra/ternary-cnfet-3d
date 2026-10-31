#!/usr/bin/env python3
"""
Manim Community Edition mathematical animation for Scene 2:
Chiral Diameter & Threshold Voltage Modulation (Vth = 0.43 V / d_CNT)
"""

from manim import *
import numpy as np


class TernaryCNFETThresholdPlot(Scene):
    def construct(self):
        self.camera.background_color = "#080c14"

        # Title Header
        title = Text(
            "CNFET Threshold Modulation via Nanotube Diameter",
            font="DejaVu Sans",
            font_size=32,
            weight=BOLD,
            color="#f0f6fc",
        ).to_edge(UP, buff=0.35)

        subtitle = Text(
            "d_CNT = 0.0783 * n (nm)     |     Eg = 0.84 eV / d_CNT     |     Vth = 0.43 V / d_CNT",
            font="DejaVu Sans Mono",
            font_size=20,
            color="#38bdf8",
        ).next_to(title, DOWN, buff=0.18)

        # Coordinate Axes: x = d_CNT (0.4 to 1.4 nm), y = V_th (0.0 to 1.2 V)
        axes = Axes(
            x_range=[0.4, 1.4, 0.2],
            y_range=[0.0, 1.2, 0.2],
            x_length=7.4,
            y_length=3.8,
            axis_config={"color": "#94a3b8", "include_tip": True, "stroke_width": 2.5},
            tips=True,
        ).shift(UP * 0.15 + LEFT * 1.05)

        x_label = Text("Diameter d_CNT (nm)", font="Liberation Sans", font_size=18, color="#cbd5e1").next_to(
            axes.x_axis, DOWN, buff=0.38
        )
        y_label = (
            Text("Threshold Vth (V)", font="Liberation Sans", font_size=18, color="#cbd5e1")
            .rotate(PI / 2)
            .next_to(axes.y_axis, LEFT, buff=0.85)
        )

        # Tick labels manually with Text (no LaTeX required)
        tick_labels = VGroup()
        for xv in [0.4, 0.6, 0.8, 1.0, 1.2, 1.4]:
            t = Text(f"{xv:.1f}", font="Liberation Mono", font_size=14, color="#94a3b8")
            t.next_to(axes.c2p(xv, 0), DOWN, buff=0.10)
            tick_labels.add(t)
        for yv in [0.2, 0.4, 0.6, 0.8, 1.0]:
            t = Text(f"{yv:.1f}V", font="Liberation Mono", font_size=14, color="#94a3b8")
            t.next_to(axes.c2p(0.4, yv), LEFT, buff=0.12)
            tick_labels.add(t)

        # Hyperbolic curve Vth(d) = 0.43 / d
        vth_curve = axes.plot(
            lambda d: 0.43 / d,
            x_range=[0.42, 1.35],
            color="#38bdf8",
            stroke_width=5,
        )

        # Operating Point 1: Wide SWCNT (13,0) -> d1 = 1.02 nm, Vth1 = 0.42 V
        d1, vth1 = 1.02, 0.43 / 1.02
        pt1 = axes.c2p(d1, vth1)
        dot1 = Dot(pt1, radius=0.11, color="#00f2d4")
        glow1 = Circle(radius=0.22, color="#00f2d4", stroke_width=2.5).move_to(pt1)
        h_line1 = DashedLine(axes.c2p(0.4, vth1), pt1, color="#00f2d4", stroke_width=2.2)
        v_line1 = DashedLine(axes.c2p(d1, 0.0), pt1, color="#00f2d4", stroke_width=2.2)
        lbl1 = Text(
            "CH1: SWCNT (13,0)\nd1 = 1.02 nm -> Vth1 = 0.42 V",
            font="DejaVu Sans Mono",
            font_size=16,
            color="#00f2d4",
        ).next_to(pt1, UP + RIGHT, buff=0.2)

        # Operating Point 2: Narrow SWCNT (7,0) -> d2 = 0.55 nm, Vth2 = 0.78 V
        d2, vth2 = 0.55, 0.43 / 0.55
        pt2 = axes.c2p(d2, vth2)
        dot2 = Dot(pt2, radius=0.11, color="#f59e0b")
        glow2 = Circle(radius=0.22, color="#f59e0b", stroke_width=2.5).move_to(pt2)
        h_line2 = DashedLine(axes.c2p(0.4, vth2), pt2, color="#f59e0b", stroke_width=2.2)
        v_line2 = DashedLine(axes.c2p(d2, 0.0), pt2, color="#f59e0b", stroke_width=2.2)
        lbl2 = Text(
            "CH2: SWCNT (7,0)\nd2 = 0.55 nm -> Vth2 = 0.78 V",
            font="DejaVu Sans Mono",
            font_size=16,
            color="#f59e0b",
        ).next_to(pt2, RIGHT, buff=0.25)

        # Right-hand Ternary State Legend Box
        box_group = VGroup()
        states_info = [
            ("STATE +1 (Vgs >= 0.78 V)", "CH1: ON   |  CH2: ON", "#22c55e"),
            ("STATE  0 (0.42 V..0.78 V)", "CH1: ON   |  CH2: OFF", "#00f2d4"),
            ("STATE -1 (Vgs < 0.42 V)", "CH1: OFF  |  CH2: OFF", "#f43f5e"),
        ]
        for idx, (st_title, st_sub, col) in enumerate(states_info):
            card = RoundedRectangle(
                corner_radius=0.12, width=4.1, height=1.05, stroke_color=col, stroke_width=2.5, fill_color=col, fill_opacity=0.12
            )
            t1 = Text(st_title, font="DejaVu Sans Mono", font_size=16, weight=BOLD, color=col)
            t2 = Text(st_sub, font="DejaVu Sans Mono", font_size=14, color="#e2e8f0")
            txt = VGroup(t1, t2).arrange(DOWN, buff=0.08).move_to(card.get_center())
            item = VGroup(card, txt).move_to(RIGHT * 4.45 + UP * (1.2 - idx * 1.35))
            box_group.add(item)

        # Animation Sequence (~23.7 seconds total to match voiceover)
        self.play(FadeIn(title, shift=DOWN * 0.2), FadeIn(subtitle), run_time=2.0)
        self.play(Create(axes), FadeIn(x_label), FadeIn(y_label), FadeIn(tick_labels), run_time=2.5)
        self.play(Create(vth_curve), run_time=3.5)
        self.play(
            Create(h_line1),
            Create(v_line1),
            FadeIn(dot1, scale=1.5),
            Create(glow1),
            FadeIn(lbl1, shift=UP * 0.15),
            run_time=4.5,
        )
        self.play(
            Create(h_line2),
            Create(v_line2),
            FadeIn(dot2, scale=1.5),
            Create(glow2),
            FadeIn(lbl2, shift=RIGHT * 0.15),
            run_time=4.5,
        )
        self.play(LaggedStart(*[FadeIn(b, shift=LEFT * 0.3) for b in box_group], lag_ratio=0.35), run_time=4.0)
        self.wait(3.0)
