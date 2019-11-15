import os

from app import db
from app.models import Problem


def make_problem(case, case_name, time, sample_input, sample_output, details):
    if not os.path.exists('cases/' + case):
        raise Exception("Cannot find cases path.")

    test_files = os.listdir('cases/' + case)
    test_files.remove('correct.py')
    test_len = len(test_files)

    prob = Problem(
        name=case_name,
        test_folder=case,
        max_score=test_len,
        max_time=time,
        sample_input=sample_input,
        sample_output=sample_output,
        details=details)
    db.session.add(prob)
    db.session.commit()
