from evennia import default_cmds

class MyCustomChannelCmd(default_cmds.CmdChannel):
   # locks = "cmd: not pperm(channel_banned); admin:perm(Builder);manage:perm(Builder);changelocks:perm(Admin)"
    pass