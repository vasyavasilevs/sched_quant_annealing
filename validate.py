from collections import defaultdict
from schedule import SCHED
from task_params import *


def check_missed_days(sched: list[tuple[int, int, int, int, int]]) -> int:
    violations_counter = 0
    for _, day, _, _, subject in sched:
        if day == SUBJECT_TO_MISSED_DAY[subject]:
            violations_counter += 1
    return violations_counter


def check_overlapping_lessons_for_group(sched: list[tuple[int, int, int, int, int]]) -> int:
    group_hour_to_workload = defaultdict(int)

    for week, day, hour, group, _ in sched:
        group_hour_id = (group, week, day, hour)
        group_hour_to_workload[group_hour_id] += 1

    return len([x for x in group_hour_to_workload.values() if x > 1])


def check_overlapping_lessons_for_teacher(sched: list[tuple[int, int, int, int, int]]) -> int:
    teacher_hour_to_workload = defaultdict(int)

    for week, day, hour, _, subject in sched:
        teacher_hour_id = (subject // 2, week, day, hour)
        teacher_hour_to_workload[teacher_hour_id] += 1

    return len([x for x in teacher_hour_to_workload.values() if x > 1])


def check_day_workload_threshold(sched: list[tuple[int, int, int, int, int]]) -> int:
    day_to_workload = defaultdict(int)

    for week, day, _, group, _ in sched:
        day_id = (group, week, day)
        day_to_workload[day_id] += 1

    return len([x for x in day_to_workload.values() if x > ALL_SUBJ_AT_DAY_THRESHOLD])


def check_subj_at_day_threshold(sched: list[tuple[int, int, int, int, int]]) -> int:
    subj_day_to_workload = {}

    for week, day, _, group, subject in sched:
        subj_day_id = (group, subject, week, day)
        if subj_day_id in subj_day_to_workload:
            subj_day_to_workload[subj_day_id] += 1
        else:
            subj_day_to_workload[subj_day_id] = 1

    return len([x for x in subj_day_to_workload.values() if x > THIS_SUBJ_AT_DAY_THRESHOLD])


def check_subj_at_two_weeks_threshold(sched: list[tuple[int, int, int, int, int]]) -> int:
    subj_to_total_workload = {}

    for _, _, _, group, subject in sched:
        subj_id = (group, subject)
        if subj_id in subj_to_total_workload:
            subj_to_total_workload[subj_id] += 1
        else:
            subj_to_total_workload[subj_id] = 1

    return len([x for x in subj_to_total_workload.values() if x != THIS_SUBJ_TWO_WEEKS_THRESHOLD])


def check_teacher_workload_threshold(sched: list[tuple[int, int, int, int, int]]) -> int:
    teacher_week_to_workload = {}

    for week, _, _, _, subject in sched:
        teacher_week_id = (subject // 2, week)
        if teacher_week_id in teacher_week_to_workload:
            teacher_week_to_workload[teacher_week_id] += 1
        else:
            teacher_week_to_workload[teacher_week_id] = 1

    return len([x for x in teacher_week_to_workload.values() if x > TEACHER_HOURS_PER_WEEK_TRESHOLD])


full_schedule = []
for job, time in SCHED:
    group, subject = decode_job(job)
    week, day, hour = decode_time(time)
    full_schedule.append((week, day, hour, group, subject))

assert len(set(full_schedule)) == len(SCHED)

print("Total lessons per two weeks:", len(full_schedule))
print("check_missed_days:", check_missed_days(full_schedule))
print("check_overlapping_lessons_for_group", check_overlapping_lessons_for_group(full_schedule))
print("heck_overlapping_lessons_for_teacher", check_overlapping_lessons_for_teacher(full_schedule));
print("check_day_workload_threshold:", check_day_workload_threshold(full_schedule))
print("check_subj_at_day_threshold:", check_subj_at_day_threshold(full_schedule))
print("check_subj_at_two_weeks_threshold:", check_subj_at_two_weeks_threshold(full_schedule))
print("check_teacher_workload_threshold:", check_teacher_workload_threshold(full_schedule))
