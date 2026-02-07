# Akinator 2.0 — Telegram UX

## Commands

| Command | Description (RU) | Description (EN) |
|---------|-------------------|-------------------|
| `/start` | Приветствие + инструкция | Welcome + instructions |
| `/new` | Начать новую игру | Start a new game |
| `/top` | Показать топ-5 кандидатов | Show top 5 candidates |
| `/why` | Объяснить текущий ход мыслей | Explain current reasoning |
| `/giveup` | Сдаться (бот не угадал) | Give up (bot failed to guess) |
| `/lang` | Переключить язык (RU/EN) | Switch language (RU/EN) |
| `/help` | Справка по командам | Command help |
| `/stats` | Статистика побед/поражений | Win/loss statistics |

## Game Flow (User Perspective)

### 1. Start
```
User: /new
Bot:  Think of a character — real or fictional.
      Ready? You can optionally give me a hint
      (describe in 1 phrase without naming):

      [Skip hint] [Give hint]
```

### 2. Hint (optional)
```
User: "A character from a space movie"
Bot:  Got it! Let me think...
      Question 1/20:
      Is this character fictional?

      [Yes] [No] [Probably yes] [Probably no] [Don't know]
```

### 3. Questions
```
Bot:  Question 3/20:
      Is this character related to the Star Wars universe?

      [Yes] [No] [Probably yes] [Probably no] [Don't know]

User: [Yes]

Bot:  Question 4/20:
      Is this character a villain?

      [Yes] [No] [Probably yes] [Probably no] [Don't know]
```

### 4. Guess
```
Bot:  I think I know! (87% confident)

      Is it **Darth Vader**?
      (Star Wars character, Sith Lord)

      [Yes, correct!] [No, wrong]
```

### 5a. Correct guess
```
User: [Yes, correct!]
Bot:  I guessed it in 4 questions!
      Want to play again?

      [New game]
```

### 5b. Wrong guess
```
User: [No, wrong]
Bot:  Hmm, let me think again...

      Is it **Luke Skywalker**?
      (Star Wars character, Jedi)

      [Yes, correct!] [No, wrong]
```

### 5c. Failed to guess
```
User: [No, wrong]
Bot:  I give up! Who were you thinking of?

User: Йода
Bot:  Yoda! Can you give a short description?

User: Маленький зелёный мастер-джедай
Bot:  Thanks! A few quick questions to remember:
      - Is Yoda fictional? [Yes] [No]
      - Is Yoda male? [Yes] [No]
      - Related to movies? [Yes] [No]

      Got it! I'll remember Yoda for next time.
      Want to play again?

      [New game]
```

## Inline Keyboard Layouts

### Answer buttons (5 columns)
```
[Да] [Нет] [Скорее да] [Скорее нет] [Не знаю]
```

### Guess confirmation (2 columns)
```
[Да, верно!] [Нет, не угадал]
```

### Post-game (1 column)
```
[Новая игра]
```

### Hint choice (2 columns)
```
[Пропустить подсказку] [Дать подсказку]
```

## Message Formatting

- Bot messages use **Markdown** formatting
- Character names are **bold**
- Confidence shown as percentage
- Question number shown as `N/20` counter
- `/top` output:
  ```
  Top 5 candidates:
  1. **Darth Vader** — 34.2%
  2. **Emperor Palpatine** — 22.1%
  3. **Kylo Ren** — 15.4%
  4. **Darth Maul** — 8.7%
  5. **Count Dooku** — 5.3%
  ```
- `/why` output:
  ```
  My reasoning:
  - You said the character IS fictional → favoring fictional characters
  - You said the character IS related to Star Wars → strong filter
  - You said the character IS a villain → narrowed to villains
  - Top candidate: Darth Vader (34.2%)
  ```

## Error Handling (User-facing)

| Situation | Bot response |
|-----------|-------------|
| No active game | "No game in progress. Use /new to start!" |
| Command during learning | "Please finish teaching me first." |
| API error | "Something went wrong. Try again or /new for a fresh game." |
| Rate limit | "Too many requests. Please wait a moment." |

## Language Support

- Bot detects language from `/lang` command or defaults to Russian
- All UI text stored in localization dict
- Questions have both `question_ru` and `question_en` in DB
- LLM generates explanations in the selected language
