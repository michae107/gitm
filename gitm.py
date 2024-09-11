#!/bin/python3
import sys
import os
import subprocess
import argparse
import threading

root = os.getcwd()

# todo 
# allow set remotes of all repos
# github api create repo
# check file sizes for lfs with >git ls-files --others --ignored --exclude-standard

class Repo:
    def __init__(self, repo_url):
        self.url = repo_url
        self.name = os.path.basename(self.url).replace('.git', '')
        self.local_path = self.name
        self.path = os.path.join(root, self.local_path)

    def __repr__(self):
        return f"{self.name} {self.url} {self.path}"

class Command:
    def __init__(self, command, cwd=root):
        self.command = command
        self.cwd = cwd

    def run(self):
        command_parsed = self.command
        if not isinstance(command_parsed, str):
            command_parsed = ' '.join(command_parsed)

        print(str(self.cwd) + " : " + command_parsed)

        process = subprocess.Popen(command_parsed.split(" "), cwd=self.cwd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(stderr.decode())
            os._exit(1)
        return stdout.decode()


def fg(command):
    for i in command:
        i.run()

def bg(command):
    thread = threading.Thread(target=lambda: fg(command))
    thread.start()

submodules = []
def update_submodules():
    lines = Command('git submodule').run().split("\n")
    submodules.clear()
    for line in lines:
        if len(line) == 0: continue
        submodules.append(line.strip().split(" ")[1])
    return submodules

def is_submodule(name):
    for submodule in submodules:
        if submodule == name:
            return True
    return False

if __name__ == "__main__":
    if not os.path.exists(".gitm"):
        print(f"no .gitm file in directory {root}")
        os._exit(0)

    config_repos = []
    with open(".gitm", 'r') as f:
        for line in f:
            config_repos.append(Repo(line.strip()))

    update_submodules()
    repos = []

    for repo in config_repos:
        if os.path.isdir(repo.path) and is_submodule(repo.name):
            repos.append(repo)
            continue

    parser = argparse.ArgumentParser(description="gitm")
    parser.add_argument("command", help="First argument (positional)")
    args = parser.parse_args()

    if args.command == "status":
        for repo in repos:
            print(str(repo))

    elif args.command == "init":
        if not os.path.exists(".git"):
            fg([Command("git init")])
        for repo in config_repos:
            if os.path.isdir(repo.path) and is_submodule(repo.name):
                repos.append(repo)
                continue
            fg([Command(['git submodule add', repo.url, repo.local_path])]) #, Command('git submodule update --init --recursive')
            if os.path.isdir(repo.path):
                fg([Command('gitm init', cwd=repo.path)])
            update_submodules()
            if os.path.isdir(repo.path) and is_submodule(repo.name):
                repos.append(repo)
            else:
                exit("couldn't add submodule: " + repo.name)

    elif args.command == "mirror":
        for repo in repos:
            print(repo)
            fg([Command('git submodule update --init --recursive')])
            fg([Command('git fetch --all', cwd=repo.path)])
            fg([Command('gitm mirror', cwd=repo.path)])

    else:
        print(f"no command {args.command}")
