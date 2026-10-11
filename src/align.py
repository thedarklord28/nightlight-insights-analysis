"""
align.py
Makes sure two grids are the same shape before comparing them.
(Real data from fetch_city.py already shares one grid; this is a safety net.)
"""

import numpy as np
from scipy.ndimage import zoom


def align_grids(grid_a: np.ndarray, grid_b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Resizes grid_b to match grid_a's shape using simple interpolation."""
    if grid_a.shape == grid_b.shape:
        return grid_a, grid_b

    scale_row = grid_a.shape[0] / grid_b.shape[0]
    scale_col = grid_a.shape[1] / grid_b.shape[1]
    grid_b_resized = zoom(grid_b, (scale_row, scale_col))
    grid_b_resized = grid_b_resized[: grid_a.shape[0], : grid_a.shape[1]]
    return grid_a, grid_b_resized
