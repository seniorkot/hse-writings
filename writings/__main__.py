from writings import data_former
from writings.schedule import Schedule

if __name__ == "__main__":
    students = data_former.get_students()
    teachers = data_former.get_teachers()
    results = []
    for i in range(data_former.get_results_spreadsheet_len()):
        results.append(data_former.get_results(i))
    schedule = Schedule(students, teachers, results)
    data_former.post_results(schedule.get_output())
