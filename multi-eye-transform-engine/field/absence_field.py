# field/absence_field.py

class AbsenceField:
    def __init__(self):
        self.empty = set()

    def update(self, samples):
        for s in samples:
            if not s["hit"]:
                key = tuple(round(v, 2) for v in s["pos"])
                self.empty.add(key)