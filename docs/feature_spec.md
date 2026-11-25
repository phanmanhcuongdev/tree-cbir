# Canonical tree-image feature specification

**Contract** · X0–X37 in the order below, grouped as trunk (9), leaves and canopy (8), branches (3), roots (6), and context (12). Values are **raw** unless stated otherwise. Min–Max, validity persistence and group ranking are defined in [requirements](requirements.md). Semantic labels, confidence, and helper measurements are separate outputs. This specification defines intended behavior for future implementation. The [decision register](team_preparation/specification_decisions.md) identifies project conventions and open parameters.

**Provenance** · Report 1 Part 2 §2.1–§2.5 gives the feature meanings, §3 the normalization and comparison design, and §4 their information value and evaluation. Native Google Docs text was read through Drive. For equations and numerical bounds omitted from native text, the supplied definitions and the local Report 1 Markdown export were used to cross-check notation. Project conventions are identified below and in the register.

## Common measurement contract

- Use standardized RGB `uint8` with shape `(H,W,3)`. `I` denotes the image domain and masks/ROI are boolean subsets of `I`. Coordinates are pixel centers numbered from zero, with `x` right, `y` down, array access `[y,x]`. `A(M)` counts true pixels and `D = hypot(W,H)` px (1280 at 768 × 1024). Feature functions consume masks, ROI and metadata with upstream validity. They do not read annotations or repair segmentation.
- Distinguish a measured region, confirmed absence in a trustworthy search region, and an unknown/unreliable measurement. Mark malformed masks, inconsistent containment, unavailable inputs, unreliable regions and undefined denominators invalid for dependent features. For confirmed absence, X0/X9/X17/X20 may be valid zero subject to their prerequisites. Geometry and color of an absent object are invalid, except a zero count measured on an actual valid skeleton/region. Confirmed absence of a visible structure refers to the image, regardless of whether the biological structure exists out of view.
- Use double precision for calculations and mark invalid dimensions in the validity vector with diagnostics. Preserve genuine zero for a computed observation. Missing metadata or unapproved required settings cause the relevant measure to be invalid/unavailable, with a reason. Shared decisions A04–A20 specify deterministic proposed conventions and parameters that must be supplied by a versioned configuration or upstream input.
- Let `M_trunk`, `M_canopy`, `M_branch`, and `M_root` be visible component masks. The foliage mask is `M_canopy`. Branches and foliage use the same reliable `ROI_canopy`. Pass the estimated trunk height, measured representative trunk width and base location as separate inputs with provenance. Width denominators use the unnormalized pixel measurement. Invalidate a dependent measurement when clipping compromises its required geometry. A border touch prompts a clipping check.
- For reported horizontal coordinate spans use rightmost minus leftmost pixel center, with no added pixel (X4, X21). Use inclusive pixel extents for measured mask heights and the canopy box width. A one-row mask has height 1. For X4–X6 use one sample per supported nonempty trunk row. For X7 use supported rows in its specified band, with no fabricated samples for unknown/occluded rows. The lower band is derived from a trustworthy trunk base/extent. See A04–A05.
- Canopy HSV uses `H_deg = 2 × H_cv8` in `[0,360)` degrees, `S = S_cv8/255` and `V = V_cv8/255`. Use the arithmetic means from Report 1. OpenCV encodes achromatic hue as zero, and X10 is invalid for an entirely achromatic mask. Low chroma and wrap-around diagnostics may be recorded separately. Bark Lab below is a proposal requiring approval. See A02–A03.
- `Sk(M)`, `L(Sk)` and `J(Sk)` use the same configured skeleton method and graph conventions for trunk, branches and roots. When testing feature math independently, supply the indicated graph or mask fixture. See A07–A08. Small dimensions such as `W=10` are mathematical unit fixtures.
- Context uses `M_ground = ROI_lower \\ (M_tree ∪ M_root)` and `M_back = I \\ (M_tree ∪ M_root ∪ M_ground)`. The explicit root exclusion in the second formula is the project correction. A reliable `M_tree` must cover the visible above-ground tree, and a failed root search cannot assert empty roots. Use a reliable assessment that no visible roots are present, or a trustworthy root exclusion mask. Color predicates `C_green`, `C_brown`, `C_gray`, `C_blue`, and `C_white` are versioned. Let `G(p)` be the fixed uint8 RGB-to-gray conversion, `E` the bool edge map from the unmasked image, and `L_lines(M)` the length of line support within region `M`. See A15–A20.

