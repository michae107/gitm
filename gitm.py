#!/bin/python3
import os
import argparse
import requests
import re
import configparser
import pygit2

# todo
# github api create repo
# git lfs integration

def get_ssh_key():
    ssh_dir = os.path.expanduser("~/.ssh/")
    key_files = [
        ("id_rsa", "id_rsa.pub"),
        ("id_ecdsa", "id_ecdsa.pub"),
        ("id_ed25519", "id_ed25519.pub")
    ]

    if not os.path.isdir(ssh_dir):
        exit(f"SSH directory does not exist: {ssh_dir}")
    
    for private_key, public_key in key_files:
        public_key_path = os.path.join(ssh_dir, public_key)
        private_key_path = os.path.join(ssh_dir, private_key)
        
        if os.path.exists(public_key_path) and os.path.exists(private_key_path):
            return (public_key_path, private_key_path)
    
    assert False

class GitmPygit2Auth(pygit2.RemoteCallbacks):
    def credentials(self, url, username_from_url, allowed_types):
        if allowed_types & pygit2.enums.CredentialType.USERNAME:
            return pygit2.Username("git")
        elif allowed_types & pygit2.enums.CredentialType.SSH_KEY:
            ssh_key = get_ssh_key()
            print("using ssh key-pair " + str(ssh_key))
            return pygit2.Keypair("git", ssh_key[0], ssh_key[1], "")
        else:
            return None

class Repo:
    def __init__(self, path, url):
        self.path = path
        self.url = url

    def __repr__(self):
        return f"{self.path} {self.url}"

class GitlabEndpoint:
    def __init__(self):
        self.secret = os.environ['GITLAB_SECRET']
        self.header = {"PRIVATE-TOKEN": self.secret}

    def create_repo(self, name) -> str:
        response = requests.post("https://gitlab.com/api/v4/projects", headers=self.header, data={"name": name})
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
    create_repository = pygit2.init_repository(path = path, origin_url = repo_git_url)

    config[f'submodule "{name}"'] = {
        'path': path,
        'url': repo_git_url
    }
    with open('.gitm', 'w') as configfile:
        config.write(configfile)
    
    update()

def update():
    if not os.path.exists(".git"):
        print("initialise gitm git repository: " + _cwd)
        pygit2.init_repository(_cwd)
        repository = pygit2.Repository(_cwd)

        for repo in config_repos:
            if not repo.path in repository.listall_submodules():
                repository.submodules.add(repo.url, repo.path, callbacks=GitmPygit2Auth())
                sub_repository = pygit2.Repository(repo.path)
                sub_repository.submodules.update(init=True)
        repository.submodules.update(init=True)
        print(str(repository.listall_submodules()))


repository: pygit2.Repository = None
_cwd: str = os.getcwd()
config_repos = []
config = configparser.ConfigParser()

def main():
    parser = argparse.ArgumentParser(description="gitm")
    parser.add_argument("command", help="init, update, status, create")
    args = parser.parse_args()

    if args.command == "init":
        if os.path.exists(".gitm"):
            exit("gitm is already initialised in this directory")
        with open(".gitm", "w") as file:
            file.write("")
        print("initialised empty .gitm repository")
        return

    if not os.path.exists(".gitm"):
        print(f"no .gitm file in directory {_cwd}")
        return

    repository = pygit2.Repository(_cwd)
    config = configparser.ConfigParser()
    config.read('.gitm')
    with open('.gitm', 'r') as file:
        for key in config.sections():
            config_repos.append(Repo(config[key]["path"], config[key]["url"]))

    if args.command == "status":
        print("submodules: " + str(repository.listall_submodules()))

    elif args.command == "create":
        if not args.name:
            exit(f"no --name")
        create_repo(args.name, GitlabEndpoint())

    elif args.command == "update":
        update()

    else:
        print(f"no command {args.command}")

if __name__ == "__main__": main()
