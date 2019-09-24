"""
This module contains Schedule class for forming students schedule
according to input data: list of students, list of teachers and previous
sessions.
"""

import pandas as pd


class Schedule(object):
    """
    An instance of this class can form new schedule in accordance with previous
    sessions.

    :param students: A :class:`~pandas.frame.DataFrame` instance with
                     students list.
    :param teachers: A :class:`~pandas.frame.DataFrame` instance with
                     teachers list.
    :param session: A list of :class:`~pandas.frame.DataFrame` instances with
                    previous sessions.
    """

    def __init__(self,
                 students: pd.DataFrame,
                 teachers: pd.DataFrame,
                 *sessions: pd.DataFrame):
        self.__students = students
        self.__teachers = teachers

        # Create filled with zeros DataFrame with
        # available teachers & prepared students
        self.__scheme = pd.DataFrame(0, index=students.index,
                                     columns=teachers.index)
        for index, row in self.__teachers.iterrows():
            if row.all() == 0:
                self.__scheme.drop(columns=index, inplace=True)

        # Fill prepared DataFrame with values from previous sessions
        for session in sessions:
            session = session[teachers.index]
            for teacher in list(session[teachers.index]):
                session_teacher = session[teacher]
                for student in session_teacher[
                        session_teacher.str.strip().astype(bool)]:
                    self.__scheme.iloc[
                        Schedule.__extract_id(student)][teacher] += 1

    @staticmethod
    def __extract_id(name: str) -> int:
        """
        Static method to extract ID from input string.

        Args:
            name (str): String in format 'Name (ID: 111)'

        Returns:
            Extracted ID in int format.
        """
        try:
            return int(name.split('(ID: ')[1][:-1])
        except (IndexError, ValueError):
            raise InvalidInputDataException(
                'Cannot extract ID from \'' + name
                + '\'. Required format is \'Name (ID: 111)\'.') from None


class InvalidInputDataException(Exception):
    """Raised when the function or method input data is incorrect"""
    pass