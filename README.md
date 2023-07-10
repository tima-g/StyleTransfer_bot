# StyleTransfer_bot 
Этот бот был создан для телеграма, он может переносить стиль с одних фотографий на другие.
Пока у бота есть один режим работы:
- Перенос стиля с одного изображения на другое (NST)
  
В дальнейшем я планирую создать ещё несколько режимов работы
### Перенос стиля с одного изображения на другое
В данном режиме бот переносит стиль с первого изображения на второе с заданными настройками. 
Данный режим использует технологию Neural style transfer. Для этого режима возможна  дополнительная настройка размер выходного изображения:
  - Low: 128х128 пикселей
  - Medium: 256х256 пикселей
  - High: 512х512 пикселей

### Информация по запуску бота
Для запуска данного бота у себя необходимо изменить файл `main.py`, а именно добавить свой токен:
```Python
  TG_BOT_TOKEN = '<YOUR TOKEN>'
```
Где:
- `<YOUR TOKEN>` -- токен вашего бота, который можно получить у официального бота сервиса Telegram для создания собственных ботов: @BotFather

### Возможные результаты работы данного режима бота:

Изначальное изображение    |  Переносимый стиль        |  Итоговое изображение
:-------------------------:|:-------------------------:|:-------------------------:
<img src="https://github.com/tima-g/StyleTransfer_bot/blob/main/images/content.jpg" height="250" width="250">  |  <img src="https://github.com/tima-g/StyleTransfer_bot/blob/main/images/style.jpg" height="250" width="181">  |   <img src="https://github.com/tima-g/StyleTransfer_bot/blob/main/images/result.jpg" height="250"  width="250">