## Trunk (X0–X8)

### X0 — Observed trunk-height ratio

- **Source and formula** · Report 1 §2.1.2 (1). `H_mask / H_expected`.
- **Inputs, range and unit** · Reliable visible trunk mask span and positive finite expected height, both in px. A confirmed absence has H_mask = 0 if the search and estimate are reliable. [0,∞), ratio.
- **Validity and edge cases** · Keep values above 1 and record the unexpectedly small estimate. Unknown trunk or missing/invalid estimate is invalid.
- **Calibration or convention** · A01, A04, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · 30 px / 50 px = 0.6. An unknown empty mask is invalid. A confirmed empty mask with the same estimate is zero.
- **Information value** · Matches the degree of trunk visibility and occlusion.

### X1 — Bark lightness

- **Source and formula** · Report 1 §2.1.2 (2). `median over M_trunk of Lab L* (proposed)`.
- **Inputs, range and unit** · RGB and a reliable nonempty trunk mask, using the proposed Lab transform in A02. [0,100], CIELAB L*.
- **Validity and edge cases** · Neutral bark still has valid lightness. Empty or contaminated measurements are invalid.
- **Calibration or convention** · A02, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · L* samples [20,40,80] → 40.
- **Information value** · Separates dark and pale bark, with sensitivity to illumination.

### X2 — Bark red–green chromaticity

- **Source and formula** · Report 1 §2.1.2 (2). `median over M_trunk of Lab a* (proposed)`.
- **Inputs, range and unit** · RGB and a reliable nonempty trunk mask under the same conversion as X1. Signed CIELAB a* units, nominal sRGB envelope within [−128,127].
- **Validity and edge cases** · Zero is valid for neutral chromaticity. Empty or unreliable masks are invalid.
- **Calibration or convention** · A02, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · a* samples [−5,0,8] → 0, valid.
- **Information value** · Adds evidence for reddish versus greener bark tones.

### X3 — Bark yellow–blue chromaticity

- **Source and formula** · Report 1 §2.1.2 (2). `median over M_trunk of Lab b* (proposed)`.
- **Inputs, range and unit** · RGB and a reliable nonempty trunk mask under the same conversion as X1. Signed CIELAB b* units, nominal sRGB envelope within [−128,127].
- **Validity and edge cases** · Zero is valid for neutral chromaticity. Empty or unreliable masks are invalid.
- **Calibration or convention** · A02, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · b* samples [−3,5,11] → 5.
- **Information value** · Distinguishes warmer and cooler bark tones independently of lightness.

### X4 — Relative trunk width

- **Source and formula** · Report 1 §2.1.2 (3). `W_trunk/W, where W_trunk = median_y (x_right(y) − x_left(y))`.
- **Inputs, range and unit** · Reliable trunk mask, supported nonempty rows and positive image width. [0,(W−1)/W], ratio.
- **Validity and edge cases** · Use outermost coordinates even across separate runs. A reliable one-column slice has zero coordinate span. A zero representative span cannot serve as a denominator for X22 or define ROI_root.
- **Calibration or convention** · A04–A05, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · With W = 10 and row spans [2,4,8], X4 = 0.4.
- **Information value** · Distinguishes slender and thick visible trunks at comparable framing.

### X5 — Absolute trunk inclination

