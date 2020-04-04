import os
from typing import Optional
import wget
from zipfile import ZipFile


def create_data_dir() -> None:
    """ Create the directory to hold all the data and the directory
    is defined inthe config.toml file
    """
    data_dir = "data"
    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)
    return data_dir


def irs_zipcode(year: int) -> Optional[str]:
    """ Download the  Individual Income Tax ZIP Code Data from the IRS
    given the year and returns the relative directory name.
    """
    data_dir = create_data_dir()
    options = list(range(2001, 2018))
    if year in options:
        filename = f"zipcode{year}.zip"
        url = f"https://www.irs.gov/pub/irs-soi/{filename}"
    else:
        print(f"Not a valid year.  Please select from {options}")
        return None
    # Download the file if not found in folder
    if not os.path.isfile(f"{data_dir}/{filename}"):
        wget.download(url, out=data_dir)
    # unzip the archive
    if not os.path.isdir(f"{data_dir}/irs-zipcode-{year}"):
        with ZipFile(f"{data_dir}/{filename}", "r") as archive:
            archive.extractall(f"{data_dir}/irs-zipcode-{year}")

    print(
        f"\n The {year} Individual Income Tax ZIP Code Data from "
        f"the IRS is in the {data_dir}/irs-zipcode-{year} directory"
    )
    return data_dir


def geojson_zipcode() -> str:
    """ Download the geojson files from git repostiory:
    OpenDataDE/State-zip-code-GeoJSON """
    data_dir = create_data_dir()
    filename = "State-zip-code-GeoJSON-master.zip"
    url = "https://github.com/OpenDataDE/State-zip-code-GeoJSON/archive/master.zip"
    # Download the file if not found in folder
    if not os.path.isfile(f"{data_dir}/{filename}"):
        wget.download(url, out=data_dir)
    # unzip the archive
    if not os.path.isdir(f"{data_dir}/State-zip-code-GeoJSON-master"):
        with ZipFile(f"{data_dir}/{filename}", "r") as archive:
            archive.extractall(f"{data_dir}")

    print(
        "\n The GeoJSON files for the US zipcode boundaries from "
        "OpenDataDE/State-zip-code-GeoJSON are in "
        f"{data_dir}/State-zip-code-GeoJSON-master directory"
    )
    return data_dir


if __name__ == "__main__":
    irs_zipcode(2017)
    geojson_zipcode()
