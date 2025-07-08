import json
import logging
from datetime import datetime
import hashlib
import random
import os

# Disease descriptions for the UI
DISEASE_DESCRIPTIONS = {
    "Hemophilia": "A rare bleeding disorder where blood doesn't clot properly due to lack of clotting factors.",
    "ALS (Lou Gehrig's Disease)": "A progressive neurodegenerative disease affecting motor neurons, causing muscle weakness and atrophy.",
    "Cystic Fibrosis": "A genetic disorder affecting the lungs and digestive system, causing thick, sticky mucus production.",
    "Huntington's Disease": "A hereditary brain disorder causing progressive breakdown of nerve cells, affecting movement, cognition, and emotions.",
    "Marfan Syndrome": "A genetic disorder affecting connective tissue, primarily impacting the heart, eyes, blood vessels, and skeleton.",
    "Sickle Cell Disease": "A genetic blood disorder causing red blood cells to become misshapen and break down, leading to pain and organ damage."
}

# Simple user authentication system (in production, use proper authentication)
USER_DATABASE = {
    "admin": {"password": "admin123", "role": "admin"},
    "researcher": {"password": "research123", "role": "researcher"},
    "viewer": {"password": "view123", "role": "viewer"}
}

def authenticate_user(username, password):
    """Simple authentication function"""
    if username in USER_DATABASE:
        stored_password = USER_DATABASE[username]["password"]
        if password == stored_password:
            return USER_DATABASE[username]["role"]
    return None

def log_generation_event(username, disease, num_records, generation_time, user_role):
    """Log generation events to a file for audit purposes"""
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "username": username,
        "user_role": user_role,
        "disease": disease,
        "num_records": num_records,
        "generation_time": generation_time,
        "ip_address": "127.0.0.1"  # In production, get actual IP
    }
    
    # Write to log file
    with open("generation_log.txt", "a") as f:
        f.write(f"{log_entry['timestamp']} | {username} ({user_role}) | {disease} | {num_records} records | {generation_time:.2f}s\n")
    
    # Also log to JSON for structured access
    if not os.path.exists("generation_log.json"):
        with open("generation_log.json", "w") as f:
            json.dump([], f)
    
    with open("generation_log.json", "r") as f:
        logs = json.load(f)
    
    logs.append(log_entry)
    
    with open("generation_log.json", "w") as f:
        json.dump(logs, f, indent=2)

def generate_summary(record, detail_level="Brief"):
    """Generate AI-like summary of patient record"""
    
    # This is a simplified rule-based summary generator
    # In production, this would use actual LLM API calls
    
    if detail_level == "Brief":
        return generate_brief_summary(record)
    elif detail_level == "Detailed":
        return generate_detailed_summary(record)
    elif detail_level == "Clinical":
        return generate_clinical_summary(record)
    else:
        return generate_brief_summary(record)

def generate_brief_summary(record):
    """Generate a brief summary of the patient record"""
    
    summaries = [
        f"Patient {record['patient_id']} is a {record['age']}-year-old {record['gender']} with {record['primary_diagnosis']}.",
        f"Current disease stage: {record['disease_stage']} with {record['diagnosis_confidence'].lower()} confidence.",
        f"Primary symptoms include: {record['primary_symptoms'].split(';')[0]}.",
        f"Patient is currently {record['functional_status'].lower()} and has been diagnosed for {record['months_since_diagnosis']} months."
    ]
    
    return " ".join(summaries)

def generate_detailed_summary(record):
    """Generate a detailed summary of the patient record"""
    
    # Extract key lab results
    lab_results = []
    for key, value in record.items():
        if key.endswith("_status") and value == "Abnormal":
            test_name = key.replace("_status", "")
            lab_results.append(test_name)
    
    summary = f"""
    PATIENT SUMMARY:
    Patient ID: {record['patient_id']}
    Demographics: {record['age']}-year-old {record['gender']} {record['ethnicity']}
    Primary Diagnosis: {record['primary_diagnosis']} ({record['disease_stage']} stage)
    
    CLINICAL PRESENTATION:
    - Symptoms: {record['primary_symptoms']}
    - Functional Status: {record['functional_status']}
    - Comorbidities: {record['comorbidities']}
    
    VITAL SIGNS:
    - Heart Rate: {record['heart_rate']} bpm
    - Blood Pressure: {record['systolic_bp']}/{record['diastolic_bp']} mmHg
    - Respiratory Rate: {record['respiratory_rate']} breaths/min
    - Oxygen Saturation: {record['oxygen_saturation']}%
    
    LABORATORY FINDINGS:
    - Abnormal results: {', '.join(lab_results) if lab_results else 'None'}
    
    TREATMENT:
    - Current medications: {record['current_medications']}
    - Time since diagnosis: {record['months_since_diagnosis']} months
    """
    
    return summary.strip()