- **Source and formula** · Report 1 §2.1.2 (4). `abs(atan(a)) × 180/π for OLS x = ay + b`.
- **Inputs, range and unit** · Distinct supported rows, with x_c = (x_left + x_right)/2, and sufficient reliable centerline coverage. [0,90), degrees.
- **Validity and edge cases** · At least two distinct rows. A vertical centerline is 0°, and mirror images share the angle. A degenerate or unreliable fit is invalid.
- **Calibration or convention** · A05, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · Centers (x,y) = (2,0),(3,1),(4,2) → 45°.
- **Information value** · Distinguishes upright and tilted trunks of similar size.

### X6 — Relative trunk curvature

- **Source and formula** · Report 1 §2.1.2 (4). `sqrt(mean_y((x_c(y) − (a y + b))²)) / H_mask`.
- **Inputs, range and unit** · Reliable centerline and positive measured trunk height. Use the same OLS fit as X5, with at least three distinct supported rows for X6. [0,∞), ratio.
- **Validity and edge cases** · Two points exactly define a line and provide no curvature evidence. A well-supported straight line has valid zero curvature.
- **Calibration or convention** · A04–A06, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · At y = [0,1,2], x_c = [0,3,0], H_mask = 3 yields sqrt(2)/3.
- **Information value** · Separates bending from straight-line inclination.

### X7 — Median lower trunk run count

- **Source and formula** · Report 1 §2.1.2 (5). `median_y count of maximal contiguous foreground x-runs for 0.15 ≤ (y_base−y)/H_mask ≤ 0.60`.
- **Inputs, range and unit** · Reliable trunk base and height with at least one supported nonempty row in the closed band. y_base is the bottom of the measured trunk extent used for this band. [1,∞), runs, including half-integers for even samples under this convention.
- **Validity and edge cases** · No usable rows is invalid. Unknown empty rows are excluded. Preserve the median without rounding.
- **Calibration or convention** · A04–A05, A18, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · Two eligible rows with 1 and 2 runs give 1.5, regardless of rows outside the band.
- **Information value** · Distinguishes a solid bole from multiple visible stems near the base.

### X8 — Lower trunk junction count

- **Source and formula** · Report 1 §2.1.2 (5). `J(Sk(M_trunk)) restricted to junctions whose representative has y ≥ (y_top+y_base)/2`.
- **Inputs, range and unit** · Reliable lower trunk extent and a valid whole-trunk skeleton graph. Nonnegative integer, junctions.
- **Validity and edge cases** · Build graph before selecting the lower half, to avoid boundary effects. Merge adjacent junction pixels. A measured simple stem yields 0.
- **Calibration or convention** · A04, A07–A08, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · Two distinct lower junction clusters and one upper cluster → 2.
- **Information value** · Adds evidence of branching from the base independently of run count.

## Leaves and canopy (X9–X16)

### X9 — Foliage visibility ratio

- **Source and formula** · Report 1 §2.2.2. `A(M_canopy)/A(ROI_canopy)`.
- **Inputs, range and unit** · Reliable nonempty canopy ROI and reliable foliage mask contained by it, or confirmed no visible foliage. [0,1], ratio.
- **Validity and edge cases** · Confirmed leafless ROI gives 0. An occluded/unknown ROI or out-of-ROI mask invalidates the result.
- **Calibration or convention** · A10, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · 20 foliage pixels in a 100 px² ROI → 0.2.
- **Information value** · Separates leafless and leafy appearances under comparable observation.

### X10 — Mean foliage hue

- **Source and formula** · Report 1 §2.2.3. `mean of H_deg over M_canopy`.
- **Inputs, range and unit** · RGB and reliable nonempty foliage mask with measurable chromatic evidence. [0,360), degrees.
- **Validity and edge cases** · Use arithmetic mean, including converter values for achromatic pixels in a mixed mask. Entirely achromatic mask is invalid for hue only. A wrap-around mixture may give an unrepresentative mean, recorded as a diagnostic.
- **Calibration or convention** · A03, A15, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · OpenCV H values [30,60] → [60°,120°] → 90°. [358°,2°] → 180° under arithmetic mean.
- **Information value** · Distinguishes green and seasonally colored foliage, with a wrap-around limitation.

