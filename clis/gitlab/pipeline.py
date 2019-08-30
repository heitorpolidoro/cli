import time

from clis.gitlab.job import Job
from helpers.command import Command, CommandArgument
from helpers.loading import Loading
from helpers.utils import *
from helpers.colors import *


# TODO
# - notify quando job falhar
# - 1 retry automático


class Pipeline(object):
    help = 'GitLab pipeline commands'
    version = '0.0.1-beta'

    def __init__(self, id=None, branch=None, **kwargs):
        self.id = id
        self.web_url = None
        self.status = None
        self.branch = branch
        self.jobs = []
        if id is None:
            if branch is None:
                self.branch = run_and_return_output('git rev-parse --abbrev-ref HEAD')

            last_commit_id = run_and_return_output('git log --pretty=%%H -1 %s' % self.branch)
            content = Requests.get_content(
                'https://gitlab.com/api/v4/projects/${GITLAB_PROJECT}/pipelines/?sha=' + last_commit_id,
                headers={'PRIVATE-TOKEN': '${PRIVATE_TOKEN}'}
            )
        else:
            content = Requests.get_content(
                'https://gitlab.com/api/v4/projects/${GITLAB_PROJECT}/pipelines/${pipeline_id}',
                headers={'PRIVATE-TOKEN': '${PRIVATE_TOKEN}'},
                pipeline_id=id
            )
        if content:
            if isinstance(content, list):
                content = content[0]
            vars(self).update(content)

    @staticmethod
    def validate_env_vars():
        # Assuming that the project has the same name in GitHub and GitLab
        validate_env_var('PRIVATE_TOKEN',
                         message='The value is in Last Pass in%s Gitlab QB CLI tokens%s notes.' % (Bold, Color_Off))

        validate_env_var('PIPELINE_TRIGGER_TOKEN',
                         message='The value is in Last Pass in%s Gitlab QB CLI tokens%s notes.' % (Bold, Color_Off))

        validate_env_var(
            'GITLAB_PROJECT',
            default=lambda: get_gitlab_project_id(
                run_and_return_output('git config --get remote.origin.url').split('/')[1].replace('.git', '')
            ),
            message='The value is the GitLab project ID.'
        )

    def update(self):
        content = Requests.get_content(
            'https://gitlab.com/api/v4/projects/${GITLAB_PROJECT}/pipelines/${pipeline_id}',
            headers={'PRIVATE-TOKEN': '${PRIVATE_TOKEN}'},
            pipeline_id=self.id
        )
        if content:
            vars(self).update(content)

        self.update_jobs()

    def update_jobs(self):
        jobs = Requests.get_content(
            'https://gitlab.com/api/v4/projects/${GITLAB_PROJECT}/pipelines/${pipeline_id}/jobs',
            headers={'PRIVATE-TOKEN': '${PRIVATE_TOKEN}'}, pipeline_id=self.id, clazz=Job)

        grouped_jobs = {}
        if not isinstance(jobs, list):
            jobs = [jobs]
        bigger_name = max(jobs, key=lambda j: len(j.name))
        pipeline_running = False
        pipeline_pending = False
        while jobs:
            job = jobs.pop(0)
            job.name = '{0:{size}}'.format(job.name, size=len(bigger_name.name))
            if job.status == 'running':
                pipeline_running = True
            elif job.status == 'pending':
                pipeline_pending = True

            if job.name in grouped_jobs:
                parent = grouped_jobs.get(job.name)
                while parent.retry_job:
                    parent = parent.retry_job

                parent.retry_job = job
            else:
                grouped_jobs[job.name] = job

        if not pipeline_running and pipeline_pending:
            self.status = 'pending'
        self.jobs = list(grouped_jobs.values())
        return self.jobs

    '''------------- PRINTS -------------'''

    def print_status(self):
        status = {'success': 'passed'}.get(self.status, self.status)

        color = {
            'success': [Green, Bold],
            'running': [IBlue],
            'pending': [Yellow],
            'failed': [Red, Bold],
        }.get(self.status, [])
        print(*color, 'Pipeline ', end='')

        if self.status == 'running':
            color.append(Blinking)
        print(*color, status)

    def print_jobs(self):
        if not self.jobs:
            self.update_jobs()
        # color = ''
        # separator = '-' * (int(run_and_return_output('tput cols')) - 1)
        separator = '-' * 20
        print_separator = True
        for job in sorted(self.jobs):
            if job.retry_job:
                if not print_separator:
                    print(separator)
                print_separator = True
            else:
                print_separator = False

            while job:
                job.print_info()
                # job.print_info(fixed_color=color)
                job = job.retry_job

            if print_separator:
                print(separator)
            # color = Dim if not color else ''

    '''------------- COMMANDS -------------'''

    @staticmethod
    @Command(
        help='start a pipeline for the current commit, if not exits',
        arguments=[
            CommandArgument('-m', '--monitor', action='store_true',
                            help='start the monitor after starting the pipeline'),
            CommandArgument('-b', '--branch', help='start a pipeline in the BRANCH'),
            CommandArgument('-f', '--force', action='store_true', help='force to start a pipeline'),
        ])
    def start(arguments):
        Pipeline.validate_env_vars()
        Loading.start()
        pipeline = Pipeline(branch=arguments.branch)

        if pipeline.id and not arguments.force:
            reset_printed_lines()
            print(Yellow, 'Pipeline already exists')
            print(Cyan, pipeline.web_url)
            pipeline.print_status()
            pipeline.print_jobs()
        else:
            print(Bold, 'Checking if the commit is mirrored')

            reset_printed_lines()
            local_commit_id = get_last_local_commit(pipeline.branch)
            print('Local:\t%s' % local_commit_id)

            github_commit_id = get_last_github_commit(pipeline.branch)
            color, symbol = (Green, check_mark) if local_commit_id == github_commit_id else (Red, cross_mark)
            print(color, 'GitHub:\t%s\t%s' % (github_commit_id, symbol))

            gitlab_commit_id = get_last_gitlab_commit(pipeline.branch)
            color, symbol = (Green, check_mark) if local_commit_id == gitlab_commit_id else (Red, cross_mark)
            print(color, 'GitLab:\t%s\t%s' % (github_commit_id, symbol))
            while gitlab_commit_id is None \
                    or local_commit_id != gitlab_commit_id \
                    or github_commit_id != gitlab_commit_id:
                return_printed_lines()
                print('Waiting to mirror the commit')

                print('Local:\t%s' % local_commit_id)

                color, symbol = (Green, check_mark) if local_commit_id == github_commit_id else (Red, cross_mark)
                print(color, 'GitHub:\t%s\t%s' % (github_commit_id, symbol))

                color, symbol = (Green, check_mark) if local_commit_id == gitlab_commit_id else (Red, cross_mark)
                print(color, 'GitLab:\t%s\t%s' % (github_commit_id, symbol))

                time.sleep(0.05)
                github_commit_id = get_last_github_commit(pipeline.branch)
                gitlab_commit_id = get_last_gitlab_commit(pipeline.branch)

            reset_printed_lines()
            time.sleep(5)  # Wait to auto-triggered pipeline to run
            pipeline = Pipeline(branch=arguments.branch)  # Check if auto-triggered pipeline
            if not pipeline.id or arguments.force:
                print('Starting pipeline for branch %s' % pipeline.branch)
                Requests.post('https://gitlab.com/api/v4/projects/${GITLAB_PROJECT}/trigger/pipeline',
                              files={'token': (None, '${PIPELINE_TRIGGER_TOKEN}'), 'ref': (None, pipeline.branch)})
                time.sleep(5)  # Wait to triggered pipelines to run
                pipeline = Pipeline(branch=arguments.branch)  # Update pipeline information
            notify('Pipeline %s' % pipeline.branch, 'Started')

        if arguments.monitor:
            return_printed_lines()
            Loading.stop()
            Pipeline.monitor(pipeline=pipeline)

    @staticmethod
    @Command(help='monitor the pipeline for the current commit',
             arguments=[
                 CommandArgument('-p', '--pipeline', help='monitor the pipeline with ID=PIPELINE'),
                 CommandArgument('-b', '--branch', help='monitor the pipeline for the branch BRANCH'),
             ])
    def monitor(arguments=None, pipeline=None, branch=None):
        Pipeline.validate_env_vars()
        Loading.start()

        if pipeline is None:
            if branch is None:
                branch = arguments.branch
            if branch is not None:
                pipeline = Pipeline(branch=branch)
            else:
                pipeline = Pipeline(id=arguments.pipeline)

        if pipeline.id is None:
            exit('There is no Pipeline for this commit in the branch: %s' % pipeline.branch)

        print(Bold, 'Starting monitor')
        print(Cyan, pipeline.web_url)
        reset_printed_lines()

        if pipeline.status in ['running', 'pending']:
            notify('Monitor pipeline %s' % pipeline.branch, 'Started')

        pipeline.update()
        Loading.stop()
        atexit.register(return_printed_lines)
        while pipeline.status in ['running', 'pending']:
            pipeline.print_status()
            pipeline.print_jobs()

            time.sleep(0.05)

            pipeline.update()
            return_printed_lines(clear=False)
        atexit.unregister(return_printed_lines)

        pipeline.print_status()
        pipeline.print_jobs()
        notify('Pipeline %s Finished' % pipeline.branch, pipeline.status)
