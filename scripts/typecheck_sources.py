import shutil
import sys
from pathlib import Path

import retype

from scripts.git_sources import PROJECT_DIRECTORY, REPO_DIRECTORY, update_django_sources_repo

if __name__ == '__main__':
    update_django_sources_repo()

    target_directory = PROJECT_DIRECTORY / 'django-sources-typed'
    shutil.rmtree(target_directory, ignore_errors=True)

    retype.Config.incremental = True
    for src_path in (REPO_DIRECTORY / 'django').glob('*'):
        for file, error, exc_type, tb in retype.retype_path(src=Path(src_path),
                                                            pyi_dir=PROJECT_DIRECTORY / 'django-stubs',
                                                            targets=target_directory / 'django',
                                                            src_explicitly_given=True):
            print(f'error: {file}: {error}', file=sys.stderr)
        break
