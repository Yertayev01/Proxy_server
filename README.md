# Оптимизированный прокси-сервис для Polygon.io API

## Обзор проекта

Этот проект включает разработку оптимизированного прокси-сервиса на основе FastAPI и Redis для взаимодействия с API Polygon.io. Цель проекта — минимизировать нагрузку на API и эффективно предоставлять данные клиентам, в частности исторические данные по акциям. Сервис выступает в качестве промежуточного звена между клиентом и Polygon.io, обрабатывая запросы, получая данные и возвращая их в оптимизированном виде.

## Обзор Polygon.io

[Polygon.io](https://polygon.io) — это платформа, предоставляющая API для финансовых данных, которая предлагает доступ к широкому спектру информации, включая котировки акций, валюты, криптовалюты, опционы, фьючерсы, исторические данные и агрегированные рыночные данные.

## Описание задачи

### Цель

Основная цель этого проекта — создать прокси-сервис, который:

1. Принимает запросы от фронтенда.
2. Перенаправляет эти запросы в Polygon.io для получения исторических данных по акциям.
3. Обрабатывает данные и возвращает результаты на фронтенд эффективно.

### Требования

#### 1. Выбор хранилища данных

- **Цель**: Выбрать оптимальное решение для хранения данных, поддерживающее временные ряды и масштабируемость.
- **Решение**: Для хранения и кэширования данных был выбран Redis.
- **Обоснование**: Redis обеспечивает высокую производительность и масштабируемость, идеально подходит для кэширования часто запрашиваемых данных и уменьшения нагрузки на внешний API.

#### 2. Оптимизация запросов

- **Цель**: Разработать стратегии для минимизации количества запросов к API Polygon.io.
- **Реализация**:
  - **Агрегация данных**: Группировка запросов данных для уменьшения количества вызовов к Polygon.io.
  - **Кэширование с использованием Redis**: Внедрение Redis для хранения часто запрашиваемых данных, что позволяет сократить количество избыточных вызовов API.
  - **Эффективная обработка запросов**: Оптимизация логики обработки запросов для снижения нагрузки на API Polygon.io.

#### 3. Обеспечение актуальности данных

- **Цель**: Обеспечить актуальность данных, предоставляемых клиентам.
- **Реализация**: Внедрение механизма автоматического обновления данных в Redis, чтобы кэшированные данные оставались актуальными.

### Пример запроса к API

Для получения исторических данных по акциям, типичный запрос к API Polygon.io может выглядеть следующим образом:

```plaintext
https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}?apiKey=RnGEjPoMpDNZC2igxQRttmZsOYCHkQNI


### Установка и запуск с Docker

1. Клонируйте репозиторий:

git clone https://github.com/Yertayev01/Proxy_server.git
cd proxy_server

2. Запустите контейнеры с помощью Docker Compose:

docker-compose up --build


### Документация API

Swagger UI: http://127.0.0.1:8000/docs

### Запуск тестов

docker-compose run app pytest

### Отчет о проценте покрываемости тестов

Name           Stmts   Miss  Cover
----------------------------------
main.py           32      6    81%
test_main.py       8      0   100%
----------------------------------
TOTAL             40      6    85%

### Отчет о реализации оптимизации и нагрузке передачи данных

1. Кэширование данных с использованием Redis

Реализация:

Инициализация Redis: Клиент Redis инициализируется с использованием параметров, заданных в переменных окружения (хост, порт и пароль).
Кэширование запросов: При получении запроса к API, сервис сначала проверяет, есть ли данные в Redis-кэше. Если данные уже кэшированы (по ключу, составленному из параметров запроса), они возвращаются клиенту сразу.
Обновление кэша: Если данные отсутствуют в кэше, сервис делает запрос к Polygon.io, получает данные и сохраняет их в Redis с установленным временем истечения (3600 секунд или 1 час).

Результат:

Снижение количества запросов: Меньшее количество обращений к Polygon.io, так как данные часто запрашиваются из Redis.
Ускорение времени ответа: Быстрый доступ к данным из Redis уменьшает время ожидания для конечного клиента.

2. Агрегация запросов и фоновое обновление кэша

Реализация:

Фоновое обновление кэша: Когда данные запрашиваются, но не найдены в кэше, запрос к Polygon.io выполняется. Одновременно с этим в фоне запускается задача по обновлению кэша, чтобы данные обновились для будущих запросов.
Использование фоновых задач: Фоновая задача, которая обновляет кэш, не блокирует основной поток обработки запроса, что позволяет клиенту получить ответ быстрее.

Результат:

Уменьшение задержек: Клиенты получают ответ быстрее, так как запросы обслуживаются из кэша, и обновление данных происходит асинхронно.
Периодическое обновление данных: Система поддерживает актуальность данных в кэше, что помогает избежать устаревших данных.

3. Обработка ошибок и управление состоянием

Реализация:

Обработка ошибок: В случае, если запрос к Polygon.io не удался (например, статус код не 200), выбрасывается исключение HTTPException, что позволяет клиенту узнать о проблеме.

Результат:

Управление ошибками: Клиенты получают информацию об ошибках, что помогает им понимать, что пошло не так при запросе данных.