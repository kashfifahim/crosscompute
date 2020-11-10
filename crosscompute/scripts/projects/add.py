from .. import OutputtingScript
from ...routines import (
    add_project,
    run_safely)


class AddProjectScript(OutputtingScript):

    def configure(self, argument_subparser):
        super().configure(argument_subparser)
        argument_subparser.add_argument(
            '--name', metavar='PROJECT_NAME',
            dest='project_name')

    def run(self, args, argv):
        super().run(args, argv)
        run_safely(add_project, [
            args.project_name,
        ], args.as_json, args.is_quiet)
