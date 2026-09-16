"""Генерация юридических документов для дел о банкротстве.

Шаблоны основаны на реальном кейсе А32-37431/2025 (Макурин В.В.),
извлечённом из базы знаний в docs/knowledge/case_16-09-2026.

Два режима:
- template: генерация по шаблонам (работает без LLM-ключей)
- llm: генерация через LLM поверх шаблона и RAG-контекста
"""

import re
from dataclasses import dataclass, field
from datetime import date

from app.ai.knowledge_base import KnowledgeChunk
from app.core.config import get_settings

settings = get_settings()

# Нормативная база, используемая в шаблонах
LEGAL_FRAMEWORK = {
    "bankruptcy_law": "Федеральный закон от 26.10.2002 № 127-ФЗ «О несостоятельности (банкротстве)»",
    "art_213_25": "пункты 5, 7 ст. 213.25 Закона о банкротстве",
    "art_213_26_7": "п. 7 ст. 213.26 Закона о банкротстве",
    "art_213_9_7": "абз. 5 п. 7 ст. 213.9 Закона о банкротстве",
    "art_213_9_9": "п. 9 ст. 213.9 Закона о банкротстве",
    "art_20_3_1": "абз. 7 п. 1 ст. 20.3 Закона о банкротстве",
    "art_223_1": "статья 223.1 Закона о банкротстве",
    "art_14_13": "ч. 4 ст. 14.13 Кодекса Российской Федерации об административных правонарушениях",
    "sc_family": "ч. 1 ст. 34 Семейного кодекса Российской Федерации",
    "law_218": "Федеральный закон от 13.07.2015 № 218-ФЗ «О государственной регистрации недвижимости»",
}

# Стандартные формулировки уведомления о статусе банкрота
BANKRUPT_NOTICE = """Настоящим уведомляю Вас о том, что в соответствии с {art_213_25} с даты признания гражданина банкротом:
- все права в отношении имущества, составляющего конкурсную массу, в том числе на распоряжение им, осуществляются только финансовым управляющим от имени гражданина и не могут осуществляться гражданином лично;
- сделки, совершенные гражданином лично (без участия финансового управляющего) в отношении имущества, составляющего конкурсную массу, ничтожны;
- регистрация перехода или обременения прав гражданина на имущество, в том числе на недвижимое имущество и бездокументарные ценные бумаги, осуществляется только на основании заявления финансового управляющего. Поданные до этой даты заявления гражданина не подлежат исполнению."""

SPOUSE_PROPERTY_NOTICE = """При этом {art_213_26_7} предусматривает, что имущество гражданина, принадлежащее ему на праве общей собственности с супругом (бывшим супругом), подлежит реализации в деле о банкротстве гражданина по общим правилам, предусмотренным настоящей статьей.
А согласно {sc_family} имущество, нажитое супругами во время брака, является их совместной собственностью."""

RIGHTS_NOTICE = """Кроме того, в силу {art_20_3_1} арбитражный управляющий вправе запрашивать необходимые сведения о должнике, о лицах, входящих в состав органов управления должника, о контролирующих лицах, о принадлежащем им имуществе (в том числе имущественных правах), о контрагентах и об обязательствах должника у физических лиц, юридических лиц, государственных органов, органов управления государственными внебюджетными фондами Российской Федерации и органов местного самоуправления, включая сведения, составляющие служебную, коммерческую и банковскую тайну."""

ACCOUNTS_NOTICE = """На основании {art_213_9_7} финансовый управляющий вправе получать информацию об имуществе гражданина, а также о счетах и вкладах (депозитах) гражданина, в том числе по банковским картам, об остатках электронных денежных средств и о переводах электронных денежных средств от граждан и юридических лиц (включая кредитные организации), от органов государственной власти, органов местного самоуправления."""

ADMIN_LIABILITY_NOTICE = """При этом {art_14_13} предусмотрена административная ответственность за неправомерный отказ финансовому управляющему в предоставлении информации, необходимой для проведения процедуры банкротства."""

DEBTOR_DUTY_NOTICE = """В соответствии с {art_213_9_9} гражданин обязан предоставлять финансовому управляющему по его требованию любые сведения о составе своего имущества, месте нахождения этого имущества, составе своих обязательств, кредиторах и иные имеющие отношение к делу о банкротстве гражданина сведения в течение пятнадцати дней с даты получения требования об этом.
При неисполнении гражданином указанной обязанности финансовый управляющий направляет в арбитражный суд ходатайство об истребовании доказательств."""


