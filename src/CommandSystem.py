from src.BaseCommand import BaseCommand
from src.Command import Command


class CommandSystem(BaseCommand):
    """The command system class"""

    def __init__(self, system_name='', help_summary='', **kwargs):
        self._system_name = system_name
        self._help_summary = help_summary
        self._meta_data = kwargs
        self._commands = {}

    def _lookup_cmd(self, cmd_string):
        """Looks up in the current command system to see if the cmd_string is a command already and returns it"""
        if cmd_string in self._commands:
            return self._commands[cmd_string]
        elif cmd_string.lower() in self._commands and not self._commands[cmd_string.lower()]['case_sensitive']:
            return self._commands[cmd_string.lower()]
        return None

    def _validate_add_command(self, cmd_string):
        """Validates the add command/command system methods"""
        if not isinstance(cmd_string, str) or not cmd_string:
            raise ValueError('Command needs to have 1 or more characters.')
        if self._lookup_cmd(cmd_string):
            raise ValueError('Command already exists.')

    def _validate_command_system_path(self, cmd_string):
        """Validates that the given command system exists"""
        if not isinstance(cmd_string, str):
            raise ValueError('Error when locating the path to the command system.')
        if not (self._lookup_cmd(cmd_string) and isinstance(self._commands[cmd_string], CommandSystem)):
            raise ValueError('Could not find command system.')

    def _validate_permissions(self, cmd, args, kwargs=None):
        call_checker = lambda func, args, kwargs: func(*args, **kwargs) if kwargs else func(*args)
        if callable(cmd['check_perms']) and not call_checker(cmd['check_perms'], args, kwargs):
            return False
        return True

    def add_command(self, cmd, cmd_func=None, help_summary=None, help_full=None, check_perms=None, case_sensitive=False):
        """Adds a command to the current command system"""
        kwargs = {
            'cmd_func': cmd_func,
            'help_summary': help_summary,
            'help_full': help_full,
            'check_perms': check_perms,
            'case_sensitive': case_sensitive
        }
        if isinstance(cmd, str):
            cmd_string = cmd
            cmd_string = cmd_string.lower() if not case_sensitive else cmd_string
            self._validate_add_command(cmd_string)
            self._commands[cmd_string] = Command(**kwargs)
        else:
            raise ValueError('First argument has to be a string when adding a command.')

    def get_command_system(self, cmd_system):
        if isinstance(cmd_system, str):
            self._validate_command_system_path(cmd_system)
            return self._commands[cmd_system]
        elif isinstance(cmd_system, list) and cmd_system:
            self._validate_command_system_path(cmd_system[0])
            cmd_system_ref = self._commands[cmd_system[0]]
            if len(cmd_system) > 1:
                return cmd_system_ref.get_command_system(cmd_system[1:])
            else:
                return cmd_system_ref
        else:
            raise ValueError("Expecting a string or list when getting a command system.")

    def add_command_system(self, cmd_string, cmd_system_or_help_summary=None, check_perms=None, case_sensitive=False):
        """Adds a command system within the current command system"""
        self._validate_add_command(cmd_string)
        cmd_system = cmd_system_or_help_summary
        if not isinstance(cmd_system_or_help_summary, CommandSystem):
            help_summary = cmd_system_or_help_summary
            cmd_system = CommandSystem(
                system_name=cmd_string,
                help_summary=help_summary,
                check_perms=check_perms,
                case_sensitive=case_sensitive
            )
        self._commands[cmd_string] = cmd_system

    async def execute(self, cmd_to_execute, *args, **kwargs):
        """Executes the desired command (whether it is within child command system or not) with arguments"""
        cmd_args = cmd_to_execute.split(' ')
        cmd = self._lookup_cmd(cmd_args[0]) if len(cmd_args) > 0 else None
        if cmd:
            if self._validate_permissions(cmd, args, kwargs):
                if isinstance(cmd, Command):
                    return await cmd.execute(args, kwargs)
                elif isinstance(cmd, CommandSystem):
                    return await cmd.execute(' '.join(cmd_args[1:]), *args, **kwargs)
                else:
                    return 'Error could not find a callable in the command object.'
            else:
                return 'Error insufficient permissions for this command.'
        else:
            if self._system_name:
                return 'Unknown ' + self._system_name + ' command. Use "help" to get a list of commands.'
            return 'Unknown command. Use "help" to get a list of commands.'

    def _gen_help(self, args, prefix=''):
        """Generates the help for the command system"""
        help_message = 'Showing help:'
        if self._system_name:
            help_message = 'Showing help for ' + self._system_name + ': '
        for cmd_string in self._commands:
            cmd = self._commands[cmd_string]
            if self._validate_permissions(cmd, args):
                help_summary = cmd.get_individual_help(args)
                help_message += '\n`' + prefix + cmd_string + '`: ' + help_summary
        return help_message + '\nTo learn more about a command, use `help <command>`'

    def get_help(self, help_cmd, *args, prefix=''):
        """Makes the help for this command system/a child command system and messages it back"""
        cmd_args = help_cmd.split(' ')
        new_prefix = prefix + self._system_name + ' '
        cmd = self._lookup_cmd(cmd_args[0]) if cmd_args else None
        if cmd:
            if isinstance(cmd, CommandSystem):
                return cmd.get_help(' '.join(cmd_args[1:]), *args, prefix=new_prefix)
            else:
                return cmd.get_individual_help(args, help_full=True)
        elif not cmd_args or cmd_args == ['']:
            return self._gen_help(args, prefix=new_prefix)
        else:
            return 'Unknown command. Use "help" to get a list of commands.'