def generate_clinical_summary(record):
    """Generate a clinical summary in medical format"""
    
    # Calculate BMI
    bmi = calculate_bmi(record['weight_kg'], record['height_cm'])
    
    # Determine if critically abnormal
    critical_findings = []
    if record['heart_rate'] > 100 or record['heart_rate'] < 60:
        critical_findings.append("Abnormal heart rate")
    if record['oxygen_saturation'] < 90:
        critical_findings.append("Hypoxemia")
    if record['systolic_bp'] > 180 or record['systolic_bp'] < 90:
        critical_findings.append("Blood pressure abnormality")
    
    summary = f"""
    CLINICAL ASSESSMENT - {record['primary_diagnosis']}
    
    CHIEF COMPLAINT: {record['primary_symptoms'].split(';')[0]}
    
    HISTORY OF PRESENT ILLNESS:
    {record['age']}-year-old {record['gender']} with known {record['primary_diagnosis']} 
    (diagnosed {record['months_since_diagnosis']} months ago) presenting with {record['primary_symptoms']}.
    Current disease stage: {record['disease_stage']}.
    
    PHYSICAL EXAMINATION:
    - Vital Signs: BP {record['systolic_bp']}/{record['diastolic_bp']}, HR {record['heart_rate']}, 
      RR {record['respiratory_rate']}, O2 Sat {record['oxygen_saturation']}%, Temp {record['temperature_c']}°C
    - BMI: {bmi}
    - General: {record['functional_status']} patient
    
    ASSESSMENT AND PLAN:
    - Primary diagnosis: {record['primary_diagnosis']} ({record['disease_stage']} stage)
    - Confidence level: {record['diagnosis_confidence']}
    - Current management: {record['current_medications']}
    - Comorbidities: {record['comorbidities']}
    """
    
    if critical_findings:
        summary += f"\n    CRITICAL FINDINGS: {', '.join(critical_findings)}"
    
    return summary.strip()

def calculate_bmi(weight_kg, height_cm):
    """Calculate BMI from weight and height"""
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)

def validate_medical_record(record):
    """Validate medical record for completeness and accuracy"""
    
    required_fields = [
        'patient_id', 'age', 'gender', 'primary_diagnosis',
        'heart_rate', 'systolic_bp', 'diastolic_bp', 'primary_symptoms'
    ]
    
    validation_results = {
        'is_valid': True,
        'missing_fields': [],
        'warnings': []
    }
    
    # Check required fields
    for field in required_fields:
        if field not in record or record[field] is None:
            validation_results['missing_fields'].append(field)
            validation_results['is_valid'] = False
    
    # Check value ranges
    if 'age' in record:
        if record['age'] < 0 or record['age'] > 120:
            validation_results['warnings'].append('Age out of realistic range')
    
    if 'heart_rate' in record:
        if record['heart_rate'] < 30 or record['heart_rate'] > 200:
            validation_results['warnings'].append('Heart rate out of realistic range')
    
    if 'systolic_bp' in record:
        if record['systolic_bp'] < 50 or record['systolic_bp'] > 300:
            validation_results['warnings'].append('Systolic BP out of realistic range')
    
    return validation_results

