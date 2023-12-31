#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import sys
import git
import git.exc as git_exception
from subprocess import PIPE
import subprocess
import json

BASE_DIR = os.environ['JENKINS_SLAVE_WORKSPACE']
REPO_CNF = json.loads(os.environ['REPO_CNF'])

def print_message(msg):
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()


def get_repo_auth(path_url):
    parts = path_url.replace('http://', '', 1).replace('https://', '', 1).split('/')
    repo_server = parts[0]
    return REPO_CNF[repo_server]


def parse_args():
    parser = argparse.ArgumentParser(description="应用编译打包STEP")
    parser.add_argument("--project-id", metavar="project_id", type=str,
                        required=True, help="项目ID")
    parser.add_argument("--scm-app-id", metavar="scm_app_id", type=str,
                        required=True, help="应用ID")
    parser.add_argument("--app-name", metavar="app_name", type=str,
                        required=True, help="应用名称")
    parser.add_argument("--app-language", metavar="app_language", type=str,
                        required=False, help="应用编程语言(java,python,go,nodejs,etc)")
    parser.add_argument("--branch-name", metavar="branch_name", type=str,
                        required=True, help="代码分支名称")
    parser.add_argument("--branch-url", metavar="branch_url", type=str,
                        required=True, help="代码分支路径")
    parser.add_argument("--vcs-type", metavar="vcs_type", type=str,
                        required=True, help="版本管理工具(git)")
    parser.add_argument("--image-version", metavar="image_version", type=str,
                        required=False, help="自定义镜像版本")
    parser.add_argument("--stage-id", metavar="stage_id", type=str,
                        required=True, help="流水线阶段ID")
    parser.add_argument("--publish-job-id", metavar="publish_job_id", type=str,
                        required=True, help="发布任务ID")
    parser.add_argument("--build-path", metavar="build_path", type=str,
                        required=True, help="构建目录")
    return parser.parse_args()


def call_subprocess(cmds=None, workspace=None, print_cmd=True, out=sys.stdout):
    if print_cmd:
        print_message(' '.join(cmds))
    p = subprocess.Popen(cmds, shell=False, cwd=workspace, stdout=out, stderr=sys.stderr)
    p.wait()
    if p.returncode != 0:
        print_message(u'命令执行失败，退出')
        sys.exit(1)


def call_subprocess_str(cmd=None, workspace=None):
    print_message(cmd)
    p = subprocess.Popen(cmd, shell=True, cwd=workspace, stdout=PIPE, stderr=sys.stderr)
    p.wait()
    if p.returncode != 0:
        print_message(u'--------------------->  ，退出')
        sys.exit(1)
    return str(p.stdout.read()).strip()


def hide_auth_info(username, password, error_info):
    error_info = str(error_info)
    new_info = error_info.replace(username + ":" + password + '@', '****:****@')
    return new_info


class BuildStep(object):
    """ 代码检出 """

    def __init__(self, args):
        self.args = args
        self.release_name = None
        self.image_version = None
        self.workspace = None
        self.ci_workspace = None

    def run(self):
        self.prepare_workspace()
        self.checkout()
        self.check_build_path()

    def prepare_workspace(self):
        print_message(u'----->开始准备工作空间')
        self.workspace = os.path.join(BASE_DIR, self.args.project_id, self.args.stage_id, self.args.app_name,
                                      self.args.branch_name)
        if os.path.exists(self.workspace):
            # clean workspace
            print_message(u'----->开始清理工作目录')
            os.system("rm -rf {}".format(self.workspace))
        print_message(u'----->创建工作目录: {}'.format(self.workspace))
        os.makedirs(self.workspace)

    def checkout(self):
        if self.args.vcs_type.upper() != 'GIT':
            print_message(u'----->只支持git类型的仓库代码检出,')
            sys.exit(1)
        self._git_checkout()

    def check_build_path(self):
        print_message(u'----->开始检查构建目录是否存在')
        if self.args.build_path[:1] == "/":
            build_path = self.args.build_path
        else:
            build_path = "/" + self.args.build_path
        self.ci_workspace = self.workspace + build_path
        if not os.path.exists(self.ci_workspace):
            print_message("\033[1;31;40m错误: 构建目录{}不存在\033[0m".format(build_path))
            sys.exit(1)
        print_message(u'代码分支{}检出成功,且构建目录存在(:'.format(self.args.branch_name))

    def _git_checkout(self):
        username, password = get_repo_auth(self.args.branch_url)
        parts = self.args.branch_url.split('://')
        if not parts[1].endswith('.git'):
            parts[1] = parts[1] + '.git'
        repo_url = '{}://{}:{}@{}'.format(parts[0], username, password, parts[1])
        try:
            print_message(u'----->git: 检出分支({})'.format(self.args.branch_name))
            repo = git.Repo.clone_from(repo_url, self.workspace, branch=self.args.branch_name)
            commit_id = repo.head.commit.hexsha[:8]
            self.current_revision = self.origin_revision = self.image_version = commit_id
        except git_exception.GitError as e:
            info = hide_auth_info(username, password, e)
            print_message(info)
            sys.exit(1)


if __name__ == "__main__":
    args = parse_args()
    build_step = BuildStep(args)
    build_step.run()
