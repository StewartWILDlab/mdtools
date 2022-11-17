## MegaDetector tools
[![CI](https://github.com/StewartWILDlab/mdtools/actions/workflows/CI.yaml/badge.svg?branch=main)](https://github.com/StewartWILDlab/mdtools/actions/workflows/CI.yaml)

MegaDetector tools - convert and parse MDv5 results

### CLI tool

#### Command: convert

```
Usage: mdtools convert [OPTIONS] {cct|ls|csv} MD_JSON DIRECTORY

  Convert MD results to different formats used in the pipeline.

Options:
  -ct, --conf-threshold FLOAT  Threshold under which predictions are removed
                               [default: 0.1]
  -ru, --image-root-url TEXT   Label Studio local file url  [default:
                               /data/local-files/?d=]
  --write-coco
  --write-csv
  --write-ls
  --help                       Show this message and exit.
```

#### Command: readexif

```
Usage: mdtools readexif [OPTIONS] MD_JSON

  Read exif from string filepath.

Options:
  -ws, --write-csv BOOLEAN  [default: True]
  --help                    Show this message and exit.
```