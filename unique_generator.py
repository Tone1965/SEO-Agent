# =====================================
# UNIQUE_GENERATOR.PY - UNIQUENESS ENGINE
# =====================================
# This ensures every generated website is completely different from others
# Prevents Google penalties by creating truly unique content, designs, and approaches
# Terry: Use this to guarantee each website is 100% unique and won't trigger duplicate content issues

import hashlib
import random
import uuid
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import re
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class UniquenessConfig:
    """Configuration for uniqueness generation"""
    business_type: str
    location: str
    target_keywords: List[str]
    baseline_content: Optional[Dict] = None
    uniqueness_level: str = "high"  # low, medium, high, extreme
    variation_seed: str = None
    avoid_patterns: List[str] = None
    
    def __post_init__(self):
        if not self.variation_seed:
            self.variation_seed = str(uuid.uuid4())
        if not self.avoid_patterns:
            self.avoid_patterns = []

class ContentVariationEngine:
    """Generates unique content variations to avoid duplication"""
    
    def __init__(self):
        self.sentence_structures = [
            "subject_verb_object",
            "passive_construction", 
            "question_format",
            "list_format",
            "storytelling_format",
            "problem_solution_format",
            "comparison_format",
            "testimonial_format"
        ]
        
        self.writing_styles = [
            "conversational",
            "authoritative", 
            "educational",
            "consultative",
            "friendly",
            "professional",
            "persuasive",
            "informative"
        ]
        
        self.content_angles = [
            "cost_savings",
            "time_efficiency", 
            "quality_focus",
            "convenience_factor",
            "expertise_emphasis",
            "local_advantage",
            "innovation_angle",
            "reliability_focus",
            "customer_service",
            "results_oriented"
        ]
        
        # Advanced synonym database for content variation
        self.synonym_database = {
            "professional": ["expert", "skilled", "qualified", "experienced", "certified", "seasoned"],
            "quality": ["excellence", "superior", "premium", "top-tier", "outstanding", "exceptional"],
            "service": ["solutions", "offerings", "expertise", "assistance", "support", "help"],
            "reliable": ["dependable", "trustworthy", "consistent", "steadfast", "solid", "stable"],
            "affordable": ["cost-effective", "budget-friendly", "economical", "reasonable", "competitive"],
            "fast": ["quick", "rapid", "swift", "speedy", "prompt", "immediate"],
            "local": ["neighborhood", "community", "area", "regional", "nearby", "vicinity"],
            "best": ["top", "leading", "premier", "foremost", "finest", "optimal"],
            "experienced": ["seasoned", "veteran", "skilled", "practiced", "knowledgeable", "established"],
            "customer": ["client", "patron", "consumer", "buyer", "user", "customer"]
        }
    
    def generate_unique_content_structure(self, config: UniquenessConfig) -> Dict[str, Any]:
        """Generate completely unique content structure"""
        
        # Use variation seed for consistent randomization
        random.seed(config.variation_seed)
        
        # Select unique combination of approaches
        structure = {
            'writing_style': random.choice(self.writing_styles),
            'content_angle': random.choice(self.content_angles),
            'sentence_structure': random.choice(self.sentence_structures),
            'paragraph_format': self._generate_paragraph_format(),
            'introduction_style': self._generate_introduction_style(config),
            'content_flow': self._generate_content_flow(),
            'call_to_action_style': self._generate_cta_style(),
            'unique_elements': self._generate_unique_elements(config)
        }
        
        return structure
    
    def _generate_paragraph_format(self) -> Dict[str, Any]:
        """Generate unique paragraph formatting approach"""
        
        formats = [
            {
                'style': 'short_punchy',
                'avg_sentences': 2,
                'max_words_per_sentence': 15,
                'use_fragments': True
            },
            {
                'style': 'detailed_explanatory',
                'avg_sentences': 4,
                'max_words_per_sentence': 25,
                'use_fragments': False
            },
            {
                'style': 'mixed_rhythm',
                'avg_sentences': 3,
                'max_words_per_sentence': 20,
                'use_fragments': True,
                'vary_length': True
            },
            {
                'style': 'bullet_heavy',
                'avg_sentences': 2,
                'use_lists': True,
                'list_frequency': 'high'
            }
        ]
        
        return random.choice(formats)
    
    def _generate_introduction_style(self, config: UniquenessConfig) -> Dict[str, str]:
        """Generate unique introduction approaches"""
        
        styles = [
            {
                'type': 'question_opening',
                'template': f"Are you looking for {config.business_type.lower()} in {config.location}?"
            },
            {
                'type': 'statistic_opening',
                'template': f"Did you know that 90% of {config.location} residents choose local {config.business_type.lower()}?"
            },
            {
                'type': 'story_opening',
                'template': f"Last month, a {config.location} family discovered the difference quality {config.business_type.lower()} makes..."
            },
            {
                'type': 'problem_opening',
                'template': f"Finding reliable {config.business_type.lower()} in {config.location} shouldn't be stressful."
            },
            {
                'type': 'benefit_opening',
                'template': f"Imagine having {config.business_type.lower()} that exceeds your expectations."
            }
        ]
        
        return random.choice(styles)
    
    def _generate_content_flow(self) -> List[str]:
        """Generate unique content flow patterns"""
        
        flow_patterns = [
            ['hook', 'problem', 'solution', 'benefits', 'proof', 'cta'],
            ['story', 'connection', 'expertise', 'process', 'results', 'action'],
            ['question', 'answer', 'details', 'examples', 'guarantee', 'next_steps'],
            ['benefit', 'feature', 'advantage', 'testimonial', 'offer', 'urgency'],
            ['local_connection', 'understanding', 'approach', 'difference', 'value', 'contact']
        ]
        
        return random.choice(flow_patterns)
    
    def _generate_cta_style(self) -> Dict[str, str]:
        """Generate unique call-to-action styles"""
        
        cta_styles = [
            {
                'urgency_level': 'high',
                'format': 'button_with_subtext',
                'tone': 'action_oriented'
            },
            {
                'urgency_level': 'medium',
                'format': 'conversational_invite',
                'tone': 'friendly'
            },
            {
                'urgency_level': 'low',
                'format': 'soft_suggestion',
                'tone': 'helpful'
            },
            {
                'urgency_level': 'extreme',
                'format': 'scarcity_driven',
                'tone': 'urgent'
            }
        ]
        
        return random.choice(cta_styles)
    
    def _generate_unique_elements(self, config: UniquenessConfig) -> List[str]:
        """Generate unique content elements to differentiate"""
        
        unique_elements = []
        
        # Location-specific elements
        unique_elements.append(f"local_{config.location.lower().replace(' ', '_')}_references")
        
        # Business-specific elements
        business_specific = {
            'plumbing': ['pipe_materials_discussion', 'water_pressure_education', 'maintenance_tips'],
            'hvac': ['energy_efficiency_focus', 'air_quality_emphasis', 'seasonal_maintenance'],
            'roofing': ['material_comparison', 'weather_protection', 'warranty_explanation'],
            'landscaping': ['plant_selection_guide', 'seasonal_care', 'design_philosophy'],
            'cleaning': ['product_safety', 'technique_explanation', 'time_saving_tips']
        }
        
        for key, elements in business_specific.items():
            if key in config.business_type.lower():
                unique_elements.extend(random.sample(elements, 2))
        
        # Random unique elements
        general_unique = [
            'behind_the_scenes_insight',
            'industry_insider_knowledge',
            'common_misconceptions',
            'future_trends_discussion',
            'cost_breakdown_transparency',
            'quality_standards_explanation',
            'team_introduction',
            'process_walkthrough'
        ]
        
        unique_elements.extend(random.sample(general_unique, 3))
        
        return unique_elements

