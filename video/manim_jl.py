#!/usr/bin/env python3
"""
Manim animation v4: Johnson-Lindenstrauss in Pseudo-Euclidean Spaces
Duration target: > 3 minutes

Render (low quality preview):
  manim -ql manim_jl.py JLVideo

Render (high quality final):
  manim -qh manim_jl.py JLVideo
"""
from manim import *
import numpy as np

config.background_color = "#0D1117"

# ── Palette ───────────────────────────────────────────────────────────────────
C_BLUE   = "#4FC3F7"
C_PURPLE = "#CE93D8"
C_ORANGE = "#FFB74D"
C_GREEN  = "#81C784"
C_RED    = "#EF9A9A"
C_YELLOW = "#FFF176"
C_GRAY   = "#78909C"
C_WHITE  = "#E8EAF0"
C_DARK   = "#1C2128"
C_TEAL   = "#4DD0E1"


# ── Helpers ───────────────────────────────────────────────────────────────────
def hdr(title: str, color: str) -> VGroup:
    t   = Text(title, font_size=26, color=color, weight=BOLD).to_edge(UP, buff=0.28)
    sep = Line(LEFT * 7, RIGHT * 7, color=color, stroke_width=1.4).next_to(t, DOWN, buff=0.14)
    return VGroup(t, sep)


