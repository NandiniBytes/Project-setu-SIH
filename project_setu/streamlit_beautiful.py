"""
Project Setu - Beautiful Working Interface
Fixed HTML rendering issues, added AI chatbot and analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import time
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Project Setu - NAMASTE Integration",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'selected_codes' not in st.session_state:
    st.session_state.selected_codes = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'show_info_page' not in st.session_state:
    st.session_state.show_info_page = False
if 'show_abha_info' not in st.session_state:
    st.session_state.show_abha_info = False
if 'show_login' not in st.session_state:
    st.session_state.show_login = False

# Beautiful CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

.stApp {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #fff8f0 0%, #f0f8f0 50%, #f8f8ff 100%);
}

/* Hero Section */
.hero-section {
    background: linear-gradient(135deg, #ff6b35 0%, #f7931e 30%, #4caf50 70%, #2e7d32 100%);
    color: white;
    padding: 3rem 2rem;
    border-radius: 20px;
    margin: 1rem 0;
    text-align: center;
    box-shadow: 0 15px 35px rgba(255, 107, 53, 0.3);
}

/* Modern Cards */
.modern-card {
    background: white;
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 107, 53, 0.1);
    transition: all 0.3s ease;
}

.modern-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(255, 107, 53, 0.2);
}

/* Chat Interface */
.chat-container {
    max-height: 400px;
    overflow-y: auto;
    padding: 1rem;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    background: #f8f9fa;
}

.user-message {
    background: #ff6b35;
    color: white;
    padding: 0.8rem;
    border-radius: 15px 15px 5px 15px;
    margin: 0.5rem 0;
    margin-left: 20%;
}

.bot-message {
    background: #4caf50;
    color: white;
    padding: 0.8rem;
    border-radius: 15px 15px 15px 5px;
    margin: 0.5rem 0;
    margin-right: 20%;
}
</style>
""", unsafe_allow_html=True)

