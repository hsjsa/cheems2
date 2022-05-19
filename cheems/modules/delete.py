from telegram.ext import CommandHandler
import threading
from telegram import Update
from cheems import dispatcher, LOGGER
from cheems.halper.telegram_halper.message_utils import auto_delete_message, sendMessage
from cheems.halper.telegram_halper.filters import CustomFilters
from cheems.halper.telegram_halper.cheems_commands import cheemsCommands
from cheems.halper.mirror_utils.upload_utils import gdriveTools

def deletefile(update, context):
	msg_args = update.message.text.split(None, 1)
	msg = ''
	try:
		link = msg_args[1]
		LOGGER.info(msg_args[1])
	except IndexError:
		msg = 'send a link along with command'

	if msg == '' : 
		drive = gdriveTools.GoogleDrivehalper()
		msg = drive.deletefile(link)
	LOGGER.info(f"this is msg : {msg}")
	reply_message = sendMessage(msg, context.cheems, update)

	threading.Thread(target=auto_delete_message, args=(context.cheems, update.message, reply_message)).start()

delete_handler = CommandHandler(command=cheemsCommands.deleteCommand, callback=deletefile,
									filters=CustomFilters.owner_filter, run_async=True)
dispatcher.add_handler(delete_handler)
