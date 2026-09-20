# Changelog

## 1.0.0 (2026-09-20)

Ground-up rewrite of the 2020-era codebase. Same feature scope for the
core (8 conversion directions, labeled/unlabeled augmentation), rebuilt
on a clean architecture with tests.

### Added
- Unified intermediate representation (`Annotation`/`Shape`): every
  format is read into it and written from it; N x M converter matrix
  collapsed to N + M readers/writers.
- Augmentation pipeline that **always** transforms image and labels
  together (affine matrix shared by pixels and polygon points,
  Sutherland-Hodgman canvas clipping, nearest-neighbor masks) with
  seeded reproducibility.
- Dataset quality analysis: annotation-consistency checks (bounds,
  duplicates, size mismatches, unknown classes), image-quality metrics
  (brightness/contrast/sharpness/noise/saturation), overlay PNGs,
  baseline comparison (class drift, area drift, metric deltas).
- Dataset statistics: positive:negative sample ratio, objects per image,
  class imbalance, foreground coverage, tiny-object fraction, near-
  duplicate image detection (dhash), and a transparent 0-100 health
  score with per-penalty breakdown.
- `convertmask split`: stratified train/val split for YOLO label
  directories (rarest classes placed first, seeded-deterministic, no
  file in both sets; legacy version leaked state across calls).
- Web UI: `convertmask serve` (FastAPI + vanilla JS/Tailwind), drag-and-
  drop upload, browser-side label overlays, report view, zip download.
  Install extra: `pip install convertmask[web]`.
- pytest suite (75 tests) with format round-trips, legacy-bug
  regressions and server integration tests; ruff-clean.
- `pyproject.toml` packaging; dependencies slimmed to numpy /
  opencv-python-headless / Pillow / PyYAML / tqdm.

### Fixed (vs 0.6.0)
- yolo2xml: width/height axes were swapped — boxes wrong on every
  non-square image; directory mode never worked (existence check on a
  wildcard path).
- xml2yolo: class table was reset between files, so class ids differed
  across output txts and labels.txt could miss classes.
- augmentation: rotated boxes computed from edge midpoints (15-30% too
  small); label maps warped with linear interpolation (invented class
  ids at boundaries); per-class zoom masks summed (class id addition);
  rotation/translation (nolabel) saved the original image; several
  always-crashing code paths (`setNoiseType`, `imgAutopad`, `np.pad`
  with floats, `yman` tag).
- CLI: `mask2xml` full name unreachable, `img2xml`/`xml2mask` advertised
  but unimplemented (silent no-op), unknown methods fell through
  silently; `-L/--nolog` was a no-op.
- Packaging: setup.py vs requirements.txt contradictory pins
  (uninstallable on Python 3.11+); config.ini missing from installs
  (import-time crash); `find_packages()` shipped dead backup code
  including a labelme monkey-patcher; PyQt UI shipped broken (missing
  dependency and `__init__.py`).
- No more silent failure: per-file `except Exception` blocks that
  logged and reported "Done!" are gone; errors raise, the CLI exits
  non-zero.

### Removed
- labelme, scikit-image, scipy, matplotlib, xmltodict dependencies (the
  few used algorithms are implemented in `convertmask.core`).
- PyQt5 GUI (replaced by the web UI), legacy backup code, ad-hoc
  test scripts, `config.ini`.

### Deferred to 1.1
WIDER-face conversion, long-image splitting, negative-sample
generation, k-means anchors.

## 0.6.0 and earlier

See git history of the original `mask2json` project.
