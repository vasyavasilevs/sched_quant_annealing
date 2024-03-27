# Так получилось, что преподаватель n1 не может вести лекции в среду, а n2 в понедельник, 
# а n3 никак не может работать по субботам, n4, n5 – не могут вести занятия по вторникам. 
# Воскресенье - день без занятий.
SUBJECT_TO_MISSED_DAY = {
    0: 2,#n1
    1: 2,#n1
    2: 0,#n2
    3: 0,#n2
    4: 5,#n3
    5: 5,#n3
    6: 1,#n4
    7: 1,#n4
    8: 1,#n5
    9: 1,#n5
}

DURATION = 1 # 1 hour lesson duration
ALL_SUBJ_AT_DAY_THRESHOLD = 6
THIS_SUBJ_AT_DAY_THRESHOLD = 2
THIS_SUBJ_TWO_WEEKS_THRESHOLD = 4
TEACHER_HOURS_PER_WEEK_TRESHOLD = 20

WEEK_DAYS = 6
WEEKS = 2
HOURS = 8
GROUPS = 2
SUBJECTS = 10
TEACHERS = 5

T_MAX = WEEK_DAYS * WEEKS * HOURS
JOB_MAX = GROUPS * SUBJECTS
DIM = T_MAX * JOB_MAX


def encode_to_index(week, day, hour, group, subject) -> int:
    return (group * SUBJECTS + subject) * T_MAX + (week * WEEK_DAYS + day) * HOURS + hour


def decode_job(job: int) -> tuple[int, int]:
    group = job // SUBJECTS
    subject = job - group * SUBJECTS
    return group, subject


def decode_time(time: int) -> tuple[int, int, int]:
    week_and_day = time // HOURS
    week = week_and_day // WEEK_DAYS
    day = week_and_day - week * WEEK_DAYS
    hour = time - week_and_day * HOURS
    return week, day, hour


def decode_index(idx: int) -> tuple[int, int, int, int, int]:
    group_and_subject = idx // T_MAX
    group, subject = decode_job(group_and_subject)

    time = idx - group_and_subject * T_MAX
    week, day, hour = decode_time(time)
    return week, day, hour, group, subject


def decode_to_job_and_time(idx: int) -> tuple[int, int]:
    week, day, hour, group, subject = decode_index(idx)
    return group * SUBJECTS + subject, (week * WEEK_DAYS + day) * HOURS + hour
