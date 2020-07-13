import time

from wip_clis.gitlab import Gitlab
from wip_clis.gitlab.job import Job
from parser import Parser
from parser.parser import CONFIG_FILE
from pyutils.command import Command, CommandArgument
from pyutils.loading import Loading
from pyutils.pyutils import *
from colors.colors import *


# TODO
# - notify quando job falhar
# - 1 retry automático


class Pipeline(object):
    help = 'GitLab pipeline commands'
    version = '0.0.1-beta'

    def __init__(self, id=None, branch=None, **_):
        self._status = None
        self._jobs = None
        self._gitlab_pipeline = None
        self.branch = branch
        if id is None:
            if branch is None:
                self.branch = run_and_return_output('git rev-parse --abbrev-ref HEAD')

            last_commit_id = run_and_return_output('git log --pretty=%%H -1 %s' % self.branch)
            resp = Gitlab.projects.get(get_env_var('GITLAB_PROJECT_ID')).pipelines.list(sha=last_commit_id)
            if resp:
                self._gitlab_pipeline = resp[0]
        else:
            self._gitlab_pipeline = Gitlab.projects.get(get_env_var('GITLAB_PROJECT_ID')).pipelines.get(id)

    def __getattr__(self, item):
        if self._gitlab_pipeline is not None:
            return getattr(self._gitlab_pipeline, item)
        return None

    @property
    def jobs(self):
        if self._jobs is None:
            self._jobs = [Job(gitlab_job=j) for j in self._gitlab_pipeline.jobs.list()]

        return self._jobs

    @jobs.setter
    def jobs(self, value):
        self._jobs = value

    @property
    def status(self):
        if self._status is None:
            self._status = self._gitlab_pipeline.status

        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @staticmethod
    def validate_env_vars():
        # Assuming that the project has the same name in GitHub and GitLab
        validate_env_var('PRIVATE_TOKEN',
                         message='The value is in Last Pass in%s Gitlab UDC CLI tokens%s notes.' % (Bold, Color_Off))

        validate_env_var('PIPELINE_TRIGGER_TOKEN',
                         message='The value is in Last Pass in%s Gitlab UDC CLI tokens%s notes.' % (Bold, Color_Off))

        project_id_key = os.getcwd() + '_PROJECT_ID'
        project_id = get_env_var(project_id_key, '')
        if not project_id:
            project = Gitlab.get_project()
            project_id = project.id
            Parser.set_local_variable(project_id_key, project_id, file_name=CONFIG_FILE, exit_on_complete=False)

        os.environ['GITLAB_PROJECT_ID'] = str(project_id)

        # trigger_id_key = os.getcwd() + '_TRIGGER_ID'
        # trigger_id = get_env_var(trigger_id_key, '')
        # if not trigger_id:
        #     project = Gitlab.get_project()
        #     for t in project.triggers.list():
        #         if t.token == get_env_var('PIPELINE_TRIGGER_TOKEN'):
        #             Parser.set_local_variable(trigger_id_key, t.id, file_name=CONFIG_FILE, exit_on_complete=False)

        os.environ['TRIGGER_ID'] = str(project_id)

    def update(self):
        self.__init__(self.id)
        self.update_jobs()

    def update_jobs(self):
        self._jobs = None
        jobs = self.jobs
        grouped_jobs = {}
        bigger_name = max(jobs, key=lambda j: len(j.name))
        pipeline_running = False
        pipeline_pending = False
        while jobs:
            job = jobs.pop(0)
            job.name = '{0:{size}}'.format(job.name, size=len(bigger_name.name))
            if job.running:
                pipeline_running = True
            elif job.pending:
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
        separator = '-' * 20
        print_separator = True
        for job in self.jobs:
            if job.retry_job:
                if not print_separator:
                    print(separator)
                print_separator = True
            else:
                print_separator = False

            while job:
                job.print_info()
                job = job.retry_job

            if print_separator:
                print(separator)

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
            github_commit_id = gitlab_commit_id = None

            reset_printed_lines()
            local_commit_id = get_last_local_commit(pipeline.ref)
            while gitlab_commit_id is None \
                    or local_commit_id != gitlab_commit_id \
                    or github_commit_id != gitlab_commit_id:
                github_commit_id = get_last_github_commit(pipeline.ref)
                gitlab_commit_id = Gitlab.get_last_commit(pipeline.ref)
                return_printed_lines()
                print('Waiting to mirror the commit')

                print('Local:\t%s' % local_commit_id)

                color, symbol = (Green, check_mark) if local_commit_id == github_commit_id else (Red, cross_mark)
                print(color, 'GitHub:\t%s\t%s' % (github_commit_id, symbol))

                color, symbol = (Green, check_mark) if local_commit_id == gitlab_commit_id else (Red, cross_mark)
                print(color, 'GitLab:\t%s\t%s' % (gitlab_commit_id, symbol))

                time.sleep(0.05)

            reset_printed_lines()
            time.sleep(5)  # Wait to auto-triggered pipeline to run
            pipeline = Pipeline(branch=arguments.branch)  # Check if auto-triggered pipeline
            if not pipeline.id or arguments.force:
                print('Starting pipeline for branch %s' % pipeline.branch)
                Gitlab.get_project().trigger_pipeline(pipeline.branch, get_env_var('PIPELINE_TRIGGER_TOKEN'))
                # Requests.post('https://gitlab.com/api/v4/projects/${GITLAB_PROJECT_ID}/trigger/pipeline',
                #               files={'token': (None, '${PIPELINE_TRIGGER_TOKEN}'), 'ref': (None, pipeline.ref)})
                time.sleep(5)  # Wait to triggered pipelines to run
                pipeline = Pipeline(branch=arguments.branch)  # Update pipeline information
            if not arguments.monitor:
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
            exit('There is no Pipeline for this commit in the branch: %s' % pipeline.ref)

        print(Bold, 'Starting monitor')
        print(Cyan, pipeline.web_url)
        reset_printed_lines()

        if pipeline.status in ['running', 'pending']:
            notify('Monitor pipeline %s' % pipeline.ref, 'Started')

        pipeline.update()
        Loading.stop()
        atexit.register(return_printed_lines)
        while pipeline.status in ['running', 'pending']:
            pipeline.print_status()
            pipeline.print_jobs()

            time.sleep(0.5)

            pipeline.update()
            return_printed_lines(clear=False)
        atexit.unregister(return_printed_lines)

        pipeline.print_status()
        pipeline.print_jobs()
        notify('Pipeline %s Finished' % pipeline.ref, pipeline.status)
