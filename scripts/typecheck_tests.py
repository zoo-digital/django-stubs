import os
import re
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Pattern

from mypy import build
from mypy.main import process_options

from scripts.git_sources import PROJECT_DIRECTORY, REPO_DIRECTORY, update_django_sources_repo

# Some errors occur for the test suite itself, and cannot be addressed via django-stubs. They should be ignored
# using this constant.
IGNORED_ERROR_PATTERNS = [
    'Need type annotation for',
    'already defined on',
    'Cannot assign to a',
    'cannot perform relative import',
    'broken_app',
    'cache_clear',
    'call_count',
    'call_args_list',
    'call_args',
    '"password_changed" does not return a value',
    '"validate_password" does not return a value',
    'LazySettings',
    'Cannot infer type of lambda',
    '"refresh_from_db" of "Model"',
    '"as_sql" undefined in superclass',
    'Incompatible types in assignment (expression has type "str", target has type "type")',
    'Incompatible types in assignment (expression has type "Callable[',
    'Invalid value for a to= parameter',
    'Incompatible types in assignment (expression has type "FilteredChildAdmin", variable has type "ChildAdmin")',
    'Incompatible types in assignment (expression has type "RelatedFieldWidgetWrapper", variable has type "AdminRadioSelect")',
    'has incompatible type "MockRequest"; expected "WSGIRequest"',
    '"NullTranslations" has no attribute "_catalog"',
    'Definition of "as_sql" in base class',
    'expression has type "property"',
    '"object" has no attribute "__iter__"',
    'Too few arguments for "dates" of "QuerySet"',
    re.compile(r'"Callable\[\[(Any(, )?)+\], Any\]" has no attribute'),
    re.compile(r'"HttpResponseBase" has no attribute "[A-Za-z_]+"'),
    re.compile(r'Incompatible types in assignment \(expression has type "Tuple\[\]", '
               r'variable has type "Tuple\[[A-Za-z, ]+\]"'),
    re.compile(r'"validate" of "[A-Za-z]+" does not return a value'),
    re.compile(r'Module has no attribute "[A-Za-z_]+"'),
    re.compile(r'"[A-Za-z\[\]]+" has no attribute "getvalue"'),
    # TODO: remove when reassignment will be possible (in 0.670? )
    re.compile(r'Incompatible types in assignment \(expression has type "(QuerySet|List){1}\[[A-Za-z, ]+\]", '
               r'variable has type "(QuerySet|List){1}\[[A-Za-z, ]+\]"\)'),
    re.compile(r'"(MockRequest|DummyRequest|DummyUser)" has no attribute "[a-zA-Z_]+"'),
]

# Test folders to typecheck
TESTS_DIRS = [
    'absolute_url_overrides',
    'admin_autodiscover',
    'admin_changelist',
    'admin_checks',
    'admin_custom_urls',
    'admin_default_site',
    'admin_docs',
    # TODO: 'admin_filters',
    'admin_inlines',
    'admin_ordering',
    'admin_registration',
    'admin_scripts',
    # TODO: 'admin_utils',
    # TODO: 'admin_views',
    'admin_widgets',
    'aggregation',
    'aggregation_regress',
    'annotations',
    'app_loading',
    'apps',
    # TODO: auth_tests
    'base',
    'bash_completion',
    'basic',
    'builtin_server',
    'bulk_create',
    # TODO: 'cache',
    # TODO: 'check_framework',
    'choices',
    'conditional_processing',
    # TODO: 'contenttypes_tests',
    'context_processors',
    'csrf_tests',
    'custom_columns',
    # TODO: 'custom_lookups',
    # TODO: 'custom_managers',
    'custom_methods',
    'custom_migration_operations',
    'custom_pk',
    'datatypes',
    'dates',
    'datetimes',
    'db_functions',
    'db_typecasts',
    'db_utils',
    'dbshell',
    # TODO: 'decorators',
    'defer',
    # TODO: 'defer_regress',
    'delete',
    'delete_regress',
    # TODO: 'deprecation',
    # TODO: 'dispatch',
    'distinct_on_fields',
    'empty',
    # TODO: 'expressions',
    'expressions_case',
    # TODO: 'expressions_window'
]


@contextmanager
def cd(path):
    """Context manager to temporarily change working directories"""
    if not path:
        return
    prev_cwd = Path.cwd().as_posix()
    if isinstance(path, Path):
        path = path.as_posix()
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def is_ignored(line: str) -> bool:
    for pattern in IGNORED_ERROR_PATTERNS:
        if isinstance(pattern, Pattern):
            if pattern.search(line):
                return True
        else:
            if pattern in line:
                return True
    return False


def check_with_mypy(abs_path: Path, config_file_path: Path) -> int:
    error_happened = False
    with cd(abs_path):
        sources, options = process_options(['--config-file', str(config_file_path), str(abs_path)])
        res = build.build(sources, options)
        for error_line in res.errors:
            if not is_ignored(error_line):
                error_happened = True
                print(error_line)
    return int(error_happened)


if __name__ == '__main__':
    mypy_tests_config_file = (PROJECT_DIRECTORY / 'scripts' / 'mypy.ini').absolute()
    tests_root = REPO_DIRECTORY / 'tests'
    global_rc = 0

    update_django_sources_repo()
    for dirname in TESTS_DIRS:
        abs_path = (PROJECT_DIRECTORY / tests_root / dirname).absolute()
        print(f'Checking {abs_path.as_uri()}')

        rc = check_with_mypy(abs_path, mypy_tests_config_file)
        if rc != 0:
            global_rc = 1

    sys.exit(rc)
