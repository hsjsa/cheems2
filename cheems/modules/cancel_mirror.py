from telegram.ext import CommandHandler

from cheems import download_dict, dispatcher, download_dict_lock, DOWNLOAD_DIR
from cheems.halper.ext_utils.fs_utils import clean_download
from cheems.halper.telegram_halper.cheems_commands import cheemsCommands
from cheems.halper.telegram_halper.filters import CustomFilters
from cheems.halper.telegram_halper.message_utils import *

from time import sleep
from cheems.halper.ext_utils.cheems_utils import getDownloadByGid, MirrorStatus


def cancel_mirror(update, context):
    args = update.message.text.split(" ", maxsplit=1)
    mirror_message = None
    if len(args) > 1:
        gid = args[1]
        dl = getDownloadByGid(gid)
        if not dl:
            sendMessage(f"GID: <code>{gid}</code> not found.", context.cheems, update)
            return
        with download_dict_lock:
            keys = list(download_dict.keys())
        mirror_message = dl.message
    elif update.message.reply_to_message:
        mirror_message = update.message.reply_to_message
        with download_dict_lock:
            keys = list(download_dict.keys())
            dl = download_dict[mirror_message.message_id]
    if len(args) == 1:
        if mirror_message is None or mirror_message.message_id not in keys:
            if cheemsCommands.MirrorCommand in update.message.text or \
                    cheemsCommands.TarMirrorCommand in update.message.text:
                msg = "Mirror already have been cancelled"
                sendMessage(msg, context.cheems, update)
                return
            else:
                msg = f"Please reply to the <code>/{cheemsCommands.MirrorCommand}</code> message which was used to start the download or <code>/{cheemsCommands.CancelMirror} GID</code> to cancel it!"
                sendMessage(msg, context.cheems, update)
                return
    if dl.status() == "Uploading":
        sendMessage("Upload in Progress, Don't Cancel it.", context.cheems, update)
        return
    elif dl.status() == "Archiving":
        sendMessage("Archival in Progress, Don't Cancel it.", context.cheems, update)
        return
    else:
        dl.download().cancel_download()
    sleep(1)  # Wait a Second For Aria2 To free Resources.
    clean_download(f'{DOWNLOAD_DIR}{mirror_message.message_id}/')


def cancel_all(update, context):
    with download_dict_lock:
        count = 0
        for dlDetails in list(download_dict.values()):
            if dlDetails.status() == MirrorStatus.STATUS_DOWNLOADING \
                    or dlDetails.status() == MirrorStatus.STATUS_WAITING:
                dlDetails.download().cancel_download()
                count += 1
    delete_all_messages()
    sendMessage(f'Cancelled {count} downloads!', context.cheems, update)


cancel_mirror_handler = CommandHandler(cheemsCommands.CancelMirror, cancel_mirror,
                                       filters=(CustomFilters.authorized_chat | CustomFilters.authorized_user) & CustomFilters.mirror_owner_filter, run_async=True)
cancel_all_handler = CommandHandler(cheemsCommands.CancelAllCommand, cancel_all,
                                    filters=CustomFilters.owner_filter, run_async=True)
dispatcher.add_handler(cancel_all_handler)
dispatcher.add_handler(cancel_mirror_handler)
