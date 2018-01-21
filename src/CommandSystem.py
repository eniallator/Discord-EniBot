class CommandSystem(object):
    """The command system class"""

    def __init__(self, system_name=''):
        self._system_name = system_name
        self._commands = {}

    def _lookup_cmd(self, cmd_string):
        """Looks up in the current command system to see if the cmd_string is a command already and returns it"""
        if cmd_string in self._commands:
            return self._commands[cmd_string]
        elif cmd_string.lower() in self._commands and not self._commands[cmd_string.lower()]['case_sensitive']:
            return self._commands[cmd_string.lower()]
        else:
            return None

    def _validate_add_command(self, cmd_string):
        """Validates the add command/command system methods"""
        if not isinstance(cmd_string, str) or not cmd_string:
            raise ValueError('Command needs to have 1 or more characters.')
        if self._lookup_cmd(cmd_string):
            raise ValueError('Command already exists.')

    def _validate_command_system_path(self, cmd_string):
        """Validates that the given command system exists"""
        if not isinstance(cmd_string, str) or not cmd_string:
            raise ValueError('Error when locating the path to the command system when adding a new command.')
        if not (self._lookup_cmd(cmd_string) and 'command_system' in self._commands[cmd_string]):
            raise ValueError('Could not find command system when adding a new command.')
    
    def _validate_permissions(self, cmd, list_args, dict_args=None):
        call_checker = lambda func, list_args, dict_args: func(*list_args, **dict_args) if dict_args else func(*list_args)
        if 'check_perms' in cmd and callable(cmd['check_perms']) and not call_checker(cmd['check_perms'], list_args, dict_args):
            return False
        return True

    def add_command(self, cmd, cmd_func=None, cmd_help=None, specific_help=None, check_perms=None, case_sensitive=False):
        """Adds a command to the current command system"""
        command_value = {'func': cmd_func, 'help': cmd_help, 'case_sensitive': case_sensitive}
        cmd_string = cmd.lower() if not case_sensitive else cmd
        if check_perms:
            command_value['check_perms'] = check_perms
        if specific_help:
            command_value['specific_help'] = specific_help
        if isinstance(cmd, str):
            cmd_string = cmd
            self._validate_add_command(cmd_string)
            self._commands[cmd_string] = command_value
        elif isinstance(cmd, list):
            if len(cmd) == 1:
                cmd_string = cmd[0]
                self._validate_add_command(cmd_string)
                self._commands[cmd_string] = command_value
            else:
                self._validate_command_system_path(cmd[0])
                self._commands[cmd[0]]['command_system'].add_command(cmd[1:], cmd_func=cmd_func, cmd_help=cmd_help, specific_help=specific_help, check_perms=check_perms, case_sensitive=case_sensitive)
        else:
            raise ValueError('First argument has to be a string or a list when adding a command.')

    def add_command_system(self, cmd_string, cmd_help=None, cmd_system=None, check_perms=None, case_sensitive=False):
        """Adds a command system within the current command system"""
        if not isinstance(cmd_system, CommandSystem):
            cmd_system = CommandSystem(cmd_string)
        command_system_value = {'command_system': cmd_system, 'help': cmd_help, 'case_sensitive': case_sensitive}
        if check_perms:
            command_system_value['check_perms'] = check_perms
        self._validate_add_command(cmd_string)
        self._commands[cmd_string] = command_system_value

    async def execute(self, cmd_to_execute, *list_args, **dict_args):
        """Executes the desired command (whether it is within child command system or not) with arguments"""
        cmd_args = cmd_to_execute.split(' ')
        cmd = self._lookup_cmd(cmd_args[0]) if len(cmd_args) > 0 else None
        if cmd:
            if self._validate_permissions(cmd, list_args, dict_args):
                if 'func' in cmd and callable(cmd['func']):
                    return await cmd['func'](*list_args, **dict_args)
                elif 'command_system' in cmd and isinstance(cmd['command_system'], CommandSystem):
                    return await cmd['command_system'].execute(' '.join(cmd_args[1:]), *list_args, **dict_args)
                else:
                    return 'Error could not find a callable in the command object.'
            else:
                return 'Error insufficient permissions for this command.'
        else:
            if self._system_name:
                return 'Unknown ' + self._system_name + ' system command. Use "help" to get a list of commands.'
            return 'Unknown command. Use "help" to get a list of commands.'

    def _get_cmd_help(self, cmd, list_args, specific_help=False):
        """Gets a command's help if it's specific_help or help and accepts callables or strings"""
        if specific_help and 'specific_help' in cmd and (isinstance(cmd['specific_help'], str) or callable(cmd['specific_help'])):
            return cmd['specific_help'](*list_args) if callable(cmd['specific_help']) else cmd['specific_help']
        elif 'help' in cmd and (isinstance(cmd['help'], str) or callable(cmd['help'])):
            return cmd['help'](*list_args) if callable(cmd['help']) else cmd['help']
        return 'Error could not find the command\'s help.'

    def _gen_help(self, list_args, prefix=''):
        """Generates the help for the command system"""
        help_message = 'Showing help:'
        if self._system_name:
            help_message = 'Showing help for ' + self._system_name + ': '
        for cmd_string in self._commands:
            if self._validate_permissions(self._commands[cmd_string], list_args):
                cmd_help = self._get_cmd_help(self._commands[cmd_string], list_args)
                help_message += '\n`' + prefix + cmd_string + '`: ' + cmd_help
        return help_message + '\nTo learn more about a command, use `help <command>`'

    def get_help(self, help_cmd, *list_args, prefix=''):
        """Makes the help for this command system/a child command system and messages it back"""
        cmd_args = help_cmd.split(' ')
        new_prefix = prefix + self._system_name + ' '
        cmd = self._lookup_cmd(cmd_args[0]) if len(cmd_args) > 0 else None
        if cmd:
            if 'command_system' in cmd:
                return cmd['command_system'].get_help(' '.join(cmd_args[1:]), *list_args, prefix=new_prefix)
            else:
                return self._get_cmd_help(cmd, list_args, specific_help=True)
        elif not cmd_args or cmd_args == ['']:
            return self._gen_help(list_args, prefix=new_prefix)
        else:
            return 'Unknown command. Use "help" to get a list of commands.'
