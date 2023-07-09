import logging
import gc

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
from aiogram.types import reply_keyboard

from net import *  # Import architecture
from functions import *  # Import functions

# Set API_TOKEN. You must have your own.
API_TOKEN = '6383658139:AAEDVkkm1Kfn7NMlIwoPTYYZAfsKTSa6CCs'

# Configure logging.
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher.
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Initialize the net.
style_model = Net(ngf=128)
style_model.load_state_dict(torch.load('21styles.model'), False)

# Initializing the flag to distinguish between images content and style.
flag = True
# Initializing flags to check for images.
content_flag = False
style_flag = False


def transform(content_root, style_root, im_size):
    """Function for image transformation."""
    content_image = tensor_load_rgbimage(content_root, size=im_size,
                                         keep_asp=True).unsqueeze(0)
    style = tensor_load_rgbimage(style_root, size=im_size).unsqueeze(0)
    style = preprocess_batch(style)
    style_v = Variable(style)
    content_image = Variable(preprocess_batch(content_image))
    style_model.setTarget(style_v)
    output = style_model(content_image)
    tensor_save_bgrimage(output.data[0], 'result.jpg', False)

    # Clear the RAM.
    del content_image
    del style
    del style_v
    del output
    torch.cuda.empty_cache()
    gc.collect()

from aiogram import types

async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("help", "Помощь"),
        types.BotCommand("continue", "Сгенерировать картинку"),
        types.BotCommand("photo", "Преобразовать фото"),
        types.BotCommand("cancel", "Отмена"),
        types.BotCommand("author", "Автор"),


    ])

@dp.message_handler(commands=['start'])
async def send_welcome(message):
    

    await bot.send_message(message.chat.id,
        f"Привет, {message.from_user.first_name}!\n Я StyleTransfer бот. " +
        "Я умею переносить стиль с картинки на картинку. " +
        "Нажми /help чтобы посмотреть инструкцию")

 


@dp.message_handler(commands=['help'])
async def help_message(message: types.Message):
    """
    Outputs a small instruction when the corresponding command is received.
    """
    await message.answer(text="Привет, "
                              "Я могу вам помочь перенести стиль с одной фотографии на другую."
                               " Чтобы преобразовать фотографию, воспользуйтесь командой /photo ."
                              " и отправьте картинку, на которую следует перенести стиль, "
                              "а затем пришлите фотографию с которой следует взять стиль"
                              " Чтобы сгенерировать картинку воспользуйтесь командой /continue ."
                              "Для остановки  можете использовать команду /cancel ."
                              "решимость. После этого я пришлю Вам картинку с перенесенным стилем"
                              "Это займет немного времени")


@dp.message_handler(content_types=['photo'])
async def photo_processing(message):
    """
    Triggered when the user sends an image and saves it for further processing.
    """

    global flag
    global content_flag
    global style_flag

    # The bot is waiting for a picture with content from the user.
    if flag:
        await message.photo[-1].download('content.jpg')
        await message.answer(text='Я получил первую фотографию, на неё я перенесу стиль.'
                                  "Теперь пришлите мне вторую фотографию со стилем, который следует перенести"
                                  )
        flag = False
        content_flag = True  # Now the bot knows that the content image exists.

    # The bot is waiting for a picture with style from the user.
    else:
        await message.photo[-1].download('style.jpg')
        await message.answer(text= 'Я получил вторую фотографию, Теперь используйте команду /continue .'
                                  "и я перенесу стиль второй фотографии на первую")
        flag = True
        style_flag = True  # Now the bot knows that the style image exists.


@dp.message_handler(commands=['cancel'])
async def photo_processing(message: types.Message):
    """позволяет пользователю выбрать другое изображение по содержанию или стилю."""

    global flag
    global content_flag

    # Let's make sure that there is something to cancel.
    if not content_flag:
        await message.answer(text="Вы еще не загрузили изображение содержимого.")
        return

    if flag:
        flag = False
    else:
        flag = True
    await message.answer(text='Успешно!')


@dp.message_handler(commands=['author'])
async def creator(message: types.Message):
    """Displays information about the bot's Creator."""
    link = 'https://github.com/tima-g/StyleTransfer_bot'
    await message.answer(text="Бот был создан tima-g." 
                              "\n Исходный код находится: " + link)



@dp.message_handler(commands=['continue'])
async def contin(message: types.Message):
    """Preparing for image processing."""

    # Let's make sure that the user has added both images.
    if not (content_flag * style_flag):  # Conjunction
        await message.answer(text="Вы еще не загрузили оба изображения.")
        return

    # Adding answer options.
    res = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                    one_time_keyboard=True)
    res.add(types.KeyboardButton(text="Low"))
    res.add(types.KeyboardButton(text="Medium"))
    res.add(types.KeyboardButton(text="High"))

    await message.answer(text= 'Хорошо, теперь нужно выбрать  разрешение'
                            "  будущего изображения."
                            "Чем выше качество, тем медленнее время обработки"
                            "Если ты хочешь начать все сначала с этого"
                            "шаг, просто пришлите мне изображение содержимого еще раз"
                            'а затем стиль изображения', reply_markup=res)


@dp.message_handler(lambda message: message.text in ("Low", "Medium", "High"))
async def processing(message: types.Message):
    """Image processing depending on the selected quality."""

    if message.text == 'Low':
        image_size = 256
    elif message.text == 'Medium':
        image_size = 300
    else:
        image_size = 350

    await message.answer(text='Обработка началась и займет некоторое время. '
                    '- Подожди немного.',
                         reply_markup=types.ReplyKeyboardRemove())
    transform('content.jpg', 'style.jpg', image_size)
    with open('result.jpg', 'rb') as file:
        await message.answer_photo(file, caption='Готово!')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup= set_default_commands)


