#! /usr/bin/python3

import os
import subprocess as sp
from dotenv import load_dotenv
import requests
import json
from sys import argv
import submitty as sm
import time

load_dotenv(os.path.dirname(os.path.realpath(__file__)) + "/.env")

user = os.getenv("user")
baseurl = os.getenv("baseurl")
vcstoken = os.getenv("vcstoken")
apitoken = os.getenv("apitoken")
semester = os.getenv("semester")
state: sm.SharedState = sm.SharedState()

headers = {"Authorization": apitoken}


def show_help():
    print(f"Usage: {argv[0]} [mode] <course> <gradeable>")
    print("Modes:")
    print("\tcourses - lists currently enrolled courses")
    print("\tinfo    - show info about a gradeable")
    print("\tpush    - push gradeable and request autograde [UNSTABLE]")
    print("\tinit    - create config file for selected gradeable")
    print("\tclone   - download git repo for selected gradeable [UNSTABLE]")


def clone():
    auth = sp.Popen(f"git clone {baseurl}/git/{semester}/{state.course}/{state.gradeable}/{user} {state.gradeable}", shell=True)
    
    os.chdir(state.gradeable)
    init()


def poll_autograder(gradeable):
    old_val = int(gradeable.queue_position)
    elapsed = 0
    print(f"In queue, position {old_val}")
    while gradeable.is_queued:
        if old_val != gradeable.queue_position:
            old_val = gradeable.queue_position
        time.sleep(1)
        elapsed += 1
        print(f"\rIn queue, position {old_val} ({elapsed}s)")
    while gradeable.is_grading:
        time.sleep(1)
        elapsed += 1
        print(f"\rAutograder is running ({elapsed}s)")
    print(f"\rAutograder finished in {elapsed} seconds.")


def init():
    if os.path.isfile("./submitty.json"):
        print("You already initialized this assignment!")
        return
    with open("./submitty.json", 'w') as smfile:
        json.dump(state.__dict__, smfile)
        print(f"Initialized submitty.json for {state.course}:{state.gradeable}")


def courses():
    # print(f"GET {baseurl}/api/courses")
    r = requests.get(f"{baseurl}/api/courses", headers=headers)
    return [sm.Course(c) for c in r.json()["data"]["unarchived_courses"]]


def submit():
    os.system("git commit -a")
    os.system("git push")
    if input("Really submit [y/n]? ").lower() != "y":
        return
    r = requests.post(f"{baseurl}/api/{semester}/{state.course}/gradeable/{state.gradeable}/grade",
                      headers=headers, data={
                            "user_id": user,
                            "vcs_checkout": True,
                            "git_repo_id": True
                          })
    if r.json()["status"] != "success":
        print(f'{r.json()["status"]}: {r.json()["message"]}')
    else:
        poll_autograder(get_info())

    return get_info()


def get_info():
    # print(f"GET {baseurl}/api/{semester}/{course}/gradeable/{gradeable}/values?user_id={user}")
    r = requests.get(
        f"{baseurl}/api/{semester}/{state.course}/gradeable/{state.gradeable}/values?user_id={user}",
        headers=headers)
    if len(r.content) == 0:
        print("Gradeable was not autograded")
        return None
    elif r.json()["status"] != "success":
        print(f'{r.json()["status"]}: {r.json()["message"]}')
        return None
    else:
        return sm.Gradeable(r.json()["data"], state.gradeable)


if __name__ == "__main__":
    print(f"Logged in as {user} on {baseurl}")

    mode = argv[1] if len(argv) >= 2 else ""

    if os.path.isfile("./submitty.json"):
        with open("./submitty.json", 'r') as smfile:
            state = sm.SharedState(json.load(smfile))
    else:
        state.course = argv[2] if len(argv) >= 3 else ""
        state.gradeable = argv[3] if len(argv) >= 4 else ""

    if mode == "" or state.course == "" or state.gradeable == "":
        show_help()
    elif mode == "courses":
        [print(str(c)) for c in courses()]
    elif mode == "info":
        print(str(get_info()))
    elif mode == "push":
        print(str(submit()))
    elif mode == "clone":
        print(str(clone()))
    elif mode == "init":
        init()
    else:
        show_help()
