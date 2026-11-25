"""Handcrafted regional feature extraction for superpixel-based trunk classification."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

import cv2
import numpy as np
from numpy.typing import NDArray
from skimage.feature import local_binary_pattern

from tree_cbir.models import RGBImage

from .superpixels import SuperpixelMap, boundary_mask

EPSILON = 1e-6


@dataclass(frozen=True)
class FeatureSpec:
    """Metadata descriptor for one handcrafted superpixel feature dimension."""

    index: int
    name: str
    group: str
    description: str


@dataclass(frozen=True)
class RegionFeatureMatrix:
    """Superpixel feature matrix computed strictly from an unseen RGB image."""

    features: NDArray[np.float64]
    region_ids: NDArray[np.int32]
    specs: tuple[FeatureSpec, ...]
    duration_seconds: float

    def __post_init__(self) -> None:
        if self.features.ndim != 2:
            raise ValueError("features must be a 2D matrix")
        if self.features.shape[0] != self.region_ids.shape[0]:
            raise ValueError("row count must match region_ids length")
        if self.features.shape[1] != len(self.specs):
            raise ValueError("column count must match feature specs length")
        if not np.isfinite(self.features).all():
            raise ValueError("all extracted region features must be finite")


def _build_specs() -> tuple[FeatureSpec, ...]:
    items: list[tuple[str, str, str]] = [
        # Group A: Color (46 dims)
        ("hsv_hue_cos_mean", "A_color", "Mean cos(2*pi*H/180) handling circular hue wraparound"),
        ("hsv_hue_sin_mean", "A_color", "Mean sin(2*pi*H/180) handling circular hue wraparound"),
        ("hsv_hue_circ_disp", "A_color", "Circular hue dispersion 1 - hypot(cos_mean, sin_mean)"),
        ("hsv_s_mean", "A_color", "Mean normalized HSV saturation [0, 1]"),
        ("hsv_s_std", "A_color", "Std of normalized HSV saturation"),
        ("hsv_s_q25", "A_color", "25th percentile of normalized HSV saturation"),
        ("hsv_s_q50", "A_color", "Median normalized HSV saturation"),
        ("hsv_s_q75", "A_color", "75th percentile of normalized HSV saturation"),
        ("hsv_v_mean", "A_color", "Mean normalized HSV value [0, 1]"),
        ("hsv_v_std", "A_color", "Std of normalized HSV value"),
        ("hsv_v_q25", "A_color", "25th percentile of normalized HSV value"),
        ("hsv_v_q50", "A_color", "Median normalized HSV value"),
        ("hsv_v_q75", "A_color", "75th percentile of normalized HSV value"),
        ("lab_l_mean", "A_color", "Mean normalized CIE Lab L* [0, 1]"),
        ("lab_l_std", "A_color", "Std of normalized CIE Lab L*"),
        ("lab_l_q25", "A_color", "25th percentile of normalized CIE Lab L*"),
        ("lab_l_q50", "A_color", "Median normalized CIE Lab L*"),
        ("lab_l_q75", "A_color", "75th percentile of normalized CIE Lab L*"),
        ("lab_a_mean", "A_color", "Mean centered CIE Lab a* (green<0, red>0)"),
        ("lab_a_std", "A_color", "Std of centered CIE Lab a*"),
        ("lab_a_q25", "A_color", "25th percentile of centered CIE Lab a*"),
        ("lab_a_q50", "A_color", "Median centered CIE Lab a*"),
        ("lab_a_q75", "A_color", "75th percentile of centered CIE Lab a*"),
        ("lab_b_mean", "A_color", "Mean centered CIE Lab b* (blue<0, yellow>0)"),
        ("lab_b_std", "A_color", "Std of centered CIE Lab b*"),
        ("lab_b_q25", "A_color", "25th percentile of centered CIE Lab b*"),
        ("lab_b_q50", "A_color", "Median centered CIE Lab b*"),
        ("lab_b_q75", "A_color", "75th percentile of centered CIE Lab b*"),
        ("lab_chroma_mean", "A_color", "Mean CIE Lab chroma hypot(a*, b*)"),
        ("excess_green_mean", "A_color", "Mean normalized excess green (2G - R - B)/(R + G + B)"),
    ]
    for b in range(8):
        items.append((f"hsv_hue_hist_{b}", "A_color", f"Normalized HSV circular hue bin {b}/8"))
    for b in range(4):
        items.append((f"hsv_v_hist_{b}", "A_color", f"Normalized HSV value histogram bin {b}/4"))
    for b in range(4):
        items.append(
            (f"hsv_s_hist_{b}", "A_color", f"Normalized HSV saturation histogram bin {b}/4")
        )
    # Group B: Texture (17 dims)
    for b in range(10):
        items.append(
            (f"lbp_u8_bin_{b}", "B_texture", f"Uniform LBP (P=8, R=1) normalized bin {b}/10")
        )
    items.extend(
        [
            ("gray_mean", "B_texture", "Mean normalized grayscale intensity [0, 1]"),
            ("gray_std", "B_texture", "Std of normalized grayscale intensity"),
            ("gray_var", "B_texture", "Variance of normalized grayscale intensity"),
            ("gray_iqr", "B_texture", "Interquartile range of normalized grayscale intensity"),
            ("local_contrast_mean", "B_texture", "Mean 3x3 morphological range local contrast"),
            ("local_contrast_std", "B_texture", "Std of 3x3 morphological range local contrast"),
            ("laplacian_abs_mean", "B_texture", "Mean absolute Laplacian texture response"),
            # Group C: Gradient and edge (12 dims)
            ("sobel_mag_mean", "C_gradient_edge", "Mean normalized Sobel gradient magnitude"),
            ("sobel_mag_std", "C_gradient_edge", "Std of normalized Sobel gradient magnitude"),
            (
                "sobel_mag_p90",
                "C_gradient_edge",
                "90th percentile of normalized Sobel gradient magnitude",
            ),
            (
                "grad_vertical_dominance",
                "C_gradient_edge",
                "Ratio mean(|gx|) / (mean(|gx|) + mean(|gy|) + eps)",
            ),
        ]
    )
    for b in range(6):
        items.append(
            (
                f"grad_ori_hist_{b}",
                "C_gradient_edge",
                f"Magnitude-weighted unsigned gradient orientation bin {b}/6",
            )
        )
    items.extend(
        [
            ("canny_edge_density", "C_gradient_edge", "Interior Canny edge density"),
            (
                "boundary_edge_support",
                "C_gradient_edge",
                "Fraction of region border pixels near dilated Canny edges",
            ),
            # Group D: Geometry (8 dims)
            ("rel_area", "D_geometry", "Superpixel pixel area relative to image area"),
            ("bbox_w_norm", "D_geometry", "Bounding-box width normalized by image width"),
            ("bbox_h_norm", "D_geometry", "Bounding-box height normalized by image height"),
            ("bbox_aspect_hw", "D_geometry", "Bounding-box height / max(1, width)"),
            ("bbox_extent", "D_geometry", "Region fill ratio area / (bbox_w * bbox_h)"),
            ("compactness", "D_geometry", "Isoperimetric quotient min(1, 4*pi*area / perimeter^2)"),
            ("centroid_x_norm", "D_geometry", "Normalized horizontal centroid [0, 1]"),
            ("centroid_y_norm", "D_geometry", "Normalized vertical centroid [0, 1]"),
            # Group E: Spatial context & structural continuity (13 dims)
            (
                "dist_from_center",
                "E_spatial_context",
                "Euclidean distance of normalized centroid from (0.5, 0.5)",
            ),
            (
                "abs_dx_from_center",
                "E_spatial_context",
                "Horizontal distance |centroid_x_norm - 0.5|",
            ),
            (
                "rel_y_top",
                "E_spatial_context",
                "Normalized top bounding-box coordinate y_min/(H-1)",
            ),
            (
                "rel_y_bottom",
                "E_spatial_context",
                "Normalized bottom bounding-box coordinate y_max/(H-1)",
            ),
            (
                "touches_bottom_border",
                "E_spatial_context",
                "Indicator 1.0 if region reaches image bottom border (y_max >= H-2)",
            ),
            (
                "nbr_lab_dist_mean",
                "E_spatial_context",
                "Mean CIE Lab Euclidean distance to adjacent superpixels",
            ),
            (
                "nbr_lab_dist_min",
                "E_spatial_context",
                "Minimum CIE Lab Euclidean distance to any adjacent superpixel",
            ),
            (
                "nbr_hsv_hue_diff_mean",
                "E_spatial_context",
                "Mean circular hue angular distance (radians/pi) to adjacent superpixels",
            ),
            (
                "nbr_vert_lab_dist_min",
                "E_spatial_context",
                "Minimum Lab distance to vertically aligned adjacent superpixels",
            ),
            (
                "nbr_horiz_lab_contrast_mean",
                "E_spatial_context",
                "Mean Lab distance to horizontally adjacent flank superpixels",
            ),
            (
                "nbr_vertical_continuity",
                "E_spatial_context",
                "Local structural continuity score with vertically aligned neighbors",
            ),
            (
                "region_vs_rowband_lab_dist",
                "E_spatial_context",
                "Lab distance from region mean to horizontal row-band mean across its y-span",
            ),
            (
                "region_vs_global_lab_dist",
                "E_spatial_context",
                "Lab distance from region mean to global image Lab mean",
            ),
        ]
    )
    return tuple(FeatureSpec(i, name, group, desc) for i, (name, group, desc) in enumerate(items))


FEATURE_SPECS: tuple[FeatureSpec, ...] = _build_specs()
FEATURE_DIMENSION = len(FEATURE_SPECS)


def _group_mean_std(
    flat_labels: NDArray[np.int32], values: NDArray[np.float64], areas: NDArray[np.float64]
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    n = areas.shape[0]
    sums = np.bincount(flat_labels, weights=values, minlength=n)
    mean = sums / areas
    sq_sums = np.bincount(flat_labels, weights=values * values, minlength=n)
    var = np.maximum(0.0, sq_sums / areas - mean * mean)
    return mean, np.sqrt(var)


def _group_quantiles(
    sorted_vals: NDArray[np.float64],
    starts: NDArray[np.int64],
    areas: NDArray[np.int64],
    probs: tuple[float, ...],
) -> list[NDArray[np.float64]]:
    n = areas.shape[0]
    outputs = [np.empty(n, dtype=np.float64) for _ in probs]
    for region_idx in range(n):
        s = int(starts[region_idx])
        c = int(areas[region_idx])
        if c == 1:
            val = float(sorted_vals[s])
            for out in outputs:
                out[region_idx] = val
            continue
        segment = np.sort(sorted_vals[s : s + c])
        last = c - 1
        for out, prob in zip(outputs, probs, strict=True):
            pos = prob * last
            lo = int(pos)
            hi = lo + 1 if lo < last else last
            frac = pos - lo
            out[region_idx] = float(segment[lo] * (1.0 - frac) + segment[hi] * frac)
    return outputs


def _adjacent_pairs(labels: NDArray[np.int32]) -> tuple[NDArray[np.int32], NDArray[np.int32]]:
    pairs_u: list[NDArray[np.int32]] = []
    pairs_v: list[NDArray[np.int32]] = []
    if labels.shape[1] > 1:
        lh = labels[:, :-1]
        rh = labels[:, 1:]
        mask_h = lh != rh
        if mask_h.any():
            pairs_u.append(lh[mask_h])
            pairs_v.append(rh[mask_h])
    if labels.shape[0] > 1:
        lv = labels[:-1, :]
        rv = labels[1:, :]
        mask_v = lv != rv
        if mask_v.any():
            pairs_u.append(lv[mask_v])
            pairs_v.append(rv[mask_v])
    if not pairs_u:
        empty = np.empty(0, dtype=np.int32)
        return empty, empty
    u = np.concatenate(pairs_u)
    v = np.concatenate(pairs_v)
    a = np.minimum(u, v)
    b = np.maximum(u, v)
    packed = a.astype(np.int64) * (int(labels.max()) + 1) + b.astype(np.int64)
    uniq = np.unique(packed)
    base = int(labels.max()) + 1
    return (uniq // base).astype(np.int32), (uniq % base).astype(np.int32)


def extract_region_features(rgb: RGBImage, superpixels: SuperpixelMap) -> RegionFeatureMatrix:
    """Extract 96 handcrafted regional features from RGB image + superpixels."""
    if rgb.ndim != 3 or rgb.shape[2] != 3 or rgb.dtype != np.uint8 or not rgb.size:
        raise ValueError("expected a nonempty RGB uint8 image")
    if rgb.shape[:2] != superpixels.labels.shape:
        raise ValueError("rgb dimensions must match superpixels.labels shape")

    started = perf_counter()
    height, width = rgb.shape[:2]
    labels = superpixels.labels
    flat_labels = labels.ravel()
    n_regions = superpixels.n_regions
    areas_int = superpixels.region_areas
    areas = areas_int.astype(np.float64)

    # Sort pixel indices once for fast quantile calculations across channels.
    order = np.argsort(flat_labels, kind="mergesort")
    starts = np.zeros(n_regions, dtype=np.int64)
    if n_regions > 1:
        starts[1:] = np.cumsum(areas_int[:-1])

    # Color space conversions (OpenCV RGB input, non-mutating)
    rgb_c = np.ascontiguousarray(rgb)
    hsv = cv2.cvtColor(rgb_c, cv2.COLOR_RGB2HSV)
    lab = cv2.cvtColor(rgb_c, cv2.COLOR_RGB2LAB).astype(np.float64)
    gray_u8 = cv2.cvtColor(rgb_c, cv2.COLOR_RGB2GRAY)

    h_raw = hsv[..., 0].ravel().astype(np.float64)
    s_norm = hsv[..., 1].ravel().astype(np.float64) / 255.0
    v_norm = hsv[..., 2].ravel().astype(np.float64) / 255.0

    theta = (2.0 * np.pi / 180.0) * h_raw
    cos_mean, _ = _group_mean_std(flat_labels, np.cos(theta), areas)
    sin_mean, _ = _group_mean_std(flat_labels, np.sin(theta), areas)
    hue_disp = np.clip(1.0 - np.hypot(cos_mean, sin_mean), 0.0, 1.0)

    s_mean, s_std = _group_mean_std(flat_labels, s_norm, areas)
    s_q25, s_q50, s_q75 = _group_quantiles(s_norm[order], starts, areas_int, (0.25, 0.50, 0.75))

    v_mean, v_std = _group_mean_std(flat_labels, v_norm, areas)
    v_q25, v_q50, v_q75 = _group_quantiles(v_norm[order], starts, areas_int, (0.25, 0.50, 0.75))

    lab_l = lab[..., 0].ravel() / 255.0
    lab_a = (lab[..., 1].ravel() - 128.0) / 127.0
    lab_b = (lab[..., 2].ravel() - 128.0) / 127.0

    l_mean, l_std = _group_mean_std(flat_labels, lab_l, areas)
    l_q25, l_q50, l_q75 = _group_quantiles(lab_l[order], starts, areas_int, (0.25, 0.50, 0.75))

    a_mean, a_std = _group_mean_std(flat_labels, lab_a, areas)
    a_q25, a_q50, a_q75 = _group_quantiles(lab_a[order], starts, areas_int, (0.25, 0.50, 0.75))

    b_mean, b_std = _group_mean_std(flat_labels, lab_b, areas)
    b_q25, b_q50, b_q75 = _group_quantiles(lab_b[order], starts, areas_int, (0.25, 0.50, 0.75))

    chroma = np.hypot(lab_a, lab_b)
    chroma_mean, _ = _group_mean_std(flat_labels, chroma, areas)

    rgb_f = rgb_c.astype(np.float64)
    r_ch, g_ch, b_ch = rgb_f[..., 0].ravel(), rgb_f[..., 1].ravel(), rgb_f[..., 2].ravel()
    exg = (2.0 * g_ch - r_ch - b_ch) / (r_ch + g_ch + b_ch + 1.0)
    exg_mean, _ = _group_mean_std(flat_labels, exg, areas)

    # Normalized histograms via vectorized 2D bincount
    h_bins = np.clip((h_raw * 8.0 / 180.0).astype(np.int64), 0, 7)
    h_hist = (
        np.bincount(flat_labels * 8 + h_bins, minlength=n_regions * 8)
        .reshape(n_regions, 8)
        .astype(np.float64)
        / areas[:, None]
    )

    v_bins = np.clip((v_norm * 4.0).astype(np.int64), 0, 3)
    v_hist = (
        np.bincount(flat_labels * 4 + v_bins, minlength=n_regions * 4)
        .reshape(n_regions, 4)
        .astype(np.float64)
        / areas[:, None]
    )

    s_bins = np.clip((s_norm * 4.0).astype(np.int64), 0, 3)
    s_hist = (
        np.bincount(flat_labels * 4 + s_bins, minlength=n_regions * 4)
        .reshape(n_regions, 4)
        .astype(np.float64)
        / areas[:, None]
    )

    # Group B: Texture
    lbp = local_binary_pattern(gray_u8, P=8, R=1, method="uniform").astype(np.int64).ravel()
    lbp = np.clip(lbp, 0, 9)
    lbp_hist = (
        np.bincount(flat_labels * 10 + lbp, minlength=n_regions * 10)
        .reshape(n_regions, 10)
        .astype(np.float64)
        / areas[:, None]
    )

    gray_f = gray_u8.astype(np.float64) / 255.0
    gray_flat = gray_f.ravel()
    gray_mean, gray_std = _group_mean_std(flat_labels, gray_flat, areas)
    gray_var = gray_std * gray_std
    g_q25, g_q75 = _group_quantiles(gray_flat[order], starts, areas_int, (0.25, 0.75))
    gray_iqr = g_q75 - g_q25

    kernel3 = np.ones((3, 3), dtype=np.uint8)
    morph_range = (cv2.dilate(gray_u8, kernel3) - cv2.erode(gray_u8, kernel3)).ravel().astype(
        np.float64
    ) / 255.0
    lc_mean, lc_std = _group_mean_std(flat_labels, morph_range, areas)

    lap = (
        np.abs(cv2.Laplacian(gray_f.astype(np.float32), cv2.CV_32F, ksize=3))
        .ravel()
        .astype(np.float64)
    )
    lap_mean, _ = _group_mean_std(flat_labels, lap, areas)

    # Group C: Gradient and edge
    gx = cv2.Sobel(gray_f.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3).ravel().astype(np.float64)
    gy = cv2.Sobel(gray_f.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3).ravel().astype(np.float64)
    grad_mag = np.hypot(gx, gy)
    sobel_mean, sobel_std = _group_mean_std(flat_labels, grad_mag, areas)
    (sobel_p90,) = _group_quantiles(grad_mag[order], starts, areas_int, (0.90,))

    gx_abs_mean, _ = _group_mean_std(flat_labels, np.abs(gx), areas)
    gy_abs_mean, _ = _group_mean_std(flat_labels, np.abs(gy), areas)
    grad_vert_dom = gx_abs_mean / (gx_abs_mean + gy_abs_mean + EPSILON)

    ori = np.mod(np.arctan2(gy, gx), np.pi)
    ori_bins = np.clip((ori * 6.0 / np.pi).astype(np.int64), 0, 5)
    ori_weighted = (
        np.bincount(flat_labels * 6 + ori_bins, weights=grad_mag, minlength=n_regions * 6)
        .reshape(n_regions, 6)
        .astype(np.float64)
    )
    ori_sum = ori_weighted.sum(axis=1, keepdims=True)
    ori_hist = np.divide(
        ori_weighted,
        ori_sum,
        out=np.zeros_like(ori_weighted),
        where=ori_sum > EPSILON,
    )

    canny_edges = cv2.Canny(gray_u8, 50, 150) > 0
    canny_density = (
        np.bincount(
            flat_labels, weights=canny_edges.ravel().astype(np.float64), minlength=n_regions
        )
        / areas
    )

    dilated_canny = cv2.dilate(canny_edges.astype(np.uint8), kernel3) > 0
    region_borders = boundary_mask(labels)
    border_counts = np.bincount(flat_labels[region_borders.ravel()], minlength=n_regions).astype(
        np.float64
    )
    border_edge_hits = np.bincount(
        flat_labels[(region_borders & dilated_canny).ravel()], minlength=n_regions
    ).astype(np.float64)
    boundary_edge_support = np.divide(
        border_edge_hits,
        border_counts,
        out=np.zeros(n_regions, dtype=np.float64),
        where=border_counts > 0,
    )

    # Group D: Geometry
    ys_grid, xs_grid = np.indices((height, width))
    flat_y = ys_grid.ravel()
    flat_x = xs_grid.ravel()
    y_sorted = flat_y[order]
    x_sorted = flat_x[order]

    y_min = np.empty(n_regions, dtype=np.float64)
    y_max = np.empty(n_regions, dtype=np.float64)
    x_min = np.empty(n_regions, dtype=np.float64)
    x_max = np.empty(n_regions, dtype=np.float64)
    for k in range(n_regions):
        s = int(starts[k])
        e = s + int(areas_int[k])
        ys_k = y_sorted[s:e]
        xs_k = x_sorted[s:e]
        y_min[k] = float(ys_k[0])
        y_max[k] = float(ys_k[-1])
        x_min[k] = float(xs_k.min())
        x_max[k] = float(xs_k.max())

    bbox_w = x_max - x_min + 1.0
    bbox_h = y_max - y_min + 1.0
    rel_area = areas / float(height * width)
    bbox_w_norm = bbox_w / float(width)
    bbox_h_norm = bbox_h / float(height)
    bbox_aspect_hw = bbox_h / np.maximum(1.0, bbox_w)
    bbox_extent = areas / np.maximum(1.0, bbox_w * bbox_h)

    # Exact pixel-boundary perimeter (outer edge count, always >= 4)
    perim = np.zeros(n_regions, dtype=np.float64)
    perim += np.bincount(labels[0, :], minlength=n_regions)
    perim += np.bincount(labels[-1, :], minlength=n_regions)
    perim += np.bincount(labels[:, 0], minlength=n_regions)
    perim += np.bincount(labels[:, -1], minlength=n_regions)
    if height > 1:
        mv = labels[:-1, :] != labels[1:, :]
        perim += np.bincount(labels[:-1, :][mv], minlength=n_regions)
        perim += np.bincount(labels[1:, :][mv], minlength=n_regions)
    if width > 1:
        mh = labels[:, :-1] != labels[:, 1:]
        perim += np.bincount(labels[:, :-1][mh], minlength=n_regions)
        perim += np.bincount(labels[:, 1:][mh], minlength=n_regions)
    compactness = np.minimum(1.0, 4.0 * np.pi * areas / np.maximum(1.0, perim * perim))

    cx_px = np.bincount(flat_labels, weights=flat_x.astype(np.float64), minlength=n_regions) / areas
    cy_px = np.bincount(flat_labels, weights=flat_y.astype(np.float64), minlength=n_regions) / areas
    cx_norm = cx_px / max(1.0, float(width - 1))
    cy_norm = cy_px / max(1.0, float(height - 1))

    # Group E: Spatial context & structural continuity
    dist_center = np.hypot(cx_norm - 0.5, cy_norm - 0.5)
    abs_dx_center = np.abs(cx_norm - 0.5)
    rel_y_top = y_min / max(1.0, float(height - 1))
    rel_y_bottom = y_max / max(1.0, float(height - 1))
    touches_bottom = (y_max >= height - 2).astype(np.float64)

    u_pairs, v_pairs = _adjacent_pairs(labels)
    nbr_lab_mean = np.zeros(n_regions, dtype=np.float64)
    nbr_lab_min = np.zeros(n_regions, dtype=np.float64)
    nbr_hue_mean = np.zeros(n_regions, dtype=np.float64)
    nbr_vert_min = np.zeros(n_regions, dtype=np.float64)
    nbr_horiz_mean = np.zeros(n_regions, dtype=np.float64)
    nbr_vert_cont = np.zeros(n_regions, dtype=np.float64)

    if len(u_pairs):
        edge_a = np.concatenate([u_pairs, v_pairs])
        edge_b = np.concatenate([v_pairs, u_pairs])
        d_lab = np.sqrt(
            (l_mean[edge_a] - l_mean[edge_b]) ** 2
            + (a_mean[edge_a] - a_mean[edge_b]) ** 2
            + (b_mean[edge_a] - b_mean[edge_b]) ** 2
        )
        dot_hue = np.clip(
            cos_mean[edge_a] * cos_mean[edge_b] + sin_mean[edge_a] * sin_mean[edge_b],
            -1.0,
            1.0,
        )
        d_hue = np.arccos(dot_hue) / np.pi

        deg = np.bincount(edge_a, minlength=n_regions).astype(np.float64)
        nbr_lab_sum = np.bincount(edge_a, weights=d_lab, minlength=n_regions)
        nbr_hue_sum = np.bincount(edge_a, weights=d_hue, minlength=n_regions)
        has_nbr = deg > 0
        nbr_lab_mean[has_nbr] = nbr_lab_sum[has_nbr] / deg[has_nbr]
        nbr_hue_mean[has_nbr] = nbr_hue_sum[has_nbr] / deg[has_nbr]

        nbr_lab_min.fill(np.inf)
        np.minimum.at(nbr_lab_min, edge_a, d_lab)
        nbr_lab_min[~has_nbr] = 0.0

        dx_edge = np.abs(cx_px[edge_a] - cx_px[edge_b])
        dy_edge = np.abs(cy_px[edge_a] - cy_px[edge_b])
        is_vert = dy_edge > dx_edge
        is_horiz = ~is_vert

        nbr_vert_min[:] = nbr_lab_min
        if is_vert.any():
            vert_min = np.full(n_regions, np.inf, dtype=np.float64)
            np.minimum.at(vert_min, edge_a[is_vert], d_lab[is_vert])
            has_vert = np.isfinite(vert_min)
            nbr_vert_min[has_vert] = vert_min[has_vert]

            w_ratio = np.minimum(bbox_w[edge_a[is_vert]], bbox_w[edge_b[is_vert]]) / np.maximum(
                bbox_w[edge_a[is_vert]], bbox_w[edge_b[is_vert]]
            )
            cont = np.exp(-4.0 * d_lab[is_vert]) * w_ratio
            np.maximum.at(nbr_vert_cont, edge_a[is_vert], cont)

        nbr_horiz_mean[:] = nbr_lab_mean
        if is_horiz.any():
            h_deg = np.bincount(edge_a[is_horiz], minlength=n_regions).astype(np.float64)
            h_sum = np.bincount(edge_a[is_horiz], weights=d_lab[is_horiz], minlength=n_regions)
            has_h = h_deg > 0
            nbr_horiz_mean[has_h] = h_sum[has_h] / h_deg[has_h]

    # Row-band Lab contrast and global Lab contrast
    lab_l_2d = lab[..., 0] / 255.0
    lab_a_2d = (lab[..., 1] - 128.0) / 127.0
    lab_b_2d = (lab[..., 2] - 128.0) / 127.0
    row_l = lab_l_2d.mean(axis=1)
    row_a = lab_a_2d.mean(axis=1)
    row_b = lab_b_2d.mean(axis=1)
    pref_l = np.concatenate([[0.0], np.cumsum(row_l)])
    pref_a = np.concatenate([[0.0], np.cumsum(row_a)])
    pref_b = np.concatenate([[0.0], np.cumsum(row_b)])
    yi0 = y_min.astype(np.int64)
    yi1 = y_max.astype(np.int64) + 1
    span = np.maximum(1, yi1 - yi0).astype(np.float64)
    band_l = (pref_l[yi1] - pref_l[yi0]) / span
    band_a = (pref_a[yi1] - pref_a[yi0]) / span
    band_b = (pref_b[yi1] - pref_b[yi0]) / span
    vs_rowband = np.sqrt((l_mean - band_l) ** 2 + (a_mean - band_a) ** 2 + (b_mean - band_b) ** 2)

    glob_l = float(row_l.mean())
    glob_a = float(row_a.mean())
    glob_b = float(row_b.mean())
    vs_global = np.sqrt((l_mean - glob_l) ** 2 + (a_mean - glob_a) ** 2 + (b_mean - glob_b) ** 2)

    columns = [
        cos_mean[:, None],
        sin_mean[:, None],
        hue_disp[:, None],
        s_mean[:, None],
        s_std[:, None],
        s_q25[:, None],
        s_q50[:, None],
        s_q75[:, None],
        v_mean[:, None],
        v_std[:, None],
        v_q25[:, None],
        v_q50[:, None],
        v_q75[:, None],
        l_mean[:, None],
        l_std[:, None],
        l_q25[:, None],
        l_q50[:, None],
        l_q75[:, None],
        a_mean[:, None],
        a_std[:, None],
        a_q25[:, None],
        a_q50[:, None],
        a_q75[:, None],
        b_mean[:, None],
        b_std[:, None],
        b_q25[:, None],
        b_q50[:, None],
        b_q75[:, None],
        chroma_mean[:, None],
        exg_mean[:, None],
        h_hist,
        v_hist,
        s_hist,
        lbp_hist,
        gray_mean[:, None],
        gray_std[:, None],
        gray_var[:, None],
        gray_iqr[:, None],
        lc_mean[:, None],
        lc_std[:, None],
        lap_mean[:, None],
        sobel_mean[:, None],
        sobel_std[:, None],
        sobel_p90[:, None],
        grad_vert_dom[:, None],
        ori_hist,
        canny_density[:, None],
        boundary_edge_support[:, None],
        rel_area[:, None],
        bbox_w_norm[:, None],
        bbox_h_norm[:, None],
        bbox_aspect_hw[:, None],
        bbox_extent[:, None],
        compactness[:, None],
        cx_norm[:, None],
        cy_norm[:, None],
        dist_center[:, None],
        abs_dx_center[:, None],
        rel_y_top[:, None],
        rel_y_bottom[:, None],
        touches_bottom[:, None],
        nbr_lab_mean[:, None],
        nbr_lab_min[:, None],
        nbr_hue_mean[:, None],
        nbr_vert_min[:, None],
        nbr_horiz_mean[:, None],
        nbr_vert_cont[:, None],
        vs_rowband[:, None],
        vs_global[:, None],
    ]
    matrix = np.hstack(columns).astype(np.float64, copy=False)
    duration = perf_counter() - started
    return RegionFeatureMatrix(
        features=matrix,
        region_ids=superpixels.region_ids,
        specs=FEATURE_SPECS,
        duration_seconds=duration,
    )
