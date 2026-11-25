# Preprocessing and common utilities

`preprocess_image()` accepts paths, bytes, or Pillow images. It decodes with Pillow, applies EXIF orientation, composites RGBA over black, converts RGB, center-crops to 3:4, and resizes only when needed to contiguous `(1024, 768, 3)` `uint8` RGB. It never writes sources. Center cropping assumes a centered query tree; tree-aware cropping is deferred.

Coordinate origin is upper-left; NumPy uses `[y, x]`. Boolean masks are H×W. OpenCV boundaries explicitly convert RGB/BGR; uint8 HSV is H 0–179, S/V 0–255. Utilities provide color conversion/range masking (including hue wrap), mask set operations/components, geometry/contours, morphology/skeletons, edges/lines, and copying overlays. They are generic demonstrations, not tree segmentation.

```mermaid
flowchart LR
Input --> Decode --> EXIF --> RGB --> Crop[center crop 3:4] --> Resize[768×1024] --> RGBArray[contiguous RGB uint8]
```
