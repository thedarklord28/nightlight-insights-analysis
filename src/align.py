"""
align.py
Makes sure two grids are the same shape/resolution before comparing them.
With the mock data they're already the same shape, but real satellite data
and real population data almost never come at the same resolution -- this
is where you'd fix that.
"""

import numpy as np
from scipy.ndimage import zoom


def align_grids(grid_a: np.ndarray, grid_b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Resizes grid_b to match grid_a's shape using simple interpolation.
    For real georeferenced satellite data, use rasterio's `reproject`
    instead (it accounts for actual geographic coordinates, not just
    pixel counts). This numpy/scipy version is enough for the mock data
    and for a quick prototype.
    """
    if grid_a.shape == grid_b.shape:
        return grid_a, grid_b

    scale_row = grid_a.shape[0] / grid_b.shape[0]
    scale_col = grid_a.shape[1] / grid_b.shape[1]
    grid_b_resized = zoom(grid_b, (scale_row, scale_col))

    # zoom can be off by a pixel due to rounding -- trim to match exactly
    grid_b_resized = grid_b_resized[: grid_a.shape[0], : grid_a.shape[1]]
    return grid_a, grid_b_resized


if __name__ == "__main__":
    # quick self-test
    a = np.random.rand(40, 40)
    b = np.random.rand(20, 20)
    a_aligned, b_aligned = align_grids(a, b)
    print(f"a: {a_aligned.shape}, b aligned to: {b_aligned.shape}")