### X11 — Mean foliage saturation

- **Source and formula** · Report 1 §2.2.3. `mean of S over M_canopy`.
- **Inputs, range and unit** · RGB and reliable nonempty foliage mask. [0,1], ratio.
- **Validity and edge cases** · Achromatic foliage can have valid zero. An empty mask is invalid.
- **Calibration or convention** · A03, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · OpenCV S samples [0,255] → 0.5.
- **Information value** · Distinguishes vivid foliage from muted foliage.

### X12 — Mean foliage value

- **Source and formula** · Report 1 §2.2.3. `mean of V over M_canopy`.
- **Inputs, range and unit** · RGB and reliable nonempty foliage mask. [0,1], ratio.
- **Validity and edge cases** · A measured very dark value can be zero. An empty mask is invalid. Report lighting sensitivity.
- **Calibration or convention** · A03, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · OpenCV V samples [0,255] → 0.5.
- **Information value** · Describes canopy brightness and supports color interpretation.

### X13 — Canopy solidity

- **Source and formula** · Report 1 §2.2.4. `A(M_canopy)/A(Hull_mask(M_canopy))`.
- **Inputs, range and unit** · Reliable nonempty canopy mask and its filled, aligned convex-hull mask, using the same raster area convention. (0,1], ratio.
- **Validity and edge cases** · Hull must contain the mask. Holes/disconnected foliage stay excluded from the numerator. Insufficient mask support is invalid.
- **Calibration or convention** · A09–A10, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · 8 foreground pixels with 10 in the hull → 0.8. A filled rectangular mask gives 1.
- **Information value** · Distinguishes tightly filled silhouettes from sparse or indented ones.

### X14 — Canopy aspect ratio

- **Source and formula** · Report 1 §2.2.5. `H_canopy/W_canopy`.
- **Inputs, range and unit** · Reliable nonempty canopy mask, with inclusive bounding-box extents H_canopy and W_canopy. (0,∞), ratio.
- **Validity and edge cases** · Missing, clipped or insufficient canopy geometry is invalid. Use all retained components.
- **Calibration or convention** · A04, A09–A10, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · An 8-row × 4-column bounding box gives 2.
- **Information value** · Separates tall and narrow canopies from wide-spreading shapes.

### X15 — Canopy circularity

- **Source and formula** · Report 1 §2.2.5. `4π A_contour/P_contour²`.
- **Inputs, range and unit** · Reliable nondegenerate canopy contours, using polygon net area and the matching Euclidean boundary length in A09. (0,1] for valid geometry, ratio.
- **Validity and edge cases** · Include all retained components and hole boundaries. Zero-area, zero-perimeter or inconsistent geometry is invalid. Do not mix pixel-count area with centerline polygon perimeter.
- **Calibration or convention** · A09–A10, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · A square contour with side 10 px gives π/4. A degenerate line contour is invalid.
- **Information value** · Distinguishes compact rounded shapes from elongated or irregular shapes.

### X16 — Vertical position of maximum canopy width

- **Source and formula** · Report 1 §2.2.5. `(y_max_width − y_top)/H_canopy`.
- **Inputs, range and unit** · Reliable canopy mask. Find the widest nonempty row by outer span and resolve ties with the uppermost row. [0,(H_canopy−1)/H_canopy], ratio.
- **Validity and edge cases** · The box height is inclusive and y increases downward, so higher raw values mean the widest part is lower. A tied row choice is deterministic.
- **Calibration or convention** · A04, A09–A10, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · For y_top = 10, H_canopy = 8, tied widest rows 14 and 15 → 0.5.
- **Information value** · Distinguishes canopies with top-heavy or bottom-heavy silhouettes.

## Branches (X17–X19)

### X17 — Visible branch-area ratio

