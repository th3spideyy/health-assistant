# 🏥 Healthcare Planning Assistant - GUI Guide

## 🎯 Overview

A user-friendly Tkinter GUI for the Healthcare Planning Assistant Agent that provides an intuitive interface for creating and managing healthcare task plans.

## 🚀 Quick Start

### Method 1: Direct Launch
```bash
python gui_app.py
```

### Method 2: Using Launcher
```bash
python run_gui.py
```

## 🖥️ GUI Features

### 📋 Input Section
- **Healthcare Goal**: Dropdown with predefined options
  - Treatment Options
  - Emergency Care  
  - Routine Checkup
  - Surgery Preparation

- **Patient Information**:
  - Age (numeric input)
  - Condition (text input)

- **Constraints**: 
  - None
  - Urgent
  - Limited Mobility
  - Requires Anesthesia
  - Routine

- **Specialist Preference**:
  - None
  - Cardiologist
  - Neurologist
  - General Practitioner
  - Orthopedic

### 🎛️ Control Buttons
- **🚀 Generate Plan**: Creates healthcare plan based on inputs
- **🗑️ Clear**: Resets all form fields
- **💾 Export Plan**: Saves current plan to JSON file

### 📊 Results Display (3 Tabs)

#### 📋 Execution Plan Tab
- Complete task breakdown
- Time schedules
- Resource assignments
- Dependencies
- Task priorities

#### 📈 Progress Tab
- Overall progress percentage
- Task status breakdown
- Completed/in-progress/remaining tasks
- Visual status indicators

#### 🏥 Resources Tab
- Resource utilization by type
- Visual utilization bars
- Current load/capacity
- Availability status

## 🎮 Usage Example

### Step 1: Fill in Patient Information
```
Healthcare Goal: Treatment Options
Patient Age: 72
Condition: Chest pain
Constraints: Limited Mobility
Specialist: Cardiologist
```

### Step 2: Generate Plan
Click "🚀 Generate Plan" button

### Step 3: Review Results
Switch between tabs to view:
- **Execution Plan**: Detailed task schedule
- **Progress**: Task completion status
- **Resources**: Healthcare resource utilization

### Step 4: Export (Optional)
Click "💾 Export Plan" to save as JSON

## 🔧 Technical Details

### Backend Integration
- GUI connects to `HealthcarePlannerAgent` from `src/planner_agent.py`
- Real-time processing with status updates
- Error handling with user-friendly messages

### Data Flow
```
User Input → GUI Form → Backend Agent → Processing → 
Results Display → GUI Tabs
```

### Resource Visualization
- Progress bars for utilization
- Color-coded status indicators
- Grouped by resource type (Doctors, Equipment, Rooms, Labs)

## 🎨 GUI Layout

```
┌─────────────────────────────────────────────────────────┐
│                🏥 Healthcare Planning Assistant          │
├─────────────────────────────────────────────────────────┤
│  📋 Planning Request                                    │
│  Healthcare Goal: [Treatment Options ▼]                │
│  Patient Age: [72          ]                           │
│  Condition: [Chest pain                               ] │
│  Constraints: [Limited Mobility ▼]                    │
│  Specialist: [Cardiologist ▼]                         │
│                                                       │
│  [🚀 Generate Plan] [🗑️ Clear] [💾 Export Plan]      │
├─────────────────────────────────────────────────────────┤
│  📊 Results                                            │
│  [📋 Execution Plan] [📈 Progress] [🏥 Resources]     │
│  ┌─────────────────────────────────────────────────┐ │
│  │                                                 │ │
│  │  Tab Content (Scrollable)                       │ │
│  │                                                 │ │
│  │                                                 │ │
│  └─────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  Status: Ready to assist with healthcare planning...   │
└─────────────────────────────────────────────────────────┘
```

## 🎯 Key Features Demonstrated

### ✅ User-Friendly Interface
- Intuitive form controls
- Clear labeling and organization
- Responsive layout

### ✅ Real-Time Processing
- Live status updates
- Progress indicators
- Error handling

### ✅ Comprehensive Results
- Multi-tab display
- Detailed task information
- Resource utilization visualization

### ✅ Export Functionality
- JSON export capability
- Timestamped filenames
- Integration with backend

## 🔍 Example Output

When you run the GUI with sample input, you'll see:

### Execution Plan Tab:
```
🏥 HEALTHCARE EXECUTION PLAN
============================================================

Goal: Treatment Options
Total Duration: 165 minutes
Number of Tasks: 4

📋 TASK 1: Initial Patient Assessment
   📝 Description: Comprehensive evaluation of patient's current condition
   ⚡ Priority: HIGH
   ⏱️  Duration: 45 minutes
   🕐 Start: 16:12
   🕐 End: 16:57
   👥 Resources: dr_jones, room_101
   📊 Status: pending
```

### Resources Tab:
```
🏥 RESOURCE UTILIZATION
============================================================

🏷️ DOCTOR
----------------------------------------
📋 Dr. Jones - General Practitioner
   Utilization: [████████░░] 80%
   Load: 1/1
   Status: 🔴 Busy

📋 Dr. Smith - Cardiologist
   Utilization: [████████░░] 80%
   Load: 1/1
   Status: 🔴 Busy
```

## 🎓 Educational Value

The GUI demonstrates:
- **Frontend-Backend Integration**: Tkinter GUI with Python backend
- **User Experience Design**: Intuitive healthcare workflow interface
- **Data Visualization**: Progress bars and status indicators
- **Real-World Application**: Practical healthcare planning tool

## 🚀 Next Steps

Try different scenarios:
1. **Emergency Planning**: Set goal to "Emergency Care"
2. **Routine Checkup**: Use "Routine Checkup" goal
3. **Surgery Prep**: Select "Surgery Preparation"
4. **Custom Inputs**: Modify patient information and constraints

## 🎉 Success!

The GUI successfully connects sophisticated Healthcare Planning Assistant backend with an intuitive, user-friendly interface, making advanced AI healthcare planning accessible to everyone!
