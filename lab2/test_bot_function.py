import unittest
from unittest.mock import Mock, patch
import bot_function

# Создание мок-объекта для TeleBot и message
bot_mock = Mock()
message_mock = Mock()

class TestNotoxicBot(unittest.TestCase):

    def setUp(self):
        # Сбрасывается состояние моков перед каждым тестом
        bot_mock.reset_mock()
        message_mock.reset_mock()
        # Устанавливаются базовые атрибуты для message_mock
        message_mock.chat.id = 123
        message_mock.from_user.id = 456
        message_mock.from_user.username = "test_user"

    def test_start_bot(self):
        # Тестируется команда /start
        bot_function.start_bot(bot_mock, message_mock)
        bot_mock.reply_to.assert_called_with(
            message_mock,
            "Привет! Я - бот для удаления токсичных комментариев и модерации сервера. Напиши /help, чтобы узнать больше."
        )

    def test_help_bot(self):
        # Тестирую команду /help
        bot_function.help_bot(bot_mock, message_mock)
        expected_message = (
            "Я - бот для удаления токсичных комментариев и модерации сервера.\n"
            "Я автоматически удаляю токсичные комментарии. Если человек ведет себя слишком токсично, "
            "я временно лишаю его возможности писать в чат.\n"
            "Все мои команды работают в ответ на сообщение пользователя, поэтому для ручной модерации "
            "требуется ввести команду в ответ на сообщение пользователя.\n"
            "Список команд: /mute - замутить пользователя, /unmute - размутить пользователя, /kick - кикнуть пользователя"
        )
        bot_mock.reply_to.assert_called_with(message_mock, expected_message)

    def test_mute_user_not_admin(self):
        # Тестируется мут обычного пользователя с 0 токсичных сообщений
        with patch('bot_function.num_toxcom', return_value=0):
            message_mock.from_user.id = 456
            bot_mock.get_chat_member.return_value.status = 'member'
            bot_function.mute_user(bot_mock, message_mock)
            bot_mock.restrict_chat_member.assert_called()
            bot_mock.reply_to.assert_called_with(message_mock, "Пользователь test_user замучен на 60 секунд.")

    def test_mute_user_admin(self):
        # Тестируется попытка замутить администратора
        bot_mock.get_chat_member.return_value.status = 'administrator'
        bot_function.mute_user(bot_mock, message_mock)
        bot_mock.reply_to.assert_called_with(message_mock, "Невозможно замутить администратора.")
        bot_mock.restrict_chat_member.assert_not_called()

    def test_kick_user_with_reply(self):
        # Тестируется кик пользователя с ответом на сообщение
        reply_message_mock = Mock()
        reply_message_mock.from_user.id = 789
        reply_message_mock.from_user.username = "bad_user"
        message_mock.reply_to_message = reply_message_mock
        bot_mock.get_chat_member.return_value.status = 'member'
        bot_function.kick_user(bot_mock, message_mock)
        bot_mock.kick_chat_member.assert_called_with(123, 789)
        bot_mock.reply_to.assert_called_with(message_mock, "Пользователь bad_user был кикнут.")

    def test_kick_user_no_reply(self):
        # Тестируется кик без ответа на сообщение
        message_mock.reply_to_message = None
        bot_function.kick_user(bot_mock, message_mock)
        bot_mock.reply_to.assert_called_with(
            message_mock,
            "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите кикнуть."
        )
        bot_mock.kick_chat_member.assert_not_called()

    def test_unmute_user_with_reply(self):
        # Тестируется unmute с ответом на сообщение
        reply_message_mock = Mock()
        reply_message_mock.from_user.id = 789
        reply_message_mock.from_user.username = "muted_user"
        message_mock.reply_to_message = reply_message_mock
        bot_function.unmute_user(bot_mock, message_mock)
        bot_mock.restrict_chat_member.assert_called_with(
            123, 789,
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
        bot_mock.reply_to.assert_called_with(message_mock, "Пользователь muted_user размучен.")

    def test_unmute_user_no_reply(self):
        # Тестируется unmute без ответа на сообщение
        message_mock.reply_to_message = None
        bot_function.unmute_user(bot_mock, message_mock)
        bot_mock.reply_to.assert_called_with(
            message_mock,
            "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите размутить."
        )
        bot_mock.restrict_chat_member.assert_not_called()

    def test_predict_bot_non_toxic(self):
        # Тестируется нетоксичное сообщение
        message_mock.text = "Привет, как дела?"
        model_mock = Mock()
        model_mock.predict.return_value = [0]
        with patch('bot_function.save_user'), patch('bot_function.log_message'):
            bot_function.predict_bot(bot_mock, message_mock, model_mock)
            bot_mock.delete_message.assert_not_called()
            bot_mock.send_message.assert_not_called()

    def test_predict_bot_toxic(self):
        # Тестируется токсичное сообщение
        message_mock.text = "Ты ужасен!"
        message_mock.message_id = 999
        model_mock = Mock()
        model_mock.predict.return_value = [1]
        with patch('bot_function.mute_user'), patch('bot_function.save_user'), patch('bot_function.log_message'):
            bot_function.predict_bot(bot_mock, message_mock, model_mock)
            bot_mock.delete_message.assert_called_with(123, 999)
            bot_mock.send_message.assert_called_with(
                456,
                "Ваше сообщение было удалено, так как оно определено как токсичное. Пожалуйста, соблюдайте правила общения."
            )

if __name__ == '__main__':
    unittest.main()