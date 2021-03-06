#!/usr/bin/env python

import os
import sys
import stat
import subprocess

root_folder = os.path.dirname(__file__)


def command(cmd, cwd=None, allow_output_on_stderr=False):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    stdout, stderr = p.communicate()
    if not allow_output_on_stderr and stderr:
        raise RuntimeError('Command %s returned with output on stderr: %s' % (cmd, stderr))
    return stdout, stderr


STATUS_GIT_DIRTY = 'dirty'
STATUS_GIT_CLEAN = 'clean'
STATUS_GIT_UNTRACKED = 'untracked'

STATUS_HOME_UNLINKED = 'unlinked'
STATUS_HOME_SYMLINKED = 'symlinked'
STATUS_HOME_HARDLINKED = 'hardlinked'
STATUS_HOME_INEXISTENT = 'inexistent'


class DotFilesRepo(object):

    def __init__(self, repo_path):
        self.repo_path = repo_path

    def get_tracked_files(self):
        stdout, stderr = command(['git', 'ls-files'], self.repo_path)
        paths = stdout.strip().split()
        return paths

    def get_untracked_files(self):
        stdout, stderr = command(['git', 'ls-files', '--other'], self.repo_path)
        paths = stdout.strip().split()
        return paths

    def get_dirty_files(self):
        stdout, stderr = command(['git', 'status', '--short', '--untracked-files=no', '.'], self.repo_path)
        if stdout.strip() == '':
            return []
        paths = [line[3:] for line in stdout.rstrip().split('\n')]
        return paths

    def get_repo_status(self):
        status_dict = {}
        for f in self.get_untracked_files():
            status_dict[f] = STATUS_GIT_UNTRACKED
        for f in self.get_tracked_files():
            status_dict[f] = STATUS_GIT_CLEAN
        for f in self.get_dirty_files():
            status_dict[f] = STATUS_GIT_DIRTY
        return status_dict


def get_link_status(files, home_path, repo_path):
    '''
    Check the (sym)link status between files (relative paths)
    in home_path and repo_path.
    '''
    status_dict = {}
    for file in files:
        home_file = os.path.join(home_path, file)
        repo_file = os.path.join(repo_path, file)

        if not os.path.exists(home_file):
            status_dict[file] = STATUS_HOME_INEXISTENT
            continue

        # Start with not linked by default
        status_dict[file] = STATUS_HOME_UNLINKED
        # Stat home file
        stat_info = os.lstat(home_file)
        # Check for symlink
        if stat.S_ISLNK(stat_info.st_mode):
            target = os.readlink(home_file)
            target = os.path.join(os.path.dirname(home_file), target)
            if os.path.realpath(target) == os.path.realpath(repo_file):
                status_dict[file] = STATUS_HOME_SYMLINKED
        # Check for hard link
        elif stat_info.st_ino == os.stat(repo_file).st_ino:
            status_dict[file] = STATUS_HOME_HARDLINKED

        #TODO: when not linked: diff or no diff?

    return status_dict


def overview(home_path, repo_path):
    # Get status of dotfiles in repo
    repo = DotFilesRepo(repo_path)
    repo_status_dict = repo.get_repo_status()
    # Get link status between home and repo
    link_status_dict = get_link_status(repo_status_dict.keys(), home_path, repo_path)

    file_max_width = max([len(f) for f in repo_status_dict.keys()])
    link_status_max_width = max([len(s) for s in link_status_dict.values()])
    repo_status_colors = {
        STATUS_GIT_CLEAN: '\033[32;m',
        STATUS_GIT_DIRTY: '\033[31;m',
        STATUS_GIT_UNTRACKED: '\033[0m',
    }
    link_status_colors = {
        STATUS_HOME_HARDLINKED: '\033[32;m',
        STATUS_HOME_SYMLINKED: '\033[32;m',
        STATUS_HOME_UNLINKED: '\033[0m',
        STATUS_HOME_INEXISTENT: '\033[33;m',
    }
    color_reset = '\033[0m'
    for file, repo_status in repo_status_dict.items():
        link_status = link_status_dict[file]
        # File name under home_path.
        sys.stdout.write(('~/' + file).ljust(file_max_width + 2))
        # Link status.
        sys.stdout.write(' ' + link_status_colors[link_status] + link_status.ljust(link_status_max_width) + color_reset + ' ')
        # Repo file name.
        sys.stdout.write(os.path.normpath(os.path.join(repo_path, file)))
        # Repo file status.
        sys.stdout.write(' ' + repo_status_colors[repo_status] + '(' + repo_status + ')' + color_reset)

        sys.stdout.write('\n')


def main():
    home_path = os.getenv('HOME')
    repo_path = os.path.join(root_folder, 'home')
    overview(home_path, repo_path)



if __name__ == '__main__':
    main()
