"""
Knowledge Base for electrical, plumbing, and general repair work.

This module contains:
- Common problems and solutions
- Step-by-step repair instructions
- Required materials and tools
- Safety guidelines
- Troubleshooting guides
- Cost estimation data
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class SkillLevel(Enum):
    """Required skill level for a task."""
    BASIC = "basic"           # Simple tasks, beginner-friendly
    INTERMEDIATE = "intermediate"  # Requires some experience
    ADVANCED = "advanced"     # Complex tasks, requires expertise
    EXPERT = "expert"         # Highly specialized, certification may be required


@dataclass
class RepairSolution:
    """A solution for a specific problem."""
    problem_id: str
    problem_name: str
    category: str
    description: str
    skill_level: SkillLevel
    estimated_time_hours: float
    required_tools: List[str]
    required_materials: List[Dict[str, Any]]
    safety_precautions: List[str]
    step_by_step_instructions: List[str]
    common_mistakes: List[str]
    troubleshooting_tips: List[str]
    estimated_cost_range: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "problem_id": self.problem_id,
            "problem_name": self.problem_name,
            "category": self.category,
            "description": self.description,
            "skill_level": self.skill_level.value,
            "estimated_time_hours": self.estimated_time_hours,
            "required_tools": self.required_tools,
            "required_materials": self.required_materials,
            "safety_precautions": self.safety_precautions,
            "step_by_step_instructions": self.step_by_step_instructions,
            "common_mistakes": self.common_mistakes,
            "troubleshooting_tips": self.troubleshooting_tips,
            "estimated_cost_range": self.estimated_cost_range
        }


class KnowledgeBase:
    """
    Knowledge base containing repair solutions and guidelines.
    
    This serves as the AI's knowledge source for:
    - Identifying problems
    - Generating repair instructions
    - Estimating costs and time
    - Providing safety guidance
    """
    
    def __init__(self):
        self.solutions: Dict[str, RepairSolution] = {}
        self._initialize_electrical_knowledge()
        self._initialize_plumbing_knowledge()
        self._initialize_appliance_knowledge()
        
    def _initialize_electrical_knowledge(self):
        """Initialize electrical repair knowledge."""
        
        # Non-working outlet
        self.solutions["elec_outlet_not_working"] = RepairSolution(
            problem_id="elec_outlet_not_working",
            problem_name="Розетка не работает",
            category="electrical",
            description="Электрическая розетка не подает питание на подключенные устройства",
            skill_level=SkillLevel.INTERMEDIATE,
            estimated_time_hours=0.5,
            required_tools=[
                "Мультиметр",
                "Индикаторная отвертка",
                "Отвертка крестовая",
                "Отвертка плоская",
                "Плоскогубцы",
                "Изолента"
            ],
            required_materials=[
                {"name": "Розетка (при необходимости замены)", "quantity": 1, "unit": "шт", "cost_rub": 150},
                {"name": "Изолента", "quantity": 1, "unit": "рулон", "cost_rub": 50}
            ],
            safety_precautions=[
                "ОБЯЗАТЕЛЬНО отключите электропитание на щитке перед началом работ",
                "Проверьте отсутствие напряжения индикаторной отверткой",
                "Работайте в сухих перчатках на резиновой основе",
                "Не прикасайтесь к проводам голыми руками",
                "Убедитесь, что пол сухой"
            ],
            step_by_step_instructions=[
                "Отключите автомат на электрощитке для данной линии",
                "Проверьте индикаторной отверткой отсутствие напряжения в розетке",
                "Снимите декоративную панель розетки",
                "Открутите винты крепления механизма розетки",
                "Аккуратно извлеките механизм из подрозетника",
                "Проверьте надежность подключения проводов к клеммам",
                "Если контакты окислены - зачистите их",
                "Если розетка повреждена - замените на новую",
                "Подключите провода согласно маркировке (фаза, ноль, земля)",
                "Закрепите механизм в подрозетнике",
                "Установите декоративную панель",
                "Включите автомат на щитке",
                "Проверьте работу розетки тестером или подключением нагрузки"
            ],
            common_mistakes=[
                "Работа без отключения электропитания",
                "Неправильное подключение фазы и нуля",
                "Слабая затяжка клемм - приводит к искрению",
                "Игнорирование заземляющего провода",
                "Использование розетки не подходящей мощности"
            ],
            troubleshooting_tips=[
                "Если розетка все равно не работает - проверьте автомат на щитке",
                "Проверьте другие розетки в той же комнате - возможна общая проблема",
                "Если сработал автомат - возможно короткое замыкание, требуется детальная диагностика",
                "Если розетка горячая - немедленно отключите питание, требуется замена"
            ],
            estimated_cost_range={
                "min": 800,
                "max": 1500,
                "materials": 200
            }
        )
        
        # Light switch not working
        self.solutions["elec_switch_not_working"] = RepairSolution(
            problem_id="elec_switch_not_working",
            problem_name="Выключатель не включает свет",
            category="electrical",
            description="Выключатель не управляет освещением",
            skill_level=SkillLevel.INTERMEDIATE,
            estimated_time_hours=0.5,
            required_tools=[
                "Индикаторная отвертка",
                "Отвертка крестовая",
                "Отвертка плоская",
                "Мультиметр",
                "Плоскогубцы"
            ],
            required_materials=[
                {"name": "Выключатель (при замене)", "quantity": 1, "unit": "шт", "cost_rub": 120},
                {"name": "Изолента", "quantity": 1, "unit": "рулон", "cost_rub": 50}
            ],
            safety_precautions=[
                "Отключите автомат освещения на щитке",
                "Проверьте отсутствие напряжения",
                "Не работайте мокрыми руками"
            ],
            step_by_step_instructions=[
                "Отключите автомат освещения",
                "Снимите клавишу выключателя",
                "Открутите рамку выключателя",
                "Извлеките механизм из подрозетника",
                "Проверьте надежность контактов",
                "При необходимости замените выключатель",
                "Соберите в обратном порядке",
                "Включите автомат и проверьте работу"
            ],
            common_mistakes=[
                "Путаница с проводами при подключении",
                "Перетягивание винтов крепления",
                "Использование выключателя неподходящей мощности"
            ],
            troubleshooting_tips=[
                "Проверьте лампочку - возможно проблема в ней",
                "Проверьте патрон светильника",
                "Если выключатель теплый - требуется замена"
            ],
            estimated_cost_range={
                "min": 700,
                "max": 1200,
                "materials": 170
            }
        )
        
        # Circuit breaker tripping
        self.solutions["elec_breaker_tripping"] = RepairSolution(
            problem_id="elec_breaker_tripping",
            problem_name="Автомат выбивает",
            category="electrical",
            description="Автоматический выключатель постоянно отключается",
            skill_level=SkillLevel.ADVANCED,
            estimated_time_hours=1.5,
            required_tools=[
                "Мультиметр",
                "Токовые клещи",
                "Отвертки",
                "Индикаторная отвертка"
            ],
            required_materials=[
                {"name": "Автоматический выключатель (при замене)", "quantity": 1, "unit": "шт", "cost_rub": 300}
            ],
            safety_precautions=[
                "Отключите вводной автомат перед работой со щитком",
                "Работайте в диэлектрических перчатках",
                "Не включайте автомат при наличии короткого замыкания"
            ],
            step_by_step_instructions=[
                "Отключите вводной автомат",
                "Отключите все приборы на проблемной линии",
                "Включите автомат - если срабатывает сразу, проблема в проводке",
                "Если не срабатывает, подключайте приборы по одному",
                "Определите проблемный прибор или участок проводки",
                "При перегрузке - распределите нагрузку или замените автомат на более мощный",
                "При коротком замыкании - найдите и устраните место КЗ",
                "Проверьте затяжку контактов в щитке"
            ],
            common_mistakes=[
                "Установка автомата большего номинала без проверки проводки",
                "Игнорирование причины срабатывания",
                "Многократное включение при КЗ - может привести к пожару"
            ],
            troubleshooting_tips=[
                "Если автомат теплый - возможна перегрузка или плохой контакт",
                "Если срабатывает при включении определенного прибора - проблема в приборе",
                "Если срабатывает во влажную погоду - возможна утечка на землю"
            ],
            estimated_cost_range={
                "min": 1500,
                "max": 5000,
                "materials": 300
            }
        )
        
        # Chandelier installation
        self.solutions["elec_chandelier_install"] = RepairSolution(
            problem_id="elec_chandelier_install",
            problem_name="Установка люстры",
            category="electrical",
            description="Монтаж и подключение потолочной люстры",
            skill_level=SkillLevel.INTERMEDIATE,
            estimated_time_hours=1.0,
            required_tools=[
                "Стремянка",
                "Отвертки",
                "Плоскогубцы",
                "Индикаторная отвертка",
                "Перфоратор (при необходимости)",
                "Клеммники или колпачки СИЗ"
            ],
            required_materials=[
                {"name": "Люстра", "quantity": 1, "unit": "шт", "cost_rub": 0},  # Клиент предоставляет
                {"name": "Клеммники", "quantity": 3, "unit": "шт", "cost_rub": 30},
                {"name": "Дюбели и крюк (если нужно)", "quantity": 1, "unit": "компл", "cost_rub": 100}
            ],
            safety_precautions=[
                "Отключите автомат освещения",
                "Проверьте отсутствие напряжения",
                "Используйте устойчивую стремянку",
                "Попросите помощника придержать люстру при монтаже"
            ],
            step_by_step_instructions=[
                "Отключите электропитание",
                "Демонтируйте старую люстру (если есть)",
                "Проверьте надежность крепления крюка или планки",
                "Определите назначение проводов (фаза, ноль, заземление)",
                "Подключите провода люстры к проводам на потолке через клеммники",
                "Закрепите люстру на крюке или планке",
                "Установите лампочки",
                "Включите питание и проверьте работу"
            ],
            common_mistakes=[
                "Неправильное подключение проводов - люстра не работает",
                "Ненадежное крепление - люстра может упасть",
                "Превышение допустимой мощности ламп"
            ],
            troubleshooting_tips=[
                "Если не включается - проверьте правильность подключения фазы",
                "Если работает только часть ламп - проверьте двухклавишный выключатель",
                "Если мигает - проверьте контакты"
            ],
            estimated_cost_range={
                "min": 1200,
                "max": 2500,
                "materials": 130
            }
        )
        
    def _initialize_plumbing_knowledge(self):
        """Initialize plumbing repair knowledge."""
        
        # Leaking faucet
        self.solutions["plumb_faucet_leak"] = RepairSolution(
            problem_id="plumb_faucet_leak",
            problem_name="Течет кран",
            category="plumbing",
            description="Капает или течет вода из крана",
            skill_level=SkillLevel.BASIC,
            estimated_time_hours=0.5,
            required_tools=[
                "Разводной ключ",
                "Плоскогубцы",
                "Отвертка",
                "Тряпка или ведро"
            ],
            required_materials=[
                {"name": "Прокладка или картридж", "quantity": 1, "unit": "шт", "cost_rub": 150},
                {"name": "Уплотнительная лента", "quantity": 1, "unit": "моток", "cost_rub": 50}
            ],
            safety_precautions=[
                "Перекройте воду на кране или стояке",
                "Подготовьте тряпки для вытирания воды",
                "Будьте аккуратны с керамическими деталями"
            ],
            step_by_step_instructions=[
                "Перекройте подачу воды",
                "Откройте кран для сброса остаточного давления",
                "Снимите декоративную заглушку на ручке крана",
                "Открутите винт крепления ручки",
                "Снимите ручку крана",
                "Открутите буксу или картридж (в зависимости от типа крана)",
                "Замените прокладку или картридж",
                "Соберите кран в обратном порядке",
                "Откройте воду и проверьте отсутствие течи"
            ],
            common_mistakes=[
                "Сильное затягивание - можно сорвать резьбу",
                "Неправильный выбор прокладки или картриджа",
                "Повреждение хромированных поверхностей инструментом"
            ],
            troubleshooting_tips=[
                "Если течь продолжается - проверьте правильность установки прокладки",
                "Если течь из-под гайки - замените уплотнение",
                "Если кран старый - возможно проще заменить целиком"
            ],
            estimated_cost_range={
                "min": 600,
                "max": 1500,
                "materials": 200
            }
        )
        
        # Clogged drain
        self.solutions["plumb_drain_clog"] = RepairSolution(
            problem_id="plumb_drain_clog",
            problem_name="Засор слива",
            category="plumbing",
            description="Вода плохо уходит или не уходит совсем",
            skill_level=SkillLevel.BASIC,
            estimated_time_hours=1.0,
            required_tools=[
                "Вантуз",
                "Сантехнический трос",
                "Разводной ключ",
                "Ведро",
                "Тряпки"
            ],
            required_materials=[
                {"name": "Средство для прочистки труб (опционально)", "quantity": 1, "unit": "бутылка", "cost_rub": 200}
            ],
            safety_precautions=[
                "Используйте перчатки при работе с химическими средствами",
                "Подготовьте ведро для сбора воды",
                "Обеспечьте вентиляцию при использовании химии"
            ],
            step_by_step_instructions=[
                "Попробуйте прочистить вантузом - создайте вакуум и резко выдерните",
                "Если не помогло - открутите сифон под раковиной",
                "Слейте воду в ведро",
                "Прочистите сифон от загрязнений",
                "Если засор глубже - используйте сантехнический трос",
                "Вводите трос вращательными движениями",
                "После прочистки промойте трубу горячей водой",
                "Установите сифон на место",
                "Проверьте герметичность соединений"
            ],
            common_mistakes=[
                "Использование слишком агрессивной химии - можно повредить трубы",
                "Неаккуратное обращение с тросом - можно повредить трубы",
                "Потеря прокладок при снятии сифона"
            ],
            troubleshooting_tips=[
                "Если засоры частые - установите решетку на слив",
                "Периодически промывайте трубы кипятком с содой",
                "Если не помогает - возможно проблема в стояке, нужна управляющая компания"
            ],
            estimated_cost_range={
                "min": 800,
                "max": 2000,
                "materials": 200
            }
        )
        
        # Toilet running constantly
        self.solutions["plumb_toilet_running"] = RepairSolution(
            problem_id="plumb_toilet_running",
            problem_name="Унитаз постоянно набирает воду",
            category="plumbing",
            description="Бачок унитаза постоянно подтекает или набирает воду",
            skill_level=SkillLevel.BASIC,
            estimated_time_hours=0.5,
            required_tools=[
                "Плоскогубцы",
                "Разводной ключ",
                "Отвертка"
            ],
            required_materials=[
                {"name": "Прокладка или мембрана поплавкового клапана", "quantity": 1, "unit": "шт", "cost_rub": 100},
                {"name": "Арматура бачка (при полной замене)", "quantity": 1, "unit": "компл", "cost_rub": 600}
            ],
            safety_precautions=[
                "Перекройте воду на подводке к бачку",
                "Слейте воду из бачка",
                "Подготовьте тряпки"
            ],
            step_by_step_instructions=[
                "Перекройте воду",
                "Слейте воду из бачка",
                "Снимите крышку бачка",
                "Проверьте уровень поплавка - отрегулируйте если нужно",
                "Проверьте запорную мембрану сливного клапана",
                "Замените поврежденные прокладки или мембраны",
                "Проверьте перелив - не должен быть ниже уровня воды",
                "Соберите бачок",
                "Откройте воду и проверьте работу"
            ],
            common_mistakes=[
                "Неправильная регулировка поплавка",
                "Повреждение хрупких пластиковых деталей",
                "Потеря мелких деталей при разборке"
            ],
            troubleshooting_tips=[
                "Если вода подтекает в чашу - проблема в сливном клапане",
                "Если бачок переполняется - проблема в поплавковом механизме",
                "Старую арматуру лучше заменить целиком"
            ],
            estimated_cost_range={
                "min": 500,
                "max": 1500,
                "materials": 700
            }
        )
        
    def _initialize_appliance_knowledge(self):
        """Initialize appliance repair knowledge."""
        
        # Washing machine not draining
        self.solutions["appl_washer_not_drain"] = RepairSolution(
            problem_id="appl_washer_not_drain",
            problem_name="Стиральная машина не сливает воду",
            category="appliances",
            description="Вода остается в барабане после стирки",
            skill_level=SkillLevel.INTERMEDIATE,
            estimated_time_hours=1.0,
            required_tools=[
                "Плоскогубцы",
                "Отвертка",
                "Тазик или ведро",
                "Фонарик"
            ],
            required_materials=[
                {"name": "Помпа (при необходимости)", "quantity": 1, "unit": "шт", "cost_rub": 1200}
            ],
            safety_precautions=[
                "Отключите машину от электросети",
                "Перекройте воду",
                "Подготовьте емкость для воды",
                "Будьте готовы к выливанию воды"
            ],
            step_by_step_instructions=[
                "Отключите машину от сети и воды",
                "Найдите фильтр сливного насоса (обычно внизу спереди)",
                "Подставьте тазик",
                "Аккуратно открутите крышку фильтра",
                "Слейте воду и извлеките фильтр",
                "Очистите фильтр от мусора, волос, мелких предметов",
                "Проверьте сливной шланг на перегибы и засоры",
                "Установите фильтр обратно",
                "Проверьте работу на коротком цикле полоскания"
            ],
            common_mistakes=[
                "Потеря или повреждение резинового уплотнителя фильтра",
                "Неполное закручивание фильтра - будет течь",
                "Проверка без подставленной емкости - потоп"
            ],
            troubleshooting_tips=[
                "Если после чистки не работает - проблема в насосе",
                "Проверьте программу - некоторые режимы завершаются с водой",
                "Если насос гудит но не качает - возможно заклинило крыльчатку"
            ],
            estimated_cost_range={
                "min": 1000,
                "max": 3500,
                "materials": 1200
            }
        )
        
    def find_solution(
        self,
        problem_description: str,
        category: Optional[str] = None
    ) -> Optional[RepairSolution]:
        """
        Find best matching solution for a problem.
        
        Args:
            problem_description: Description of the problem
            category: Optional category hint
            
        Returns:
            Best matching RepairSolution or None
        """
        desc_lower = problem_description.lower()
        
        # Keyword matching to find relevant solutions
        matches: List[Tuple[str, float]] = []
        
        for solution_id, solution in self.solutions.items():
            # Filter by category if provided
            if category and solution.category != category:
                continue
                
            # Calculate relevance score
            score = 0.0
            
            # Check problem name match
            if any(word in desc_lower for word in solution.problem_name.lower().split()):
                score += 2.0
                
            # Check description match
            if any(word in desc_lower for word in solution.description.lower().split()):
                score += 1.0
                
            if score > 0:
                matches.append((solution_id, score))
                
        if matches:
            # Return solution with highest score
            best_match = max(matches, key=lambda x: x[1])
            return self.solutions[best_match[0]]
            
        return None
        
    def get_solutions_by_category(self, category: str) -> List[RepairSolution]:
        """Get all solutions for a category."""
        return [s for s in self.solutions.values() if s.category == category]
        
    def get_solution_by_id(self, problem_id: str) -> Optional[RepairSolution]:
        """Get a specific solution by ID."""
        return self.solutions.get(problem_id)
        
    def generate_job_instructions(
        self,
        solution: RepairSolution,
        client_specifics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate complete job instructions for a master.
        
        Args:
            solution: The repair solution to use
            client_specifics: Specific details from client
            
        Returns:
            Structured job instructions
        """
        instructions = {
            "job_title": solution.problem_name,
            "category": solution.category,
            "skill_level_required": solution.skill_level.value,
            "estimated_duration": solution.estimated_time_hours,
            "safety_first": solution.safety_precautions,
            "required_tools": solution.required_tools,
            "materials_to_bring": solution.required_materials,
            "step_by_step": solution.step_by_step_instructions,
            "common_mistakes_to_avoid": solution.common_mistakes,
            "troubleshooting": solution.troubleshooting_tips,
            "estimated_cost": solution.estimated_cost_range,
            "client_notes": client_specifics.get("notes") if client_specifics else None,
            "urgency": client_specifics.get("urgency") if client_specifics else "normal"
        }
        
        return instructions
