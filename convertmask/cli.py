"""Command-line interface.

Subcommands:
    convertmask convert <method> --imgs .. [--masks/--labels/--annos ..] [--classes ..] [--out ..]
    convertmask augment --imgs .. [--labels ..] [--methods flip,noise] [--number N] [--seed S]
    convertmask analyze --annos .. [--imgs ..] [--classes ..] [--baseline ..]
    convertmask serve [--host H] [--port P]

The legacy flat form ``convertmask m2j -i imgs masks yaml`` is still
accepted and translated to the subcommand form.
"""

from __future__ import annotations

import argparse
import logging
import sys

from convertmask import SUPPORTED_METHODS, __version__
from convertmask.converters import CONVERTER_ARGS, normalize_method

logger = logging.getLogger("convertmask")

# legacy flat form: -i argument order per method
_LEGACY_INPUT_ORDER = {
    "mask2json": ["imgs", "masks", "classes"],
    "mask2xml": ["imgs", "masks"],
    "json2mask": ["jsons"],
    "json2xml": ["jsons"],
    "xml2json": ["xmls", "imgs"],
    "xml2yolo": ["xmls", "classes"],
    "yolo2xml": ["txts", "imgs", "classes"],
    "xml2mask": ["xmls", "classes"],
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="convertmask",
        description="Annotation conversion, augmentation and quality analysis",
    )
    parser.add_argument("-v", "--version", action="version",
                        version=f"convertmask {__version__}")
    sub = parser.add_subparsers(dest="command")

    p_conv = sub.add_parser("convert", help="convert between annotation formats")
    p_conv.add_argument("method", help=f"one of {', '.join(SUPPORTED_METHODS)} (or aliases m2j, x2y, ...)")
    p_conv.add_argument("--imgs", help="origin images (file or dir)")
    p_conv.add_argument("--masks", help="mask images (mask2json/mask2xml)")
    p_conv.add_argument("--jsons", help="labelme JSON file or dir")
    p_conv.add_argument("--xmls", help="VOC XML file or dir")
    p_conv.add_argument("--txts", help="YOLO txt file or dir")
    p_conv.add_argument("--classes", help="class file: txt / info.yaml / .names")
    p_conv.add_argument("--out", help="output directory (default: alongside input)")

    p_aug = sub.add_parser("augment", help="augment images, labels follow")
    p_aug.add_argument("--imgs", required=True, help="images (file or dir)")
    p_aug.add_argument("--labels", help="labelme JSON / VOC XML file or dir")
    p_aug.add_argument("--label-fmt", choices=["json", "xml", "none"],
                       help="disambiguate mixed label dirs")
    p_aug.add_argument("--methods", default="flip,rotation,translation,zoom,noise",
                       help="comma-separated augmentation methods")
    p_aug.add_argument("--number", type=int, default=1, help="rounds per image")
    p_aug.add_argument("--seed", type=int, default=None, help="random seed")
    p_aug.add_argument("--out", help="output directory")
    p_aug.add_argument("--save-mask", action="store_true",
                       help="also write class-id masks of augmented annotations")

    p_ana = sub.add_parser("analyze", help="dataset quality analysis")
    p_ana.add_argument("--annos", required=True, help="annotations (json/xml, file or dir)")
    p_ana.add_argument("--imgs", help="images (file or dir)")
    p_ana.add_argument("--classes", help="class file for unknown-class check")
    p_ana.add_argument("--baseline", help="baseline annotations for drift comparison")
    p_ana.add_argument("--baseline-imgs", help="images belonging to the baseline set")
    p_ana.add_argument("--out", help="output dir (default: <annos>/../analysis)")

    p_split = sub.add_parser("split", help="stratified train/val split of YOLO label dirs")
    p_split.add_argument("--txts", required=True, help="YOLO label txt file or dir")
    p_split.add_argument("--out", help="output dir for train.txt / val.txt")
    p_split.add_argument("--val-ratio", type=float, default=0.1,
                         help="target validation fraction per class")
    p_split.add_argument("--seed", type=int, default=None)

    p_serve = sub.add_parser("serve", help="start the web UI (needs convertmask[web])")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8000)

    return parser


def _run_convert(args) -> int:
    from convertmask.converters import convert

    method = normalize_method(args.method)
    kwargs = {}
    for name in CONVERTER_ARGS[method]:
        value = getattr(args, name, None)
        if value:
            kwargs[name] = value
    missing = [
        n for n in CONVERTER_ARGS[method]
        if n not in {"out", "classes"} and n not in kwargs
    ]
    if missing:
        print(
            f"convert {method}: missing required input(s): {', '.join(missing)}",
            file=sys.stderr,
        )
        return 2
    outputs = convert(method, **kwargs)
    for p in outputs:
        print(p)
    print(f"{len(outputs)} file(s) written")
    return 0


