from typing import Set
from .subprocess import check_output

def get_first_commit_hash(cwd: str) -> str:
    """..."""

    cmd = ['git', 'rev-list', '--max-parents=0', 'HEAD']
    stdout, _ = check_output(cmd, cwd=cwd)
    hash: str = stdout.strip()

    return hash

def get_changed_files_between_commits(cwd: str, before_commit: str, after_comit='HEAD', location: str = None) -> Set[str]:
    """Get changed files between commits without duplicates
    
    example: 
        >>> git log --format=''  --name-only <before_commit>..<after_commit> <location> | sort -u
    """
    cmd = ['git', 'log', '--format=', '--name-only', f'{before_commit}..{after_comit}']
    if location:
        cmd.append(location)

    stdout, _ = check_output(cmd, cwd=cwd)
    if stdout:
        files = stdout.strip().split('\n')
        return set(files)

    return set([])