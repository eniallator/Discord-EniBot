class BaseCommand():
    """The base class for CommandSystem and Command classes"""

    _help_full = lambda: None
    _help_summary = lambda: None
    _meta_data = {}

    def __getitem__(self, i):
        return self._meta_data[i] if i in self._meta_data else None


    def get_individual_help(self, args, help_full=False):
        """Gets a command's help if it's help_full or help_summary and accepts callables or strings"""
        if help_full and self._help_full and (isinstance(self._help_full, str) or callable(self._help_full)):
            return self._help_full(*args) if callable(self._help_full) else self._help_full
        elif self._help_summary and (isinstance(self._help_summary, str) or callable(self._help_summary)):
            return self._help_summary(*args) if callable(self._help_summary) else self._help_summary
        return 'Error could not find the command\'s help.'
