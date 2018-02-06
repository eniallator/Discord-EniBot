class BaseCommand():
    """The base class for CommandSystem and Command classes"""

    _cmd_term = None
    _help_full = None
    _help_summary = None
    _meta_data = {}

    def __str__(self):
        return self._cmd_term

    def __hash__(self):
        return hash(self._cmd_term)

    def __eq__(self, arg):
        return self._cmd_term == arg
    
    def __getitem__(self, i):
        return self._meta_data[i] if i in self._meta_data else None


    def get_individual_help(self, args, help_full=False):
        """Gets a command's help if it's help_full or help_summary and accepts callables or strings"""
        if help_full and self._help_full and (isinstance(self._help_full, str) or callable(self._help_full)):
            return self._help_full(*args) if callable(self._help_full) else self._help_full
        elif self._help_summary and (isinstance(self._help_summary, str) or callable(self._help_summary)):
            return self._help_summary(*args) if callable(self._help_summary) else self._help_summary
        return 'Error could not find the command\'s help.'


    def update_meta_data(self, **kwargs):
        for key in kwargs:
            self._meta_data[key] = kwargs[key]