class ProjectSetuApp:
    """Beautiful Project Setu Application"""
    
    def __init__(self):
        self.api_base = "http://localhost:8000/api"
    
    def show_landing_page(self):
        """Beautiful landing page"""
        # Hero section
        st.markdown("""
        <div class="hero-section">
            <h1 style="font-size: 4rem; margin: 0;">🏥 Project Setu</h1>
            <h2 style="font-size: 2rem; margin: 1rem 0;">Bridging Millennia of Wisdom with Modern Medicine</h2>
            <p style="font-size: 1.2rem;">Advanced NAMASTE Terminology Integration with AI-Powered Assistance</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Central content
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Medical animation placeholder
            st.markdown("""
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 6rem; margin: 1rem 0;">🩺⚡🧬</div>
                <h3>Advanced Healthcare Technology</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            button_col1, button_col2 = st.columns(2)
            
            with button_col1:
                if st.button("🆔 I have an ABHA ID", key="has_abha", use_container_width=True):
                    st.session_state.show_login = True
                    st.session_state.show_abha_info = False
                    st.rerun()
            
            with button_col2:
                if st.button("❓ What is ABHA?", key="what_abha", use_container_width=True):
                    st.session_state.show_abha_info = True
                    st.session_state.show_login = False
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("🚀 Discover Project Setu", key="discover", use_container_width=True):
                st.session_state.show_info_page = True
                st.rerun()
        
        # Show ABHA info or login (mutually exclusive)
        if st.session_state.get('show_abha_info', False):
            self.show_abha_info()
        elif st.session_state.get('show_login', False):
            self.show_login_form()
        
        # Features showcase
        if not st.session_state.get('show_abha_info', False) and not st.session_state.get('show_login', False):
            st.markdown("---")
            st.markdown("## 🌟 Platform Features")
            
            feat_col1, feat_col2, feat_col3, feat_col4 = st.columns(4)
            
            features = [
                ("🔍", "Smart Search", "AI-powered search across 4,478+ terms"),
                ("🔄", "Code Mapping", "Translate between terminologies"),
                ("🤖", "AI Diagnostics", "Revolutionary diagnostic assistance"),
                ("📊", "Analytics", "Real-time insights and reporting")
            ]
            
            for col, (icon, title, desc) in zip([feat_col1, feat_col2, feat_col3, feat_col4], features):
                with col:
                    st.markdown(f"""
                    <div class="modern-card" style="text-align: center;">
                        <div style="font-size: 2.5rem; margin-bottom: 1rem;">{icon}</div>
                        <h4 style="color: #ff6b35;">{title}</h4>
                        <p style="color: #666;">{desc}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    def show_abha_info(self):
        """Show ABHA information"""
        st.markdown("## 🆔 ABHA - India's National Health ID")
        
        info_col1, info_col2 = st.columns([2, 1])
        
        with info_col1:
            st.info("""
            **ABHA (Ayushman Bharat Health Account)** is India's revolutionary national health ID system:
            
            ✅ **Single Health Identity** across all healthcare providers
            ✅ **Secure Access** to your complete medical history  
            ✅ **Interoperability** between hospitals, clinics, and labs
            ✅ **Insurance Integration** for seamless claims processing
            
            **How to Get Your ABHA:**
            1. **Visit:** https://abha.abdm.gov.in/
            2. **Register:** Using Mobile + OTP or Aadhaar verification
            3. **Verify:** Complete KYC process
            4. **Receive:** Your 14-digit ABHA Number
            5. **Create:** Username and secure password
            """)
        
        with info_col2:
            st.success("""
            **🎮 Demo Credentials**
            
            For testing Project Setu:
            
            **ABHA ID:** `12-3456-7890-1234`
            **Password:** `testpassword`
            
            *These are demo credentials for testing. In production, use your real ABHA ID.*
            """)
        
        if st.button("🔙 Back to Home", key="back_from_abha"):
            st.session_state.show_abha_info = False
            st.rerun()
    
    def show_login_form(self):
        """Beautiful login form"""
        st.markdown("## 🔐 ABHA Authentication")
        
        with st.form("login_form"):
            login_col1, login_col2 = st.columns([2, 1])
            
            with login_col1:
                st.markdown("#### Enter Your ABHA Credentials")
                abha_id = st.text_input("🆔 ABHA ID", placeholder="12-3456-7890-1234")
                password = st.text_input("🔒 Password", type="password")
                remember_me = st.checkbox("🔄 Remember me for 30 days")
            
            with login_col2:
                st.info("""
                **🎮 Demo Credentials:**
                
                **ABHA ID:** `12-3456-7890-1234`
                **Password:** `testpassword`
                
                **Alternative:**
                **ABHA ID:** `98-7654-3210-9876`
                **Password:** `demopassword`
                """)
            
            # Login buttons
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            
            with btn_col1:
                login_clicked = st.form_submit_button("🔐 Login", use_container_width=True)
            
            with btn_col2:
                demo_clicked = st.form_submit_button("🎮 Demo Login", use_container_width=True)
            
            with btn_col3:
                back_clicked = st.form_submit_button("🔙 Back", use_container_width=True)
            
            if login_clicked or demo_clicked:
                if demo_clicked or self.authenticate_user(abha_id, password):
                    st.session_state.authenticated = True
                    st.session_state.user_data = {
                        'abha_id': abha_id if abha_id else '12-3456-7890-1234',
                        'name': 'Dr. Rajesh Kumar',
                        'specialty': 'Ayurveda',
                        'license': 'MED123456'
                    }
                    st.session_state.show_login = False
                    st.success("🎉 Login successful! Welcome to Project Setu!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Try demo credentials.")
            
            if back_clicked:
                st.session_state.show_login = False
                st.rerun()
    
    def show_info_page(self):
        """Component information page"""
        st.markdown("""
        <div class="hero-section">
            <h1>🏥 Project Setu Components</h1>
            <p>Understanding Healthcare Terminology Integration</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🏠 Back to Home"):
            st.session_state.show_info_page = False
            st.rerun()
        
        # Core Terminologies
        with st.expander("🎯 Core Medical Terminologies", expanded=True):
            term_col1, term_col2 = st.columns(2)
            
            with term_col1:
                st.info("""
                **🇮🇳 NAMASTE**
                *National AYUSH Morbidity & Standardized Terminologies Electronic*
                
                • India's official coding for traditional medicine
                • 4,478+ Ayurveda/Siddha/Unani terms
                • Example: NAMC001 = "Jvara" (fever)
                • Portal: namaste.ayush.gov.in
                """)
                
                st.info("""
                **🔬 SNOMED CT**
                *Systematized Nomenclature of Medicine Clinical Terms*
                
                • World's most comprehensive clinical terminology
                • 350,000+ clinical concepts
                • Example: 386661006 = "Fever"
                • Use: Precise clinical documentation
                """)
            
            with term_col2:
                st.info("""
                **🌍 ICD-11**
                *International Classification of Diseases, 11th Revision*
                
                • WHO's global disease classification
                • TM2 module for traditional medicine
                • Example: MG30 = "Fever, unspecified"
                • Use: Insurance claims, global compatibility
                """)
                
                st.info("""
                **🧪 LOINC**
                *Logical Observation Identifiers Names and Codes*
                
                • Universal standard for lab tests
                • 95,000+ observation codes
                • Example: 8310-5 = "Body temperature"
                • Use: Laboratory and vital signs
                """)
        
        # AI & Technology
        with st.expander("🤖 AI & Technology Components"):
            tech_col1, tech_col2 = st.columns(2)
            
            with tech_col1:
                st.success("""
                **🧠 Semantic Search**
                
                • Meaning-based search (not just keywords)
                • Finds related terms across languages
                • Example: "fever" finds "jvara", "pyrexia"
                • Uses AI embeddings and vector databases
                """)
                
                st.success("""
                **🔄 Concept Mapping**
                
                • Translates between medical coding systems
                • NAMASTE → ICD-11 → SNOMED CT
                • Confidence scoring (0-100%)
                • Explains mapping reasoning
                """)
            
            with tech_col2:
                st.success("""
                **🤖 AI Diagnostic Assistant**
                
                • ML-powered diagnostic suggestions
                • Combines traditional + modern medicine
                • Safety checks and emergency detection
                • Personalized recommendations
                """)
                
                st.success("""
                **💬 AI Medical Chatbot**
                
                • Natural language medical queries
                • Real-time terminology assistance
                • Multi-language support
                • Context-aware responses
                """)
    
    def setup_sidebar(self):
        """Setup sidebar for authenticated users"""
        with st.sidebar:
            # User info
            user = st.session_state.user_data
            st.markdown(f"""
            ### 👨‍⚕️ Welcome!
            **Dr.** {user.get('name', 'User')}
            
            **ABHA:** {user.get('abha_id', 'N/A')}
            **Specialty:** {user.get('specialty', 'N/A')}
            """)
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user_data = {}
                st.success("👋 Logged out successfully!")
                time.sleep(1)
                st.rerun()
            
            # Navigation
            st.markdown("---")
            page = st.selectbox(
                "📋 Navigation",
                ["🔍 Smart Search", "🔄 Code Mapping", "📊 Analytics Dashboard", 
                 "📋 Problem List Builder", "🤖 AI Medical Chatbot", "ℹ️ About Components"],
                key="navigation"
            )
            
            # Filters
            st.markdown("---")
            st.markdown("### 🎯 Filters")
            
            system_filter = st.selectbox(
                "System",
                ["All Systems", "NAMASTE", "ICD-11", "SNOMED CT", "LOINC"]
            )
            
            confidence_threshold = st.slider("Confidence", 0, 100, 70)
            
            # Quick stats
            st.markdown("---")
            st.markdown("### 📈 Stats")
            st.metric("Total Codes", "4,478")
            st.metric("Searches Today", "1,247")
            st.metric("Active Users", "42")
            
            return page
    
    def show_smart_search_page(self):
        """Modern search interface"""
        st.markdown("""
        <div class="hero-section">
            <h1>🔍 Intelligent Medical Search</h1>
            <p>Search across NAMASTE, ICD-11, SNOMED CT, and LOINC terminologies</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Search interface
        search_query = st.text_input(
            "Search medical terms...",
            placeholder="e.g., 'fever', 'jvara', 'headache', 'बुखार'",
            key="search_input"
        )
        
        # Search options
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            search_mode = st.selectbox("Mode", ["🧠 Semantic", "🎯 Exact", "🔤 Fuzzy"])
        with col2:
            include_synonyms = st.checkbox("Include synonyms", value=True)
        with col3:
            include_translations = st.checkbox("Include translations", value=True)
        with col4:
            max_results = st.slider("Max results", 5, 20, 10)
        
        # Voice search
        if st.button("🎤 Voice Search"):
            st.info("🎤 Voice search activated! (Demo)")
        
        # Perform search
        if search_query:
            results = self.perform_search(search_query, max_results)
            self.display_search_results(results)
    
    def perform_search(self, query: str, max_results: int) -> List[Dict]:
        """Perform search and return results"""
        # Add to history
        if query not in st.session_state.search_history:
            st.session_state.search_history.append(query)
        
        # Mock results
        results = [
            {
                'code': 'NAMC001',
                'display': 'Jvara (Fever)',
                'definition': 'Elevated body temperature due to various causes in Ayurveda. Characterized by increased Pitta dosha.',
                'system': 'NAMASTE',
                'specialty': 'Ayurveda',
                'confidence': 95,
                'mappings': [
                    {'system': 'ICD-11', 'code': 'MG30', 'display': 'Fever, unspecified'},
                    {'system': 'SNOMED CT', 'code': '386661006', 'display': 'Fever'}
                ],
                'synonyms': ['Jwara', 'Ushna', 'Santapa'],
                'translations': {'hindi': 'बुखार', 'tamil': 'காய்ச்சல்'}
            },
            {
                'code': 'NAMC002',
                'display': 'Shiroroga (Headache)',
                'definition': 'Pain in the head region, often due to Vata-Pitta imbalance.',
                'system': 'NAMASTE',
                'specialty': 'Ayurveda',
                'confidence': 89,
                'mappings': [
                    {'system': 'ICD-11', 'code': 'MB40', 'display': 'Headache'},
                    {'system': 'SNOMED CT', 'code': '25064002', 'display': 'Headache'}
                ],
                'synonyms': ['Shirah Shool', 'Mastaka Ruja'],
                'translations': {'hindi': 'सिरदर्द', 'tamil': 'தலைவலி'}
            },
            {
                'code': 'SNOMED-386661006',
                'display': 'Fever',
                'definition': 'An abnormal increase in body temperature.',
                'system': 'SNOMED CT',
                'specialty': 'General Medicine',
                'confidence': 92,
                'mappings': [
                    {'system': 'NAMASTE', 'code': 'NAMC001', 'display': 'Jvara'},
                    {'system': 'ICD-11', 'code': 'MG30', 'display': 'Fever, unspecified'}
                ]
            }
        ]
        
        return results[:max_results]
    
    def display_search_results(self, results: List[Dict]):
        """Display beautiful search results"""
        if not results:
            st.warning("🔍 No results found. Try different search terms.")
            return
        
        st.markdown(f"### 🎯 Found {len(results)} Results")
        
        for i, result in enumerate(results):
            # Create beautiful result card using Streamlit components
            with st.container():
                # Header
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### {result['display']}")
                    st.caption(f"Code: {result['code']} | System: {result['system']} | Specialty: {result['specialty']}")
                
                with col2:
                    confidence_color = "🟢" if result['confidence'] >= 90 else "🟡" if result['confidence'] >= 70 else "🔴"
                    st.metric("Confidence", f"{result['confidence']}%", delta=confidence_color)
                
                # Definition
                st.markdown(f"**Definition:** {result['definition']}")
                
                # System tags
                tag_col1, tag_col2, tag_col3 = st.columns(3)
                with tag_col1:
                    st.info(f"📊 {result['system']}")
                with tag_col2:
                    st.info(f"⚕️ {result['specialty']}")
                with tag_col3:
                    urgency = result.get('urgency', 'Moderate')
                    st.warning(f"🚨 {urgency} Priority")
                
                # Action buttons
                btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
                
                with btn_col1:
                    if st.button(f"🔍 Details", key=f"details_{i}"):
                        self.show_code_details(result)
                
                with btn_col2:
                    if st.button(f"🔄 Mappings", key=f"mappings_{i}"):
                        self.show_code_mappings(result)
                
                with btn_col3:
                    if st.button(f"➕ Add to List", key=f"add_{i}"):
                        self.add_to_problem_list(result)
                        st.toast(f"✅ Added {result['display']}!")
                
                with btn_col4:
                    if st.button(f"📋 Copy", key=f"copy_{i}"):
                        st.toast(f"📋 {result['code']} copied!")
                
                # Expandable sections
                if result.get('mappings'):
                    with st.expander(f"🔄 Code Mappings ({len(result['mappings'])})"):
                        for mapping in result['mappings']:
                            st.markdown(f"**{mapping['system']}:** `{mapping['code']}` - {mapping['display']}")
                
                if result.get('synonyms') or result.get('translations'):
                    with st.expander("🌐 Synonyms & Translations"):
                        if result.get('synonyms'):
                            st.markdown(f"**Synonyms:** {', '.join(result['synonyms'])}")
                        if result.get('translations'):
                            for lang, trans in result['translations'].items():
                                st.markdown(f"**{lang.title()}:** {trans}")
                
                st.markdown("---")
    
    def show_ai_chatbot_page(self):
        """AI Medical Chatbot Interface"""
        st.markdown("""
        <div class="hero-section">
            <h1>🤖 AI Medical Assistant</h1>
            <p>Your intelligent healthcare terminology companion</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Chat interface
        st.markdown("### 💬 Chat with AI Assistant")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message['type'] == 'user':
                    st.markdown(f"""
                    <div style="text-align: right; margin: 1rem 0;">
                        <div style="background: #ff6b35; color: white; padding: 1rem; border-radius: 15px 15px 5px 15px; display: inline-block; max-width: 70%;">
                            {message['content']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="text-align: left; margin: 1rem 0;">
                        <div style="background: #4caf50; color: white; padding: 1rem; border-radius: 15px 15px 15px 5px; display: inline-block; max-width: 70%;">
                            🤖 {message['content']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Chat input
        with st.form("chat_form", clear_on_submit=True):
            chat_col1, chat_col2 = st.columns([4, 1])
            
            with chat_col1:
                user_input = st.text_input(
                    "Ask anything about medical terminology...",
                    placeholder="e.g., 'What is the ICD-11 code for fever?', 'Explain Jvara in Ayurveda'",
                    label_visibility="collapsed"
                )
            
            with chat_col2:
                send_clicked = st.form_submit_button("💬 Send", use_container_width=True)
            
            if send_clicked and user_input:
                # Add user message
                st.session_state.chat_history.append({
                    'type': 'user',
                    'content': user_input,
                    'timestamp': datetime.now()
                })
                
                # Generate AI response
                ai_response = self.generate_ai_response(user_input)
                st.session_state.chat_history.append({
                    'type': 'bot',
                    'content': ai_response,
                    'timestamp': datetime.now()
                })
                
                st.rerun()
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        quick_col1, quick_col2, quick_col3 = st.columns(3)
        
        with quick_col1:
            if st.button("🔍 Search Fever Terms"):
                self.add_chat_message("Show me all terms related to fever", "What is fever called in different medical systems?")
        
        with quick_col2:
            if st.button("🔄 Explain Code Mapping"):
                self.add_chat_message("Explain code mapping", "Code mapping translates medical terms between different systems like NAMASTE, ICD-11, and SNOMED CT.")
        
        with quick_col3:
            if st.button("🧹 Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()
    
    def show_analytics_dashboard(self):
        """Comprehensive analytics dashboard"""
        st.markdown("""
        <div class="hero-section">
            <h1>📊 Real-time Analytics Dashboard</h1>
            <p>Comprehensive insights into system usage and performance</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Key metrics
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.metric("Total Searches Today", "1,247", delta="12%")
        
        with metric_col2:
            st.metric("Mapping Accuracy", "94.2%", delta="2.1%")
        
        with metric_col3:
            st.metric("Active Users", "42", delta="5")
        
        with metric_col4:
            st.metric("Response Time", "145ms", delta="-23ms")
        
        # Charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("#### 📈 Search Volume Trends")
            # Generate sample data
            dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
            searches = np.random.randint(800, 1500, 30)
            df = pd.DataFrame({'Date': dates, 'Searches': searches})
            
            fig = px.line(df, x='Date', y='Searches', title='Daily Search Volume')
            fig.update_traces(line_color='#ff6b35')
            st.plotly_chart(fig, use_container_width=True)
        
        with chart_col2:
            st.markdown("#### 🎯 System Usage")
            systems = ['NAMASTE', 'ICD-11', 'SNOMED CT', 'LOINC']
            usage = [45, 30, 20, 5]
            
            fig = px.pie(values=usage, names=systems, title='Terminology System Usage')
            fig.update_traces(marker=dict(colors=['#ff6b35', '#4caf50', '#2196f3', '#ff9800']))
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed analytics
        detail_col1, detail_col2 = st.columns(2)
        
        with detail_col1:
            st.markdown("#### 🔍 Top Search Terms")
            top_searches = pd.DataFrame({
                'Term': ['Fever', 'Jvara', 'Headache', 'Cough', 'Pain'],
                'Searches': [156, 142, 98, 87, 76],
                'System': ['Mixed', 'NAMASTE', 'Mixed', 'Mixed', 'Mixed']
            })
            st.dataframe(top_searches, use_container_width=True, hide_index=True)
        
        with detail_col2:
            st.markdown("#### ⚡ Performance Metrics")
            perf_data = {
                'Metric': ['Avg Response Time', 'Cache Hit Rate', 'Error Rate', 'Uptime'],
                'Value': ['145ms', '87.3%', '0.12%', '99.98%'],
                'Status': ['🟢 Good', '🟢 Excellent', '🟢 Excellent', '🟢 Excellent']
            }
            perf_df = pd.DataFrame(perf_data)
            st.dataframe(perf_df, use_container_width=True, hide_index=True)
        
        # Real-time updates
        if st.button("🔄 Refresh Data"):
            st.toast("📊 Analytics data refreshed!")
            st.rerun()
    
    def generate_ai_response(self, user_input: str) -> str:
        """Generate AI chatbot response"""
        user_lower = user_input.lower()
        
        # Simple rule-based responses
        if 'fever' in user_lower or 'jvara' in user_lower:
            return "Fever (Jvara in Ayurveda) is coded as NAMC001 in NAMASTE, MG30 in ICD-11, and 386661006 in SNOMED CT. In Ayurveda, it's considered a Pitta dosha imbalance."
        
        elif 'headache' in user_lower:
            return "Headache (Shiroroga in Ayurveda) is coded as NAMC002 in NAMASTE, MB40 in ICD-11, and 25064002 in SNOMED CT. Traditional treatment includes head massage and pranayama."
        
        elif 'mapping' in user_lower or 'translate' in user_lower:
            return "Code mapping translates medical terms between systems. For example, NAMASTE code NAMC001 (Jvara) maps to ICD-11 MG30 (Fever) with 95% confidence."
        
        elif 'abha' in user_lower:
            return "ABHA (Ayushman Bharat Health Account) is India's national health ID. Get yours at abha.abdm.gov.in. Demo credentials: 12-3456-7890-1234 / testpassword"
        
        else:
            return f"I understand you're asking about '{user_input}'. I can help with medical terminology, code mappings, ABHA information, and diagnostic assistance. Try asking about specific medical terms!"
    
    def add_chat_message(self, user_msg: str, bot_msg: str):
        """Add predefined chat messages"""
        st.session_state.chat_history.extend([
            {'type': 'user', 'content': user_msg, 'timestamp': datetime.now()},
            {'type': 'bot', 'content': bot_msg, 'timestamp': datetime.now()}
        ])
        st.rerun()
    
    def show_code_details(self, code_data: Dict):
        """Show code details"""
        with st.expander(f"📋 Details: {code_data['display']}", expanded=True):
            detail_col1, detail_col2 = st.columns(2)
            
            with detail_col1:
                st.markdown(f"""
                **Code:** `{code_data['code']}`
                **Display:** {code_data['display']}
                **System:** {code_data['system']}
                **Specialty:** {code_data['specialty']}
                **Confidence:** {code_data['confidence']}%
                """)
            
            with detail_col2:
                st.markdown(f"**Definition:** {code_data['definition']}")
                if code_data.get('synonyms'):
                    st.markdown(f"**Synonyms:** {', '.join(code_data['synonyms'])}")
    
    def show_code_mappings(self, code_data: Dict):
        """Show code mappings"""
        with st.expander(f"🔄 Mappings: {code_data['display']}", expanded=True):
            if code_data.get('mappings'):
                for mapping in code_data['mappings']:
                    st.info(f"**{mapping['system']}:** `{mapping['code']}` - {mapping['display']}")
            else:
                st.warning("No mappings available.")
    
    def add_to_problem_list(self, code_data: Dict):
        """Add to problem list"""
        if code_data not in st.session_state.selected_codes:
            st.session_state.selected_codes.append(code_data)
            return True
        return False
    
    def show_problem_list_page(self):
        """Problem list builder"""
        st.markdown("""
        <div class="hero-section">
            <h1>📋 Problem List Builder</h1>
            <p>Create FHIR-compliant problem lists with dual coding</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.selected_codes:
            st.markdown(f"### 📝 Current Problem List ({len(st.session_state.selected_codes)} items)")
            
            for i, code in enumerate(st.session_state.selected_codes):
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{code['display']}** (`{code['code']}`)")
                        st.caption(f"{code['system']} - {code['specialty']}")
                    
                    with col2:
                        st.metric("Confidence", f"{code['confidence']}%")
                    
                    with col3:
                        if st.button(f"🗑️ Remove", key=f"remove_{i}"):
                            st.session_state.selected_codes.pop(i)
                            st.toast("🗑️ Item removed!")
                            st.rerun()
                    
                    st.markdown("---")
            
            # Export options
            st.markdown("### 📤 Export Options")
            
            export_col1, export_col2, export_col3 = st.columns(3)
            
            with export_col1:
                if st.button("📋 Export FHIR Bundle", use_container_width=True):
                    bundle = self.create_fhir_bundle()
                    st.download_button(
                        "💾 Download Bundle",
                        data=json.dumps(bundle, indent=2),
                        file_name="problem_list.json",
                        mime="application/json"
                    )
            
            with export_col2:
                if st.button("📊 Export CSV", use_container_width=True):
                    csv_data = self.create_csv_export()
                    st.download_button(
                        "💾 Download CSV",
                        data=csv_data,
                        file_name="problem_list.csv",
                        mime="text/csv"
                    )
            
            with export_col3:
                if st.button("📄 View FHIR Preview", use_container_width=True):
                    bundle = self.create_fhir_bundle()
                    with st.expander("📋 FHIR Bundle Preview", expanded=True):
                        st.json(bundle)
        
        else:
            st.info("📝 No codes in problem list. Use Smart Search to add medical codes.")
    
    def create_fhir_bundle(self) -> Dict:
        """Create FHIR Bundle"""
        bundle = {
            "resourceType": "Bundle",
            "id": f"problem-list-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "type": "collection",
            "timestamp": datetime.now().isoformat(),
            "entry": []
        }
        
        for code in st.session_state.selected_codes:
            condition = {
                "resource": {
                    "resourceType": "Condition",
                    "id": f"condition-{code['code']}",
                    "code": {
                        "coding": [{
                            "system": f"http://terminology.hl7.org/{code['system'].lower()}",
                            "code": code['code'],
                            "display": code['display']
                        }]
                    },
                    "subject": {"reference": "Patient/example"}
                }
            }
            bundle["entry"].append(condition)
        
        return bundle
    
    def create_csv_export(self) -> str:
        """Create CSV export"""
        df = pd.DataFrame([{
            'Code': code['code'],
            'Display': code['display'],
            'System': code['system'],
            'Specialty': code['specialty'],
            'Confidence': code['confidence']
        } for code in st.session_state.selected_codes])
        
        return df.to_csv(index=False)
    
    def show_code_mapping_page(self):
        """Complete Code Mapping Interface"""
        st.markdown("""
        <div class="hero-section">
            <h1>🔄 Code Mapping & Translation</h1>
            <p>Intelligent translation between NAMASTE, ICD-11, SNOMED CT, and LOINC</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Main mapping interface
        st.markdown("### 🔄 Single Code Translation")
        
        # Source and target selection
        mapping_col1, mapping_col2 = st.columns(2)
        
        with mapping_col1:
            st.markdown("#### 📤 Source Code")
            source_system = st.selectbox(
                "Source System",
                ["NAMASTE", "ICD-11 TM2", "ICD-11 Biomedicine", "SNOMED CT", "LOINC"],
                key="source_system"
            )
            
            # Use example code if set
            default_value = st.session_state.get("example_code", "")
            source_code = st.text_input(
                "Source Code",
                value=default_value,
                placeholder="Enter code to translate (e.g., NAMC001)",
                key="source_code_input",
                help="Enter the medical code you want to translate"
            )
            
            # Quick examples
            st.markdown("**Quick Examples:**")
            example_col1, example_col2 = st.columns(2)
            
            with example_col1:
                if st.button("🔥 NAMC001 (Fever)", key="example1"):
                    st.session_state["example_code"] = "NAMC001"
                    st.rerun()
            
            with example_col2:
                if st.button("🤕 NAMC002 (Headache)", key="example2"):
                    st.session_state["example_code"] = "NAMC002"
                    st.rerun()
        
        with mapping_col2:
            st.markdown("#### 📥 Target System")
            target_system = st.selectbox(
                "Target System",
                ["ICD-11 TM2", "ICD-11 Biomedicine", "SNOMED CT", "LOINC", "NAMASTE"],
                key="target_system"
            )
            
            # Mapping options
            st.markdown("**Mapping Options:**")
            include_partial = st.checkbox("Include partial matches", value=True)
            min_confidence = st.slider("Minimum confidence", 0, 100, 60)
            max_mappings = st.selectbox("Max mappings", [1, 3, 5, 10], index=1)
        
        # Translation button
        if st.button("🔄 Translate Code", use_container_width=True, type="primary"):
            if source_code:
                with st.spinner("🔄 Translating code across terminologies..."):
                    time.sleep(1)  # Simulate processing
                    translation_result = self.translate_code(source_code, source_system, target_system)
                    self.display_translation_result(translation_result)
            else:
                st.warning("⚠️ Please enter a source code to translate")
        
        # Batch translation section
        st.markdown("---")
        st.markdown("### 📊 Batch Code Translation")
        
        batch_col1, batch_col2 = st.columns([2, 1])
        
        with batch_col1:
            st.markdown("#### 📁 Upload CSV File")
            uploaded_file = st.file_uploader(
                "Upload CSV with codes",
                type=['csv'],
                help="CSV should have columns: 'code', 'system'"
            )
            
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.success(f"✅ Loaded {len(df)} codes for translation")
                    st.dataframe(df.head(), use_container_width=True)
                    
                    if st.button("🔄 Process Batch Translation", type="primary"):
                        self.process_batch_translation(df, target_system)
                
                except Exception as e:
                    st.error(f"❌ Error reading CSV: {e}")
        
        with batch_col2:
            st.markdown("#### 📝 CSV Format Example")
            example_csv = """code,system,display
NAMC001,NAMASTE,Jvara
NAMC002,NAMASTE,Shiroroga
MG30,ICD-11,Fever"""
            
            st.code(example_csv, language="csv")
            
            # Download example
            st.download_button(
                "📥 Download Example CSV",
                data=example_csv,
                file_name="example_codes.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        # Recent translations
        if hasattr(st.session_state, 'recent_translations') and st.session_state.recent_translations:
            st.markdown("---")
            st.markdown("### 📜 Recent Translations")
            
            for i, translation in enumerate(st.session_state.recent_translations[-5:]):
                with st.expander(f"🔄 {translation['source_code']} → {translation['target_system']}", expanded=False):
                    st.markdown(f"**Source:** {translation['source_display']} (`{translation['source_code']}`)")
                    st.markdown(f"**Target:** {translation['target_display']} (`{translation['target_code']}`)")
                    st.markdown(f"**Confidence:** {translation['confidence']}%")
                    st.markdown(f"**Translated:** {translation['timestamp']}")
    
    def translate_code(self, code: str, source_system: str, target_system: str) -> Dict:
        """Translate code between systems"""
        # Mock translation with realistic data
        translations = {
            'NAMC001': {
                'source': {
                    'code': 'NAMC001',
                    'system': 'NAMASTE',
                    'display': 'Jvara (Fever)',
                    'definition': 'Elevated body temperature due to various causes in Ayurveda'
                },
                'targets': [
                    {
                        'code': 'MG30',
                        'system': 'ICD-11',
                        'display': 'Fever, unspecified',
                        'confidence': 95,
                        'explanation': 'Direct semantic match - both represent elevated body temperature'
                    },
                    {
                        'code': '386661006',
                        'system': 'SNOMED CT',
                        'display': 'Fever',
                        'confidence': 92,
                        'explanation': 'Strong clinical terminology match'
                    },
                    {
                        'code': '8310-5',
                        'system': 'LOINC',
                        'display': 'Body temperature',
                        'confidence': 78,
                        'explanation': 'Related observation code for temperature measurement'
                    }
                ]
            },
            'NAMC002': {
                'source': {
                    'code': 'NAMC002',
                    'system': 'NAMASTE',
                    'display': 'Shiroroga (Headache)',
                    'definition': 'Pain in the head region in Ayurveda'
                },
                'targets': [
                    {
                        'code': 'MB40',
                        'system': 'ICD-11',
                        'display': 'Headache',
                        'confidence': 89,
                        'explanation': 'Direct match for head pain condition'
                    },
                    {
                        'code': '25064002',
                        'system': 'SNOMED CT',
                        'display': 'Headache',
                        'confidence': 87,
                        'explanation': 'Clinical terminology for cephalgia'
                    }
                ]
            }
        }
        
        # Get translation or create default
        result = translations.get(code, {
            'source': {
                'code': code,
                'system': source_system,
                'display': f'Unknown term ({code})',
                'definition': 'Definition not available'
            },
            'targets': [
                {
                    'code': 'UNKNOWN',
                    'system': target_system,
                    'display': 'No mapping found',
                    'confidence': 0,
                    'explanation': 'No suitable mapping available in target system'
                }
            ]
        })
        
        # Store recent translation
        if not hasattr(st.session_state, 'recent_translations'):
            st.session_state.recent_translations = []
        
        if result['targets'] and result['targets'][0]['confidence'] > 0:
            st.session_state.recent_translations.append({
                'source_code': code,
                'source_display': result['source']['display'],
                'target_code': result['targets'][0]['code'],
                'target_display': result['targets'][0]['display'],
                'target_system': target_system,
                'confidence': result['targets'][0]['confidence'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return result
    
    def display_translation_result(self, result: Dict):
        """Display beautiful translation results"""
        st.markdown("### 🎯 Translation Results")
        
        # Source code information
        source = result['source']
        st.markdown(f"""
        <div class="modern-card" style="border-left: 4px solid #ff6b35;">
            <h4>📤 Source Code</h4>
            <p><strong>{source['system']}:</strong> <code>{source['code']}</code> - {source['display']}</p>
            <p><em>{source['definition']}</em></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Target translations
        if result['targets'] and result['targets'][0]['confidence'] > 0:
            st.markdown("#### 📥 Target Translations")
            
            for i, target in enumerate(result['targets']):
                confidence_color = "#4caf50" if target['confidence'] >= 80 else "#ff9800" if target['confidence'] >= 60 else "#f44336"
                
                # Translation card
                trans_col1, trans_col2 = st.columns([3, 1])
                
                with trans_col1:
                    st.markdown(f"""
                    <div class="modern-card" style="border-left: 4px solid {confidence_color};">
                        <h4>{target['system']}</h4>
                        <p><strong>Code:</strong> <code>{target['code']}</code></p>
                        <p><strong>Display:</strong> {target['display']}</p>
                        <p><strong>Explanation:</strong> <em>{target['explanation']}</em></p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with trans_col2:
                    # Confidence meter
                    confidence = target['confidence']
                    confidence_color_text = "🟢 High" if confidence >= 80 else "🟡 Medium" if confidence >= 60 else "🔴 Low"
                    
                    st.metric(
                        "Confidence",
                        f"{confidence}%",
                        delta=confidence_color_text
                    )
                    
                    # Action buttons for this mapping
                    if st.button(f"➕ Add to List", key=f"add_mapping_{i}"):
                        mapping_data = {
                            'code': target['code'],
                            'display': target['display'],
                            'system': target['system'],
                            'specialty': 'General',
                            'confidence': confidence,
                            'definition': f"Mapped from {source['display']}"
                        }
                        self.add_to_problem_list(mapping_data)
                        st.toast(f"✅ Added {target['display']} to problem list!")
                    
                    if st.button(f"📋 Copy", key=f"copy_mapping_{i}"):
                        st.toast(f"📋 {target['code']} copied!")
                
                st.markdown("---")
        
        else:
            st.warning("❌ No suitable mappings found in the target system.")
            st.info("💡 Try adjusting the minimum confidence threshold or using a different target system.")
    
    def process_batch_translation(self, df: pd.DataFrame, target_system: str):
        """Process batch translation"""
        st.markdown("### 🔄 Batch Translation Results")
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results = []
        total_codes = len(df)
        
        for i, row in df.iterrows():
            # Update progress
            progress = (i + 1) / total_codes
            progress_bar.progress(progress)
            status_text.text(f"Translating {i+1}/{total_codes}: {row.get('code', 'Unknown')}")
            
            # Translate each code
            source_code = row.get('code', '')
            source_system = row.get('system', 'NAMASTE')
            
            if source_code:
                translation = self.translate_code(source_code, source_system, target_system)
                
                if translation['targets'] and translation['targets'][0]['confidence'] > 0:
                    best_target = translation['targets'][0]
                    results.append({
                        'Source Code': source_code,
                        'Source System': source_system,
                        'Source Display': translation['source']['display'],
                        'Target Code': best_target['code'],
                        'Target System': best_target['system'],
                        'Target Display': best_target['display'],
                        'Confidence': f"{best_target['confidence']}%",
                        'Status': '✅ Mapped'
                    })
                else:
                    results.append({
                        'Source Code': source_code,
                        'Source System': source_system,
                        'Source Display': translation['source']['display'],
                        'Target Code': 'N/A',
                        'Target System': target_system,
                        'Target Display': 'No mapping found',
                        'Confidence': '0%',
                        'Status': '❌ No mapping'
                    })
            
            time.sleep(0.1)  # Simulate processing time
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Display results
        if results:
            st.success(f"✅ Batch translation completed! Processed {len(results)} codes.")
            
            # Results summary
            mapped_count = len([r for r in results if r['Status'] == '✅ Mapped'])
            unmapped_count = len(results) - mapped_count
            
            summary_col1, summary_col2, summary_col3 = st.columns(3)
            
            with summary_col1:
                st.metric("Total Processed", len(results))
            with summary_col2:
                st.metric("Successfully Mapped", mapped_count, delta="✅")
            with summary_col3:
                st.metric("No Mapping Found", unmapped_count, delta="❌")
            
            # Results table
            results_df = pd.DataFrame(results)
            st.dataframe(results_df, use_container_width=True, hide_index=True)
            
            # Export options
            export_col1, export_col2 = st.columns(2)
            
            with export_col1:
                csv_data = results_df.to_csv(index=False)
                st.download_button(
                    "📥 Download Results CSV",
                    data=csv_data,
                    file_name=f"batch_translation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with export_col2:
                # Create FHIR ConceptMap
                concept_map = self.create_concept_map(results)
                st.download_button(
                    "📥 Download FHIR ConceptMap",
                    data=json.dumps(concept_map, indent=2),
                    file_name=f"concept_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        # Interactive mapping explorer
        st.markdown("---")
        st.markdown("### 🗺️ Interactive Mapping Explorer")
        
        explorer_col1, explorer_col2 = st.columns([1, 1])
        
        with explorer_col1:
            st.markdown("#### 🔍 Explore by System")
            explore_system = st.selectbox(
                "Select System to Explore",
                ["NAMASTE", "ICD-11", "SNOMED CT", "LOINC"],
                key="explore_system"
            )
            
            if st.button("🔍 Show Sample Codes", key="show_samples"):
                sample_codes = self.get_sample_codes(explore_system)
                self.display_sample_codes(sample_codes)
        
        with explorer_col2:
            st.markdown("#### 📊 Mapping Statistics")
            
            # Mock statistics
            stats_data = {
                'System Pair': [
                    'NAMASTE → ICD-11',
                    'NAMASTE → SNOMED CT', 
                    'ICD-11 → SNOMED CT',
                    'SNOMED CT → LOINC'
                ],
                'Available Mappings': [4102, 3876, 8234, 2156],
                'Avg Confidence': ['94.2%', '89.7%', '96.1%', '87.3%']
            }
            
            stats_df = pd.DataFrame(stats_data)
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    def create_concept_map(self, results: List[Dict]) -> Dict:
        """Create FHIR ConceptMap from translation results"""
        concept_map = {
            "resourceType": "ConceptMap",
            "id": f"translation-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "url": "http://projectsetu.in/fhir/ConceptMap/batch-translation",
            "version": "1.0.0",
            "name": "BatchTranslationConceptMap",
            "title": "Batch Translation Results",
            "status": "active",
            "date": datetime.now().isoformat(),
            "publisher": "Project Setu",
            "description": "ConceptMap generated from batch translation",
            "sourceUri": "http://ayush.gov.in/fhir/CodeSystem/NAMASTE",
            "targetUri": "http://terminology.hl7.org/CodeSystem/icd11",
            "group": []
        }
        
        # Group mappings
        group = {
            "source": "http://ayush.gov.in/fhir/CodeSystem/NAMASTE",
            "target": "http://terminology.hl7.org/CodeSystem/icd11",
            "element": []
        }
        
        for result in results:
            if result['Status'] == '✅ Mapped':
                element = {
                    "code": result['Source Code'],
                    "display": result['Source Display'],
                    "target": [{
                        "code": result['Target Code'],
                        "display": result['Target Display'],
                        "equivalence": "equivalent" if int(result['Confidence'].replace('%', '')) > 90 else "wider"
                    }]
                }
                group["element"].append(element)
        
        concept_map["group"].append(group)
        return concept_map
    
    def get_sample_codes(self, system: str) -> List[Dict]:
        """Get sample codes for a system"""
        sample_data = {
            'NAMASTE': [
                {'code': 'NAMC001', 'display': 'Jvara (Fever)', 'category': 'Symptom'},
                {'code': 'NAMC002', 'display': 'Shiroroga (Headache)', 'category': 'Symptom'},
                {'code': 'NAMC003', 'display': 'Kasa (Cough)', 'category': 'Respiratory'},
                {'code': 'NAMC004', 'display': 'Atisara (Diarrhea)', 'category': 'Digestive'},
                {'code': 'NAMC005', 'display': 'Shwasa (Dyspnea)', 'category': 'Respiratory'}
            ],
            'ICD-11': [
                {'code': 'MG30', 'display': 'Fever, unspecified', 'category': 'General'},
                {'code': 'MB40', 'display': 'Headache', 'category': 'Neurological'},
                {'code': 'CA80', 'display': 'Cough', 'category': 'Respiratory'},
                {'code': 'DD90', 'display': 'Diarrhoea', 'category': 'Digestive'}
            ],
            'SNOMED CT': [
                {'code': '386661006', 'display': 'Fever', 'category': 'Clinical Finding'},
                {'code': '25064002', 'display': 'Headache', 'category': 'Clinical Finding'},
                {'code': '49727002', 'display': 'Cough', 'category': 'Clinical Finding'},
                {'code': '62315008', 'display': 'Diarrhoea', 'category': 'Clinical Finding'}
            ],
            'LOINC': [
                {'code': '8310-5', 'display': 'Body temperature', 'category': 'Vital Signs'},
                {'code': '8480-6', 'display': 'Systolic blood pressure', 'category': 'Vital Signs'},
                {'code': '8462-4', 'display': 'Diastolic blood pressure', 'category': 'Vital Signs'},
                {'code': '8867-4', 'display': 'Heart rate', 'category': 'Vital Signs'}
            ]
        }
        
        return sample_data.get(system, [])
    
    def display_sample_codes(self, codes: List[Dict]):
        """Display sample codes"""
        st.markdown("#### 📋 Sample Codes")
        
        for code in codes:
            code_col1, code_col2, code_col3 = st.columns([2, 2, 1])
            
            with code_col1:
                st.code(code['code'])
            
            with code_col2:
                st.markdown(f"**{code['display']}**")
                st.caption(f"Category: {code['category']}")
            
            with code_col3:
                if st.button(f"🔄 Map", key=f"map_{code['code']}"):
                    st.session_state["example_code"] = code['code']
                    st.toast(f"🔄 Code {code['code']} ready for mapping!")
                    st.rerun()
    
    def authenticate_user(self, abha_id: str, password: str) -> bool:
        """Authenticate user"""
        demo_accounts = {
            "12-3456-7890-1234": "testpassword",
            "98-7654-3210-9876": "demopassword"
        }
        return demo_accounts.get(abha_id) == password
    
    def run(self):
        """Main app runner"""
        if st.session_state.show_info_page:
            self.show_info_page()
        elif not st.session_state.authenticated:
            self.show_landing_page()
        else:
            # Setup sidebar and get current page
            page = self.setup_sidebar()
            
            # Route to appropriate page
            if page == '🔍 Smart Search':
                self.show_smart_search_page()
            elif page == '🔄 Code Mapping':
                self.show_code_mapping_page()
            elif page == '📊 Analytics Dashboard':
                self.show_analytics_dashboard()
            elif page == '🤖 AI Medical Chatbot':
                self.show_ai_chatbot_page()
            elif page == '📋 Problem List Builder':
                self.show_problem_list_page()
            elif page == 'ℹ️ About Components':
                self.show_info_page()
            else:
                st.markdown(f"""
                <div class="hero-section">
                    <h1>{page}</h1>
                    <p>Feature available - interface being enhanced!</p>
                </div>
                """, unsafe_allow_html=True)
                st.info(f"🚧 {page} is fully functional. Enhanced UI coming soon!")

# Run the application
if __name__ == "__main__":
    app = ProjectSetuApp()
    app.run()
