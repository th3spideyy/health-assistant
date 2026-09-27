"""
Simple Healthcare Planning Assistant Demo
A minimal example showing the basic functionality
"""

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from planner_agent import HealthcarePlannerAgent

def simple_demo():
    """Simple demonstration of the Healthcare Planning Assistant"""
    
    print("🏥 Simple Healthcare Planning Demo")
    print("=" * 40)
    
    # Create the agent
    agent = HealthcarePlannerAgent()
    
    # Example 1: Basic treatment planning
    print("\n📋 Example 1: Treatment Planning")
    plan1 = agent.process_request(
        goal="Treatment Options for Chest Pain",
        patient_info={"age": 65, "condition": "chest pain"}
    )
    
    # Example 2: Emergency care
    print("\n📋 Example 2: Emergency Care")
    plan2 = agent.process_request(
        goal="Emergency Care for Severe Pain",
        patient_info={"age": 40, "condition": "severe abdominal pain"},
        constraints=["urgent"]
    )
    
    # Show summary
    print("\n📊 Summary:")
    print(f"Plan 1: {len(plan1.tasks)} tasks, {plan1.total_duration} minutes total")
    print(f"Plan 2: {len(plan2.tasks)} tasks, {plan2.total_duration} minutes total")
    
    print("\n✅ Simple demo completed!")

if __name__ == "__main__":
    simple_demo()
