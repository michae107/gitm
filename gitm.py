#!/bin/python3
import sys
import os
import subprocess
import argparse
import threading

cwd = os.getcwd()

# def remove_remotes(repo_path):
#     git_dir = os.path.join(repo_path, ".git")
#     if os.path.isdir(git_dir):
#         print(f"Removing remote origins in: {repo_path}")
#         remotes = subprocess.check_output(['git', 'remote'], cwd=repo_path).decode().splitlines()
#         if 'origin' in remotes:
#             subprocess.run(['git', 'remote', 'remove', 'origin'], cwd=repo_path, check=True)
#             print(f"Removed origin from {repo_path}")
#         else:
#             print(f"No origin found in {repo_path}")

# def traverse(start_dir):
#     for root, dirs, files in os.walk(start_dir):
#         # if ".git" in dirs:
#         #     remove_remotes(root)
#         for d in dirs:
#             traverse(os.path.join(root, d))

class Repo:
    def __init__(self, repo_url):
        self.url = repo_url
        self.name = os.path.basename(self.url).replace('.git', '')
        self.local_path = self.name
        self.path = os.path.join(cwd, self.local_path)

    def __repr__(self):
        return f"{self.name} {self.url}"

class Command:
    def __init__(self, command, cwd=cwd):
        self.command = command
        self.cwd = cwd

    def run(self):
        command_parsed = self.command
        if not isinstance(command_parsed, str):
            command_parsed = ' '.join(command_parsed)
        print(command_parsed)
        process = subprocess.Popen(command_parsed.split(" "), cwd=cwd, stderr=sys.stderr, stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return stdout, stderr


def fg(command):
    # if isinstance(command, list) or isinstance(command, tuple):
        for i in command:
            i.run()
    # else:
        # command.run()

def bg(command):
    thread = threading.Thread(target=lambda: fg(command))
    thread.start()
    # fg(command)

def get_git_ignored_files(repo_directory):
    return  subprocess.run(
        ['git', 'ls-files', '--others', '--ignored', '--exclude-standard'],
        capture_output=True,
        text=True,
        check=True
    ).splitlines()

if __name__ == "__main__":
    repos = []
    with open("gitm.txt", 'r') as f:
        for line in f:
            repos.append(Repo(line.strip()))

    parser = argparse.ArgumentParser(description="gitm")
    parser.add_argument("command", help="First argument (positional)")
    # parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode")
    args = parser.parse_args()

    print(f"gitm {cwd}")

    if args.command == "init":
        # if os.path.exists(".git") and os.path.exists("gitm.txt"):
        #     sys.exit("gitm is already inititalised in this directory")
        if not os.path.exists(".git"):
            fg([Command("git init")])
        if os.path.exists("gitm.txt"):
            for repo in repos:
                if not os.path.isdir(repo.path):
                    bg([Command(['git submodule add', repo.url, repo.local_path]), Command('git submodule update --init --recursive')])
            
    # elif cmd == "clone":
    #     for repo in repos:
    #         if not os.path.isdir(self.path):
    #             command('git submodule add ' + self.url)
    #             command('git submodule update --init --recursive')
    # elif cmd == "mirror":
    #     for repo in repos: 
    #         repo.clone()
    #         command('git fetch --all', cwd=repo.path)
    else:
        print(f"no command {args.command}")
