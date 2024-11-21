#!/bin/python3
import sys
import os
import subprocess
import argparse
import threading
import requests
import re
import configparser

root = os.getcwd()

# todo 
# github api create repo
# 

class Repo:
    def __init__(self, path, url):
        self.path = path
        self.url = url

    def __repr__(self):
        return f"{self.path} {self.url}"

class Command:
    def __init__(self, command, cwd=root):
        self.command = command
        self.cwd = cwd

    def run(self):
        command_parsed = self.command
        if not isinstance(command_parsed, str):
            command_parsed = ' '.join(command_parsed)

        print("[debug]: " + str(self.cwd) + " : " + command_parsed)

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

class GitlabEndpoint:
    def __init__(self):
        self.secret = os.environ['GITLAB_SECRET']
        self.header = {"PRIVATE-TOKEN": self.secret}

    def create_repo(self, name) -> str:
        # response = requests.get("https://gitgud.io/api/v4/projects", headers=self.header, data={"name": name})
        # print(response.json())
        # if response.status_code != 404:
        #     print(f"gitlab get repo '{name}' was not 404, code: {response.status_code}")
        #     exit(1)
        response = requests.post("https://gitgud.io/api/v4/projects", headers=self.header, data={"name": name})
        if response.status_code != 201:
            print(f"gitlab create repo '{name}' failed with code: {response.status_code}")
            exit(1)
        print(response.json())
        return response.json()["ssh_url_to_repo"]

def create_repo(path, endpoint):
    name = os.path.basename(path)
    if not re.match(r'^[a-zA-Z0-9._-]+$', name):
        exit(f"Repository name is invalid: " + name)
    if os.path.exists(path):
        exit(f"Repository path already exists: " + path)

    repo_git_url = endpoint.create_repo(name)

    os.makedirs(path)
    fg([Command('git init', cwd=path)])

    config[f'submodule "{name}"'] = {
        'path': path,
        'url': repo_git_url
    }
    with open('.gitm', 'w') as configfile:
        config.write(configfile)

    abs_path = os.path.abspath(path)
    fg([
        Command('git init', abs_path), # todo change cwd to beginning so text begin is aligned
        Command(['git remote add origin', repo_git_url], cwd=abs_path),
        Command('touch README.md', cwd=abs_path),
        Command('git add README.md', cwd=abs_path),
        Command('git commit -m \"auto\"', cwd=abs_path),
        Command('git push --set-upstream origin master', cwd=abs_path),
        Command('gitm update', cwd=root)
    ])

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

config = configparser.ConfigParser()
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="gitm")
    parser.add_argument("command", help="init, update, status, create")
    args = parser.parse_args()

    if args.command == "init":
        if os.path.exists(".gitm"):
            exit(f"gitm is already initialised in this directory")
        os.makedirs(".gitm")
        print("initialised empty .gitm repository")
        exit(0)

    if not os.path.exists(".gitm"):
        print(f"no .gitm file in directory {root}")
        os._exit(0)

    config_repos = []

    config = configparser.ConfigParser()
    config.read('.gitm')
    with open('.gitm', 'r') as file:
        for key in config.sections():
            config_repos.append(Repo(config[key]["path"], config[key]["url"]))

    update_submodules()
    repos = []

    for repo in config_repos:
        if os.path.isdir(repo.path) and is_submodule(repo.path):
            repos.append(repo)
            continue

    if args.command == "status":
        for repo in repos:
            print(str(repo))

    elif args.command == "add":
        # todo
        print("")

    elif args.command == "update":
        if not os.path.exists(".git"):
            fg([Command("git init")])

        for repo in config_repos:
            if os.path.isdir(repo.path) and is_submodule(repo.path):
                repos.append(repo)
            else:
                # add git submodule
                fg([Command(['git submodule add', repo.url, repo.path])]) #, Command('git submodule update --init --recursive')
                if os.path.isdir(repo.path):
                    fg([Command('gitm init', cwd=repo.path)])

                # now we reload 'git submodule --list' to make sure it was successful
                update_submodules()
                if os.path.isdir(repo.path) and is_submodule(repo.path):
                    repos.append(repo)
                else:
                    exit("couldn't add submodule: " + repo.name)

    elif args.command == "create":
        if not args.name:
            exit(f"no --name")
        create_repo(args.name, GitlabEndpoint())

    # elif args.command == "mirror":
    #     for repo in repos:
    #         print(repo)
    #         fg([Command('git submodule update --init --recursive')])
    #         fg([Command('git fetch --all', cwd=repo.path)])
    #         fg([Command('gitm mirror', cwd=repo.path)])

    else:
        print(f"no command {args.command}")
