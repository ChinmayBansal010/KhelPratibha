class RepCounter:
    def __init__(self, name):
        self.name = name
        self.stage = None
        self.good_reps = 0
        self.bad_reps = 0
        self.feedback_log = []

    def add_rep(self, form_ok, feedback):
        total_reps = self.good_reps + self.bad_reps + 1
        if form_ok:
            self.good_reps += 1
            self.feedback_log.append(f"Rep {total_reps}: Good Form!")
        else:
            self.bad_reps += 1
            self.feedback_log.append(f"Rep {total_reps}: {feedback}")
        
        print(f"[{self.name}] Good: {self.good_reps} | Bad: {self.bad_reps} | Feedback: {self.feedback_log[-1]}")