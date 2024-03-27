from collections import defaultdict
from dwave.system import LeapHybridSampler
from dimod import BinaryQuadraticModel
from pprint import pprint
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from task_params import *
import numpy as np

LAGRANGE_FREE_DAY = 70
LAGRANGE_NON_OVERLAPPING_LESSONS_GROUP = 80
LAGRANGE_NON_OVERLAPPING_LESSONS_TEACHER = 80
LAGRANGE_SUBJ_DAY = 2
LAGRANGE_DAY = 1
LAGRANGE_SUBJ_TWO_WEEKS = 0.4
LAGRANGE_TEACHER_WEEK = 0.3

GLOBAL_OFFSET = 0
Q = defaultdict(int)

# Penalties for teachers-non-working days

for group in range(GROUPS):
    for week in range(WEEKS):
        for subject in SUBJECT_TO_MISSED_DAY:
            day = SUBJECT_TO_MISSED_DAY[subject]
            for hour in range(HOURS):
                idx = encode_to_index(week, day, hour, group, subject)
                Q[idx, idx] += LAGRANGE_FREE_DAY


# Penalties for overlapping-lessons-for-group

for group in range(GROUPS):
    for week in range(WEEKS):
        for day in range(WEEK_DAYS):
            for hour in range(HOURS):

                for subject1 in range(SUBJECTS):
                    for subject2 in range(subject1 + 1, SUBJECTS):
                        idx = encode_to_index(week, day, hour, group, subject1)
                        jdx = encode_to_index(week, day, hour, group, subject2)
                        Q[idx, jdx] += LAGRANGE_NON_OVERLAPPING_LESSONS_GROUP


# Penalties for overlapping-lessons-for-teacher

for week in range(WEEKS):
    for day in range(WEEK_DAYS):
        for hour in range(HOURS):
            for teacher in range(TEACHERS):

                for subject1 in range(2 * teacher, 2 * teacher + 2):
                    for subject2 in range(2 * teacher, 2 * teacher + 2):
                        for group1 in range(GROUPS):
                            for group2 in range(group1 + 1, GROUPS):
                                idx = encode_to_index(week, day, hour, group1, subject1)
                                jdx = encode_to_index(week, day, hour, group2, subject2)
                                Q[idx, jdx] += LAGRANGE_NON_OVERLAPPING_LESSONS_TEACHER


# Penalties for 2-hours-subject-per-day limit

for group in range(GROUPS):
    for subject in range(SUBJECTS):
        for week in range(WEEKS):
            for day in range(WEEK_DAYS):
                GLOBAL_OFFSET += LAGRANGE_SUBJ_DAY * THIS_SUBJ_AT_DAY_THRESHOLD ** 2

                for hour in range(HOURS):
                    idx = encode_to_index(week, day, hour, group, subject)
                    Q[idx, idx] += LAGRANGE_SUBJ_DAY * (DURATION ** 2 - 2 * DURATION * THIS_SUBJ_AT_DAY_THRESHOLD)

                for hour1 in range(HOURS):
                    for hour2 in range(hour1 + 1, HOURS):
                        idx = encode_to_index(week, day, hour1, group, subject)
                        jdx = encode_to_index(week, day, hour2, group, subject)
                        # Q will be upper triangular
                        Q[idx, jdx] += LAGRANGE_SUBJ_DAY * (2 * DURATION ** 2)


# Penalties for 6-hours-working-day limit

for group in range(GROUPS):
    for week in range(WEEKS):
        for day in range(WEEK_DAYS):
            GLOBAL_OFFSET += LAGRANGE_DAY * ALL_SUBJ_AT_DAY_THRESHOLD ** 2

            for subject in range(SUBJECTS):
                for hour in range(HOURS):
                    idx = encode_to_index(week, day, hour, group, subject)
                    Q[idx, idx] += LAGRANGE_DAY * (DURATION ** 2 - 2 * DURATION * ALL_SUBJ_AT_DAY_THRESHOLD)

            for subject1 in range(SUBJECTS):
                for subject2 in range(subject1 + 1, SUBJECTS):
                    for hour1 in range(HOURS):
                        for hour2 in range(hour1 + 1, HOURS):
                            idx = encode_to_index(week, day, hour1, group, subject1)
                            jdx = encode_to_index(week, day, hour2, group, subject2)
                            # Q will be upper triangular
                            Q[idx, jdx] += LAGRANGE_DAY * (2 * DURATION ** 2)


# Penalties for 4-lessons-per-2-week limit

