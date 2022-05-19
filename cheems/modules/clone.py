from telegram.ext import CommandHandler
from cheems.halper.mirror_utils.upload_utils.gdriveTools import GoogleDrivehalper
from cheems.halper.telegram_halper.message_utils import *
from cheems.halper.telegram_halper.filters import CustomFilters
from cheems.halper.telegram_halper.cheems_commands import cheemsCommands
from cheems.halper.ext_utils.cheems_utils import new_thread
from cheems import dispatcher


def cloneNode(update,context):
    args = update.message.text.split(" ",maxsplit=1)
    if len(args) > 1:
        link = args[1]
        msg = sendMessage(f"Cloning: <code>{link}</code>",context.cheems,update)
        gd = GoogleDrivehalper()
        result, button = gd.clone(link)
        deleteMessage(context.cheems,msg)
        if button == "":
            sendMessage(result,context.cheems,update)
        else:
            sendMarkup(result,context.cheems,update,button)
    else:
        sendMessage("Provide G-Drive Shareable Link to Clone.",context.cheems,update)

clone_handler = CommandHandler(cheemsCommands.CloneCommand,cloneNode,filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(clone_handler)
