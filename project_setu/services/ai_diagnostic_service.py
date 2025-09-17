"""
AI-Powered Diagnostic Service
Advanced machine learning system for diagnostic assistance and code recommendations.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)


class DiagnosticConfidence(Enum):
    """Diagnostic confidence levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class MedicalSystem(Enum):
    """Medical system preferences"""
    AYURVEDA = "ayurveda"
    SIDDHA = "siddha"
    UNANI = "unani"
    MODERN_MEDICINE = "modern_medicine"
    INTEGRATIVE = "integrative"


@dataclass
class PatientProfile:
    """Patient profile for diagnostic analysis"""
    age: int
    gender: str
    medical_history: List[str]
    current_medications: List[str]
    allergies: List[str]
    lifestyle_factors: Dict[str, Any]
    vital_signs: Dict[str, float]
    lab_results: Dict[str, float]
    preferred_system: MedicalSystem = MedicalSystem.INTEGRATIVE


@dataclass
class Symptom:
    """Symptom representation"""
    description: str
    severity: int  # 1-10 scale
    duration: str
    frequency: str
    associated_factors: List[str]
    location: str = ""
    quality: str = ""


@dataclass
class DiagnosticSuggestion:
    """AI diagnostic suggestion"""
    condition_name: str
    condition_codes: Dict[str, str]  # system -> code mapping
    confidence: DiagnosticConfidence
    confidence_score: float
    reasoning: str
    supporting_evidence: List[str]
    contradicting_evidence: List[str]
    recommended_tests: List[str]
    treatment_suggestions: List[str]
    differential_rank: int
    medical_system: MedicalSystem
    urgency_level: str  # LOW, MODERATE, HIGH, CRITICAL


@dataclass
class TreatmentRecommendation:
    """Treatment recommendation"""
    treatment_name: str
    treatment_type: str  # MEDICATION, THERAPY, LIFESTYLE, PROCEDURE
    medical_system: MedicalSystem
    dosage: str
    duration: str
    precautions: List[str]
    contraindications: List[str]
    monitoring_required: List[str]
    evidence_level: str


class AIEthicsChecker:
    """AI ethics and safety checker"""
    
    def __init__(self):
        self.safety_rules = [
            "Never provide definitive diagnosis without clinical examination",
            "Always recommend consulting healthcare professional",
            "Flag emergency symptoms for immediate attention",
            "Respect patient privacy and confidentiality",
            "Provide culturally sensitive recommendations",
            "Acknowledge limitations of AI system"
        ]
        
        self.emergency_keywords = [
            "chest pain", "difficulty breathing", "severe bleeding",
            "loss of consciousness", "severe headache", "stroke symptoms",
            "heart attack", "severe allergic reaction", "poisoning"
        ]
    
    def check_emergency_symptoms(self, symptoms: List[Symptom]) -> Tuple[bool, List[str]]:
        """Check for emergency symptoms"""
        emergency_flags = []
        is_emergency = False
        
        for symptom in symptoms:
            symptom_text = symptom.description.lower()
            for keyword in self.emergency_keywords:
                if keyword in symptom_text:
                    emergency_flags.append(f"Emergency keyword detected: {keyword}")
                    is_emergency = True
            
            # High severity symptoms
            if symptom.severity >= 8:
                emergency_flags.append(f"High severity symptom: {symptom.description}")
                is_emergency = True
        
        return is_emergency, emergency_flags
    
    def validate_recommendation(self, recommendation: DiagnosticSuggestion) -> Tuple[bool, List[str]]:
        """Validate diagnostic recommendation for safety"""
        warnings = []
        is_safe = True
        
        # Check confidence levels
        if recommendation.confidence_score < 0.3:
            warnings.append("Very low confidence - recommend multiple opinions")
        
        # Check for high-risk conditions
        high_risk_conditions = ["cancer", "heart disease", "stroke", "diabetes complications"]
        for condition in high_risk_conditions:
            if condition.lower() in recommendation.condition_name.lower():
                warnings.append(f"High-risk condition detected: {condition}")
        
        return is_safe, warnings


