import os
import re
import json
import gspread
import datetime
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials


# Load spreadsheets config
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                       'config', 'spreadsheets.json'),
          encoding='utf-8') as _file:
    _cfg = json.load(_file)

# Client instance
_client = None


def _get_client() -> gspread.Client:
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
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            os.path.join(os.path.abspath(os.path.dirname(__file__)),
                         'config', 'credentials.json'), scope)
        _client = gspread.authorize(credentials)
    return _client


def _get_students_spreadsheet() -> gspread.models.Spreadsheet:
    """
    Open students spreadsheet defined in spreadsheets config file.

    Returns:
        A :class:`~gspread.models.Spreadsheet` instance.

    Raises:
        gspread.exceptions.APIError: if no spreadsheet is found
                                     or unauthenticated.
    """
    return _get_client().open_by_key(_cfg['spreadsheet-students']['key'])


def get_students_spreadsheet_len() -> int:
    """
    Returns:
        Number of worksheets in students spreadsheet.
    """
    return len(_get_students_spreadsheet().worksheets())


def _get_teachers_spreadsheet() -> gspread.models.Spreadsheet:
    """
    Open teachers spreadsheet defined in spreadsheets config file.

    Returns:
        A :class:`~gspread.models.Spreadsheet` instance.

    Raises:
        gspread.exceptions.APIError: if no spreadsheet is found
                                     or unauthenticated.
    """
    return _get_client().open_by_key(_cfg['spreadsheet-teachers']['key'])


def get_teachers_spreadsheet_len() -> int:
    """
    Returns:
        Number of worksheets in teachers spreadsheet.
    """
    return len(_get_teachers_spreadsheet().worksheets())


def _get_results_spreadsheet() -> gspread.models.Spreadsheet:
    """
    Open results spreadsheet defined in spreadsheets config file.

    Returns:
        A :class:`~gspread.models.Spreadsheet` instance.

    Raises:
        gspread.exceptions.APIError: if no spreadsheet is found
                                     or unauthenticated.
    """
    return _get_client().open_by_key(_cfg['spreadsheet-results']['key'])


def get_results_spreadsheet_len() -> int:
    """
    Returns:
        Number of worksheets in results spreadsheet.
    """
    return len(_get_results_spreadsheet().worksheets())


def _get_records(spreadsheet: gspread.models.Spreadsheet,
                 spreadsheet_name: str,
                 sheet_index: int = None,) -> pd.DataFrame or None:
    """
    Collect data from specified spreadsheet and return a sheet as
    pandas DataFrame object.

    Args:
        spreadsheet (:class:`~gspread.models.Spreadsheet`):
            Opened spreadsheet.
        spreadsheet_name (str):
            Spreadsheet name from spreadsheets.json file.
        sheet_index (int):
            Sheet index. Optional.
            If None - function returns data from the last sheet.

    Returns:
        A :class:`~pandas.frame.DataFrame` instance.
    """
    if sheet_index is None:
        sheet_index = len(spreadsheet.worksheets()) - 1
    try:
        df = pd.DataFrame(spreadsheet.get_worksheet(sheet_index)
                          .get_all_records())
    except IndexError:
        return None
    df_id = _cfg[spreadsheet_name]['id-col']
    if df_id is not None:
        df.set_index(df_id, inplace=True)
    return df.drop(columns='', errors='ignore')


def get_students(sheet_index: int = None) -> pd.DataFrame or None:
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
    return _get_records(_get_students_spreadsheet(),
                        'spreadsheet-students',
                        sheet_index)


def get_teachers(sheet_index: int = None) -> pd.DataFrame or None:
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
    return _get_records(_get_teachers_spreadsheet(),
                        'spreadsheet-teachers',
                        sheet_index)\
        .reindex(columns=_cfg['spreadsheet-teachers']['columns'])


def get_results(sheet_index: int = None) -> pd.DataFrame or None:
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
    rs = _get_records(_get_results_spreadsheet(),
                      'spreadsheet-results',
                      sheet_index)
    rs.columns = [re.sub(' [0-9]+/[0-9]+', '', col) for col in rs.columns]
    return rs


def post_results(schedule):
    """
    Post schedule to the results spreadsheet.

    Args:
        schedule:
            Formed schedule.

    """
    now = datetime.datetime.now()
    spreadsheet = _get_results_spreadsheet()
    sheet = spreadsheet.add_worksheet(now.strftime("%d.%m %H:%M"),
                                      rows=1000, cols=100)
    spreadsheet.values_update(sheet.title + '!A1:CV1000',
                              params={'valueInputOption': 'USER_ENTERED'},
                              body={'values': schedule,
                                    'majorDimension': 'COLUMNS'})