# ══════════════════════════════════════════════════════════════════════════════
class JLVideo(ThreeDScene):
    """Full animation ≥ 3 minutes (five acts)."""

    def construct(self):
        # Initial 2D camera view
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES)
        self.act1_jl_lemma()
        self.act2_pseudo_euclidean()
        self.act3_light_cone()
        self.act4_proof()
        self.act5_clustering()

    # ══════════════════════════════════════════════════════════════════════════
    # ACT 1 — JL-лемма  (~70 s)
    # ══════════════════════════════════════════════════════════════════════════
    def act1_jl_lemma(self):
        # ── Title card ────────────────────────────────────────────────────────
        title = Text("Лемма Джонсона–Линденштраусса", font_size=38, color=C_BLUE, weight=BOLD)
        sub_t1 = Text("в псевдоевклидовом пространстве ", font_size=24, color=C_GRAY)
        sub_m1 = MathTex(r"\mathbb{R}^{p,q}", font_size=30, color=C_YELLOW)
        sub_grp = VGroup(sub_t1, sub_m1).arrange(RIGHT, buff=0.15)
        card  = VGroup(title, sub_grp).arrange(DOWN, buff=0.4).move_to(ORIGIN)
        
        self.play(FadeIn(title, shift=UP * 0.25), run_time=1.0)
        self.wait(0.5)
        self.play(FadeIn(sub_grp, shift=UP * 0.15))
        self.wait(3.0)
        self.play(FadeOut(card))
        self.wait(0.3)

        # ── Act header ────────────────────────────────────────────────────────
        header = hdr("Шаг 1 — Лемма Джонсона–Линденштраусса в евклидовом пространстве", C_BLUE)
        self.add_fixed_in_frame_mobjects(header)
        self.play(FadeIn(header, shift=DOWN * 0.08))

        # ── Conceptual points in 3D (d=1000 high-dimensional points visualization) ──
        np.random.seed(10)
        n_pts = 120
        d_high = 3
        
        # 4 clusters in 3D
        centers = np.array([
            [ 1.4,  1.4,  1.4],
            [-1.4, -1.4,  1.4],
            [ 1.4, -1.4, -1.4],
            [-1.4,  1.4, -1.4]
        ])
        
        X_3d = np.vstack([
            centers[k % 4] + np.random.randn(n_pts // 4, d_high) * 0.42
            for k in range(4)
        ])
        
        scale_3d = 0.65
        X_3d_scaled = X_3d * scale_3d
        
        cluster_colors = [C_BLUE, C_GREEN, C_ORANGE, C_PURPLE]
        
        dots_3d = VGroup(*[
            Dot3D(point=[X_3d_scaled[i, 0] - 2.5, X_3d_scaled[i, 1], X_3d_scaled[i, 2]],
                  radius=0.08,
                  color=cluster_colors[(i * 4 // n_pts) % 4]
                  ).set_opacity(0.85)
            for i in range(n_pts)
        ])

        # Show initial high dimension label in TeX (centered under the dots on the left)
        dim_lbl_t = Text("Исходная размерность ", font_size=15, color=C_GRAY)
        dim_lbl_m = MathTex(r"d = 1000", font_size=18, color=C_YELLOW)
        dim_lbl = VGroup(dim_lbl_t, dim_lbl_m).arrange(RIGHT, buff=0.06).move_to(LEFT * 2.5 + DOWN * 2.0)
        self.add_fixed_in_frame_mobjects(dim_lbl)

        self.play(FadeIn(dots_3d, shift=UP * 0.1), Write(dim_lbl), run_time=1.5)
        
        # Rotate camera to showcase 3D structure
        self.move_camera(phi=70 * DEGREES, theta=-45 * DEGREES, run_time=2.0)
        # Rotate only the dots, not the entire scene
        self.play(Rotate(dots_3d, angle=1.5 * TAU, axis=UP + RIGHT, about_point=LEFT * 2.5), run_time=3.5)
        self.wait(0.5)

        # ── Projection to 2D plane (visual collapsing) ────────────────────────
        proj_plane = Square(side_length=3.5, fill_color=C_TEAL, fill_opacity=0.15, stroke_color=C_TEAL, stroke_width=1.5)
        proj_plane.move_to([-2.5, 0, -1.2])
        self.play(Create(proj_plane), run_time=1.0)
        self.wait(0.5)

        # Collapse points onto the plane z = -1.2
        self.play(
            *[
                d.animate.move_to([d.get_center()[0], d.get_center()[1], -1.2])
                for d in dots_3d
            ],
            run_time=2.2
        )
        self.wait(0.5)

        # Convert to flat 2D dots, shift camera back to standard 2D view
        dots_2d = VGroup(*[
            Dot(point=[d.get_center()[0], d.get_center()[1], 0],
                radius=0.06,
                color=d.get_color()
                ).set_opacity(0.85)
            for d in dots_3d
        ])
        
        self.move_camera(
            phi=0.05 * DEGREES, theta=-90 * DEGREES,
            added_anims=[Transform(dots_3d, dots_2d)],
            run_time=1.8
        )
        self.wait(0.2)

        # ── Show beautiful explanation box on the right ──────────────────────
        idea_box = RoundedRectangle(
            width=6.0, height=3.5, corner_radius=0.15,
            fill_color=C_DARK, fill_opacity=0.95,
            stroke_color=C_BLUE, stroke_width=1.5
        ).move_to(RIGHT * 3.1 + DOWN * 0.1)
        
        idea_title = Text("Идея сжатия:", font_size=15, color=C_BLUE, weight=BOLD)
        idea_text1 = Text("Снизить размерность данных так,", font_size=13, color=C_WHITE)
        idea_text2 = Text("чтобы все попарные расстояния", font_size=13, color=C_WHITE)
        idea_text3 = Text("изменились не более чем на", font_size=13, color=C_WHITE)
        
        idea_formula = MathTex(
            r"(1-\varepsilon)\|x_i - x_j\|^2 \;\le\;"
            r"\|f(x_i) - f(x_j)\|^2 \;\le\;"
            r"(1+\varepsilon)\|x_i - x_j\|^2",
            font_size=14, color=C_YELLOW
        )
        
        idea_grp = VGroup(
            idea_title, idea_text1, idea_text2, idea_text3, idea_formula
        ).arrange(DOWN, buff=0.16).move_to(idea_box.get_center())

        target_lbl_t = Text("Целевая размерность ", font_size=15, color=C_GRAY)
        target_lbl_m = MathTex(r"k = O\left(\frac{\log n}{\varepsilon^2}\right)", font_size=18, color=C_GREEN)
        target_lbl = VGroup(target_lbl_t, target_lbl_m).arrange(RIGHT, buff=0.06).next_to(idea_box, DOWN, buff=0.3)
        self.add_fixed_in_frame_mobjects(target_lbl)

        self.play(Create(idea_box))
        self.play(Write(idea_grp))
        self.play(Write(target_lbl))
        self.wait(3.0)

        # Clean up Act 1 visualization
        self.play(FadeOut(VGroup(dots_3d, proj_plane, dim_lbl, idea_box, idea_grp, target_lbl)))
        self.wait(0.2)

        # ── Full formulation (drawn step-by-step) ─────────────────────────────
        def_box = RoundedRectangle(
            width=10.5, height=3.8, corner_radius=0.2,
            fill_color="#161B22", fill_opacity=1.0,
            stroke_color=C_BLUE, stroke_width=2,
        ).move_to(DOWN * 0.1)

        def_title_t1 = Text("Лемма Джонсона–Линденштраусса (", font_size=19, color=C_BLUE, weight=BOLD)
        def_title_m1 = MathTex(r"\varepsilon", font_size=24, color=C_YELLOW)
        def_title_t2 = Text("-изометрия)", font_size=19, color=C_BLUE, weight=BOLD)
        def_title = VGroup(def_title_t1, def_title_m1, def_title_t2).arrange(RIGHT, buff=0.08)
        def_title.move_to(def_box.get_top() + DOWN * 0.4)

        item1_t1 = Text("Для любого набора из ", font_size=16, color=C_WHITE)
        item1_m1 = MathTex(r"n", font_size=18, color=C_YELLOW)
        item1_t2 = Text(" точек в евклидовом пространстве и ", font_size=16, color=C_WHITE)
        item1_m2 = MathTex(r"0 < \varepsilon < 1", font_size=18, color=C_YELLOW)
        item1 = VGroup(item1_t1, item1_m1, item1_t2, item1_m2).arrange(RIGHT, buff=0.06)

        item2 = Text("существует отображение f, сохраняющее расстояния с относительной точностью:", font_size=15, color=C_GRAY)
        
        item3 = MathTex(
            r"(1-\varepsilon)\|x_i - x_j\|^2 \;\le\; \|f(x_i) - f(x_j)\|^2 \;\le\; (1+\varepsilon)\|x_i - x_j\|^2",
            font_size=24, color=C_YELLOW
        )
        
        item4_t1 = Text("где размерность целевого пространства ", font_size=16, color=C_GRAY)
        item4_m1 = MathTex(r"k", font_size=20, color=C_GREEN)
        item4_t2 = Text(" составляет всего:", font_size=16, color=C_GRAY)
        item4_grp = VGroup(item4_t1, item4_m1, item4_t2).arrange(RIGHT, buff=0.08)
        
        item5 = MathTex(r"k \;=\; O\!\left(\frac{\log n}{\varepsilon^2}\right)", font_size=32, color=C_GREEN)

        def_body = VGroup(item1, item2, item3, item4_grp, item5).arrange(DOWN, buff=0.25).move_to(def_box.get_center() + DOWN * 0.12)

        self.play(Create(def_box))
        self.play(Write(def_title))
        for item in def_body:
            self.play(FadeIn(item, shift=UP * 0.08), run_time=0.6)
        self.wait(5.5)

        self.play(FadeOut(VGroup(header, def_box, def_title, def_body)))
        self.wait(0.4)

    # ══════════════════════════════════════════════════════════════════════════
    # ACT 2 — Псевдоевклидово пространство  (~60 s)
    # ══════════════════════════════════════════════════════════════════════════
    def act2_pseudo_euclidean(self):
        header_tex_t = Text("Шаг 2 — Псевдоевклидово пространство ", font_size=26, color=C_PURPLE, weight=BOLD)
        header_tex_m = MathTex(r"\mathbb{R}^{p,q}", font_size=30, color=C_YELLOW)
        header_tex = VGroup(header_tex_t, header_tex_m).arrange(RIGHT, buff=0.15).to_edge(UP, buff=0.28)
        header_line = Line(LEFT * 7, RIGHT * 7, color=C_PURPLE, stroke_width=1.4).next_to(header_tex, DOWN, buff=0.14)
        
        self.play(FadeIn(header_tex, shift=DOWN * 0.08), Create(header_line))

        # ── Motivating distance matrix (left side) ────────────────────────────
        np.random.seed(9)
        matrix_vals = np.array([
            [ 0.0,  3.2, -1.5,  2.0, -2.4],
            [ 3.2,  0.0,  1.8, -0.7,  4.1],
            [-1.5,  1.8,  0.0,  3.5, -0.9],
            [ 2.0, -0.7,  3.5,  0.0,  1.2],
            [-2.4,  4.1, -0.9,  1.2,  0.0]
        ])
        
        tile_s = 0.72
        matrix_tiles = VGroup()
        matrix_labels = VGroup()
        
        for i in range(5):
            for j in range(5):
                val = matrix_vals[i, j]
                if i == j:
                    col = C_DARK
                    opa = 0.6
                else:
                    col = C_BLUE if val > 0 else C_RED
                    opa = 0.8
                sq = Square(side_length=tile_s - 0.05, fill_color=col, fill_opacity=opa,
                            stroke_color="#2A3040", stroke_width=0.8)
                sq.move_to([
                    -3.8 + j * tile_s - 0.8,
                    1.4 - i * tile_s,
                    0
                ])
                matrix_tiles.add(sq)
                if i != j:
                    lbl = Text(f"{val:+.1f}", font_size=11, color=C_WHITE).move_to(sq.get_center())
                    matrix_labels.add(lbl)

        matrix_title = Text("Матрица квадратов расстояний d²ᵢⱼ", font_size=15, color=C_GRAY)
        matrix_title.next_to(matrix_tiles, DOWN, buff=0.25)
        
        # Legend with strict LaTeX!
        leg_t1 = MathTex(r"d^2 > 0", font_size=20, color=C_BLUE)
        leg_item1 = VGroup(Square(0.18, fill_color=C_BLUE, fill_opacity=0.8, stroke_width=0), leg_t1).arrange(RIGHT, buff=0.12)
        
        leg_t2 = MathTex(r"d^2 < 0", font_size=20, color=C_RED)
        leg_item2 = VGroup(Square(0.18, fill_color=C_RED, fill_opacity=0.8, stroke_width=0), leg_t2).arrange(RIGHT, buff=0.12)
        
        legend = VGroup(leg_item1, leg_item2).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        legend.next_to(matrix_tiles, RIGHT, buff=0.25).shift(UP * 0.7)

        # ── Explanations on the right (strictly shifted higher to avoid overlap) ───────
        expl_text1 = Text("Изучая геномы, фильмы или графы,", font_size=15, color=C_WHITE)
        expl_text2 = Text("мы часто получаем матрицы несходств,", font_size=15, color=C_WHITE)
        expl_text3 = Text("у которых часть собственных значений", font_size=15, color=C_WHITE)
        
        hsm_lbl = Text("отрицательна. Это свойство ", font_size=15, color=C_WHITE)
        hsm_bold = Text("HSM", font_size=15, color=C_PURPLE, weight=BOLD)
        hsm_grp = VGroup(hsm_lbl, hsm_bold).arrange(RIGHT, buff=0.06)
        
        expl_text4_t1 = Text("— пространств со знакопеременной метрикой.", font_size=15, color=C_GRAY)
        
        expl_text5_t1 = Text("Квадрат расстояния ", font_size=15, color=C_GRAY)
        expl_text5_m1 = MathTex(r"d^2", font_size=20, color=C_RED)
        expl_text5_t2 = Text(" может быть отрицательным!", font_size=15, color=C_RED)
        expl_text5_grp = VGroup(expl_text5_t1, expl_text5_m1, expl_text5_t2).arrange(RIGHT, buff=0.06)

        expl_text = VGroup(
            expl_text1, expl_text2, expl_text3, hsm_grp, expl_text4_t1, expl_text5_grp
        ).arrange(DOWN, buff=0.28, aligned_edge=LEFT) # Increased spacing (buff=0.28)
        expl_text.move_to(RIGHT * 3.3 + UP * 0.2) # Shifted higher (UP * 0.2)

        # Render everything sequentially
        self.play(LaggedStart(*[FadeIn(s, scale=0.5) for s in matrix_tiles], lag_ratio=0.03), run_time=1.2)
        self.play(LaggedStart(*[Write(l) for l in matrix_labels], lag_ratio=0.02), Write(matrix_title), FadeIn(legend), run_time=1.0)
        
        # Write explanation on the right step-by-step
        for item in expl_text:
            self.play(FadeIn(item, shift=RIGHT * 0.08), run_time=0.5)
        self.wait(4.0)

        # Remove matrix view
        self.play(FadeOut(VGroup(matrix_tiles, matrix_labels, matrix_title, legend, expl_text)))
        self.wait(0.2)

        # ── Formal definition of R^{p,q} (drawn step-by-step) ────────────────
        def_box = RoundedRectangle(
            width=10.8, height=4.2, corner_radius=0.2,
            fill_color="#161B22", fill_opacity=1.0,
            stroke_color=C_PURPLE, stroke_width=2,
        ).move_to(DOWN * 0.1)

        def_lbl_t1 = Text("Определение псевдоевклидова пространства ", font_size=19, color=C_PURPLE, weight=BOLD)
        def_lbl_m1 = MathTex(r"\mathbb{R}^{p,q}", font_size=24, color=C_YELLOW)
        def_lbl = VGroup(def_lbl_t1, def_lbl_m1).arrange(RIGHT, buff=0.08)
        def_lbl.move_to(def_box.get_top() + DOWN * 0.4)

        def_item1_t1 = Text("Пространство с квадратичной формой сигнатуры ", font_size=16, color=C_WHITE)
        def_item1_m1 = MathTex(r"(p, q)", font_size=20, color=C_YELLOW)
        def_item1_grp = VGroup(def_item1_t1, def_item1_m1).arrange(RIGHT, buff=0.06)

        def_item2 = MathTex(r"\|v\|^2_{p,q} \;=\; \sum_{i=1}^{p} v_i^2 \;-\; \sum_{j=p+1}^{p+q} v_j^2", font_size=28, color=C_YELLOW)
        
        def_item3_t1 = Text("Оно содержит ", font_size=15, color=C_GRAY)
        def_item3_m1 = MathTex(r"p", font_size=18, color=C_GREEN)
        def_item3_t2 = Text(" положительных и ", font_size=15, color=C_GRAY)
        def_item3_m2 = MathTex(r"q", font_size=18, color=C_RED)
        def_item3_t3 = Text(" отрицательных направлений.", font_size=15, color=C_GRAY)
        def_item3_grp = VGroup(def_item3_t1, def_item3_m1, def_item3_t2, def_item3_m2, def_item3_t3).arrange(RIGHT, buff=0.06)

        def_item4 = Text("Скалярное произведение знакопеременно:", font_size=16, color=C_WHITE)
        def_item5 = MathTex(r"\langle u, v \rangle_{p,q} \;=\; \sum_{i=1}^p u_i v_i \;-\; \sum_{j=p+1}^{p+q} u_j v_j", font_size=24, color=C_TEAL)

        def_content = VGroup(def_item1_grp, def_item2, def_item3_grp, def_item4, def_item5).arrange(DOWN, buff=0.25).move_to(def_box.get_center() + DOWN * 0.12)

        self.play(Create(def_box), Write(def_lbl))
        for item in def_content:
            self.play(FadeIn(item, shift=UP * 0.08), run_time=0.6)
        self.wait(4.0)

        # ── Question in LaTeX ─────────────────────────────────────────────────
        q_text = Text("Работает ли JL-лемма в ", font_size=24, color=C_WHITE)
        q_math = MathTex(r"\mathbb{R}^{p,q}?", font_size=32, color=C_YELLOW)
        q_group = VGroup(q_text, q_math).arrange(RIGHT, buff=0.15)
        q_group.to_edge(DOWN, buff=0.45)

        self.play(
            def_box.animate.set_opacity(0.3),
            *[it.animate.set_opacity(0.2) for it in def_content],
            def_lbl.animate.set_opacity(0.2),
        )
        self.play(Write(q_group))
        self.wait(4.5)

        self.play(FadeOut(VGroup(header_tex, header_line, def_box, def_lbl, def_content, q_group)))
        self.wait(0.4)

    # ══════════════════════════════════════════════════════════════════════════
    # ACT 3 — Световой конус в 2D/zy Projection (~50 s)
    # ══════════════════════════════════════════════════════════════════════════
    def act3_light_cone(self):
        header_t = Text("Шаг 3 — Геометрия светового конуса в ", font_size=26, color=C_ORANGE, weight=BOLD)
        header_m = MathTex(r"\mathbb{R}^{p,q}", font_size=30, color=C_YELLOW)
        header = VGroup(header_t, header_m).arrange(RIGHT, buff=0.12).to_edge(UP, buff=0.28)
        header_line = Line(LEFT * 7, RIGHT * 7, color=C_ORANGE, stroke_width=1.4).next_to(header, DOWN, buff=0.14)
        header_all = VGroup(header, header_line)
        self.add_fixed_in_frame_mobjects(header_all)
        
        self.play(FadeIn(header_all, shift=DOWN * 0.08))

        # ── 3D Double Cone (x^2 + y^2 = z^2) ──────────────────────────────────
        top_cone = Surface(
            lambda u, v: np.array([u * np.cos(v), u * np.sin(v), u]),
            u_range=[0, 2.0], v_range=[0, TAU],
            resolution=(15, 30),
            fill_color=C_ORANGE, fill_opacity=0.35,
            stroke_color=C_ORANGE, stroke_width=0.3
        )
        bot_cone = Surface(
            lambda u, v: np.array([u * np.cos(v), u * np.sin(v), -u]),
            u_range=[0, 2.0], v_range=[0, TAU],
            resolution=(15, 30),
            fill_color=C_ORANGE, fill_opacity=0.35,
            stroke_color=C_ORANGE, stroke_width=0.3
        )
        cone_3d = VGroup(top_cone, bot_cone)
        
        # 3D Axes
        cone_ax = ThreeDAxes(
            x_range=[-2.5, 2.5], y_range=[-2.5, 2.5], z_range=[-2.5, 2.5],
            x_length=4.5, y_length=4.5, z_length=4.5,
            axis_config={"color": C_GRAY, "stroke_width": 1.2}
        )
        
        ylbl = MathTex(r"y", font_size=18, color=C_GRAY).next_to(cone_ax.y_axis.get_end(), RIGHT, buff=0.1)
        zlbl = MathTex(r"z", font_size=18, color=C_GRAY).next_to(cone_ax.z_axis.get_end(), UP, buff=0.1)
        cone_ax_grp = VGroup(cone_ax, ylbl, zlbl)
        
        cone_title = Text("Световой конус (d² = 0)", font_size=18, color=C_ORANGE)
        cone_title.to_edge(UP, buff=1.2)
        self.add_fixed_in_frame_mobjects(cone_title)
        
        # Animate initial presentation in 3D perspective
        self.play(FadeIn(cone_ax_grp), FadeIn(cone_3d), Write(cone_title), run_time=1.5)
        self.move_camera(phi=75 * DEGREES, theta=-45 * DEGREES, run_time=2.0)
        # Rotate ONLY the cone, not the whole scene
        self.play(Rotate(cone_3d, angle=1.5 * TAU, axis=UP), run_time=3.5)
        self.wait(0.5)
        
        # ── Transition to flat 2D projection ──────────────────────────────────
        cone_ax_2d = Axes(
            x_range=[-2.5, 2.5], y_range=[-2.5, 2.5],
            x_length=4.5, y_length=4.5,
            axis_config={"color": C_GRAY, "stroke_width": 1.2}
        )
        ylbl_2d = MathTex(r"y", font_size=18, color=C_GRAY).next_to(cone_ax_2d.x_axis.get_end(), RIGHT, buff=0.1)
        zlbl_2d = MathTex(r"z", font_size=18, color=C_GRAY).next_to(cone_ax_2d.y_axis.get_end(), UP, buff=0.1)
        line1_2d = cone_ax_2d.plot(lambda x: x, color=C_ORANGE, stroke_width=2.5)
        line2_2d = cone_ax_2d.plot(lambda x: -x, color=C_ORANGE, stroke_width=2.5)
        cone_2d_grp = VGroup(cone_ax_2d, ylbl_2d, zlbl_2d, line1_2d, line2_2d).move_to(ORIGIN)

        self.move_camera(
            phi=0.05 * DEGREES, theta=-90 * DEGREES,
            added_anims=[
                FadeOut(cone_3d),
                FadeOut(cone_ax_grp),
                FadeIn(cone_2d_grp)
            ],
            run_time=2.0
        )
        self.wait(0.5)
        
        # Now place two points on the line and show their distance is zero
        pt1 = Dot(point=cone_ax_2d.c2p(1.5, 1.5), radius=0.09, color=C_RED)
        pt2 = Dot(point=cone_ax_2d.c2p(0.5, 0.5), radius=0.09, color=C_RED)
        line_connect = Line(start=pt2.get_center(), end=pt1.get_center(), color=C_RED, stroke_width=3.5)
        
        lbl_x1 = MathTex(r"x_1", font_size=16, color=C_RED)
        lbl_x2 = MathTex(r"x_2", font_size=16, color=C_RED)
        lbl_x1.next_to(pt1, RIGHT, buff=0.12)
        lbl_x2.next_to(pt2, RIGHT, buff=0.12)
        
        self.play(FadeIn(pt1), FadeIn(pt2), Write(lbl_x1), Write(lbl_x2))
        self.play(Create(line_connect), run_time=1.0)
        self.wait(0.5)
        
        # Distance label
        dist_val = MathTex(r"\|x_1 - x_2\|_{p,q}^2 = 0 \quad (x_1 \neq x_2)", font_size=20, color=C_RED)
        dist_val.to_edge(UP, buff=1.4).shift(LEFT * 2.8)
        self.play(Write(dist_val))
        self.wait(1.5)
        
        # Group everything together to shift left
        cone_grp = VGroup(cone_2d_grp, pt1, pt2, line_connect, lbl_x1, lbl_x2)
        
        self.play(
            cone_grp.animate.shift(LEFT * 2.8),
            dist_val.animate.shift(LEFT * 2.8),
            cone_title.animate.shift(LEFT * 2.8),
            run_time=2.0
        )
        self.wait(0.5)

        # ── Explanation box on the right (perfect alignment, no overlap) ──────
        expl_box = RoundedRectangle(
            width=6.0, height=4.2, corner_radius=0.15,
            fill_color=C_DARK, fill_opacity=0.95,
            stroke_color=C_ORANGE, stroke_width=1.5
        ).move_to(RIGHT * 3.3 + DOWN * 0.1)

        t_cone_1 = Text("Световой конус — множество", font_size=15, color=C_WHITE)
        t_cone_2_t = Text("векторов ", font_size=15, color=C_WHITE)
        t_cone_2_m = MathTex(r"v", font_size=18, color=C_YELLOW)
        t_cone_2_t2 = Text(" с нулевой псевдонормой:", font_size=15, color=C_WHITE)
        t_cone_2 = VGroup(t_cone_2_t, t_cone_2_m, t_cone_2_t2).arrange(RIGHT, buff=0.06)
        
        t_cone_3 = MathTex(r"V_0 \;=\; \{ v \in \mathbb{R}^{p,q} \mid \|v\|_{p,q}^2 = 0 \}", font_size=18, color=C_ORANGE)

        t_cone_4_t = Text("Точки ", font_size=15, color=C_GRAY)
        t_cone_4_m1 = MathTex(r"x", font_size=18, color=C_YELLOW)
        t_cone_4_t2 = Text(" и ", font_size=15, color=C_GRAY)
        t_cone_4_m2 = MathTex(r"y", font_size=18, color=C_YELLOW)
        t_cone_4_t3 = Text(" могут быть далеко", font_size=15, color=C_GRAY)
        t_cone_4 = VGroup(t_cone_4_t, t_cone_4_m1, t_cone_4_t2, t_cone_4_m2, t_cone_4_t3).arrange(RIGHT, buff=0.06)
        
        t_cone_5 = Text("в обычном евклидовом смысле, но", font_size=15, color=C_GRAY)
        
        t_cone_6_t = Text("иметь нулевое расстояние в ", font_size=15, color=C_GRAY)
        t_cone_6_m = MathTex(r"\mathbb{R}^{p,q}:", font_size=18, color=C_YELLOW)
        t_cone_6 = VGroup(t_cone_6_t, t_cone_6_m).arrange(RIGHT, buff=0.06)
        
        t_cone_7 = MathTex(r"\|x - y\|_{p,q}^2 = 0 \quad (x \neq y)", font_size=20, color=C_RED)
        
        t_cone_8 = Text("Это фундаментально ломает", font_size=15, color=C_YELLOW)
        t_cone_8_2 = Text("классическое евклидово сжатие.", font_size=15, color=C_YELLOW)

        expl_text = VGroup(
            t_cone_1, t_cone_2, t_cone_3, t_cone_4, t_cone_5, t_cone_6, t_cone_7, t_cone_8, t_cone_8_2
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to(expl_box) # Increased line spacing (buff=0.25)

        self.play(Create(expl_box))
        for item in expl_text:
            self.play(FadeIn(item, shift=UP * 0.05), run_time=0.45)
        self.wait(5.0)

        self.play(FadeOut(VGroup(
            header, header_line, cone_grp, cone_title, expl_box, expl_text, dist_val
        )))
        self.wait(0.4)

    # ══════════════════════════════════════════════════════════════════════════
    # ACT 4 — Доказательство нижней оценки  (~85 s)
    # ══════════════════════════════════════════════════════════════════════════
    def act4_proof(self):
        header = hdr("Шаг 4 — Доказательство нижней оценки", C_GREEN)
        self.play(FadeIn(header, shift=DOWN * 0.08))

        # ── Preprint card (no overlaps, strictly clean layout!) ───────────────
        pre_box = RoundedRectangle(
            width=9.5, height=1.6, corner_radius=0.18,
            fill_color=C_DARK, fill_opacity=1.0,
            stroke_color=C_TEAL, stroke_width=2,
        ).move_to(UP * 1.7)

        pre_badge = Text("Препринт  2025", font_size=14, color=C_DARK, weight=BOLD)
        pre_badge_bg = SurroundingRectangle(
            pre_badge, color=C_TEAL, buff=0.12,
            corner_radius=0.08, fill_color=C_TEAL, fill_opacity=1.0)
        pre_badge_grp = VGroup(pre_badge_bg, pre_badge)
        pre_badge_grp.move_to(pre_box.get_corner(UL) + RIGHT * 1.1 + DOWN * 0.3)

        pre_text_t = Text("Аналог JL-леммы доказан для ", font_size=16, color=C_WHITE)
        pre_text_m = MathTex(r"\mathbb{R}^{p,q}", font_size=20, color=C_YELLOW)
        pre_text_t2 = Text(" с точностью до константы ", font_size=16, color=C_WHITE)
        pre_text_m2 = MathTex(r"C_{ij}", font_size=20, color=C_GREEN)
        pre_text = VGroup(pre_text_t, pre_text_m, pre_text_t2, pre_text_m2).arrange(RIGHT, buff=0.06)
        pre_text.move_to(pre_box.get_center() + DOWN * 0.2)

        self.play(Create(pre_box))
        self.play(FadeIn(pre_badge_grp), Write(pre_text))
        self.wait(1.0)

        # ── Task Formulation block with exact preprint inequality ─────────────
        task_box = RoundedRectangle(
            width=11.2, height=1.8, corner_radius=0.18,
            fill_color=C_DARK, fill_opacity=1.0,
            stroke_color=C_BLUE, stroke_width=1.5,
        ).move_to(DOWN * 0.3)
        
        task_title = Text("Постановка задачи сжатия", font_size=16, color=C_BLUE, weight=BOLD)
        task_title.move_to(task_box.get_top() + DOWN * 0.3)
        
        # Formula: (1 - eps * C_ij)||x_i - x_j||^2 <= ||f(x_i) - f(x_j)||^2 <= (1 + eps * C_ij)||x_i - x_j||^2
        task_formula = MathTex(
            r"(1 - \varepsilon \cdot ",
            r"C_{ij}",
            r")\|x_i - x_j\|_{p,q}^2 \;\le\; \|f(x_i) - f(x_j)\|_{p',q'}^2 \;\le\; (1 + \varepsilon \cdot ",
            r"C_{ij}",
            r")\|x_i - x_j\|_{p,q}^2",
            font_size=22, color=C_YELLOW
        )
        task_formula.move_to(task_box.get_center() + DOWN * 0.1)

        self.play(Create(task_box))
        self.play(Write(task_title))
        self.play(FadeIn(task_formula, shift=UP * 0.05))
        self.wait(2.5)

        # ── Highlight C_ij and interpret it ───────────────────────────────────
        self.play(FadeOut(pre_box), FadeOut(pre_badge_grp), FadeOut(pre_text),
                  task_box.animate.move_to(UP * 1.5))
        task_title.move_to(task_box.get_top() + DOWN * 0.3)
        task_formula.move_to(task_box.get_center() + DOWN * 0.1)
        self.wait(0.5)

        # Separate formula to show C_ij definition
        cij_eq_math = MathTex(
            r"C_{ij} \;=\; \left|\frac{\|x_i-x_j\|_E^2}{\|x_i-x_j\|_{p,q}^2}\right|",
            font_size=28, color=C_YELLOW,
        ).move_to(DOWN * 0.2)
        
        cij_highlight_box = SurroundingRectangle(cij_eq_math, color=C_YELLOW, buff=0.18, stroke_width=2.0)
        
        # Highlight C_ij in the main formula above
        cij_hl1 = SurroundingRectangle(task_formula[1], color=C_RED, buff=0.06, stroke_width=1.5)
        cij_hl2 = SurroundingRectangle(task_formula[3], color=C_RED, buff=0.06, stroke_width=1.5)
        
        cij_interp_1_t1 = Text("Константа ", font_size=16, color=C_WHITE)
        cij_interp_1_m1 = MathTex(r"C_{ij}", font_size=20, color=C_YELLOW)
        cij_interp_1_t2 = Text(" характеризует близость к световому конусу.", font_size=16, color=C_WHITE)
        cij_interp_1 = VGroup(cij_interp_1_t1, cij_interp_1_m1, cij_interp_1_t2).arrange(RIGHT, buff=0.06)

        cij_interp_2_t1 = Text("При приближении к конусу ", font_size=15, color=C_GRAY)
        cij_interp_2_m1 = MathTex(r"C_{ij} \to +\infty", font_size=18, color=C_RED)
        cij_interp_2_t2 = Text(", и погрешность неограниченно растет.", font_size=15, color=C_GRAY)
        cij_interp_2 = VGroup(cij_interp_2_t1, cij_interp_2_m1, cij_interp_2_t2).arrange(RIGHT, buff=0.06)
        
        cij_interp = VGroup(cij_interp_1, cij_interp_2).arrange(DOWN, buff=0.25).to_edge(DOWN, buff=0.6)

        self.play(Create(cij_hl1), Create(cij_hl2))
        self.play(Write(cij_eq_math))
        self.play(Create(cij_highlight_box))
        self.wait(1.5)
        
        for item in cij_interp:
            self.play(FadeIn(item, shift=UP * 0.08), run_time=0.6)
        self.wait(5.0)

        self.play(FadeOut(VGroup(task_box, task_title, task_formula, cij_hl1, cij_hl2, cij_eq_math, cij_highlight_box, cij_interp)))
        self.wait(0.2)

        # ── KEY IDEA: counting & Milnor-Thom (Strictly structured based on anti-proof.tex) ──
        idea_title = Text("Идея доказательства", font_size=24, color=C_ORANGE, weight=BOLD)
        idea_title.to_edge(UP, buff=1.2)

        # ── Step 1: Реализуемость «матриц светового конуса» ──
        step1_title = Text("1. Реализуемость «матриц светового конуса»", font_size=18, color=C_GREEN, weight=BOLD)
        
        col1_t1 = Text("Любая симметричная 0,1-матрица A размера n × n (нули на диагонали)", font_size=15, color=C_WHITE)
        
        t1_t1 = Text("реализуема точками в ", font_size=15, color=C_WHITE)
        t1_m1 = MathTex(r"\mathbb{R}^{n,n}:", font_size=18, color=C_YELLOW)
        t1_grp = VGroup(t1_t1, t1_m1).arrange(RIGHT, buff=0.06)
        
        t1_formula = MathTex(r"A_{ij} = 0 \iff \|x_i-x_j\|_{p,q}^2 = 0", font_size=22, color=C_YELLOW)
        
        col1_t3_t = Text("Конструкция — через положительно определенную матрицу Грама:", font_size=15, color=C_GRAY)
        col1_m2 = MathTex(r"M = I_n + \varepsilon_0 B", font_size=22, color=C_YELLOW)
        
        step1_content = VGroup(step1_title, col1_t1, t1_grp, t1_formula, col1_t3_t, col1_m2).arrange(DOWN, buff=0.28).move_to(DOWN * 0.1)

        self.play(Write(idea_title))
        for item in step1_content:
            self.play(FadeIn(item, shift=UP * 0.08), run_time=0.55)
        self.wait(5.0)

        self.play(FadeOut(step1_content))
        self.wait(0.2)

        # ── Step 2: Нижняя оценка по счёту ──
        step2_title = Text("2. Нижняя оценка по счёту", font_size=18, color=C_GREEN, weight=BOLD)
        
        t2_t1 = Text("Число матриц, реализуемых в пространстве сигнатуры ", font_size=15, color=C_WHITE)
        t2_m1 = MathTex(r"s = p + q,", font_size=18, color=C_YELLOW)
        t2_grp1 = VGroup(t2_t1, t2_m1).arrange(RIGHT, buff=0.06)
        
        r_txt_2_t = Text("ограничено сверху числом знаковых условий квадратичных полиномов", font_size=15, color=C_WHITE)
        r_txt_3_t = Text("(теорема Милнора–Тома / оценка Уоррена):", font_size=15, color=C_GRAY)
        
        r_txt_4_m = MathTex(r"N \;\le\; \left(\frac{C_0 n}{s}\right)^{ns}", font_size=24, color=C_YELLOW)
        
        t2_t2 = Text("При ", font_size=15, color=C_RED, weight=BOLD)
        t2_m2 = MathTex(r"s < C n", font_size=18, color=C_YELLOW)
        t2_t3 = Text(" не все матрицы реализуемы.", font_size=15, color=C_RED, weight=BOLD)
        t2_grp2 = VGroup(t2_t2, t2_m2, t2_t3).arrange(RIGHT, buff=0.06)

        step2_content = VGroup(step2_title, t2_grp1, r_txt_2_t, r_txt_3_t, r_txt_4_m, t2_grp2).arrange(DOWN, buff=0.28).move_to(DOWN * 0.1)

        for item in step2_content:
            self.play(FadeIn(item, shift=UP * 0.08), run_time=0.55)
        self.wait(5.0)

        self.play(FadeOut(step2_content))
        self.wait(0.2)

        # ── Step 3: Перенос на JL ──
        step3_title = Text("3. Перенос на JL", font_size=18, color=C_GREEN, weight=BOLD)
        
        trans_1_t = MathTex(r"\varepsilon", font_size=18, color=C_GREEN)
        trans_1_t2 = Text("-изометрия сохраняет нулевые расстояния.", font_size=15, color=C_WHITE)
        trans_1 = VGroup(trans_1_t, trans_1_t2).arrange(RIGHT, buff=0.06)

        trans_2_t = Text("Образы «плохой» конфигурации из ", font_size=15, color=C_WHITE)
        trans_2_m = MathTex(r"\min(p,q)", font_size=18, color=C_YELLOW)
        trans_2_t2 = Text(" точек", font_size=15, color=C_WHITE)
        trans_2 = VGroup(trans_2_t, trans_2_m, trans_2_t2).arrange(RIGHT, buff=0.06)

        trans_3_t = Text("дали бы реализацию в целевом пространстве малой сигнатуры", font_size=15, color=C_GRAY)
        trans_4_t = Text("— это приводит к противоречию.", font_size=15, color=C_RED, weight=BOLD)
        
        step3_content = VGroup(step3_title, trans_1, trans_2, trans_3_t, trans_4_t).arrange(DOWN, buff=0.28).move_to(DOWN * 0.1)
        
        for item in step3_content:
            self.play(FadeIn(item, shift=UP * 0.08), run_time=0.55)
        self.wait(5.0)
        
        self.play(FadeOut(VGroup(idea_title, step3_content)))
        self.wait(0.2)

        # ── Lower bound theorem (drawn step-by-step) ─────────────────────────
        res_box = RoundedRectangle(
            width=10.5, height=3.8, corner_radius=0.2,
            fill_color="#161B22", fill_opacity=1.0,
            stroke_color=C_GREEN, stroke_width=2,
        ).move_to(DOWN * 0.1)

        res_title_t = Text("Теорема: нижняя граница сигнатуры в ", font_size=19, color=C_GREEN, weight=BOLD)
        res_title_m = MathTex(r"\mathbb{R}^{p',q'}", font_size=24, color=C_YELLOW)
        res_title = VGroup(res_title_t, res_title_m).arrange(RIGHT, buff=0.08)
        res_title.move_to(res_box.get_top() + DOWN * 0.4)

        res_item1_t1 = Text("Всякое ", font_size=16, color=C_WHITE)
        res_item1_m1 = MathTex(r"\varepsilon", font_size=20, color=C_GREEN)
        res_item1_t2 = Text("-изометрическое вложение требует размерности:", font_size=16, color=C_WHITE)
        res_item1 = VGroup(res_item1_t1, res_item1_m1, res_item1_t2).arrange(RIGHT, buff=0.06)

        res_item2 = MathTex(r"p' + q' \;\ge\; C \cdot \min(p,\, q)", font_size=32, color=C_YELLOW)
        
        res_item3_t1 = Text("где ", font_size=16, color=C_GRAY)
        res_item3_m1 = MathTex(r"C > 0", font_size=20, color=C_TEAL)
        res_item3_t2 = Text(" — абсолютная константа.", font_size=16, color=C_GRAY)
        res_item3 = VGroup(res_item3_t1, res_item3_m1, res_item3_t2).arrange(RIGHT, buff=0.06)

        res_item4_t1 = Text("Сжатие до логарифма в ", font_size=16, color=C_WHITE)
        res_item4_m1 = MathTex(r"\mathbb{R}^{p',q'}", font_size=20, color=C_YELLOW)
        res_item4_t2 = Text(" невозможно.", font_size=16, color=C_RED, weight=BOLD)
        res_item4 = VGroup(res_item4_t1, res_item4_m1, res_item4_t2).arrange(RIGHT, buff=0.06)

        res_content = VGroup(res_item1, res_item2, res_item3, res_item4).arrange(DOWN, buff=0.28).move_to(res_box.get_center() + DOWN * 0.12) # Increased spacing (buff=0.28)

        self.play(Create(res_box), Write(res_title))
        for item in res_content:
            self.play(FadeIn(item, shift=UP * 0.08), run_time=0.6)
        self.wait(7.0)

        self.play(FadeOut(VGroup(header, res_box, res_title, res_content)))
        self.wait(0.4)

    # ══════════════════════════════════════════════════════════════════════════
    # ACT 5 — Кластеризация и методы  (~65 s)
    # ══════════════════════════════════════════════════════════════════════════
    def act5_clustering(self):
        header_t = Text("Шаг 5 — Применение в задаче кластеризации в ", font_size=26, color=C_PURPLE, weight=BOLD)
        header_m = MathTex(r"\mathbb{R}^{p,q}", font_size=30, color=C_YELLOW)
        header = VGroup(header_t, header_m).arrange(RIGHT, buff=0.12).to_edge(UP, buff=0.28)
        header_line = Line(LEFT * 7, RIGHT * 7, color=C_PURPLE, stroke_width=1.4).next_to(header, DOWN, buff=0.14)
        
        self.play(FadeIn(header, shift=DOWN * 0.08), Create(header_line))

        # ── Explanation about topology issues in R^{p,q} ──────────────────────
        why_title = Text("Проблема классических метрических методов", font_size=20, color=C_ORANGE, weight=BOLD)
        why_title.to_edge(UP, buff=1.2)

        why_item1 = Text("Кластеризация (например, k-means) — это метрический метод.", font_size=16, color=C_WHITE)
        why_item2 = Text("Результаты напрямую зависят от корректности расстояний.", font_size=16, color=C_WHITE)
        
        why_item3_t1 = Text("В псевдоевклидовых пространствах ", font_size=16, color=C_GRAY)
        why_item3_m1 = MathTex(r"\mathbb{R}^{p,q}", font_size=20, color=C_YELLOW)
        why_item3_t2 = Text(" метрика знакопеременна:", font_size=16, color=C_GRAY)
        why_item3 = VGroup(why_item3_t1, why_item3_m1, why_item3_t2).arrange(RIGHT, buff=0.06)

        why_m1 = MathTex(r"\|v\|^2_{p,q} < 0", font_size=20, color=C_RED)
        why_t1 = Text(" или ", font_size=15, color=C_RED)
        why_m2 = MathTex(r"\|v\|^2_{p,q} = 0", font_size=20, color=C_RED)
        why_t2 = Text(" (для ", font_size=15, color=C_RED)
        why_m3 = MathTex(r"v \neq 0", font_size=20, color=C_RED)
        why_t3 = Text(")", font_size=15, color=C_RED)
        why_item4 = VGroup(why_m1, why_t1, why_m2, why_t2, why_m3, why_t3).arrange(RIGHT, buff=0.06)
        why_item5 = Text("Здесь невозможно ввести топологию привычным образом.", font_size=16, color=C_WHITE)
        why_item6 = Text("Поэтому классические методы сжатия и кластеризации не применимы.", font_size=16, color=C_PURPLE, weight=BOLD)

        why_content = VGroup(why_item1, why_item2, why_item3, why_item4, why_item5, why_item6).arrange(DOWN, buff=0.28).move_to(DOWN * 0.1) # Increased spacing (buff=0.28)

        self.play(Write(why_title))
        for item in why_content:
            self.play(FadeIn(item, shift=RIGHT * 0.08), run_time=0.6)
        self.wait(5.0)

        self.play(FadeOut(VGroup(why_title, why_content)))
        self.wait(0.2)

        # ── Two specialized methods (No overlap, clean unified layout boxes!) ──
        m_title = Text("Методы адаптивного проецирования", font_size=20, color=C_ORANGE, weight=BOLD)
        m_title.to_edge(UP, buff=1.2)

        m1_box = RoundedRectangle(
            width=5.1, height=3.5, corner_radius=0.18,
            fill_color=C_DARK, fill_opacity=1.0,
            stroke_color=C_BLUE, stroke_width=2,
        ).move_to(LEFT * 2.9 + DOWN * 0.2)

        # Unified vertical group for box 1 contents to prevent overlap with title
        m1_content = VGroup(
            Text("MASS-WATERFILL", font_size=16, color=C_BLUE, weight=BOLD),
            Line(LEFT * 2.0, RIGHT * 2.0, color=C_BLUE, stroke_width=1.0),
            Text("Разделяет собственные значения", font_size=13, color=C_WHITE),
            Text("матрицы на положительную и", font_size=13, color=C_WHITE),
            Text("отрицательную части, применяя", font_size=13, color=C_WHITE),
            Text("свое сжатие к каждому блоку.", font_size=13, color=C_WHITE),
            MathTex(r"D \;\approx\; D_+ \;-\; D_-", font_size=18, color=C_YELLOW),
        ).arrange(DOWN, buff=0.20).move_to(m1_box.get_center())

        m2_box = RoundedRectangle(
            width=5.1, height=3.5, corner_radius=0.18,
            fill_color=C_DARK, fill_opacity=1.0,
            stroke_color=C_GREEN, stroke_width=2,
        ).move_to(RIGHT * 2.9 + DOWN * 0.2)

        # Unified vertical group for box 2 contents to prevent overlap with title
        m2_content = VGroup(
            Text("TOPLAM-HYBRID", font_size=16, color=C_GREEN, weight=BOLD),
            Line(LEFT * 2.0, RIGHT * 2.0, color=C_GREEN, stroke_width=1.0),
            Text("Гибридный подход: проецирует", font_size=13, color=C_WHITE),
            Text("положительную часть в евклидово,", font_size=13, color=C_WHITE),
            Text("а отрицательную — в", font_size=13, color=C_WHITE),
            Text("гиперболическое пространство.", font_size=13, color=C_WHITE),
            MathTex(r"\mathbb{R}^p \,\oplus\, \mathbb{H}^q", font_size=18, color=C_YELLOW),
        ).arrange(DOWN, buff=0.20).move_to(m2_box.get_center())

        self.play(Write(m_title))
        self.play(Create(m1_box), Create(m2_box))
        self.play(Write(m1_content), Write(m2_content), run_time=1.8)
        self.wait(5.5)

        self.play(FadeOut(VGroup(m_title, m1_box, m1_content, m2_box, m2_content)))
        self.wait(0.2)

        # ── Bar chart (ARI on datasets) ───────────────────────────────────────
        chart_title = Text("Сравнение качества кластеризации (ARI) после сжатия", font_size=18, color=C_GRAY)
        chart_title.to_edge(UP, buff=1.2)

        datasets = ["Brain", "Breast", "Renal", "Leukemia", "Colorectal"]
        jl_pe_s  = [0.18, 0.05, 0.32, 0.11, 0.22]
        wf_s     = [0.68, 0.44, 1.00, 0.60, 0.99]
        tp_s     = [0.79, 0.28, 1.00, 0.78, 1.00]

        n, g_w, b_w, max_h = len(datasets), 1.55, 0.33, 2.3
        origin = np.array([-3.8, -1.8, 0])

        def make_bar(x_off, frac, color):
            h = max(frac * max_h, 0.04)
            r = Rectangle(width=b_w, height=h, fill_color=color, fill_opacity=0.85, stroke_width=0)
            r.move_to(origin + np.array([x_off, h / 2, 0]))
            return r

        bars_pe, bars_wf, bars_tp, xlabels = VGroup(), VGroup(), VGroup(), VGroup()
        for i, (ds, pe, wf, tp) in enumerate(zip(datasets, jl_pe_s, wf_s, tp_s)):
            cx = i * g_w + 0.7
            bars_pe.add(make_bar(cx - b_w * 1.1, pe, C_BLUE))
            bars_wf.add(make_bar(cx,              wf, C_GREEN))
            bars_tp.add(make_bar(cx + b_w * 1.1,  tp, C_ORANGE))
            lbl = Text(ds, font_size=12, color=C_GRAY).move_to(origin + np.array([cx, -0.22, 0]))
            xlabels.add(lbl)

        x_end = n * g_w + 0.5
        x_ax = Line(origin + LEFT * 0.1, origin + RIGHT * x_end, stroke_width=1.4, color=C_GRAY)
        y_ax = Line(origin + LEFT * 0.1, origin + UP * (max_h + 0.3), stroke_width=1.4, color=C_GRAY)

        ytick_grp = VGroup()
        for v, s in [(0.5, "0.5"), (1.0, "1.0")]:
            tk = Line(origin + np.array([-0.2, v * max_h, 0]), origin + np.array([0.0,  v * max_h, 0]),
                      stroke_width=1.0, color=C_GRAY)
            tl = Text(s, font_size=11, color=C_GRAY).next_to(tk, LEFT, buff=0.07)
            ytick_grp.add(tk, tl)

        ari_lbl = Text("ARI", font_size=13, color=C_GRAY).rotate(PI / 2)
        ari_lbl.next_to(y_ax, LEFT, buff=0.25)

        def leg_item(color, name):
            sq = Square(0.2, fill_color=color, fill_opacity=0.85, stroke_width=0)
            t  = Text(name, font_size=13, color=C_WHITE)
            return VGroup(sq, t).arrange(RIGHT, buff=0.15)

        legend = VGroup(
            leg_item(C_BLUE,   "JL-PE (наивный)"),
            leg_item(C_GREEN,  "MASS-WATERFILL"),
            leg_item(C_ORANGE, "TOPLAM-HYBRID"),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        legend.to_corner(UR, buff=0.9).shift(DOWN * 1.6)

        insight = Text(
            "Алгоритмы адаптивного проецирования существенно лучше базового JL-PE.",
            font_size=17, color=C_GREEN,
        ).to_edge(DOWN, buff=0.38)

        self.play(Write(chart_title))
        self.play(Create(x_ax), Create(y_ax), FadeIn(ytick_grp), Write(ari_lbl))
        self.play(Write(xlabels))
        self.play(
            LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars_pe],  lag_ratio=0.08),
            LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars_wf],  lag_ratio=0.08),
            LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars_tp],  lag_ratio=0.08),
            run_time=2.5,
        )
        self.play(FadeIn(legend))
        self.wait(2.0)
        self.play(Write(insight))
        self.wait(5.0)

        # ── Final closing card ────────────────────────────────────────────────
        chart_all = VGroup(
            chart_title, x_ax, y_ax, ytick_grp, ari_lbl,
            xlabels, bars_pe, bars_wf, bars_tp, legend, insight,
        )
        self.play(FadeOut(chart_all))
        self.wait(0.2)

        final_title = Text("Псевдоевклидова геометрия", font_size=40, color=C_BLUE, weight=BOLD)
        final_subtitle = Text("— не математическая экзотика", font_size=26, color=C_WHITE)
        final_line = Line(LEFT * 5, RIGHT * 5, color=C_GRAY, stroke_width=1)
        final_barrier = Text("Доказанный нижний барьер на сжатие:", font_size=20, color=C_GRAY)
        final_formula = MathTex(r"p' + q' \;=\; \Omega(\min(p,q))", font_size=30, color=C_YELLOW)
        final_desc = Text("Но адаптивные методы позволяют работать с ней эффективно.", font_size=20, color=C_GRAY)

        final = VGroup(
            final_title, final_subtitle, final_line, final_barrier, final_formula, final_desc
        ).arrange(DOWN, buff=0.30)

        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.18) for m in final], lag_ratio=0.25))
        self.wait(9.0)

        self.play(FadeOut(VGroup(header, final)))
        self.wait(0.5)
