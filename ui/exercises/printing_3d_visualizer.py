
import math

import numpy as np
import plotly.graph_objects as go


class Printing3DVisualizer:
    CUBE_SIZE = 20.0
    DEFORMATION_SCALE = 5.0

    @staticmethod
    def _clamp(value):
        return max(0.0, min(1.0, value))

    def _create_layer_mesh(
        self, z_bottom, z_top, x_shift, warping
    ):
        half = self.CUBE_SIZE / 2.0

        xy = np.array([
            [-half, -half],
            [0, -half],
            [half, -half],
            [half, 0],
            [half, half],
            [0, half],
            [-half, half],
            [-half, 0],
            [0, 0],
        ], dtype=float)

        corner_weights = np.array([
            1, 0.25, 1, 0.25,
            1, 0.25, 1, 0.25, 0
        ])

        bottom = np.column_stack((
            xy[:, 0] + x_shift,
            xy[:, 1],
            z_bottom + warping * corner_weights,
        ))

        top = np.column_stack((
            xy[:, 0] + x_shift,
            xy[:, 1],
            z_top + warping * corner_weights,
        ))

        faces = []

        for j in range(8):
            nxt = (j + 1) % 8
            faces.extend((
                [8, nxt, j],
                [17, 9 + j, 9 + nxt],
                [j, nxt, 9 + nxt],
                [j, 9 + nxt, 9 + j],
            ))

        return (
            np.vstack((bottom, top)),
            np.asarray(faces, dtype=np.int32),
        )

    def create_figure(self, result):
        layer_count = result["layer_count"]
        layer_height = result["layer_height"]

        warping_mm = result["warping_mm"]
        shifting_mm = result["layer_shifting_mm"]

        vertices_list = []
        faces_list = []
        offset = 0

        shift_start = int(layer_count * 0.60)

        for index in range(layer_count):
            z_bottom = index * layer_height
            z_top = min(
                (index + 1) * layer_height,
                self.CUBE_SIZE,
            )

            progress = index / max(layer_count - 1, 1)

            warping = (
                warping_mm
                * ((1.0 - progress) ** 3)
                * self.DEFORMATION_SCALE
            )

            x_shift = (
                shifting_mm * self.DEFORMATION_SCALE
                if index >= shift_start
                else 0.0
            )

            vertices, faces = self._create_layer_mesh(
                z_bottom, z_top, x_shift, warping
            )

            vertices_list.append(vertices)
            faces_list.append(faces + offset)
            offset += len(vertices)

        vertices = np.concatenate(vertices_list)
        faces = np.concatenate(faces_list)

        fig = go.Figure()

        fig.add_trace(go.Mesh3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            i=faces[:, 0],
            j=faces[:, 1],
            k=faces[:, 2],
            color="#3B82F6",
            opacity=1.0,
            flatshading=False,
            lighting=dict(
                ambient=0.55,
                diffuse=0.8,
                specular=0.2,
                roughness=0.8,
            ),
            hoverinfo="skip",
            showscale=False,
        ))

        fig.add_trace(go.Surface(
            x=[[-13, 13], [-13, 13]],
            y=[[-13, -13], [13, 13]],
            z=[[0, 0], [0, 0]],
            colorscale=[
                [0, "#64748B"],
                [1, "#64748B"],
            ],
            opacity=0.20,
            showscale=False,
            hoverinfo="skip",
        ))

        fig.update_layout(
            title="3D-Drucksimulation",
            scene=dict(
                xaxis_title="X (mm)",
                yaxis_title="Y (mm)",
                zaxis_title="Z (mm)",
                aspectmode="data",
                camera=dict(
                    eye=dict(x=1.6, y=1.6, z=1.25)
                ),
            ),
            margin=dict(l=0, r=0, t=45, b=0),
            height=600,
            showlegend=False,
        )

        return fig