@dataclass
class CaseContext:
    """Контекст дела для генерации (заполняется из модели Case + Debtor)."""

    case_number: str = ""
    court_name: str = "Арбитражный суд"
    court_decision_date: str = ""
    kad_url: str = ""  # ссылка на карточку дела (можно оставить пустой)

    debtor_full_name: str = ""
    debtor_birth_date: str = ""
    debtor_birth_place: str = ""
    debtor_inn: str = ""
    debtor_snils: str = ""
    debtor_address: str = ""

    spouse_full_name: str = ""
    spouse_birth_date: str = ""
    spouse_birth_place: str = ""
    spouse_address: str = ""

    manager_full_name: str = ""
    manager_address: str = ""
    manager_email: str = ""
    manager_phone: str = ""
    manager_passport: str = ""   # серия+номер, напр. "0306 № 418377"
    manager_snils: str = ""

    period_start: str = "07.07.2015"  # 3 года до подачи заявления (по умолчанию)
    date_today: str = field(default_factory=lambda: date.today().strftime("%d.%m.%Y"))


class DocumentTemplateGenerator:
    """Генератор документов по шаблонам реального кейса."""

    DOCUMENT_TYPES = {
        "request_fns": "Запрос в ФНС России",
        "request_rosreestr": "Запрос в Росреестр (уведомление)",
        "request_egrn": "Запрос выписки из ЕГРН (форма Росреестра)",
        "request_egrn_spouse": "Запрос выписки ЕГРН по супругу",
        "request_gibdd": "Запрос в ГИБДД",
        "request_gims": "Запрос в ГИМС МЧС",
        "request_gostekhnadzor": "Запрос в Гостехнадзор",
        "request_depository": "Запрос в депозитарий",
        "request_zags": "Запрос в ЗАГС",
        "request_osfr": "Запрос в ОСФР",
        "request_land": "Запрос по земельным участкам и аренде",
        "request_rosaviation": "Запрос в Росавиацию",
        "request_rosgvardiya": "Запрос в Росгвардию",
        "request_rospatent": "Запрос в Роспатент",
        "request_bti": "Запрос в БТИ (Ростехинвентаризация)",
        "request_rsa": "Запрос в РСА",
        "request_migration_mvd": "Запрос в УВМ МВД",
        "request_magistrate": "Запрос мировому судье",
        "request_general_court": "Запрос в суд общей юрисдикции",
        "request_bailiff": "Уведомление приставов ОСП",
        "request_spouse": "Требование к супругу (совместное имущество)",
        "request_debtor": "Требование к должнику (сведения об имуществе)",
        "creditor_notification": "Уведомление кредиторам и запрос досье",
        "account_closure": "Закрытие счетов должника в банке",
        "completion_petition": "Ходатайство о завершении процедуры",
    }

    # --- Шапка и общие элементы ---

    def _header(self, c: CaseContext) -> str:
        return (
            "АРБИТРАЖНЫЙ УПРАВЛЯЮЩИЙ\n"
            f"{c.manager_full_name}\n"
            f"{c.manager_address}\n"
            f"эл. почта {c.manager_email} телефон {c.manager_phone}"
        )

    def _debtor_block(self, c: CaseContext) -> str:
        lines = ["(далее – должник):", ""]
        if c.debtor_full_name:
            lines.append(f"Фамилия, имя, отчество: {c.debtor_full_name}")
        if c.debtor_birth_date:
            lines.append(f"Дата рождения: {c.debtor_birth_date}")
        if c.debtor_birth_place:
            lines.append(f"Место рождения: {c.debtor_birth_place}")
        if c.debtor_inn:
            lines.append(f"ИНН: {c.debtor_inn}")
        if c.debtor_snils:
            lines.append(f"СНИЛС: {c.debtor_snils}")
        if c.debtor_address:
            lines.append(f"Зарегистрирован по адресу: {c.debtor_address}")
        return "\n".join(lines)

    def _preamble(self, c: CaseContext, title: str = "ЗАПРОС") -> str:
        kad = (
            f" (автоматизированная копия судебного акта размещена в официальном сервисе "
            f"«Картотека арбитражных дел» по адресу {c.kad_url})"
            if c.kad_url
            else ""
        )
        return (
            f"{c.court_decision_date}г.\n"
            f"{title}\n"
            f"Решением {c.court_name} от {c.court_decision_date} по делу № {c.case_number}{kad} "
            f"введена процедура банкротства в отношении\n"
            f"{self._debtor_block(c)}\n"
            f"Финансовым управляющим должника утверждена {c.manager_full_name}."
        )

    def _footer(self, c: CaseContext) -> str:
        return (
            f"Ответ прошу продублировать по электронной почте: {c.manager_email}\n"
            "Приложение:\n"
            "1. Автоматизированная копия судебного акта о введении процедуры банкротства в 1 экз.\n"
            "2. Копия свидетельства о заключении брака в 1 экз.\n\n"
            f"Финансовый управляющий {c.manager_full_name}"
        )

    # --- Просительные части по органам ---

    def _fns_request_items(self, c: CaseContext) -> str:
        p = c.period_start
        inn = c.debtor_inn
        spouse = c.spouse_full_name or f"супруг(а) должника"
        return (
            f"Представить:\n"
            f"- справки о доходах (форма 2-НДФЛ) {c.debtor_full_name} за период с {p} по настоящее время;\n"
            f"- сведения об открытых (закрытых) счетах {c.debtor_full_name} и {spouse}, за период с {p} по настоящее время;\n"
            f"- налоговые декларации {c.debtor_full_name} по НДФЛ (форма 3-НДФЛ) за период с {p} по настоящее время;\n"
            f"- сведения об участии {c.debtor_full_name} и {spouse} в уставных капиталах юридических лиц;\n"
            f"- сведения о сделках, совершенных {c.debtor_full_name} и {spouse}, с долями в уставных капиталах юридических лиц за период с {p} по настоящее время;\n"
            f"- сведения о {c.debtor_full_name} как о руководителе юридических лиц;\n"
            f"- справку о наличии и размере задолженности {c.debtor_full_name} по налогам и пеням на текущую дату с указанием периода возникновения задолженности.\n"
            f"Также просим представить налоговые декларации, соответствующие применяемому {c.debtor_full_name} и {spouse} режиму налогообложения, книги расходов и доходов, книги покупок за период с {p} по настоящее время как индивидуальными предпринимателями."
        )

    # --- Генерация по типам ---

    def generate(self, doc_type: str, c: CaseContext) -> str:
        """Генерация документа по типу и контексту."""
        if doc_type not in self.DOCUMENT_TYPES:
            raise ValueError(f"Unknown document type: {doc_type}")

        generator = getattr(self, f"_gen_{doc_type}", None)
        if generator is None:
            raise ValueError(f"No generator for document type: {doc_type}")
        return generator(c)

    # === Запросы ===

    def _gen_request_fns(self, c: CaseContext) -> str:
        return (
            f"{self._header(c)}\n"
            f"Межрайонная ИФНС России № 10 по Краснодарскому краю\n"
            f"Адрес: ул. Ленина, 171, Тимашевск, Краснодарский край, 352708\n"
            f"Финансовый управляющий\n{c.manager_full_name}\n{c.manager_address}\n\n"
            f"{self._preamble(c)}\n\n"
            f"{BANKRUPT_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            f"{SPOUSE_PROPERTY_NOTICE.format(**LEGAL_FRAMEWORK)}\n"
            f"Финансовым управляющим установлено, что должник состоит в браке с {c.spouse_full_name}, "
            f"дата рождения {c.spouse_birth_date}, место рождения {c.spouse_birth_place}.\n\n"
            f"{RIGHTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            f"{ACCOUNTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            f"{ADMIN_LIABILITY_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            f"На основании изложенного,\nП Р О Ш У:\n{self._fns_request_items(c)}\n\n"
            f"{self._footer(c)}"
        )

    def _gen_request_spouse(self, c: CaseContext) -> str:
        spouse = c.spouse_full_name or "Супруг(а) должника"
        return (
            f"{self._header(c)}\n"
            f"{spouse}\n"
            f"{c.spouse_address}\n\n"
            f"{self._preamble(c)}\n\n"
            f"{BANKRUPT_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            f"{DEBTOR_DUTY_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            f"{RIGHTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            f"{ACCOUNTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            f"{ADMIN_LIABILITY_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            "На основании изложенного,\nТ Р Е Б У Ю:\n"
            "I. Обеспечить передачу финансовому управляющему Вашего совместно нажитого имущества "
            "(автотранспортные средства, самоходные машины, иное движимое имущество) и материальных "
            "ценностей, не подлежащих исключению из конкурсной массы.\n"
            "II. Представить:\n"
            "1. актуальный перечень Вашего имущества, в том числе имущественных прав, приобретенных в период брака;\n"
            "2. документы, подтверждающие Ваши права на недвижимое имущество, транспортные средства, "
            "самоходные машины, объекты незавершенного строительства, которые принадлежат Вам на праве "
            "собственности, аренды, безвозмездного пользования или ином праве, возникшие в период брака;\n"
            "3. перечень Ваших дебиторов с указанием их адресов, размера основной задолженности, штрафов, "
            "пеней и иных финансовых (экономических) санкций;\n"
            "4. материалы судебных процессов с Вашим участием;\n"
            "5. сведения о наличии у Вас криптовалюты;\n"
            "6. информацию о Вашем имуществе, хранящемся в арендованных складских помещениях.\n\n"
            f"Ответ прошу продублировать по электронной почте: {c.manager_email}\n\n"
            f"Финансовый управляющий {c.manager_full_name}"
        )

    def _gen_request_gibdd(self, c: CaseContext) -> str:
        spouse = c.spouse_full_name or f"супруг(а) должника"
        return (
            f"{self._header(c)}\n"
            f"УПРАВЛЕНИЕ ГИБДД ГУ МВД РОССИИ ПО КРАСНОДАРСКОМУ КРАЮ\n"
            f"350020, г. Краснодар, ул. Гаврилова, 96\n\n"
            f"{self._preamble(c, title='УВЕДОМЛЕНИЕ-ЗАПРОС')}\n\n"
            f"{BANKRUPT_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            f"{SPOUSE_PROPERTY_NOTICE.format(**LEGAL_FRAMEWORK)}\n"
            f"Финансовым управляющим установлено, что должник состоит в браке с {spouse}.\n\n"
            f"{RIGHTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            f"{ACCOUNTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            f"{ADMIN_LIABILITY_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            "На основании изложенного,\nП Р О Ш У:\n"
            f"1. Не производить государственную регистрацию или снятие с учета автотранспортных средств "
            f"{c.debtor_full_name} и {spouse}, без письменного заявления финансового управляющего.\n"
            f"2. Представить:\n"
            f"- сведения о транспортных средствах, зарегистрированных за {c.debtor_full_name} и {spouse};\n"
            f"- сведения о совершенных {c.debtor_full_name} и {spouse} сделках с транспортными средствами "
            f"за период с {c.period_start} по настоящее время.\n"
            f"В случае совершения сделок прошу предоставить копию соответствующего правоустанавливающего документа "
            f"(договора купли-продажи, дарения и т.п.).\n\n"
            f"{self._footer(c)}"
        )

    def _gen_request_egrn(self, c: CaseContext) -> str:
        """Форма запроса выписки ЕГРН (по приказу Росреестра № П/0149)."""
        return (
            "Приложение № 2 к Порядку предоставления сведений, содержащихся в Едином государственном реестре "
            "недвижимости, утвержденному приказом Росреестра от 8 апреля 2021 г. № П/0149\n"
            "(в ред. Приказа Росреестра от 08.11.2021 № П/0501, от 04.07.2022 № П/0264, от 07.11.2022 № П/0427)\n"
            "ЗАПРОС\n"
            "о предоставлении сведений, содержащихся в Едином государственном реестре недвижимости, "
            "об объектах недвижимости и (или) их правообладателях\n\n"
            "1.1. Прошу предоставить сведения:\n"
            "правообладатель: физическое лицо:\n"
            f"фамилия, имя, отчество (при наличии): {c.debtor_full_name}\n"
            f"дата рождения: {c.debtor_birth_date}\n"
            f"СНИЛС: {c.debtor_snils}\n"
            f"адрес места жительства: {c.debtor_address}\n"
            "в виде: выписки из Единого государственного реестра недвижимости о правах отдельного лица "
            f"на имевшиеся (имеющиеся) у него объекты недвижимости\n"
            f"вид(ы) объекта(ов): все\n"
            f"на территории: Российской Федерации\n"
            f"за период: с {c.period_start} по настоящее время.\n"
            "1.2. Форма предоставления сведений: в виде бумажного документа.\n"
            f"1.3. Способ получения: Почтовым отправлением по адресу: {c.manager_address}\n\n"
            "3. Сведения о заявителе (арбитражном управляющем):\n"
            f"фамилия, имя, отчество (при наличии): {c.manager_full_name}\n"
            f"СНИЛС: {c.manager_snils}\n"
            f"телефон: {c.manager_phone}, адрес электронной почты: {c.manager_email}\n\n"
            "6. Документы, прилагаемые к запросу:\n"
            f"Решение суда от {c.court_decision_date} № {c.case_number}. Копия в количестве 1 экз.\n\n"
            "8. Подтверждаю свое согласие на обработку персональных данных.\n"
            f"9. _______________ {c.manager_full_name}  (подпись)  дата {c.date_today}"
        )

    def _gen_request_egrn_spouse(self, c: CaseContext) -> str:
        """Форма запроса выписки ЕГРН по супругу (вариант запроса)."""
        spouse = c.spouse_full_name or c.spouse_full_name
        return (
            f"{self._header(c)}\n"
            f"В ФИЛИАЛ ППК «РОСКАДАСТР» ПО КРАСНОДАРСКОМУ КРАЮ\n\n"
            f"{self._preamble(c)}\n\n"
            f"{SPOUSE_PROPERTY_NOTICE.format(**LEGAL_FRAMEWORK)}\n"
            f"Финансовым управляющим установлено, что должник состоит в браке с {spouse}.\n\n"
            f"{RIGHTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            "На основании изложенного,\nП Р О Ш У:\n"
            f"Представить выписку из ЕГРН о правах отдельного лица на имевшиеся (имеющиеся) у него объекты "
            f"недвижимости в отношении {spouse} за период с {c.period_start} по настоящее время.\n\n"
            f"{self._footer(c)}"
        )

    def _gen_request_rosreestr(self, c: CaseContext) -> str:
        return (
            f"{self._header(c)}\n"
            f"УПРАВЛЕНИЕ ФЕДЕРАЛЬНОЙ СЛУЖБЫ ГОСУДАРСТВЕННОЙ РЕГИСТРАЦИИ, КАДАСТРА И КАРТОГРАФИИ "
            f"ПО КРАСНОДАРСКОМУ КРАЮ (РОСРЕЕСТР)\n"
            f"350063, г. Краснодар, ул. Ленина, 28\n\n"
            f"{self._preamble(c, title='УВЕДОМЛЕНИЕ')}\n\n"
            f"{BANKRUPT_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            f"{SPOUSE_PROPERTY_NOTICE.format(**LEGAL_FRAMEWORK)}\n"
            f"Финансовым управляющим установлено, что должник состоит в браке с {c.spouse_full_name}.\n\n"
            "На основании изложенного,\nП Р О Ш У:\n"
            f"Не производить государственную регистрацию перехода или обременения прав на недвижимое имущество "
            f"{c.debtor_full_name} и {c.spouse_full_name}, без письменного заявления финансового управляющего.\n\n"
            f"Ответ прошу продублировать по электронной почте: {c.manager_email}\n\n"
            f"Финансовый управляющий {c.manager_full_name}"
        )

    def _gen_request_zags(self, c: CaseContext) -> str:
        return (
            f"{self._header(c)}\n"
            f"ОРГАН ЗАПИСИ АКТОВ ГРАЖДАНСКОГО СОСТОЯНИЯ (ЗАГС)\n"
            f"350010, г. Краснодар, ул. Постовая, 47\n\n"
            f"{self._preamble(c)}\n\n"
            f"{RIGHTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            f"{ACCOUNTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            "На основании изложенного,\nП Р О Ш У:\n"
            f"Представить сведения о государственной регистрации актов гражданского состояния "
            f"в отношении {c.debtor_full_name} и {c.spouse_full_name} (регистрация брака, рождение детей, "
            f"смена фамилии) за период с {c.period_start} по настоящее время.\n\n"
            f"{self._footer(c)}"
        )

    def _gen_request_osfr(self, c: CaseContext) -> str:
        return (
            f"{self._header(c)}\n"
            f"ОТДЕЛЕНИЕ ФОНДА ПЕНСИОННОГО И СОЦИАЛЬНОГО СТРАХОВАНИЯ (ОСФР) ПО КРАСНОДАРСКОМУ КРАЮ\n"
            f"350015, Краснодарский край, г. Краснодар\n\n"
            f"{self._preamble(c)}\n\n"
            f"{RIGHTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            f"{ACCOUNTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            "На основании изложенного,\nП Р О Ш У:\n"
            f"Представить сведения о {c.debtor_full_name} (СНИЛС {c.debtor_snils}): страховой номер, "
            f"сведения о пенсионных накоплениях, о работодателях и периодах работы, о размере страховой пенсии.\n\n"
            f"{self._footer(c)}"
        )

    def _gen_request_gims(self, c: CaseContext) -> str:
        return (
            f"{self._header(c)}\n"
            f"ЦЕНТР ГИМС ГЛАВНОГО УПРАВЛЕНИЯ МЧС РОССИИ ПО КРАСНОДАРСКОМУ КРАЮ\n"
            f"350080, г. Краснодар, ул. Красных Партизан, 121\n\n"
            f"{self._preamble(c)}\n\n"
            f"{RIGHTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            "На основании изложенного,\nП Р О Ш У:\n"
            f"Представить сведения о зарегистрированных за {c.debtor_full_name} и {c.spouse_full_name} маломерных "
            f"судах и о совершенных сделках с ними за период с {c.period_start} по настоящее время.\n\n"
            f"{self._footer(c)}"
        )

    def _gen_request_gostekhnadzor(self, c: CaseContext) -> str:
        return (
            f"{self._header(c)}\n"
            f"ГОСУДАРСТВЕННЫЙ НАДЗОР ЗА ТЕХНИЧЕСКИМ СОСТОЯНИЕМ САМОХОДНЫХ МАШИН И ДРУГИХ ВИДОВ ТЕХНИКИ "
            f"ПО КРАСНОДАРСКОМУ КРАЮ\n\n"
            f"{self._preamble(c)}\n\n"
            f"{RIGHTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            "На основании изложенного,\nП Р О Ш У:\n"
            f"Представить сведения о зарегистрированных за {c.debtor_full_name} и {c.spouse_full_name} "
            f"самоходных машинах и других видах техники и о сделках с ними за период с {c.period_start} "
            f"по настоящее время.\n\n"
            f"{self._footer(c)}"
        )

    def _gen_request_rosaviation(self, c: CaseContext) -> str:
        return (
            f"{self._header(c)}\n"
            f"ФЕДЕРАЛЬНОЕ АГЕНТСТВО ВОЗДУШНОГО ТРАНСПОРТА (РОСАВИАЦИЯ)\n"
            f"125993, г. Москва, Ленинградский проспект, 37, корп. 2\n\n"
            f"{self._preamble(c)}\n\n"
            f"{RIGHTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            "На основании изложенного,\nП Р О Ш У:\n"
            f"Представить сведения в отношении {c.debtor_full_name} и {c.spouse_full_name} о зарегистрированных "
            f"правах на воздушные суда, об ограничениях (обременениях), в том числе арестах, запрещениях "
            f"заключения сделок, за период с {c.period_start} по настоящее время.\n\n"
            f"{self._footer(c)}"
        )

    def _gen_request_rosgvardiya(self, c: CaseContext) -> str:
        return (
            f"{self._header(c)}\n"
            f"ГЛАВНОЕ УПРАВЛЕНИЕ РОСГВАРДИИ ПО КРАСНОДАРСКОМУ КРАЮ\n"
            f"350051, г. Краснодар\n\n"
            f"{self._preamble(c)}\n\n"
            f"{RIGHTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            "На основании изложенного,\nП Р О Ш У:\n"
            f"Представить сведения о зарегистрированном за {c.debtor_full_name} гражданском оружии "
            f"и о совершенных сделках с ним за период с {c.period_start} по настоящее время.\n\n"
            f"{self._footer(c)}"
        )

    def _gen_request_rospatent(self, c: CaseContext) -> str:
        return (
            f"{self._header(c)}\n"
            f"ФЕДЕРАЛЬНАЯ СЛУЖБА ПО ИНТЕЛЛЕКТУАЛЬНОЙ СОБСТВЕННОСТИ (РОСПАТЕНТ)\n"
            f"125993, г. Москва, Бережковская наб., 30, корп. 1\n\n"
            f"{self._preamble(c)}\n\n"
            f"{RIGHTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            "На основании изложенного,\nП Р О Ш У:\n"
            f"Представить сведения о зарегистрированных за {c.debtor_full_name} и {c.spouse_full_name} "
            f"объектах интеллектуальной собственности (патенты, товарные знаки, программы для ЭВМ) "
            f"за период с {c.period_start} по настоящее время.\n\n"
            f"{self._footer(c)}"
        )

    def _gen_request_bti(self, c: CaseContext) -> str:
        return (
            f"{self._header(c)}\n"
            f"ФГУП РОСТЕХИНВЕНТАРИЗАЦИЯ — ФЕДЕРАЛЬНОЕ БТИ\n"
            f"350049, г. Краснодар, ул. Красноармейская, 135/1\n\n"
            f"{self._preamble(c)}\n\n"
            f"{RIGHTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            "На основании изложенного,\nП Р О Ш У:\n"
            f"Представить сведения в отношении {c.debtor_full_name} и {c.spouse_full_name} о зарегистрированном "
            f"имуществе (объекты недвижимости до 1998 года, доли) за период с {c.period_start} по настоящее время.\n\n"
            f"{self._footer(c)}"
        )

    def _gen_request_rsa(self, c: CaseContext) -> str:
        return (
            f"{self._header(c)}\n"
            f"РОССИЙСКИЙ СОЮЗ АВТОСТРАХОВЩИКОВ (РСА)\n"
            f"115093, г. Москва, ул. Люсиновская, 27, стр. 16\n\n"
            f"{self._preamble(c)}\n\n"
            f"{RIGHTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            "На основании изложенного,\nП Р О Ш У:\n"
            f"Представить сведения о заключенных договорах ОСАГО в отношении {c.debtor_full_name} "
            f"и {c.spouse_full_name} за период с {c.period_start} по настоящее время.\n\n"
            f"{self._footer(c)}"
        )

    def _gen_request_migration_mvd(self, c: CaseContext) -> str:
        return (
            f"{self._header(c)}\n"
            f"УПРАВЛЕНИЕ ПО ВОПРОСАМ МИГРАЦИИ МВД РОССИИ\n\n"
            f"{self._preamble(c)}\n\n"
            f"{RIGHTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            "На основании изложенного,\nП Р О Ш У:\n"
            f"Представить сведения о заграничных паспортах, выданных {c.debtor_full_name} и {c.spouse_full_name}, "
            f"о пересечении границы за период с {c.period_start} по настоящее время.\n\n"
            f"{self._footer(c)}"
        )

    def _gen_request_depository(self, c: CaseContext) -> str:
        return (
            f"{self._header(c)}\n"
            f"ДЕПОЗИТАРИЙ (НАЦИОНАЛЬНЫЙ РАСЧЕТНЫЙ ДЕПОЗИТАРИЙ)\n\n"
            f"{self._preamble(c)}\n\n"
            f"{RIGHTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            f"{ACCOUNTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            "На основании изложенного,\nП Р О Ш У:\n"
            f"Представить сведения об открытых (закрытых) счетах депо {c.debtor_full_name} и {c.spouse_full_name}, "
            f"о ценных бумагах и об операциях с ними за период с {c.period_start} по настоящее время.\n\n"
            f"{self._footer(c)}"
        )

    def _gen_request_land(self, c: CaseContext) -> str:
        return (
            f"{self._header(c)}\n"
            f"ДЕПАРТАМЕНТ ИМУЩЕСТВЕННЫХ ОТНОШЕНИЙ КРАСНОДАРСКОГО КРАЯ (ЗЕМЕЛЬНЫЕ УЧАСТКИ)\n"
            f"350000, г. Краснодар, ул. Гимназическая, 36\n\n"
            f"{self._preamble(c)}\n\n"
            f"{RIGHTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            "На основании изложенного,\nП Р О Ш У:\n"
            f"Представить сведения о земельных участках, принадлежащих {c.debtor_full_name} и {c.spouse_full_name} "
            f"на праве собственности, аренды или ином праве, включая договоры аренды, за период с {c.period_start} "
            f"по настоящее время.\n\n"
            f"{self._footer(c)}"
        )

    def _gen_request_bailiff(self, c: CaseContext) -> str:
        return (
            f"{self._header(c)}\n"
            f"ОТДЕЛ СУДЕБНЫХ ПРИСТАВОВ (ОСП) ПО КРАСНОДАРСКОМУ КРАЮ\n"
            f"350063, г. Краснодар, ул. Красноармейская, 22\n\n"
            f"{self._preamble(c, title='УВЕДОМЛЕНИЕ')}\n\n"
            f"{BANKRUPT_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            "В соответствии со ст. 213.11 Закона о банкротстве с даты признания гражданина банкротом "
            "снимаются аресты с имущества гражданина и иные ограничения распоряжения имуществом гражданина.\n"
            "На основании изложенного,\nП Р О Ш У:\n"
            f"1. Снять аресты и иные ограничения, наложенные в рамках исполнительных производств в отношении "
            f"{c.debtor_full_name} (ИНН {c.debtor_inn}).\n"
            f"2. Представить сведения о возбужденных исполнительных производствах в отношении должника "
            f"и {c.spouse_full_name} за период с {c.period_start} по настоящее время.\n\n"
            f"{self._footer(c)}"
        )

    def _gen_request_magistrate(self, c: CaseContext) -> str:
        return (
            f"{self._header(c)}\n"
            f"МИРОВОМУ СУДЬЕ СУДЕБНОГО УЧАСТКА № 213 ТИМАШЕВСКОГО РАЙОНА\n"
            f"352708, Краснодарский край, г. Тимашевск\n\n"
            f"{self._preamble(c)}\n\n"
            f"{RIGHTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            "На основании изложенного,\nП Р О Ш У:\n"
            f"Представить сведения о судебных делах с участием {c.debtor_full_name} и {c.spouse_full_name} "
            f"(гражданские дела, вынесенные судебные акты) за период с {c.period_start} по настоящее время.\n\n"
            f"{self._footer(c)}"
        )

    def _gen_request_general_court(self, c: CaseContext) -> str:
        return (
            f"{self._header(c)}\n"
            f"В ТИМАШЕВСКИЙ РАЙОННЫЙ СУД КРАСНОДАРСКОГО КРАЯ\n"
            f"г. Тимашевск, ул. Братьев Степановых, 101\n\n"
            f"{self._preamble(c)}\n\n"
            f"{RIGHTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            "На основании изложенного,\nП Р О Ш У:\n"
            f"Представить сведения о судебных делах с участием {c.debtor_full_name} и {c.spouse_full_name} "
            f"(гражданские дела, вынесенные судебные акты) за период с {c.period_start} по настоящее время.\n\n"
            f"{self._footer(c)}"
        )

    def _gen_request_debtor(self, c: CaseContext) -> str:
        return (
            f"{self._header(c)}\n"
            f"Должник: {c.debtor_full_name}\n"
            f"{c.debtor_address}\n\n"
            f"{self._preamble(c)}\n\n"
            f"{DEBTOR_DUTY_NOTICE.format(**LEGAL_FRAMEWORK)}\n"
            f"Сокрытие имущества, имущественных прав или имущественных обязанностей, сведений о размере "
            f"имущества, месте его нахождения или иных сведений об имуществе, отчуждение или уничтожение "
            f"имущества, а также незаконное воспрепятствование деятельности финансового управляющего, "
            f"в том числе уклонение или отказ от предоставления сведений, влечет ответственность в "
            f"соответствии с законодательством Российской Федерации.\n\n"
            "На основании изложенного,\nТ Р Е Б У Ю:\n"
            f"1. Передать финансовому управляющему все банковские карты не позднее одного рабочего дня "
            f"с даты получения настоящего требования.\n"
            "2. Представить в течение пятнадцати дней сведения о составе имущества, месте нахождения "
            "имущества, составе обязательств, кредиторах, все имеющиеся документы.\n"
            "3. Обеспечить передачу финансовому управляющему имущества, составляющего конкурсную массу.\n\n"
            f"Ответ прошу продублировать по электронной почте: {c.manager_email}\n\n"
            f"Финансовый управляющий {c.manager_full_name}"
        )

    def _gen_creditor_notification(self, c: CaseContext) -> str:
        return (
            f"{self._header(c)}\n"
            f"ВСЕМ КРЕДИТОРАМ ДОЛЖНИКА\n\n"
            f"{self._preamble(c, title='УВЕДОМЛЕНИЕ')}\n\n"
            f"{BANKRUPT_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            "В соответствии со ст. 213.8 Закона о банкротстве кредиторы вправе предъявить свои требования "
            "к должнику в течение тридцати дней с даты опубликования сообщения о признании гражданина "
            "банкротом в газете «Коммерсантъ» и включения в ЕФРСБ.\n"
            "На основании изложенного,\nП Р О Ш У:\n"
            f"1. Представить финансовому управляющему сведения и документы, подтверждающие наличие и размер "
            f"задолженности {c.debtor_full_name} перед Вами.\n"
            "2. Заявить о включении требования в реестр требований кредиторов в установленном порядке.\n\n"
            f"{self._footer(c)}"
        )

    def _gen_account_closure(self, c: CaseContext) -> str:
        return (
            f"{self._header(c)}\n"
            f"В БАНК (КРЕДИТНУЮ ОРГАНИЗАЦИЮ)\n\n"
            f"{self._preamble(c)}\n\n"
            f"{BANKRUPT_NOTICE.format(**LEGAL_FRAMEWORK)}\n\n"
            f"{ACCOUNTS_NOTICE.format(**LEGAL_FRAMEWORK)}\n"
            "В соответствии со ст. 213.11 Закона о банкротстве с даты признания гражданина банкротом "
            "все права на счета и вклады реализуются только финансовым управляющим.\n"
            "На основании изложенного,\nП Р О Ш У:\n"
            f"1. Представить сведения об открытых (закрытых) счетах, вкладах, остатках денежных средств "
            f"{c.debtor_full_name} и {c.spouse_full_name} за период с {c.period_start} по настоящее время.\n"
            f"2. Закрыть счета {c.debtor_full_name} и перечислить остатки на основной счет должника.\n\n"
            f"{self._footer(c)}"
        )

    def _gen_completion_petition(self, c: CaseContext) -> str:
        return (
            f"В {c.court_name}\n"
            f"350063, г. Краснодар, ул. Постовая, 32\n\n"
            f"Финансовый управляющий\n{c.manager_full_name}\n{c.manager_address}\n\n"
            f"{c.date_today}г.\n"
            f"ХОДАТАЙСТВО О ЗАВЕРШЕНИИ ПРОЦЕДУРЫ БАНКРОТСТВА\n\n"
            f"Решением {c.court_name} от {c.court_decision_date} по делу № {c.case_number} {c.debtor_full_name} "
            f"признан несостоятельным (банкротом), введена процедура реализации имущества гражданина.\n"
            f"Определением суда от «__» ________ 20__ г. применены правила параграфа 4 главы X Закона "
            f"о банкротстве в связи со смертью должника.\n\n"
            f"В ходе процедуры финансовым управляющим выполнены все мероприятия:\n"
            f"1. Направлены запросы в регистрирующие органы и кредитные организации.\n"
            f"2. Проведена инвентаризация и оценка имущества должника, составляющего конкурсную массу.\n"
            f"3. Включены требования кредиторов в реестр требований кредиторов.\n"
            f"4. Проведены мероприятия по реализации имущества должника.\n"
            f"5. Составлен отчет финансового управляющего о своей деятельности и результатах проведения "
            f"процедуры.\n\n"
            "На основании изложенного, руководствуясь ст. 213.28 Закона о банкротстве,\n\n"
            "П Р О Ш У:\n"
            f"Завершить процедуру реализации имущества {c.debtor_full_name} "
            f"и освободить его от дальнейшего исполнения требований кредиторов.\n\n"
            f"Финансовый управляющий {c.manager_full_name}"
        )


class DocumentGenerator:
    """Унифицированный генератор документов (шаблон + LLM/RAG)."""

    def __init__(self) -> None:
        self.template_generator = DocumentTemplateGenerator()
        self._ai_enabled = settings.FF_ENABLE_AI_ANALYSIS

    @property
    def document_types(self) -> dict[str, str]:
        return self.template_generator.DOCUMENT_TYPES

    def generate(self, doc_type: str, context: CaseContext, rag_chunks: list[KnowledgeChunk] | None = None) -> str:
        """Генерирует документ.

        При включённом FF_ENABLE_AI_ANALYSIS дополняет результат RAG-контекстом.
        """
        base = self.template_generator.generate(doc_type, context)

        if self._ai_enabled and rag_chunks:
            sources = "\n".join(
                f"- {ch.source} ({ch.case_id})" for ch in rag_chunks[:5]
            )
            base += (
                "\n\n---\n"
                "ИСТОЧНИКИ ДЛЯ ПРОВЕРКИ (RAG):\n"
                f"{sources}\n"
                "Документ сгенерирован на основе шаблона кейса А32-37431/2025. "
                "Перед отправкой требуется проверка юристом."
            )
        return base

    def generate_with_rag(
        self,
        doc_type: str,
        context: CaseContext,
        search: "RagSearch | None" = None,
        query: str | None = None,
    ) -> str:
        """Генерация с RAG-подсказками из базы знаний."""
        from app.ai.rag_search import RagSearch as _RagSearch
        chunks: list[KnowledgeChunk] = []
        if isinstance(search, _RagSearch) and query:
            chunks = search.query(query, top_k=5)
        return self.generate(doc_type, context, rag_chunks=chunks)