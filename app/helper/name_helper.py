import random, string

def make_random_str(n):
    return ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=n))