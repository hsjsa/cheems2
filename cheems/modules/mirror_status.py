from telegram.ext import CommandHandler
from cheems import dispatcher, status_reply_dict, DOWNLOAD_STATUS_UPDATE_INTERVAL, status_reply_dict_lock
from cheems.halper.telegram_halper.message_utils import *
from time import sleep
from cheems.halper.ext_utils.cheems_utils import get_readable_message
from telegram.error import BadRequest
from cheems.halper.telegram_halper.filters import CustomFilters
from cheems.halper.telegram_halper.cheems_commands import cheemsCommands
import threading

def mirror_status(update,context):
    message = get_readable_message()
    if len(message) == 0:
        message = "No active downloads"
        reply_message = sendMessage(message, context.cheems, update)
        threading.Thread(target=auto_delete_message, args=(cheems, update.message, reply_message)).start()
        return
    index = update.effective_chat.id
    with status_reply_dict_lock:
        if index in status_reply_dict.keys():
            deleteMessage(cheems, status_reply_dict[index])
            del status_reply_dict[index]
    sendStatusMessage(update,context.cheems)
    deleteMessage(context.cheems,update.message)


mirror_status_handler = CommandHandler(cheemsCommands.StatusCommand, mirror_status,
                                       filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(mirror_status_handler)
