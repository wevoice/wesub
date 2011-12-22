import os, sys, re
from subprocess import Popen, PIPE

def get_current_commit_hash(short=True):
    if os.path.islink('.git'):
        sys.stderr.write('WARNING: .git is a symlink.  '
                         'Things may not work correctly.\n')

    process = Popen(["git", "rev-parse", "HEAD"], stdout=PIPE)

    guid =  process.communicate()[0].strip()
    if guid:
        guid = guid[:8]

    try:
        import commit
        if commit.LAST_COMMIT_GUID.split('/')[-1] != guid:
            sys.stderr.write('WARNING: commit.py is out of date.  '
                             'Things may not work correctly.  '
                             'Use "python deploy/create_commit_file.py" to update it.\n')
    except ImportError:
        sys.stderr.write('WARNING: commit.py does not exist.  '
                         'Things may not work correctly.  '
                         'Use "python deploy/create_commit_file.py" to create it.\n')
    return guid

def get_current_branch():
    if os.path.islink('.git'):
        sys.stderr.write('WARNING: .git is a symlink.  '
                         'Things may not work correctly.\n')

    process = Popen(["git", "branch"], stdout=PIPE)

    branches = process.communicate()[0].strip()
    branch = re.search(r"\* ([^\n]+)", branches).group(1)

    return branch

def get_guid():
    guid = get_current_commit_hash()
    branch = get_current_branch()
    return "%s/%s" % (branch, guid)
