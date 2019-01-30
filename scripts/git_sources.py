# Django branch to typecheck against
from pathlib import Path

from git import Repo

DJANGO_BRANCH = 'stable/2.1.x'

# Specific commit in the Django repository to check against
DJANGO_COMMIT_SHA = '03219b5f709dcd5b0bfacd963508625557ec1ef0'

PROJECT_DIRECTORY = Path(__file__).parent.parent
REPO_DIRECTORY = PROJECT_DIRECTORY / 'django-sources'


def update_django_sources_repo():
    # clone Django repository, if it does not exist
    if not REPO_DIRECTORY.exists():
        repo = Repo.clone_from('https://github.com/django/django.git', REPO_DIRECTORY)
    else:
        repo = Repo(REPO_DIRECTORY)
        repo.remotes['origin'].pull(DJANGO_BRANCH)

    repo.git.checkout(DJANGO_COMMIT_SHA)
