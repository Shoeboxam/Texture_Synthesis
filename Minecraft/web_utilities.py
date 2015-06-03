from git import Repo


def clone_repo(url, target):
    Repo.clone_from(url, target)
