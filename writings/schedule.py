"""
This module contains Schedule class for forming students schedule
according to input data: list of students, list of teachers and previous
sessions.
"""

import pandas as pd
import numpy as np


class Schedule(object):
    """
    An instance of this class can form new schedule in accordance with previous
    sessions.

    :param students: A :class:`~pandas.frame.DataFrame` instance with
                     students list.
    :param teachers: A :class:`~pandas.frame.DataFrame` instance with
                     teachers list.
    :param sessions: A list of :class:`~pandas.frame.DataFrame` instances with
                     previous sessions.
    """

    def __init__(self,
                 students: pd.DataFrame,
                 teachers: pd.DataFrame,
                 sessions: list):
        self.__students = students
        self.__teachers = teachers
        self.__sessions = \
            [session for session in sessions if session is not None]
        self.__schedule = None

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
            for teacher in teachers.index:
                session_teacher = session[teacher]
                for student in session_teacher.replace('', np.nan).dropna():
                    try:
                        self.__scheme.loc[student][teacher] += 1
                    except KeyError:
                        pass

        # Generate schedule
        self.__generate_schedule()

    def __generate_schedule(self):
        # Get students count & total desired and maximum
        total = len(self.__students)
        desired = maximum = 0
        for _, row in self.__teachers.iterrows():
            desired += row[-2]
            maximum += row[-1]

        # Create schedule as dictionary with teacher keys
        # and empty list values
        self.__schedule = dict()
        for teacher in self.__teachers.index:
            self.__schedule[teacher] = []

        # Choose strategy & fill in the schedule
        if total >= maximum:
            for i in range(maximum):
                self.__fill_student(self.__students.iloc[i].name, 1, False)
            if total > maximum:
                self.__schedule['Остальные'] = \
                    self.__students.iloc[maximum:total].index.to_list()
        elif total >= desired:
            for i in range(desired):
                self.__fill_student(self.__students.iloc[i].name, 1, True)
            if total > desired:
                proportion = total / maximum
                for i in range(desired, total):
                    self.__fill_student(self.__students.iloc[i].name,
                                        proportion, False)
        else:
            proportion = total / desired
            for i in range(total):
                self.__fill_student(self.__students.iloc[i].name,
                                    proportion, True)

    def __fill_student(self,
                       student_id: int,
                       proportion: float,
                       desired: bool):
        # Check previous teacher
        prev_teacher = None
        for col in self.__sessions[-1].columns:
            if student_id in self.__sessions[-1][col].values:
                prev_teacher = col

        # Fill in the schedule with proportion
        if prev_teacher:
            scheme = self.__scheme.loc[student_id]. \
                drop(columns=prev_teacher).sort_values().items()
        else:
            scheme = self.__scheme.loc[student_id].sort_values().items()

        for teacher, value in scheme:
            if desired:
                std_count = int(self.__teachers.loc[teacher][-2] * proportion)
            else:
                std_count = int(self.__teachers.loc[teacher][-1] * proportion)
            if len(self.__schedule[teacher]) < std_count:
                self.__schedule[teacher].append(student_id)
                return

        # Fill in the schedule without proportion
        for teacher, value in scheme:
            if desired \
                    and len(self.__schedule[teacher]) < \
                    self.__teachers.loc[teacher][-2] \
                    or len(self.__schedule[teacher]) < \
                    self.__teachers.loc[teacher][-1]:
                self.__schedule[teacher].append(student_id)
                return

    @staticmethod
    def __extract_id(name: str) -> int:
        """
        Static method to extract ID from input string.

        Args:
            name (str): String in format 'Name (ID: 111)'

        Returns:
            Extracted ID in int format.

        Raises:
            writings.schedule.InvalidInputDataException: if string is invalid
        """
        try:
            return int(name.split('(ID: ')[1][:-1])
        except (IndexError, ValueError):
            raise InvalidInputDataException(
                'Cannot extract ID from \'' + name
                + '\'. Required format is \'Name (ID: 111)\'.') from None

    def __get_student_str(self, std_id: int) -> str:
        """
        Return specific string with student name & ID to fill
        results spreadsheet.

        Args:
            std_id (int): Student ID

        Returns:
            String in form 'Name (ID: 111)'

        Raises:
            writings.schedule.InvalidInputDataException: if no such student in
                                                         current schedule
        """
        try:
            std_name = self.__students.iloc[std_id][0]
        except IndexError:
            raise InvalidInputDataException(
                'Cannot find student with ID ' + str(std_id)) from None
        return std_name + ' (ID: ' + str(std_id) + ')'


class InvalidInputDataException(Exception):
    """Raised when the function or method input data is incorrect"""
    pass