- **Source and formula** · Report 1 §2.3.2. `A(M_branch)/A(ROI_canopy)`.
- **Inputs, range and unit** · Reliable nonempty canopy ROI and a reliable contained visible branch mask or confirmed absence of exposed branches. [0,1], ratio.
- **Validity and edge cases** · A confirmed lack of exposed branches gives 0. An unreliable observation is invalid even if its mask is empty.
- **Calibration or convention** · A10–A11, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · 15 branch pixels in a 100 px² ROI → 0.15.
- **Information value** · Describes how much exposed wood is visible within the canopy search region.

### X18 — Relative branch skeleton length

- **Source and formula** · Report 1 §2.3.3. `L(Sk(M_branch))/D`.
- **Inputs, range and unit** · Reliable nonempty branch mask, a valid skeleton and positive image diagonal. [0,∞), ratio.
- **Validity and edge cases** · A reliable singleton skeleton has zero link length if it meets quality criteria. An unavailable skeleton is invalid. Total length across limbs can exceed the image diagonal.
- **Calibration or convention** · A07, A10–A11, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · A four-point straight skeleton has three unit links, so X18 = 3/1280 at standard size.
- **Information value** · Distinguishes short exposed fragments from an extensive visible branch network.

### X19 — Branch skeleton junction count

- **Source and formula** · Report 1 §2.3.3. `J(Sk(M_branch))`.
- **Inputs, range and unit** · Reliable visible branch skeleton with support for topology. Nonnegative integer, junctions.
- **Validity and edge cases** · A verified exposed unbranched segment gives a distinct valid zero. Unknown or absent topology is invalid.
- **Calibration or convention** · A07–A08, A11, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · A simple line gives 0. Three arms meeting in one junction cluster give 1.
- **Information value** · Separates simple exposed wood from ramified branch structures.

## Roots (X20–X25)

### X20 — Exposed root-area ratio

- **Source and formula** · Report 1 §2.4.2. `A(M_root)/A(ROI_root)`.
- **Inputs, range and unit** · Reliable trunk base and positive representative trunk width for a nonempty root ROI, and a reliable contained mask or confirmed absence of exposed roots. [0,1], ratio.
- **Validity and edge cases** · A reliably inspected ROI with no exposed root gives 0. Unknown base, invalid width, unreliable ROI or failed segmentation yields invalid.
- **Calibration or convention** · A12, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · 12 root pixels in an 80 px² ROI → 0.15.
- **Information value** · Distinguishes images with and without visible exposed roots.

### X21 — Relative horizontal root spread

- **Source and formula** · Report 1 §2.4.3. `(x_max − x_min)/W`.
- **Inputs, range and unit** · Reliable nonempty root mask and image width. [0,(W−1)/W], ratio.
- **Validity and edge cases** · One occupied column gives 0. Unobserved extent or an empty mask is invalid.
- **Calibration or convention** · A04, A12, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · At W = 100 with extrema 20 and 50, result is 0.30.
- **Information value** · Compares the visible lateral reach of root systems.

### X22 — Relative root thickness

- **Source and formula** · Report 1 §2.4.3. `W_root/W_trunk with W_root the median of local eligible thickness samples`.
- **Inputs, range and unit** · Reliable root mask and supported skeleton width samples, plus positive reliable W_trunk in px from X4's numerator. (0,∞), ratio.
- **Validity and edge cases** · A zero or unknown trunk width invalidates the ratio. Apply consistent measurement support at crop/ROI boundaries.
- **Calibration or convention** · A12–A13, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · Root samples [2,4,8] px and W_trunk = 20 px give 0.20.
- **Information value** · Compares the thickness of visible roots relative to their stems.

### X23 — Relative root skeleton length

- **Source and formula** · Report 1 §2.4.3. `L(Sk(M_root))/D`.
- **Inputs, range and unit** · Reliable nonempty root mask, valid root skeleton and positive image diagonal. [0,∞), ratio.
- **Validity and edge cases** · A reliable isolated vertex contributes zero link length. A failed skeleton or unobserved roots are invalid.
- **Calibration or convention** · A07, A12, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · Two unit links and one unambiguous diagonal give (2+sqrt(2))/1280 at standard size.
- **Information value** · Describes the aggregate reach of the visible root network.

