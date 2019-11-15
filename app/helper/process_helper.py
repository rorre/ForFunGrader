import subprocess

def call_child(file_path, test_path, max_time=None):
    proc = subprocess.run(['python', file_path],
        stdin=open(test_path), capture_output=True, timeout=max_time, check=True)
    return proc.stdout.decode().strip()
