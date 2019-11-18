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

        # Fill prepared DataFrame with values from previous sessions
        for session in sessions:
            session = session.reindex(columns=teachers.index)
            for teacher in teachers.index:
                session_teacher = session[teacher]
                for student in session_teacher.replace('', np.nan).dropna():
                    try:
                        self.__scheme.loc[student, teacher] += 1
                    except KeyError:
                        pass

        # Generate schedule
        self.generate_schedule()

    def get_students(self) -> pd.DataFrame:
        return self.__students

    def set_students(self, students: pd.DataFrame):
        self.__students = students

    def get_teachers(self) -> pd.DataFrame:
        return self.__teachers

    def set_teachers(self, teachers: pd.DataFrame):
        self.__teachers = teachers

    def get_sessions(self) -> list:
        return self.__sessions

    def set_sessions(self, sessions: list):
        self.__sessions = sessions

    def generate_schedule(self):
        """
        Generates a schedule using information about students, teachers &
        previous sessions.
        """
        # Get students count & total desired and maximum
        total = len(self.__students)
        desired = sum(self.__teachers.iloc[:, -2])
        maximum = sum(self.__teachers.iloc[:, -1])

        # Drop teachers with zeroes
        teachers = self.__teachers.copy()
        for index, row in teachers.iterrows():
            if row.all() == 0:
                self.__scheme.drop(columns=index, inplace=True,
                                   errors='ignore')
                teachers.drop(index, inplace=True)

        # Create schedule as dictionary with teacher keys
        # and empty list values
        self.__schedule = {teacher: [] for teacher in self.__teachers.index}
        if total < desired:
            tc = 2
            while sum(teachers.iloc[:tc, -2]) < total:
                tc += 1
            self.__scheme = self.__scheme.iloc[:, :tc]

        # Choose strategy & fill in the schedule
        if total <= desired:
            for i in range(total):
                self.__fill_student(self.__students.iloc[i].name)
        else:
            for i in range(desired):
                self.__fill_student(self.__students.iloc[i].name)
            if total <= maximum:
                proportion = (total - desired) / (maximum - desired)
                for i in range(desired, total):
                    self.__fill_student(self.__students.iloc[i].name,
                                        proportion, True)
            else:
                for i in range(desired, maximum):
                    self.__fill_student(self.__students.iloc[i].name,
                                        maximum=True)
                self.__schedule['Остальные'] = \
                    self.__students.iloc[maximum:total].index.to_list()

    def __fill_student(self,
                       student_id: int,
                       proportion: float = 1.0,
                       maximum: bool = False):
        """
        Fills the schedule with a concrete student.

        Args:
            student_id (int):
                Student ID.
            proportion (float):
                Desired/maximum proportion.
            maximum (bool):
                True if all desired places were taken.
        """
        # Check previous teacher
        prev_teacher = ''
        for col in self.__sessions[-1].columns:
            if student_id in self.__sessions[-1][col].values:
                prev_teacher = col
                break

        # Extract values from the scheme for certain student
        scheme = self.__scheme.loc[student_id]. \
            drop(columns=prev_teacher, errors='ignore').\
            sort_values(kind='mergesort').items()

        # Fill in with desired values
        if not maximum:
            for teacher, value in scheme:
                if len(self.__schedule[teacher]) < \
                        self.__teachers.loc[teacher][-2]:
                    self.__schedule[teacher].append(student_id)
                    return
        # Fill in with other values till maximum
        else:
            for teacher, value in scheme:
                std_count = int((self.__teachers.loc[teacher][-2] -
                                self.__teachers.loc[teacher][-1]) * proportion)
                if proportion != 1.0:
                    std_count += 1
                if len(self.__schedule[teacher]) < std_count:
                    self.__schedule[teacher].append(student_id)
                    return

    def get_output(self) -> list:
        """
        Generates an output for posting to a spreadsheet.

        Returns:
            A list of values for each worksheet column.
        """
        output = []
        for teacher in self.__teachers.index:
            lst1 = [teacher + ' ' + str(self.__teachers.loc[teacher][-2])
                    + '/' + str(self.__teachers.loc[teacher][-1])]
            lst1.extend(str(v) for v in self.__schedule[teacher])
            lst2 = ['']
            lst2.extend(self.__students.loc[self.__schedule[teacher]].
                        iloc[:, 0].tolist())
            output.extend([lst1, lst2, ['']])
        if 'Остальные' in self.__schedule:
            lst1 = ['Остальные']
            lst1.extend(str(v) for v in self.__schedule['Остальные'])
            lst2 = ['']
            lst2.extend(self.__students.loc[self.__schedule['Остальные']].
                        iloc[:, 0].tolist())
            output.extend([lst1, lst2])
        return output
