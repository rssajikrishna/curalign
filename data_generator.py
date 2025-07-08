import random
import json
from datetime import datetime, timedelta
from faker import Faker
import uuid

fake = Faker()

class MedicalDataGenerator:
    def __init__(self):
        self.fake = Faker()
        
        # Disease-specific parameters
        self.disease_params = {
            "Hemophilia": {
                "age_range": (5, 65),
                "gender_bias": {"male": 0.85, "female": 0.15},  # X-linked recessive
                "common_symptoms": [
                    "Easy bruising", "Prolonged bleeding", "Joint pain", 
                    "Muscle bleeding", "Nosebleeds", "Bleeding gums"
                ],
                "lab_tests": {
                    "PTT": {"normal": (25, 35), "abnormal": (50, 120)},
                    "Factor_VIII": {"normal": (50, 150), "abnormal": (0, 30)},
                    "Factor_IX": {"normal": (50, 150), "abnormal": (0, 30)},
                    "Platelet_count": {"normal": (150, 450), "abnormal": (150, 450)}
                },
                "vitals_adjustment": {
                    "heart_rate": (-5, 5),
                    "blood_pressure": (-10, 10)
                }
            },
            "ALS (Lou Gehrig's Disease)": {
                "age_range": (40, 70),
                "gender_bias": {"male": 0.6, "female": 0.4},
                "common_symptoms": [
                    "Muscle weakness", "Muscle twitching", "Difficulty swallowing",
                    "Speech problems", "Muscle cramps", "Breathing difficulties"
                ],
                "lab_tests": {
                    "CK": {"normal": (30, 200), "abnormal": (300, 1000)},
                    "EMG_abnormal": {"normal": (0, 10), "abnormal": (70, 100)},
                    "Nerve_conduction": {"normal": (40, 60), "abnormal": (20, 39)},
                    "Protein_CSF": {"normal": (15, 45), "abnormal": (50, 100)}
                },
                "vitals_adjustment": {
                    "heart_rate": (-10, 15),
                    "respiratory_rate": (2, 8)
                }
            },
            "Cystic Fibrosis": {
                "age_range": (1, 40),
                "gender_bias": {"male": 0.5, "female": 0.5},
                "common_symptoms": [
                    "Persistent cough", "Thick mucus", "Lung infections",
                    "Poor growth", "Salty skin", "Digestive problems"
                ],
                "lab_tests": {
                    "Sweat_chloride": {"normal": (0, 29), "abnormal": (60, 120)},
                    "FEV1_percent": {"normal": (80, 120), "abnormal": (30, 79)},
                    "Pseudomonas": {"normal": (0, 0), "abnormal": (1, 1)},
                    "Pancreatic_enzymes": {"normal": (100, 300), "abnormal": (10, 99)}
                },
                "vitals_adjustment": {
                    "respiratory_rate": (5, 15),
                    "oxygen_saturation": (-10, -2)
                }
            },
            "Huntington's Disease": {
                "age_range": (30, 60),
                "gender_bias": {"male": 0.5, "female": 0.5},
                "common_symptoms": [
                    "Involuntary movements", "Cognitive decline", "Emotional problems",
                    "Difficulty walking", "Speech problems", "Memory loss"
                ],
                "lab_tests": {
                    "CAG_repeats": {"normal": (10, 35), "abnormal": (40, 80)},
                    "Brain_volume": {"normal": (1200, 1600), "abnormal": (800, 1199)},
                    "Dopamine_level": {"normal": (0.5, 3.0), "abnormal": (0.1, 0.4)},
                    "Motor_score": {"normal": (0, 10), "abnormal": (20, 80)}
                },
                "vitals_adjustment": {
                    "heart_rate": (-5, 10),
                    "blood_pressure": (-5, 15)
                }
            },
            "Marfan Syndrome": {
                "age_range": (10, 50),
                "gender_bias": {"male": 0.5, "female": 0.5},
                "common_symptoms": [
                    "Tall stature", "Long limbs", "Heart problems",
                    "Eye problems", "Spine curvature", "Chest deformity"
                ],
                "lab_tests": {
                    "Aortic_root": {"normal": (20, 37), "abnormal": (40, 60)},
                    "Arm_span_ratio": {"normal": (0.95, 1.05), "abnormal": (1.05, 1.15)},
                    "Lens_dislocation": {"normal": (0, 0), "abnormal": (1, 1)},
                    "Fibrillin_mutation": {"normal": (0, 0), "abnormal": (1, 1)}
                },
                "vitals_adjustment": {
                    "heart_rate": (-10, 20),
                    "blood_pressure": (-20, 5)
                }
            },
            "Sickle Cell Disease": {
                "age_range": (1, 50),
                "gender_bias": {"male": 0.5, "female": 0.5},
                "common_symptoms": [
                    "Pain crises", "Fatigue", "Swelling", "Frequent infections",
                    "Vision problems", "Delayed growth"
                ],
                "lab_tests": {
                    "HbS_percent": {"normal": (0, 5), "abnormal": (70, 95)},
                    "Hemoglobin": {"normal": (12, 16), "abnormal": (6, 10)},
                    "Reticulocyte": {"normal": (0.5, 2.5), "abnormal": (5, 20)},
                    "Bilirubin": {"normal": (0.3, 1.2), "abnormal": (2, 10)}
                },
                "vitals_adjustment": {
                    "heart_rate": (10, 25),
                    "respiratory_rate": (2, 8)
                }
            }
        }
    
    def generate_patient_record(self, disease, data_quality="Standard", include_anomalies=True):
        """Generate a complete synthetic patient record for the specified disease"""
        
        # Get disease parameters
        params = self.disease_params.get(disease, self.disease_params["Hemophilia"])
        
        # Generate basic demographics
        record = self._generate_demographics(params)
        
        # Generate vitals
        record.update(self._generate_vitals(params))
        
        # Generate symptoms
        record.update(self._generate_symptoms(params, include_anomalies))
        
        # Generate lab tests
        record.update(self._generate_lab_tests(params, data_quality))
        
        # Generate diagnosis and medical history
        record.update(self._generate_diagnosis_info(disease, params))
        
        # Add metadata
        record.update(self._generate_metadata(disease, data_quality))
        
        return record
    
    def _generate_demographics(self, params):
        """Generate basic demographic information"""
        
        # Age based on disease-specific range
        age_min, age_max = params["age_range"]
        age = random.randint(age_min, age_max)
        
        # Gender with disease-specific bias
        gender_probs = params["gender_bias"]
        gender = random.choices(
            list(gender_probs.keys()),
            weights=list(gender_probs.values())
        )[0]
        
        return {
            "patient_id": str(uuid.uuid4())[:8],
            "age": age,
            "gender": gender,
            "ethnicity": random.choice([
                "Caucasian", "African American", "Hispanic", "Asian", 
                "Native American", "Other"
            ]),
            "height_cm": random.randint(150, 190) if gender == "male" else random.randint(140, 180),
            "weight_kg": random.randint(50, 100) if gender == "male" else random.randint(45, 85),
        }
    
    def _generate_vitals(self, params):
        """Generate vital signs with disease-specific adjustments"""
        
        # Base vital signs
        base_vitals = {
            "heart_rate": random.randint(60, 100),
            "systolic_bp": random.randint(110, 140),
            "diastolic_bp": random.randint(70, 90),
            "respiratory_rate": random.randint(12, 20),
            "temperature_c": round(random.uniform(36.1, 37.2), 1),
            "oxygen_saturation": random.randint(95, 100)
        }
        
        # Apply disease-specific adjustments
        adjustments = params.get("vitals_adjustment", {})
        
        for vital, (min_adj, max_adj) in adjustments.items():
            if vital in base_vitals:
                adjustment = random.randint(min_adj, max_adj)
                base_vitals[vital] = max(0, base_vitals[vital] + adjustment)
        
        # Ensure reasonable limits
        base_vitals["heart_rate"] = max(40, min(200, base_vitals["heart_rate"]))
        base_vitals["oxygen_saturation"] = max(70, min(100, base_vitals["oxygen_saturation"]))
        
        return base_vitals
    
    def _generate_symptoms(self, params, include_anomalies):
        """Generate disease-specific symptoms"""
        
        common_symptoms = params["common_symptoms"]
        
        # Select 3-6 symptoms
        num_symptoms = random.randint(3, 6)
        selected_symptoms = random.sample(common_symptoms, min(num_symptoms, len(common_symptoms)))
        
        # Add severity and duration
        symptoms_data = []
        for symptom in selected_symptoms:
            severity = random.choice(["Mild", "Moderate", "Severe"])
            duration = random.choice([
                "< 1 week", "1-4 weeks", "1-6 months", "> 6 months"
            ])
            symptoms_data.append(f"{symptom} ({severity}, {duration})")
        
        # Occasionally add atypical symptoms if anomalies are enabled
        if include_anomalies and random.random() < 0.2:
            atypical_symptoms = [
                "Unusual fatigue", "Cognitive changes", "Sleep disturbances",
                "Mood changes", "Appetite changes"
            ]
            atypical = random.choice(atypical_symptoms)
            symptoms_data.append(f"{atypical} (Atypical)")
        
        return {
            "primary_symptoms": "; ".join(symptoms_data),
            "symptom_count": len(symptoms_data),
            "severity_score": random.randint(1, 10)
        }
    
    def _generate_lab_tests(self, params, data_quality):
        """Generate laboratory test results"""
        
        lab_tests = params["lab_tests"]
        results = {}
        
        for test_name, ranges in lab_tests.items():
            # Determine if result should be normal or abnormal
            # Higher quality data has more consistent abnormal results
            abnormal_probability = 0.8 if data_quality == "Research Grade" else 0.7
            
            if random.random() < abnormal_probability:
                # Abnormal result
                min_val, max_val = ranges["abnormal"]
                value = round(random.uniform(min_val, max_val), 2)
                status = "Abnormal"
            else:
                # Normal result
                min_val, max_val = ranges["normal"]
                value = round(random.uniform(min_val, max_val), 2)
                status = "Normal"
            
            results[f"{test_name}_value"] = value
            results[f"{test_name}_status"] = status
        
        return results
    
    def _generate_diagnosis_info(self, disease, params):
        """Generate diagnosis-related information"""
        
        # Disease stage/severity
        stages = ["Early", "Mild", "Moderate", "Severe", "End-stage"]
        stage = random.choice(stages)
        
        # Confidence level
        confidence = random.choice(["High", "Medium", "Low"])
        
        # Time since diagnosis
        months_since_diagnosis = random.randint(0, 120)  # 0-10 years
        
        return {
            "primary_diagnosis": disease,
            "disease_stage": stage,
            "diagnosis_confidence": confidence,
            "months_since_diagnosis": months_since_diagnosis,
            "comorbidities": self._generate_comorbidities(),
            "current_medications": self._generate_medications(disease),
            "functional_status": random.choice([
                "Independent", "Partially dependent", "Dependent", "Bedridden"
            ])
        }
    
    def _generate_comorbidities(self):
        """Generate common comorbidities"""
        common_comorbidities = [
            "Hypertension", "Diabetes", "Depression", "Anxiety",
            "Osteoarthritis", "Chronic pain", "Sleep apnea"
        ]
        
        num_comorbidities = random.randint(0, 3)
        if num_comorbidities == 0:
            return "None"
        
        return "; ".join(random.sample(common_comorbidities, num_comorbidities))
    
    def _generate_medications(self, disease):
        """Generate disease-specific medications"""
        
        medication_map = {
            "Hemophilia": ["Factor concentrates", "Desmopressin", "Antifibrinolytics"],
            "ALS (Lou Gehrig's Disease)": ["Riluzole", "Edaravone", "Baclofen"],
            "Cystic Fibrosis": ["Ivacaftor", "Lumacaftor", "Pancreatic enzymes"],
            "Huntington's Disease": ["Tetrabenazine", "Deutetrabenazine", "Haloperidol"],
            "Marfan Syndrome": ["Beta-blockers", "ACE inhibitors", "Calcium channel blockers"],
            "Sickle Cell Disease": ["Hydroxyurea", "Voxelotor", "Folic acid"]
        }
        
        disease_meds = medication_map.get(disease, ["Supportive care"])
        num_meds = random.randint(1, min(3, len(disease_meds)))
        
        return "; ".join(random.sample(disease_meds, num_meds))
    
    def _generate_metadata(self, disease, data_quality):
        """Generate metadata for the record"""
        
        return {
            "record_id": str(uuid.uuid4()),
            "generated_timestamp": datetime.now().isoformat(),
            "data_quality": data_quality,
            "synthetic_flag": True,
            "disease_category": disease,
            "generation_version": "1.0",
            "privacy_compliant": True
        }

# Additional utility functions for specific calculations
def calculate_bmi(weight_kg, height_cm):
    """Calculate BMI from weight and height"""
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)

def generate_genetic_profile(disease):
    """Generate genetic markers for specific diseases"""
    genetic_profiles = {
        "Hemophilia": {
            "chromosome": "X",
            "mutation_type": random.choice(["Point mutation", "Deletion", "Inversion"]),
            "inheritance": "X-linked recessive"
        },
        "Huntington's Disease": {
            "chromosome": "4",
            "mutation_type": "CAG repeat expansion",
            "inheritance": "Autosomal dominant"
        },
        "Cystic Fibrosis": {
            "chromosome": "7",
            "mutation_type": random.choice(["ΔF508", "G542X", "N1303K"]),
            "inheritance": "Autosomal recessive"
        }
    }
    
    return genetic_profiles.get(disease, {})