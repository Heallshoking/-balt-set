"""
Computer Vision Service for analyzing images and videos of problems.

This module handles:
- Image analysis to identify equipment and components
- Problem severity assessment from visual cues
- Safety hazard detection
- Equipment/component recognition
- Damage assessment
- Video analysis for detailed diagnostics
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
import base64
from datetime import datetime


class ProblemSeverity(Enum):
    """Severity levels for identified problems."""
    CRITICAL = "critical"      # Immediate danger, requires urgent attention
    SEVERE = "severe"          # Serious issue, needs prompt repair
    MODERATE = "moderate"      # Standard repair needed
    MINOR = "minor"           # Small issue, low priority
    COSMETIC = "cosmetic"     # Aesthetic issue only


class SafetyHazard(Enum):
    """Types of safety hazards that can be detected."""
    ELECTRICAL_FIRE_RISK = "electrical_fire_risk"
    WATER_DAMAGE = "water_damage"
    EXPOSED_WIRING = "exposed_wiring"
    GAS_LEAK_SIGNS = "gas_leak_signs"
    STRUCTURAL_DAMAGE = "structural_damage"
    MOLD_GROWTH = "mold_growth"
    NONE = "none"


@dataclass
class VisualAnalysisResult:
    """Result of visual analysis."""
    problem_category: str
    detected_components: List[str]
    problem_description: str
    severity: ProblemSeverity
    safety_hazards: List[SafetyHazard]
    estimated_complexity: str  # simple, medium, complex
    confidence_score: float
    recommendations: List[str]
    required_tools: List[str]
    requires_expert: bool
    analysis_timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "problem_category": self.problem_category,
            "detected_components": self.detected_components,
            "problem_description": self.problem_description,
            "severity": self.severity.value,
            "safety_hazards": [h.value for h in self.safety_hazards],
            "estimated_complexity": self.estimated_complexity,
            "confidence_score": self.confidence_score,
            "recommendations": self.recommendations,
            "required_tools": self.required_tools,
            "requires_expert": self.requires_expert,
            "analysis_timestamp": self.analysis_timestamp
        }


class VisionService:
    """
    Computer Vision service for analyzing problem images and videos.
    
    In production, this would integrate with:
    - OpenAI Vision API (GPT-4 Vision)
    - Google Cloud Vision API
    - Custom trained models for electrical/plumbing components
    - YOLOv8 for object detection
    
    For MVP, we use rule-based heuristics and pattern matching.
    """
    
    def __init__(self):
        # Component recognition patterns (in production: trained ML models)
        self.electrical_components = {
            "outlet": ["розетка", "розетки", "socket"],
            "switch": ["выключатель", "switch"],
            "circuit_breaker": ["автомат", "автоматический выключатель", "breaker"],
            "wire": ["провод", "проводка", "кабель", "wire"],
            "light_fixture": ["светильник", "лампа", "люстра", "light"],
            "electrical_panel": ["щиток", "электрощит", "panel"],
            "junction_box": ["распаечная коробка", "junction box"]
        }
        
        self.plumbing_components = {
            "faucet": ["кран", "смеситель", "faucet"],
            "pipe": ["труба", "трубопровод", "pipe"],
            "toilet": ["унитаз", "toilet"],
            "sink": ["раковина", "мойка", "sink"],
            "bathtub": ["ванна", "bathtub"],
            "water_heater": ["бойлер", "водонагреватель", "heater"],
            "drain": ["слив", "канализация", "drain"],
            "valve": ["вентиль", "кран", "valve"]
        }
        
        # Safety indicators (visual patterns to look for)
        self.safety_indicators = {
            SafetyHazard.ELECTRICAL_FIRE_RISK: [
                "black marks", "burn marks", "scorch", "charred",
                "черные пятна", "следы горения", "обугленный"
            ],
            SafetyHazard.WATER_DAMAGE: [
                "water stain", "wet", "puddle", "leak",
                "пятна воды", "влага", "лужа", "протечка"
            ],
            SafetyHazard.EXPOSED_WIRING: [
                "exposed wire", "bare wire", "hanging wire",
                "оголенный провод", "висящий провод"
            ],
            SafetyHazard.MOLD_GROWTH: [
                "mold", "mildew", "black spots",
                "плесень", "грибок", "черные пятна"
            ]
        }
        
    def analyze_image(
        self,
        image_url: str,
        context: Optional[Dict[str, Any]] = None
    ) -> VisualAnalysisResult:
        """
        Analyze a single image to identify problems.
        
        Args:
            image_url: URL or path to the image
            context: Optional context (problem description, category hint)
            
        Returns:
            VisualAnalysisResult with detected information
        """
        # In production: call OpenAI Vision API or custom model
        # For MVP: return structured analysis based on context
        
        # Extract hints from context
        category_hint = context.get("category") if context else None
        description = context.get("description", "") if context else ""
        
        # Determine problem category
        category = self._determine_category(description, category_hint)
        
        # Detect components based on category
        components = self._detect_components(description, category)
        
        # Assess severity
        severity = self._assess_severity(description)
        
        # Detect safety hazards
        hazards = self._detect_hazards(description)
        
        # Estimate complexity
        complexity = self._estimate_complexity(category, severity, len(components))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(category, severity, hazards)
        
        # Determine required tools
        tools = self._determine_required_tools(category, components)
        
        # Check if expert required
        requires_expert = severity in [ProblemSeverity.CRITICAL, ProblemSeverity.SEVERE]
        
        # Generate problem description
        problem_desc = self._generate_problem_description(category, components, severity)
        
        return VisualAnalysisResult(
            problem_category=category,
            detected_components=components,
            problem_description=problem_desc,
            severity=severity,
            safety_hazards=hazards,
            estimated_complexity=complexity,
            confidence_score=0.75,  # Placeholder confidence
            recommendations=recommendations,
            required_tools=tools,
            requires_expert=requires_expert,
            analysis_timestamp=datetime.utcnow().isoformat()
        )
        
    def analyze_images(
        self,
        image_urls: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze multiple images and aggregate results.
        
        Args:
            image_urls: List of image URLs
            context: Optional context information
            
        Returns:
            Aggregated analysis results
        """
        if not image_urls:
            return {
                "error": "No images provided",
                "analysis": None
            }
            
        # Analyze each image
        analyses = [self.analyze_image(url, context) for url in image_urls]
        
        # Aggregate results
        # Take the most severe assessment
        max_severity = max(analyses, key=lambda a: list(ProblemSeverity).index(a.severity))
        
        # Combine all detected components
        all_components = list(set(sum([a.detected_components for a in analyses], [])))
        
        # Combine all hazards
        all_hazards = list(set(sum([a.safety_hazards for a in analyses], [])))
        
        # Take highest complexity
        complexity_order = ["simple", "medium", "complex"]
        max_complexity = max(analyses, key=lambda a: complexity_order.index(a.estimated_complexity))
        
        # Combine recommendations
        all_recommendations = list(set(sum([a.recommendations for a in analyses], [])))
        
        # Combine tools
        all_tools = list(set(sum([a.required_tools for a in analyses], [])))
        
        return {
            "total_images": len(image_urls),
            "primary_category": max_severity.problem_category,
            "detected_components": all_components,
            "severity": max_severity.severity.value,
            "safety_hazards": [h.value for h in all_hazards],
            "estimated_complexity": max_complexity.estimated_complexity,
            "recommendations": all_recommendations,
            "required_tools": all_tools,
            "requires_expert": any(a.requires_expert for a in analyses),
            "individual_analyses": [a.to_dict() for a in analyses],
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
    def analyze_video(
        self,
        video_url: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze video for detailed diagnostics.
        
        In production: extract key frames and analyze sequentially
        For MVP: treat similar to image analysis
        """
        # In production: use video processing to extract frames
        # Analyze multiple frames to understand the problem better
        
        # For MVP: return similar structure to image analysis
        return {
            "video_url": video_url,
            "analysis_type": "video",
            "message": "Video analysis requires frame extraction and sequential analysis",
            "recommendation": "Please provide photos of the problem area for faster analysis",
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
    def _determine_category(self, description: str, hint: Optional[str] = None) -> str:
        """Determine problem category from description and hint."""
        if hint:
            return hint
            
        description_lower = description.lower()
        
        # Check for electrical keywords
        electrical_keywords = ["розетка", "выключатель", "свет", "провод", "автомат", "электри"]
        if any(kw in description_lower for kw in electrical_keywords):
            return "electrical"
            
        # Check for plumbing keywords
        plumbing_keywords = ["кран", "вода", "труба", "унитаз", "течь", "сантехник"]
        if any(kw in description_lower for kw in plumbing_keywords):
            return "plumbing"
            
        # Check for appliances
        appliance_keywords = ["стиральная", "холодильник", "бойлер", "плита"]
        if any(kw in description_lower for kw in appliance_keywords):
            return "appliances"
            
        # Default to electrical
        return "electrical"
        
    def _detect_components(self, description: str, category: str) -> List[str]:
        """Detect specific components mentioned or visible."""
        components = []
        description_lower = description.lower()
        
        if category == "electrical":
            for component, keywords in self.electrical_components.items():
                if any(kw in description_lower for kw in keywords):
                    components.append(component)
        elif category == "plumbing":
            for component, keywords in self.plumbing_components.items():
                if any(kw in description_lower for kw in keywords):
                    components.append(component)
                    
        return components if components else ["unidentified_component"]
        
    def _assess_severity(self, description: str) -> ProblemSeverity:
        """Assess problem severity from description."""
        description_lower = description.lower()
        
        # Critical indicators
        critical_keywords = ["искрит", "горит", "дым", "удар током", "затопление", "фонтан"]
        if any(kw in description_lower for kw in critical_keywords):
            return ProblemSeverity.CRITICAL
            
        # Severe indicators
        severe_keywords = ["течет сильно", "не работает совсем", "запах", "треснул"]
        if any(kw in description_lower for kw in severe_keywords):
            return ProblemSeverity.SEVERE
            
        # Minor indicators
        minor_keywords = ["слегка", "немного", "иногда", "периодически"]
        if any(kw in description_lower for kw in minor_keywords):
            return ProblemSeverity.MINOR
            
        # Default to moderate
        return ProblemSeverity.MODERATE
        
    def _detect_hazards(self, description: str) -> List[SafetyHazard]:
        """Detect potential safety hazards."""
        hazards = []
        description_lower = description.lower()
        
        for hazard, keywords in self.safety_indicators.items():
            if any(kw in description_lower for kw in keywords):
                hazards.append(hazard)
                
        return hazards if hazards else [SafetyHazard.NONE]
        
    def _estimate_complexity(
        self,
        category: str,
        severity: ProblemSeverity,
        component_count: int
    ) -> str:
        """Estimate repair complexity."""
        # Critical issues are always complex
        if severity == ProblemSeverity.CRITICAL:
            return "complex"
            
        # Multiple components = more complex
        if component_count > 2:
            return "complex"
            
        # Severe issues are medium to complex
        if severity == ProblemSeverity.SEVERE:
            return "medium"
            
        # Minor issues are simple
        if severity == ProblemSeverity.MINOR:
            return "simple"
            
        # Default to medium
        return "medium"
        
    def _generate_recommendations(
        self,
        category: str,
        severity: ProblemSeverity,
        hazards: List[SafetyHazard]
    ) -> List[str]:
        """Generate safety and action recommendations."""
        recommendations = []
        
        # Critical severity recommendations
        if severity == ProblemSeverity.CRITICAL:
            if category == "electrical":
                recommendations.append("Немедленно отключите электропитание на щитке")
                recommendations.append("Не пользуйтесь поврежденными приборами")
            elif category == "plumbing":
                recommendations.append("Перекройте основной водопроводный кран")
                recommendations.append("Уберите ценные вещи от места протечки")
                
        # Hazard-specific recommendations
        if SafetyHazard.ELECTRICAL_FIRE_RISK in hazards:
            recommendations.append("Отключите электричество в помещении")
            recommendations.append("Не включайте приборы до ремонта")
            
        if SafetyHazard.WATER_DAMAGE in hazards:
            recommendations.append("Вытрите воду для предотвращения повреждений")
            recommendations.append("Обеспечьте вентиляцию помещения")
            
        if SafetyHazard.EXPOSED_WIRING in hazards:
            recommendations.append("Не прикасайтесь к оголенным проводам")
            recommendations.append("Ограничьте доступ к опасной зоне")
            
        # Default recommendation
        if not recommendations:
            recommendations.append("Дождитесь прибытия мастера для безопасного ремонта")
            
        return recommendations
        
    def _determine_required_tools(self, category: str, components: List[str]) -> List[str]:
        """Determine which tools are likely needed."""
        tools = []
        
        if category == "electrical":
            tools.extend([
                "Мультиметр",
                "Отвертки",
                "Плоскогубцы",
                "Изолента"
            ])
            
            if "wire" in components or "проводка" in str(components):
                tools.append("Кусачки")
                tools.append("Стриппер для проводов")
                
            if "outlet" in components or "розетка" in str(components):
                tools.append("Индикаторная отвертка")
                
        elif category == "plumbing":
            tools.extend([
                "Разводной ключ",
                "Плоскогубцы",
                "Уплотнительная лента"
            ])
            
            if "pipe" in components or "труба" in str(components):
                tools.append("Труборез")
                tools.append("Паяльник для труб")
                
            if "drain" in components or "засор" in str(components):
                tools.append("Вантуз")
                tools.append("Трос сантехнический")
                
        return tools
        
    def _generate_problem_description(
        self,
        category: str,
        components: List[str],
        severity: ProblemSeverity
    ) -> str:
        """Generate human-readable problem description."""
        category_names = {
            "electrical": "электрической системы",
            "plumbing": "сантехники",
            "appliances": "бытовой техники",
            "renovation": "отделки"
        }
        
        severity_descriptions = {
            ProblemSeverity.CRITICAL: "критическая неисправность",
            ProblemSeverity.SEVERE: "серьезная проблема",
            ProblemSeverity.MODERATE: "неисправность",
            ProblemSeverity.MINOR: "незначительная проблема",
            ProblemSeverity.COSMETIC: "косметический дефект"
        }
        
        category_name = category_names.get(category, "системы")
        severity_desc = severity_descriptions.get(severity, "проблема")
        
        if components and components[0] != "unidentified_component":
            component_list = ", ".join(components[:3])  # First 3 components
            return f"Обнаружена {severity_desc} {category_name}: проблема с {component_list}"
        else:
            return f"Обнаружена {severity_desc} {category_name}"
            
    def get_analysis_confidence(self, analysis: VisualAnalysisResult) -> Dict[str, Any]:
        """
        Get confidence metrics for the analysis.
        
        In production: based on ML model confidence scores
        For MVP: rule-based confidence
        """
        confidence = {
            "overall": analysis.confidence_score,
            "category_detection": 0.8,
            "component_detection": 0.7,
            "severity_assessment": 0.75,
            "needs_manual_review": analysis.confidence_score < 0.6
        }
        
        return confidence
