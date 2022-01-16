"""Texts for messages"""
from ..database import actions

# ======= generic =======================
UNKNOWN_COMMAND = "Команда не распознана."
CANCEL = "Отмена"
CHOOSE_OPTION = "Выберите опцию:"
CONVERSATION_CANCELLED = "Диалог отменен."
YES = "Да"
NO = "Нет"


LOGIN = "Логин"
COMPLETE_SURVEY = "Опрос"
REGISTER_ACTION = "Регистрация действия"
MAIN_MENU = "Главное меню бота. Выберите действие."


START_MESSAGE = "Добрый день. Я -- бот для регистрации повседневных действий.\n" \
                "Для начала необходимо пройти регистрацию."

LOGIN_CHIP_ASK = "Пожалуйста, введите номер чипа из 4 цифр, например: `0987`"
LOGIN_CHIP_INPUT_ERR = "Формат номера чипа неправильный. Сообщение должно содержать " \
                       "только 4 цифры 0-9. Попробуйте еще раз."
LOGIN_CHIP_PROG_ERR = "При регистрации чипа произошла ошибка. Попробуйте ввести номер чипа еще раз."
LOGIN_CHIP_INVALID_ID = "Номер чипа {:04d} не действителен. Пожалуйста, введите другой номер."
LOGIN_CHIP_COMPLETE = "Чип {:04d} успешно зарегистрирован."

LOGIN_EMAIL_ASK = "Пожалуйста, укажите свой email. Вы можете пропустить данный шаг, нажав сюда: /{skip_cmd}"
LOGIN_EMAIL_INPUT_ERR = "Строка {} не разпознана как email-адрес. " \
                  "Попробуйте снова или пропустите этот шаг."
LOGIN_EMAIL_PROG_ERR = "При регистрации email произошла ошибка. Попробуйте ввести адрес еще раз." \
                           " или пропустите этот шаг."
LOGIN_EMAIL_SKIPPED = "Регистрация email-aдреса пропущена."
LOGIN_EMAIL_COMPLETE = "email-адрес {} успешно зарегистрирован."

LOGIN_SURVEY_ASK = "Пожалуйста, пройдите [короткий опрос]({SURVEY_URL}), это займет всего 5-7 минут.\n" \
                         "После прохождения опроса нажмите сюда: /{skip_cmd}"
LOGIN_SURVEY_CHIP_UNREGISTERED = "Пожалуйста, зарегистрируйте чип для данного пользователя перед прохождением опроса."

LOGIN_COMPLETE = "Поздравляем с успешным прохождением регистрации и опроса!"


ACTION_START = "Режим регистрации повседневных действий. Пожалуйста, укажите действие."
STR_TO_ACTIONS = {
    "углеводы": actions.food_carbo,
    "неуглеводы": actions.food_other,
    "спорт": actions.sport,
    "алкоголь": actions.alcohol,
    "кофеин": actions.caffeine,
    "никотин": actions.nicotine,
    "другое действие": actions.unlisted_action,
}
ACTIONS_TO_STR = {v: k for k, v in STR_TO_ACTIONS.items()}
ACTION_CONFIRMATION_ASK = \
    "Вы действительно хотите зарегистрировать: {action_data}?"
ACTION_CONFIRMED = "Действие успешно зарегистрировано."
ACTION_CANCELED = "Регистрация действия отменена."


ASK_ACTION_DESCRIPTION = "Пожалуйста, опишите в нескольких предложениях. Текст должен занимать одно сообщение."
DESCRIPTION_TEMPLATE = "описание: {}"