class DesignVariationEngine:
    """Generates unique design variations to avoid visual similarity"""
    
    def __init__(self):
        self.layout_patterns = [
            "traditional_header_nav",
            "hero_with_overlay",
            "split_screen_layout", 
            "card_based_design",
            "magazine_style",
            "minimal_centered",
            "sidebar_navigation",
            "full_width_sections"
        ]
        
        self.color_schemes = [
            "monochromatic_blue",
            "complementary_orange_blue",
            "triadic_red_yellow_blue",
            "analogous_green_variations",
            "split_complementary",
            "neutral_with_accent",
            "warm_earth_tones",
            "cool_professional"
        ]
        
        self.visual_styles = [
            "modern_minimal",
            "classic_professional",
            "creative_bold",
            "warm_friendly",
            "tech_forward",
            "elegant_sophisticated",
            "rustic_authentic",
            "clean_corporate"
        ]
    
    def generate_unique_design_variation(self, config: UniquenessConfig) -> Dict[str, Any]:
        """Generate completely unique design approach"""
        
        random.seed(config.variation_seed)
        
        design_variation = {
            'layout_pattern': random.choice(self.layout_patterns),
            'color_scheme': random.choice(self.color_schemes),
            'visual_style': random.choice(self.visual_styles),
            'typography_approach': self._generate_typography_variation(),
            'spacing_system': self._generate_spacing_variation(),
            'component_styles': self._generate_component_variations(),
            'visual_hierarchy': self._generate_hierarchy_variation(),
            'interaction_patterns': self._generate_interaction_variations()
        }
        
        return design_variation
    
    def _generate_typography_variation(self) -> Dict[str, str]:
        """Generate unique typography combinations"""
        
        typography_variations = [
            {
                'heading_font': 'serif_traditional',
                'body_font': 'sans_serif_clean',
                'accent_font': 'script_elegant'
            },
            {
                'heading_font': 'sans_serif_modern',
                'body_font': 'sans_serif_readable',
                'accent_font': 'monospace_tech'
            },
            {
                'heading_font': 'display_bold',
                'body_font': 'serif_readable',
                'accent_font': 'sans_serif_condensed'
            },
            {
                'heading_font': 'custom_brand',
                'body_font': 'system_font',
                'accent_font': 'handwritten_style'
            }
        ]
        
        return random.choice(typography_variations)
    
    def _generate_spacing_variation(self) -> Dict[str, str]:
        """Generate unique spacing approaches"""
        
        spacing_variations = [
            {
                'approach': 'tight_compact',
                'section_spacing': 'minimal',
                'element_spacing': 'close'
            },
            {
                'approach': 'generous_breathing',
                'section_spacing': 'large',
                'element_spacing': 'wide'
            },
            {
                'approach': 'varied_rhythm',
                'section_spacing': 'alternating',
                'element_spacing': 'responsive'
            },
            {
                'approach': 'golden_ratio',
                'section_spacing': 'proportional',
                'element_spacing': 'mathematical'
            }
        ]
        
        return random.choice(spacing_variations)
    
    def _generate_component_variations(self) -> Dict[str, str]:
        """Generate unique component styling approaches"""
        
        return {
            'button_style': random.choice(['rounded_corners', 'sharp_edges', 'pill_shaped', 'custom_angled']),
            'card_style': random.choice(['flat_minimal', 'raised_shadows', 'outlined_borders', 'gradient_backgrounds']),
            'form_style': random.choice(['clean_lines', 'rounded_friendly', 'boxed_sections', 'floating_labels']),
            'navigation_style': random.choice(['horizontal_bar', 'hamburger_menu', 'sidebar_fixed', 'tabbed_interface'])
        }
    
    def _generate_hierarchy_variation(self) -> Dict[str, str]:
        """Generate unique visual hierarchy approaches"""
        
        hierarchy_variations = [
            {
                'primary_emphasis': 'size_based',
                'secondary_emphasis': 'color_based',
                'tertiary_emphasis': 'position_based'
            },
            {
                'primary_emphasis': 'contrast_based',
                'secondary_emphasis': 'typography_based',
                'tertiary_emphasis': 'spacing_based'
            },
            {
                'primary_emphasis': 'motion_based',
                'secondary_emphasis': 'depth_based',
                'tertiary_emphasis': 'pattern_based'
            }
        ]
        
        return random.choice(hierarchy_variations)
    
    def _generate_interaction_variations(self) -> List[str]:
        """Generate unique interaction patterns"""
        
        interaction_options = [
            'hover_animations',
            'scroll_triggered_effects',
            'click_feedback_animations',
            'parallax_scrolling',
            'sticky_navigation',
            'smooth_transitions',
            'micro_interactions',
            'loading_animations'
        ]
        
        return random.sample(interaction_options, 4)

