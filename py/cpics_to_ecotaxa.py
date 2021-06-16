import csv
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, List
from zipfile import ZipFile, ZIP_DEFLATED

ROI_TXT_FILES = "*.roicoords.txt"
ROI_IMAGE_FILES = "**/*.png"

"""
The following come from the CPICS itself:
Item (ROI is the only option here)
Date (format YYYY/MM/DD)
Time (format HH:MM:SS.SSS , the three decimal points bring the time accuracy down to the millisecond range)
Name (file name of the roi in question, composed of DATE_TIME.NumericalIdentifyer.png, the numerical identifyer starts at 0 and counts up in steps of 1, in case several ROIS were captured in the same millisecond)
Position upper leftx (Upper left x-axis coordinate of the ROI within the fullframe)
Position upper lefty (Upper left y-axis coordinate of the ROI within the fullframe)
Position lower rightx (Lower right x-axis coordinate of the ROI within the fullframe)
Position lower rightY (Lower right y-axis coordinate of the ROI within the fullframe)
Environmental measures (Temperature,Conductivity,Pressure,Depth,Salinity,Sound Velocity,local density) are provided by a CTD that is linked to the CPICS. Linking the CTD is optional but we basically never run the CPICS on its own without CTD, except for during tests.
"""
ROI_BASE_HDR = "Item,Date Time,Name".split(",")
ROI_POS_HDR = "Position upper leftx,Position upper lefty,Position lower rightx,Position lower righty". \
    split(",")
CTD_HDR = "Temperature,Conductivity,Pressure,Depth,Salinity,Sound Velocity,local density".split(",")
FULL_HDR = ROI_BASE_HDR + ROI_POS_HDR + CTD_HDR

ECOTAXA_BASE_HDR = ["img_file_name", "object_id", "object_date", "object_time"]


def to_ecotaxa(a_hdr: str):
    return "object_" + a_hdr


ECOTAXA_POS_CTD_HDR = [to_ecotaxa(hdr) for hdr in ROI_POS_HDR + CTD_HDR]


def cips_to_ecotaxa(a_row: Dict[str, Any]) -> Dict[str, Any]:
    # e.g. ROI,2019/11/24 21:12:38.986,20191124_211238.986.0.png,2216,1684,2272,1728,  22.4756,  0.00003,   -0.189,  -0.188,   0.0110, 1489.718, -2.3297,
    ret = {}
    date, time = a_row["Date Time"].split(" ")
    ret["object_date"] = date.replace("/", "-")
    ret["object_time"] = time[:8]  # Unfortunately no ms
    img_name = a_row["Name"]
    ret["img_file_name"] = img_name
    assert img_name.endswith(".png")
    ret["object_id"] = img_name[:-4]
    # Copy the rest as TSV
    for a_col, a_free_col in zip(ROI_POS_HDR + CTD_HDR, ECOTAXA_POS_CTD_HDR):
        ret[a_free_col] = a_row[a_col]
    return ret


def find_image(images: List[Path], qry: str) -> Path:
    # TODO: slow
    for an_image in images:
        if qry in str(an_image):
            return an_image


def csv_to_tsv_with_images(roi_path: Path, image_files: List[Path], ecotaxa_path: Path):
    roi_directory = roi_path.parent
    zipfile = ZipFile(ecotaxa_path, mode="w", allowZip64=True, compression=ZIP_DEFLATED)
    image_refs_in_csv = []
    with tempfile.NamedTemporaryFile(suffix=".tsv", mode="w", delete=False) as tsvfile:
        eco_writer = csv.DictWriter(tsvfile, ECOTAXA_BASE_HDR + ECOTAXA_POS_CTD_HDR, dialect=csv.excel_tab)
        eco_writer.writeheader()
        types_row = {a_col: "[t]" for a_col in ECOTAXA_BASE_HDR}
        types_row.update({a_col: "[f]" for a_col in ECOTAXA_POS_CTD_HDR})
        eco_writer.writerow(types_row)
        with open(roi_path, newline='') as csvfile:
            roi_reader = csv.reader(csvfile)
            for raw_row in roi_reader:
                # There is a trailing ,
                assert (raw_row[-1].strip()) == ""
                raw_row = raw_row[:-1]
                assert len(raw_row) == len(FULL_HDR)
                row = {col: val.strip() for col, val in zip(FULL_HDR, raw_row)}
                assert row["Item"] == "ROI"
                ecotaxa_row = cips_to_ecotaxa(row)
                png_file = find_image(image_files, ecotaxa_row["img_file_name"])
                if png_file is None:
                    print("Bad ref: %s" % ecotaxa_row["img_file_name"])
                    continue
                else:
                    ecotaxa_row["img_file_name"] = str(png_file)
                image_refs_in_csv.append(str(png_file))
                eco_writer.writerow(ecotaxa_row)
    # Zip the CSV
    zipfile.write(filename=tsvfile.name, arcname="ecotaxa.tsv")
    # Zip the images
    for an_image in image_refs_in_csv:
        abs_img_path = roi_directory / an_image
        zipfile.write(filename=abs_img_path, arcname=an_image)
    zipfile.close()
    os.unlink(tsvfile.name)


def main(src_path: Path, dst_path: Path):
    roi = list(src_path.glob(ROI_TXT_FILES))
    assert len(roi) == 1
    the_roi = roi[0]
    abs_images = list(src_path.glob(ROI_IMAGE_FILES))
    assert len(abs_images) > 1
    rel_images = [an_image.relative_to(the_roi.parent) for an_image in abs_images]
    csv_to_tsv_with_images(the_roi, rel_images, dst_path)


if __name__ == '__main__':
    cpics = "/home/laurent/Devs/from_Lab/CPICS/CPICS_example"
    out_zip = "/home/laurent/Devs/from_Lab/CPICS/ecotaxa.zip"
    main(Path(cpics), Path(out_zip))
