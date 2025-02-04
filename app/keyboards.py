from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Остатки')],
                                              [KeyboardButton(text='Отгрузки')],
                                              [KeyboardButton(text='Поступления')]],
                                    resize_keyboard=True, input_field_placeholder='Выберите пункт меню...')



remains_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Общий остаток'),
                                                  KeyboardButton(text='Остаток определенного товара')],
                                                 [KeyboardButton(text='Остаток контроллеров '),
                                                  KeyboardButton(text='Вернуться в главное меню')]],
                                       resize_keyboard=True,)


transaction_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='За 7 дней')],
                                              [KeyboardButton(text='За месяц')],
                                              [KeyboardButton(text='Вернуться в главное меню')]],
                                    resize_keyboard=True)