class StructuralVariationEngine:
    """Generates unique website structures and architectures"""
    
    def __init__(self):
        self.page_structures = [
            "traditional_multipage",
            "single_page_scroll",
            "hybrid_approach",
            "tab_based_navigation",
            "accordion_sections",
            "modal_based_content"
        ]
        
        self.navigation_patterns = [
            "top_horizontal",
            "side_vertical", 
            "bottom_sticky",
            "floating_menu",
            "mega_menu",
            "breadcrumb_heavy"
        ]
        
        self.content_organization = [
            "service_focused",
            "benefit_driven",
            "process_oriented",
            "problem_solution",
            "testimonial_heavy",
            "portfolio_showcase"
        ]
    
    def generate_unique_structure(self, config: UniquenessConfig) -> Dict[str, Any]:
        """Generate unique website structure"""
        
        random.seed(config.variation_seed)
        
        structure = {
            'page_structure': random.choice(self.page_structures),
            'navigation_pattern': random.choice(self.navigation_patterns),
            'content_organization': random.choice(self.content_organization),
            'section_order': self._generate_section_order(),
            'page_hierarchy': self._generate_page_hierarchy(config),
            'content_depth': self._generate_content_depth_strategy(),
            'internal_linking': self._generate_linking_strategy()
        }
        
        return structure
    
    def _generate_section_order(self) -> List[str]:
        """Generate unique section ordering"""
        
        base_sections = ['hero', 'about', 'services', 'testimonials', 'contact']
        optional_sections = ['process', 'gallery', 'faq', 'blog', 'team', 'pricing']
        
        # Shuffle base sections (except hero stays first)
        sections = ['hero']
        remaining_base = base_sections[1:]
        random.shuffle(remaining_base)
        sections.extend(remaining_base)
        
        # Add random optional sections
        num_optional = random.randint(2, 4)
        selected_optional = random.sample(optional_sections, num_optional)
        
        # Insert optional sections at random positions
        for section in selected_optional:
            position = random.randint(1, len(sections))
            sections.insert(position, section)
        
        return sections
    
    def _generate_page_hierarchy(self, config: UniquenessConfig) -> Dict[str, List[str]]:
        """Generate unique page hierarchy"""
        
        business_pages = {
            'plumbing': ['emergency_services', 'drain_cleaning', 'water_heaters', 'pipe_repair'],
            'hvac': ['heating', 'cooling', 'maintenance', 'indoor_air_quality'],
            'roofing': ['roof_repair', 'roof_replacement', 'gutters', 'siding'],
            'landscaping': ['design', 'maintenance', 'hardscaping', 'irrigation'],
            'cleaning': ['residential', 'commercial', 'deep_cleaning', 'move_out']
        }
        
        # Get business-specific pages
        service_pages = []
        for key, pages in business_pages.items():
            if key in config.business_type.lower():
                service_pages = random.sample(pages, random.randint(3, len(pages)))
                break
        
        if not service_pages:
            service_pages = ['service_1', 'service_2', 'service_3']
        
        hierarchy = {
            'main_pages': ['home', 'about', 'services', 'contact'],
            'service_pages': service_pages,
            'support_pages': random.sample(['faq', 'blog', 'reviews', 'gallery', 'process'], 3),
            'legal_pages': ['privacy', 'terms']
        }
        
        return hierarchy
    
    def _generate_content_depth_strategy(self) -> Dict[str, str]:
        """Generate unique content depth approach"""
        
        strategies = [
            {
                'approach': 'comprehensive_detail',
                'page_length': 'long_form',
                'information_density': 'high'
            },
            {
                'approach': 'concise_focused',
                'page_length': 'medium_form',
                'information_density': 'medium'
            },
            {
                'approach': 'scannable_quick',
                'page_length': 'short_form',
                'information_density': 'low'
            },
            {
                'approach': 'mixed_strategy',
                'page_length': 'variable',
                'information_density': 'adaptive'
            }
        ]
        
        return random.choice(strategies)
    
    def _generate_linking_strategy(self) -> Dict[str, Any]:
        """Generate unique internal linking approach"""
        
        return {
            'strategy': random.choice(['hub_spoke', 'interconnected_web', 'linear_progression', 'topic_clusters']),
            'anchor_text_style': random.choice(['keyword_rich', 'natural_language', 'branded_terms', 'descriptive']),
            'link_placement': random.choice(['contextual_inline', 'sidebar_related', 'footer_navigation', 'banner_promotion']),
            'link_density': random.choice(['minimal', 'moderate', 'high', 'strategic'])
        }