for group in range(GROUPS):
    for subject in range(SUBJECTS):
        GLOBAL_OFFSET += LAGRANGE_SUBJ_TWO_WEEKS * THIS_SUBJ_TWO_WEEKS_THRESHOLD ** 2

        for week in range(WEEKS):
            for day in range(WEEK_DAYS):
                for hour in range(HOURS):
                    idx = encode_to_index(week, day, hour, group, subject)
                    Q[idx, idx] += LAGRANGE_SUBJ_TWO_WEEKS * (DURATION ** 2 - 2 * DURATION * THIS_SUBJ_TWO_WEEKS_THRESHOLD)

        for week1 in range(WEEKS):
            for week2 in range(week1 + 1, WEEKS):
                for day1 in range(WEEK_DAYS):
                    for day2 in range(day1 + 1, WEEK_DAYS):
                        for hour1 in range(HOURS):
                            for hour2 in range(hour1 + 1, HOURS):
                                idx = encode_to_index(week1, day1, hour1, group, subject)
                                jdx = encode_to_index(week2, day2, hour2, group, subject)
                                # Q will be upper triangular
                                Q[idx, jdx] += LAGRANGE_SUBJ_TWO_WEEKS * (2 * DURATION ** 2)


# Penalties for teachers-working-week limit             

for week in range(WEEKS):
    for teacher in range(TEACHERS):
        GLOBAL_OFFSET += LAGRANGE_TEACHER_WEEK * TEACHER_HOURS_PER_WEEK_TRESHOLD ** 2

        for subject in range(2 * teacher, 2 * teacher + 2):
            for group in range(GROUPS):
                for day in range(WEEK_DAYS):
                    for hour in range(HOURS):
                        idx = encode_to_index(week, day, hour, group, subject)
                        Q[idx, idx] += LAGRANGE_TEACHER_WEEK * (DURATION ** 2 - 2 * DURATION * TEACHER_HOURS_PER_WEEK_TRESHOLD)

        for subject1 in range(2 * teacher, 2 * teacher + 2):
            for subject2 in range(2 * teacher, 2 * teacher + 2):
                for group1 in range(GROUPS):
                    for group2 in range(group1 + 1, GROUPS):
                        for day1 in range(WEEK_DAYS):
                            for day2 in range(day1 + 1, WEEK_DAYS):
                                for hour1 in range(HOURS):
                                    for hour2 in range(hour1 + 1, HOURS):
                                        idx = encode_to_index(week, day1, hour1, group1, subject1)
                                        jdx = encode_to_index(week, day2, hour2, group2, subject2)
                                        # Q will be upper triangular
                                        Q[idx, jdx] += LAGRANGE_TEACHER_WEEK * (2 * DURATION ** 2)


VALS = list(Q.values())
print(VALS)
print('Dictionary length:', len(Q))

API_KEY = " "

bqm = BinaryQuadraticModel.from_qubo(Q, offset=GLOBAL_OFFSET)

print("\nSending problem to hybrid sampler...")
sampler = LeapHybridSampler(token=API_KEY)
results = sampler.sample(bqm, label='Shedule')

# Get the results
smpl = results.first.sample

# Graphics
print("\nBuilding schedule and checking constraints...\n")
sched: list[tuple[int, int]] = [
    decode_to_job_and_time(idx)
    for idx in range(DIM)
    if smpl[idx] == 1
]

with open('schedule.py', mode='w') as f:
    f.write("SCHED =" + str(sched))

pprint(sched)

x, y = zip(*sched)
fig = plt.figure(figsize=(30, 10))
ax = fig.add_subplot(111)
ax.scatter(y, x)
width = 1
height = 1

subject_to_color = {
    0: (1, 0, 0),     
    1: (1, 0, 0, 0.5),
    2: (0, 1, 0),     
    3: (0, 1, 0, 0.5),
    4: (0.5, 0.5, 0), 
    5: (0.5, 0.5, 0, 0.5), 
    6: (0, 0, 0),  
    7: (0, 0, 0, 0.5),
    8: (1, 0, 1),     
    9: (1, 0, 1, 0.5) 
}


for a_y, a_x in sched:
    subject = a_y % SUBJECTS
    c = subject_to_color[subject]
    ax.add_patch(Rectangle(
        xy=(a_x - width, a_y - height / 2), width=width, height=height,
        linewidth=1, color=c, fill=True))


ax.axis('equal')
ax.set_xticks(range(T_MAX))
ax.set_yticks(range(JOB_MAX))
ax.set_xlabel("Time slots")
ax.set_ylabel("Subjects")

plt.grid(True, which='both', linestyle='-', linewidth=0.5) 

x_ticks = plt.gca().get_xticks()
x_ticks_indices = np.arange(len(x_ticks))
every_eighth = x_ticks_indices[::8]

for idx, grid_line in enumerate(plt.gca().get_xgridlines()):
    if idx in every_eighth:
        grid_line.set_linewidth(1.5) 
plt.savefig("schedule.png", dpi=800)
