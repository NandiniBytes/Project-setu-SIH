# 🎮 Project Setu - Manual Testing Scenarios

## 🚀 **Launch Command**
```bash
cd "project_setu"
python3 run_streamlit.py
```
**→ Open: http://localhost:8501**

---

## 🧪 **COMPREHENSIVE MANUAL TESTING GUIDE**

### **🔐 SCENARIO 1: Authentication & Login**
**Test the authentication system:**

1. **Mock Login Test:**
   - ABHA ID: `12-3456-7890-1234`
   - Password: `testpassword`
   - ✅ **Expected**: Login successful, welcome message appears
   - ✅ **Check**: User profile shows in sidebar

2. **Invalid Login Test:**
   - Try wrong ABHA ID: `00-0000-0000-0000`
   - ✅ **Expected**: Error message displayed

---

### **🔍 SCENARIO 2: Smart Medical Search**
**Test the intelligent search functionality:**

1. **Basic Medical Terms:**
   ```
   Search Terms to Try:
   • "fever" → Should find multiple matches
   • "jvara" → Ayurvedic term for fever
   • "headache" → Common symptom
   • "cough" → Respiratory symptom
   • "pain" → General term
   ```
   
2. **Multi-language Search:**
   ```
   Try These:
   • "बुखार" (Hindi for fever)
   • "காய்ச்சல்" (Tamil for fever)
   • "ज्वर" (Sanskrit for fever)
   ```

3. **Advanced Search Features:**
   - ✅ **Test semantic search** vs exact match
   - ✅ **Try voice search** button (will show activation message)
   - ✅ **Use filters** - change system, specialty, confidence
   - ✅ **Check auto-suggestions** as you type

4. **Expected Results:**
   - Results show **confidence scores**
   - Multiple **terminology systems** (NAMASTE, ICD-11, SNOMED CT)
   - **Clickable actions**: View Details, View Mappings, Add to Problem List

---

### **🔄 SCENARIO 3: Code Mapping & Translation**
**Test terminology translation:**

1. **Navigate to Code Mapping tab**

2. **Test Translations:**
   ```
   Source Codes to Try:
   • NAMC001 (NAMASTE) → ICD-11
   • MG30 (ICD-11) → SNOMED CT
   • 386661006 (SNOMED CT) → NAMASTE
   ```

3. **Batch Translation:**
   - Create a CSV file with codes:
   ```csv
   code,system
   NAMC001,NAMASTE
   MG30,ICD-11
   386661006,SNOMED-CT
   ```
   - Upload and test batch processing

4. **Expected Results:**
   - **Confidence scores** for each mapping
   - **Detailed explanations** of why codes match
   - **Multiple target suggestions** ranked by confidence

---

### **🤖 SCENARIO 4: AI Diagnostic Assistant**
**Test the AI-powered diagnostics:**

1. **Navigate to AI Diagnostics page**

2. **Test Case 1 - Simple Fever:**
   ```
   Symptoms: "Patient has fever of 102°F for 2 days, headache, and body aches"
   Age: 35
   Gender: Male
   Medical System: Integrative
   ```

3. **Test Case 2 - Complex Symptoms:**
   ```
   Symptoms: "Chronic fatigue, joint pain, morning stiffness for 3 weeks"
   Age: 45
   Gender: Female
   Medical System: Ayurveda
   ```

4. **Test Case 3 - Emergency Symptoms:**
   ```
   Symptoms: "Severe chest pain, difficulty breathing, sweating"
   Age: 55
   Gender: Male
   ```

5. **Expected Results:**
   - **AI diagnostic suggestions** with confidence scores
   - **Traditional medicine recommendations** (Ayurveda/Siddha/Unani)
   - **Modern medicine suggestions**
   - **Emergency alerts** for critical symptoms
   - **Treatment recommendations**
   - **Recommended tests**

---

### **📋 SCENARIO 5: Problem List Builder**
**Test FHIR problem list creation:**

1. **Add codes from search results:**
   - Search for "fever" → Click "Add to Problem List"
   - Search for "headache" → Click "Add to Problem List"
   - Search for "cough" → Click "Add to Problem List"

2. **Navigate to Problem List Builder**

3. **Test Problem List Features:**
   - ✅ **View added codes** in the list
   - ✅ **Edit problem items** (click Edit button)
   - ✅ **Remove items** (click Remove button)

4. **Test Export Options:**
   - ✅ **Export as FHIR Bundle** → Download JSON file
   - ✅ **Export as CSV** → Download CSV file
   - ✅ **Check file contents** - should be properly formatted

5. **Expected Results:**
   - **FHIR-compliant Bundle** with proper structure
   - **Dual coding** (traditional + modern codes)
   - **Valid JSON format** for EHR integration

---

### **👥 SCENARIO 6: Consent Management**
**Test patient consent tracking:**

1. **Navigate to Consent Management page**

2. **Create New Consent:**
   ```
   Patient ABHA ID: 98-7654-3210-9876
   Practitioner ID: DR12345
   Purpose: Treatment
   Data Types: Medical History, Current Medications, Lab Results
   Expiry Date: 1 year from now
   ```