### X24 — Main roots originating at the base

- **Source and formula** · Report 1 §2.4.3. `count of distinct supported main root departures from the trunk-base anchor`.
- **Inputs, range and unit** · Reliable root skeleton, trunk-base anchor and a trusted connection from the skeleton to the base. Nonnegative integer, roots.
- **Validity and edge cases** · Exclude disconnected/unanchored fragments from the count. If the base connection is unobservable or attribution ambiguous, mark invalid. Zero is valid only when the observable anchor supports that conclusion.
- **Calibration or convention** · A07, A12, A14, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · Two independent connected departures and one isolated fragment → 2.
- **Information value** · Distinguishes sparse main roots from roots radiating in several directions.

### X25 — Root edge density

- **Source and formula** · Report 1 §2.4.3. `A(E ∩ M_root)/A(M_root)`.
- **Inputs, range and unit** · RGB, configured edge map and reliable nonempty root mask. [0,1], ratio.
- **Validity and edge cases** · No detected edge gives 0. Absent or unreliable mask invalidates the result.
- **Calibration or convention** · A12, A16, A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · 3 edge pixels among 12 root pixels → 0.25. Edge pixels outside the mask contribute nothing.
- **Information value** · Adds evidence of visible root surface roughness and structural detail.

## Ground context (X26–X31)

### X26 — Ground green fraction

- **Source and formula** · Report 1 §2.5.3. `A(C_green ∩ M_ground)/A(M_ground)`.
- **Inputs, range and unit** · RGB, reliable ground with sufficient area and configured green predicate. [0,1], ratio.
- **Validity and edge cases** · Zero when no ground pixel is green. Unknown area or predicate yields invalid.
- **Calibration or convention** · A15, A19–A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · 4 green ground pixels out of 10 → 0.4, ignoring green elsewhere.
- **Information value** · Helps distinguish vegetation-covered ground from other surfaces.

### X27 — Ground brown fraction

- **Source and formula** · Report 1 §2.5.3. `A(C_brown ∩ M_ground)/A(M_ground)`.
- **Inputs, range and unit** · RGB, reliable ground with sufficient area and configured brown predicate. [0,1], ratio.
- **Validity and edge cases** · Zero is valid for a ground region without brown pixels. Brown roots are excluded.
- **Calibration or convention** · A15, A19–A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · 2 brown ground pixels out of 10 → 0.2. Brown pixels in the excluded root mask do not count.
- **Information value** · Helps distinguish earth, sand and brown materials.

### X28 — Ground gray fraction

- **Source and formula** · Report 1 §2.5.3. `A(C_gray ∩ M_ground)/A(M_ground)`.
- **Inputs, range and unit** · RGB, reliable ground with sufficient area and configured gray predicate. [0,1], ratio.
- **Validity and edge cases** · Zero if no pixel meets the configured gray rule. Keep the denominator as all ground pixels.
- **Calibration or convention** · A15, A19–A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · 3 gray among 10 ground pixels → 0.3.
- **Information value** · Adds evidence for pavement, rock or other neutral surfaces.

### X29 — Ground grayscale population variance

- **Source and formula** · Report 1 §2.5.3. `mean over M_ground of (G(p) − mean_ground(G))²`.
- **Inputs, range and unit** · RGB, uint8 grayscale and reliable ground with sufficient area. [0,16256.25], squared intensity levels.
- **Validity and edge cases** · Use population denominator N. Constant measured ground has variance 0. Insufficient region area is invalid.
- **Calibration or convention** · A16, A19–A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · Intensity samples [0,10] → 25.
- **Information value** · Distinguishes uniform ground from ground with strong tonal variation.

### X30 — Ground edge density

