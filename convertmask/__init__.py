"""convertmask: annotation conversion, augmentation and quality analysis.

Core layout:
    convertmask.core       -- intermediate representation and format IO
    convertmask.converters -- conversions between annotation formats
    convertmask.augment    -- image augmentation with label synchronization
    convertmask.analyze    -- annotation-consistency and image-quality analysis
    convertmask.server     -- optional FastAPI web frontend (`pip install convertmask[web]`)
"""

__version__ = "1.0.0"
__appname__ = "convertmask"

SUPPORTED_IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}

# labelme JSON, Pascal VOC XML, YOLO txt, class-id mask images
SUPPORTED_ANNO_EXTS = {".json", ".xml", ".txt"}

SUPPORTED_CLASSFILE_EXTS = {".txt", ".names", ".yaml", ".yml"}

# conversion directions, "src2dst"
SUPPORTED_METHODS = [
    "mask2json",
    "mask2xml",
    "json2mask",
    "json2xml",
    "xml2json",
    "xml2yolo",
    "yolo2xml",
    "xml2mask",
]

METHOD_ALIASES = {
    "mask2json": "m2j",
    "mask2xml": "m2x",
    "json2mask": "j2m",
    "json2xml": "j2x",
    "xml2json": "x2j",
    "xml2yolo": "x2y",
    "yolo2xml": "y2x",
}

AUG_METHODS = ["flip", "rotation", "translation", "zoom", "noise"]

AUG_OPTIONAL_METHODS = [
    "crop",
    "distort",
    "inpaint",
    "perspective",
    "resize",
    "mixup",
    "cutmix",
]
