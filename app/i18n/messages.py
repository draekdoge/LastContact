"""Тексты бота (HTML). Ключи: ru, en, uk, de, es, pt, ko, ja, zh."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Msg:
    btn_spread: str
    btn_status: str
    btn_admin: str
    """Reply-кнопка «Админка» — только для BOT_ADMIN_TELEGRAM_IDS."""

    welcome_title: str
    welcome_subtitle_organic: str
    welcome_subtitle_referral: str
    welcome_timer: str
    welcome_link_hint: str
    welcome_no_bot_username: str

    already_in_game_reinfect: str
    welcome_back_title: str
    stats_direct: str
    stats_network: str
    stats_country: str
    stats_banner: str
    """Заголовок блока статистики в карточке (эпично, CAPS ок)."""

    share_title: str
    invite_share_bonus_for_inviter_line: str
    """Строка про бонус отправителю для карточки у контакта; {bonus_hours:g}."""

    share_no_username: str
    spread_open_failed: str
    """Текст при сбое открытия экрана передачи (inline под карточкой)."""

    timer_inactive: str
    timer_zombie: str
    timer_expired_pending: str
    """Редкий рассинхрон данных (не кризисный дедлайн)."""

    timer_zombie_transition_pending: str
    """infected, кризисный дедлайн прошёл, перевод в зомби ещё не применён — без «воркер»."""

    zombie_screen06_banner: str
    zombie_card_header: str
    zombie_card_body: str
    """HTML; {chain_total} — носители в ветке под тобой."""
    zombie_card_hint: str
    zombie_bar_label: str
    zombie_phase_label: str
    zombie_badges_line: str
    zombie_timer_strip: str
    """Полоса некроза для зомби (кнопка «Сколько осталось»)."""

    timer_countdown: str
    timer_reserve: str
    """Должен содержать {pct} — доля оставшегося окна до кризиса (0–100)."""

    timer_zone_title: str
    """Короткий заголовок над активным таймером (до кризиса)."""

    timer_extend_sources: str
    """HTML; {bonus_hours:g} — бонус за нового игрока по ссылке. Фаза 0: прозрачность источников времени."""

    own_invite_card_title: str
    btn_refresh_remain: str
    btn_pick_contacts: str
    hint_after_contacts_shared: str
    invite_bottom_keyboard_prompt: str
    """После inline «Мои контакты»: объяснить клавиатуру снизу (Telegram не даёт оба типа кнопок в одном сообщении)."""

    spread_contact_send_failed: str
    """Не удалось доставить карточку выбранному контакту."""

    spread_contact_sent_ok: str
    """Карточка отправлена контакту в чат с ботом."""

    spread_join_chain_button: str
    """Единственная URL-кнопка на карточке приглашения."""

    share_native_prefill: str
    """Короткий «хук» для t.me/share/url — текст, который увидит друг до ссылки (без спойлеров механик)."""

    mock_header_new: str
    mock_header_return: str
    mock_header_status: str
    mock_header_invite: str
    mock_body_new_organic: str  # плейсхолдер {timer_hours_phrase} (экранирован в коде)
    mock_body_new_referral: str
    mock_body_return: str
    """HTML; плейсхолдер {network} — носители в цепочке (как в SCREEN 02)."""
    mock_badges_new: str
    mock_badges_active: str
    invite_link_box_label: str
    mock_vita_label: str
    mock_decay_label: str
    mock_stat_ab_direct: str
    mock_stat_ab_net: str
    mock_stat_ab_sector: str

    mock_header_immune: str
    mock_body_immune: str
    mock_immune_vita_label: str
    mock_immune_decay_label: str
    timer_immune_line: str
    """Одна строка; плейсхолдер {time_str} — HH:MM:SS."""

    status_title: str
    btn_terminal: str
    """Основная кнопка Mini App — открывает «Терминал» (бывший live_timer, теперь полный хаб)."""
    btn_live_timer: str
    btn_world: str
    btn_mutations: str
    btn_top: str
    btn_immunity: str
    """Reply-кнопка Mini App (восстановление / статус иммунитета)."""
    stub_feature_soon: str
    """Ответ на кнопки меню, пока раздела нет."""
    btn_back: str
    """Возврат с «дочерней» reply-клавиатуры (экран передачи штамма)."""
    back_to_main_ack: str
    """Короткое подтверждение после «Назад»."""
    status_use_start: str

    referral_new_carrier: str
    """HTML; {newcomer} — упоминание; {bonus_block} — referral_timer_bonus или пусто; {branch_total} — int."""

    referral_timer_bonus: str
    """Одна строка о продлении таймера; {bonus_hms} — +H:MM:SS; с \\n\\n в конце."""

    menu_open_mini_hint: str
    """Если разделы ведут в Mini App: ответ при нажатии текста меню (редко — дублирует кнопки)."""

    sweep_warn_10m: str
    sweep_warn_30m: str
    sweep_warn_2h: str
    sweep_warn_1h: str

    immune_activated_notice: str
    """HTML; сообщение в чат после активации иммунитета из Mini App."""
    sweep_immune_ended: str
    """HTML; иммунитет истёк — снова infected с таймером."""

    lab_ready_push: str
    """HTML; пуш воркера: анализ Лабы готов."""
    lab_revived_push: str
    """HTML; пуш воркера: зомби воскрешён через Лабу. {timer_hours:g} — часов бонуса."""

    affliction_type_necrosis_bloom: str
    affliction_type_signal_spoof: str
    affliction_type_enzyme_leak: str
    affliction_type_latency_fog: str
    """Локализованные названия типов дебаффов штамма."""

    affliction_spawn_push_pool: tuple[str, ...]
    """HTML; варианты пуша о появлении дебаффа. {strain} {type} {sev}."""

    affliction_cured_push_pool: tuple[str, ...]
    """HTML; варианты пуша о лечении дебаффа. {strain} {type}."""

    admin_forbidden: str
    """Ответ, если не админ нажал скрытую кнопку или подделал текст."""
    admin_panel_intro: str
    """HTML; при открытии админ-меню."""
    admin_btn_main_menu: str
    """Вернуть reply-клавиатуру как у обычного игрока."""
    admin_btn_me_energy: str
    admin_btn_me_reagents: str
    admin_btn_me_timer: str
    admin_me_need_register: str
    admin_me_energy_ok: str
    """HTML; {e} {m} — энергия и максимум."""
    admin_me_reagents_ok: str
    """HTML; {d} {r} {c}."""
    admin_me_timer_ok: str
    """HTML; {h:g} ч."""
    admin_me_timer_skip: str
    """Таймер без изменений: нужен infected + активный дедлайн."""

    boost_card_header: str
    """HTML; заголовок карточки boost в чате от бота."""
    boost_card_bonus: str
    """HTML; {bonus_pct} — процент бонуса."""
    boost_card_expires: str
    """HTML; {expires} — UTC строка."""
    boost_card_uses: str
    """HTML; {uses}."""
    boost_card_url_hint: str
    """Строка перед блоком с URL."""
    boost_btn_copy: str
    """Подпись copy-кнопки."""
    boost_btn_owner_share: str
    """Кнопка inline после покупки boost в ЛС владельцу (switch_inline_query)."""
    boost_btn_spread: str
    """Кнопка «Войти в цепочку» (deep link в бота)."""
    boost_inline_title: str
    """Заголовок inline-результата boost."""
    boost_inline_description: str
    """Описание в списке inline для boost."""
    boost_share_invite_body_html: str
    """HTML карточки приглашения boost в чате получателя; плейсхолдер {sender} — имя отправителя (экранировать в коде)."""


RU = Msg(
    btn_spread="☣️ Передать штамм",
    btn_status="📊 Статус",
    btn_admin="⚙️ Админка",
    welcome_title="Вспышка зафиксирована",
    welcome_subtitle_organic=(
        "Ты — <b>очаг</b> своей цепочки. Пока не поздно, найди носителей.\n\n"
        "<i>Откуда взялся штамм и кто вёл первую запись — в открытом протоколе не сказано. Есть только обратный отсчёт.</i>"
    ),
    welcome_subtitle_referral=(
        "Ты вошёл по чужой ссылке — ты в <b>чужой сети</b>. "
        "Чей это след и зачем цепочка сходится сюда — не объясняют. Играй или сдавай позиции."
    ),
    welcome_timer="Осталось до кризиса",
    welcome_link_hint="Твоя персональная ссылка",
    welcome_no_bot_username="Задай боту username в @BotFather — без него не собрать реферальную ссылку.",
    already_in_game_reinfect=(
        "Ты уже в симуляции. Повторно пройти по чужой ссылке нельзя — "
        "передавай только <b>свою</b> ссылку (кнопка ниже)."
    ),
    welcome_back_title="Очаг снова в эфире.",
    stats_direct="Прямой удар (заражения)",
    stats_network="Под тобой в цепочке",
    stats_country="Твой сектор",
    stats_banner="СВОДКА ОЧАГА",
    share_title=(
        "Биологический пакет собран.\n"
        "Выбери контакт кнопкой ниже — <b>бот отправит ему карточку</b> в Telegram (только ссылка на бота, <code>t.me/…</code>).\n\n"
        "Ссылку в карточке можно скопировать тапом по строке.\n\n"
        "Каждый открывший по твоей ссылке — <b>+{bonus_hours:g} ч.</b> тебе.\n"
        "Каждый просроченный — минус один выживший."
    ),
    invite_share_bonus_for_inviter_line="Каждый, кто откроет эту ссылку, отправителю — <b>+{bonus_hours:g} ч.</b> к таймеру.",
    share_no_username="У бота нет username — задай его в @BotFather.",
    spread_open_failed="Не удалось открыть экран передачи. Отправь <code>/start</code> ещё раз.",
    timer_inactive="Таймер не активен.",
    timer_zombie="💀 <b>ДЕГРАДАЦИЯ ЗАВЕРШЕНА · ЗОМБИ</b>\n\nСостояние: <b>зомби</b>. Открой полную карточку через /start.",
    timer_expired_pending="Редкий сбой данных. Обнови <code>/start</code> или подожди минуту.",
    timer_zombie_transition_pending=(
        "<b>🧪 ОЦЕНКА СОСТОЯНИЯ</b> · превращение в зомби\n\n"
        "Кризисный дедлайн исчерпан: фиксируем фазу деградации. Статус <b>зомби</b> обычно закрепляется в чате в течение <b>около минуты</b> "
        "(симуляция синхронизируется по минутному циклу).\n\n"
        "Можно снова открыть <code>/start</code> или подождать следующее сообщение."
    ),
    zombie_screen06_banner="ПРЕВРАЩЕНИЕ В ЗОМБИ",
    zombie_card_header="ДЕГРАДАЦИЯ ЗАВЕРШЕНА · ЗОМБИ",
    zombie_card_body=(
        "Время вышло.\n\n"
        "Ты больше не человек — ты <b>зомби</b>.\n"
        "Вирус ведёт себя хаотично — <i>или по сценарию, который нам не показывают</i>.\n\n"
        "Игра не закончена."
    ),
    zombie_card_hint=(
        "Три пути выйти из зомби-режима:\n"
        "— <b>🧪 Лаба</b> — 3 цикла подряд без пропуска → воскрешение (+48 ч)\n"
        "— <b>🌊 Фонтан</b> — участвуй в глобальном ивенте → шанс воскреснуть\n"
        "— <b>🛡 Иммунитет</b> — одноразовый протокол через <b>🔬 Терминал</b>"
    ),
    zombie_bar_label="НЕКРОЗ",
    zombie_phase_label="ФАЗА ЗОМБИ",
    zombie_badges_line="ЗОМБИ  ХАОТИЧНОЕ ЗАРАЖЕНИЕ",
    zombie_timer_strip=(
        "🟪🟪🟪🟪🟪🟪🟪🟪🟪 <b>НЕКРОЗ</b>\n"
        "⏱ <b>кризисный таймер отключён</b> · фаза зомби"
    ),
    timer_countdown="До кризиса",
    timer_reserve="<i>Запас окна до кризиса: <b>{pct}%</b></i>",
    timer_zone_title="ОБРАТНЫЙ ОТСЧЁТ",
    timer_extend_sources=(
        "<b>От чего растёт время</b>\n"
        "• Новый игрок по твоей ссылке — <b>+{bonus_hours:g} ч.</b>\n"
        "• Лаборатория в <b>🔬 Терминале</b> — до <b>+8 ч.</b> в сутки\n"
        "• Фонтан жизни там же — <b>+12 ч.</b> участникам ивента"
    ),
    own_invite_card_title="Код распространения · активен",
    btn_refresh_remain="Сколько осталось",
    btn_pick_contacts="🧬 Мои Контакты",
    hint_after_contacts_shared=(
        "Если ты только что вставил inline-карточку через кнопку под сообщением, собеседник уже получил приглашение.\n\n"
        "Иначе перешли своё сообщение со ссылкой или отправь ссылку вручную."
    ),
    invite_bottom_keyboard_prompt=(
        "Устаревшее: нажми кнопку <b>«☣️ Передать штамм»</b> под сообщением — inline, выбери чат и вставь карточку."
    ),
    spread_contact_send_failed=(
        "Не удалось доставить карточку: у контакта может быть заблокирован бот или закрыты ЛС от незнакомых."
    ),
    spread_contact_sent_ok="Карточка отправлена выбранному контакту в чат с ботом.",
    spread_join_chain_button="☣️ Войти в цепочку заражений",
    share_native_prefill=(
        "Меня уже вписали в цепочку. Открой — узнаешь, не ты ли следующий."
    ),
    mock_header_new="☣️ ШТАММ X-77 · ИНФИЦИРОВАН",
    mock_header_return="🧫 СТАТУС · ШТАММ АКТИВЕН",
    mock_header_status="🧫 СТАТУС · ШТАММ АКТИВЕН",
    mock_header_invite="🧬 КОД РАСПРОСТРАНЕНИЯ · АКТИВЕН",
    mock_body_new_organic=(
        "Поздравляю. Ты только что подхватил нечто, от чего нет вакцины.\n\n"
        "У тебя <b>{timer_hours_phrase}</b> пока не началась деградация.\n"
        "Единственный способ выжить — <b>распространить штамм</b> как можно быстрее.\n\n"
        "<i>В реестре есть пометка «источник недоступен для перекрёстной проверки» — как будто кто-то стёр хвост.</i>"
    ),
    mock_body_new_referral=(
        "Ты вошёл по чужой ссылке — ты в <b>чужой сети</b>.\n"
        "Окно до кризиса уже тикает. Играй на опережение — или сдавай позиции."
    ),
    mock_body_return=(
        "Штамм распространяется. Твоя цепочка охватила <b>{network}</b>.\n"
        "Неплохо — но вирус не спит. Таймер тоже."
    ),
    mock_badges_new=(
        "<code>ЗАРАЖЁН</code>  <code>ЦЕПОЧКА #1</code>  <code>РАНГ: НОСИТЕЛЬ</code>"
    ),
    mock_badges_active="<i>☣️ ЗАРАЖЁН · СЕТЬ АКТИВНА · НОСИТЕЛЬ</i>",
    invite_link_box_label="▸ ПЕРСОНАЛЬНЫЙ ШТАММ-ЛИНК",
    mock_vita_label="ЗАПАС",
    mock_decay_label="ДО РАСПАДА",
    mock_stat_ab_direct="прямых по ссылке",
    mock_stat_ab_net="всего в сети под тобой",
    mock_stat_ab_sector="Рейтинг в мире",
    mock_header_immune="🛡 ИММУНИТЕТ · ВОССТАНОВЛЕНИЕ",
    mock_body_immune=(
        "Активирован <b>защитный протокол</b> после деградации. "
        "До конца окна кризисный таймер не идёт — затем симуляция продолжится с новым дедлайном."
    ),
    mock_immune_vita_label="ЩИТ",
    mock_immune_decay_label="ДО КОНЦА ОКНА",
    timer_immune_line="🛡 Иммунитет: <code>{time_str}</code>",
    status_title="Статус",
    btn_terminal="🔬 Терминал",
    btn_live_timer="⏱ Таймер",
    btn_world="🌍 Мир",
    btn_mutations="🧬 Мутации",
    btn_top="🏆 Топ",
    btn_immunity="🛡 Иммунитет",
    stub_feature_soon="Раздел ещё в разработке — загляни позже.",
    btn_back="↩ Назад",
    back_to_main_ack="Главное меню.",
    status_use_start="Сначала открой /start в боте.",
    referral_new_carrier=(
        "✅ <b>ШТАММ ПРИНЯТ · НОВЫЙ НОСИТЕЛЬ</b>\n\n"
        "Ещё один.\n\n"
        "{newcomer} открыл твою ссылку и\n"
        "уже заражён. Твоя цепочка растёт.\n\n"
        "{bonus_block}"
        "Итого носителей в ветке: <b>{branch_total}</b>"
    ),
    referral_timer_bonus="<b>{bonus_hms}</b> к твоему таймеру.\n\n",
    menu_open_mini_hint=(
        "Открой <b>🔬 Терминал</b> внизу чата с ботом — там таймер, лаба и фонтан.\n\n"
        "<i>Иногда строки там расходятся с «официальным» брифом — в симуляции так и заложено.</i>"
    ),
    sweep_warn_10m=(
        "💀 <b>КРИТИЧЕСКИЙ УРОВЕНЬ</b>\n\n"
        "Слышишь? Это твои клетки.\n\n"
        "Осталось <b>меньше 10 минут</b>. Каждое заражение сейчас — "
        "<b>+4 ч.</b> Или ты станешь следующим зомби в статистике.\n\n"
        "Передай ссылку."
    ),
    sweep_warn_30m=(
        "⚠️ <b>30 МИНУТ ДО КРИЗИСА</b>\n\n"
        "Штамм ждёт. Таймер — нет.\n\n"
        "Одно заражение прямо сейчас даёт <b>+4 ч.</b> — "
        "хватит, чтобы пережить эту волну."
    ),
    sweep_warn_2h="⏱ До кризиса <b>меньше 2 часов</b>. Распространяй штамм.",
    sweep_warn_1h=(
        "🔴 <b>МЕНЬШЕ ЧАСА</b> до кризиса.\n\n"
        "Твой таймер в красной зоне. Успей передать ссылку — "
        "<b>+4 ч.</b> за каждого нового носителя."
    ),
    immune_activated_notice=(
        "<b>🛡 Иммунитет активирован</b>\n\n"
        "Срок смотри в Mini App (кнопка «Иммунитет») или обнови карточку через /start."
    ),
    sweep_immune_ended=(
        "<b>Окно иммунитета закончилось</b>\n\n"
        "Таймер кризиса снова запущен — распространяй ссылку, чтобы не вернуться в зомби."
    ),
    lab_ready_push=(
        "🧪 <b>АНАЛИЗ ЗАВЕРШЁН</b>\n\n"
        "Образец обработан. Открой <b>Лабораторию</b> и забери результат.\n\n"
        "<i>В хвосте лога — фрагмент без расшифровки. На выдачу результата это не влияет.</i>"
    ),
    lab_revived_push=(
        "⚡ <b>ВОСКРЕШЕНИЕ</b>\n\n"
        "Лаборатория сработала. Ты снова <b>Infected</b>.\n"
        "Новый дедлайн: <b>+{timer_hours:g} ч.</b> — распространяй штамм."
    ),
    affliction_type_necrosis_bloom="некроз‑цветение",
    affliction_type_signal_spoof="подмена сигнала",
    affliction_type_enzyme_leak="утечка фермента",
    affliction_type_latency_fog="туман задержки",
    affliction_spawn_push_pool=(
        "📡 <b>Сводка штамма</b>\n\nВ {strain} зафиксирован новый сбой: <b>{type}</b> ({sev}).\n"
        "Лаба просит помощь: откройте «🧪 Лаборатория» и завершайте циклы, чтобы найти лекарство.",
        "☣️ <b>Аномалия</b>\n\nУ штамма {strain}: <b>{type}</b> ({sev}).\n"
        "Если хотите выжить красиво — заходите в Лабу и приносите результаты анализа.",
    ),
    affliction_cured_push_pool=(
        "🧬 <b>Лекарство готово</b>\n\nШтамм {strain}: протокол против <b>{type}</b> завершён.\n"
        "Давление спало. Можно снова спокойно фармить Лабу и готовиться к Фонтану.",
        "✅ <b>Вылечено</b>\n\n{strain}: эффект <b>{type}</b> нейтрализован.\n"
        "Лаба сработала. Держим темп.",
    ),
    admin_forbidden="Недостаточно прав.",
    admin_panel_intro="<b>Админ-панель</b>\n\nВыбери действие — каждая кнопка на отдельной строке.",
    admin_btn_main_menu="↩ Обычное меню",
    admin_btn_me_energy="⚡ Мне: полная энергия кликера",
    admin_btn_me_reagents="🧬 Мне: +500 ДНК · +500 РНК · +50 CAT",
    admin_btn_me_timer="⏱ Мне: +24 ч к таймеру",
    admin_me_need_register="Нет записи в игре — зайди через /start.",
    admin_me_energy_ok="<b>Энергия</b>: <code>{e}</code> / <code>{m}</code>",
    admin_me_reagents_ok="<b>Реагенты</b>: ДНК <code>{d}</code> · РНК <code>{r}</code> · CAT <code>{c}</code>",
    admin_me_timer_ok="<b>Таймер</b>: +<code>{h:g}</code> ч к дедлайну.",
    admin_me_timer_skip="Таймер без изменений: нужен статус <b>infected</b> и активный дедлайн.",
    boost_card_header="🧬 <b>УСИЛЕННАЯ ССЫЛКА</b>",
    boost_card_bonus="Бонус за нового носителя: <b>+{bonus_pct}%</b> к времени таймера.",
    boost_card_expires="Действует до: <code>{expires}</code>",
    boost_card_uses="Использований: <b>{uses}</b>",
    boost_card_url_hint="Ссылка для нового носителя:",
    boost_btn_copy="📋 Скопировать ссылку",
    boost_btn_owner_share="УСИЛЕННОЕ ЗАРАЖЕНИЕ",
    boost_btn_spread="☣️ Войти в цепочку",
    boost_inline_title="🧬 Усиленное приглашение",
    boost_inline_description="Отправь усиленный штамм выбранному контакту.",
    boost_share_invite_body_html=(
        "<b>{sender}</b> передаёт тебе усиленный штамм.\n\n"
        "Симуляция ждёт нового носителя.\n"
        "Открой приглашение и войди в цепочку."
    ),
)

EN = Msg(
    btn_spread="☣️ Spread strain",
    btn_status="📊 Status",
    btn_admin="⚙️ Admin",
    welcome_title="Outbreak logged",
    welcome_subtitle_organic=(
        "You're the <b>index case</b> of your chain. Find hosts before it's too late.\n\n"
        "<i>The public brief won't name a source. There's only the countdown.</i>"
    ),
    welcome_subtitle_referral=(
        "You joined via someone else's link — you're in <b>their</b> network. "
        "<i>Who routed you here — unstated.</i>"
    ),
    welcome_timer="Time until crisis",
    welcome_link_hint="Your personal link",
    welcome_no_bot_username="Set a bot username in @BotFather — required for referral links.",
    already_in_game_reinfect=(
        "You're already in the sim. You can't re-enter via another link — "
        "share only <b>your</b> link (button below)."
    ),
    welcome_back_title="Patient zero is back online.",
    stats_direct="Direct hits (infections)",
    stats_network="Under you in the chain",
    stats_country="Your sector",
    stats_banner="OUTBREAK BRIEF",
    share_title=(
        "Biological payload ready.\n"
        "Use <b>My contacts</b> below — <b>the bot will send them a card</b> in Telegram (bot link only, <code>t.me/…</code>).\n\n"
        "They can copy the link from the card by tapping the line.\n\n"
        "Everyone who opens your link — <b>+{bonus_hours:g} h</b> for you.\n"
        "Every missed deadline — one less survivor."
    ),
    invite_share_bonus_for_inviter_line="Everyone who opens this link adds <b>+{bonus_hours:g} h</b> to the sender's timer.",
    share_no_username="The bot has no username — set it in @BotFather.",
    spread_open_failed="Couldn't open the spread screen. Send <code>/start</code> again.",
    timer_inactive="Timer inactive.",
    timer_zombie="💀 <b>DEGRADATION COMPLETE · ZOMBIE</b>\n\nState: <b>zombie</b>. Open the full card with /start.",
    timer_expired_pending="Rare data glitch. Try <code>/start</code> or wait a minute.",
    timer_zombie_transition_pending=(
        "<b>🧪 STATE ASSESSMENT</b> · turning zombie\n\n"
        "Crisis deadline is over: we're locking in the degradation phase. Your <b>zombie</b> status usually appears in chat "
        "within <b>about a minute</b> (the sim syncs on a once-per-minute tick).\n\n"
        "Send <code>/start</code> again or wait for the next message."
    ),
    zombie_screen06_banner="💀 SCREEN 06 · ZOMBIE TRANSFORMATION",
    zombie_card_header="DEGRADATION COMPLETE · ZOMBIE",
    zombie_card_body=(
        "Time's up.\n\n"
        "You're no longer in the previous state — you're a <b>zombie</b>. "
        "The strain behaves chaotically — <i>or on a script we never get to read</i>.\n\n"
        "Your branch still has <b>{chain_total}</b> carriers under you.\n\n"
        "<b>The game isn't over.</b>"
    ),
    zombie_card_hint=(
        "Three ways out of zombie mode:\n"
        "— <b>🧪 Lab</b> — 3 cycles in a row without missing → resurrection (+48h)\n"
        "— <b>🌊 Fountain</b> — join the global event → chance to revive\n"
        "— <b>🛡 Immunity</b> — one-shot protocol via <b>🔬 Terminal</b>"
    ),
    zombie_bar_label="NECROSIS",
    zombie_phase_label="ZOMBIE PHASE",
    zombie_badges_line="<code>ZOMBIE</code>  <code>CHAOTIC SPREAD</code>",
    zombie_timer_strip=(
        "🟪🟪🟪🟪🟪🟪🟪🟪🟪 <b>NECROSIS</b>\n"
        "⏱ <b>crisis timer off</b> · zombie phase"
    ),
    timer_countdown="Until crisis",
    timer_reserve="<i>Window left before crisis: <b>{pct}%</b></i>",
    timer_zone_title="COUNTDOWN",
    timer_extend_sources=(
        "<b>What adds time</b>\n"
        "• A new player via your link — <b>+{bonus_hours:g} h</b>\n"
        "• Lab — up to <b>+8 h</b> per day\n"
        "• Fountain of Life — <b>+12 h</b> for participants (global event)"
    ),
    own_invite_card_title="Propagation code · active",
    btn_refresh_remain="Time left",
    btn_pick_contacts="🧬 My contacts",
    hint_after_contacts_shared=(
        "If you just inserted the inline card via the button under the message, they already got the invite.\n\n"
        "Otherwise forward your link message or paste the link manually."
    ),
    invite_bottom_keyboard_prompt=(
        "Legacy: tap <b>«☣️ Spread strain»</b> under the message — inline, pick a chat and insert the card."
    ),
    spread_contact_send_failed=(
        "Could not deliver the card — they may have blocked the bot or restricted DMs from non-contacts."
    ),
    spread_contact_sent_ok="Card sent to the selected contact in their chat with the bot.",
    spread_join_chain_button="☣️ Join the infection chain",
    share_native_prefill="I'm already in the chain. Open this — see if you're next.",
    mock_header_new="☣️ STRAIN X-77 · INFECTED",
    mock_header_return="🧫 STATUS · STRAIN ACTIVE",
    mock_header_status="🧫 STATUS · STRAIN ACTIVE",
    mock_header_invite="🧬 PROPAGATION CODE · ACTIVE",
    mock_body_new_organic=(
        "Congrats — you just caught something there's no vaccine for.\n\n"
        "You have <b>{timer_hours_phrase}</b> before degradation begins.\n"
        "The only way to survive is to <b>spread the strain</b> as fast as you can.\n\n"
        "<i>Registry footnote: source marked <b>unverifiable</b> — like someone clipped the trail.</i>"
    ),
    mock_body_new_referral=(
        "You joined via someone else's link — you're in <b>their</b> network.\n"
        "The crisis clock is already running. Play ahead — or fold."
    ),
    mock_body_return=(
        "The strain is spreading. Your chain has reached <b>{network}</b>.\n"
        "Not bad — but the virus never sleeps. Neither does the timer."
    ),
    mock_badges_new=(
        "<code>INFECTED</code>  <code>CHAIN #1</code>  <code>RANK: CARRIER</code>"
    ),
    mock_badges_active="<i>☣️ INFECTED · NETWORK LIVE · CARRIER</i>",
    invite_link_box_label="▸ PERSONAL STRAIN LINK",
    mock_vita_label="RESERVE",
    mock_decay_label="UNTIL DECAY",
    mock_stat_ab_direct="direct (your link)",
    mock_stat_ab_net="in your branch",
    mock_stat_ab_sector="World ranking",
    mock_header_immune="🛡 IMMUNITY · RECOVERY",
    mock_body_immune=(
        "<b>Protective protocol</b> is active after degradation. "
        "The crisis timer is on hold until this window ends — then the sim restarts with a fresh deadline."
    ),
    mock_immune_vita_label="SHIELD",
    mock_immune_decay_label="WINDOW LEFT",
    timer_immune_line="🛡 Immunity: <code>{time_str}</code>",
    status_title="Status",
    btn_terminal="🔬 Terminal",
    btn_live_timer="⏱ Timer",
    btn_world="🌍 World",
    btn_mutations="🧬 Mutations",
    btn_top="🏆 Top",
    btn_immunity="🛡 Immunity",
    stub_feature_soon="This section is still in development — check back later.",
    btn_back="↩ Back",
    back_to_main_ack="Main menu.",
    status_use_start="Open /start in the bot first.",
    referral_new_carrier=(
        "Another one.\n\n"
        "{newcomer} opened your link and\n"
        "is infected now. Your chain is growing.\n\n"
        "{bonus_block}"
        "Carriers in your branch so far: <b>{branch_total}</b>"
    ),
    referral_timer_bonus="<b>{bonus_hms}</b> added to your timer.\n\n",
    menu_open_mini_hint=(
        "Tap <b>🔬 Terminal</b> at the bottom of the bot chat — timer, lab, and fountain are there.\n\n"
        "<i>Sometimes lines there don't match the public brief — that's part of the sim.</i>"
    ),
    sweep_warn_10m="<b>Less than 10 minutes</b> to crisis. Share your link.",
    sweep_warn_30m="<b>Less than 30 minutes</b> to crisis.",
    sweep_warn_2h="<b>Less than 2 hours</b> to crisis.",
    sweep_warn_1h="<b>Less than an hour</b> to crisis. Share your link.",
    immune_activated_notice=(
        "<b>🛡 Immunity activated</b>\n\n"
        "Track time left in the Mini App (Immunity button) or refresh with /start."
    ),
    sweep_immune_ended=(
        "<b>Immunity window closed</b>\n\n"
        "Crisis timer is running again — spread your link so you don't fall back to zombie."
    ),
    lab_ready_push=(
        "🧪 <b>ANALYSIS COMPLETE</b>\n\n"
        "Sample processed. Open <b>Lab</b> and claim your result.\n\n"
        "<i>Log tail shows an undecoded fragment — it doesn't block your pickup.</i>"
    ),
    lab_revived_push=(
        "⚡ <b>RESURRECTION</b>\n\n"
        "The Lab worked. You're <b>Infected</b> again.\n"
        "New deadline: <b>+{timer_hours:g} h</b> — spread the strain."
    ),
    affliction_type_necrosis_bloom="necrosis bloom",
    affliction_type_signal_spoof="signal spoof",
    affliction_type_enzyme_leak="enzyme leak",
    affliction_type_latency_fog="latency fog",
    affliction_spawn_push_pool=(
        "📡 <b>Strain brief</b>\n\nA new failure was detected in {strain}: <b>{type}</b> ({sev}).\n"
        "Lab needs help: open «🧪 Laboratory» and finish cycles to produce a cure.",
        "☣️ <b>Anomaly</b>\n\n{strain} is unstable: <b>{type}</b> ({sev}).\n"
        "Get to the Lab and bring results — each claim moves the cure forward.",
    ),
    affliction_cured_push_pool=(
        "🧬 <b>Cure ready</b>\n\n{strain}: protocol against <b>{type}</b> is complete.\n"
        "Pressure is down. Back to Lab farming and Fountain prep.",
        "✅ <b>Cured</b>\n\n{strain}: <b>{type}</b> has been neutralized.\n"
        "Lab delivered. Keep the pace.",
    ),
    admin_forbidden="Access denied.",
    admin_panel_intro="<b>Admin panel</b>\n\nPick an action — one button per row.",
    admin_btn_main_menu="↩ Player menu",
    admin_btn_me_energy="⚡ Me: full clicker energy",
    admin_btn_me_reagents="🧬 Me: +500 DNA · +500 RNA · +50 CAT",
    admin_btn_me_timer="⏱ Me: +24 h to crisis timer",
    admin_me_need_register="No game profile — open /start first.",
    admin_me_energy_ok="<b>Energy</b>: <code>{e}</code> / <code>{m}</code>",
    admin_me_reagents_ok="<b>Reagents</b>: DNA <code>{d}</code> · RNA <code>{r}</code> · CAT <code>{c}</code>",
    admin_me_timer_ok="<b>Timer</b>: +<code>{h:g}</code> h to deadline.",
    admin_me_timer_skip="Timer unchanged: need <b>infected</b> with an active deadline.",
    boost_card_header="🧬 <b>BOOSTED LINK</b>",
    boost_card_bonus="New carrier bonus: <b>+{bonus_pct}%</b> to your timer time.",
    boost_card_expires="Valid until: <code>{expires}</code>",
    boost_card_uses="Uses: <b>{uses}</b>",
    boost_card_url_hint="Link for a new carrier:",
    boost_btn_copy="📋 Copy link",
    boost_btn_owner_share="BOOSTED INFECTION",
    boost_btn_spread="☣️ Join the chain",
    boost_inline_title="🧬 Boosted invite",
    boost_inline_description="Send the boosted strain to a contact.",
    boost_share_invite_body_html=(
        "<b>{sender}</b> sends you the boosted strain.\n\n"
        "The simulation awaits a new carrier.\n"
        "Open the invite and join the chain."
    ),
)

# Украинский: базовый набор; при необходимости вынести в отдельный файл
UK = Msg(
    btn_spread="☣️ Передати штам",
    btn_status="📊 Статус",
    btn_admin="⚙️ Адмінка",
    welcome_title="Спалах зафіксовано",
    welcome_subtitle_organic=(
        "Ти — <b>осередок</b> свого ланцюга. Знайди носіїв, поки не пізно.\n\n"
        "<i>Звідки штам і хто вів першопочатковий запис — у відкритому брифі не сказано. Є лише зворотний відлік.</i>"
    ),
    welcome_subtitle_referral=(
        "Ти зайшов за чужим посиланням — ти в <b>чужій мережі</b>. "
        "Чий це слід і навіщо ланцюг зходиться сюди — не пояснюють. Грай або здавай позиції."
    ),
    welcome_timer="Залишилось до кризу",
    welcome_link_hint="Твоє персональне посилання",
    welcome_no_bot_username="Задай боту username у @BotFather — без цього не зібрати реферальне посилання.",
    already_in_game_reinfect=(
        "Ти вже в симуляції. Повторно пройти за чужим посиланням не можна — "
        "передавай лише <b>своє</b> посилання (кнопка нижче)."
    ),
    welcome_back_title="Вогнище знову в ефірі.",
    stats_direct="Прямі ураження",
    stats_network="Під тобою в ланцюгу",
    stats_country="Твій сектор",
    stats_banner="ЗВЕДЕННЯ ВОГНИЩА",
    share_title=(
        "Біологічний пакет зібрано.\n"
        "Натисни <b>«🧬 Мої контакти»</b> нижче — <b>бот надішле контакту картку</b> у Telegram (лише посилання на бота, <code>t.me/…</code>).\n\n"
        "Посилання в картці можна скопіювати дотиком до рядка.\n\n"
        "Кожен, хто відкриє твоє посилання — <b>+{bonus_hours:g} год.</b> тобі.\n"
        "Кожен прострочений — мінус один той, хто вижив."
    ),
    invite_share_bonus_for_inviter_line="Кожен, хто відкриє це посилання, відправнику — <b>+{bonus_hours:g} год.</b> до таймера.",
    share_no_username="У бота немає username — задай у @BotFather.",
    spread_open_failed="Не вдалося відкрити екран передачі. Надішли <code>/start</code> ще раз.",
    timer_inactive="Таймер не активний.",
    timer_zombie="💀 <b>ДЕГРАДАЦІЮ ЗАВЕРШЕНО · ЗОМБІ</b>\n\nСтан: <b>зомбі</b>. Повну картку — <code>/start</code>.",
    timer_expired_pending="Рідкий збій даних. Спробуй <code>/start</code> або зачекай хвилину.",
    timer_zombie_transition_pending=(
        "<b>🧪 ОЦІНКА СТАНУ</b> · перехід у зомбі\n\n"
        "Кризовий дедлайн вичерпано: фіксуємо фазу деградації. Статус <b>зомбі</b> зазвичай з’являється в чаті протягом <b>близько хвилини</b> "
        "(симуляція синхронізується щохвилини).\n\n"
        "Можна знову відкрити <code>/start</code> або дочекатися наступного повідомлення."
    ),
    zombie_screen06_banner="💀 SCREEN 06 · ПЕРЕТВОРЕННЯ НА ЗОМБІ",
    zombie_card_header="ДЕГРАДАЦІЮ ЗАВЕРШЕНО · ЗОМБІ",
    zombie_card_body=(
        "Час вийшов.\n\n"
        "Ти вже не в попередньому статусі — ти <b>зомбі</b>. "
        "Штам поводиться хаотично — <i>або за сценарієм, який нам не показують</i>.\n\n"
        "У твоїй гілці під тобою досі <b>{chain_total}</b> носіїв.\n\n"
        "<b>Гра не закінчена.</b>"
    ),
    zombie_card_hint=(
        "Три шляхи вийти з зомбі-режиму:\n"
        "— <b>🧪 Лаба</b> — 3 цикли поспіль без пропуску → воскресіння (+48 год)\n"
        "— <b>🌊 Фонтан</b> — бери участь у глобальному івенті → шанс воскреснути\n"
        "— <b>🛡 Імунітет</b> — одноразовий протокол через <b>🔬 Термінал</b>"
    ),
    zombie_bar_label="НЕКРОЗ",
    zombie_phase_label="ФАЗА ЗОМБІ",
    zombie_badges_line="<code>ЗОМБІ</code>  <code>ХАОТИЧНЕ ЗАРАЖЕННЯ</code>",
    zombie_timer_strip=(
        "🟪🟪🟪🟪🟪🟪🟪🟪🟪 <b>НЕКРОЗ</b>\n"
        "⏱ <b>кризовий таймер вимкнено</b> · фаза зомбі"
    ),
    timer_countdown="До кризу",
    timer_reserve="<i>Запас вікна до кризу: <b>{pct}%</b></i>",
    timer_zone_title="ЗВОРОТНІЙ ВІДЛІК",
    timer_extend_sources=(
        "<b>Звідки береться час</b>\n"
        "• Новий гравець за твоїм посиланням — <b>+{bonus_hours:g} год.</b>\n"
        "• Лабораторія в <b>🔬 Терміналі</b> — до <b>+8 год.</b> на добу\n"
        "• Фонтан життя там само — <b>+12 год.</b> учасникам івенту"
    ),
    own_invite_card_title="Код поширення · активний",
    btn_refresh_remain="Скільки лишилось",
    btn_pick_contacts="🧬 Мої контакти",
    hint_after_contacts_shared=(
        "Якщо ти щойно вставив inline-картку через кнопку під повідомленням, контакт уже отримав запрошення.\n\n"
        "Інакше перешли повідомлення з посиланням або встав посилання вручну."
    ),
    invite_bottom_keyboard_prompt=(
        "Застаріле: натисни <b>«☣️ Передати штам»</b> під повідомленням — inline, обери чат і встав картку."
    ),
    spread_contact_send_failed=(
        "Не вдалося доставити картку: бот може бути заблокований або закриті ЛС від незнайомих."
    ),
    spread_contact_sent_ok="Картку надіслано обраному контакту в чат із ботом.",
    spread_join_chain_button="☣️ Увійти в ланцюг заражень",
    share_native_prefill="Мене вже вписали в ланцюг. Відкрий — дізнаєшся, чи не ти наступний.",
    mock_header_new="☣️ ШТАМ X-77 · ІНФІКОВАНО",
    mock_header_return="🧫 СТАТУС · ШТАМ АКТИВНИЙ",
    mock_header_status="🧫 СТАТУС · ШТАМ АКТИВНИЙ",
    mock_header_invite="🧬 КОД ПОШИРЕННЯ · АКТИВНИЙ",
    mock_body_new_organic=(
        "Вітаю. Ти щойно підхопив щось, від чого немає вакцини.\n\n"
        "У тебе <b>{timer_hours_phrase}</b>, поки не почалася деградація.\n"
        "Єдиний спосіб вижити — <b>поширити штам</b> якомога швидше.\n\n"
        "<i>У реєстрі є позначка «джерело недоступне для перехресної перевірки» — ніби хтось обрізав слід.</i>"
    ),
    mock_body_new_referral=(
        "Ти зайшов за чужим посиланням — ти в <b>чужій мережі</b>.\n"
        "Вікно до кризу вже тікає. Грай на випередження — або здавай позиції."
    ),
    mock_body_return=(
        "Штам поширюється. Твій ланцюг охопив <b>{network}</b>.\n"
        "Непогано — але вірус не спить. Таймер теж."
    ),
    mock_badges_new=(
        "<code>ЗАРАЖЕНИЙ</code>  <code>ЛАНЦЮГ #1</code>  <code>РАНГ: НОСІЙ</code>"
    ),
    mock_badges_active="<i>☣️ ЗАРАЖЕНИЙ · МЕРЕЖА АКТИВНА · НОСІЙ</i>",
    invite_link_box_label="▸ ПЕРСОНАЛЬНИЙ ШТАМ-ЛІНК",
    mock_vita_label="ЗАПАС",
    mock_decay_label="ДО РОЗПАДУ",
    mock_stat_ab_direct="прямих за посиланням",
    mock_stat_ab_net="усього в мережі під тобою",
    mock_stat_ab_sector="Рейтинг у світі",
    mock_header_immune="🛡 ІМУНІТЕТ · ВІДНОВЛЕННЯ",
    mock_body_immune=(
        "Увімкнено <b>захисний протокол</b> після деградації. "
        "До кінця вікна кризовий таймер не йде — далі симуляція продовжиться з новим дедлайном."
    ),
    mock_immune_vita_label="ЩИТ",
    mock_immune_decay_label="ДО КІНЦЯ ВІКНА",
    timer_immune_line="🛡 Імунітет: <code>{time_str}</code>",
    status_title="Статус",
    btn_terminal="🔬 Термінал",
    btn_live_timer="⏱ Таймер",
    btn_world="🌍 Світ",
    btn_mutations="🧬 Мутації",
    btn_top="🏆 Топ",
    btn_immunity="🛡 Імунітет",
    stub_feature_soon="Розділ ще в розробці — зайди пізніше.",
    btn_back="↩ Назад",
    back_to_main_ack="Головне меню.",
    status_use_start="Спочатку відкрий /start у боті.",
    referral_new_carrier=(
        "Ще один.\n\n"
        "{newcomer} відкрив твоє посилання й\n"
        "вже заражений. Твій ланцюг росте.\n\n"
        "{bonus_block}"
        "Усього носіїв у гілці: <b>{branch_total}</b>"
    ),
    referral_timer_bonus="<b>{bonus_hms}</b> до твого таймера.\n\n",
    menu_open_mini_hint=(
        "Натисни <b>🔬 Термінал</b> внизу чату з ботом — там таймер, лаба й фонтан.\n\n"
        "<i>Іноді рядки там не збігаються з «офіційним» брифом — у симуляції так і закладено.</i>"
    ),
    sweep_warn_10m="Залишилось <b>менше 10 хвилин</b> до кризу. Передай посилання.",
    sweep_warn_30m="Залишилось <b>менше 30 хвилин</b> до кризу.",
    sweep_warn_2h="Залишилось <b>менше 2 годин</b> до кризу.",
    sweep_warn_1h="Залишилось <b>менше години</b> до кризу. Передай посилання.",
    immune_activated_notice=(
        "<b>🛡 Імунітет активовано</b>\n\n"
        "Термін — у Mini App (кнопка «Імунітет») або онови картку через /start."
    ),
    sweep_immune_ended=(
        "<b>Вікно імунітету закінчилось</b>\n\n"
        "Таймер кризу знову запущено — поширюй посилання, щоб не повернутися в зомбі."
    ),
    lab_ready_push=(
        "🧪 <b>АНАЛІЗ ЗАВЕРШЕНО</b>\n\n"
        "Зразок оброблено. Відкрий <b>Лабораторію</b> та забери результат.\n\n"
        "<i>У хвості лога — фрагмент без розшифровки. На видачу результату це не впливає.</i>"
    ),
    lab_revived_push=(
        "⚡ <b>ВОСКРЕСІННЯ</b>\n\n"
        "Лабораторія спрацювала. Ти знову <b>Інфікований</b>.\n"
        "Новий дедлайн: <b>+{timer_hours:g} год.</b> — поширюй штам."
    ),
    affliction_type_necrosis_bloom="некроз‑цвітіння",
    affliction_type_signal_spoof="підміна сигналу",
    affliction_type_enzyme_leak="витік ферменту",
    affliction_type_latency_fog="туман затримки",
    affliction_spawn_push_pool=(
        "📡 <b>Зведення штаму</b>\n\nУ {strain} зафіксовано новий збій: <b>{type}</b> ({sev}).\n"
        "Лаба просить допомоги: відкрий «🧪 Лабораторія» і завершуйте цикли, щоб знайти ліки.",
    ),
    affliction_cured_push_pool=(
        "✅ <b>Вилікувано</b>\n\n{strain}: ефект <b>{type}</b> нейтралізовано.\n"
        "Лаба спрацювала. Тримаємо темп.",
    ),
    admin_forbidden="Немає прав.",
    admin_panel_intro="<b>Адмін-панель</b>\n\nОбери дію — кожна кнопка в окремому рядку.",
    admin_btn_main_menu="↩ Меню гравця",
    admin_btn_me_energy="⚡ Мені: повна енергія клікера",
    admin_btn_me_reagents="🧬 Мені: +500 ДНК · +500 РНК · +50 CAT",
    admin_btn_me_timer="⏱ Мені: +24 год до таймера",
    admin_me_need_register="Немає запису в грі — відкрий /start.",
    admin_me_energy_ok="<b>Енергія</b>: <code>{e}</code> / <code>{m}</code>",
    admin_me_reagents_ok="<b>Реагенти</b>: ДНК <code>{d}</code> · РНК <code>{r}</code> · CAT <code>{c}</code>",
    admin_me_timer_ok="<b>Таймер</b>: +<code>{h:g}</code> год до дедлайну.",
    admin_me_timer_skip="Таймер без змін: потрібен <b>infected</b> і активний дедлайн.",
    boost_card_header="🧬 <b>ПІДСИЛЕНЕ ПОСИЛАННЯ</b>",
    boost_card_bonus="Бонус за нового носія: <b>+{bonus_pct}%</b> до часу таймера.",
    boost_card_expires="Діє до: <code>{expires}</code>",
    boost_card_uses="Використань: <b>{uses}</b>",
    boost_card_url_hint="Посилання для нового носія:",
    boost_btn_copy="📋 Скопіювати посилання",
    boost_btn_owner_share="ПОСИЛЕНЕ ЗАРАЖЕННЯ",
    boost_btn_spread="☣️ Увійти в ланцюг",
    boost_inline_title="🧬 Посилене запрошення",
    boost_inline_description="Надішли підсилений штам контакту.",
    boost_share_invite_body_html=(
        "<b>{sender}</b> передає тобі підсилений штам.\n\n"
        "Симуляція чекає нового носія.\n"
        "Відкрий запрошення й увійди в ланцюг."
    ),
)

DE = Msg(
    btn_spread="☣️ Stamm übertragen",
    btn_status="📊 Status",
    btn_admin="⚙️ Admin",
    welcome_title="Ausbruch erfasst",
    welcome_subtitle_organic=(
        "Du bist der <b>Indexfall</b> deiner Kette. Finde Wirte, solange es noch geht.\n\n"
        "<i>Der öffentliche Brief nennt keine Quelle. Es gibt nur den Countdown.</i>"
    ),
    welcome_subtitle_referral=(
        "Du bist über einen fremden Link eingestiegen — du bist in <b>deren</b> Netzwerk. "
        "<i>Wer dich hierher geleitet hat — unbenannt.</i>"
    ),
    welcome_timer="Zeit bis zur Krise",
    welcome_link_hint="Dein persönlicher Link",
    welcome_no_bot_username=(
        "Vergib dem Bot einen @BotFather-Username — sonst gibt es keinen Empfehlungslink."
    ),
    already_in_game_reinfect=(
        "Du bist schon in der Simulation. Über einen anderen Link kommst du nicht erneut rein — "
        "teile nur <b>deinen</b> Link (Button unten)."
    ),
    welcome_back_title="Indexfall wieder online.",
    stats_direct="Direkte Treffer",
    stats_network="Unter dir in der Kette",
    stats_country="Dein Sektor",
    stats_banner="LAGEBILD",
    share_title=(
        "Biologisches Paket bereit.\n"
        "Tippe unten auf <b>«🧬 Meine Kontakte»</b> — <b>der Bot sendet dem Kontakt eine Karte</b> in Telegram (nur Bot-Link, <code>t.me/…</code>).\n\n"
        "Den Link in der Karte kann man per Tippen auf die Zeile kopieren.\n\n"
        "Jeder, der deinen Link öffnet — <b>+{bonus_hours:g} h</b> für dich.\n"
        "Jede verpasste Frist — ein Überlebender weniger."
    ),
    invite_share_bonus_for_inviter_line="Jeder, der diesen Link öffnet, gibt dem Absender <b>+{bonus_hours:g} h</b> auf den Timer.",
    share_no_username="Der Bot hat keinen Username — in @BotFather setzen.",
    spread_open_failed="Übertragungsbildschirm konnte nicht geöffnet werden. Sende <code>/start</code> erneut.",
    timer_inactive="Timer inaktiv.",
    timer_zombie="💀 <b>DEGRADATION ABGESCHLOSSEN · ZOMBIE</b>\n\nStatus: <b>Zombie</b>. Volle Karte: <code>/start</code>.",
    timer_expired_pending="Daten-Kurzfehler. <code>/start</code> oder 1 Minute warten.",
    timer_zombie_transition_pending=(
        "<b>🧪 STATUSCHECK</b> · Zombie-Wende\n\n"
        "Krisen-Deadline ist vorbei: wir sichern die Degradationsphase. Dein <b>Zombie</b>-Status erscheint meist innerhalb "
        "<b>ca. einer Minute</b> (Sim sync jede Minute).\n\n"
        "Erneut <code>/start</code> senden oder auf die nächste Nachricht warten."
    ),
    zombie_screen06_banner="💀 SCREEN 06 · ZOMBIE-WANDEL",
    zombie_card_header="DEGRADATION ABGESCHLOSSEN · ZOMBIE",
    zombie_card_body=(
        "Die Zeit ist um.\n\n"
        "Du bist nicht mehr im alten Status — du bist ein <b>Zombie</b>. "
        "Der Stamm agiert chaotisch — <i>oder nach einem Drehbuch, das wir nicht lesen</i>.\n\n"
        "In deinem Ast unter dir gibt es weiter <b>{chain_total}</b> Wirte.\n\n"
        "<b>Das Spiel ist nicht vorbei.</b>"
    ),
    zombie_card_hint=(
        "Drei Wege aus dem Zombie-Modus:\n"
        "— <b>🧪 Labor</b> — 3 Zyklen ohne Pause → Auferstehung (+48 h)\n"
        "— <b>🌊 Brunnen</b> — am globalen Event teilnehmen → Auferstehungschance\n"
        "— <b>🛡 Immunität</b> — Einmalprotokoll über <b>🔬 Terminal</b>"
    ),
    zombie_bar_label="NEKROSE",
    zombie_phase_label="ZOMBIE-PHASE",
    zombie_badges_line="<code>ZOMBIE</code>  <code>CHAOTISCHE AUSBREITUNG</code>",
    zombie_timer_strip=(
        "🟪🟪🟪🟪🟪🟪🟪🟪🟪 <b>NEKROSE</b>\n"
        "⏱ <b>Krisen-Timer aus</b> · Zombie-Phase"
    ),
    timer_countdown="Bis zur Krise",
    timer_reserve="<i>Fenster bis zur Krise: <b>{pct}%</b></i>",
    timer_zone_title="COUNTDOWN",
    timer_extend_sources=(
        "<b>Woher die Zeit kommt</b>\n"
        "• Neuer Spieler über deinen Link — <b>+{bonus_hours:g} h</b>\n"
        "• Labor im <b>🔬 Terminal</b> — bis <b>+8 h</b> pro Tag\n"
        "• Brunnen des Lebens dort — <b>+12 h</b> für Event-Teilnehmer"
    ),
    own_invite_card_title="Verbreitungscode · aktiv",
    btn_refresh_remain="Verbleibende Zeit",
    btn_pick_contacts="🧬 Meine Kontakte",
    hint_after_contacts_shared=(
        "Wenn du gerade die Inline-Karte über die Schaltfläche unter der Nachricht eingefügt hast, hat der Kontakt die Einladung schon.\n\n"
        "Sonst leite deine Link-Nachricht weiter oder füge den Link manuell ein."
    ),
    invite_bottom_keyboard_prompt=(
        "Alt: <b>«☣️ Stamm übertragen»</b> unter der Nachricht — Inline, Chat wählen und Karte einfügen."
    ),
    spread_contact_send_failed=(
        "Karte konnte nicht zugestellt werden — Bot blockiert oder DMs von Fremden deaktiviert."
    ),
    spread_contact_sent_ok="Karte an den gewählten Kontakt im Bot-Chat gesendet.",
    spread_join_chain_button="☣️ In die Infektionskette eintreten",
    share_native_prefill="Ich stehe schon in der Kette. Öffnen — sieh, ob du als Nächstes dran bist.",
    mock_header_new="☣️ STAMM X-77 · INFIZIERT",
    mock_header_return="🧫 STATUS · STAMM AKTIV",
    mock_header_status="🧫 STATUS · STAMM AKTIV",
    mock_header_invite="🧬 VERBREITUNGSCODE · AKTIV",
    mock_body_new_organic=(
        "Glückwunsch — du hast dir etwas eingefangen, wogegen es keinen Impfstoff gibt.\n\n"
        "Du hast <b>{timer_hours_phrase}</b>, bevor der Zerfall beginnt.\n"
        "Der einzige Weg zu überleben: den <b>Stamm so schnell wie möglich verbreiten</b>.\n\n"
        "<i>Registerhinweis: Quelle als <b>nicht verifizierbar</b> markiert — als hätte jemand die Spur gekappt.</i>"
    ),
    mock_body_new_referral=(
        "Du bist über einen fremden Link reingekommen — du bist in <b>deren</b> Netzwerk.\n"
        "Die Krisenuhr läuft schon. Spiel voraus — oder steig aus."
    ),
    mock_body_return=(
        "Der Stamm breitet sich aus. Deine Kette hat <b>{network}</b> erreicht.\n"
        "Nicht schlecht — aber das Virus schläft nie. Der Timer auch nicht."
    ),
    mock_badges_new=(
        "<code>INFIZIERT</code>  <code>KETTE #1</code>  <code>RANG: WIRT</code>"
    ),
    mock_badges_active="<i>☣️ INFIZIERT · NETZ AKTIV · WIRT</i>",
    invite_link_box_label="▸ PERSÖNLICHER STAMM-LINK",
    mock_vita_label="RESERVE",
    mock_decay_label="BIS ZUM ZERFALL",
    mock_stat_ab_direct="direkt (dein Link)",
    mock_stat_ab_net="im Ast unter dir",
    mock_stat_ab_sector="Weltrang (alle Spieler)",
    mock_header_immune="🛡 IMMUNITÄT · ERHOLUNG",
    mock_body_immune=(
        "<b>Schutzprotokoll</b> nach der Degradation aktiv. "
        "Der Krisen-Timer pausiert bis Fensterende — danach läuft die Sim mit neuer Frist weiter."
    ),
    mock_immune_vita_label="SCHILD",
    mock_immune_decay_label="FENSTER",
    timer_immune_line="🛡 Immunität: <code>{time_str}</code>",
    status_title="Status",
    btn_terminal="🔬 Terminal",
    btn_live_timer="⏱ Timer",
    btn_world="🌍 Welt",
    btn_mutations="🧬 Mutationen",
    btn_top="🏆 Top",
    btn_immunity="🛡 Immunität",
    stub_feature_soon="Dieser Bereich ist noch in Arbeit — schau später wieder vorbei.",
    btn_back="↩ Zurück",
    back_to_main_ack="Hauptmenü.",
    status_use_start="Bitte zuerst /start im Bot senden.",
    referral_new_carrier=(
        "Noch einer.\n\n"
        "{newcomer} hat deinen Link geöffnet und\n"
        "ist jetzt infiziert. Deine Kette wächst.\n\n"
        "{bonus_block}"
        "Wirte in deinem Ast insgesamt: <b>{branch_total}</b>"
    ),
    referral_timer_bonus="<b>{bonus_hms}</b> auf deinen Timer.\n\n",
    menu_open_mini_hint=(
        "Tippe unten im Bot-Chat auf <b>🔬 Terminal</b> — Timer, Labor und Brunnen.\n\n"
        "<i>Manchmal passen Zeilen dort nicht zum öffentlichen Brief — Absicht in der Sim.</i>"
    ),
    sweep_warn_10m="<b>Weniger als 10 Minuten</b> bis zur Krise. Link teilen.",
    sweep_warn_30m="<b>Weniger als 30 Minuten</b> bis zur Krise.",
    sweep_warn_2h="<b>Weniger als 2 Stunden</b> bis zur Krise.",
    sweep_warn_1h="<b>Weniger als 1 Stunde</b> bis zur Krise. Link teilen.",
    immune_activated_notice=(
        "<b>🛡 Immunität aktiviert</b>\n\n"
        "Restzeit in der Mini App (Button Immunität) oder /start zum Aktualisieren."
    ),
    sweep_immune_ended=(
        "<b>Immunitätsfenster zu</b>\n\n"
        "Krisen-Timer läuft wieder — teile deinen Link, um nicht erneut Zombie zu werden."
    ),
    lab_ready_push=(
        "🧪 <b>ANALYSE ABGESCHLOSSEN</b>\n\n"
        "Probe verarbeitet. Öffne das <b>Labor</b> und hole dein Ergebnis ab.\n\n"
        "<i>Im Log-Ende: ein Fragment ohne Dekodierung — blockiert die Abholung nicht.</i>"
    ),
    lab_revived_push=(
        "⚡ <b>AUFERSTEHUNG</b>\n\n"
        "Das Labor hat gewirkt. Du bist wieder <b>Infiziert</b>.\n"
        "Neue Deadline: <b>+{timer_hours:g} h</b> — verbreite den Stamm."
    ),
    affliction_type_necrosis_bloom="Nekroseblüte",
    affliction_type_signal_spoof="Signalspoofing",
    affliction_type_enzyme_leak="Enzymleck",
    affliction_type_latency_fog="Latenznebel",
    affliction_spawn_push_pool=(
        "📡 <b>Stammbriefing</b>\n\nNeuer Ausfall in {strain}: <b>{type}</b> ({sev}).\n"
        "Das Labor braucht Hilfe: Öffne «🧪 Labor» und schließe Zyklen ab, um ein Heilmittel zu finden.",
    ),
    affliction_cured_push_pool=(
        "✅ <b>Geheilt</b>\n\n{strain}: <b>{type}</b> wurde neutralisiert.\n"
        "Labor hat geliefert. Tempo halten.",
    ),
    admin_forbidden="Zugriff verweigert.",
    admin_panel_intro="<b>Admin-Panel</b>\n\nAktion wählen — jede Schaltfläche in einer eigenen Zeile.",
    admin_btn_main_menu="↩ Spieler-Menü",
    admin_btn_me_energy="⚡ Ich: volle Clicker-Energie",
    admin_btn_me_reagents="🧬 Ich: +500 DNA · +500 RNA · +50 CAT",
    admin_btn_me_timer="⏱ Ich: +24 h zum Krisen-Timer",
    admin_me_need_register="Kein Profil — zuerst /start.",
    admin_me_energy_ok="<b>Energie</b>: <code>{e}</code> / <code>{m}</code>",
    admin_me_reagents_ok="<b>Reagenzien</b>: DNA <code>{d}</code> · RNA <code>{r}</code> · CAT <code>{c}</code>",
    admin_me_timer_ok="<b>Timer</b>: +<code>{h:g}</code> h bis Deadline.",
    admin_me_timer_skip="Timer unverändert: braucht <b>infected</b> mit aktiver Deadline.",
    boost_card_header="🧬 <b>VERSTÄRKTER LINK</b>",
    boost_card_bonus="Bonus für neuen Wirt: <b>+{bonus_pct}%</b> Timerzeit.",
    boost_card_expires="Gültig bis: <code>{expires}</code>",
    boost_card_uses="Nutzungen: <b>{uses}</b>",
    boost_card_url_hint="Link für einen neuen Wirt:",
    boost_btn_copy="📋 Link kopieren",
    boost_btn_owner_share="VERSTÄRKTE INFEKTION",
    boost_btn_spread="☣️ In die Kette eintreten",
    boost_inline_title="🧬 Verstärkte Einladung",
    boost_inline_description="Verstärkten Stamm an einen Kontakt senden.",
    boost_share_invite_body_html=(
        "<b>{sender}</b> übergibt dir den verstärkten Stamm.\n\n"
        "Die Simulation wartet auf einen neuen Wirt.\n"
        "Öffne die Einladung und tritt der Kette bei."
    ),
)

ES = Msg(
    btn_spread="☣️ Propagar cepa",
    btn_status="📊 Estado",
    btn_admin="⚙️ Admin",
    welcome_title="Brote registrado",
    welcome_subtitle_organic=(
        "Eres el <b>caso índice</b> de tu cadena. Encuentra huéspedes antes de que sea tarde.\n\n"
        "<i>El briefing público no cita el origen. Solo queda la cuenta atrás.</i>"
    ),
    welcome_subtitle_referral=(
        "Entraste con el enlace de otra persona — estás en <b>su</b> red. "
        "<i>Quién te enrutó aquí — sin declarar.</i>"
    ),
    welcome_timer="Tiempo hasta la crisis",
    welcome_link_hint="Tu enlace personal",
    welcome_no_bot_username=(
        "Ponle username al bot en @BotFather — sin eso no hay enlace de referidos."
    ),
    already_in_game_reinfect=(
        "Ya estás en la simulación. No puedes volver a entrar por otro enlace — "
        "comparte solo <b>tu</b> enlace (botón abajo)."
    ),
    welcome_back_title="El foco vuelve a estar activo.",
    stats_direct="Impactos directos",
    stats_network="Bajo ti en la cadena",
    stats_country="Tu sector",
    stats_banner="INFORME DEL FOCO",
    share_title=(
        "Paquete biológico listo.\n"
        "Pulsa <b>«🧬 Mis contactos»</b> abajo — <b>el bot le enviará una tarjeta</b> en Telegram (solo enlace al bot, <code>t.me/…</code>).\n\n"
        "Puede copiar el enlace de la tarjeta tocando la línea.\n\n"
        "Cada apertura de tu enlace — <b>+{bonus_hours:g} h</b> para ti.\n"
        "Cada plazo incumplido — un superviviente menos."
    ),
    invite_share_bonus_for_inviter_line="Cada apertura de este enlace suma <b>+{bonus_hours:g} h</b> al temporizador del remitente.",
    share_no_username="El bot no tiene username — configúralo en @BotFather.",
    spread_open_failed="No se pudo abrir la pantalla de propagación. Envía <code>/start</code> otra vez.",
    timer_inactive="Temporizador inactivo.",
    timer_zombie="💀 <b>DEGRADACIÓN COMPLETA · ZOMBI</b>\n\nEstado: <b>zombi</b>. Tarjeta completa: <code>/start</code>.",
    timer_expired_pending="Fallo raro de datos. Prueba <code>/start</code> o espera un minuto.",
    timer_zombie_transition_pending=(
        "<b>🧪 EVALUACIÓN</b> · conversión a zombi\n\n"
        "El plazo de crisis acabó: fijamos la fase de degradación. Tu estado <b>zombi</b> suele aparecer en el chat en "
        "<b>~1 minuto</b> (la sim se sincroniza cada minuto).\n\n"
        "Reenvía <code>/start</code> o espera el siguiente mensaje."
    ),
    zombie_screen06_banner="💀 SCREEN 06 · CONVERSIÓN ZOMBI",
    zombie_card_header="DEGRADACIÓN COMPLETA · ZOMBI",
    zombie_card_body=(
        "Se acabó el tiempo.\n\n"
        "Ya no estás en el estado anterior — eres <b>zombi</b>. "
        "La cepa actúa con caos — <i>o con un guion que no nos muestran</i>.\n\n"
        "En tu rama bajo ti siguen <b>{chain_total}</b> huéspedes.\n\n"
        "<b>El juego no terminó.</b>"
    ),
    zombie_card_hint=(
        "Tres caminos para salir del modo zombi:\n"
        "— <b>🧪 Lab</b> — 3 ciclos seguidos sin omitir → resurrección (+48 h)\n"
        "— <b>🌊 Fuente</b> — participa en el evento global → posibilidad de revivir\n"
        "— <b>🛡 Inmunidad</b> — protocolo único vía <b>🔬 Terminal</b>"
    ),
    zombie_bar_label="NECROSIS",
    zombie_phase_label="FASE ZOMBI",
    zombie_badges_line="<code>ZOMBI</code>  <code>PROPAGACIÓN CAÓTICA</code>",
    zombie_timer_strip=(
        "🟪🟪🟪🟪🟪🟪🟪🟪🟪 <b>NECROSIS</b>\n"
        "⏱ <b>temporizador de crisis apagado</b> · fase zombi"
    ),
    timer_countdown="Hasta la crisis",
    timer_reserve="<i>Ventana hasta la crisis: <b>{pct}%</b></i>",
    timer_zone_title="CUENTA ATRÁS",
    timer_extend_sources=(
        "<b>Qué alarga el tiempo</b>\n"
        "• Un jugador nuevo con tu enlace — <b>+{bonus_hours:g} h</b>\n"
        "• Laboratorio en el <b>🔬 Terminal</b> — hasta <b>+8 h</b> al día\n"
        "• Fuente de vida ahí — <b>+12 h</b> para quienes participen en el evento"
    ),
    own_invite_card_title="Código de propagación · activo",
    btn_refresh_remain="Cuánto queda",
    btn_pick_contacts="🧬 Mis contactos",
    hint_after_contacts_shared=(
        "Si acabas de insertar la tarjeta inline con el botón bajo el mensaje, ya recibieron la invitación.\n\n"
        "Si no, reenvía tu mensaje con el enlace o pégalo manualmente."
    ),
    invite_bottom_keyboard_prompt=(
        "Antiguo: pulsa <b>«☣️ Propagar cepa»</b> bajo el mensaje — inline, elige chat e inserta la tarjeta."
    ),
    spread_contact_send_failed=(
        "No se pudo entregar la tarjeta — quizá bloqueó el bot o restringió MD de desconocidos."
    ),
    spread_contact_sent_ok="Tarjeta enviada al contacto elegido en su chat con el bot.",
    spread_join_chain_button="☣️ Entrar en la cadena de infección",
    share_native_prefill="Ya me metieron en la cadena. Ábrelo — mira si tú eres el siguiente.",
    mock_header_new="☣️ CEPA X-77 · INFECTADO",
    mock_header_return="🧫 ESTADO · CEPA ACTIVA",
    mock_header_status="🧫 ESTADO · CEPA ACTIVA",
    mock_header_invite="🧬 CÓDIGO DE PROPAGACIÓN · ACTIVO",
    mock_body_new_organic=(
        "Felicidades — acabas de pillar algo para lo que no hay vacuna.\n\n"
        "Tienes <b>{timer_hours_phrase}</b> antes de que empiece la degradación.\n"
        "La única forma de sobrevivir es <b>propagar la cepa</b> lo más rápido posible.\n\n"
        "<i>Nota en el registro: fuente marcada como <b>no verificable</b> — como si cortaran el rastro.</i>"
    ),
    mock_body_new_referral=(
        "Entraste por enlace ajeno — estás en <b>su</b> red.\n"
        "El reloj de crisis ya corre. Juega con ventaja — o retírate."
    ),
    mock_body_return=(
        "La cepa se propaga. Tu cadena ha alcanzado <b>{network}</b>.\n"
        "No está mal — pero el virus no duerme. El temporizador tampoco."
    ),
    mock_badges_new=(
        "<code>INFECTADO</code>  <code>CADENA #1</code>  <code>RANGO: HUÉSPED</code>"
    ),
    mock_badges_active="<i>☣️ INFECTADO · RED ACTIVA · HUÉSPED</i>",
    invite_link_box_label="▸ ENLACE PERSONAL DE CEPA",
    mock_vita_label="RESERVA",
    mock_decay_label="HASTA EL DECAIMIENTO",
    mock_stat_ab_direct="directos (tu enlace)",
    mock_stat_ab_net="en tu rama",
    mock_stat_ab_sector="Ranking mundial",
    mock_header_immune="🛡 INMUNIDAD · RECUPERACIÓN",
    mock_body_immune=(
        "<b>Protocolo protector</b> tras la degradación. "
        "El temporizador de crisis está en pausa hasta que cierre la ventana — luego la sim sigue con un plazo nuevo."
    ),
    mock_immune_vita_label="ESCUDO",
    mock_immune_decay_label="VENTANA",
    timer_immune_line="🛡 Inmunidad: <code>{time_str}</code>",
    status_title="Estado",
    btn_terminal="🔬 Terminal",
    btn_live_timer="⏱ Temporizador",
    btn_world="🌍 Mundo",
    btn_mutations="🧬 Mutaciones",
    btn_top="🏆 Top",
    btn_immunity="🛡 Inmunidad",
    stub_feature_soon="Esta sección aún está en desarrollo — vuelve más tarde.",
    btn_back="↩ Atrás",
    back_to_main_ack="Menú principal.",
    status_use_start="Primero abre /start en el bot.",
    referral_new_carrier=(
        "Uno más.\n\n"
        "{newcomer} abrió tu enlace y\n"
        "ya está infectado. Tu cadena crece.\n\n"
        "{bonus_block}"
        "Huéspedes en tu rama en total: <b>{branch_total}</b>"
    ),
    referral_timer_bonus="<b>{bonus_hms}</b> a tu temporizador.\n\n",
    menu_open_mini_hint=(
        "Pulsa <b>🔬 Terminal</b> abajo en el chat del bot: temporizador, lab y fuente.\n\n"
        "<i>A veces las líneas no coinciden con el briefing público — va en la sim.</i>"
    ),
    sweep_warn_10m="Quedan <b>menos de 10 minutos</b> para la crisis. Comparte tu enlace.",
    sweep_warn_30m="Quedan <b>menos de 30 minutos</b> para la crisis.",
    sweep_warn_2h="Quedan <b>menos de 2 horas</b> para la crisis.",
    sweep_warn_1h="Queda <b>menos de una hora</b> para la crisis. Comparte tu enlace.",
    immune_activated_notice=(
        "<b>🛡 Inmunidad activada</b>\n\n"
        "Tiempo restante en la Mini App (botón Inmunidad) o actualiza con /start."
    ),
    sweep_immune_ended=(
        "<b>Ventana de inmunidad cerrada</b>\n\n"
        "El temporizador de crisis vuelve a correr — comparte tu enlace para no volver a zombi."
    ),
    lab_ready_push=(
        "🧪 <b>ANÁLISIS COMPLETO</b>\n\n"
        "Muestra procesada. Abre el <b>Laboratorio</b> y reclama tu resultado.\n\n"
        "<i>Cola de registro: fragmento sin decodificar — no bloquea la recogida.</i>"
    ),
    lab_revived_push=(
        "⚡ <b>RESURRECCIÓN</b>\n\n"
        "El Laboratorio funcionó. Estás <b>Infectado</b> de nuevo.\n"
        "Nueva fecha límite: <b>+{timer_hours:g} h</b> — propaga la cepa."
    ),
    affliction_type_necrosis_bloom="floración de necrosis",
    affliction_type_signal_spoof="suplantación de señal",
    affliction_type_enzyme_leak="fuga de enzima",
    affliction_type_latency_fog="niebla de latencia",
    affliction_spawn_push_pool=(
        "📡 <b>Parte de la cepa</b>\n\nNuevo fallo detectado en {strain}: <b>{type}</b> ({sev}).\n"
        "El laboratorio necesita ayuda: abre «🧪 Laboratorio» y completa ciclos para encontrar una cura.",
    ),
    affliction_cured_push_pool=(
        "✅ <b>Curado</b>\n\n{strain}: <b>{type}</b> ha sido neutralizado.\n"
        "El laboratorio cumplió. Mantén el ritmo.",
    ),
    admin_forbidden="Acceso denegado.",
    admin_panel_intro="<b>Panel admin</b>\n\nElige una acción — un botón por fila.",
    admin_btn_main_menu="↩ Menú jugador",
    admin_btn_me_energy="⚡ Yo: energía clicker llena",
    admin_btn_me_reagents="🧬 Yo: +500 DNA · +500 RNA · +50 CAT",
    admin_btn_me_timer="⏱ Yo: +24 h al temporizador",
    admin_me_need_register="Sin perfil — abre /start primero.",
    admin_me_energy_ok="<b>Energía</b>: <code>{e}</code> / <code>{m}</code>",
    admin_me_reagents_ok="<b>Reactivos</b>: DNA <code>{d}</code> · RNA <code>{r}</code> · CAT <code>{c}</code>",
    admin_me_timer_ok="<b>Temporizador</b>: +<code>{h:g}</code> h al plazo.",
    admin_me_timer_skip="Sin cambios: necesitas <b>infected</b> con plazo activo.",
    boost_card_header="🧬 <b>ENLACE POTENCIADO</b>",
    boost_card_bonus="Bono por nuevo huésped: <b>+{bonus_pct}%</b> al temporizador.",
    boost_card_expires="Válido hasta: <code>{expires}</code>",
    boost_card_uses="Usos: <b>{uses}</b>",
    boost_card_url_hint="Enlace para un nuevo huésped:",
    boost_btn_copy="📋 Copiar enlace",
    boost_btn_owner_share="INFECCIÓN POTENCIADA",
    boost_btn_spread="☣️ Entrar en la cadena",
    boost_inline_title="🧬 Invitación potenciada",
    boost_inline_description="Envía la cepa potenciada a un contacto.",
    boost_share_invite_body_html=(
        "<b>{sender}</b> te transmite la cepa potenciada.\n\n"
        "La simulación espera un nuevo huésped.\n"
        "Abre la invitación y entra en la cadena."
    ),
)

PT = Msg(
    btn_spread="☣️ Espalhar cepa",
    btn_status="📊 Status",
    btn_admin="⚙️ Admin",
    welcome_title="Surto registrado",
    welcome_subtitle_organic=(
        "Você é o <b>caso índice</b> da sua cadeia. Encontre hospedeiros antes que seja tarde.\n\n"
        "<i>O briefing público não cita a origem. Só há a contagem regressiva.</i>"
    ),
    welcome_subtitle_referral=(
        "Você entrou pelo link de outra pessoa — está na <b>rede dela</b>. "
        "<i>Quem te encaminhou — não declarado.</i>"
    ),
    welcome_timer="Tempo até a crise",
    welcome_link_hint="Seu link pessoal",
    welcome_no_bot_username=(
        "Defina um username para o bot no @BotFather — sem isso não há link de indicação."
    ),
    already_in_game_reinfect=(
        "Você já está na simulação. Não dá para entrar de novo por outro link — "
        "compartilhe só o <b>seu</b> link (botão abaixo)."
    ),
    welcome_back_title="O foco volta ao ar.",
    stats_direct="Acertos diretos",
    stats_network="Abaixo de você na cadeia",
    stats_country="Seu setor",
    stats_banner="RESUMO DO SURTO",
    share_title=(
        "Pacote biológico pronto.\n"
        "Toque em <b>«🧬 Meus contatos»</b> abaixo — <b>o bot enviará um cartão</b> no Telegram (apenas link do bot, <code>t.me/…</code>).\n\n"
        "Dá para copiar o link do cartão tocando na linha.\n\n"
        "Cada abertura do seu link — <b>+{bonus_hours:g} h</b> para você.\n"
        "Cada prazo perdido — um sobrevivente a menos."
    ),
    invite_share_bonus_for_inviter_line="Cada abertura deste link adiciona <b>+{bonus_hours:g} h</b> ao timer do remetente.",
    share_no_username="O bot não tem username — configure no @BotFather.",
    spread_open_failed="Não foi possível abrir a tela de propagação. Envie <code>/start</code> de novo.",
    timer_inactive="Timer inativo.",
    timer_zombie="💀 <b>DEGRADAÇÃO COMPLETA · ZUMBI</b>\n\nEstado: <b>zumbi</b>. Cartão completo: <code>/start</code>.",
    timer_expired_pending="Falha rara de dados. Tente <code>/start</code> ou espere 1 minuto.",
    timer_zombie_transition_pending=(
        "<b>🧪 AVALIAÇÃO</b> · virando zumbi\n\n"
        "Prazo de crise esgotado: fixamos a fase de degradação. O status <b>zumbi</b> costuma aparecer no chat em "
        "<b>~1 minuto</b> (a sim sincroniza a cada minuto).\n\n"
        "Envie <code>/start</code> de novo ou aguarde a próxima mensagem."
    ),
    zombie_screen06_banner="💀 SCREEN 06 · TRANSFORMAÇÃO ZUMBI",
    zombie_card_header="DEGRADAÇÃO COMPLETA · ZUMBI",
    zombie_card_body=(
        "O tempo acabou.\n\n"
        "Você não está mais no estado anterior — é <b>zumbi</b>. "
        "A cepa age de forma caótica — <i>ou segue um roteiro que não vemos</i>.\n\n"
        "No seu ramo abaixo de você ainda há <b>{chain_total}</b> hospedeiros.\n\n"
        "<b>O jogo não acabou.</b>"
    ),
    zombie_card_hint=(
        "Três caminhos para sair do modo zumbi:\n"
        "— <b>🧪 Lab</b> — 3 ciclos seguidos sem pular → ressurreição (+48 h)\n"
        "— <b>🌊 Fonte</b> — participe do evento global → chance de reviver\n"
        "— <b>🛡 Imunidade</b> — protocolo único via <b>🔬 Terminal</b>"
    ),
    zombie_bar_label="NECROSE",
    zombie_phase_label="FASE ZUMBI",
    zombie_badges_line="<code>ZUMBI</code>  <code>PROPAGAÇÃO CAÓTICA</code>",
    zombie_timer_strip=(
        "🟪🟪🟪🟪🟪🟪🟪🟪🟪 <b>NECROSE</b>\n"
        "⏱ <b>timer de crise desligado</b> · fase zumbi"
    ),
    timer_countdown="Até a crise",
    timer_reserve="<i>Janela até a crise: <b>{pct}%</b></i>",
    timer_zone_title="CONTAGEM REGRESSIVA",
    timer_extend_sources=(
        "<b>O que aumenta o tempo</b>\n"
        "• Novo jogador pelo seu link — <b>+{bonus_hours:g} h</b>\n"
        "• Laboratório no <b>🔬 Terminal</b> — até <b>+8 h</b> por dia\n"
        "• Fonte da vida lá — <b>+12 h</b> para quem participar do evento"
    ),
    own_invite_card_title="Código de propagação · ativo",
    btn_refresh_remain="Quanto falta",
    btn_pick_contacts="🧬 Meus contatos",
    hint_after_contacts_shared=(
        "Se você acabou de inserir o cartão inline pelo botão abaixo da mensagem, a pessoa já recebeu o convite.\n\n"
        "Caso contrário, encaminhe sua mensagem com o link ou cole manualmente."
    ),
    invite_bottom_keyboard_prompt=(
        "Legado: toque em <b>«☣️ Espalhar cepa»</b> abaixo da mensagem — inline, escolha o chat e insira o cartão."
    ),
    spread_contact_send_failed=(
        "Não foi possível entregar o cartão — talvez o bot esteja bloqueado ou DMs de estranhos desativadas."
    ),
    spread_contact_sent_ok="Cartão enviado ao contato escolhido no chat com o bot.",
    spread_join_chain_button="☣️ Entrar na cadeia de infecção",
    share_native_prefill="Já me colocaram na cadeia. Abre — vê se você é o próximo.",
    mock_header_new="☣️ CEPA X-77 · INFECTADO",
    mock_header_return="🧫 STATUS · CEPA ATIVA",
    mock_header_status="🧫 STATUS · CEPA ATIVA",
    mock_header_invite="🧬 CÓDIGO DE PROPAGAÇÃO · ATIVO",
    mock_body_new_organic=(
        "Parabéns — você acabou de pegar algo sem vacina.\n\n"
        "Você tem <b>{timer_hours_phrase}</b> antes da degradação começar.\n"
        "A única forma de sobreviver é <b>espalhar a cepa</b> o mais rápido possível.\n\n"
        "<i>Nota no registro: fonte marcada como <b>inverificável</b> — como se cortassem o rastro.</i>"
    ),
    mock_body_new_referral=(
        "Você entrou por link alheio — está na <b>rede dele(a)</b>.\n"
        "O relógio da crise já corre. Jogue na frente — ou saia."
    ),
    mock_body_return=(
        "A cepa se espalha. Sua cadeia alcançou <b>{network}</b>.\n"
        "Nada mal — mas o vírus não dorme. O timer também não."
    ),
    mock_badges_new=(
        "<code>INFECTADO</code>  <code>CADEIA #1</code>  <code>RANK: HOSPEDEIRO</code>"
    ),
    mock_badges_active="<i>☣️ INFECTADO · REDE ATIVA · HOSPEDEIRO</i>",
    invite_link_box_label="▸ LINK PESSOAL DA CEPA",
    mock_vita_label="RESERVA",
    mock_decay_label="ATÉ A DEGRADAÇÃO",
    mock_stat_ab_direct="diretos (seu link)",
    mock_stat_ab_net="no seu ramo",
    mock_stat_ab_sector="Ranking mundial",
    mock_header_immune="🛡 IMUNIDADE · RECUPERAÇÃO",
    mock_body_immune=(
        "<b>Protocolo de proteção</b> após a degradação. "
        "O timer de crise fica em pausa até o fim da janela — depois a sim continua com novo prazo."
    ),
    mock_immune_vita_label="ESCUDO",
    mock_immune_decay_label="JANELA",
    timer_immune_line="🛡 Imunidade: <code>{time_str}</code>",
    status_title="Status",
    btn_terminal="🔬 Terminal",
    btn_live_timer="⏱ Timer",
    btn_world="🌍 Mundo",
    btn_mutations="🧬 Mutações",
    btn_top="🏆 Top",
    btn_immunity="🛡 Imunidade",
    stub_feature_soon="Esta seção ainda está em desenvolvimento — volte mais tarde.",
    btn_back="↩ Voltar",
    back_to_main_ack="Menu principal.",
    status_use_start="Abra /start no bot primeiro.",
    referral_new_carrier=(
        "Mais um.\n\n"
        "{newcomer} abriu seu link e\n"
        "já está infectado. Sua cadeia cresce.\n\n"
        "{bonus_block}"
        "Total de hospedeiros no seu ramo: <b>{branch_total}</b>"
    ),
    referral_timer_bonus="<b>{bonus_hms}</b> no seu timer.\n\n",
    menu_open_mini_hint=(
        "Toque em <b>🔬 Terminal</b> no rodapé do chat do bot — timer, lab e fonte.\n\n"
        "<i>Às vezes o que aparece ali não bate com o briefing público — faz parte da sim.</i>"
    ),
    sweep_warn_10m="Faltam <b>menos de 10 minutos</b> para a crise. Envie seu link.",
    sweep_warn_30m="Faltam <b>menos de 30 minutos</b> para a crise.",
    sweep_warn_2h="Faltam <b>menos de 2 horas</b> para a crise.",
    sweep_warn_1h="Falta <b>menos de 1 hora</b> para a crise. Envie seu link.",
    immune_activated_notice=(
        "<b>🛡 Imunidade ativada</b>\n\n"
        "Veja o tempo restante na Mini App (botão Imunidade) ou atualize com /start."
    ),
    sweep_immune_ended=(
        "<b>Janela de imunidade encerrada</b>\n\n"
        "O timer de crise voltou — envie seu link para não cair de novo em zumbi."
    ),
    lab_ready_push=(
        "🧪 <b>ANÁLISE CONCLUÍDA</b>\n\n"
        "Amostra processada. Abra o <b>Laboratório</b> e resgate o resultado.\n\n"
        "<i>Cauda do log mostra um fragmento sem decifrar — não impede a retirada.</i>"
    ),
    lab_revived_push=(
        "⚡ <b>RESSURREIÇÃO</b>\n\n"
        "O Laboratório funcionou. Você está <b>Infectado</b> novamente.\n"
        "Novo prazo: <b>+{timer_hours:g} h</b> — espalhe a cepa."
    ),
    affliction_type_necrosis_bloom="floração de necrose",
    affliction_type_signal_spoof="falsificação de sinal",
    affliction_type_enzyme_leak="vazamento de enzima",
    affliction_type_latency_fog="névoa de latência",
    affliction_spawn_push_pool=(
        "📡 <b>Boletim da cepa</b>\n\nNovo erro detectado em {strain}: <b>{type}</b> ({sev}).\n"
        "O laboratório precisa de ajuda: abra «🧪 Laboratório» e conclua ciclos para achar a cura.",
    ),
    affliction_cured_push_pool=(
        "✅ <b>Curado</b>\n\n{strain}: <b>{type}</b> foi neutralizado.\n"
        "O laboratório entregou. Mantenha o ritmo.",
    ),
    admin_forbidden="Acesso negado.",
    admin_panel_intro="<b>Painel admin</b>\n\nEscolha uma ação — um botão por linha.",
    admin_btn_main_menu="↩ Menu do jogador",
    admin_btn_me_energy="⚡ Eu: energia do clicker cheia",
    admin_btn_me_reagents="🧬 Eu: +500 DNA · +500 RNA · +50 CAT",
    admin_btn_me_timer="⏱ Eu: +24 h ao temporizador",
    admin_me_need_register="Sem perfil — abra /start primeiro.",
    admin_me_energy_ok="<b>Energia</b>: <code>{e}</code> / <code>{m}</code>",
    admin_me_reagents_ok="<b>Reagentes</b>: DNA <code>{d}</code> · RNA <code>{r}</code> · CAT <code>{c}</code>",
    admin_me_timer_ok="<b>Timer</b>: +<code>{h:g}</code> h ao prazo.",
    admin_me_timer_skip="Sem mudanças: precisa <b>infected</b> com prazo ativo.",
    boost_card_header="🧬 <b>LINK POTENCIALIZADO</b>",
    boost_card_bonus="Bônus para novo hospedeiro: <b>+{bonus_pct}%</b> no tempo do timer.",
    boost_card_expires="Válido até: <code>{expires}</code>",
    boost_card_uses="Usos: <b>{uses}</b>",
    boost_card_url_hint="Link para novo hospedeiro:",
    boost_btn_copy="📋 Copiar link",
    boost_btn_owner_share="INFECÇÃO POTENCIALIZADA",
    boost_btn_spread="☣️ Entrar na cadeia",
    boost_inline_title="🧬 Convite potencializado",
    boost_inline_description="Envie a cepa amplificada para um contato.",
    boost_share_invite_body_html=(
        "<b>{sender}</b> passa a cepa amplificada para você.\n\n"
        "A simulação aguarda um novo hospedeiro.\n"
        "Abra o convite e entre na cadeia."
    ),
)

KO = Msg(
    btn_spread="☣️ 균주 전파",
    btn_status="📊 상태",
    btn_admin="⚙️ 관리자",
    welcome_title="발생이 기록되었습니다",
    welcome_subtitle_organic=(
        "당신은 이 체인의 <b>최초 감염자</b>입니다. 늦기 전에 숙주를 찾으세요.\n\n"
        "<i>공개 브리핑에는 출처가 없습니다. 남은 것은 카운트다운뿐.</i>"
    ),
    welcome_subtitle_referral=(
        "다른 사람의 링크로 들어왔습니다 — <b>상대 네트워크</b>에 있습니다. "
        "<i>누가 여기로 연결했는지 — 명시되지 않았습니다.</i>"
    ),
    welcome_timer="위기까지 남은 시간",
    welcome_link_hint="개인 링크",
    welcome_no_bot_username="@BotFather에서 봇 username을 설정하세요. 없으면 추천 링크를 만들 수 없습니다.",
    already_in_game_reinfect=(
        "이미 시뮬레이션에 참가 중입니다. 다른 링크로 다시 들어올 수 없습니다 — "
        "아래 버튼으로 <b>본인의</b> 링크만 공유하세요."
    ),
    welcome_back_title="오염원이 다시 접속했습니다.",
    stats_direct="직접 타격",
    stats_network="체인에서 네 아래",
    stats_country="네 구역",
    stats_banner="오염원 브리핑",
    share_title=(
        "생물학적 페이로드 준비 완료.\n"
        "아래 <b>«🧬 내 연락처»</b>를 누르면 <b>봇이 상대에게 카드를 보냅니다</b>(봇 링크만, <code>t.me/…</code>).\n\n"
        "카드 안 링크는 줄을 눌러 복사할 수 있어요.\n\n"
        "링크를 연 사람마다 — 너에게 <b>+{bonus_hours:g}시간</b>.\n"
        "기한을 놓칠 때마다 — 생존자 하나 감소."
    ),
    invite_share_bonus_for_inviter_line="이 링크를 연 사람마다 발신자 타이머에 <b>+{bonus_hours:g}시간</b>.",
    share_no_username="봇에 username이 없습니다 — @BotFather에서 설정하세요.",
    spread_open_failed="전파 화면을 열 수 없습니다. <code>/start</code>를 다시 보내세요.",
    timer_inactive="타이머 비활성.",
    timer_zombie="💀 <b>분해 완료 · 좀비</b>\n\n상태: <b>좀비</b>. 전체 카드는 <code>/start</code>.",
    timer_expired_pending="드문 데이터 오류. <code>/start</code> 또는 1분 대기.",
    timer_zombie_transition_pending=(
        "<b>🧪 상태 평가</b> · 좀비 전환\n\n"
        "위기 데드라인이 지났습니다. 단계를 확정하는 중이며, <b>좀비</b> 상태는 보통 <b>약 1분 안에</b> "
        "채팅에 반영됩니다(분 단위 동기화).\n\n"
        "<code>/start</code>를 다시 보내거나 다음 메시지를 기다리세요."
    ),
    zombie_screen06_banner="💀 SCREEN 06 · 좀비 전환",
    zombie_card_header="분해 완료 · 좀비",
    zombie_card_body=(
        "시간이 끝났습니다.\n\n"
        "이전 상태가 아닙니다 — 당신은 <b>좀비</b>입니다. "
        "균주는 혼란스럽게 움직입니다 — <i>또는 우리가 읽을 수 없는 스크립트대로</i>.\n\n"
        "가지 아래에는 여전히 <b>{chain_total}</b>명의 숙주가 있습니다.\n\n"
        "<b>게임은 끝나지 않았습니다.</b>"
    ),
    zombie_card_hint=(
        "좀비 모드 탈출 3가지 방법:\n"
        "— <b>🧪 실험실</b> — 연속 3사이클 (하루도 빠짐없이) → 부활 (+48h)\n"
        "— <b>🌊 분수</b> — 글로벌 이벤트 참여 → 부활 기회\n"
        "— <b>🛡 면역</b> — <b>🔬 터미널</b>에서 1회 프로토콜"
    ),
    zombie_bar_label="괴사",
    zombie_phase_label="좀비 단계",
    zombie_badges_line="<code>좀비</code>  <code>혼돈 전파</code>",
    zombie_timer_strip=(
        "🟪🟪🟪🟪🟪🟪🟪🟪🟪 <b>괴사</b>\n"
        "⏱ <b>위기 타이머 꺼짐</b> · 좀비 단계"
    ),
    timer_countdown="위기까지",
    timer_reserve="<i>위기까지 남은 창: <b>{pct}%</b></i>",
    timer_zone_title="카운트다운",
    timer_extend_sources=(
        "<b>시간이 늘어나는 경우</b>\n"
        "• 내 링크로 새 플레이어 — <b>+{bonus_hours:g}시간</b>\n"
        "• <b>🔬 터미널</b>의 실험실 — 하루 최대 <b>+8시간</b>\n"
        "• 같은 곳의 분수 — 이벤트 참가자 <b>+12시간</b>"
    ),
    own_invite_card_title="전파 코드 · 활성",
    btn_refresh_remain="남은 시간",
    btn_pick_contacts="🧬 내 연락처",
    hint_after_contacts_shared=(
        "메시지 아래 버튼으로 인라인 카드를 방금 넣었다면 상대는 이미 초대를 받았습니다.\n\n"
        "아니면 링크 메시지를 전달하거나 링크를 직접 붙여 넣으세요."
    ),
    invite_bottom_keyboard_prompt=(
        "이전: 메시지 아래 <b>«☣️ 균주 전파»</b> — 인라인, 채팅 고르고 카드 삽입."
    ),
    spread_contact_send_failed=(
        "카드를 전달하지 못했습니다 — 봇 차단이나 DM 제한일 수 있습니다."
    ),
    spread_contact_sent_ok="선택한 연락처의 봇 채팅으로 카드를 보냈습니다.",
    spread_join_chain_button="☣️ 감염 체인 참여",
    share_native_prefill="나도 이미 체인에 붙었어. 열어봐 — 네가 다음인지 확인해.",
    mock_header_new="☣️ 균주 X-77 · 감염됨",
    mock_header_return="🧫 상태 · 균주 활성",
    mock_header_status="🧫 상태 · 균주 활성",
    mock_header_invite="🧬 전파 코드 · 활성",
    mock_body_new_organic=(
        "축하합니다 — 방금 백신 없는 것에 걸렸습니다.\n\n"
        "붕괴가 시작되기 전까지 <b>{timer_hours_phrase}</b>가 있습니다.\n"
        "살아남는 유일한 방법은 <b>균주를 최대한 빨리 퍼뜨리는 것</b>입니다.\n\n"
        "<i>등록 각주: 출처 <b>검증 불가</b>로 표기 — 누군가 흔적을 잘랐는 것 같습니다.</i>"
    ),
    mock_body_new_referral=(
        "남의 링크로 들어왔습니다 — <b>상대 네트워크</b>에 있습니다.\n"
        "위기 시계는 이미 돕니다. 앞서가거나 물러나세요."
    ),
    mock_body_return=(
        "균주가 퍼지고 있습니다. 네 체인은 <b>{network}</b>명에 닿았습니다.\n"
        "나쁘지 않지만 — 바이러스는 잠들지 않습니다. 타이머도 마찬가지입니다."
    ),
    mock_badges_new=(
        "<code>감염됨</code>  <code>체인 #1</code>  <code>등급: 숙주</code>"
    ),
    mock_badges_active="<i>☣️ 감염 · 네트워크 활성 · 숙주</i>",
    invite_link_box_label="▸ 개인 균주 링크",
    mock_vita_label="잔여",
    mock_decay_label="붕괴까지",
    mock_stat_ab_direct="직접 링크",
    mock_stat_ab_net="내 아래 네트워크",
    mock_stat_ab_sector="전체 순위",
    mock_header_immune="🛡 면역 · 회복",
    mock_body_immune=(
        "분해 이후 <b>보호 프로토콜</b>이 켜졌어요. "
        "창이 끝날 때까지 위기 타이머는 멈춤 — 이후 시뮬은 새 데드라인으로 이어져요."
    ),
    mock_immune_vita_label="실드",
    mock_immune_decay_label="창 종료까지",
    timer_immune_line="🛡 면역: <code>{time_str}</code>",
    status_title="상태",
    btn_terminal="🔬 터미널",
    btn_live_timer="⏱ 타이머",
    btn_world="🌍 세계",
    btn_mutations="🧬 돌연변이",
    btn_top="🏆 랭킹",
    btn_immunity="🛡 면역",
    stub_feature_soon="이 기능은 아직 준비 중이에요 — 나중에 다시 와 주세요.",
    btn_back="↩ 뒤로",
    back_to_main_ack="메인 메뉴.",
    status_use_start="먼저 봇에서 /start를 보내세요.",
    referral_new_carrier=(
        "또 한 명.\n\n"
        "{newcomer}님이 네 링크를 열었고\n"
        "이미 감염됐어. 체인이 길어지고 있어.\n\n"
        "{bonus_block}"
        "가지 숙주 합계: <b>{branch_total}</b>"
    ),
    referral_timer_bonus="타이머에 <b>{bonus_hms}</b>.\n\n",
    menu_open_mini_hint=(
        "봇 채팅 하단의 <b>🔬 터미널</b>을 누르세요 — 타이머·실험실·분수.\n\n"
        "<i>가끔 그곳의 줄은 공개 브리핑과 맞지 않습니다 — 그것도 시뮬의 일부입니다.</i>"
    ),
    sweep_warn_10m="위기까지 <b>10분 미만</b>입니다. 링크를 보내세요.",
    sweep_warn_30m="위기까지 <b>30분 미만</b>입니다.",
    sweep_warn_2h="위기까지 <b>2시간 미만</b>입니다.",
    sweep_warn_1h="위기까지 <b>1시간 미만</b>입니다. 링크를 보내세요.",
    immune_activated_notice=(
        "<b>🛡 면역 활성화</b>\n\n"
        "남은 시간은 Mini App(면역 버튼)에서 확인하거나 /start로 갱신하세요."
    ),
    sweep_immune_ended=(
        "<b>면역 창이 끝났습니다</b>\n\n"
        "위기 타이머가 다시 돌아갑니다 — 링크를 보내 좀비로 돌아가지 마세요."
    ),
    lab_ready_push=(
        "🧪 <b>분석 완료</b>\n\n"
        "샘플 처리됨. <b>실험실</b>을 열고 결과를 받으세요.\n\n"
        "<i>로그 끝에 해독되지 않은 조각이 보입니다 — 수령을 막지는 않습니다.</i>"
    ),
    lab_revived_push=(
        "⚡ <b>부활</b>\n\n"
        "실험실이 작동했습니다. 다시 <b>감염됨</b> 상태입니다.\n"
        "새 데드라인: <b>+{timer_hours:g}h</b> — 균주를 퍼뜨리세요."
    ),
    affliction_type_necrosis_bloom="괴사 개화",
    affliction_type_signal_spoof="신호 위장",
    affliction_type_enzyme_leak="효소 누출",
    affliction_type_latency_fog="지연 안개",
    affliction_spawn_push_pool=(
        "📡 <b>균주 브리핑</b>\n\n{strain}에서 새로운 이상: <b>{type}</b> ({sev}).\n"
        "실험실이 도움을 요청합니다. «🧪 실험실»에서 사이클을 완료해 치료제를 찾으세요.",
    ),
    affliction_cured_push_pool=(
        "✅ <b>치료 완료</b>\n\n{strain}: <b>{type}</b>이(가) 무력화되었습니다.\n"
        "실험실 성공. 페이스 유지.",
    ),
    admin_forbidden="권한이 없습니다.",
    admin_panel_intro="<b>관리자 패널</b>\n\n작업 선택 — 버튼은 한 줄에 하나.",
    admin_btn_main_menu="↩ 일반 메뉴",
    admin_btn_me_energy="⚡ 나: 클리커 에너지 가득",
    admin_btn_me_reagents="🧬 나: DNA +500 · RNA +500 · CAT +50",
    admin_btn_me_timer="⏱ 나: 타이머 +24시간",
    admin_me_need_register="프로필 없음 — 먼저 /start.",
    admin_me_energy_ok="<b>에너지</b>: <code>{e}</code> / <code>{m}</code>",
    admin_me_reagents_ok="<b>시약</b>: DNA <code>{d}</code> · RNA <code>{r}</code> · CAT <code>{c}</code>",
    admin_me_timer_ok="<b>타이머</b>: 데드라인 +<code>{h:g}</code>시간.",
    admin_me_timer_skip="변경 없음: <b>infected</b>와 활성 데드라인 필요.",
    boost_card_header="🧬 <b>강화 링크</b>",
    boost_card_bonus="신규 숙주 보너스: 타이머 <b>+{bonus_pct}%</b>.",
    boost_card_expires="유효 기한: <code>{expires}</code>",
    boost_card_uses="사용 횟수: <b>{uses}</b>",
    boost_card_url_hint="신규 숙주용 링크:",
    boost_btn_copy="📋 링크 복사",
    boost_btn_owner_share="강화 감염",
    boost_btn_spread="☣️ 체인 참여",
    boost_inline_title="🧬 강화 초대",
    boost_inline_description="강화 스트레인을 연락처에 보냅니다.",
    boost_share_invite_body_html=(
        "<b>{sender}</b>가 강화 스트레인을 전달합니다.\n\n"
        "시뮬레이션이 새 숙주를 기다립니다.\n"
        "초대를 열고 체인에 참여하세요."
    ),
)

JA = Msg(
    btn_spread="☣️ 株を伝播",
    btn_status="📊 ステータス",
    btn_admin="⚙️ 管理",
    welcome_title="発生を記録しました",
    welcome_subtitle_organic=(
        "あなたはこの連鎖の<b>インデックスケース</b>です。手遅れになる前に宿主を見つけてください。\n\n"
        "<i>公開ブリーフは出典を名指ししない。あるのはカウントダウンだけ。</i>"
    ),
    welcome_subtitle_referral=(
        "他人のリンクから参加しました — <b>相手のネットワーク</b>にいます。 "
        "<i>誰がここへルーティングしたか — 未記載。</i>"
    ),
    welcome_timer="危機までの時間",
    welcome_link_hint="あなた専用のリンク",
    welcome_no_bot_username="@BotFather でボットに username を設定してください。ないと紹介リンクを作れません。",
    already_in_game_reinfect=(
        "すでにシミュレーションに参加中です。別のリンクから再参加はできません — "
        "下のボタンから<b>自分の</b>リンクだけ共有してください。"
    ),
    welcome_back_title="感染源、再び接続。",
    stats_direct="直撃感染",
    stats_network="チェーン上の下流",
    stats_country="あなたのセクター",
    stats_banner="感染源ブリーフ",
    share_title=(
        "生物パケット準備完了。\n"
        "下の <b>「🧬 マイ連絡先」</b> で相手を選べ — <b>ボットがカードを送る</b>（ボットへのリンクのみ、<code>t.me/…</code>）。\n\n"
        "カード内のリンクは行をタップでコピーできる。\n\n"
        "リンクを開いた人一人につき — お前に <b>+{bonus_hours:g} 時間</b>。\n"
        "期限を逃すたび — 生存者が一人減る。"
    ),
    invite_share_bonus_for_inviter_line="このリンクを開いた人一人につき送信者のタイマーに <b>+{bonus_hours:g} 時間</b>。",
    share_no_username="ボットに username がありません — @BotFather で設定してください。",
    spread_open_failed="伝播画面を開けませんでした。<code>/start</code> をもう一度送ってください。",
    timer_inactive="タイマーは無効です。",
    timer_zombie="💀 <b>劣化完了 · ゾンビ</b>\n\n状態: <b>ゾンビ</b>。フルカードは <code>/start</code>。",
    timer_expired_pending="稀なデータ不整合。<code>/start</code> か 1 分待機。",
    timer_zombie_transition_pending=(
        "<b>🧪 状態評価</b> · ゾンビ化\n\n"
        "危機の期限が切れました。劣化フェーズを確定中です。<b>ゾンビ</b>表示は通常 <b>約1分以内</b>にチャットへ "
        "（毎分同期）。\n\n"
        "<code>/start</code> を再送するか、次のメッセージを待ってください。"
    ),
    zombie_screen06_banner="💀 SCREEN 06 · ゾンビ化",
    zombie_card_header="劣化完了 · ゾンビ",
    zombie_card_body=(
        "時間切れ。\n\n"
        "もう以前の状態ではない — お前は <b>ゾンビ</b>。"
        "株は混沌と動く — <i>あるいは我々が読めない台本に従って</i>。\n\n"
        "枝の下流にはまだ <b>{chain_total}</b> の宿主がいる。\n\n"
        "<b>ゲームは終わっていない。</b>"
    ),
    zombie_card_hint=(
        "ゾンビモード脱出の3つの方法:\n"
        "— <b>🧪 ラボ</b> — 連続3サイクル（1日も欠かさず）→ 復活（+48h）\n"
        "— <b>🌊 噴水</b> — グローバルイベントに参加 → 復活チャンス\n"
        "— <b>🛡 免疫</b> — <b>🔬 ターミナル</b>で1回限りのプロトコル"
    ),
    zombie_bar_label="壊死",
    zombie_phase_label="ゾンビ段階",
    zombie_badges_line="<code>ゾンビ</code>  <code>混沌感染</code>",
    zombie_timer_strip=(
        "🟪🟪🟪🟪🟪🟪🟪🟪🟪 <b>壊死</b>\n"
        "⏱ <b>危機タイマー停止中</b> · ゾンビ段階"
    ),
    timer_countdown="危機まで",
    timer_reserve="<i>危機までのウィンドウ: <b>{pct}%</b></i>",
    timer_zone_title="カウントダウン",
    timer_extend_sources=(
        "<b>時間が伸びる条件</b>\n"
        "• あなたのリンク経由の新規プレイヤー — <b>+{bonus_hours:g} 時間</b>\n"
        "• <b>🔬 ターミナル</b>のラボ — 1日最大 <b>+8 時間</b>\n"
        "• 同じ場所の噴水 — イベント参加者 <b>+12 時間</b>"
    ),
    own_invite_card_title="伝播コード · 有効",
    btn_refresh_remain="残り時間",
    btn_pick_contacts="🧬 マイ連絡先",
    hint_after_contacts_shared=(
        "メッセージ下のボタンからインラインカードを挿入したなら、相手はすでに招待を受け取っている。\n\n"
        "そうでなければリンク付きメッセージを転送するか、リンクを手で貼れ。"
    ),
    invite_bottom_keyboard_prompt=(
        "旧: メッセージ下の <b>「☣️ 株を伝播」</b> — インラインでチャットを選びカードを挿入。"
    ),
    spread_contact_send_failed=(
        "カードを届けられなかった — ボットをブロックしているかDM制限の可能性。"
    ),
    spread_contact_sent_ok="選んだ連絡先のボットチャットにカードを送った。",
    spread_join_chain_button="☣️ 感染チェーンに参加",
    share_native_prefill="もう連鎖に入れられた。開けて — 次がお前か確かめろ。",
    mock_header_new="☣️ 株 X-77 · 感染",
    mock_header_return="🧫 ステータス · 株アクティブ",
    mock_header_status="🧫 ステータス · 株アクティブ",
    mock_header_invite="🧬 伝播コード · 有効",
    mock_body_new_organic=(
        "おめでとう — ワクチンのないものにかかった。\n\n"
        "劣化が始まるまで <b>{timer_hours_phrase}</b> ある。\n"
        "生き残るには <b>株をできるだけ早く拡散する</b>しかない。\n\n"
        "<i>レジストリ脚注：出所は<b>検証不能</b>と印 — 痕跡を途中で切ったみたいだ。</i>"
    ),
    mock_body_new_referral=(
        "他人のリンクから入った — <b>相手のネットワーク</b>にいる。\n"
        "危機の時計はもう動いている。先手を取れ — または降りろ。"
    ),
    mock_body_return=(
        "株は広がっている。チェーンは <b>{network}</b> に達した。\n"
        "悪くない — だがウイルスは眠らない。タイマーもな。"
    ),
    mock_badges_new=(
        "<code>感染</code>  <code>チェーン #1</code>  <code>ランク: 宿主</code>"
    ),
    mock_badges_active="<i>☣️ 感染 · ネットワーク稼働 · 宿主</i>",
    invite_link_box_label="▸ 個人株リンク",
    mock_vita_label="残量",
    mock_decay_label="崩壊まで",
    mock_stat_ab_direct="直接（あなたのリンク）",
    mock_stat_ab_net="枝の合計",
    mock_stat_ab_sector="全体ランキング",
    mock_header_immune="🛡 免疫 · 回復",
    mock_body_immune=(
        "劣化後の<b>保護プロトコル</b>が有効。 "
        "ウィンドウが閉じるまで危機タイマーは停止 — その後シムは新しい期限で再開。"
    ),
    mock_immune_vita_label="シールド",
    mock_immune_decay_label="ウィンドウ終了まで",
    timer_immune_line="🛡 免疫: <code>{time_str}</code>",
    status_title="ステータス",
    btn_terminal="🔬 ターミナル",
    btn_live_timer="⏱ タイマー",
    btn_world="🌍 世界",
    btn_mutations="🧬 変異",
    btn_top="🏆 トップ",
    btn_immunity="🛡 免疫",
    stub_feature_soon="この項目はまだ開発中です — また後でどうぞ。",
    btn_back="↩ 戻る",
    back_to_main_ack="メインメニュー。",
    status_use_start="先にボットで /start を送ってください。",
    referral_new_carrier=(
        "もう一人。\n\n"
        "{newcomer} がリンクを開き、\n"
        "感染済み。チェーンが伸びている。\n\n"
        "{bonus_block}"
        "枝の宿主（合計）: <b>{branch_total}</b>"
    ),
    referral_timer_bonus="タイマーに <b>{bonus_hms}</b>。\n\n",
    menu_open_mini_hint=(
        "ボットチャット下部の<b>🔬 ターミナル</b>から — タイマー・ラボ・噴水。\n\n"
        "<i>そこの行が公開ブリーフと食い違うことがある — それもシムの一部。</i>"
    ),
    sweep_warn_10m="危機まで<b>10分未満</b>です。リンクを送ってください。",
    sweep_warn_30m="危機まで<b>30分未満</b>です。",
    sweep_warn_2h="危機まで<b>2時間未満</b>です。",
    sweep_warn_1h="危機まで<b>1時間未満</b>です。リンクを送ってください。",
    immune_activated_notice=(
        "<b>🛡 免疫を有効化</b>\n\n"
        "残り時間は Mini App（免疫ボタン）か /start で確認。"
    ),
    sweep_immune_ended=(
        "<b>免疫ウィンドウ終了</b>\n\n"
        "危機タイマーが再開 — リンクを広めてゾンビに戻らないように。"
    ),
    lab_ready_push=(
        "🧪 <b>分析完了</b>\n\n"
        "サンプル処理済み。<b>ラボ</b>を開いて結果を受け取ってください。\n\n"
        "<i>ログ末尾に未解読の断片 — 受け取り自体は妨げられない。</i>"
    ),
    lab_revived_push=(
        "⚡ <b>復活</b>\n\n"
        "ラボが機能しました。再び<b>感染者</b>になりました。\n"
        "新デッドライン: <b>+{timer_hours:g}h</b> — 菌株を広めてください。"
    ),
    affliction_type_necrosis_bloom="壊死ブルーム",
    affliction_type_signal_spoof="信号スプーフ",
    affliction_type_enzyme_leak="酵素漏出",
    affliction_type_latency_fog="遅延フォグ",
    affliction_spawn_push_pool=(
        "📡 <b>菌株ブリーフ</b>\n\n{strain}で新たな異常: <b>{type}</b>（{sev}）。\n"
        "ラボが支援を要求。«🧪 ラボ»でサイクルを完了し、治療を進めろ。",
    ),
    affliction_cured_push_pool=(
        "✅ <b>治療完了</b>\n\n{strain}: <b>{type}</b> を中和。\n"
        "ラボは仕事をした。ペース維持。",
    ),
    admin_forbidden="権限がありません。",
    admin_panel_intro="<b>管理パネル</b>\n\n操作を選んでください — ボタンは1行に1つ。",
    admin_btn_main_menu="↩ 通常メニュー",
    admin_btn_me_energy="⚡ 自分: クリッカー満タン",
    admin_btn_me_reagents="🧬 自分: DNA +500 · RNA +500 · CAT +50",
    admin_btn_me_timer="⏱ 自分: タイマー +24h",
    admin_me_need_register="プロフィールなし — 先に /start。",
    admin_me_energy_ok="<b>エネルギー</b>: <code>{e}</code> / <code>{m}</code>",
    admin_me_reagents_ok="<b>試薬</b>: DNA <code>{d}</code> · RNA <code>{r}</code> · CAT <code>{c}</code>",
    admin_me_timer_ok="<b>タイマー</b>: 締切 +<code>{h:g}</code>h。",
    admin_me_timer_skip="変更なし: <b>infected</b> と有効な締切が必要。",
    boost_card_header="🧬 <b>強化リンク</b>",
    boost_card_bonus="新規宿主ボーナス: タイマー <b>+{bonus_pct}%</b>。",
    boost_card_expires="有効期限: <code>{expires}</code>",
    boost_card_uses="使用回数: <b>{uses}</b>",
    boost_card_url_hint="新規宿主向けリンク:",
    boost_btn_copy="📋 コピー",
    boost_btn_owner_share="強化感染",
    boost_btn_spread="☣️ チェーンに参加",
    boost_inline_title="🧬 強化招待",
    boost_inline_description="強化株を連絡先に送る。",
    boost_share_invite_body_html=(
        "<b>{sender}</b> が強化株を渡す。\n\n"
        "シミュレーションは新しい宿主を待っている。\n"
        "招待を開いてチェーンに参加。"
    ),
)

ZH = Msg(
    btn_spread="☣️ 传播毒株",
    btn_status="📊 状态",
    btn_admin="⚙️ 管理",
    welcome_title="疫情已记录",
    welcome_subtitle_organic=(
        "你是这条传播链的<b>指示病例</b>。趁还来得及，找到新的宿主。\n\n"
        "<i>公开简报不点名源头 — 只有倒计时。</i>"
    ),
    welcome_subtitle_referral=(
        "你通过他人的链接进入 — 你在<b>对方的网络</b>中。"
        "<i>谁把你路由到这里 — 未说明。</i>"
    ),
    welcome_timer="距离危机",
    welcome_link_hint="你的专属链接",
    welcome_no_bot_username="请在 @BotFather 为机器人设置 username，否则无法生成邀请链接。",
    already_in_game_reinfect=(
        "你已在模拟中。无法通过其他链接再次进入 — 请只分享<b>你自己的</b>链接（下方按钮）。"
    ),
    welcome_back_title="疫源再次上线。",
    stats_direct="直接命中",
    stats_network="链条中在你之下",
    stats_country="你的扇区",
    stats_banner="疫源简报",
    share_title=(
        "生物载荷已就绪。\n"
        "点下方 <b>「🧬 我的联系人」</b> — <b>机器人会给对方发卡片</b>（仅机器人链接，<code>t.me/…</code>）。\n\n"
        "卡片里的链接可点击该行复制。\n\n"
        "每有人打开你的链接 — 你获得 <b>+{bonus_hours:g} 小时</b>。\n"
        "每错过一次期限 — 少一个幸存者。"
    ),
    invite_share_bonus_for_inviter_line="每有人打开此链接，发送方计时器 <b>+{bonus_hours:g} 小时</b>。",
    share_no_username="机器人没有 username — 请在 @BotFather 设置。",
    spread_open_failed="无法打开传播界面。请再发送一次 <code>/start</code>。",
    timer_inactive="计时器未启用。",
    timer_zombie="💀 <b>降解完成 · 僵尸</b>\n\n状态：<b>僵尸</b>。完整卡片请 <code>/start</code>。",
    timer_expired_pending="偶发数据不同步。请 <code>/start</code> 或等待约一分钟。",
    timer_zombie_transition_pending=(
        "<b>🧪 状态评估</b> · 僵尸转化\n\n"
        "危机截止时间已过：正在锁定降解阶段。<b>僵尸</b>状态通常会在 <b>约一分钟内</b>同步到聊天"
        "（每分钟同步一次）。\n\n"
        "可再次发送 <code>/start</code> 或等待下一条消息。"
    ),
    zombie_screen06_banner="💀 SCREEN 06 · 僵尸转化",
    zombie_card_header="降解完成 · 僵尸",
    zombie_card_body=(
        "时间到了。\n\n"
        "你不再是先前状态 — 你是 <b>僵尸</b>。"
        "毒株行为混乱 — <i>或者按我们读不到的剧本在动</i>。\n\n"
        "你的分支下仍有 <b>{chain_total}</b> 名宿主。\n\n"
        "<b>游戏未结束。</b>"
    ),
    zombie_card_hint=(
        "退出僵尸模式的三条路：\n"
        "— <b>🧪 实验室</b> — 连续3个周期（不漏一天）→ 复活（+48小时）\n"
        "— <b>🌊 喷泉</b> — 参与全球活动 → 复活机会\n"
        "— <b>🛡 免疫</b> — 通过 <b>🔬 终端</b> 一次性协议"
    ),
    zombie_bar_label="坏死",
    zombie_phase_label="僵尸阶段",
    zombie_badges_line="<code>僵尸</code>  <code>混沌传播</code>",
    zombie_timer_strip=(
        "🟪🟪🟪🟪🟪🟪🟪🟪🟪 <b>坏死</b>\n"
        "⏱ <b>危机计时已关闭</b> · 僵尸阶段"
    ),
    timer_countdown="距离危机",
    timer_reserve="<i>距危机剩余窗口：<b>{pct}%</b></i>",
    timer_zone_title="倒计时",
    timer_extend_sources=(
        "<b>哪些情况会延长倒计时</b>\n"
        "• 有人通过你的链接首次入坑 — <b>+{bonus_hours:g} 小时</b>\n"
        "• <b>🔬 终端</b>里的实验室 — 每天最多 <b>+8 小时</b>\n"
        "• 同一处的生命喷泉 — 活动参与者 <b>+12 小时</b>"
    ),
    own_invite_card_title="传播代码 · 生效中",
    btn_refresh_remain="还剩多久",
    btn_pick_contacts="🧬 我的联系人",
    hint_after_contacts_shared=(
        "如果你刚通过消息下的按钮插入了内联卡片，对方已收到邀请。\n\n"
        "否则请转发带链接的消息或手动粘贴链接。"
    ),
    invite_bottom_keyboard_prompt=(
        "旧流程：点消息下方 <b>「☣️ 传播毒株」</b> — 内联选聊天并插入卡片。"
    ),
    spread_contact_send_failed=(
        "无法送达卡片 — 可能屏蔽了机器人或限制了陌生人私聊。"
    ),
    spread_contact_sent_ok="卡片已发送到所选联系人与机器人的聊天。",
    spread_join_chain_button="☣️ 加入感染链",
    share_native_prefill="我已经被写进传播链了。点开看看 — 下一个会不会是你。",
    mock_header_new="☣️ 毒株 X-77 · 已感染",
    mock_header_return="🧫 状态 · 毒株活跃",
    mock_header_status="🧫 状态 · 毒株活跃",
    mock_header_invite="🧬 传播代码 · 生效中",
    mock_body_new_organic=(
        "恭喜 — 你刚染上了没有疫苗的东西。\n\n"
        "在降解开始前你还有 <b>{timer_hours_phrase}</b>。\n"
        "唯一能活下去的方法是<b>尽快把毒株扩散出去</b>。\n\n"
        "<i>登记脚注：来源标为<b>不可核实</b> — 像有人截断了轨迹。</i>"
    ),
    mock_body_new_referral=(
        "你从别人的链接进来 — 你在<b>对方的网络</b>里。\n"
        "危机时钟已在走。抢先 — 或退出。"
    ),
    mock_body_return=(
        "毒株在扩散。你的链条已触及 <b>{network}</b>。\n"
        "不错 — 但病毒从不睡。计时器也是。"
    ),
    mock_badges_new=(
        "<code>已感染</code>  <code>链 #1</code>  <code>等级：宿主</code>"
    ),
    mock_badges_active="<i>☣️ 已感染 · 网络活跃 · 宿主</i>",
    invite_link_box_label="▸ 个人毒株链接",
    mock_vita_label="余量",
    mock_decay_label="距降解",
    mock_stat_ab_direct="直接（你的链接）",
    mock_stat_ab_net="你分支下合计",
    mock_stat_ab_sector="全服排名",
    mock_header_immune="🛡 免疫 · 恢复",
    mock_body_immune=(
        "降解后<b>保护协议</b>已启用。 "
        "窗口结束前危机计时暂停 — 之后模拟将以新的截止时间继续。"
    ),
    mock_immune_vita_label="护盾",
    mock_immune_decay_label="窗口剩余",
    timer_immune_line="🛡 免疫: <code>{time_str}</code>",
    status_title="状态",
    btn_terminal="🔬 终端",
    btn_live_timer="⏱ 计时器",
    btn_world="🌍 世界",
    btn_mutations="🧬 变异",
    btn_top="🏆 排行",
    btn_immunity="🛡 免疫",
    stub_feature_soon="该功能仍在开发中 — 请稍后再试。",
    btn_back="↩ 返回",
    back_to_main_ack="主菜单。",
    status_use_start="请先在机器人中发送 /start。",
    referral_new_carrier=(
        "又来一个。\n\n"
        "{newcomer} 打开了你的链接，\n"
        "已经感染。你的链条在壮大。\n\n"
        "{bonus_block}"
        "分支宿主合计：<b>{branch_total}</b>"
    ),
    referral_timer_bonus="计时器 <b>{bonus_hms}</b>。\n\n",
    menu_open_mini_hint=(
        "在机器人聊天底部点<b>🔬 终端</b> — 计时器、实验室、喷泉。\n\n"
        "<i>那里的文字有时和公开简报不一致 — 这也是模拟的一部分。</i>"
    ),
    sweep_warn_10m="距离危机<b>不足 10 分钟</b>。请尽快发送你的链接。",
    sweep_warn_30m="距离危机<b>不足 30 分钟</b>。",
    sweep_warn_2h="距离危机<b>不足 2 小时</b>。",
    sweep_warn_1h="距离危机<b>不足 1 小时</b>。请发送你的链接。",
    immune_activated_notice=(
        "<b>🛡 免疫已激活</b>\n\n"
        "剩余时间在 Mini App（免疫按钮）或通过 /start 刷新。"
    ),
    sweep_immune_ended=(
        "<b>免疫窗口已结束</b>\n\n"
        "危机计时再次运行 — 传播链接以免回到僵尸状态。"
    ),
    lab_ready_push=(
        "🧪 <b>分析完成</b>\n\n"
        "样本已处理。打开<b>实验室</b>领取结果。\n\n"
        "<i>日志尾部有一段未解码碎片 — 不影响你领取。</i>"
    ),
    lab_revived_push=(
        "⚡ <b>复活</b>\n\n"
        "实验室发挥了作用。你再次成为<b>感染者</b>。\n"
        "新截止时间：<b>+{timer_hours:g}小时</b> — 传播毒株。"
    ),
    affliction_type_necrosis_bloom="坏死绽放",
    affliction_type_signal_spoof="信号伪装",
    affliction_type_enzyme_leak="酶泄漏",
    affliction_type_latency_fog="延迟迷雾",
    affliction_spawn_push_pool=(
        "📡 <b>毒株简报</b>\n\n{strain} 检测到新异常：<b>{type}</b>（{sev}）。\n"
        "实验室需要协助：打开「🧪 实验室」完成循环以推进解药。",
    ),
    affliction_cured_push_pool=(
        "✅ <b>已治愈</b>\n\n{strain}：<b>{type}</b> 已被中和。\n"
        "实验室奏效。继续保持节奏。",
    ),
    admin_forbidden="权限不足。",
    admin_panel_intro="<b>管理面板</b>\n\n选择操作 — 每行一个按钮。",
    admin_btn_main_menu="↩ 普通菜单",
    admin_btn_me_energy="⚡ 我：点击器能量加满",
    admin_btn_me_reagents="🧬 我：DNA +500 · RNA +500 · CAT +50",
    admin_btn_me_timer="⏱ 我：危机计时 +24 小时",
    admin_me_need_register="没有档案 — 请先 /start。",
    admin_me_energy_ok="<b>能量</b>: <code>{e}</code> / <code>{m}</code>",
    admin_me_reagents_ok="<b>试剂</b>: DNA <code>{d}</code> · RNA <code>{r}</code> · CAT <code>{c}</code>",
    admin_me_timer_ok="<b>计时器</b>: 截止 +<code>{h:g}</code> 小时。",
    admin_me_timer_skip="未改动：需要 <b>infected</b> 且有活跃截止时间。",
    boost_card_header="🧬 <b>强化链接</b>",
    boost_card_bonus="新宿主加成：计时 <b>+{bonus_pct}%</b>。",
    boost_card_expires="有效期至：<code>{expires}</code>",
    boost_card_uses="可用次数：<b>{uses}</b>",
    boost_card_url_hint="给新宿主的链接：",
    boost_btn_copy="📋 复制链接",
    boost_btn_owner_share="强化感染",
    boost_btn_spread="☣️ 加入链条",
    boost_inline_title="🧬 强化邀请",
    boost_inline_description="将强化毒株发送给联系人。",
    boost_share_invite_body_html=(
        "<b>{sender}</b> 向你传递强化毒株。\n\n"
        "模拟等待新的宿主。\n"
        "打开邀请并加入链条。"
    ),
)

MESSAGES: dict[str, Msg] = {
    "ru": RU,
    "en": EN,
    "uk": UK,
    "de": DE,
    "es": ES,
    "pt": PT,
    "ko": KO,
    "ja": JA,
    "zh": ZH,
}

SPREAD_BUTTON_TEXTS: frozenset[str] = frozenset(m.btn_spread for m in MESSAGES.values()) | frozenset(
    {
        "☣️ Передать штамп",  # опечатка / старая подпись клавиатуры
    }
)

REFRESH_TIME_BUTTON_TEXTS: frozenset[str] = frozenset(m.btn_refresh_remain for m in MESSAGES.values())

STATUS_BUTTON_TEXTS: frozenset[str] = frozenset(m.btn_status for m in MESSAGES.values())

ADMIN_BUTTON_TEXTS: frozenset[str] = frozenset(m.btn_admin for m in MESSAGES.values())

ADMIN_MAIN_MENU_TEXTS: frozenset[str] = frozenset(m.admin_btn_main_menu for m in MESSAGES.values())

ADMIN_ME_ENERGY_TEXTS: frozenset[str] = frozenset(m.admin_btn_me_energy for m in MESSAGES.values())

ADMIN_ME_REAGENTS_TEXTS: frozenset[str] = frozenset(m.admin_btn_me_reagents for m in MESSAGES.values())

ADMIN_ME_TIMER_TEXTS: frozenset[str] = frozenset(m.admin_btn_me_timer for m in MESSAGES.values())

MENU_BUTTON_TEXTS: frozenset[str] = frozenset(
    t for m in MESSAGES.values() for t in (m.btn_world, m.btn_mutations, m.btn_top)
)

BACK_BUTTON_TEXTS: frozenset[str] = frozenset(m.btn_back for m in MESSAGES.values())


def pick_locale(language_code: str | None) -> str:
    """BCP 47 → ключ локали для MESSAGES."""
    if not language_code:
        return "en"
    lc = language_code.strip()
    primary = lc.split("-")[0].lower()

    # Китайский: теги вида zh-Hans, zh-CN → zh
    if primary == "zh":
        return "zh"

    if primary == "en":
        return "en"
    if primary == "uk":
        return "uk"
    if primary in ("ru", "be", "kk", "ky"):
        return "ru"
    if primary == "de":
        return "de"
    if primary == "es":
        return "es"
    if primary == "pt":
        return "pt"
    if primary == "ko":
        return "ko"
    if primary == "ja":
        return "ja"
    return "en"


def get_msg(locale: str | None) -> Msg:
    if locale and locale in MESSAGES:
        return MESSAGES[locale]
    return EN
