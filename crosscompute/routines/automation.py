# TODO: Send refresh without server restart for template changes
import logging
import subprocess
from os import getenv
from os.path import join, relpath
from pyramid.config import Configurator
from waitress import serve
from watchgod import watch

from .configuration import (
    get_automation_definitions,
    get_raw_variable_definitions,
    load_configuration,
    prepare_batch_folder)
from ..constants import (
    # CONFIGURATION_EXTENSIONS,
    HOST, PORT,
    # TEMPLATE_EXTENSIONS,
)
from ..macros import StoppableProcess, format_path, make_folder
from ..views import AutomationViews, EchoViews


class Automation():

    def initialize_from_path(self, configuration_path):
        configuration = load_configuration(configuration_path)
        configuration_folder = configuration['folder']
        script_definition = configuration.get('script', {})
        script_folder = script_definition.get('folder', '')
        command_string = script_definition.get('command', '')
        automation_definitions = get_automation_definitions(
            configuration)

        self.configuration_path = configuration_path
        self.configuration = configuration
        self.configuration_folder = configuration_folder
        self.script_folder = script_folder
        self.command_string = command_string
        self.automation_definitions = automation_definitions
        self.automation_views = AutomationViews(automation_definitions)
        self.echo_views = EchoViews(configuration_folder)

        logging.debug('configuration_path = %s', configuration_path)
        logging.debug('configuration_folder = %s', configuration_folder)

    @classmethod
    def load(Class, configuration_path):
        instance = Class()
        instance.initialize_from_path(configuration_path)
        return instance

    def run(self, custom_environment=None):
        if not self.command_string:
            logging.warning('command not defined in script configuration')
            return
        automation_definition = self.automation_definitions[0]
        variable_definitions = get_raw_variable_definitions(
            automation_definition, 'input')
        # TODO: Load base custom environment from configuration
        for batch_definition in automation_definition.get('batches', []):
            batch_folder = prepare_batch_folder(
                batch_definition, variable_definitions,
                self.configuration_folder)
            self.run_batch(batch_folder, custom_environment)

    def run_batch(self, batch_folder, custom_environment=None):
        # TODO: Consider accepting batch_name
        input_folder = join(batch_folder, 'input')
        output_folder = join(batch_folder, 'output')
        log_folder = join(batch_folder, 'log')
        debug_folder = join(batch_folder, 'debug')
        self.run_script(
            input_folder, output_folder, log_folder, debug_folder,
            custom_environment)

    def run_script(
            self, input_folder, output_folder, log_folder, debug_folder,
            custom_environment=None):
        # TODO: Make each folder optional
        default_environment = {
            'CROSSCOMPUTE_INPUT_FOLDER': relpath(
                input_folder, self.script_folder),
            'CROSSCOMPUTE_OUTPUT_FOLDER': relpath(
                output_folder, self.script_folder),
            'CROSSCOMPUTE_LOG_FOLDER': relpath(
                log_folder, self.script_folder),
            'CROSSCOMPUTE_DEBUG_FOLDER': relpath(
                debug_folder, self.script_folder),
            'PATH': getenv('PATH', ''),
        }
        environment = default_environment | (custom_environment or {})
        logging.debug('environment = %s', environment)

        for folder_label, relative_folder in {
            'input': input_folder,
            'output': output_folder,
            'log': log_folder,
            'debug': debug_folder,
        }.items():
            folder = make_folder(join(
                self.configuration_folder, relative_folder))
            logging.info(f'{folder_label}_folder = {format_path(folder)}')

        # TODO: Capture stdout and stderr for live output
        subprocess.run(
            self.command_string,
            shell=True,
            cwd=self.configuration_folder,
            env=environment)

    def serve(
            self, host=HOST, port=PORT, is_production=False, is_static=False):

        def run_server():
            app = self.get_app(is_static)
            serve(app, host=host, port=port)

        if is_production and is_static:
            run_server()
            return

        server_process = StoppableProcess(target=run_server)
        server_process.start()
        for changes in watch(self.configuration_folder):
            for changed_type, changed_path in changes:
                logging.debug('%s %s', changed_type, changed_path)
                # changed_extension = splitext(changed_path)[1]
                '''
                # if changed_extension in CONFIGURATION_EXTENSIONS:
                if changed_extension in sum([
                    CONFIGURATION_EXTENSIONS,
                    TEMPLATE_EXTENSIONS,
                ], ()):
                '''
                server_process.stop()
                # TODO: Search for configuration if the file is gone
                self.initialize_from_path(self.configuration_path)
                server_process = StoppableProcess(target=run_server)
                server_process.start()
                '''
                elif changed_extension in TEMPLATE_EXTENSIONS:
                    self.echo_views.reset_time()
                    # for queue in self.echo_views.queues:
                    # queue.put(changed_path)
                '''

    def get_app(self, is_static=False):
        with Configurator() as config:
            config.include('pyramid_jinja2')
            config.include(self.automation_views.includeme)
            if not is_static:
                config.include(self.echo_views.includeme)
        return config.make_wsgi_app()