3. **Test Consent Operations:**
   - ✅ **Create consent** → Should show success message
   - ✅ **View active consents** → Should appear in list
   - ✅ **Withdraw consent** → Click withdraw button

4. **Expected Results:**
   - **Consent records** properly tracked
   - **Status updates** (ACTIVE → WITHDRAWN)
   - **Audit trail** of consent actions

---

### **📊 SCENARIO 7: Analytics Dashboard**
**Test real-time analytics:**

1. **Navigate to Analytics page**

2. **Check Key Metrics:**
   - ✅ **Total searches today** (should show numbers)
   - ✅ **Mapping accuracy** percentage
   - ✅ **Active users** count
   - ✅ **API response time**

3. **Test Interactive Charts:**
   - ✅ **Search volume trends** (line chart)
   - ✅ **System usage distribution** (pie chart)
   - ✅ **Top search terms** list
   - ✅ **Performance metrics** table

4. **Test Refresh:**
   - ✅ **Click "Refresh Data"** → Charts should update

---

### **📜 SCENARIO 8: Audit Trail**
**Test compliance and audit logging:**

1. **Navigate to Audit Trail page**

2. **Test Filters:**
   ```
   Filter Options:
   • Event Type: Login, Search, Access Granted
   • Date Range: Last 7 days
   • User Filter: Leave blank or enter user ID
   ```

3. **Generate Audit Report:**
   - ✅ **Click "Generate Audit Report"**
   - ✅ **View event timeline** chart
   - ✅ **Check detailed audit log** table

4. **Expected Results:**
   - **Complete activity log** with timestamps
   - **Event classification** (SUCCESS/FAILURE)
   - **User tracking** and IP addresses
   - **Compliance metrics** and statistics

---

### **⚙️ SCENARIO 9: Admin Panel** (If Available)
**Test administrative functions:**

1. **Navigate to Admin Panel**

2. **Check System Status:**
   - ✅ **API Status** indicators
   - ✅ **Database connections**
   - ✅ **WHO API sync** status
   - ✅ **Cache status**

3. **Test Configuration:**
   - ✅ **Adjust API timeout** settings
   - ✅ **Modify cache TTL**
   - ✅ **Update security settings**

4. **Test Data Management:**
   - ✅ **Sync WHO Data** button
   - ✅ **Clear Cache** button
   - ✅ **Generate System Report**

---

## 🎯 **STRESS TESTING SCENARIOS**

### **Performance Tests:**
1. **Rapid Search Test:**
   - Type quickly: "fever headache cough pain"
   - ✅ **Check response time** < 2 seconds

2. **Multiple Tab Test:**
   - Open multiple browser tabs
   - ✅ **Test concurrent usage**

3. **Large Data Test:**
   - Search for common terms with many results
   - ✅ **Check pagination** and loading

### **Error Handling Tests:**
1. **Invalid Input Test:**
   - Enter special characters: `!@#$%^&*()`
   - ✅ **Should handle gracefully**

2. **Network Simulation:**
   - Disconnect internet briefly
   - ✅ **Check error messages**

3. **Edge Cases:**
   - Very long search queries (>1000 characters)
   - Empty searches
   - Non-English special characters

---

## 📝 **TESTING CHECKLIST**

### **Core Functionality:**
- [ ] Authentication works
- [ ] Search returns relevant results
- [ ] Code mapping shows confidence scores
- [ ] AI diagnostics provide suggestions
- [ ] Problem list builder exports FHIR
- [ ] Consent management tracks records
- [ ] Analytics show real-time data
- [ ] Audit trail logs activities

### **User Experience:**
- [ ] Interface is responsive
- [ ] Navigation is intuitive
- [ ] Loading states are clear
- [ ] Error messages are helpful
- [ ] Multi-language support works
- [ ] Voice search activates

### **Data Quality:**
- [ ] Medical terms are accurate
- [ ] Code mappings make sense
- [ ] Confidence scores are reasonable
- [ ] FHIR exports are valid JSON
- [ ] Audit logs are complete

### **Performance:**
- [ ] Search results < 2 seconds
- [ ] Page loads < 3 seconds
- [ ] No memory leaks during use
- [ ] Handles concurrent users

---

## 🏆 **SUCCESS CRITERIA**

After testing, you should observe:
- ✅ **4,478+ medical concepts** searchable
- ✅ **Multi-language search** working
- ✅ **AI diagnostic suggestions** with confidence
- ✅ **FHIR-compliant exports** 
- ✅ **Real-time analytics** updating
- ✅ **Comprehensive audit trails**
- ✅ **Smooth user experience**

## 🎉 **BONUS TESTS**

### **Creative Scenarios:**
1. **Multi-language Diagnosis:**
   - Enter symptoms in Hindi, get results in English
   
2. **Traditional Medicine Focus:**
   - Set preference to "Ayurveda" only
   - Search for modern terms, get traditional equivalents

3. **Emergency Simulation:**
   - Enter "chest pain difficulty breathing"
   - Should trigger emergency warnings

4. **Workflow Test:**
   - Search → Add to Problem List → Export → Verify in external tool

**Your Project Setu system is ready for comprehensive testing! 🚀**
