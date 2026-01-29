#! /usr/bin/python3

import os
from dotenv import load_dotenv
import requests
import json
from sys import argv
import submitty as sm

load_dotenv()

user = os.getenv("user")
baseurl = os.getenv("baseurl")
vcstoken = os.getenv("vcstoken")
apitoken = os.getenv("apitoken")
semester = os.getenv("semester")
mode = argv[1] if len(argv) >= 2 else ""
course = argv[2] if len(argv) >= 3 else ""
gradeable = argv[3] if len(argv) >= 4 else ""


headers = {"Authorization": apitoken}


def courses():
    # print(f"GET {baseurl}/api/courses")
    r = requests.get(f"{baseurl}/api/courses", headers=headers)
    return [sm.Course(c) for c in r.json()["data"]["unarchived_courses"]]


def get_gradeable():
    # print(f"GET {baseurl}/api/{semester}/{course}/gradeable/{gradeable}/values?user_id={user}")
    r = requests.get(
    f"{baseurl}/api/{semester}/{course}/gradeable/{gradeable}/values?user_id={user}",
        headers=headers)
    if len(r.content) == 0:
        return "Gradeable was not autograded"
    elif r.json()["status"] != "success":
        return f'{r.json()["status"]}: {r.json()["message"]}'
    else:
        return sm.Gradeable(r.json()["data"], gradeable)


if __name__ == "__main__":
    print(f"Logged in as {user} on {baseurl}")

    if mode == "":
        print(f"Usage: {argv[0]} [mode] <additional args>")
        print("Modes:")
        print("\tcourses")
        print("\tget [course] [gradeable]")
    elif mode == "courses":
        [print(str(c)) for c in courses()]
    elif mode == "get":
        print(str(get_gradeable()))
