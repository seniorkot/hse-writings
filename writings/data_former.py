import os
import json
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials


# Load spreadsheets config
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                       'config', 'spreadsheets.json')) as _file:
    _cfg = json.load(_file)

# Client instance
_client = None


def _get_client():
    """
    Login to Google API using OAuth2 credentials and
    return authorized client instance.

    Returns:
        A :class:`~gspread.Client` instance.
    """
    global _client
    if not isinstance(_client, gspread.Client):
        scope = ["https://spreadsheets.google.com/feeds",
                 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file",
                 "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials \
            .from_json_keyfile_name("config/credentials.json", scope)
        _client = gspread.authorize(credentials)
    return _client


def _get_students_spreadsheet():
    """
    Open students spreadsheet defined in spreadsheets config file.

    Returns:
        A :class:`~gspread.models.Spreadsheet` instance.

    Raises:
        gspread.SpreadsheetNotFound: if no spreadsheet with specified in config
                                     file `title` is found.
    """
    return _get_client().open_by_key(_cfg['spreadsheet-students']['key'])


def _get_students_spreadsheet_len():
    """
    Returns:
        Number of worksheets in students spreadsheet.
    """
    return len(_get_students_spreadsheet().worksheets())


def _get_teachers_spreadsheet():
    """
    Open teachers spreadsheet defined in spreadsheets config file.

    Returns:
        A :class:`~gspread.models.Spreadsheet` instance.

    Raises:
        gspread.SpreadsheetNotFound: if no spreadsheet with specified in config
                                     file `title` is found.
    """
    return _get_client().open_by_key(_cfg['spreadsheet-teachers']['key'])


def _get_teachers_spreadsheet_len():
    """
    Returns:
        Number of worksheets in teachers spreadsheet.
    """
    return len(_get_teachers_spreadsheet().worksheets())


def _get_results_spreadsheet():
    """
    Open results spreadsheet defined in spreadsheets config file.

    Returns:
        A :class:`~gspread.models.Spreadsheet` instance.

    Raises:
        gspread.SpreadsheetNotFound: if no spreadsheet with specified in config
                                     file `title` is found.
    """
    return _get_client().open_by_key(_cfg['spreadsheet-results']['key'])


def _get_results_spreadsheet_len():
    """
    Returns:
        Number of worksheets in results spreadsheet.
    """
    return len(_get_results_spreadsheet().worksheets())


def get_students(sheet_index=None):
    """
    Collect data from students spreadsheet and return specific sheet as
    pandas DataFrame object.

    Args:
        sheet_index (int):
            Sheet index. Optional.
            If None - function returns data from the last sheet.

    Returns:
        A :class:`~pandas.frame.DataFrame` instance.
    """
    spreadsheet = _get_students_spreadsheet()
    if sheet_index is None:
        sheet_index = len(spreadsheet.worksheets()) - 1
    df = pd.DataFrame(spreadsheet.get_worksheet(sheet_index).get_all_records())
    df_id = _cfg['spreadsheet-students']['id-col']
    if df_id is not None:
        df.set_index(df_id, inplace=True)
    return df


def get_teachers(sheet_index=None):
    """
    Collect data from teachers spreadsheet and return specific sheet as
    pandas DataFrame object.

    Args:
        sheet_index (int):
            Sheet index. Optional.
            If None - function returns data from the last sheet.

    Returns:
        A :class:`~pandas.frame.DataFrame` instance.
    """
    spreadsheet = _get_teachers_spreadsheet()
    if sheet_index is None:
        sheet_index = len(spreadsheet.worksheets()) - 1
    df = pd.DataFrame(spreadsheet.get_worksheet(sheet_index).get_all_records())
    df_id = _cfg['spreadsheet-teachers']['id-col']
    if df_id is not None:
        df.set_index(df_id, inplace=True)
    return df


def get_results(sheet_index=None):
    """
    Collect data from results spreadsheet and return specific sheet as
    pandas DataFrame object.

    Args:
        sheet_index (int):
            Sheet index. Optional.
            If None - function returns data from the last sheet.

    Returns:
        A :class:`~pandas.frame.DataFrame` instance.
    """
    spreadsheet = _get_results_spreadsheet()
    if sheet_index is None:
        sheet_index = len(spreadsheet.worksheets()) - 1
    df = pd.DataFrame(spreadsheet.get_worksheet(sheet_index).get_all_records())
    df_id = _cfg['spreadsheet-results']['id-col']
    if df_id is not None:
        df.set_index(df_id, inplace=True)
    return df