class KeywordVariationEngine:
    """Generates unique keyword targeting and SEO approaches"""
    
    def __init__(self):
        self.keyword_strategies = [
            "long_tail_focus",
            "local_dominant",
            "semantic_clustering",
            "question_based",
            "commercial_intent",
            "educational_content"
        ]
    
    def generate_unique_keyword_approach(self, config: UniquenessConfig) -> Dict[str, Any]:
        """Generate unique keyword targeting strategy"""
        
        random.seed(config.variation_seed)
        
        # Generate variations of target keywords
        keyword_variations = self._generate_keyword_variations(config.target_keywords, config.location)
        
        keyword_approach = {
            'primary_strategy': random.choice(self.keyword_strategies),
            'keyword_variations': keyword_variations,
            'semantic_clusters': self._generate_semantic_clusters(config),
            'long_tail_targets': self._generate_long_tail_keywords(config),
            'local_modifiers': self._generate_local_modifiers(config.location),
            'content_themes': self._generate_content_themes(config),
            'meta_tag_approach': self._generate_meta_tag_strategy()
        }
        
        return keyword_approach
    
    def _generate_keyword_variations(self, keywords: List[str], location: str) -> Dict[str, List[str]]:
        """Generate variations of target keywords"""
        
        variations = {}
        
        for keyword in keywords:
            keyword_vars = []
            
            # Synonym variations
            words = keyword.split()
            for i, word in enumerate(words):
                if word.lower() in self.synonym_database:
                    synonyms = self.synonym_database[word.lower()]
                    for synonym in synonyms[:3]:  # Limit to 3 synonyms
                        new_keyword = words.copy()
                        new_keyword[i] = synonym
                        keyword_vars.append(' '.join(new_keyword))
            
            # Location variations
            location_formats = [
                f"{keyword} in {location}",
                f"{keyword} {location}",
                f"{location} {keyword}",
                f"{keyword} near {location}",
                f"{keyword} services {location}"
            ]
            keyword_vars.extend(location_formats)
            
            # Intent variations
            intent_variations = [
                f"best {keyword}",
                f"affordable {keyword}",
                f"professional {keyword}",
                f"{keyword} company",
                f"{keyword} contractor"
            ]
            keyword_vars.extend(intent_variations)
            
            variations[keyword] = list(set(keyword_vars))  # Remove duplicates
        
        return variations
    
    def _generate_semantic_clusters(self, config: UniquenessConfig) -> Dict[str, List[str]]:
        """Generate semantic keyword clusters"""
        
        business_clusters = {
            'plumbing': {
                'emergency': ['emergency plumber', 'urgent plumbing', '24/7 plumber', 'plumbing emergency'],
                'repair': ['pipe repair', 'leak repair', 'plumbing repair', 'fix plumbing'],
                'installation': ['plumbing installation', 'new plumbing', 'plumbing upgrade']
            },
            'hvac': {
                'heating': ['heating repair', 'furnace service', 'boiler repair', 'heat pump'],
                'cooling': ['air conditioning', 'AC repair', 'cooling system', 'central air'],
                'maintenance': ['HVAC maintenance', 'tune-up', 'system cleaning', 'filter change']
            },
            'roofing': {
                'repair': ['roof repair', 'leak repair', 'storm damage', 'emergency roofing'],
                'replacement': ['new roof', 'roof replacement', 'roofing installation'],
                'materials': ['asphalt shingles', 'metal roofing', 'tile roofing']
            }
        }
        
        # Find matching clusters
        for business_type, clusters in business_clusters.items():
            if business_type in config.business_type.lower():
                return clusters
        
        # Default generic clusters
        return {
            'services': [f'{config.business_type.lower()} services', f'professional {config.business_type.lower()}'],
            'quality': [f'quality {config.business_type.lower()}', f'reliable {config.business_type.lower()}'],
            'local': [f'{config.location} {config.business_type.lower()}', f'local {config.business_type.lower()}']
        }
    
    def _generate_long_tail_keywords(self, config: UniquenessConfig) -> List[str]:
        """Generate long-tail keyword opportunities"""
        
        long_tail_templates = [
            f"how to choose {config.business_type.lower()} in {config.location}",
            f"best {config.business_type.lower()} company near {config.location}",
            f"affordable {config.business_type.lower()} services {config.location}",
            f"emergency {config.business_type.lower()} {config.location} area",
            f"professional {config.business_type.lower()} contractor {config.location}",
            f"reliable {config.business_type.lower()} company {config.location}",
            f"quality {config.business_type.lower()} services near me",
            f"licensed {config.business_type.lower()} {config.location}",
            f"experienced {config.business_type.lower()} team {config.location}",
            f"local {config.business_type.lower()} experts {config.location}"
        ]
        
        return random.sample(long_tail_templates, 6)
    
    def _generate_local_modifiers(self, location: str) -> List[str]:
        """Generate local keyword modifiers"""
        
        modifiers = [
            f"in {location}",
            f"near {location}",
            f"{location} area",
            f"serving {location}",
            f"{location} and surrounding areas",
            f"local to {location}",
            f"{location} region",
            f"throughout {location}"
        ]
        
        return modifiers
    
    def _generate_content_themes(self, config: UniquenessConfig) -> List[str]:
        """Generate content themes for keyword targeting"""
        
        themes = [
            f"why choose {config.business_type.lower()} in {config.location}",
            f"benefits of professional {config.business_type.lower()}",
            f"common {config.business_type.lower()} problems in {config.location}",
            f"cost of {config.business_type.lower()} services",
            f"how to maintain {config.business_type.lower()}",
            f"seasonal {config.business_type.lower()} tips",
            f"emergency {config.business_type.lower()} guide",
            f"choosing {config.business_type.lower()} contractors"
        ]
        
        return random.sample(themes, 5)
    
    def _generate_meta_tag_strategy(self) -> Dict[str, str]:
        """Generate unique meta tag approach"""
        
        strategies = [
            {
                'title_format': 'keyword_location_brand',
                'description_style': 'benefit_focused',
                'length_preference': 'full_length'
            },
            {
                'title_format': 'brand_keyword_location',
                'description_style': 'action_oriented',
                'length_preference': 'concise'
            },
            {
                'title_format': 'question_based_title',
                'description_style': 'problem_solution',
                'length_preference': 'moderate'
            }
        ]
        
        return random.choice(strategies)

