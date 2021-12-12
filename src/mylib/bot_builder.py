"""Creates bot business logic"""

import logging
from datetime import datetime
from typing import Dict

from . import (
    database,
    resources as rss,
    messages as msg
)

from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# ========================== login conversation ========================================
# login conversation states:
PRE_REGISTER, REGISTER_CHIP, REGISTER_EMAIL, COMPLETE_SURVEY, POST_SURVEY = range(5)


def start(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(msg.ru.START_MESSAGE)
    return login(update, _)


def login(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(msg.ru.ASK_CHIP_ID)
    return REGISTER_CHIP


def register_chip(update: Update, _: CallbackContext) -> int:
    chip = update.message.text
    if not rss.HEX_INT_REGEX.match(chip):
        update.message.reply_text(msg.ru.CHIP_ID_MALFORMED)
        return REGISTER_CHIP
    chip_int = int(chip, 16)
    if chip_int not in rss.valid_chips:
        update.message.reply_text(msg.ru.CHIP_ID_INVALID.format(chip))
        return REGISTER_CHIP
    try:
        database.db_write(database.ChipData(update.effective_user.id, chip_int))
        update.message.reply_text(msg.ru.CHIP_SUCCESSFULLY_REGISTERED.format(chip_int))
        update.message.reply_text(msg.ru.ASK_EMAIL)
        return REGISTER_EMAIL
    except Exception as e:
        update.message.reply_text(msg.ru.CHIP_ID_REGISTRATION_ERROR)
        logging.getLogger(__name__).info(f"{e}")
        return REGISTER_CHIP


def register_email(update: Update, _: CallbackContext) -> int:
    email = update.message.text
    if not rss.EMAIL_REGEX.match(email):
        update.message.reply_text(msg.ru.EMAIL_MALFORMED.format(email))
        return REGISTER_EMAIL
    try:
        database.db_write(database.EmailData(update.effective_user.id, email))
        update.message.reply_text(msg.ru.EMAIL_SUCCESSFULLY_REGISTERED.format(email))
        return survey(update, _)
    except Exception as e:
        update.message.reply_text(msg.ru.EMAIL_REGISTRATION_ERROR)
        logging.getLogger(__name__).info(f"{e}")
        return REGISTER_EMAIL


def register_email_skip(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(msg.ru.EMAIL_SKIPPED)
    return survey(update, _)


def survey(update: Update, _: CallbackContext) -> int:
    chip_data = database.db_read_user(update.effective_user.id)
    if chip_data is None:
        update.message.reply_text(msg.ru.CHIP_ID_UNREGISTERED)
        update.message.reply_text(msg.ru.ASK_CHIP_ID)
        return REGISTER_CHIP
    update.message.reply_text(msg.ru.ASK_TO_COMPLETE_SURVEY.format(
            SURVEY_URL=rss.SURVERY_URL.format(chip_id=chip_data.chip)))
    return COMPLETE_SURVEY


def cancel_dialog(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(msg.ru.CONVERSATION_CANCELLED)
    return ConversationHandler.END


def dialog_complete(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(msg.ru.LOGIN_COMPLETE)
    update.message.reply_text(msg.ru.HELP_MESSAGE)
    return ConversationHandler.END


def login_conversation() -> ConversationHandler:
    start_h = CommandHandler("start", start)
    login_h = CommandHandler("login", login)
    chip_h = MessageHandler(Filters.text & (~Filters.command), register_chip)
    email_h = MessageHandler(Filters.text & (~Filters.command), register_email, run_async=True)
    email_skip_h = CommandHandler("skip", register_email_skip, run_async=True,)
    survey_h = CommandHandler("survey", survey, run_async=True)
    end_h = CommandHandler("ok", dialog_complete)
    cancel_h = CommandHandler("cancel", cancel_dialog)
    return ConversationHandler(
        entry_points=[start_h, login_h, survey_h],
        states={
            PRE_REGISTER: [login_h, ],
            REGISTER_CHIP: [chip_h, ],
            REGISTER_EMAIL: [email_h, email_skip_h],
            COMPLETE_SURVEY: [end_h],
            # POST_SURVEY: [],
        },
        fallbacks=[cancel_h],
        allow_reentry=True,
    )


# ====================== action conversation =====================================
REGISTER_ACTION, CONFIRM_ACTION = range(2)
YES = "y"
NO = "n"

pending_action_data: Dict[int, database.ActionData] = dict()


def start_action_conversation(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(msg.ru.ACTION_CONVERSATION_HELP)
    return REGISTER_ACTION


def parse_action_data(user: int, s: str) -> database.ActionData:
    chunks = s.split()
    action: database.actions = msg.ru.STRINGS_TO_ACTIONS[chunks[0]]
    amount = float(chunks[1])
    return database.ActionData(user, datetime.now(), action, amount)


def localize_action_data(ad: database.ActionData) -> str:
    return f"{ad.time.strftime(rss.DATETIME_FMT)}: {msg.ru.ACTIONS_TO_STRINGS[ad.action]} {ad.amount}"


def register_action(update: Update, _: CallbackContext) -> int:
    try:
        ad = parse_action_data(update.effective_user.id, update.message.text)
        pending_action_data[update.effective_user.id] = ad
        # reading past messages is not supported or not well-documented, so we need to store them
        update.message.reply_text(msg.ru.ACTION_READY_TO_BE_REGISTERED.format(
            action_data=localize_action_data(ad), yes=YES, no=NO))
        return CONFIRM_ACTION
    except (IndexError, ValueError, KeyError) as e:  # ad is an error message (str)
        update.message.reply_text(msg.ru.ACTION_COMMAND_MALFORMED)
        logging.getLogger(__name__).debug(f"[{update.message.text}] parsing failed with:", exc_info=e)
        return REGISTER_ACTION


def confirm_action_registration(update: Update, _: CallbackContext) -> int:
    cmd = update.message.text[1:]
    user = update.effective_user.id
    if cmd == YES:
        database.db_write(pending_action_data.pop(user))
        # retrieves message from temporary storage and registers it
        update.message.reply_text(msg.ru.ACTION_REGISTERED)
        return ConversationHandler.END
    elif cmd == NO:
        pending_action_data.pop(user)
        update.message.reply_text(msg.ru.ACTION_CANCELED)
        return ConversationHandler.END
    else:
        update.message.reply_text(msg.ru.UNKNOWN_COMMAND)
        return CONFIRM_ACTION


def help_action_conversation(update: Update, _: CallbackContext) -> int:
    if update.message.text == "/help":
        update.message.reply_text(msg.ru.ACTION_REGISTRATION_HELP_MESSAGE)
    # elif update.message.text == "/cancel":  # this is ridiculous!
    #     return cancel_dialog(update, _)
    # else:
    #     update.message.reply_text(msg.ru.UNKNOWN_COMMAND)
    return REGISTER_ACTION


def action_conversation() -> ConversationHandler:
    start_h = CommandHandler("action", start_action_conversation)
    help_h = CommandHandler("help", help_action_conversation)
    register_hs = [MessageHandler(Filters.text & (~ Filters.command), register_action), ]
    confirm_hs = [CommandHandler(c, confirm_action_registration) for c in (YES, NO)]
    cancel_h = CommandHandler("cancel", cancel_dialog)
    unknown_h = MessageHandler(Filters.all, unknown_command)
    return ConversationHandler(
        entry_points=[start_h],
        states={
            REGISTER_ACTION: register_hs + [help_h, ],
            CONFIRM_ACTION: confirm_hs,
        },
        fallbacks=[cancel_h, unknown_h],
        allow_reentry=True,
    )


def help_command(update: Update, _: CallbackContext):
    update.message.reply_text(msg.ru.HELP_MESSAGE)


def unknown_command(update: Update, _: CallbackContext):
    update.message.reply_text(msg.ru.UNKNOWN_COMMAND)


def build_bot(updater: Updater) -> Updater:
    dispatcher = updater.dispatcher
    dispatcher.add_handler(login_conversation())
    dispatcher.add_handler(action_conversation())
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.all, unknown_command))
    return updater
