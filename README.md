# Healthcare Planning Assistant Agent 🏥

A sophisticated AI agent designed to orchestrate complex healthcare tasks through multi-step reasoning, resource validation, and optimized scheduling.

## 🎯 Overview

The Healthcare Planning Assistant Agent demonstrates advanced AI capabilities in healthcare task management. When given a high-level goal (e.g., "Treatment Options"), the agent autonomously:

1. **Decomposes** the objective into actionable steps
2. **Validates** resource availability through mock interface tools
3. **Generates** detailed execution schedules
4. **Handles** dependencies and optimizes task sequences
5. **Tracks** progress and resource utilization

## 🚀 Features

- **Multi-step Reasoning**: Intelligent task decomposition based on healthcare scenarios
- **Resource Management**: Mock validation of doctors, equipment, rooms, and facilities
- **Dependency Handling**: Automatic resolution of task dependencies and constraints
- **Schedule Optimization**: Efficient task sequencing to minimize wait times
- **Progress Tracking**: Real-time monitoring of task completion and resource utilization
- **Export Capabilities**: Save plans to JSON for documentation and integration

## 📁 Project Structure

```
healthcare-planning-agent/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── models.py                # Data models and enums
│   ├── planner_agent.py         # Main agent class
│   ├── task_decomposer.py       # Task decomposition logic
│   ├── resource_manager.py      # Mock resource validation
│   └── scheduler.py             # Schedule optimization
├── examples/
│   ├── demo.py                  # Comprehensive interactive demo
│   └── simple_demo.py           # Basic functionality demo
├── tests/                       # Unit tests (placeholder)
├── docs/                        # Documentation (placeholder)
├── requirements.txt            # Python dependencies
└── README.md                    # This file
```

## 🛠️ Installation

1. **Clone or download** the project to your local machine
2. **Navigate** to the project directory
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Quick Start

### Simple Demo (Recommended for beginners)

Run the simple demo to see basic functionality:

```bash
python examples/simple_demo.py
```

### Interactive Demo

Experience the full capabilities with an interactive demo:

```bash
python examples/demo.py
```

Choose between:
- **Automated Demo**: Pre-defined scenarios showcasing all features
- **Interactive Mode**: Enter your own healthcare planning requests

## 💡 Usage Examples

### Basic Usage

```python
from src.planner_agent import HealthcarePlannerAgent

# Initialize the agent
agent = HealthcarePlannerAgent()

# Process a healthcare planning request
plan = agent.process_request(
    goal="Treatment Options for Cardiac Condition",
    patient_info={"age": 72, "condition": "chest pain"},
    constraints=["limited mobility"],
    preferences={"specialist": "cardiologist"}
)

# Get progress information
progress = agent.get_task_progress()
print(f"Progress: {progress['progress_percentage']:.1f}%")

# Export the plan
agent.export_plan("my_healthcare_plan.json")
```

### Supported Healthcare Scenarios

The agent includes predefined templates for common healthcare scenarios:

- **Treatment Options**: Comprehensive care planning
- **Emergency Care**: Urgent medical response coordination
- **Routine Checkup**: Preventive care scheduling
- **Surgery Preparation**: Pre-operative assessment and planning

### Example Request

```python
# Elderly patient with cardiac concerns
plan = agent.process_request(
    goal="Treatment Options",
    patient_info={
        "age": 72,
        "condition": "chest pain",
        "history": "hypertension"
    },
    constraints=["limited mobility"],
    preferences={"specialist": "cardiologist"}
)
```

## 🧠 How It Works

### 1. Multi-Step Reasoning Loop

The agent follows a sophisticated reasoning process:

```
Input Goal → Task Decomposition → Resource Validation → 
Sequence Optimization → Schedule Generation → Execution Plan
```

### 2. Task Decomposition

High-level goals are broken down into specific, actionable tasks:

- **"Treatment Options"** → Assessment → Diagnostics → Consultation → Planning
- **"Emergency Care"** → Triage → Stabilization → Emergency Tests
- **"Routine Checkup"** → Vitals → Examination → Counseling

### 3. Resource Validation

Mock healthcare resources include:
- **Medical Staff**: Doctors (Cardiologist, GP, Neurologist), Nurses
- **Equipment**: MRI, X-Ray, Ultrasound machines
- **Facilities**: Examination rooms, Operating rooms
- **Laboratories**: Blood lab, Pathology lab

### 4. Dependency Management

Tasks are automatically ordered based on:
- **Prerequisites**: Diagnostic tests before treatment planning
- **Resource Availability**: Optimal scheduling to minimize conflicts
- **Priority Levels**: Urgent tasks scheduled before routine ones

## 📊 Key Components

### HealthcarePlannerAgent
Main orchestrator class that coordinates all planning activities.

### Task Decomposer
Breaks down high-level goals into specific healthcare tasks using predefined templates.

### Resource Manager
Mock interface for validating healthcare resource availability.

### Scheduler
Optimizes task sequences and creates time-based execution schedules.

## 🎯 Learning Objectives

This project demonstrates:

- **AI Agent Architecture**: Multi-component system design
- **Task Planning**: Automated decomposition and sequencing
- **Resource Management**: Constraint validation and optimization
- **Dependency Resolution**: Topological sorting and conflict handling
- **Healthcare Domain**: Application of AI to medical workflows

## 🔧 Customization

### Adding New Healthcare Scenarios

1. **Edit** `src/task_decomposer.py`
2. **Add** new templates to the `task_templates` dictionary
3. **Define** task titles, descriptions, priorities, and resource requirements

### Extending Resource Types

1. **Modify** `src/models.py` to add new `ResourceType` enums
2. **Update** `src/resource_manager.py` to initialize new resources
3. **Add** validation logic for the new resource types

## 🧪 Testing

Run the simple demo to verify functionality:

```bash
python examples/simple_demo.py
```

For comprehensive testing, use the interactive demo:

```bash
python examples/demo.py
```

## 📚 Educational Value

This project is designed to be **entry-level friendly** while demonstrating sophisticated concepts:

- **Clear Code Structure**: Well-organized, commented code
- **Modular Design**: Separate components for different functionalities
- **Comprehensive Examples**: Multiple demo scenarios
- **Progressive Complexity**: Start simple, add advanced features

## 🔮 Future Enhancements

Potential extensions for advanced users:

- **Real API Integration**: Connect to actual healthcare systems
- **Machine Learning**: Learn from historical planning data
- **Web Interface**: Browser-based planning dashboard
- **Mobile App**: On-the-go healthcare planning
- **Multi-patient Coordination**: Handle multiple patients simultaneously

## 📄 License

This project is designed for educational purposes. Feel free to use, modify, and distribute for learning and development.

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows the existing style and structure
- Add comments for new functionality
- Update documentation as needed
- Test your changes thoroughly

## 📞 Support

For questions or issues:
1. Check the examples for usage patterns
2. Review the code comments for implementation details
3. Experiment with the interactive demo to understand behavior

---

**Built with ❤️ for Healthcare AI Education**

## New fixes in the latest build
- Fixed Streamlit `st.button()` inside `st.form()` crash.
- Login and Sign Up now use a real Streamlit selector instead of non-functional page anchors.
- Plan History now reads plans from the backend.
- Progress Tracking is implemented with per-task status updates.
- Added an authenticated Doctor Directory with admin-only add/edit/delete API support.
- Added doctor specializations to the Create Plan selector.
- Added persistent `data/doctors.json` storage.
