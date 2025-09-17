#!/usr/bin/env python3
"""
Project Setu - System Testing Script
Comprehensive testing suite for all components.
"""

import asyncio
import requests
import json
import time
import sys
from pathlib import Path
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProjectSetuTester:
    """Comprehensive testing suite for Project Setu"""
    
    def __init__(self):
        self.api_base = "http://localhost:8000"
        self.streamlit_base = "http://localhost:8501"
        self.test_results = {}
        self.auth_token = None
    
    def run_all_tests(self):
        """Run all system tests"""
        logger.info("🧪 Starting Project Setu System Tests")
        
        # Test categories
        test_categories = [
            ("📁 File Structure", self.test_file_structure),
            ("📦 Dependencies", self.test_dependencies),
            ("💾 Data Files", self.test_data_files),
            ("🔧 Configuration", self.test_configuration),
            ("🚀 API Endpoints", self.test_api_endpoints),
            ("🔐 Authentication", self.test_authentication),
            ("🔍 Search Functionality", self.test_search),
            ("🔄 Code Mapping", self.test_code_mapping),
            ("🤖 AI Diagnostics", self.test_ai_diagnostics),
            ("📊 Analytics", self.test_analytics),
            ("🌐 Streamlit UI", self.test_streamlit_ui)
        ]
        
        for category_name, test_func in test_categories:
            logger.info(f"\n{category_name}")
            logger.info("=" * 50)
            
            try:
                result = test_func()
                self.test_results[category_name] = result
                if result.get('passed', False):
                    logger.info(f"✅ {category_name} - PASSED")
                else:
                    logger.error(f"❌ {category_name} - FAILED")
                    if result.get('errors'):
                        for error in result['errors']:
                            logger.error(f"   • {error}")
            except Exception as e:
                logger.error(f"❌ {category_name} - ERROR: {e}")
                self.test_results[category_name] = {'passed': False, 'errors': [str(e)]}
        
        # Generate test report
        self.generate_test_report()
    
    def test_file_structure(self) -> Dict[str, Any]:
        """Test project file structure"""
        required_files = [
            "main.py",
            "streamlit_app.py",
            "run_streamlit.py",
            "run_fastapi.py",
            "requirements.txt",
            "README.md",
            "models.py",
            "schemas.py",
            "database.py",
            "crud.py",
            "api/terminology.py",
            "api/users.py",
            "security/auth.py",
            "security/abha_auth.py",
            "services/who_icd11_service.py",
            "services/semantic_mapping_service.py",
            "services/ai_diagnostic_service.py",
            "services/audit_service.py",
            "../ingest_namaste.py",
            "../CodeSystem-NAMASTE.json"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        return {
            'passed': len(missing_files) == 0,
            'total_files': len(required_files),
            'missing_files': missing_files,
            'errors': [f"Missing file: {f}" for f in missing_files]
        }
    
    def test_dependencies(self) -> Dict[str, Any]:
        """Test if all dependencies are installed"""
        required_packages = [
            'fastapi', 'uvicorn', 'streamlit', 'pandas', 'numpy',
            'requests', 'sqlalchemy', 'pydantic', 'passlib',
            'python-jose', 'plotly', 'scikit-learn'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        return {
            'passed': len(missing_packages) == 0,
            'total_packages': len(required_packages),
            'missing_packages': missing_packages,
            'errors': [f"Missing package: {p}" for p in missing_packages]
        }
    
    def test_data_files(self) -> Dict[str, Any]:
        """Test data files and their content"""
        errors = []
        
        # Test CodeSystem-NAMASTE.json
        codesystem_file = Path("../CodeSystem-NAMASTE.json")
        if codesystem_file.exists():
            try:
                with open(codesystem_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data.get('resourceType') != 'CodeSystem':
                    errors.append("CodeSystem file has incorrect resourceType")
                
                concepts = data.get('concept', [])
                if len(concepts) < 1000:
                    errors.append(f"CodeSystem has only {len(concepts)} concepts (expected >1000)")
                
                logger.info(f"📊 CodeSystem contains {len(concepts)} concepts")
                
            except Exception as e:
                errors.append(f"Error reading CodeSystem file: {e}")
        else:
            errors.append("CodeSystem-NAMASTE.json file not found")
        
        # Test Excel files
        excel_files = ["../Ayurveda.xls", "../Siddha.xls", "../Unani.xls"]
        for excel_file in excel_files:
            if not Path(excel_file).exists():
                errors.append(f"Missing Excel file: {excel_file}")
        
        return {
            'passed': len(errors) == 0,
            'errors': errors
        }
    
    def test_configuration(self) -> Dict[str, Any]:
        """Test system configuration"""
        errors = []
        
        # Test if services can be imported
        try:
            from services.who_icd11_service import who_icd_service
            from services.semantic_mapping_service import semantic_mapping_service
            from services.ai_diagnostic_service import ai_diagnostic_service
            from services.audit_service import audit_service
            logger.info("✅ All services imported successfully")
        except Exception as e:
            errors.append(f"Service import error: {e}")
        
        # Test database models
        try:
            from models import Doctor
            from database import Base, engine
            logger.info("✅ Database models imported successfully")
        except Exception as e:
            errors.append(f"Database model error: {e}")
        
        return {
            'passed': len(errors) == 0,
            'errors': errors
        }
    
    def test_api_endpoints(self) -> Dict[str, Any]:
        """Test FastAPI endpoints"""
        errors = []
        
        # Test if API server is running
        try:
            response = requests.get(f"{self.api_base}/", timeout=5)
            if response.status_code == 200:
                logger.info("✅ API server is running")
            else:
                errors.append(f"API health check failed: {response.status_code}")
        except requests.exceptions.ConnectionError:
            errors.append("API server is not running - start with 'python run_fastapi.py'")
        except Exception as e:
            errors.append(f"API connection error: {e}")
        
        # Test API documentation
        try:
            response = requests.get(f"{self.api_base}/docs", timeout=5)
            if response.status_code == 200:
                logger.info("✅ API documentation accessible")
            else:
                errors.append("API documentation not accessible")
        except Exception as e:
            errors.append(f"API docs error: {e}")
        
        return {
            'passed': len(errors) == 0,
            'errors': errors
        }
    
    def test_authentication(self) -> Dict[str, Any]:
        """Test authentication system"""
        errors = []
        
        if self.api_base not in str(self.test_results.get('🚀 API Endpoints', {}).get('errors', [])):
            try:
                # Test login endpoint
                login_data = {
                    "username": "test@example.com",
                    "password": "testpassword"
                }
                
                response = requests.post(
                    f"{self.api_base}/api/token",
                    data=login_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=5
                )
                
                if response.status_code in [200, 401]:  # 401 is expected for invalid credentials
                    logger.info("✅ Authentication endpoint accessible")
                    if response.status_code == 200:
                        token_data = response.json()
                        self.auth_token = token_data.get('access_token')
                else:
                    errors.append(f"Authentication endpoint error: {response.status_code}")
                
            except Exception as e:
                errors.append(f"Authentication test error: {e}")
        else:
            errors.append("Skipping authentication test - API server not available")
        
        return {
            'passed': len(errors) == 0,
            'errors': errors
        }
    
    def test_search(self) -> Dict[str, Any]:
        """Test search functionality"""
        errors = []
        
        # Test terminology lookup
        if not any("API server is not running" in str(e) for e in self.test_results.get('🚀 API Endpoints', {}).get('errors', [])):
            try:
                response = requests.get(
                    f"{self.api_base}/api/CodeSystem/$lookup",
                    params={'code': 'fever', 'system': 'NAMASTE'},
                    timeout=10
                )
                
                if response.status_code in [200, 401]:  # 401 expected without auth
                    logger.info("✅ Search endpoint accessible")
                else:
                    errors.append(f"Search endpoint error: {response.status_code}")
                
            except Exception as e:
                errors.append(f"Search test error: {e}")
        else:
            errors.append("Skipping search test - API server not available")
        
        return {
            'passed': len(errors) == 0,
            'errors': errors
        }
    
    def test_code_mapping(self) -> Dict[str, Any]:
        """Test code mapping functionality"""
        errors = []
        
        # Test ConceptMap translation
        if not any("API server is not running" in str(e) for e in self.test_results.get('🚀 API Endpoints', {}).get('errors', [])):
            try:
                response = requests.get(
                    f"{self.api_base}/api/ConceptMap/$translate",
                    params={'code': 'NAMC001', 'system': 'NAMASTE', 'target': 'ICD-11'},
                    timeout=10
                )
                
                if response.status_code in [200, 401]:  # 401 expected without auth
                    logger.info("✅ Code mapping endpoint accessible")
                else:
                    errors.append(f"Code mapping endpoint error: {response.status_code}")
                
            except Exception as e:
                errors.append(f"Code mapping test error: {e}")
        else:
            errors.append("Skipping code mapping test - API server not available")
        
        return {
            'passed': len(errors) == 0,
            'errors': errors
        }
    
    def test_ai_diagnostics(self) -> Dict[str, Any]:
        """Test AI diagnostic functionality"""
        errors = []
        
        try:
            # Test AI service import and basic functionality
            from services.ai_diagnostic_service import ai_diagnostic_service
            
            # Test if AI models are accessible
            if hasattr(ai_diagnostic_service, 'diagnostic_classifier'):
                logger.info("✅ AI diagnostic service initialized")
            else:
                logger.info("ℹ️ AI diagnostic service using fallback models")
            
        except Exception as e:
            errors.append(f"AI diagnostics test error: {e}")
        
        return {
            'passed': len(errors) == 0,
            'errors': errors
        }
    
    def test_analytics(self) -> Dict[str, Any]:
        """Test analytics functionality"""
        errors = []
        
        try:
            # Test audit service
            from services.audit_service import audit_service
            
            # Test basic audit functionality
            event_id = audit_service.log_event(
                event_type=audit_service.AuditEventType.READ,
                user_id="test_user",
                user_name="Test User",
                resource_type="TestResource",
                resource_id="test_123",
                action="TEST_ACTION",
                details={'test': True}
            )
            
            if event_id:
                logger.info("✅ Audit system working")
            else:
                errors.append("Audit system failed to log event")
                
        except Exception as e:
            errors.append(f"Analytics test error: {e}")
        
        return {
            'passed': len(errors) == 0,
            'errors': errors
        }
    
    def test_streamlit_ui(self) -> Dict[str, Any]:
        """Test Streamlit UI"""
        errors = []
        
        try:
            # Test if Streamlit server is running
            response = requests.get(f"{self.streamlit_base}", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Streamlit server is running")
            else:
                errors.append("Streamlit server not accessible")
        except requests.exceptions.ConnectionError:
            errors.append("Streamlit server is not running - start with 'python run_streamlit.py'")
        except Exception as e:
            errors.append(f"Streamlit test error: {e}")
        
        return {
            'passed': len(errors) == 0,
            'errors': errors
        }
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("\n" + "="*60)
        logger.info("🧪 PROJECT SETU - TEST RESULTS SUMMARY")
        logger.info("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get('passed', False))
        failed_tests = total_tests - passed_tests
        
        logger.info(f"📊 Total Test Categories: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        logger.info("\n📋 DETAILED RESULTS:")
        logger.info("-" * 40)
        
        for category, result in self.test_results.items():
            status = "✅ PASS" if result.get('passed', False) else "❌ FAIL"
            logger.info(f"{status} | {category}")
            
            if not result.get('passed', False) and result.get('errors'):
                for error in result['errors'][:3]:  # Show first 3 errors
                    logger.info(f"      └─ {error}")
        
        # Recommendations
        logger.info("\n💡 RECOMMENDATIONS:")
        logger.info("-" * 40)
        
        if failed_tests == 0:
            logger.info("🎉 All tests passed! System is ready for use.")
            logger.info("🚀 Start the system with:")
            logger.info("   • Streamlit UI: python run_streamlit.py")
            logger.info("   • FastAPI Backend: python run_fastapi.py")
        else:
            logger.info("🔧 Please address the failed tests before proceeding:")
            
            if any("API server is not running" in str(result.get('errors', [])) for result in self.test_results.values()):
                logger.info("   1. Start FastAPI server: python run_fastapi.py")
            
            if any("Streamlit server is not running" in str(result.get('errors', [])) for result in self.test_results.values()):
                logger.info("   2. Start Streamlit server: python run_streamlit.py")
            
            if any("Missing package" in str(result.get('errors', [])) for result in self.test_results.values()):
                logger.info("   3. Install missing packages: pip install -r requirements.txt")
            
            if any("Missing file" in str(result.get('errors', [])) for result in self.test_results.values()):
                logger.info("   4. Ensure all project files are present")
        
        logger.info("\n" + "="*60)


def main():
    """Run the test suite"""
    print("🏥 Project Setu - System Testing")
    print("="*50)
    
    tester = ProjectSetuTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
