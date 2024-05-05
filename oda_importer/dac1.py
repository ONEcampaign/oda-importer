import pandas as pd

from oda_importer.common import api_response_to_df, logger
from oda_importer.query_builder import QueryBuilder
from oda_importer.schemas.dac1_translation import convert_to_dotstat_codes
from oda_importer.schemas.schema_tools import (
    read_schema_translation,
    get_dtypes,
    preprocess,
)

DATAFLOW_ID: str = "DSD_DAC1@DF_DAC1"


def download_dac1(
    start_year: int | None = None,
    end_year: int | None = None,
    download_filters: dict | None = None,
    pre_process: bool = True,
    dotstat_codes: bool = True,
) -> pd.DataFrame:
    """
    Download the DAC1 data from the API.

    Args:
        start_year (int): The start year of the data to download. Optional
        end_year (int): The end year of the data to download. Optional
        download_filters (dict): Optional filters to pass to the download.
        pre_process (bool): Whether to preprocess the data. Defaults to True.
        Preprocessing makes it comply with the .stat schema.
        dotstat_codes (bool): Whether to convert the donor codes to the .stat schema.

    Returns:
        pd.DataFrame: The DAC1 data.

    """
    # Load the translation schema from .stat  to the new explorer
    schema_translation = read_schema_translation()

    # Get a data types dictionary
    data_types = get_dtypes(schema=schema_translation)

    # Set read csv options
    df_options = {
        "na_values": ("_Z", "nan"),
        "keep_default_na": True,
        "dtype": data_types,
    }

    # Inform download is about to start
    logger.info("Downloading DAC1 data. This may take a while...")

    # instantiate the query builder
    qb = QueryBuilder(dataflow_id=DATAFLOW_ID)

    # Optionally set filters
    if download_filters:
        filter_str = qb.build_dac1_filter(**download_filters)
        qb.set_filter(filter_str)

    # Get the url
    url = qb.set_time_period(start=start_year, end=end_year).build_query()

    # Get the dataframe
    df = api_response_to_df(url=url, read_csv_options=df_options)

    # Preprocess the data
    if pre_process:
        df = preprocess(df=df, schema_translation=schema_translation)
        if dotstat_codes:
            df = convert_to_dotstat_codes(df)
    else:
        if dotstat_codes:
            raise ValueError("Cannot convert to dotstat codes without preprocessing.")

    # Return the dataframe
    logger.info("Data downloaded correctly.")

    return df
