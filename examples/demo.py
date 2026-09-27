"""
Healthcare Planning Assistant Agent Demo
Interactive demonstration of the agent's capabilities
"""

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from planner_agent import HealthcarePlannerAgent
from models import TaskStatus

def main():
    """Run an interactive demo of the Healthcare Planning Assistant"""
    
    print("🏥 Healthcare Planning Assistant Agent - Interactive Demo")
    print("=" * 60)
    print("This demo shows how the agent handles complex healthcare planning tasks")
    print("through multi-step reasoning, resource validation, and schedule optimization.")
    print()
    
    # Initialize the agent
    agent = HealthcarePlannerAgent()
    
    # Demo scenarios
    scenarios = [
        {
            "name": "Elderly Patient Treatment Planning",
            "goal": "Treatment Options for Cardiac Condition",
            "patient_info": {
                "age": 72,
                "condition": "chest pain",
                "history": "hypertension"
            },
            "constraints": ["limited mobility"],
            "preferences": {"specialist": "cardiologist"}
        },
        {
            "name": "Emergency Care Planning",
            "goal": "Emergency Care for Acute Symptoms",
            "patient_info": {
                "age": 45,
                "condition": "severe abdominal pain",
                "history": "none"
            },
            "constraints": ["urgent"],
            "preferences": {}
        },
        {
            "name": "Routine Annual Checkup",
            "goal": "Annual Health Checkup",
            "patient_info": {
                "age": 35,
                "condition": "healthy",
                "history": "no major issues"
            },
            "constraints": ["routine"],
            "preferences": {"time_preference": "morning"}
        },
        {
            "name": "Surgery Preparation",
            "goal": "Pre-operative Assessment for Knee Surgery",
            "patient_info": {
                "age": 58,
                "condition": "knee osteoarthritis",
                "history": "previous surgery"
            },
            "constraints": ["requires anesthesia clearance"],
            "preferences": {"specialist": "orthopedic"}
        }
    ]
    
    # Run each scenario
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎯 Scenario {i}: {scenario['name']}")
        print("-" * 50)
        
        # Process the scenario
        plan = agent.process_request(
            goal=scenario["goal"],
            patient_info=scenario["patient_info"],
            constraints=scenario["constraints"],
            preferences=scenario["preferences"]
        )
        
        # Show progress tracking
        print("\n📊 Task Progress Tracking:")
        progress = agent.get_task_progress()
        print(f"   Total Tasks: {progress['total_tasks']}")
        print(f"   Completed: {progress['completed_tasks']}")
        print(f"   In Progress: {progress['in_progress_tasks']}")
        print(f"   Progress: {progress['progress_percentage']:.1f}%")
        
        # Simulate task completion
        if plan.tasks:
            first_task = plan.tasks[0]
            agent.update_task_status(first_task.id, TaskStatus.IN_PROGRESS)
            agent.update_task_status(first_task.id, TaskStatus.COMPLETED)
            
            updated_progress = agent.get_task_progress()
            print(f"\n   After completing first task:")
            print(f"   Progress: {updated_progress['progress_percentage']:.1f}%")
        
        # Show resource utilization
        print("\n🏥 Resource Utilization:")
        utilization = agent.get_resource_utilization()
        for resource_id, info in list(utilization.items())[:5]:  # Show first 5 resources
            print(f"   {info['name']}: {info['utilization_percentage']:.0f}% utilized")
        
        # Ask user if they want to continue
        if i < len(scenarios):
            input("\nPress Enter to continue to next scenario...")
    
    # Show execution history
    print("\n📚 Execution History:")
    history = agent.get_execution_history()
    for entry in history:
        print(f"   {entry['timestamp'][:19]} - {entry['goal']}")
        print(f"     Tasks: {entry['task_count']}, Duration: {entry['total_duration']} min")
    
    # Export final plan
    print("\n💾 Exporting Plan...")
    export_result = agent.export_plan("demo_healthcare_plan.json")
    print(f"   {export_result}")
    
    print("\n✅ Demo completed successfully!")
    print("The Healthcare Planning Assistant Agent demonstrated:")
    print("   • Multi-step reasoning and task decomposition")
    print("   • Resource availability validation")
    print("   • Dependency-aware scheduling")
    print("   • Task sequence optimization")
    print("   • Progress tracking and resource utilization")
    print("   • Plan export capabilities")

def interactive_mode():
    """Run the agent in interactive mode"""
    agent = HealthcarePlannerAgent()
    
    print("\n🎮 Interactive Mode - Enter your own healthcare planning requests")
    print("Type 'quit' to exit")
    print("-" * 60)
    
    while True:
        try:
            print("\n📋 Enter healthcare goal (e.g., 'Treatment Options', 'Emergency Care'):")
            goal = input("> ").strip()
            
            if goal.lower() in ['quit', 'exit', 'q']:
                break
            
            if not goal:
                continue
            
            # Optional patient information
            print("\n👤 Patient age (press Enter to skip):")
            age_input = input("> ").strip()
            patient_info = {}
            if age_input.isdigit():
                patient_info["age"] = int(age_input)
            
            # Process the request
            plan = agent.process_request(goal=goal, patient_info=patient_info)
            
            # Ask if user wants to see more details
            show_details = input("\n📊 Show resource utilization? (y/n): ").strip().lower()
            if show_details in ['y', 'yes']:
                utilization = agent.get_resource_utilization()
                print("\n🏥 Current Resource Utilization:")
                for resource_id, info in utilization.items():
                    if info['utilization_percentage'] > 0:
                        print(f"   {info['name']}: {info['utilization_percentage']:.0f}% utilized")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again.")

if __name__ == "__main__":
    print("Choose demo mode:")
    print("1. Automated Demo (recommended)")
    print("2. Interactive Mode")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "2":
        interactive_mode()
    else:
        main()
