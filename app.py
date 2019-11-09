from quart import Quart, request, render_template, jsonify, flash, url_for, redirect
import asyncio
import os
import subprocess
import random
import string
import functools
import config

app = Quart(__name__)
app.secret_key = config.secret


@app.route('/')
async def index():
    return await render_template('index.html')


def check_script(filename, test):
    test_files = os.listdir('cases/' + test)
    test_files.remove('correct.py')
    for i, fname in enumerate(test_files):
        try:
            user = subprocess.run(['python', filename], stdin=open(
                f"cases/{test}/{fname}"), capture_output=True, timeout=5)
        except:
            return {'status' : 400, 'err': 'Timed out.'}
        result = subprocess.run(['python', 'cases/' + test + '/correct.py'],
                                stdin=open(f"cases/{test}/{fname}"), capture_output=True, timeout=5)

        user_output = user.stdout.decode().strip()
        expected_output = result.stdout.decode().strip()
        if user_output != expected_output:
            return {'status': 400, 'err': {
                'expected': expected_output,
                'output': user_output,
                'testno': i + 1,
                'maxtest': len(test_files),
                'input': open(f"cases/{test}/{fname}").read()
            }}
    return {'status': 200, 'message': 'OK'}


@app.route('/check', methods=['POST'])
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
    if not os.path.exists('cases/' + test_name):
        return jsonify({'status': 400, 'err': "No test with that name."})

    filename = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=6)) + '.py'
    file.save('script/' + filename)

    result = await asyncio.get_running_loop().run_in_executor(
        None,
        functools.partial(check_script, 'script/' + filename, test_name)
    )
    try:
        os.unlink('script/' + filename)
    except:
        pass

    return jsonify(result)

app.run()