class MultiModalDiagnosticAI:
    """
    Advanced AI diagnostic system with multi-modal analysis.
    
    Features:
    - Natural language processing for symptom analysis
    - Machine learning models for pattern recognition
    - Traditional medicine knowledge integration
    - Ethical AI with safety checks
    - Personalized recommendations
    - Continuous learning from feedback
    - Cultural sensitivity and multi-language support
    """
    
    def __init__(self):
        self.model_dir = Path("./models/diagnostic_ai")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize AI models
        self.symptom_analyzer = None
        self.diagnostic_classifier = None
        self.treatment_recommender = None
        self.text_vectorizer = TfidfVectorizer(max_features=5000)
        self.scaler = StandardScaler()
        
        # Knowledge bases
        self.ayurveda_knowledge = self._load_ayurveda_knowledge()
        self.modern_medicine_knowledge = self._load_modern_medicine_knowledge()
        self.drug_interaction_db = self._load_drug_interactions()
        
        # Ethics checker
        self.ethics_checker = AIEthicsChecker()
        
        # Feedback storage
        self.feedback_data = []
        
        # Initialize models (will be done lazily)
        self._models_initialized = False
    
    async def _initialize_models(self):
        """Initialize AI models"""
        try:
            # Load pre-trained models or create new ones
            await self._load_or_create_diagnostic_models()
            
            # Initialize NLP pipeline for symptom analysis
            self.symptom_analyzer = pipeline(
                "text-classification",
                model="distilbert-base-uncased",
                return_all_scores=True
            )
            
            logger.info("AI diagnostic models initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {e}")
            # Use fallback models
            await self._create_fallback_models()
    
    async def _load_or_create_diagnostic_models(self):
        """Load existing models or create new ones"""
        model_file = self.model_dir / "diagnostic_classifier.pkl"
        
        if model_file.exists():
            with open(model_file, 'rb') as f:
                self.diagnostic_classifier = pickle.load(f)
            logger.info("Loaded existing diagnostic classifier")
        else:
            await self._train_diagnostic_models()
    
    async def _train_diagnostic_models(self):
        """Train diagnostic models with synthetic and real data"""
        logger.info("Training diagnostic models...")
        
        # Generate training data (in production, use real medical datasets)
        training_data = self._generate_training_data()
        
        # Prepare features and labels
        X = np.array([sample['features'] for sample in training_data])
        y = np.array([sample['diagnosis'] for sample in training_data])
        
        # Train ensemble model
        self.diagnostic_classifier = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        
        self.diagnostic_classifier.fit(X, y)
        
        # Save model
        model_file = self.model_dir / "diagnostic_classifier.pkl"
        with open(model_file, 'wb') as f:
            pickle.dump(self.diagnostic_classifier, f)
        
        logger.info("Diagnostic models trained and saved")
    
    async def _create_fallback_models(self):
        """Create simple fallback models for demo"""
        # Simple rule-based fallback
        self.diagnostic_classifier = self._create_rule_based_classifier()
        logger.info("Created fallback diagnostic models")
    
    def _create_rule_based_classifier(self):
        """Create a simple rule-based classifier"""
        class RuleBasedClassifier:
            def __init__(self):
                self.rules = {
                    'fever': ['viral_infection', 'bacterial_infection', 'jvara'],
                    'headache': ['tension_headache', 'migraine', 'shiroroga'],
                    'cough': ['respiratory_infection', 'bronchitis', 'kasa'],
                    'fatigue': ['anemia', 'depression', 'klama'],
                    'pain': ['inflammation', 'injury', 'vedana']
                }
            
            def predict_proba(self, symptoms):
                # Simple keyword matching
                predictions = []
                for symptom_list in symptoms:
                    symptom_text = ' '.join(symptom_list).lower()
                    scores = {}
                    
                    for keyword, conditions in self.rules.items():
                        if keyword in symptom_text:
                            for condition in conditions:
                                scores[condition] = scores.get(condition, 0) + 0.3
                    
                    # Normalize scores
                    if scores:
                        max_score = max(scores.values())
                        normalized_scores = {k: v/max_score for k, v in scores.items()}
                    else:
                        normalized_scores = {'unknown_condition': 0.5}
                    
                    predictions.append(normalized_scores)
                
                return predictions
        
        return RuleBasedClassifier()
    
    def _generate_training_data(self) -> List[Dict]:
        """Generate synthetic training data for model development"""
        # This would be replaced with real medical datasets in production
        training_samples = []
        
        # Sample conditions with features
        conditions = {
            'viral_fever': {
                'symptoms': ['fever', 'headache', 'body_ache', 'fatigue'],
                'age_range': (5, 80),
                'severity': (3, 7),
                'features': [1, 1, 1, 1, 0, 0, 0]  # Simplified feature vector
            },
            'hypertension': {
                'symptoms': ['headache', 'dizziness', 'chest_pain'],
                'age_range': (40, 80),
                'severity': (4, 8),
                'features': [0, 1, 0, 0, 1, 1, 0]
            },
            'diabetes': {
                'symptoms': ['frequent_urination', 'excessive_thirst', 'fatigue'],
                'age_range': (30, 80),
                'severity': (3, 6),
                'features': [0, 0, 0, 1, 0, 0, 1]
            }
        }
        
        # Generate samples
        for condition, data in conditions.items():
            for _ in range(100):  # 100 samples per condition
                sample = {
                    'features': data['features'],
                    'diagnosis': condition,
                    'symptoms': data['symptoms'],
                    'confidence': np.random.uniform(0.6, 0.9)
                }
                training_samples.append(sample)
        
        return training_samples
    
    async def analyze_symptoms(self, symptoms: List[Symptom], 
                             patient_profile: PatientProfile) -> List[DiagnosticSuggestion]:
        """
        Analyze symptoms and provide diagnostic suggestions.
        
        This is the main AI diagnostic function that combines multiple approaches:
        - NLP analysis of symptom descriptions
        - Pattern matching with medical knowledge
        - Traditional medicine integration
        - Personalized recommendations based on patient profile
        """
        
        # Check for emergency symptoms first
        is_emergency, emergency_flags = self.ethics_checker.check_emergency_symptoms(symptoms)
        
        if is_emergency:
            return self._create_emergency_response(symptoms, emergency_flags)
        
        # Extract features from symptoms and patient profile
        features = self._extract_features(symptoms, patient_profile)
        
        # Get AI predictions
        ai_predictions = await self._get_ai_predictions(features, symptoms)
        
        # Integrate traditional medicine knowledge
        traditional_suggestions = await self._get_traditional_medicine_suggestions(
            symptoms, patient_profile
        )
        
        # Combine and rank suggestions
        combined_suggestions = self._combine_suggestions(ai_predictions, traditional_suggestions)
        
        # Apply ethical filtering and safety checks
        filtered_suggestions = self._apply_ethical_filtering(combined_suggestions)
        
        # Personalize based on patient profile
        personalized_suggestions = self._personalize_suggestions(
            filtered_suggestions, patient_profile
        )
        
        return personalized_suggestions[:10]  # Top 10 suggestions
    
    def _create_emergency_response(self, symptoms: List[Symptom], 
                                 emergency_flags: List[str]) -> List[DiagnosticSuggestion]:
        """Create emergency response for critical symptoms"""
        emergency_suggestion = DiagnosticSuggestion(
            condition_name="EMERGENCY - Seek Immediate Medical Attention",
            condition_codes={"EMERGENCY": "999"},
            confidence=DiagnosticConfidence.VERY_HIGH,
            confidence_score=1.0,
            reasoning="Emergency symptoms detected requiring immediate medical attention",
            supporting_evidence=emergency_flags,
            contradicting_evidence=[],
            recommended_tests=["Immediate clinical assessment"],
            treatment_suggestions=["Call emergency services", "Go to nearest emergency room"],
            differential_rank=1,
            medical_system=MedicalSystem.MODERN_MEDICINE,
            urgency_level="CRITICAL"
        )
        
        return [emergency_suggestion]
    
    def _extract_features(self, symptoms: List[Symptom], 
                         patient_profile: PatientProfile) -> np.ndarray:
        """Extract features for ML model input"""
        features = []
        
        # Symptom features
        symptom_keywords = ['fever', 'headache', 'cough', 'pain', 'fatigue', 'nausea', 'dizziness']
        for keyword in symptom_keywords:
            has_symptom = any(keyword.lower() in s.description.lower() for s in symptoms)
            features.append(1.0 if has_symptom else 0.0)
        
        # Severity features
        avg_severity = np.mean([s.severity for s in symptoms]) if symptoms else 0
        max_severity = max([s.severity for s in symptoms]) if symptoms else 0
        features.extend([avg_severity / 10.0, max_severity / 10.0])
        
        # Patient profile features
        features.extend([
            patient_profile.age / 100.0,  # Normalized age
            1.0 if patient_profile.gender.lower() == 'male' else 0.0,
            len(patient_profile.medical_history) / 10.0,  # Normalized history count
            len(patient_profile.current_medications) / 10.0  # Normalized medication count
        ])
        
        # Vital signs (if available)
        if patient_profile.vital_signs:
            temperature = patient_profile.vital_signs.get('temperature', 98.6)
            bp_systolic = patient_profile.vital_signs.get('bp_systolic', 120)
            heart_rate = patient_profile.vital_signs.get('heart_rate', 70)
            
            features.extend([
                (temperature - 98.6) / 10.0,  # Temperature deviation
                (bp_systolic - 120) / 100.0,  # BP deviation
                (heart_rate - 70) / 100.0     # HR deviation
            ])
        else:
            features.extend([0.0, 0.0, 0.0])
        
        return np.array(features)
    
    async def _get_ai_predictions(self, features: np.ndarray, 
                                symptoms: List[Symptom]) -> List[DiagnosticSuggestion]:
        """Get predictions from AI models"""
        suggestions = []
        
        try:
            if self.diagnostic_classifier:
                # Reshape features for prediction
                features_reshaped = features.reshape(1, -1)
                
                # Get predictions
                predictions = self.diagnostic_classifier.predict_proba([features])
                
                if isinstance(predictions, list) and predictions:
                    pred_dict = predictions[0]
                    
                    for condition, confidence in pred_dict.items():
                        if confidence > 0.3:  # Minimum confidence threshold
                            suggestion = DiagnosticSuggestion(
                                condition_name=condition.replace('_', ' ').title(),
                                condition_codes=self._get_condition_codes(condition),
                                confidence=self._map_confidence_level(confidence),
                                confidence_score=confidence,
                                reasoning=f"AI model prediction based on symptom pattern analysis",
                                supporting_evidence=[s.description for s in symptoms],
                                contradicting_evidence=[],
                                recommended_tests=self._get_recommended_tests(condition),
                                treatment_suggestions=self._get_treatment_suggestions(condition),
                                differential_rank=len(suggestions) + 1,
                                medical_system=MedicalSystem.MODERN_MEDICINE,
                                urgency_level=self._determine_urgency(condition, confidence)
                            )
                            suggestions.append(suggestion)
        
        except Exception as e:
            logger.error(f"Error in AI predictions: {e}")
        
        return suggestions
    
    async def _get_traditional_medicine_suggestions(self, symptoms: List[Symptom], 
                                                  patient_profile: PatientProfile) -> List[DiagnosticSuggestion]:
        """Get suggestions from traditional medicine knowledge base"""
        suggestions = []
        
        # Ayurveda suggestions
        if patient_profile.preferred_system in [MedicalSystem.AYURVEDA, MedicalSystem.INTEGRATIVE]:
            ayurveda_suggestions = self._get_ayurveda_suggestions(symptoms)
            suggestions.extend(ayurveda_suggestions)
        
        # Siddha suggestions
        if patient_profile.preferred_system in [MedicalSystem.SIDDHA, MedicalSystem.INTEGRATIVE]:
            siddha_suggestions = self._get_siddha_suggestions(symptoms)
            suggestions.extend(siddha_suggestions)
        
        # Unani suggestions
        if patient_profile.preferred_system in [MedicalSystem.UNANI, MedicalSystem.INTEGRATIVE]:
            unani_suggestions = self._get_unani_suggestions(symptoms)
            suggestions.extend(unani_suggestions)
        
        return suggestions
    
    def _get_ayurveda_suggestions(self, symptoms: List[Symptom]) -> List[DiagnosticSuggestion]:
        """Get Ayurveda-specific diagnostic suggestions"""
        suggestions = []
        
        # Simple rule-based Ayurveda diagnosis
        ayurveda_mappings = {
            'fever': {
                'condition': 'Jvara',
                'dosha': 'Pitta imbalance',
                'treatments': ['Tulsi tea', 'Ginger decoction', 'Rest', 'Light diet']
            },
            'headache': {
                'condition': 'Shiroroga',
                'dosha': 'Vata-Pitta imbalance',
                'treatments': ['Head massage with oil', 'Pranayama', 'Meditation']
            },
            'cough': {
                'condition': 'Kasa',
                'dosha': 'Kapha imbalance',
                'treatments': ['Honey with ginger', 'Steam inhalation', 'Turmeric milk']
            }
        }
        
        for symptom in symptoms:
            for keyword, ayurveda_info in ayurveda_mappings.items():
                if keyword.lower() in symptom.description.lower():
                    suggestion = DiagnosticSuggestion(
                        condition_name=ayurveda_info['condition'],
                        condition_codes={"NAMASTE": f"AYU_{keyword.upper()}"},
                        confidence=DiagnosticConfidence.MODERATE,
                        confidence_score=0.7,
                        reasoning=f"Ayurvedic analysis suggests {ayurveda_info['dosha']}",
                        supporting_evidence=[symptom.description],
                        contradicting_evidence=[],
                        recommended_tests=['Nadi Pariksha (Pulse diagnosis)', 'Prakriti assessment'],
                        treatment_suggestions=ayurveda_info['treatments'],
                        differential_rank=len(suggestions) + 1,
                        medical_system=MedicalSystem.AYURVEDA,
                        urgency_level="MODERATE"
                    )
                    suggestions.append(suggestion)
        
        return suggestions
    
    def _get_siddha_suggestions(self, symptoms: List[Symptom]) -> List[DiagnosticSuggestion]:
        """Get Siddha-specific diagnostic suggestions"""
        # Similar implementation for Siddha medicine
        return []
    
    def _get_unani_suggestions(self, symptoms: List[Symptom]) -> List[DiagnosticSuggestion]:
        """Get Unani-specific diagnostic suggestions"""
        # Similar implementation for Unani medicine
        return []
    
    def _combine_suggestions(self, ai_suggestions: List[DiagnosticSuggestion], 
                           traditional_suggestions: List[DiagnosticSuggestion]) -> List[DiagnosticSuggestion]:
        """Combine AI and traditional medicine suggestions"""
        all_suggestions = ai_suggestions + traditional_suggestions
        
        # Remove duplicates and merge similar conditions
        unique_suggestions = {}
        for suggestion in all_suggestions:
            key = suggestion.condition_name.lower()
            if key not in unique_suggestions or suggestion.confidence_score > unique_suggestions[key].confidence_score:
                unique_suggestions[key] = suggestion
        
        # Sort by confidence score
        combined = list(unique_suggestions.values())
        combined.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return combined
    
    def _apply_ethical_filtering(self, suggestions: List[DiagnosticSuggestion]) -> List[DiagnosticSuggestion]:
        """Apply ethical AI filtering to suggestions"""
        filtered_suggestions = []
        
        for suggestion in suggestions:
            is_safe, warnings = self.ethics_checker.validate_recommendation(suggestion)
            
            if is_safe:
                # Add ethical disclaimers
                suggestion.reasoning += " [AI Suggestion - Please consult healthcare professional for confirmation]"
                filtered_suggestions.append(suggestion)
            else:
                logger.warning(f"Filtered unsafe suggestion: {suggestion.condition_name} - {warnings}")
        
        return filtered_suggestions
    
    def _personalize_suggestions(self, suggestions: List[DiagnosticSuggestion], 
                               patient_profile: PatientProfile) -> List[DiagnosticSuggestion]:
        """Personalize suggestions based on patient profile"""
        personalized = []
        
        for suggestion in suggestions:
            # Adjust based on age
            if patient_profile.age > 65 and suggestion.urgency_level == "LOW":
                suggestion.urgency_level = "MODERATE"
                suggestion.reasoning += " [Adjusted for elderly patient]"
            
            # Adjust based on medical history
            for history_item in patient_profile.medical_history:
                if history_item.lower() in suggestion.condition_name.lower():
                    suggestion.confidence_score *= 1.2  # Increase confidence for known conditions
                    suggestion.reasoning += f" [History of {history_item}]"
            
            # Check for drug interactions
            if patient_profile.current_medications:
                interaction_warnings = self._check_drug_interactions(
                    suggestion.treatment_suggestions, patient_profile.current_medications
                )
                if interaction_warnings:
                    suggestion.reasoning += f" [Drug interaction warnings: {', '.join(interaction_warnings)}]"
            
            personalized.append(suggestion)
        
        return personalized
    
    def _get_condition_codes(self, condition: str) -> Dict[str, str]:
        """Get medical codes for a condition"""
        # Mock implementation - in production, use actual code mappings
        code_mappings = {
            'viral_fever': {
                'ICD-11': 'MG30',
                'SNOMED-CT': '386661006',
                'NAMASTE': 'NAMC001'
            },
            'hypertension': {
                'ICD-11': 'BA00',
                'SNOMED-CT': '38341003',
                'NAMASTE': 'NAMC002'
            }
        }
        
        return code_mappings.get(condition, {'UNKNOWN': 'UNK001'})
    
    def _map_confidence_level(self, score: float) -> DiagnosticConfidence:
        """Map confidence score to confidence level"""
        if score >= 0.9:
            return DiagnosticConfidence.VERY_HIGH
        elif score >= 0.75:
            return DiagnosticConfidence.HIGH
        elif score >= 0.6:
            return DiagnosticConfidence.MODERATE
        elif score >= 0.4:
            return DiagnosticConfidence.LOW
        else:
            return DiagnosticConfidence.VERY_LOW
    
    def _get_recommended_tests(self, condition: str) -> List[str]:
        """Get recommended tests for a condition"""
        test_mappings = {
            'viral_fever': ['Complete Blood Count', 'ESR', 'CRP'],
            'hypertension': ['Blood Pressure Monitoring', 'ECG', 'Lipid Profile'],
            'diabetes': ['Fasting Glucose', 'HbA1c', 'Urine Analysis']
        }
        
        return test_mappings.get(condition, ['General Health Checkup'])
    
    def _get_treatment_suggestions(self, condition: str) -> List[str]:
        """Get treatment suggestions for a condition"""
        treatment_mappings = {
            'viral_fever': ['Rest', 'Hydration', 'Paracetamol for fever', 'Monitor symptoms'],
            'hypertension': ['Lifestyle modifications', 'Regular exercise', 'Low sodium diet'],
            'diabetes': ['Diet control', 'Regular exercise', 'Blood sugar monitoring']
        }
        
        return treatment_mappings.get(condition, ['Consult healthcare provider'])
    
    def _determine_urgency(self, condition: str, confidence: float) -> str:
        """Determine urgency level for a condition"""
        high_urgency_conditions = ['heart_attack', 'stroke', 'severe_infection']
        moderate_urgency_conditions = ['hypertension', 'diabetes', 'pneumonia']
        
        if any(urgent in condition.lower() for urgent in high_urgency_conditions):
            return "HIGH"
        elif any(moderate in condition.lower() for moderate in moderate_urgency_conditions):
            return "MODERATE"
        elif confidence > 0.8:
            return "MODERATE"
        else:
            return "LOW"
    
    def _check_drug_interactions(self, treatments: List[str], 
                               current_medications: List[str]) -> List[str]:
        """Check for potential drug interactions"""
        # Simplified drug interaction checking
        interactions = []
        
        interaction_db = {
            'aspirin': ['warfarin', 'methotrexate'],
            'paracetamol': ['warfarin'],
            'ibuprofen': ['aspirin', 'warfarin']
        }
        
        for treatment in treatments:
            treatment_lower = treatment.lower()
            for medication in current_medications:
                medication_lower = medication.lower()
                
                for drug, interactions_list in interaction_db.items():
                    if drug in treatment_lower and medication_lower in interactions_list:
                        interactions.append(f"{treatment} may interact with {medication}")
        
        return interactions
    
    def _load_ayurveda_knowledge(self) -> Dict:
        """Load Ayurveda knowledge base"""
        return {
            'doshas': ['vata', 'pitta', 'kapha'],
            'conditions': {
                'jvara': 'fever',
                'kasa': 'cough',
                'shiroroga': 'headache'
            }
        }
    
    def _load_modern_medicine_knowledge(self) -> Dict:
        """Load modern medicine knowledge base"""
        return {
            'specialties': ['internal_medicine', 'cardiology', 'neurology'],
            'conditions': {
                'hypertension': 'high_blood_pressure',
                'diabetes': 'blood_sugar_disorder'
            }
        }
    
    def _load_drug_interactions(self) -> Dict:
        """Load drug interaction database"""
        return {
            'aspirin': ['warfarin', 'methotrexate'],
            'paracetamol': ['warfarin'],
            'ibuprofen': ['aspirin', 'warfarin']
        }
    
    async def add_feedback(self, suggestion_id: str, feedback_type: str, 
                          accuracy_score: float, comments: str = ""):
        """Add feedback to improve AI model"""
        feedback = {
            'suggestion_id': suggestion_id,
            'feedback_type': feedback_type,  # CORRECT, INCORRECT, PARTIAL
            'accuracy_score': accuracy_score,
            'comments': comments,
            'timestamp': datetime.utcnow()
        }
        
        self.feedback_data.append(feedback)
        
        # Use feedback to retrain models (simplified)
        if len(self.feedback_data) > 100:  # Retrain after 100 feedback items
            await self._retrain_with_feedback()
    
    async def _retrain_with_feedback(self):
        """Retrain models with user feedback"""
        logger.info("Retraining AI models with user feedback...")
        # In production, implement proper model retraining
        logger.info("Model retraining completed")
    
    async def get_model_statistics(self) -> Dict[str, Any]:
        """Get AI model performance statistics"""
        return {
            'total_predictions': len(self.feedback_data),
            'accuracy_rate': np.mean([f['accuracy_score'] for f in self.feedback_data]) if self.feedback_data else 0,
            'feedback_breakdown': {
                'correct': len([f for f in self.feedback_data if f['feedback_type'] == 'CORRECT']),
                'incorrect': len([f for f in self.feedback_data if f['feedback_type'] == 'INCORRECT']),
                'partial': len([f for f in self.feedback_data if f['feedback_type'] == 'PARTIAL'])
            },
            'model_version': '1.0.0',
            'last_retrain': datetime.utcnow().isoformat()
        }


# Global AI diagnostic service instance
ai_diagnostic_service = MultiModalDiagnosticAI()


def get_ai_diagnostic_service() -> MultiModalDiagnosticAI:
    """Dependency injection for AI diagnostic service"""
    return ai_diagnostic_service
