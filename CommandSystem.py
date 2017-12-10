class CommandSystem(object):
    """The command system class"""
    def __init__(self, system_name=''):
        self._system_name = system_name
        self._commands = {}

    def _validate_add_command(self, cmd_string):
        if not isinstance(cmd_string, str) or not cmd_string:
            raise ValueError('Command needs to have 1 or more characters.')
        if cmd_string in self._commands:
            raise ValueError('Command already exists.')

    def _validate_command_system_path(self, cmd_string):
        if not isinstance(cmd_string, str) or not cmd_string:
            raise ValueError('Error when locating the path to the command system when adding a new command.')
        if not (cmd_string in self._commands and 'command_system' in self._commands[cmd_string]):
            raise ValueError('Could not find command system when adding a new command.')

    def add_command(self, cmd, cmd_func=lambda client, user_cmd, message, iteration: {'output': ''}, cmd_help=lambda client, user_cmd, message: {'output': ''}, specific_help=None):
        command_value = {'func': cmd_func, 'help': cmd_help}
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
                self._commands[cmd[0]]['command_system'].add_command(cmd[1:], cmd_func=cmd_func, cmd_help=cmd_help, specific_help=specific_help)
        else:
            raise ValueError('First argument has to be a string or a list when adding a command.')
    
    def add_command_system(self, cmd_string, cmd_help=lambda client, user_cmd, message: {'output': ''}, cmd_system=None):
        if not isinstance(cmd_system, CommandSystem):
            cmd_system = CommandSystem(cmd_string)
        self._validate_add_command(cmd_string)
        self._commands[cmd_string] = {'command_system': cmd_system, 'help': cmd_help}
    
    async def execute(self, client, user_cmd, message, iteration):
        cmd_args = user_cmd.split(' ')
        if cmd_args and cmd_args[0] in self._commands:
            cmd = self._commands[cmd_args[0]]
            if 'func' in cmd:
                return await cmd['func'](client, user_cmd, message, iteration)
            elif 'command_system' in cmd:
                return await cmd['command_system'].execute(client, ' '.join(cmd_args[1:]), message, iteration)
            else:
                return {'output': 'Error could not find a callable in the command object.'}
        else:
            if self._system_name:
                return {'output': 'Unknown ' + self._system_name + ' system command. Use "help" to get a list of commands.'}
            return {'output': 'Unknown command. Use "help" to get a list of commands.'}
    
    def _gen_help(self, client, user_cmd, message):
        help_message = 'Showing help:'
        if self._system_name:
            help_message = 'Showing help for ' + self._system_name + ': '
        for cmd_string in self._commands:
            cmd_help = self._commands[cmd_string]['help'](client, user_cmd, message)
            help_message += '\n"' + cmd_string + '": ' + cmd_help
        return help_message + '\nTo learn more about a command, use "help <command>"'

    def get_help(self, client, user_cmd, message):
        cmd_args = user_cmd.split(' ')
        if cmd_args and cmd_args[0] in self._commands:
            cmd = self._commands[cmd_args[0]]
            if 'command_system' in cmd:
                return cmd['command_system'].get_help(client, ' '.join(cmd_args[1:]), message)
            elif 'specific_help' in cmd:
                return cmd['specific_help'](client, ' '.join(cmd_args[1:]), message)
            elif 'help' in cmd:
                return cmd['help'](client, ' '.join(cmd_args[1:]), message)
            else:
                return 'Error could not find the command\'s help.'
        elif not cmd_args or cmd_args == ['']:
            return self._gen_help(client, ' '.join(cmd_args[1:]), message)
        else:
            return 'Unknown command. Use "help" to get a list of commands.'
