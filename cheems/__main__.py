import os
import shutil, psutil
import signal

from sys import executable
import time

from telegram.ext import CommandHandler
from cheems import cheems, dispatcher, updater, cheemsStartTime
from cheems.halper.ext_utils import fs_utils
from cheems.halper.telegram_halper.cheems_commands import cheemsCommands
from cheems.halper.telegram_halper.message_utils import *
from .halper.ext_utils.cheems_utils import get_readable_file_size, get_readable_time
from .halper.telegram_halper.filters import CustomFilters
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, delete

from pyrogram import idle
from cheems import app


def stats(update, context):
    currentTime = get_readable_time(time.time() - cheemsStartTime)
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    stats = f'<b>cheems Uptime:</b> {currentTime}\n' \
            f'<b>Total disk space:</b> {total}\n' \
            f'<b>Used:</b> {used}  ' \
            f'<b>Free:</b> {free}\n\n' \
            f'📊Data Usage📊\n<b>Upload:</b> {sent}\n' \
            f'<b>Down:</b> {recv}\n\n' \
            f'<b>CPU:</b> {cpuUsage}% ' \
            f'<b>RAM:</b> {memory}% ' \
            f'<b>Disk:</b> {disk}%'
    sendMessage(stats, context.cheems, update)


def start(update, context):
    start_string = f'''
This is a cheems which can mirror all your links to Google drive!
Type /{cheemsCommands.HelpCommand} to get a list of available commands
'''
    sendMessage(start_string, context.cheems, update)


def restart(update, context):
    restart_message = sendMessage("Restarting, Please wait!", context.cheems, update)
    # Save restart message ID and chat ID in order to edit it after restarting
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    fs_utils.clean_all()
    os.execl(executable, executable, "-m", "cheems")


def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Starting Ping", context.cheems, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.cheems, update)


def cheems_help(update, context):
    help_string = f'''
/{cheemsCommands.HelpCommand}: To get this message

/{cheemsCommands.MirrorCommand} [download_url][magnet_link]: Start mirroring the link to google drive.\nPlzzz see this for full use of this command https://telegra.ph/Magneto-Python-Aria---Custom-Filename-Examples-01-20

/{cheemsCommands.UnzipMirrorCommand} [download_url][magnet_link] : starts mirroring and if downloaded file is any archive , extracts it to google drive

/{cheemsCommands.TarMirrorCommand} [download_url][magnet_link]: start mirroring and upload the archived (.tar) version of the download

/{cheemsCommands.WatchCommand} [youtube-dl supported link]: Mirror through youtube-dl. Click /{cheemsCommands.WatchCommand} for more help.

/{cheemsCommands.TarWatchCommand} [youtube-dl supported link]: Mirror through youtube-dl and tar before uploading

/{cheemsCommands.CancelMirror} : Reply to the message by which the download was initiated and that download will be cancelled

/{cheemsCommands.StatusCommand}: Shows a status of all the downloads

/{cheemsCommands.ListCommand} [search term]: Searches the search term in the Google drive, if found replies with the link

/{cheemsCommands.StatsCommand}: Show Stats of the machine the cheems is hosted on

/{cheemsCommands.AuthorizeCommand}: Authorize a chat or a user to use the cheems (Can only be invoked by owner of the cheems)

/{cheemsCommands.LogCommand}: Get a log file of the cheems. Handy for getting crash reports

'''
    sendMessage(help_string, context.cheems, update)


def main():
    fs_utils.start_cleanup()
    # Check if the cheems is restarting
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        cheems.edit_message_text("Restarted successfully!", chat_id, msg_id)
        os.remove(".restartmsg")

    start_handler = CommandHandler(cheemsCommands.StartCommand, start,
                                   filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    ping_handler = CommandHandler(cheemsCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    restart_handler = CommandHandler(cheemsCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter, run_async=True)
    help_handler = CommandHandler(cheemsCommands.HelpCommand,
                                  cheems_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    stats_handler = CommandHandler(cheemsCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    log_handler = CommandHandler(cheemsCommands.LogCommand, log, filters=CustomFilters.owner_filter, run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling()
    LOGGER.info("cheems Started!")
    signal.signal(signal.SIGINT, fs_utils.exit_clean_up)

app.start()
main()
idle()