- **Source and formula** · Report 1 §2.5.3. `A(E ∩ M_ground)/A(M_ground)`.
- **Inputs, range and unit** · RGB, configured edge map and reliable ground with sufficient area. [0,1], ratio.
- **Validity and edge cases** · Edge-free ground gives 0. Compute edges before masking to avoid edges created by blacking out pixels.
- **Calibration or convention** · A16, A19–A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · 3 ground edge pixels out of 10 → 0.3.
- **Information value** · Describes the amount of boundary and texture detail in the ground.

### X31 — Ground straight-line density

- **Source and formula** · Report 1 §2.5.3. `L_lines(M_ground)/A(M_ground)`.
- **Inputs, range and unit** · RGB, configured edge/line method and reliable ground with sufficient area. [0,∞), px per px².
- **Validity and edge cases** · No qualifying lines in a valid region gives 0. Mask holes split line support, and duplicate steps are counted once under A17.
- **Calibration or convention** · A16–A17, A19–A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · Two disjoint in-mask line fragments of 3 and 2 px over 10 px² give 0.5 px⁻¹.
- **Information value** · Adds evidence of curbs, markings and other linear ground structures.

## Background context (X32–X37)

### X32 — Background blue fraction

- **Source and formula** · Report 1 §2.5.4. `A(C_blue ∩ M_back)/A(M_back)`.
- **Inputs, range and unit** · RGB, reliable background with sufficient area and configured blue predicate. [0,1], ratio.
- **Validity and edge cases** · A region without blue is valid zero. Exclude ground, tree and visible roots from the measurement.
- **Calibration or convention** · A15, A19–A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · 5 blue pixels among 20 background pixels → 0.25.
- **Information value** · Supports comparison of blue-sky-like backgrounds.

### X33 — Background green fraction

- **Source and formula** · Report 1 §2.5.4. `A(C_green ∩ M_back)/A(M_back)`.
- **Inputs, range and unit** · RGB, reliable background with sufficient area and the same green predicate as X26. [0,1], ratio.
- **Validity and edge cases** · Zero if no background pixel is green. Foreground foliage does not count.
- **Calibration or convention** · A15, A19–A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · 4 green background pixels among 20 → 0.20 even if the canopy is entirely green.
- **Information value** · Adds evidence of vegetation behind the subject.

### X34 — Background white fraction

- **Source and formula** · Report 1 §2.5.4. `A(C_white ∩ M_back)/A(M_back)`.
- **Inputs, range and unit** · RGB, reliable background with sufficient area and configured white predicate. [0,1], ratio.
- **Validity and edge cases** · Zero if no pixel meets the predicate. Saturation and brightness settings must share the HSV scale.
- **Calibration or convention** · A03, A15, A19–A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · 8 white pixels among 20 background pixels → 0.40.
- **Information value** · Adds evidence for clouds, very bright sky or plain white backgrounds.

### X35 — Background grayscale population variance

- **Source and formula** · Report 1 §2.5.4. `mean over M_back of (G(p) − mean_back(G))²`.
- **Inputs, range and unit** · RGB, uint8 grayscale and reliable background with sufficient area. [0,16256.25], squared intensity levels.
- **Validity and edge cases** · Use population denominator N. A uniform measured background has genuine zero variance.
- **Calibration or convention** · A16, A19–A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · Intensity samples [20,40] → 100.
- **Information value** · Separates plain backgrounds from backgrounds with tonal variation.

### X36 — Background edge density

- **Source and formula** · Report 1 §2.5.4. `A(E ∩ M_back)/A(M_back)`.
- **Inputs, range and unit** · RGB, configured edge map and reliable background with sufficient area. [0,1], ratio.
- **Validity and edge cases** · Edge-free background gives zero. Exclude tree, ground and roots from the edge count.
- **Calibration or convention** · A16, A19–A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · 6 edge pixels among 20 background pixels → 0.30.
- **Information value** · Measures visible texture and structural complexity behind the tree.

### X37 — Background straight-line density

