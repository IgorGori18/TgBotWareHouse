from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton



main_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отчеты')],
                                              [KeyboardButton(text='Ввод поступления/отгрузки')]],
                                    resize_keyboard=True, input_field_placeholder='Выберите пункт меню...')

second_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Остатки'),
                                              KeyboardButton(text='Отгрузки')],
                                              [KeyboardButton(text='Поступления'),
                                              KeyboardButton(text='Отчеты сотрудников')],
                                              [KeyboardButton(text='Вернуться в главное меню')]],
                                    resize_keyboard=True, input_field_placeholder='Выберите пункт меню...')



remains_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Общий остаток'),
                                                  KeyboardButton(text='Остаток определенного товара')],
                                                 [KeyboardButton(text='Остаток контроллеров '),
                                                  KeyboardButton(text='Назад')]],
                                       resize_keyboard=True,)


delivery_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Поступления за 7 дней')],
                                              [KeyboardButton(text='Поступления за месяц')],
                                              [KeyboardButton(text='Назад')]],
                                    resize_keyboard=True)

shipment_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отгрузки за 7 дней')],
                                              [KeyboardButton(text='Отгрузки за месяц')],
                                              [KeyboardButton(text='Назад')]],
                                    resize_keyboard=True)


surname_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Воронин", callback_data="Воронин")],
        [InlineKeyboardButton(text="Коцюба", callback_data="Коцюба")],
        [InlineKeyboardButton(text="Козлов", callback_data="Козлов")]
    ])