# randomized-seating

This script produces a CSV that contains a random assignment of students in your course to seats in a lecture room, for the purposes of administering exams. It works even if your course has multiple lecture sections, each of which is in a different room (in fact, it was created for such a course – DSC 10 in Fall 2022). Credit goes to Glenn Tesler in the Math department, who hosts the necessary seating charts on his [website](https://mathweb.ucsd.edu/~gptesler/assigningseats.html). In fact, his site has videos on how to do essentially the same thing, and his videos are much more comprehensive, though the techniques there are not as automated. 

_Disclaimer: This has only ever been tested with one course, so something is bound to go wrong. If something is clearly broken, [submit an issue](https://github.com/dsc-courses/randomized-seating/issues) or let us know at rampure@ucsd.edu!_

How to use this script:
- Add your standard `.xls` blink roster in `rosters/`. If your course has multiple sections, make sure the roster has them all.
    - If you are teaching a multi-section course and you want a student to "swap" sections – for instance, they are enrolled in lecture section A00 but need to take the exam with lecture section B00 – list them in the CSV file `rosters/swaps.csv`. The CSV file should have four columns, `"Name"`, `"PID"`, `"Original"`, and `"New"`. For instance, one row may look like `King Triton,A01234567,A00,C00`, denoting that student King Triton needs to be assigned to a seat with section C00 despite being enrolled in section A00.
    - If there are students that you don't want to assign a room to – say, if they have OSD accommodations and will be taking the exam in a separate room – list them in the CSV file `rosters/exclude.csv`. The CSV file should have two columns, `"Name"` and `"PID"`.
- Edit the details for your course in `config.json`. An example (complicated) configuration file is provided in this repo.
    - Find links to your rooms' seating charts [here](https://mathweb.ucsd.edu/~gptesler/assigningseats.html) (click Classroom seat spreadsheets).
    - Manually change the `"seed"` in between exams, but keep it fixed when re-running the script for a particular exam, so that you get the same assignments each time.
    - Remove the `"swaps"` and `"exclude"` entries if you're not using those features.
    - The `"room"` names you pick can be anything.
    - The `"exports"` path is where your final spreadsheets will be stored.
- Run `python run.py`. After doing so, in a subfolder of `exports`, you will see two CSV files:
    - `seating-for-mailing.csv`, which contains each student's name, email, PID, lecture section, and assigned seat. We typically upload this CSV to Google Sheets and use it to run a [mail merge](https://yamm.com) that sends each student an email with their seat info (let us know if you want tips on how to do this!).
    - `seating-for-posting.csv`, which contains the same information as `seating-for-mailing.csv` but without student names and emails. We typically upload this CSV to Google Sheets and post it for students to look up their seat assignment in the event they can't find it in their email.

Note: The script _tries_ to take into account the orientation of each desk – that is, the fact that some desks are right-handed and some are left-handed. If there are fewer students in the section than right-handed seats, then all students are assigned to a right-handed seat and you can tell left-handed students to sit in the left-handed seat closest to them. If not, then students are assigned totally randomly, and right-handed students may end up in left-handed seats and vice versa. In this case, you can tell all students to sit in the seat closest to them that matches their writing orientation (this sounds chaotic, but in practice it wasn't).

Roadmap:
- The script currently requires one to enter the URL of their room's seating chart, though this could be automated.
- The script doesn't work in the case where multiple sections need to take an exam in the same room (this could happen in the case of shared final exams, perhaps).