- **Source and formula** · Report 1 §2.5.4. `L_lines(M_back)/A(M_back)`.
- **Inputs, range and unit** · RGB, configured edge/line method and reliable background with sufficient area. [0,∞), px per px².
- **Validity and edge cases** · No qualifying line gives valid zero. A segment crossing a masked tree or root contributes only supported steps outside it.
- **Calibration or convention** · A16–A17, A19–A20 in the decision register. Calibrate only the referenced open settings.
- **Expected mathematical test** · 12 px of unique line length inside 20 px² of background gives 0.6 px⁻¹.
- **Information value** · Adds evidence for buildings, walls and other linear structures.

## Semantic labels outside X0–X37

These Report 1 rules are starting points. They are neither confidence claims nor validated production thresholds. Apply a rule only when its needed inputs are valid. Return an unknown/indeterminate label when a threshold or input is unavailable. A raw numerical result remains independent of the assigned label.

| Subject | Initial rule and implementation status |
| --- | --- |
| Trunk visibility | X0 < 0.10 not visible, 0.10 ≤ X0 ≤ 0.60 partial, X0 > 0.60 relatively clear. |
| Trunk width | X4 < 0.05 thin, 0.05 ≤ X4 ≤ 0.12 medium, X4 > 0.12 thick. |
| Trunk form | X6 > ε_curve indicates curved. Otherwise X5 ≤ 7° is straight/upright, and X5 > 7° is inclined. ε_curve needs calibration. |
| Basal structure | X7 = 1 and X8 = 0 gives single trunk. X7 ≥ 2 or X8 ≥ 1 gives multiple stems or basal branching given valid qualifying evidence. With X7 = 1.5 and X8 = 0, return indeterminate pending a label decision. |
| Bark tone | Brown, light/dark gray and intermediate tones are intended. The rules and cutoffs depend on the approved X1–X3 representation. |
| Leafiness | X9 ≥ 0.10 leafy, below 0.10 leafless for an observed ROI. |
| Canopy fill | X13 > 0.70 dense, 0.45 ≤ X13 ≤ 0.70 medium, X13 < 0.45 sparse. |
| Canopy shape | Rounded if 0.85 ≤ X14 ≤ 1.15 and X15 > 0.75. Conical if X14 > 1.25 and X16 ≥ 0.67. Horizontally spreading if X14 < 0.75. Free-form otherwise when the required shape inputs are valid. |
| Foliage colors | The draft bands in the local export are green [35,85], yellow-green [25,35), yellow/orange [15,25), earthy orange [10,15) with V < 0.55, and red/pink/purple for hue <10 or ≥160. Confirm the original hue scale and calibrate categories before enabling labels. OpenCV 8-bit hue bins must never be compared directly with physical degrees. See A03 and A15. |
| Branches | Propose visible if X17 ≥ τ_branch_visibility and low-visible below it. For visible branches, zero X19 means exposed unbranched when the skeleton is reliable. Use X18 > τ_branch_length for sufficient extent to interpret the draft junction brackets of 1–6 for lighter branching and >6 for dense branching. Short visible branched cases remain visible with insufficient extent for a density label. See A11. |
| Roots | X20 ≥ τ_root_visible gives exposed roots. X20 below that threshold gives unexposed for a reliable observation. Optional intensity `I_root = Σ_(k=21..25) v_k z_k`, with nonnegative weights summing to one, uses one approved normalization profile and valid normalized inputs for every positive-weight term. For exposed roots, `I_root < τ_root_intensity` indicates low intensity, otherwise high. The weights and thresholds require calibration. |
| Context | Draft ground labels include grass, soil, snow and pavement. Draft backdrop labels include sky, natural, artificial and white. Score functions, units, tie/unknown behavior and thresholds require definition and calibration. Ground white proportion and mean V/S may support labels outside the vector. No semantic score adds a feature dimension. |

Report 1 §3 governs Min–Max and the five-group combination. Report 1 §4 motivates each feature's information value above. Claims about actual retrieval gains require the evaluation in [R04C and E06](requirements.md#experimental-evaluation).
