import logging
import os
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from generator import Generator

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
messages = dict()


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
    Generate midi with chords set:
    
    1. create chordset, e.g.: 
       /chords Am Dm E
       Only 9 chords are available in chordset!
       
    2. (optional) set tempo, e.g.: 
       /tempo 96
       
    3. (optional) set size, e.g.: 
       /size 1/4
       
    4. write melody string, e.g.: 
       1...2---3.3.
       . means "no sound" / "stop chord"
       - means "sustain on" / "keep playing chord"
       1-9 are the chords, by order starting from 1 (1 is Am for "Am Dm E")
    
    5. Open MIDI file in your preferred DAW 
    """
    update.message.reply_text(help_text)


class ChordBot:

    user_settings = dict()

    @classmethod
    def _get_generator(cls, user):
        if cls.user_settings.get(user) is None:
            cls.user_settings[user] = Generator()
        return cls.user_settings[user]

    @classmethod
    def set_chords(cls, update: Update, context: CallbackContext):
        gen = cls._get_generator(update.effective_user)
        gen.set_chords(' '.join(context.args))

    @classmethod
    def set_tempo(cls, update: Update, context: CallbackContext):
        gen = cls._get_generator(update.effective_user)
        gen.set_tempo(' '.join(context.args))

    @classmethod
    def set_size(cls, update: Update, context: CallbackContext):
        gen = cls._get_generator(update.effective_user)
        gen.set_size(' '.join(context.args))

    @classmethod
    def get_midi(cls, update: Update, context: CallbackContext):
        melody_str = update.message.text
        gen = cls._get_generator(update.effective_user)
        if not gen.chords:
            update.message.reply_text('Please make chordset first ("/chords Am Dm...")')
        update.message.reply_document(gen.midi(melody_str), filename='{}.mid'.format(melody_str))


def main() -> None:
    """Start the bot."""
    updater = Updater(os.environ.get("chord_bot_token"))
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("chords", ChordBot.set_chords))
    dispatcher.add_handler(CommandHandler("tempo", ChordBot.set_tempo))
    dispatcher.add_handler(CommandHandler("size", ChordBot.set_size))
    dispatcher.add_handler(MessageHandler(Filters.text, ChordBot.get_midi))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
