# convertmask

Annotation-format conversion, image augmentation with label
synchronization, and dataset quality analysis — for labelme JSON, Pascal
VOC XML, YOLO txt and class-id mask images.

This is a ground-up rewrite of the original 2020-era `mask2json` tool
(see [CHANGELOG](CHANGELOG.md)): every conversion goes through a single
intermediate representation, augmentation always transforms image and
labels together, and nothing fails silently.

## Install

```bash
pip install .                # core: convert / augment / analyze
pip install '.[web]'         # + web UI (fastapi/uvicorn)
pip install '.[dev]'         # + pytest / ruff
```

Requires Python 3.10+. Runtime dependencies are just numpy,
opencv-python-headless, Pillow, PyYAML and tqdm.

## CLI

```text
convertmask convert <method> [inputs]
convertmask augment  --imgs DIR [--labels DIR] [options]
convertmask analyze  --annos DIR [--imgs DIR] [options]
convertmask serve    [--host H] [--port P]
```

Methods (aliases in brackets): `mask2json [m2j]`, `mask2xml [m2x]`,
`json2mask [j2m]`, `json2xml [j2x]`, `xml2json [x2j]`, `xml2yolo [x2y]`,
`yolo2xml [y2x]`, `xml2mask`. Every method accepts single files or
directories (jpg/jpeg/png/bmp) and an optional class file
(`.txt` names, `.names`, or labelme `info.yaml` name->value map).

```bash
# masks (with a class file) -> labelme JSON
convertmask convert mask2json --imgs imgs/ --masks masks/ --classes classes.txt

# VOC xmls -> YOLO txts (+ labels.txt, stable ids across all files)
convertmask convert xml2yolo --xmls xmls/ --classes classes.txt

# augment with labels following the pixels, reproducible
convertmask augment --imgs imgs/ --labels labels/ \
    --methods rotation,noise,flip --number 3 --seed 42

# check a dataset: bounds, duplicates, class drift, image quality
convertmask analyze --annos labels/ --imgs imgs/ --classes classes.txt

# web UI
convertmask serve --port 8000
```

The legacy flat form is still accepted and translated:
`convertmask m2j -i imgs masks classes.txt`.

## Library

```python
from convertmask.converters import convert
outputs = convert("mask2json", imgs="imgs/", masks="masks/", classes="c.txt")

from convertmask.augment import augment_images
outputs = augment_images("imgs/", "labels/", methods=["rotation", "noise"],
                         number=2, seed=7, out="aug/")

from convertmask.analyze import analyze_dataset
report = analyze_dataset("labels/", imgs="imgs/", out="analysis/")
```

## Web UI

`convertmask serve` starts a local web app: drag-and-drop upload
(images / labels / class files are grouped automatically; tick *treat
dropped images as masks* for mask2json), run conversions/augmentations,
preview images with label overlays drawn in the browser, view the
analysis report (issue table, class distribution, quality metrics) and
download results as zip.

## What the analyzer checks

- annotation consistency: out-of-bounds / degenerate / tiny boxes,
  same-class near-duplicates (IoU), empty annotations, unknown classes
  vs your class file, annotation-vs-image size mismatches
- augmentation safety: per-class area drift against a baseline set,
  class-distribution drift, before/after image-quality deltas
  (brightness, contrast, sharpness, noise, saturation)
- every image gets an overlay PNG with problematic shapes highlighted

## Development

```bash
pip install -e '.[dev,web]'
pytest          # 75 tests: round-trips, legacy-bug regressions, server API
ruff check .
./web/build.sh  # rebuild web UI (needs npx; built assets are committed)
```

Fixtures live in `static/`. Roadmap for v1.1: WIDER-face conversion,
long-image splitting, negative-sample generation, train/val split and
k-means anchors.

## License

Apache-2.0
