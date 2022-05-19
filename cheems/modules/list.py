from telegram.ext import CommandHandler
from cheems.halper.mirror_utils.upload_utils.gdriveTools import GoogleDrivehalper
from cheems import LOGGER, dispatcher
from cheems.halper.telegram_halper.message_utils import sendMessage, sendMarkup, editMessage
from cheems.halper.telegram_halper.filters import CustomFilters
from cheems.halper.telegram_halper.cheems_commands import cheemsCommands

def list_drive(update,context):
    try:
        search = update.message.text.split(' ',maxsplit=1)[1]
        LOGGER.info(f"Searching: {search}")
        reply = sendMessage('Searching..... Please wait!', context.cheems, update)
        gdrive = GoogleDrivehalper(None)
        msg, button = gdrive.drive_list(search)

        if button:
            editMessage(msg, reply, button)
        else:
            editMessage('No result found', reply, button)

    except IndexError:
        sendMessage('send a search key along with command', context.cheems, update)


list_handler = CommandHandler(cheemsCommands.ListCommand, list_drive,filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(list_handler)
