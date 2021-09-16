## Скрипт для подсчета статистики для логов

- Скрипт работает с любым количеством логов, которые находятся в указанной директории
- Считает количество запросов для каждого IP-адреса, разбивая по методам
- Для каждого IP-адреса формируется словарь с методами и общим количеством запросов TOTAL
- Результат работы скрипты выводится в консоль и в папку /statistics 
- Файл с результатом получает название `stat_for_file_{filename}.json`
- В данный файл записывается JSON с результатами сбора статистики

### Особенности запуска скрипта

Данный скрипт запускается командой:

`python script.py -d /dir`, 

где ключ `-d` означает директорию с лог-файлами. Название директории должно задаваться относительно текущего пути.