from cheems.halper.telegram_halper.message_utils import sendMessage
from cheems import AUTHORIZED_CHATS, dispatcher
from telegram.ext import CommandHandler
from cheems.halper.telegram_halper.filters import CustomFilters
from telegram.ext import Filters
from telegram import Update
from cheems.halper.telegram_halper.cheems_commands import cheemsCommands


def authorize(update,context):
    reply_message = update.message.reply_to_message
    msg = ''
    with open('authorized_chats.txt', 'a') as file:
        if reply_message is None:
            # Trying to authorize a chat
            chat_id = update.effective_chat.id
            if chat_id not in AUTHORIZED_CHATS:
                file.write(f'{chat_id}\n')
                AUTHORIZED_CHATS.add(chat_id)
                msg = 'Chat authorized'
            else:
                msg = 'Already authorized chat'
        else:
            # Trying to authorize someone in specific
            user_id = reply_message.from_user.id
            if user_id not in AUTHORIZED_CHATS:
                file.write(f'{user_id}\n')
                AUTHORIZED_CHATS.add(user_id)
                msg = 'Person Authorized to use the cheems!'
            else:
                msg = 'Person already authorized'
        sendMessage(msg, context.cheems, update)


def unauthorize(update,context):
    reply_message = update.message.reply_to_message
    if reply_message is None:
        # Trying to unauthorize a chat
        chat_id = update.effective_chat.id
        if chat_id in AUTHORIZED_CHATS:
            AUTHORIZED_CHATS.remove(chat_id)
            msg = 'Chat unauthorized'
        else:
            msg = 'Already unauthorized chat'
    else:
        # Trying to authorize someone in specific
        user_id = reply_message.from_user.id
        if user_id in AUTHORIZED_CHATS:
            AUTHORIZED_CHATS.remove(user_id)
            msg = 'Person unauthorized to use the cheems!'
        else:
            msg = 'Person already unauthorized!'
    with open('authorized_chats.txt', 'a') as file:
        file.truncate(0)
        for i in AUTHORIZED_CHATS:
            file.write(f'{i}\n')
    sendMessage(msg, context.cheems, update)


authorize_handler = CommandHandler(command=cheemsCommands.AuthorizeCommand, callback=authorize,
                                   filters=CustomFilters.owner_filter & Filters.group, run_async=True)
unauthorize_handler = CommandHandler(command=cheemsCommands.UnAuthorizeCommand, callback=unauthorize,
                                     filters=CustomFilters.owner_filter & Filters.group, run_async=True)
dispatcher.add_handler(authorize_handler)
dispatcher.add_handler(unauthorize_handler)