def _run_augment(args) -> int:
    from convertmask.augment import augment_images

    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    outputs = augment_images(
        imgs=args.imgs,
        labels=args.labels,
        methods=methods,
        number=args.number,
        seed=args.seed,
        out=args.out,
        label_fmt=args.label_fmt,
        save_mask=args.save_mask,
    )
    print(f"{len(outputs)} file(s) written")
    return 0


def _run_analyze(args) -> int:
    from convertmask.analyze import analyze_dataset

    report = analyze_dataset(
        annos=args.annos,
        imgs=args.imgs,
        classes=args.classes,
        out=args.out,
        baseline=args.baseline,
        baseline_imgs=args.baseline_imgs,
    )
    s = report["summary"]
    health = report.get("health", {})
    stats = report.get("stats", {})
    print(
        f"{s['annotations']} annotation(s), {s['images']} image(s): "
        f"{s['errors']} error(s), {s['warnings']} warning(s)"
    )
    if health:
        print(
            f"health: {health['score']}/100 (grade {health['grade']}); "
            f"pos:neg = {stats.get('pos_neg_ratio', '-')}, "
            f"{stats.get('objects_per_image', {}).get('mean', 0)} objects/image"
        )
    for code, count in list(s["issue_counts"].items())[:10]:
        print(f"  {code}: {count}")
    return 1 if s["errors"] else 0


def _run_split(args) -> int:
    from convertmask.tools import train_val_split

    result = train_val_split(
        txts=args.txts, out=args.out, val_ratio=args.val_ratio, seed=args.seed
    )
    print(f"train: {len(result['train'])} file(s), val: {len(result['val'])} file(s)")
    for cls, count in result["class_counts"].items():
        print(f"  class {cls}: {count} object(s)")
    if args.out:
        print(f"written to {args.out}/train.txt and {args.out}/val.txt")
    else:
        print("--out not given; nothing written")
    return 0


def _run_serve(args) -> int:
    try:
        import uvicorn
    except ImportError:
        print(
            "web dependencies missing; install with: pip install convertmask[web]",
            file=sys.stderr,
        )
        return 2
    from convertmask.server.app import create_app

    uvicorn.run(create_app(), host=args.host, port=args.port)
    return 0


def _legacy_to_subcommand(argv: list[str]) -> list[str] | None:
    """Translate the legacy flat form to subcommand form."""
    first = argv[0]
    methods = set(SUPPORTED_METHODS) | {"augmentation", "aug", "m2j", "m2x", "j2m",
                                        "j2x", "x2j", "x2y", "y2x"}
    if first not in methods:
        return None

    # minimal manual parse of the legacy flags
    inputs: list[str] = []
    opts: dict[str, str] = {}
    nolabel = labelimg = False
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "-i" or a == "--input":
            i += 1
            while i < len(argv) and not argv[i].startswith("-"):
                inputs.append(argv[i])
                i += 1
            continue
        if a in ("-c", "--classfilepath"):
            opts["classes"] = argv[i + 1]
            i += 2
            continue
        if a in ("-N", "--number"):
            opts["number"] = argv[i + 1]
            i += 2
            continue
        if a in ("-n", "--nolabel"):
            nolabel = True
            i += 1
            continue
        if a in ("-X", "--labelImg"):
            labelimg = True
            i += 1
            continue
        if a in ("-L", "--nolog", "-H", "--HELP", "-v", "--version"):
            i += 1
            continue
        i += 1

    if first == "augmentation" or first == "aug":
        cmd = ["augment", "--imgs", inputs[0] if inputs else ""]
        if len(inputs) > 1 and not nolabel:
            cmd += ["--labels", inputs[1]]
        if labelimg:
            cmd += ["--label-fmt", "xml"]
        if "number" in opts:
            cmd += ["--number", opts["number"]]
        return cmd

    method = normalize_method(first)
    order = _LEGACY_INPUT_ORDER[method]
    cmd = ["convert", method]
    for pos, name in enumerate(order):
        if pos < len(inputs):
            cmd += [f"--{name}", inputs[pos]]
    if "classes" in opts and "classes" not in order:
        cmd += ["--classes", opts["classes"]]
    return cmd


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    argv = list(sys.argv[1:] if argv is None else argv)

    if argv and argv[0] not in {"convert", "augment", "analyze", "split", "serve",
                                "-v", "--version", "-h", "--help"}:
        translated = _legacy_to_subcommand(argv)
        if translated is not None:
            argv = translated

    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0
    try:
        if args.command == "convert":
            return _run_convert(args)
        if args.command == "augment":
            return _run_augment(args)
        if args.command == "analyze":
            return _run_analyze(args)
        if args.command == "split":
            return _run_split(args)
        if args.command == "serve":
            return _run_serve(args)
    except (ValueError, FileNotFoundError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
