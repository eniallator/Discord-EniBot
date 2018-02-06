from src.BaseCommand import BaseCommand

class Command(BaseCommand):
    """The command class"""

    def __init__(self, cmd_term, cmd_func, help_summary, help_full=None, **kwargs):
        self._cmd_term = cmd_term
        self._cmd_func = cmd_func
        self._help_summary = help_summary
        self._help_full = help_full
        self._meta_data = kwargs

    def execute(self, args=[], kwargs={}):
        if callable(self._cmd_func):
            return self._cmd_func(*args, **kwargs)
        else:
            return 'Error could not find a callable in the command object.'
