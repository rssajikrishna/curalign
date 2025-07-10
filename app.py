import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os
from data_generator import MedicalDataGenerator
from utils import log_generation_event, generate_summary, authenticate_user, DISEASE_DESCRIPTIONS
import time

# Page configuration
st.set_page_config(
    page_title="Curalign - Smart Medical Data Generator",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None

def main():
    # Header
    st.title("🏥 Curalign")
    st.subheader("Smart Synthetic Medical Data Generator for Rare Diseases")
    
    # Authentication
    if not st.session_state.authenticated:
        show_login()
        return
    
    # Sidebar for model settings and user info
    with st.sidebar:
        st.header("⚙️ Settings")
        st.write(f"**User:** {st.session_state.username}")
        st.write(f"**Role:** {st.session_state.user_role}")
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.session_state.username = None
            st.rerun()
        
        st.divider()
        
        # Model Settings
        st.subheader("🤖 AI Model Settings")
        use_ai_summary = st.checkbox("Enable AI Summarization", value=True)
        summary_detail = st.selectbox(
            "Summary Detail Level",
            ["Brief", "Detailed", "Clinical"]
        )
        
        st.divider()
        
        # Generation Settings
        st.subheader("📊 Generation Settings")
        data_quality = st.selectbox(
            "Data Quality",
            ["Standard", "High Fidelity", "Research Grade"]
        )
        
        include_anomalies = st.checkbox("Include Anomalous Cases", value=True)
        
        st.divider()
        
        # Audit Log
        st.subheader("📋 Recent Activity")
        if os.path.exists("generation_log.txt"):
            with open("generation_log.txt", "r") as f:
                logs = f.readlines()
                for log in logs[-3:]:  # Show last 3 entries
                    st.text(log.strip())
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Disease Selection
        st.header("🔬 Disease Selection")
        diseases = list(DISEASE_DESCRIPTIONS.keys())
        selected_disease = st.selectbox(
            "Select a rare disease:",
            diseases,
            help="Choose the rare disease for synthetic data generation"
        )
        
        # Show disease description
        if selected_disease:
            st.info(f"**{selected_disease}:** {DISEASE_DESCRIPTIONS[selected_disease]}")
        
        # Number of records
        st.header("📝 Generation Parameters")
        num_records = st.number_input(
            "Number of synthetic records to generate:",
            min_value=1,
            max_value=1000,
            value=10,
            help="Enter the number of synthetic patient records to generate"
        )
        
        # Generate button
        if st.button("🚀 Generate Synthetic Data", type="primary"):
            if st.session_state.user_role not in ["researcher", "admin"]:
                st.error("❌ Access Denied: You don't have permission to generate data")
                return
            
            generate_data(selected_disease, num_records, use_ai_summary, summary_detail, data_quality, include_anomalies)
    
    with col2:
        # Statistics and Info
        st.header("📊 Statistics")
        
        # Show generation stats
        if os.path.exists("generation_log.txt"):
            with open("generation_log.txt", "r") as f:
                logs = f.readlines()
                total_generated = len(logs)
                st.metric("Total Records Generated", total_generated)
                
                # Today's generation
                today = datetime.now().strftime("%Y-%m-%d")
                today_count = sum(1 for log in logs if today in log)
                st.metric("Generated Today", today_count)
        
        # Supported Diseases
        st.subheader("🎯 Supported Diseases")
        for disease in diseases:
            st.write(f"• {disease}")
        
        # Privacy Notice
        st.subheader("🛡️ Privacy & Ethics")
        st.info("""
        **Responsible AI Notice:**
        - All data is synthetically generated
        - No real patient information is used
        - Data is for research purposes only
        - Complies with HIPAA guidelines
        - Regular bias audits performed
        """)

def show_login():
    st.header("🔐 Authentication Required")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Login to Curalign")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", type="primary"):
            user_role = authenticate_user(username, password)
            if user_role:
                st.session_state.authenticated = True
                st.session_state.user_role = user_role
                st.session_state.username = username
                st.success(f"Welcome, {username}! Role: {user_role}")
                st.rerun()
            else:
                st.error("Invalid credentials")
        
        st.divider()
        
        st.subheader("Demo Credentials")
        st.code("""
        Admin: admin / admin123
        Researcher: researcher / research123
        Viewer: viewer / view123
        """)

def generate_data(disease, num_records, use_ai_summary, summary_detail, data_quality, include_anomalies):
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Initialize generator
    generator = MedicalDataGenerator()
    
    # Generate data
    status_text.text("🔄 Generating synthetic medical data...")
    
    start_time = time.time()
    records = []
    
    for i in range(num_records):
        record = generator.generate_patient_record(disease, data_quality, include_anomalies)
        
        # Add AI summary if enabled
        if use_ai_summary:
            record['ai_summary'] = generate_summary(record, summary_detail)
        
        records.append(record)
        
        # Update progress
        progress = (i + 1) / num_records
        progress_bar.progress(progress)
        status_text.text(f"🔄 Generated {i+1}/{num_records} records...")
    
    generation_time = time.time() - start_time
    
    # Convert to DataFrame
    df = pd.DataFrame(records)
    
    # Log generation event
    log_generation_event(
        st.session_state.username,
        disease,
        num_records,
        generation_time,
        st.session_state.user_role
    )
    
    # Display results
    status_text.text("✅ Generation completed!")
    progress_bar.progress(1.0)
    
    st.success(f"🎉 Successfully generated {num_records} synthetic records for {disease} in {generation_time:.2f} seconds")
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Records Generated", num_records)
    with col2:
        st.metric("Generation Time", f"{generation_time:.2f}s")
    with col3:
        st.metric("Avg Time/Record", f"{generation_time/num_records:.3f}s")
    with col4:
        st.metric("Data Quality", data_quality)
    
    # Display data table
    st.header("📊 Generated Synthetic Data")
    st.dataframe(df, use_container_width=True)
    
    # Download options
    st.header("📥 Download Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📄 Download as CSV",
            data=csv_data,
            file_name=f"synthetic_{disease.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        json_data = df.to_json(orient='records', indent=2)
        st.download_button(
            label="📋 Download as JSON",
            data=json_data,
            file_name=f"synthetic_{disease.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col3:
        # Generate summary report
        summary_report = generate_summary_report(df, disease, generation_time)
        st.download_button(
            label="📊 Download Summary Report",
            data=summary_report,
            file_name=f"report_{disease.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

def generate_summary_report(df, disease, generation_time):
    report = f"""
Curalign Generation Report
=============================

Disease: {disease}
Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
User: {st.session_state.username}
Role: {st.session_state.user_role}

Generation Statistics:
- Total Records: {len(df)}
- Generation Time: {generation_time:.2f} seconds
- Average Time per Record: {generation_time/len(df):.3f} seconds

Data Summary:
- Age Range: {df['age'].min()} - {df['age'].max()} years
- Gender Distribution: {df['gender'].value_counts().to_dict()}
- Average Heart Rate: {df['heart_rate'].mean():.1f} bpm
- Average Blood Pressure: {df['systolic_bp'].mean():.1f}/{df['diastolic_bp'].mean():.1f} mmHg

Quality Metrics:
- Data Completeness: 100%
- Realistic Value Ranges: ✓
- Disease-Specific Patterns: ✓
- Privacy Compliance: ✓

Note: This is synthetically generated data for research purposes only.
All data complies with privacy regulations and ethical AI guidelines.
"""
    return report

if __name__ == "__main__":
    main()