import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import json

import requests
import re


API_TOKEN = '7878235867:AAEM2ybsAy11nWQYtlgb4TVYTcKXr8K9cTY'
mainPrompt = '''Ты — эксперт по анализу промтов. Твоя задача — сравнить пользовательский промт с идеальным промтом и предоставить краткий, структурированный отчёт, который включает:
1. **Сравнительный анализ:**  
   - Определи, насколько пользовательский промт ясен, полон и логически структурирован по сравнению с идеальным промтом.  
   - Выяви ключевые различия: что отсутствует, что избыточно, а также ошибки или неясности в формулировке.
2. **Рекомендации по улучшению:**  
   - **Что добавить:** укажи, какие детали или пояснения стоит добавить, чтобы сделать промт более точным и информативным.  
   - **Что убрать:** определи лишние или запутывающие элементы, которые можно удалить для повышения ясности.  
   - **Что изучить:** предложи темы, материалы или источники, которые помогут пользователю расширить понимание предмета и улучшить формулировку промта.
3. **Вывод:**  
   - Составь краткое резюме с основными выводами по оценке, включая общее качество промта и ключевые рекомендации.
Используй следующий формат вывода:
**Резюме оценки:**  
[Краткое резюме основных моментов и общего качества промта]
**Рекомендации по улучшению:**  
- Добавить: [указать конкретные элементы, которых не хватает].  
- Убрать: [указать элементы, которые вызывают путаницу или избыточны].  
- Изучить: [предложить тему или ресурсы для повышения знаний].
**Вопросы для доработки (если необходимо):**  
- [Вопрос 1 для уточнения деталей промта].  
- [Вопрос 2 для дальнейшего улучшения формулировки].
**Пример входных данных для анализа:**  
Пользовательский промт: [Вставьте текст пользовательского промта]  
Идеальный промт: [Вставьте текст идеального промта]
На основе предоставленных данных сформируй оценку и рекомендации.'''


