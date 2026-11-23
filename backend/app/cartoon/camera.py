"""
Cartoon Camera Dynamics Engine.
Provides:
- Smooth camera push-in / zoom into character or focal point
- Camera shake (earthquake / shock impact effect) with realistic exponential decay
"""

import math
from typing import Optional, Tuple
from PIL import Image


class CameraController:
    """Controls 2D viewport transformations (zoom and shake)."""

    def __init__(self, width: int = 1080, height: int = 1920):
        self.width = width
        self.height = height

    def apply(
        self,
        frame: Image.Image,
        zoom: float = 1.0,
        focal_point: Tuple[int, int] = (540, 1100),
        shake_intensity: float = 0.0,
        t: float = 0.0,
    ) -> Image.Image:
        """Applies zoom and shake transformations to frame."""
        # 1. Compute shake displacement (high-frequency oscillation)
        offset_x = 0
        offset_y = 0
        if shake_intensity > 0.01:
            # Shake frequency ~28 Hz
            phase = t * 28.0 * 2.0 * math.pi
            offset_x = int(math.sin(phase) * shake_intensity * 18.0)
            offset_y = int(math.cos(phase * 1.3) * shake_intensity * 12.0)

        # 2. Compute zoom crop box if zoom != 1.0
        if abs(zoom - 1.0) < 0.005 and offset_x == 0 and offset_y == 0:
            return frame

        # Clamped effective zoom
        z = max(1.0, min(zoom, 1.35))
        crop_w = int(self.width / z)
        crop_h = int(self.height / z)

        fx, fy = focal_point
        fx += offset_x
        fy += offset_y

        left = max(0, min(fx - crop_w // 2, self.width - crop_w))
        top = max(0, min(fy - crop_h // 2, self.height - crop_h))
        right = left + crop_w
        bottom = top + crop_h

        cropped = frame.crop((left, top, right, bottom))
        return cropped.resize((self.width, self.height), Image.Resampling.BILINEAR)
