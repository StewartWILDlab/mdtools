import pandas as pd


def join_exif_to_csv(csv_file, exif_file, join_file, write=True, by="source_file"):
    csv = pd.read_csv(csv_file)
    # csv["SourceFile"] = (
    #     "/media/vlucet/TrailCamST/TrailCamStorage/" + csv["folder"] + "/" + csv["file"]
    # )
    exif = pd.read_csv(exif_file)

    joined = pd.merge(csv, exif, how="left", on=by)
    
    if write:
        joined.to_csv(join_file, index = False)

    return joined
