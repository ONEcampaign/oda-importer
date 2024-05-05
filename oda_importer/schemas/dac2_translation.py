import pandas as pd

from oda_importer.common import ImporterPaths
from oda_importer.schemas.dac1_translation import prices_mapping
from oda_importer.schemas.schema_tools import map_area_codes, map_amount_type_codes
from oda_importer.schemas.xml_tools import (
    parse_xml,
    extract_dac_to_area_codes,
    read_mapping,
)

DAC2_TRANSLATION_SCHEMA_URL = (
    "https://stats.oecd.org/FileView2.aspx?IDFile=997ad7fb-48f1-4046-945d-067dc5bec7de"
)

MAPPINGS = {
    "dac2_codes_area": ImporterPaths.schemas / "dac2_codes_area.json",
    "area_code_corrections": ImporterPaths.schemas / "area_code_corrections.json",
}


def update_dac2_translation_mappings():
    """Pipeline to update the DAC1 translation mappings"""
    xml_data = parse_xml(xml_url=DAC2_TRANSLATION_SCHEMA_URL)["Structures"]

    # oecd dac donor codes to area codes
    extract_dac_to_area_codes(xml_dict=xml_data, filename=MAPPINGS["dac2_codes_area"])


def area_code_mapping() -> dict:
    """Reads the area code mapping."""
    return read_mapping(
        MAPPINGS["dac2_codes_area"],
        keys_as_int=True,
        update=update_dac2_translation_mappings,
    ) | read_mapping(
        MAPPINGS["area_code_corrections"],
        keys_as_int=True,
        update=update_dac2_translation_mappings,
    )


def convert_to_dotstat_codes(df: pd.DataFrame) -> pd.DataFrame:
    # Get the area codes
    area_codes = area_code_mapping()

    # Prices mapping
    prices_codes = {v: k for k, v in prices_mapping().items()}

    # Map the donor codes
    df = map_area_codes(df, area_code_mapping=area_codes)

    # Map region codes
    df = map_area_codes(
        df,
        area_code_mapping=area_codes,
        source_column="recipient_code",
        target_column="recipient_code",
    )

    # Map the prices codes
    df = map_amount_type_codes(
        df,
        prices_mapping=prices_codes,
        source_column="data_type_code",
        target_column="data_type_code",
    )

    return df
