import re

def identity(x): return x
def lower(x): return x.lower()

def clean(x):
    x = re.sub(r'[^a-zA-Z0-9 ]', ' ', x)
    x = re.sub(r'\s+', ' ', x).strip()
    return x

def sort_words(x):
    return " ".join(sorted(x.split()))

def reverse(x): return x[::-1]

TRANSFORMS = {
    "identity": identity,
    "lower": lower,
    "clean": clean,
    "sort": sort_words,
    "reverse": reverse
}