class UniquenessValidator:
    """Validates uniqueness and prevents duplication"""
    
    def __init__(self):
        self.content_fingerprints = set()
        self.design_fingerprints = set()
        self.structure_fingerprints = set()
    
    def generate_content_fingerprint(self, content: Dict) -> str:
        """Generate fingerprint for content to check uniqueness"""
        
        # Extract key content elements
        content_elements = []
        
        if 'structure' in content:
            content_elements.append(str(content['structure']))
        if 'keywords' in content:
            content_elements.append(str(sorted(content['keywords'])))
        if 'writing_style' in content:
            content_elements.append(content['writing_style'])
        
        # Create hash of combined elements
        content_string = '|'.join(content_elements)
        fingerprint = hashlib.md5(content_string.encode()).hexdigest()
        
        return fingerprint
    
    def validate_uniqueness(self, generated_content: Dict, uniqueness_threshold: float = 0.8) -> Dict[str, Any]:
        """Validate that generated content is sufficiently unique"""
        
        content_fingerprint = self.generate_content_fingerprint(generated_content)
        
        # Check against existing fingerprints
        is_unique = content_fingerprint not in self.content_fingerprints
        
        if is_unique:
            self.content_fingerprints.add(content_fingerprint)
        
        # Calculate similarity score (simplified)
        similarity_scores = []
        for existing_fingerprint in self.content_fingerprints:
            if existing_fingerprint != content_fingerprint:
                # Simple Hamming distance for demonstration
                similarity = sum(c1 == c2 for c1, c2 in zip(content_fingerprint, existing_fingerprint)) / len(content_fingerprint)
                similarity_scores.append(similarity)
        
        max_similarity = max(similarity_scores) if similarity_scores else 0
        is_sufficiently_unique = max_similarity < (1 - uniqueness_threshold)
        
        return {
            'is_unique': is_unique,
            'is_sufficiently_unique': is_sufficiently_unique,
            'max_similarity': max_similarity,
            'fingerprint': content_fingerprint,
            'recommendations': self._generate_uniqueness_recommendations(max_similarity, uniqueness_threshold)
        }
    
    def _generate_uniqueness_recommendations(self, similarity: float, threshold: float) -> List[str]:
        """Generate recommendations to improve uniqueness"""
        
        recommendations = []
        
        if similarity > (1 - threshold):
            recommendations.extend([
                "Vary the content structure approach",
                "Use different keyword variations",
                "Change the writing style or tone",
                "Modify the section ordering",
                "Add unique local references",
                "Incorporate different content angles",
                "Use alternative sentence structures"
            ])
        
        return recommendations

