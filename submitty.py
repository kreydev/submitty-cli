class Course:
    def __init__(self, _json):
        self.semester = _json["semester"]
        self.title = _json["title"]
        self.display_name = _json["display_name"]
        self.display_semester = _json["display_semester"]
        self.user_group = _json["user_group"]
        self.registration_section = _json["registration_section"]

    def __str__(self):
        return f"[{self.title}] {self.display_name}, sec {self.registration_section}"


class TestCase:
    def __init__(self, _json):
        self.name = _json["name"]
        self.details = _json["details"]
        self.is_extra_credit = _json["is_extra_credit"]
        self.points_available = _json["points_available"]
        self.has_extra_results = _json["has_extra_results"]
        self.points_received = _json["points_received"]
        self.testcase_message = _json["testcase_message"]

    def __str__(self):
        return f"""{self.name}: {self.points_received}/{self.points_available} points\
{"\nEXTRA CREDIT" if self.is_extra_credit else ""}\
{"\nDetails: " + self.details if self.details != "" else ""}\
{"\n" + self.testcase_message if self.testcase_message != "" else ""}
"""


class Gradeable:
    def __init__(self, _json, name):
        self.name = name
        self.is_queued = _json["is_queued"]
        self.queue_position = _json["queue_position"]
        self.is_grading = _json["is_grading"]
        self.has_submission = _json["has_submission"]
        self.autograding_complete = _json["autograding_complete"]
        self.has_active_version = _json["has_active_version"]
        self.highest_version = _json["highest_version"]
        self.total_points = _json["total_points"]
        self.total_percent = _json["total_percent"]
        self.test_cases = [TestCase(t) for t in _json["test_cases"]]

    def __str__(self):
        outstr = f"Viewing gradeable {self.name}:\n"
        outstr += f"Attempts used: {self.highest_version}\n"
        outstr += f"Current score: {sum([x.points_received for x in self.test_cases])}/{self.total_points}\n"

        if len(self.test_cases) > 0:
            outstr += "Test Cases:\n\t"
            outstr += f"{"\t".join([str(t) for t in self.test_cases])}"
        elif not self.autograding_complete:
            outstr += "This gradeable has not been autograded.\n"
        else:
            outstr += "There are no test cases for this gradeable.\n"
        outstr += f"This gradeable is worth {self.total_percent}% of your grade.\n"
        return outstr


class SharedState:
    def __init__(self, indict=dict()):
        for k in indict.keys():
            self[k] = indict[k]

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)
