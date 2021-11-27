# fo4-marathon
**fo4-marathon** - программа под *Windows* для автоматического ежедневного получения бесплатного значка марафона на множестве аккаунтов.  
Написана на коленке, но если соберется какой-то фидбек и это будет кому-то нужно, возможно я замотивируюсь и обновлю логику работы, сделаю удобный интерфейс, etc..  
Отблагодарить меня можно по ссылкам ниже:  
- https://steamcommunity.com/tradeoffer/new/?partner=235145465&token=M8bisq0z

## Описание
После запуска программы у вас откроется окно браузера и консоль с выводом статусных сообщений ее работы.  
В файле ***result.log*** можно посмотреть результат работы программы, если значок успешно получен - будет выведен общий баланс значков на аккаунте в формате: **login - n значков**.  
При ошибке получения вместо баланса вы увидите соответсующее сообщение.  

## Требования:
- Программа работает на базе браузера Google Chrome, поэтому для ее работы нужен вебдрайвер этого браузера - [скачать](https://chromedriver.chromium.org/)  
Версия вебдрайвера обязательно должна совпадать с текущей версией браузера. [Подробнее об установке chromedriver](https://chromedriver.chromium.org/getting-started)

## Установка:
Скачиваем актуальный релиз [отсюда](https://github.com/vvvvvvvvlone/fo4-marathon/releases) и переходим к настройке.

## Настройка:
1. В переменную среды **Path** добавляем путь до папки со скачанным вебдрайвером. Возможно, позже сделаю какой-то конфиг и это действие станет неактуальным.  
Пример: **G:\coding\web\selenium-server\**  
Загуглив, можно узнать подробнее и с примерами как это правильно сделать.  
2. Заполняем конфигурационный файл data.txt данным от ваших аккаунтов 101xp в формате login:password.  
Каждый последующий аккаунт заполняется с новой строки.  
Пример заполнения:  
*qwerty@mail.ru:qwerty  
qwerty123@mail.ru:qwerty123  
qwerty321@mail.ru:qwerty321*
