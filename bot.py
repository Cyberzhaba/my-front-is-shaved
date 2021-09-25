import telebot
import config
from req import Request
from telebot.types import ReplyKeyboardMarkup


class Bot:

    def __init__(self):

        self.bot = telebot.TeleBot(token=config.token)
        self.req = Request()

        self.main_menu_keyb = ReplyKeyboardMarkup(row_width=1)
        self.main_menu_keyb.row('Аккаунт')
        self.main_menu_keyb.row('Купить токен')
        self.main_menu_keyb.row('История')
        self.go_back = ReplyKeyboardMarkup(row_width=1)
        self.go_back.row('<= Назад в меню')

    def mainloop(self):

        def get_step(msg):
            if msg.text == '<= Назад в меню':
                main_menu(msg)
            self.bot.send_message(msg.chat.id, 'Мне похй я шагаю от тебя')
            self.bot.send_message(msg.chat.id, 'Поздравляю я все добавил', reply_markup=self.go_back)


        def get_max_bid(msg):
            if msg.text == '<= Назад в меню':
                main_menu(msg)
            message = self.bot.send_message(msg.chat.id, 'Да, мне побать, поставлю мин ставку - весь твой бюджет', reply_markup=self.go_back)
            self.bot.register_next_step_handler(message, get_step)

        def get_link(msg):
            if msg.text == '<= Назад в меню':
                main_menu(msg)
            message = self.bot.send_message(msg.chat.id, 'Ага спасибо, я ее все равно не запомнил, я же сказал, мне похуй', reply_markup=self.go_back)
            self.bot.register_next_step_handler(message, get_max_bid)

        @self.bot.message_handler(commands=['start'])
        def main_commands(msg):
            if self.req.create_user(msg.from_user.id):
                self.bot.send_message(msg.chat.id, 'Мы вас зарегестрировали, вот ваша сид фраза:\n',
                                      reply_markup=self.main_menu_keyb)
            else:
                self.bot.send_message(msg.chat.id, 'Это команда для создания юзера, ты блять ее писал\n'
                                                   'Ты хули меня выводишь, не шути так со мной, пидарас',
                                      reply_markup=self.main_menu_keyb)

        @self.bot.message_handler(func=lambda msg: True)
        def main_menu(msg):
            if msg.text == 'Аккаунт':
                user = self.req.get_user(msg.from_user.id)
                n = '\n'
                to_send = f'Ващ user_id: {user["user_id"]}\n\n' \
                          f'Ваша сид фраза:\n' \
                          f'{n.join(str(str(i) + " - " + user["seed_fraze"][i]) for i in range(12))}\n\n' \
                          f'Ваши купленные токены:\n' \
                          f'{n.join(str(i) for i in user["owned_tokens"])}\n\n' \
                          f'Ваши токены находящиеся в процессе покупки:\n' \
                          f'{n.join(str(i) for i in user["buying_tokens"])}'
                self.bot.send_message(msg.chat.id, to_send, reply_markup=self.main_menu_keyb)
            elif msg.text == 'Купить токен':
                message = self.bot.send_message(msg.chat.id, 'А да мне похуй, кидай ссылку', reply_markup=self.go_back)
                self.bot.register_next_step_handler(message, get_link)
            elif msg.text == 'История':
                history = self.req.get_history(msg.from_user.id)
                n = '\n'
                to_send = 'История ваших действий в боте:\n' \
                          f'{n.join(history)}'
                self.bot.send_message(msg.chat.id, to_send)




        self.bot.polling()


if __name__ == '__main__':
    bot = Bot()
    bot.mainloop()
