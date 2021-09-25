import telebot
import config
from req import Request
from telebot.types import ReplyKeyboardMarkup
import uuid
import validators
import time


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

        self.all_tokens = {}

    def mainloop(self):

        def verify_all(msg, uid):
            self.log_obj(msg, uid)
            if msg.text == '<= Назад в меню':
                main_menu(msg, True)
            else:
                t = msg.text.lower()
                self.all_tokens[msg.from_user.id][uid]['Verified'] = None
                if t == 'да' or t == 'д' or t == 'yes' or t == 'y':
                    self.all_tokens[msg.from_user.id][uid]['Verified'] = True
                    self.bot.send_message(msg.chat.id, 'Я добавил ваш токен в очередь')
                elif t == 'нет' or t == 'н' or t == 'no' or t == 'n':
                    self.all_tokens[msg.from_user.id][uid]['Verified'] = False
                    self.bot.send_message(msg.chat.id, 'Ваш токен не был добавлен в очередь, '
                                                       'напишите /start чтобы сново войти в меню и создать ордер '
                                                       'на покупку новго токена')
                else:
                    message = self.bot.send_message(msg.chat.id, 'Неправильный формат ответа, напишите да или нет')
                    self.bot.register_next_step_handler(message, lambda msg: verify_all(msg, uid))

        def get_step(msg, uid):
            self.log_obj(msg, uid)
            if msg.text == '<= Назад в меню':
                main_menu(msg, True)
            else:
                if msg.text.isdigit():
                    self.all_tokens[msg.from_user.id][uid]['step'] = msg.text
                    order = self.all_tokens[msg.from_user.id][uid]
                    to_send = f'Покупка ордера \n{order["link"]}\n' \
                              f'Максимальная цена = {order["max_bid"]}\n' \
                              f'Шаг ребида = {order["step"]} '
                    self.bot.send_message(msg.chat.id, to_send)
                    message = self.bot.send_message(msg.chat.id, 'Вы подтверждате данную покупку'
                                                       'напишите да/нет')
                    self.bot.register_next_step_handler(message, lambda msg: verify_all(msg, uid))

                else:
                    message = self.bot.send_message(msg.chat.id, 'Вы ввели минимальный шаг в неправильном формате\n'
                                                                 'Отправьте цену в формате числа без точек 777')
                    self.bot.register_next_step_handler(message, lambda msg: verify_all(msg, uid))

        def get_max_bid(msg, uid):
            self.log_obj(msg, uid)
            if msg.text == '<= Назад в меню':
                main_menu(msg, True)
            else:
                if msg.text.isdigit():
                    self.all_tokens[msg.from_user.id][uid]['max_bid'] = msg.text
                    message = self.bot.send_message(msg.chat.id, 'Прекрасно, теперь отправьте минимальный шаг с '
                                                                 'которым вы будете перебивать чужие биды',
                                                    reply_markup=self.go_back)
                    self.bot.register_next_step_handler(message, lambda msg: get_step(msg, uid))

                else:
                    message = self.bot.send_message(msg.chat.id, 'Вы ввели максимальную цену в неправильном формате\n'
                                                                 'Отправьте цену в формате числа без точек 777')
                    self.bot.register_next_step_handler(message, lambda msg: get_step(msg, uid))

        def get_link(msg):
            self.log_obj(msg)

            if msg.text == '<= Назад в меню':
                main_menu(msg, True)

            else:
                if validators.url(msg.text):
                    uid = str(uuid.uuid1())
                    try:
                        self.all_tokens[msg.from_user.id][uid]['link'] = msg.text
                    except KeyError:
                        try:
                            self.all_tokens[msg.from_user.id][uid] = {'link': msg.text}
                        except KeyError:
                            self.all_tokens[msg.from_user.id] = {uid: {'link': msg.text}}
                    message = self.bot.send_message(msg.chat.id,
                                                    'Я запомнил ссылку. Теперь введите максимальную цену которую '
                                                    'вы готовы заплатить за этот токен',
                                                    reply_markup=self.go_back)
                    self.bot.register_next_step_handler(message, lambda msg: get_max_bid(msg, uid))

                else:
                    message = self.bot.send_message(msg.chat.id, 'Вы ввели ссылку в неправильном формате, '
                                                                 'введите ссылку в формате \n'
                                                                 'https://rarible.com/token'
                                                                 '/0x60f80121c31a0d46b5279700f9df786054aa5ee5:1372954'
                                                                 '?tab=bids')
                    self.bot.register_next_step_handler(message, get_link)

        @self.bot.message_handler(commands=['start'])
        def main_commands(msg):
            self.log_obj(msg)
            if self.req.create_user(msg.from_user.id):
                self.bot.send_message(msg.chat.id, 'Аккаунт пользователя создан и был привязан к '
                                                   'вашему аккаунту в телеграм\n'
                                                   'Нажмите кнопку Аккаунт чтобы получить информацию о нем',
                                      reply_markup=self.main_menu_keyb)
            else:
                self.bot.send_message(msg.chat.id, 'Ваша аккаунт уже создан. \n'
                                                   'Чтобы получить информацию о нем нажмите кнопку Аккаунт',
                                      reply_markup=self.main_menu_keyb)

        @self.bot.message_handler(func=lambda msg: True)
        def main_menu(msg, is_back=False):
            self.log_obj(msg)
            if is_back:
                self.bot.send_message(msg.chat.id, 'Вы вернулись в меню, ориентируйтесь по кнопкам снизу',
                                      reply_markup=self.main_menu_keyb)

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
                message = self.bot.send_message(msg.chat.id,
                                                'Отправьте ссылку на токен который вы хотите купить\n'
                                                'Ссылка должна быть в формате\n'
                                                'https://rarible.com/token/'
                                                '0x60f80121c31a0d46b5279700f9df786054aa5ee5:1372954?tab=bids',
                                                reply_markup=self.go_back)
                self.bot.register_next_step_handler(message, get_link)

            elif msg.text == 'История':
                history = self.req.get_history(msg.from_user.id)
                n = '\n'
                to_send = 'История ваших действий в боте:\n' \
                          f'{n.join(history)}'
                self.bot.send_message(msg.chat.id, to_send)

            else:
                self.bot.send_message(msg.chat.id, 'Я вас не понимаю, выберете пункт из меню или напишите /start')

        self.bot.polling()

    def log_obj(self, msg, uid=None):
        if uid is not None:
            try:
                order = self.all_tokens[msg.from_user.id][uid]
                print(f'[{time.time()}]: <{msg.from_user.id}>-{msg.text}')
                print(f'^^{order}^^')
                print(f'####{self.all_tokens}###')
            except Exception as e:
                e = e
                print(f'[{time.time()}]: <{msg.from_user.id}>-{msg.text}')
                print(f'^^{e}^^')
        else:
            print(f'[{time.time()}]: <{msg.from_user.id}>-{msg.text}')

if __name__ == '__main__':
    bot = Bot()
    bot.mainloop()
