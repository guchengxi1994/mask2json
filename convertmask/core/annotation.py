"""Intermediate representation (IR) shared by every converter.

Every supported format (labelme JSON, Pascal VOC XML, YOLO txt, class-id
masks) is read into :class:`Annotation` and written from it, so each
conversion is just ``reader -> writer`` and width/height or class-id
mismatches between formats cannot happen by construction.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

# labelme version string written into generated JSON files. The legacy tool
# used labelme.__version__; a fixed "5.x"-era value keeps files recognizable
# by labelme itself without the dependency.
LABELME_VERSION = "5.0.1"

BACKGROUND = "_background_"


@dataclass
class Shape:
    """One annotated object.

    ``points`` is a list of ``[x, y]`` pixel coordinates. ``shape_type`` is
    ``"polygon"`` (N points, N >= 3) or ``"rectangle"`` (2 corner points,
    labelme style). Bbox-only formats (VOC, YOLO) map to 4-point polygons.
    """

    label: str
    points: list[list[float]]
    shape_type: str = "polygon"
    group_id: int | None = None
    flags: dict = field(default_factory=dict)
    difficult: bool = False

    def bbox(self) -> tuple[float, float, float, float]:
        """Return ``(xmin, ymin, xmax, ymax)`` in pixel coordinates."""
        if self.shape_type == "rectangle" and len(self.points) == 2:
            (x1, y1), (x2, y2) = self.points
            return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        return min(xs), min(ys), max(xs), max(ys)

    def to_labelme_dict(self) -> dict:
        return {
            "label": self.label,
            "points": [[float(x), float(y)] for x, y in self.points],
            "group_id": self.group_id,
            "shape_type": self.shape_type,
            "flags": dict(self.flags),
        }

    @classmethod
    def from_labelme_dict(cls, data: dict) -> Shape:
        return cls(
            label=str(data.get("label", "")),
            points=[[float(p[0]), float(p[1])] for p in data.get("points", [])],
            group_id=data.get("group_id"),
            shape_type=data.get("shape_type", "polygon"),
            flags=dict(data.get("flags") or {}),
        )

    def to_polygon(self) -> Shape:
        """Return an equivalent polygon shape (rectangles become 4 points)."""
        if self.shape_type == "rectangle" and len(self.points) == 2:
            (x1, y1), (x2, y2) = self.points
            xmin, ymin, xmax, ymax = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
            pts = [
                [xmin, ymin],
                [xmax, ymin],
                [xmax, ymax],
                [xmin, ymax],
            ]
            return Shape(self.label, pts, "polygon", self.group_id, self.flags, self.difficult)
        return Shape(self.label, [list(p) for p in self.points], "polygon",
                     self.group_id, self.flags, self.difficult)


@dataclass
class Annotation:
    """All shapes of one image plus the ordered class table.

    ``label_names`` defines class ids where meaningful (YOLO, masks):
    id ``i`` corresponds to ``label_names[i]`` and id 0 is background.
    It may be ``None`` when the source format carries no class table
    (e.g. a single labelme JSON); callers then derive it from shape labels.
    """

    width: int
    height: int
    shapes: list[Shape] = field(default_factory=list)
    image_path: Path | None = None
    label_names: list[str] | None = None

    def __post_init__(self):
        if isinstance(self.image_path, str):
            self.image_path = Path(self.image_path) or None

    # ------------------------------------------------------------------ #
    # labelme JSON

    def to_labelme_dict(self, image_data_b64: str | None = None) -> dict:
        return {
            "version": LABELME_VERSION,
            "flags": {},
            "shapes": [s.to_labelme_dict() for s in self.shapes],
            "imagePath": self.image_path.name if self.image_path else "",
            "imageData": image_data_b64,
            "imageHeight": int(self.height),
            "imageWidth": int(self.width),
        }

    @classmethod
    def from_labelme_dict(cls, data: dict) -> Annotation:
        return cls(
            width=int(data["imageWidth"]),
            height=int(data["imageHeight"]),
            shapes=[Shape.from_labelme_dict(s) for s in data.get("shapes") or []],
            image_path=Path(data.get("imagePath") or "") if data.get("imagePath") else None,
        )

    # ------------------------------------------------------------------ #
    # YOLO txt

    def to_yolo_lines(self) -> tuple[list[str], list[str]]:
        """Return ``(lines, labels)``; ``labels`` is the class table used.

        The class table is ``label_names`` without the background entry,
        falling back to first-appearance order of shape labels.
        """
        names = self.class_table()
        lines = []
        for s in self.shapes:
            xmin, ymin, xmax, ymax = s.bbox()
            x = (xmin + xmax) / 2.0 / self.width
            y = (ymin + ymax) / 2.0 / self.height
            w = (xmax - xmin) / self.width
            h = (ymax - ymin) / self.height
            cls_id = names.index(s.label) if s.label in names else -1
            lines.append(f"{cls_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}")
        return lines, names

    @classmethod
    def from_yolo_lines(
        cls,
        lines: list[str],
        labels: list[str],
        width: int,
        height: int,
        image_path: Path | None = None,
    ) -> Annotation:
        shapes = []
        for line in lines:
            parts = line.split()
            if len(parts) < 5:
                continue
            cls_id = int(float(parts[0]))
            x, y, w, h = (float(v) for v in parts[1:5])
            # denormalize: x, y are box centers, w, h box sizes
            cx, cy = x * width, y * height
            bw, bh = w * width, h * height
            xmin, ymin = cx - bw / 2.0, cy - bh / 2.0
            xmax, ymax = cx + bw / 2.0, cy + bh / 2.0
            label = labels[cls_id] if 0 <= cls_id < len(labels) else str(cls_id)
            shapes.append(
                Shape(label, [[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]])
            )
        names = [BACKGROUND, *labels]
        return cls(width, height, shapes, image_path, names)

    # ------------------------------------------------------------------ #

    def class_table(self) -> list[str]:
        """Ordered class names (no background) for id assignment.

        Prefers an explicit ``label_names``; otherwise ids follow
        first-appearance order of the shape labels (legacy behavior of
        ``labelme.utils.shapes_to_label``).
        """
        if self.label_names:
            names = [n for n in self.label_names if n != BACKGROUND]
            if names:
                return names
        seen: list[str] = []
        for s in self.shapes:
            if s.label and s.label not in seen:
                seen.append(s.label)
        return seen

    def label_ids(self) -> dict[str, int]:
        """Map class name -> 1-based id (0 reserved for background)."""
        return {name: i + 1 for i, name in enumerate(self.class_table())}

    # ------------------------------------------------------------------ #
    # convenience IO

    def save_labelme_json(self, path: Path, image_data_b64: str | None = None) -> Path:
        data = self.to_labelme_dict(image_data_b64)
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    @classmethod
    def load_labelme_json(cls, path: Path) -> Annotation:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_labelme_dict(data)