user_task_state = {}
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
tasks = {
    1: {
        'task': 'Составьте промт, который попросит ИИ провести глубокий анализ длинного текста: выделить ключевые идеи, определить скрытые подтексты и выявить аспекты, которые могут быть упущены при поверхностном прочтении.',
        'ideal_promt': 'Проанализируй следующий текст и составь структурированный аналитический отчет. Определи ключевые идеи, выяви скрытые подтексты, возможные предвзятости и аспекты, которые могли остаться незамеченными при поверхностном анализе. Предложи возможные альтернативные интерпретации.',
        'data_for_solve': 'В эпоху цифровой трансформации компании вынуждены переосмысливать свои бизнес-процессы...'
    },
    2: {
        'task': 'Составьте промт для генерации Python-кода, реализующего алгоритм сортировки списка чисел без использования встроенных функций сортировки.',
        'ideal_promt': 'Напиши функцию на Python, которая реализует алгоритм сортировки списка чисел без использования встроенных функций sort() и sorted(). Используй, например, быструю сортировку или сортировку слиянием. Пример входных данных: [5, 2, 9, 1, 5, 6].',
        'data_for_solve': '[5, 2, 9, 1, 5, 6]'
    },
    3: {
        'task': 'Создайте промт для извлечения дат, имён и организаций из сложного текста с использованием регулярных выражений.',
        'ideal_promt': 'Проанализируй следующий текст и извлеки все упоминания дат, имён и организаций, используя регулярные выражения. Верни результат в формате JSON с ключами "dates", "names" и "organizations". Обоснуй выбор регулярных выражений. Текст: "На конференции в MIT 15 марта 2023 года выступали Илья Петров из OpenAI и Анна Смирнова из Google.".',
        'data_for_solve': 'На конференции в MIT 15 марта 2023 года выступали Илья Петров из OpenAI и Анна Смирнова из Google.'
    },
    4: {
        'task': 'Составьте промт, который попросит ИИ определить эмоциональную окраску текста и выявить манипулятивные элементы.',
        'ideal_promt': 'Проанализируй следующий текст, определи его эмоциональную окраску (позитивное, негативное или нейтральное настроение) и выяви возможные манипулятивные элементы, такие как эмоциональные триггеры, предвзятость или скрытые призывы к действию. Обоснуй свой вывод, приводя примеры из текста.',
        'data_for_solve': 'Сегодня был отличный день, но внезапно всё пошло наперекосяк, и теперь я не знаю, как исправить ситуацию.'
    },
    5: {
        'task': 'Составьте промт для генерации Python-кода, который преобразует текст в HTML с учетом адаптивности и SEO-оптимизации.',
        'ideal_promt': 'Напиши Python-скрипт, который принимает текст и преобразует его в HTML, оборачивая каждый абзац в <p> и применяя адаптивную верстку. Добавь семантические теги для SEO-оптимизации (например, <h1>, <meta>, <article>). Объясни важность каждого элемента.',
        'data_for_solve': 'Это пример текста, который будет преобразован в HTML.'
    },
    6: {
        'task': 'Составьте промт для генерации Python-кода, который анализирует данные и предсказывает их тренд.',
        'ideal_promt': 'Напиши Python-код, который анализирует временной ряд данных и предсказывает его тренд, используя библиотеку pandas и метод линейной регрессии из scikit-learn. Объясни выбор модели и предобработку данных.',
        'data_for_solve': '[Временной ряд значений: "Дата, Значение\n2024-01-01, 100\n2024-02-01, 120\n2024-03-01, 140"]'
    },
    7: {
        'task': 'Составьте промт для генерации научного отчёта по биоинформатике, включающего анализ ДНК-цепочек.',
        'ideal_promt': 'Создай научный отчёт по биоинформатике, в котором будет проведён анализ ДНК-цепочки. Определи повторяющиеся последовательности, мутации и возможные генетические аномалии. Используй Python и библиотеку BioPython.',
        'data_for_solve': '[Последовательность ДНК: "AGCTTAGCTAATCG"]'
    8: {
        'task': 'Создайте промт для автоматической генерации отчётов о продажах по заданным данным.',
        'ideal_promt': 'Напиши Python-скрипт, который принимает данные о продажах в формате CSV и генерирует структурированный отчёт с основными метриками, такими как общая выручка, средний чек и количество транзакций. Используй библиотеку pandas для анализа данных и matplotlib для визуализации результатов.',
        'data_for_solve': 'Дата, Продажи\n2024-01-01, 5000\n2024-02-01, 7000\n2024-03-01, 6000'
    },
    9: {
        'task': 'Создайте промт для анализа текстов и извлечения ключевых слов с использованием TF-IDF.',
        'ideal_promt': 'Напиши Python-скрипт, который принимает текст и извлекает ключевые слова, используя метод TF-IDF. Объясни выбор параметров и представь результаты в виде словаря с ключевыми словами и их значениями.',
        'data_for_solve': 'Текст для анализа: "Искусственный интеллект меняет мир. Мы наблюдаем за его ростом и развитием."'
    },
    10: {
        'task': 'Создайте промт для предсказания цен на акции на основе исторических данных.',
        'ideal_promt': 'Напиши Python-скрипт, который анализирует исторические данные о ценах акций и предсказывает их будущее значение с использованием модели линейной регрессии. Объясни выбор модели и предобработку данных.',
        'data_for_solve': 'Дата, Цена\n2024-01-01, 150\n2024-02-01, 155\n2024-03-01, 160'
    11: {
        'task': 'Создай промт для анализа текстов и извлечения ключевых слов с использованием методов NLP.',
        'ideal_promt': 'Напиши Python-скрипт, который принимает текст и извлекает ключевые слова с использованием библиотеки NLTK. Объясни выбор методов и представь результаты в виде списка ключевых слов.',
        'data_for_solve': 'Текст для анализа: "Искусственный интеллект меняет наш мир и открывает новые возможности."'
    },
    12: {
        'task': 'Создай промт для визуализации данных о продажах.',
        'ideal_promt': 'Напиши Python-скрипт, который принимает данные о продажах в формате CSV и создает график с использованием библиотеки matplotlib. Объясни выбор типа графика и его параметры.',
        'data_for_solve': 'Дата, Продажи\n2024-01-01, 5000\n2024-02-01, 7000\n2024-03-01, 6000'
    },
    13: {
        'task': 'Создай промт для предсказания погоды на основе исторических данных.',
        'ideal_promt': 'Напиши Python-скрипт, который анализирует исторические данные о погоде и предсказывает будущее состояние с использованием модели машинного обучения. Объясни выбор модели и предобработку данных.',
        'data_for_solve': 'Дата, Температура\n2024-01-01, -5\n2024-01-02, -3\n2024-01-03, 0'
    },
    14: {
        'task': 'Создай промт для генерации SQL-запросов на основе требований.',
        'ideal_promt': 'Напиши Python-скрипт, который принимает описание задачи и генерирует соответствующий SQL-запрос. Объясни структуру запроса и его элементы.',
        'data_for_solve': 'Требование: "Вывести имена и возраста всех пользователей старше 18 лет."'
    },
    15: {
        'task': 'Создай промт для анализа финансовых данных компании.',
        'ideal_promt': 'Напиши Python-скрипт, который анализирует финансовые данные компании и генерирует отчёт о прибылях и убытках. Используй библиотеку pandas для анализа данных.',
        'data_for_solve': 'Дата, Прибыль\n2024-01-01, 10000\n2024-02-01, 15000\n2024-03-01, 12000'
    },
    16: {
        'task': 'Создай промт для генерации тестов для веб-приложения.',
        'ideal_promt': 'Напиши Python-скрипт, который генерирует тесты для веб-приложения с использованием фреймворка pytest. Опиши логику тестов и их структуру.',
        'data_for_solve': 'Функция: def add(a, b): return a + b'
    },
    17: {
        'task': 'Создай промт для анализа социальных медиа.',
        'ideal_promt': 'Напиши Python-скрипт, который анализирует данные из социальных медиа и определяет основные тренды. Используй библиотеку pandas для обработки данных.',
        'data_for_solve': 'Дата, Посты\n2024-01-01, 150\n2024-01-02, 200\n2024-01-03, 180'
    },
    18: {
        'task': 'Создай промт для прогнозирования спроса на продукцию.',
        'ideal_promt': 'Напиши Python-скрипт, который анализирует данные о продажах и предсказывает будущий спрос с использованием регрессионной модели.',
        'data_for_solve': 'Дата, Продажи\n2024-01-01, 300\n2024-01-02, 350\n2024-01-03, 400'
    },
    19: {
        'task': 'Создай промт для генерации рекомендаций на основе пользовательских данных.',
        'ideal_promt': 'Напиши Python-скрипт, который анализирует пользовательские предпочтения и генерирует персонализированные рекомендации.',
        'data_for_solve': 'Пользователь: "Иван", Предпочтения: "Фильмы, Спорт"'
    },
    20: {
        'task': 'Создай промт для создания чат-бота.',
        'ideal_promt': 'Напиши Python-скрипт, который создает простого чат-бота, способного отвечать на основные вопросы пользователей.',
        'data_for_solve': 'Вопрос: "Какой сегодня день?"'
    },
    21: {
        'task': 'Создай промт для анализа текстов на предмет эмоциональной окраски.',
        'ideal_promt': 'Напиши Python-скрипт, который анализирует текст и определяет его эмоциональную окраску с использованием методов NLP.',
        'data_for_solve': 'Текст: "Сегодня был прекрасный день, хотя и немного холодный."'
    },
    22: {
        'task': 'Создай промт для автоматизации процессов в Excel.',
        'ideal_promt': 'Напиши Python-скрипт, который взаимодействует с Excel-файлом, выполняя автоматизацию рутинных задач.',
        'data_for_solve': 'Файл: "данные.xlsx", Задача: "Суммировать значения в колонке A."'
    },
    23: {
        'task': 'Создай промт для анализа данных о здоровье.',
        'ideal_promt': 'Напиши Python-скрипт, который анализирует данные о здоровье и генерирует отчёт о состоянии здоровья.',
        'data_for_solve': 'Дата, Давление, Пульс\n2024-01-01, 120/80, 75\n2024-01-02, 130/85, 80'
    },
    24: {
        'task': 'Создай промт для анализа данных о климате.',
        'ideal_promt': 'Напиши Python-скрипт, который анализирует климатические данные и генерирует отчёт о тенденциях изменения климата.',
        'data_for_solve': 'Дата, Температура\n2024-01-01, 15\n2024-01-02, 16\n2024-01-03, 14'
    },
    25: {
        'task': 'Создай промт для построения нейронной сети.',
        'ideal_promt': 'Напиши Python-скрипт, который строит и обучает простую нейронную сеть с использованием библиотеки TensorFlow.',
        'data_for_solve': 'Данные для обучения: "X_train, y_train"'
    },
    26: {
        'task': 'Создай промт для создания мобильного приложения.',
        'ideal_promt': 'Напиши Python-скрипт, который создает простое мобильное приложение с использованием фреймворка Kivy.',
        'data_for_solve': 'Задача: "Сделать калькулятор."'
    },
    27: {
        'task': 'Создай промт для генерации QR-кодов.',
        'ideal_promt': 'Напиши Python-скрипт, который генерирует QR-коды на основе предоставленных данных.',
        'data_for_solve': 'Данные: "https://example.com"'
    },
    28: {
        'task': 'Создай промт для обработки изображений.',
        'ideal_promt': 'Напиши Python-скрипт, который обрабатывает изображения с использованием библиотеки PIL.',
        'data_for_solve': 'Файл: "image.jpg", Задача: "Изменить размер на 100x100."'
    },
    29: {
        'task': 'Создай промт для создания веб-скрапера.',
        'ideal_promt': 'Напиши Python-скрипт, который извлекает данные с веб-страницы с использованием библиотеки BeautifulSoup.',
        'data_for_solve': 'URL: "https://example.com"'
    },
    30: {
        'task': 'Создай промт для выполнения статистического анализа.',
        'ideal_promt': 'Напиши Python-скрипт, который выполняет статистический анализ данных с использованием библиотеки scipy.',
        'data_for_solve': 'Данные: [1, 2, 3, 4, 5]'
    }
}



'''Ты — эксперт по анализу промтов. Твоя задача — сравнить пользовательский промт с идеальным промтом и предоставить краткий, структурированный отчёт, который включает:
1. **Сравнительный анализ:**  
   - Определи, насколько пользовательский промт ясен, полон и логически структурирован по сравнению с идеальным промтом.  
   - Выяви ключевые различия: что отсутствует, что избыточно, а также ошибки или неясности в формулировке.
2. **Рекомендации по улучшению:**  
   - **Что добавить:** укажи, какие детали или пояснения стоит добавить, чтобы сделать промт более точным и информативным.  
   - **Что убрать:** определи лишние или запутывающие элементы, которые можно удалить для повышения ясности.  
   - **Что изучить:** предложи темы, материалы или источники, которые помогут пользователю расширить понимание предмета и улучшить формулировку промта.
3. **Вывод:**  
   - Составь краткое резюме с основными выводами по оценке, включая общее качество промта и ключевые рекомендации.
Используй следующий формат вывода:
**Резюме оценки:**  
[Краткое резюме основных моментов и общего качества промта]
**Рекомендации по улучшению:**  
- Добавить: [указать конкретные элементы, которых не хватает].  
- Убрать: [указать элементы, которые вызывают путаницу или избыточны].  
- Изучить: [предложить тему или ресурсы для повышения знаний].
**Вопросы для доработки (если необходимо):**  
- [Вопрос 1 для уточнения деталей промта].  
- [Вопрос 2 для дальнейшего улучшения формулировки].
**Пример входных данных для анализа:**  
Пользовательский промт: [Вставьте текст пользовательского промта]  
Идеальный промт: [Вставьте текст идеального промта]
На основе предоставленных данных сформируй оценку и рекомендации.'''



#JSON формат
{
  "instruction": "Ты — эксперт по анализу промтов. Сравни пользовательский промт с идеальным промтом и дай рекомендации по улучшению.",
  "steps": [
    "Анализируй ясность, полноту и структуру обоих промтов.",
    "Определи, какие ключевые элементы отсутствуют или избыточны в пользовательском промте.",
    "Предложи рекомендации: что добавить, что убрать и что изучить для улучшения формулировки.",
    "Сформируй краткое резюме оценки и список рекомендаций."
  ],
  "output_format": {
    "evaluation_summary": "Краткое резюме оценки общего качества пользовательского промта.",
    "recommendations": [
      "Добавить: [конкретные рекомендации]",
      "Убрать: [конкретные рекомендации]",
      "Изучить: [предложение по дополнительным материалам]"
    ],
    "improvement_questions": [
      "Вопрос для уточнения 1",
      "Вопрос для уточнения 2"
    ]
  },
  "input": {
    "user_prompt": "[Вставьте текст пользовательского промта]",
    "ideal_prompt": "[Вставьте текст идеального промта]"
  }
}


class UserState(StatesGroup):
    waiting_for_prompt = State()



@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я помогу тебе улучшить навыки промпт-инжениринга.\nНачнем с первого задания:")
    user_id = message.from_user.id
    user_task_state[user_id] = 1
    await send_task(message.chat.id)



async def send_task(chat_id):
    task = list(tasks.items())[0]
    await bot.send_message(chat_id, f"Задание:\n{task[0]}")
    await UserState.waiting_for_prompt.set()


@dp.message_handler(state=UserState.waiting_for_prompt)
async def process_prompt(message: types.Message, state: FSMContext):
    user_prompt = message.text
    analysis = await analyze_prompt(user_prompt)
    await message.reply(f"Анализ вашего промпта:\n{analysis}")

    task = list(tasks.items())[0]
    await message.reply(f"Идеальный промпт:\n{task[1]}")

    await state.finish()



async def analyze_prompt(prompt):
    url = "https://api.blackbox.ai/api/chat"

    payload = json.dumps({
        "messages": [
            {
                "content": "Реши задачу: 2 + 2 = ",
                "role": "user"
            }
        ],
        "model": "deepseek-ai/DeepSeek-V3",
        "max_tokens": 1024
    })

    headers = {
        'Content-Type': 'application/json',

    }

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        s = response.text
        s = s.replace(']', '').replace('[', '').replace('\\', '').replace('boxed{', '').replace('}', '').replace('*',                                                                                                    '')
        return s

    except requests.exceptions.JSONDecodeError:
        pass
    except Exception as e:
        pass


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)