from telegram.ext import CommandHandler
from telegram import cheems, Update
from cheems import Interval, DOWNLOAD_DIR, DOWNLOAD_STATUS_UPDATE_INTERVAL, dispatcher, LOGGER
from cheems.halper.ext_utils.cheems_utils import setInterval
from cheems.halper.telegram_halper.message_utils import update_all_messages, sendMessage, sendStatusMessage
from .mirror import MirrorListener
from cheems.halper.mirror_utils.download_utils.youtube_dl_download_halper import YoutubeDLhalper
from cheems.halper.telegram_halper.cheems_commands import cheemsCommands
from cheems.halper.telegram_halper.filters import CustomFilters
import threading


def _watch(cheems: cheems, update, isTar=False):
    mssg = update.message.text
    message_args = mssg.split(' ')
    name_args = mssg.split('|')
    try:
        link = message_args[1]
    except IndexError:
        msg = f"/{cheemsCommands.WatchCommand} [yt_dl supported link] [quality] |[CustomName] to mirror with youtube_dl.\n\n"
        msg += "<b>Note :- Quality and custom name are optional</b>\n\nExample of quality :- audio, 144, 240, 360, 480, 720, 1080, 2160."
        msg += "\n\nIf you want to use custom filename, plz enter it after |"
        msg += f"\n\nExample :-\n<code>/{cheemsCommands.WatchCommand} https://youtu.be/ocX2FN1nguA 720 |My video bro</code>\n\n"
        msg += "This file will be downloaded in 720p quality and it's name will be <b>My video bro</b>"
        sendMessage(msg, cheems, update)
        return
    try:
      if "|" in mssg:
        mssg = mssg.split("|")
        qual = mssg[0].split(" ")[2]
        if qual == "":
          raise IndexError
      else:
        qual = message_args[2]
      if qual != "audio":
        qual = f'bestvideo[height<={qual}]+bestaudio/best[height<={qual}]'
    except IndexError:
      qual = "bestvideo+bestaudio/best"
    try:
      name = name_args[1]
    except IndexError:
      name = ""
    reply_to = update.message.reply_to_message
    if reply_to is not None:
        tag = reply_to.from_user.username
    else:
        tag = None
    pswd = ""
    listener = MirrorListener(cheems, update, pswd, isTar, tag)
    ydl = YoutubeDLhalper(listener)
    threading.Thread(target=ydl.add_download,args=(link, f'{DOWNLOAD_DIR}{listener.uid}', qual, name)).start()
    sendStatusMessage(update, cheems)
    if len(Interval) == 0:
        Interval.append(setInterval(DOWNLOAD_STATUS_UPDATE_INTERVAL, update_all_messages))


def watchTar(update, context):
    _watch(context.cheems, update, True)


def watch(update, context):
    _watch(context.cheems, update)


mirror_handler = CommandHandler(cheemsCommands.WatchCommand, watch,
                                filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
tar_mirror_handler = CommandHandler(cheemsCommands.TarWatchCommand, watchTar,
                                    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(mirror_handler)
dispatcher.add_handler(tar_mirror_handler)