class UniquenessOrchestrator:
    """Main class that orchestrates all uniqueness generation"""
    
    def __init__(self):
        self.content_engine = ContentVariationEngine()
        self.design_engine = DesignVariationEngine()
        self.structure_engine = StructuralVariationEngine()
        self.keyword_engine = KeywordVariationEngine()
        self.validator = UniquenessValidator()
    
    def generate_complete_uniqueness_package(self, config: UniquenessConfig) -> Dict[str, Any]:
        """Generate complete uniqueness package for website"""
        
        try:
            logger.info(f"Generating uniqueness package for {config.business_type} in {config.location}")
            
            # Generate all uniqueness components
            content_variation = self.content_engine.generate_unique_content_structure(config)
            design_variation = self.design_engine.generate_unique_design_variation(config)
            structure_variation = self.structure_engine.generate_unique_structure(config)
            keyword_variation = self.keyword_engine.generate_unique_keyword_approach(config)
            
            # Combine all variations
            uniqueness_package = {
                'content_variation': content_variation,
                'design_variation': design_variation,
                'structure_variation': structure_variation,
                'keyword_variation': keyword_variation,
                'variation_metadata': {
                    'uniqueness_level': config.uniqueness_level,
                    'variation_seed': config.variation_seed,
                    'generation_timestamp': datetime.now().isoformat(),
                    'business_context': {
                        'type': config.business_type,
                        'location': config.location,
                        'keywords': config.target_keywords
                    }
                }
            }
            
            # Validate uniqueness
            validation_result = self.validator.validate_uniqueness(uniqueness_package)
            
            # If not unique enough, regenerate with different seed
            if not validation_result['is_sufficiently_unique'] and config.uniqueness_level == 'high':
                logger.info("Regenerating with higher uniqueness...")
                config.variation_seed = str(uuid.uuid4())
                return self.generate_complete_uniqueness_package(config)
            
            return {
                'success': True,
                'uniqueness_package': uniqueness_package,
                'validation_result': validation_result,
                'generation_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'config': asdict(config)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating uniqueness package: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def apply_uniqueness_to_content(self, base_content: Dict, uniqueness_package: Dict) -> Dict[str, Any]:
        """Apply uniqueness variations to base content"""
        
        try:
            content_variation = uniqueness_package['content_variation']
            
            # Apply content structure variations
            modified_content = base_content.copy()
            
            # Apply writing style
            modified_content['writing_style'] = content_variation['writing_style']
            modified_content['content_angle'] = content_variation['content_angle']
            
            # Apply paragraph formatting
            modified_content['paragraph_format'] = content_variation['paragraph_format']
            
            # Apply introduction style
            modified_content['introduction_style'] = content_variation['introduction_style']
            
            # Apply content flow
            modified_content['content_flow'] = content_variation['content_flow']
            
            # Apply unique elements
            modified_content['unique_elements'] = content_variation['unique_elements']
            
            return {
                'success': True,
                'modified_content': modified_content,
                'applied_variations': content_variation
            }
            
        except Exception as e:
            logger.error(f"Error applying uniqueness to content: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_uniqueness_statistics(self) -> Dict[str, Any]:
        """Get statistics about generated uniqueness patterns"""
        
        return {
            'total_fingerprints': len(self.validator.content_fingerprints),
            'unique_content_patterns': len(self.validator.content_fingerprints),
            'unique_design_patterns': len(self.validator.design_fingerprints),
            'unique_structure_patterns': len(self.validator.structure_fingerprints),
            'generation_timestamp': datetime.now().isoformat()
        }

# Usage example and integration
if __name__ == "__main__":
    # Example configuration
    config = UniquenessConfig(
        business_type="HVAC Services",
        location="Birmingham, AL",
        target_keywords=["hvac repair", "air conditioning", "heating services"],
        uniqueness_level="high"
    )
    
    # Generate complete uniqueness package
    orchestrator = UniquenessOrchestrator()
    result = orchestrator.generate_complete_uniqueness_package(config)
    
    if result['success']:
        print("Uniqueness package generated successfully!")
        print(f"Variation seed: {result['uniqueness_package']['variation_metadata']['variation_seed']}")
        print(f"Uniqueness validation: {result['validation_result']['is_sufficiently_unique']}")
        
        # Save uniqueness package
        with open(f"uniqueness_{config.variation_seed[:8]}.json", 'w') as f:
            json.dump(result, f, indent=2)
            
        # Get statistics
        stats = orchestrator.get_uniqueness_statistics()
        print(f"Total unique patterns generated: {stats['total_fingerprints']}")
        
    else:
        print(f"Error: {result['error']}")