import asyncio
import functools
import os
import random
import string
import subprocess

from flask_login import current_user
from quart import Blueprint, jsonify, request

from app import db
from app.models import Problem, Submission
from app.helper import call_child

CheckerBlueprint = Blueprint('checker', __name__)


def check_script(filename, test, max_time):
    test_files = os.listdir('cases/' + test)
    test_files.remove('correct.py')
    for i, fname in enumerate(test_files):
        test_file = f"cases/{test}/{fname}"
        user = None

        try:
            user = call_child(filename, test_file, max_time)
        except subprocess.TimeoutExpired:
            return {'status': 400, 'err': 'Timed out.'}
        except subprocess.CalledProcessError as e:
            return {'status': 406, 'stdout': e.stderr.decode().strip()}
        
        result = call_child(f'cases/{test}/correct.py', test_file)
        if user != result:
            return {'status': 400, 'err': {
                'expected': result,
                'output': user,
                'maxtest': len(test_files),
                'input': open(f"cases/{test}/{fname}").read()
            }, 'score': i}
    return {'status': 200, 'message': 'OK', 'score': len(test_files)}


@CheckerBlueprint.route('/check', methods=['POST'])
async def check():
    files = await request.files
    if 'file' not in files:
        return jsonify({'status': 400, 'err': "Please upload a file."})

    file = files['file']
    if file.filename == '':
        return jsonify({'status': 400, 'err': "Please upload a file."})

    test_name, extension = os.path.splitext(file.filename)
    if extension != '.py':
        return jsonify({'status': 400, 'err': "Only python."})

    problem_db = Problem.query.filter_by(test_folder=test_name).first()
    if not problem_db:
        return jsonify({'status': 400, 'err': "No test with that name."})

    dirname = f'script/{current_user.username}'
    filename = test_name + ' - ' + ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=6)) + '.py'
    save_path = f'{dirname}/{filename}'

    if not os.path.exists(dirname):
        os.mkdir(dirname)
    file.save(save_path)

    result = await asyncio.get_running_loop().run_in_executor(
        None,
        functools.partial(check_script, save_path, test_name, problem_db.max_time)
    )

    if result['status'] == 406:
        os.unlink(save_path)
        return jsonify(result)

    user_submissions = [s for s in current_user.submissions if s.problem_id == problem_db.id]
    user_submissions.sort(key=lambda x: x.score, reverse=True)
    best = None
    if user_submissions:
        best = user_submissions[0]

    submit_db = True
    if best and best.score > result['score']:
        os.unlink(save_path)
        submit_db = False

    if submit_db:
        user_submission = Submission(score=result['score'], file=save_path, problem=problem_db, user=current_user)
        if best:
            current_user.score -= best.score
        current_user.score += result['score']

        db.session.add(user_submission)
        db.session.commit()

    return jsonify(result)
