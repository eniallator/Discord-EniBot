from src.BaseCommand import BaseCommand
from src.Command import Command

class CommandSystem(BaseCommand):
    """The command system class"""

    def __init__(self, system_name='', help_summary='', **kwargs):
        self._cmd_term = system_name
        self._help_summary = help_summary
        self._meta_data = kwargs
        self._commands = []

    def _get_cmd(self, cmd_string):
        return self._commands[self._commands.index(cmd_string)] if cmd_string in self._commands else None

    def _lookup_cmd(self, cmd_string):
        """Looks up in the current command system to see if the cmd_string is a command already and returns it"""
        # if cmd_string in self._commands:
        #     return self._commands[cmd_string]
        # elif cmd_string.lower() in self._commands and not self._commands[self._commands.index(cmd_string.lower())]['case_sensitive']:
        #     return self._commands[cmd_string.lower()]
        # return None
        cmd_string_lower = self._get_cmd(cmd_string.lower())
        return self._get_cmd(cmd_string) or (cmd_string_lower if not cmd_string_lower['case_sensitive'] else None)

    def _validate_add_command(self, cmd_string):
        """Validates the add command/command system methods"""
        if not isinstance(cmd_string, str) or not cmd_string:
            raise ValueError('Command needs to have 1 or more characters.')
        if self._lookup_cmd(cmd_string):
            raise ValueError('Command already exists.')

    def _validate_command_system_path(self, cmd_string):
        """Validates that the given command system exists"""
        if not isinstance(cmd_string, str):
            raise ValueError('Error when locating the path to the command system when adding a new command.')
        if not (self._lookup_cmd(cmd_string) and isinstance(self._commands[cmd_string]), CommandSystem):
            raise ValueError('Could not find command system when adding a new command.')

    def _validate_permissions(self, cmd, args, kwargs=None):
        call_checker = lambda func, args, kwargs: func(*args, **kwargs) if kwargs else func(*args)
        if callable(cmd['check_perms']) and not call_checker(cmd['check_perms'], args, kwargs):
            return False
        return True

    def add_command(self, cmd, cmd_func=None, help_summary=None, help_full=None, check_perms=None, case_sensitive=False):
        """Adds a command to the current command system"""
        # command_value = {'func': cmd_func, 'help': help_summary, 'case_sensitive': case_sensitive}
        # if check_perms:
        #     command_value['check_perms'] = check_perms
        # if help_full:
        #     command_value['help_full'] = help_full
        kwargs = {
            'cmd_func': cmd_func,
            'help_summary': help_summary,
            'help_full': help_full,
            'check_perms': check_perms,
            'case_sensitive': case_sensitive
        }
        if isinstance(cmd, str):
            cmd_string = cmd
            self._validate_add_command(cmd_string)
            # cmd_string = cmd_string.lower() if not case_sensitive else cmd_string
            # self._commands[cmd_string] = command_value
            self._commands.append(Command(cmd_string, **kwargs))
        elif isinstance(cmd, list):
            if len(cmd) == 1:
                cmd_string = cmd[0]
                self._validate_add_command(cmd_string)
                # cmd_string = cmd_string.lower() if not case_sensitive else cmd_string
                # self._commands[cmd_string] = command_value
                self._commands.append(Command(cmd_string, **kwargs))
            else:
                self._validate_command_system_path(cmd[0])
                self._commands[cmd[0]]['command_system'].add_command(cmd[1:], **kwargs)
        else:
            raise ValueError('First argument has to be a string or a list when adding a command.')

    def add_command_system(self, cmd_string_or_system, cmd_system_help=None, check_perms=None, case_sensitive=False):
        """Adds a command system within the current command system"""
        self._validate_add_command(cmd_string_or_system)
        cmd_system = cmd_string_or_system
        if not isinstance(cmd_string_or_system, CommandSystem):
            cmd_string = cmd_string_or_system
            cmd_system = CommandSystem(cmd_string,
                cmd_system_help=cmd_system_help,
                check_perms=check_perms,
                case_sensitive=case_sensitive)
        self._commands.append(cmd_system)
        # command_system_value = {'command_system': cmd_system, 'help': help_summary, 'case_sensitive': case_sensitive}
        # if check_perms:
        #     command_system_value['check_perms'] = check_perms
        # self._validate_add_command(cmd_string)
        # self._commands[cmd_string] = command_system_value

    async def execute(self, cmd_to_execute, *args, **kwargs):
        """Executes the desired command (whether it is within child command system or not) with arguments"""
        cmd_args = cmd_to_execute.split(' ')
        cmd = self._lookup_cmd(cmd_args[0]) if len(cmd_args) > 0 else None
        if cmd:
            if self._validate_permissions(cmd, args, kwargs):
                if 'func' in cmd and callable(cmd['func']):
                    return await cmd['func'](*args, **kwargs)
                elif 'command_system' in cmd and isinstance(cmd['command_system'], CommandSystem):
                    return await cmd['command_system'].execute(' '.join(cmd_args[1:]), *args, **kwargs)
                else:
                    return 'Error could not find a callable in the command object.'
            else:
                return 'Error insufficient permissions for this command.'
        else:
            if self._cmd_term:
                return 'Unknown ' + self._cmd_term + ' system command. Use "help" to get a list of commands.'
            return 'Unknown command. Use "help" to get a list of commands.'

    def _gen_help(self, args, prefix=''):
        """Generates the help for the command system"""
        help_message = 'Showing help:'
        if self._cmd_term:
            help_message = 'Showing help for ' + self._cmd_term + ': '
        for cmd in self._commands:
            if self._validate_permissions(cmd, args):
                help_summary = cmd.get_individual_help(args)
                help_message += '\n`' + prefix + str(cmd) + '`: ' + help_summary
        return help_message + '\nTo learn more about a command, use `help <command>`'

    def get_help(self, help_cmd, *args, prefix=''):
        """Makes the help for this command system/a child command system and messages it back"""
        cmd_args = help_cmd.split(' ')
        new_prefix = prefix + self._cmd_term + ' '
        cmd = self._lookup_cmd(cmd_args[0]) if cmd_args else None
        if cmd:
            if isinstance(cmd, CommandSystem):
                return cmd['command_system'].get_help(' '.join(cmd_args[1:]), *args, prefix=new_prefix)
            else:
                return cmd.get_individual_help(args, help_full=True)
        elif not cmd_args or cmd_args == ['']:
            return self._gen_help(args, prefix=new_prefix)
        else:
            return 'Unknown command. Use "help" to get a list of commands.'
