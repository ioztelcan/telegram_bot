from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
import logging
from functools import wraps

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s (%(name)s)', level=logging.INFO)
logger = logging.getLogger(__name__)

LIST_OF_ADMINS = []

def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        user_lastname = update.effective_user.last_name
        user_is_bot = update.effective_user.is_bot
        user_username = update.effective_user.username
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for [{} {}] username: {} | id: {} | is_bot: {} | tried to execute: {}.".format(user_name, user_lastname, user_username, user_id, user_is_bot, func.__name__))
            return
        return func(update, context, *args, **kwargs)
    return wrapped

@restricted
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

class TelegramBot():
    def __init__(self, user_id, bot_token, error_handler=error):
        """
        user_id: User ID for bot's owner, becomes admin by default.
        bot_token: Token generated for the bot by telegram.
        error_handler: a function to act as error handler, uses local handler by default.
        """
        self.user_id = user_id
        self.token = bot_token
        LIST_OF_ADMINS.append(int(user_id))

        self.bot = telegram.Bot(token=self.token)
        self.bot.can_join_groups = True
        self.updater = Updater(token=self.token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_error_handler(error)

    def start(self):
        logger.info("Starting bot.")
        self.updater.start_polling()

    def stop(self):
        logger.info("Stopping bot.")
        self.updater.stop()

    def add_command(self, name, callback):
        logger.debug("Adding command handler: {}".format(callback.__name__))
        self.dispatcher.add_handler(CommandHandler(name, callback))

    def remove_command(self, callback):
        logger.debug("Removing command handler: {}".format(callback.__name__))
        self.dispatcher.remove_handler(callback)

    def get_commands(self):
        return self.dispatcher.handlers

    def add_error_handler(self, callback):
        """ Default error handler has to be removed first. """
        logger.debug("Adding error handler: {}".format(callback.__name__))
        self.dispatcher.add_error_handler(callback)

    def remove_error_handler(self, callback):
        logger.debug("Removing error handler: {}".format(callback.__name__))
        self.dispatcher.remove_error_handler(callback)

    def send_msg(self, msg, dest=None, parse_mode="Markdown"):
        if dest == None:
            dest = self.user_id
        self.bot.send_message(dest, msg, parse_mode=parse_mode)

    def add_admin(self, id):
        logger.info("Adding user: {} to admin list.".format(id))
        LIST_OF_ADMINS.append(id)

    def remove_admin(self, id):
        logger.info("Removing user: {} from admin list.".format(id))
        LIST_OF_ADMINS.remove(id)