def generate_quality_metrics(records):
    """Generate quality metrics for a batch of records"""
    
    if not records:
        return {}
    
    metrics = {
        'total_records': len(records),
        'valid_records': 0,
        'completeness_score': 0,
        'consistency_score': 0,
        'realism_score': 0,
        'diversity_score': 0
    }
    
    # Calculate metrics
    valid_count = 0
    for record in records:
        validation = validate_medical_record(record)
        if validation['is_valid']:
            valid_count += 1
    
    metrics['valid_records'] = valid_count
    metrics['completeness_score'] = (valid_count / len(records)) * 100
    
    # Calculate diversity (unique values for key fields)
    unique_ages = len(set(record.get('age', 0) for record in records))
    unique_symptoms = len(set(record.get('primary_symptoms', '') for record in records))
    max_diversity = min(len(records), 100)  # Cap at 100 for percentage
    
    metrics['diversity_score'] = ((unique_ages + unique_symptoms) / (2 * max_diversity)) * 100
    
    # Simple realism score based on value ranges
    realistic_count = 0
    for record in records:
        if (record.get('age', 0) > 0 and record.get('age', 0) < 120 and
            record.get('heart_rate', 0) > 30 and record.get('heart_rate', 0) < 200):
            realistic_count += 1
    
    metrics['realism_score'] = (realistic_count / len(records)) * 100
    metrics['consistency_score'] = 95.0  # Simplified for demo
    
    return metrics

def export_to_fhir_format(record):
    """Export record to FHIR-like format for interoperability"""
    
    fhir_record = {
        "resourceType": "Patient",
        "id": record['patient_id'],
        "identifier": [
            {
                "system": "urn:oid:1.2.3.4.5",
                "value": record['patient_id']
            }
        ],
        "name": [
            {
                "family": "SyntheticPatient",
                "given": [f"Patient{record['patient_id']}"]
            }
        ],
        "gender": record['gender'].lower(),
        "birthDate": calculate_birth_date(record['age']),
        "address": [
            {
                "use": "home",
                "city": "Synthetic City",
                "country": "US"
            }
        ],
        "extension": [
            {
                "url": "synthetic-flag",
                "valueBoolean": True
            }
        ]
    }
    
    return fhir_record

def calculate_birth_date(age):
    """Calculate birth date from age"""
    from datetime import date
    current_year = date.today().year
    birth_year = current_year - age
    return f"{birth_year}-01-01"

def generate_privacy_report(records):
    """Generate privacy compliance report"""
    
    report = {
        "total_records": len(records),
        "synthetic_flag": all(record.get('synthetic_flag', False) for record in records),
        "privacy_compliant": all(record.get('privacy_compliance', False) for record in records),
        "contains_real_data": False,
        "anonymization_level": "Full",
        "audit_timestamp": datetime.now().isoformat(),
        "compliance_score": 100
    }
    
    # Check for any potential privacy issues
    sensitive_fields = ['name', 'address', 'phone', 'email', 'ssn']
    for record in records:
        for field in sensitive_fields:
            if field in record:
                report['contains_real_data'] = True
                report['compliance_score'] = 0
                break
    
    return report

def generate_export_manifest(records, export_type="csv"):
    """Generate export manifest with metadata"""
    
    manifest = {
        "export_timestamp": datetime.now().isoformat(),
        "export_type": export_type,
        "record_count": len(records),
        "file_size_bytes": len(str(records)),
        "checksum": hashlib.md5(str(records).encode()).hexdigest(),
        "schema_version": "1.0",
        "privacy_compliant": True,
        "synthetic_data": True,
        "fields": list(records[0].keys()) if records else [],
        "generated_by": "GenSynth-Med v1.0"
    }
    
    return manifest

# Error handling and logging setup
def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('gensynth.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

# Configuration management
def load_config():
    """Load configuration from file or environment"""
    config = {
        "max_records_per_generation": 1000,
        "default_data_quality": "Standard",
        "enable_audit_logging": True,
        "privacy_mode": "strict",
        "export_formats": ["csv", "json", "fhir"],
        "supported_diseases": list(DISEASE_DESCRIPTIONS.keys())
    }
    
    # In production, load from config file or environment variables
    return config

# Helper function for demo purposes
def simulate_ai_processing_delay():
    """Simulate AI processing delay for more realistic feel"""
    import time
    time.sleep(random.uniform(0.1, 0.3))  # 100-300ms delay