from app.models import Problem
from quart import render_template, Blueprint, flash, url_for, redirect, request, abort
from flask_login import login_required, current_user
from app.helper import make_problem, call_child, make_random_str
import os, subprocess, shutil, traceback, html
TaskBlueprint = Blueprint('task', __name__)


def test_checker(files, max_time):
    if not os.path.exists('tmp'):
        os.mkdir('tmp')
    tmpdir = 'tmp/' + make_random_str(6)
    os.mkdir(tmpdir)
    for f in files:
        f.save(f'{tmpdir}/{f.filename}')
    
    for f in files:
        if f.filename == "correct.py":
            continue
        try:
            call_child(f'{tmpdir}/correct.py', f'{tmpdir}/{f.filename}', max_time)
        except Exception as e:
            shutil.rmtree(tmpdir, ignore_errors=True)
            raise e
    return tmpdir

@TaskBlueprint.route('/problem/<int:problem_id>')
@login_required
async def problem(problem_id):
    problem_db = Problem.query.get(problem_id)
    if not problem_db:
        await flash("No problemset found with that id.")
        return redirect(url_for('task.problems'))
    return await render_template('problem.html', problem=problem_db)


@TaskBlueprint.route('/problem')
async def problems():
    problemsets = Problem.query.all()
    return await render_template('problems.html', problems=problemsets)


@TaskBlueprint.route('/create', methods=["GET", "POST"])
@login_required
async def create_problem():
    if not current_user.role or current_user.role.name != "Admin":
        abort(401)
    if request.method == "GET":
        return await render_template('creator.html')

    form = await request.form
    files = (await request.files).getlist('file')
    test_name = form.get('test_name')
    readable_name = form.get('readable_name')
    max_time = int(form.get('max_time'))
    i_sample = form.get('i_sample')
    o_sample = form.get('o_sample')
    details = form.get('details')

    if not files:
        await flash("Please upload valid test cases.")
        return await render_template('creator.html')

    if not any(x.filename == 'correct.py' for x in files):
        await flash("You must provide a correct.py file!")
        return await render_template('creator.html')

    if len(files) == 1:
        await flash("Please provide at least one test case!")
        return await render_template('creator.html')

    existing_db = Problem.query.filter_by(test_folder=test_name).first()
    if existing_db:
        await flash("There's already a test with that name.")
        return await render_template('creator.html')

    if not all((files, test_name, readable_name, max_time, i_sample, o_sample, details)):
        await flash("Please input all fields.")
        return await render_template('creator.html')

    details = html.escape(details)

    try:
        tmpdir = test_checker(files, max_time)
    except subprocess.TimeoutExpired:
        await flash("Your correct.py timed out. Consider raising maximum time or optimize your code.")
        return await render_template('creator.html')
    except subprocess.CalledProcessError as e:
        await flash("An error has occured on your correct.py.")
        await flash(e.stderr)
        return await render_template('creator.html')

    try:
        dirname = 'cases/' + test_name
        shutil.move(tmpdir, dirname)
        make_problem(test_name, readable_name, max_time, i_sample, o_sample, details)
        await flash("OK!")
    except:
        traceback.print_exc()
        await flash("Something went wrong...")
    finally:
        return await render_template('creator.html')
