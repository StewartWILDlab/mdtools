## MegaDetector tools

MegaDetector tools - convert and parse MDv5 results

### CLI tool

#### Command: convert

```bash
Usage: mdtools convert [OPTIONS] {cct|ls|csv} MD_JSON

Options:
  -ct, --conf-threshold FLOAT   Threshold under which predictions
                                are removed  [default: 0.1]
  -bd, --image-base-dir TEXT    Directory containing the raw
                                images  [default: .]
  -ru, --image-root-url TEXT    Label Studio local file url
                                [default: /data/local-files/?d=]
  -wc, --write-coco BOOLEAN     [default: False]
  -wl, --write-ls BOOLEAN       [default: True]
  -ws, --write-csv BOOLEAN      [default: True]
  -oc, --output-json-coco TEXT
  -ol, --output-json-ls TEXT
  --help                        Show this message and exit.
```