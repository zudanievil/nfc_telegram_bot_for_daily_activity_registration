"""Creates bot business logic"""

import logging
from datetime import datetime
from functools import partial
from typing import (
    Dict,
    Optional,
    Generic,
    TypeVar,
)
from telegram import (
    Update,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

from . import (
    database,
    resources as rss,
    messages as msg
)

# ====================== helper classes ===========================================
_T = TypeVar("_T")


class DictKeys(Generic[_T]):
    __slots__ = "options",

    def __init__(self, options: Dict[str, _T]):
        self.options = options

    def to_keyboard(self, one_time=True, placeholder: Optional[str] = msg.ru.CHOOSE_OPTION) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            [(k,) for k in self.options.keys()],
            one_time_keyboard=one_time,
            input_field_placeholder=placeholder
        )

    def parse(self, s: str) -> Optional[_T]:
        """:returns None if s does not match options else corresponding value"""
        try:
            return self.options[s]
        except KeyError:
            return None

    def to_filter(self) -> Filters:
        return Filters.text(self.options.keys())


# ========================== generic commands, handlers ==========================================
START_CMD, SKIP_CMD, CANCEL_CMD = "start", "next", "cancel"


def cancel_dialog(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(msg.ru.CONVERSATION_CANCELLED)
    return main_menu(update, _)


def unknown_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(msg.ru.UNKNOWN_COMMAND)


CANCEL_HANDLER = CommandHandler(CANCEL_CMD, cancel_dialog)
UNKNOWN_COMMAND = MessageHandler(Filters.all, unknown_command)


# =========================== main bot menu =============================================


MAIN_MENU_KEYS = DictKeys(dict.fromkeys((
    msg.ru.REGISTER_ACTION,
    msg.ru.COMPLETE_SURVEY,
    msg.ru.LOGIN,
)))


def main_menu(update: Update, _: CallbackContext) -> int:
    """! always :returns :class:`ConversationHandler.END`"""
    update.message.reply_text(
        msg.ru.MAIN_MENU,
        reply_markup=MAIN_MENU_KEYS.to_keyboard(one_time=False)
    )
    return ConversationHandler.END


def start_the_bot(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(msg.ru.START_MESSAGE)
    return login_pre(update, _)


# ========================== login conversation ========================================
PRE, CHIP, EMAIL, SURVEY = 1, 2, 3, 4  # conversation states


def login_pre(update: Update, _: CallbackContext) -> int:
    update.message.reply_markdown(msg.ru.LOGIN_CHIP_ASK)
    return CHIP


def login_chip(update: Update, _: CallbackContext) -> Optional[int]:
    chip = update.message.text
    if not rss.CHIP_ID_REGEX.match(chip):
        update.message.reply_text(msg.ru.LOGIN_CHIP_INPUT_ERR)
        return  # same step
    chip = int(chip)
    if chip not in rss.valid_chips:
        update.message.reply_text(msg.ru.LOGIN_CHIP_INVALID_ID.format(chip))
        return
    try:
        database.db_write(database.ChipData(update.effective_user.id, chip))
        update.message.reply_text(msg.ru.LOGIN_CHIP_COMPLETE.format(chip))
        update.message.reply_text(msg.ru.LOGIN_EMAIL_ASK.format(skip_cmd=SKIP_CMD))
        return EMAIL
    except Exception as e:
        update.message.reply_text(msg.ru.LOGIN_CHIP_PROG_ERR)
        logging.getLogger(__name__).critical(f"{e}")
        return


def login_email(update: Update, _: CallbackContext) -> Optional[int]:
    email = update.message.text
    if not rss.EMAIL_REGEX.match(email):
        update.message.reply_text(msg.ru.LOGIN_EMAIL_INPUT_ERR.format(email))
        return
    try:
        database.db_write(database.EmailData(update.effective_user.id, email))
        update.message.reply_text(msg.ru.LOGIN_EMAIL_COMPLETE.format(email))
        return login_survey(update, _)
    except Exception as e:
        update.message.reply_text(msg.ru.LOGIN_EMAIL_PROG_ERR)
        logging.getLogger(__name__).critical(f"{e}")
        return


def login_email_skip(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(msg.ru.LOGIN_EMAIL_SKIPPED)
    return login_survey(update, _)


def login_survey(update: Update, _: CallbackContext) -> int:
    chip_data = database.db_read_user(update.effective_user.id)
    if chip_data is None:
        update.message.reply_text(msg.ru.LOGIN_SURVEY_CHIP_UNREGISTERED)
        return login_pre(update, _)
    update.message.reply_markdown(
        msg.ru.LOGIN_SURVEY_ASK.format(
            SURVEY_URL=rss.SURVERY_URL.format(chip_id=chip_data.chip),
            skip_cmd=SKIP_CMD
        ),
        disable_web_page_preview=True,
    )
    return SURVEY


def login_complete(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(msg.ru.LOGIN_COMPLETE)
    return main_menu(update, _)


def build_login_conversation() -> ConversationHandler:
    start_h = CommandHandler(START_CMD, start_the_bot)
    login_h = MessageHandler(Filters.text([msg.ru.LOGIN]), login_pre)
    email_h = MessageHandler(Filters.text & (~Filters.command(SKIP_CMD)), login_email, run_async=True)
    email_skip_h = CommandHandler(SKIP_CMD, login_email_skip, run_async=True, )
    survey_h = MessageHandler(Filters.text([msg.ru.COMPLETE_SURVEY, ]), login_survey, run_async=True)
    return ConversationHandler(
        entry_points=[start_h, login_h, survey_h],
        states={
            PRE: [login_h, ],
            CHIP: [MessageHandler(Filters.text, login_chip), ],
            EMAIL: [email_h, email_skip_h],
            SURVEY: [CommandHandler(SKIP_CMD, login_complete)],
        },
        fallbacks=[CANCEL_HANDLER],
        allow_reentry=True,
    )


# ====================== action conversation =====================================
REGISTER, CONFIRM = 1, 2

pending_action_data: Dict[int, database.ActionData] = dict()

ACTION_KEYS = DictKeys(msg.ru.STR_TO_ACTIONS)
YES_NO_KEYS = DictKeys({msg.ru.YES: True, msg.ru.NO: False})


def action_start(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        msg.ru.ACTION_START,
        reply_markup=ACTION_KEYS.to_keyboard()
    )
    return REGISTER


def localize_action_data(ad: database.ActionData) -> str:
    return f"`{msg.ru.ACTIONS_TO_STR[ad.action]} ({ad.time.strftime(rss.DATETIME_FMT)})`"


def action_register(update: Update, _: CallbackContext) -> int:
    ad = database.ActionData(update.effective_user.id, datetime.now(), ACTION_KEYS.parse(update.message.text))
    pending_action_data[update.effective_user.id] = ad
    # reading past messages is not supported or not well-documented, so we need to store them
    update.message.reply_markdown(
        msg.ru.ACTION_CONFIRMATION_ASK.format(action_data=localize_action_data(ad)),
        reply_markup=YES_NO_KEYS.to_keyboard(),
    )
    return CONFIRM


def action_confirm(update: Update, _: CallbackContext) -> int:
    if YES_NO_KEYS.parse(update.message.text):
        database.db_write(pending_action_data.pop(update.effective_user.id))
        update.message.reply_text(msg.ru.ACTION_CONFIRMED)
    else:
        pending_action_data.pop(update.effective_user.id)
        update.message.reply_text(msg.ru.ACTION_CANCELED)
    return main_menu(update, _)


def build_action_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[MessageHandler(Filters.text(msg.ru.REGISTER_ACTION), action_start)],
        states={
            REGISTER: [MessageHandler(ACTION_KEYS.to_filter(), action_register), ],
            CONFIRM: [MessageHandler(YES_NO_KEYS.to_filter(), action_confirm), ],
        },
        fallbacks=[CANCEL_HANDLER, UNKNOWN_COMMAND],
        allow_reentry=True,
    )


def senddoc(update: Update, _: CallbackContext, password=None) -> None:
    try:
        _, fname, passw = update.message.text.split()
        fname = rss.STORAGE_PATH / fname
        assert passw == password and fname.exists()
        with fname.open("rb") as f:
            update.message.reply_document(f, disable_content_type_detection=True)
    except Exception as e:
        logging.getLogger(__name__).critical(f"attempt to download file pass={passw}, f={fname}", exc_info=e)
        return unknown_command(update, _)


def build_bot(updater: Updater, password=None) -> Updater:
    dispatcher = updater.dispatcher
    dispatcher.add_handler(build_login_conversation())
    dispatcher.add_handler(build_action_conversation())
    if password is not None:
        dispatcher.add_handler(
            MessageHandler(Filters.command("senddoc") & Filters.text, partial(senddoc, password=password)))
    dispatcher.add_handler(UNKNOWN_COMMAND)
    return updater
