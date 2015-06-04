from git import Repo, GitCommandError


def clone_repo(url, target):
    try:
        Repo.clone_from(url, target)
    except GitCommandError:
        print("Repository already exists, skipping clone")