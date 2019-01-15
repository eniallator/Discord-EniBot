from time import gmtime, strftime


class Logger:
    def __init__(self, client, log_dest):
        self._client = client
        self._log_user = {'name': log_dest}

    def get_dest_name(self):
        return self._log_user['name']

    def set_member(self, member):
        self._log_user['member'] = member

    def _get_time(self):
        raw_time = strftime("%Y/%m/%d %H:%M:%S", gmtime())
        return '[' + raw_time + '] '

    async def _get_last_msg(self):
        if 'member' not in self._log_user:
            return

        await self._client.start_private_message(self._log_user['member'])
        for channel in self._client.private_channels:
            if len(channel.recipients) == 1 and channel.recipients[0].id == self._log_user['member'].id:
                log_channel = channel

        async for msg in self._client.logs_from(log_channel, limit=1):
            return msg

    async def log(self, msg_to_log, logging=True, first_log=False):
        timestamp_msg = self._get_time() + msg_to_log
        edit_last_msg = False

        if first_log:
            last_msg = await self._get_last_msg()
            if last_msg and last_msg.author.id == self._client.user.id and last_msg.content.startswith('-'):
                edit_last_msg = True
            else:
                timestamp_msg = '-' * 90 + '\n' + timestamp_msg

        print(timestamp_msg)

        if not logging:
            return

        if edit_last_msg:
            await self._client.edit_message(last_msg, last_msg.content + '\r\n' + timestamp_msg)
        elif 'member' in self._log_user:
            await self._client.send_message(self._log_user['member'], timestamp_msg)
