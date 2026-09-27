"""
Healthcare Planning Assistant - Tkinter GUI
Simple frontend for the Healthcare Planning Assistant Agent
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sys
import os
from datetime import datetime, timedelta

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.planner_agent import HealthcarePlannerAgent
from src.models import TaskStatus

class HealthcarePlanningGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🏥 Healthcare Planning Assistant")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f8ff')
        
        # Initialize the backend agent
        self.agent = HealthcarePlannerAgent()
        self.current_plan = None
        
        # Create GUI components
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🏥 Healthcare Planning Assistant", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Input Section
        input_frame = ttk.LabelFrame(main_frame, text="📋 Planning Request", padding="10")
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # Goal Input
        ttk.Label(input_frame, text="Healthcare Goal:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.goal_var = tk.StringVar(value="Treatment Options")
        goal_combo = ttk.Combobox(input_frame, textvariable=self.goal_var, width=40)
        goal_combo['values'] = ("Treatment Options", "Emergency Care", "Routine Checkup", "Surgery Preparation")
        goal_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Patient Information
        ttk.Label(input_frame, text="Patient Age:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.age_var = tk.StringVar()
        age_entry = ttk.Entry(input_frame, textvariable=self.age_var, width=10)
        age_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(input_frame, text="Condition:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.condition_var = tk.StringVar()
        condition_entry = ttk.Entry(input_frame, textvariable=self.condition_var, width=40)
        condition_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Constraints
        ttk.Label(input_frame, text="Constraints:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.constraints_var = tk.StringVar(value="None")
        constraints_combo = ttk.Combobox(input_frame, textvariable=self.constraints_var, width=40)
        constraints_combo['values'] = ("None", "Urgent", "Limited Mobility", "Requires Anesthesia", "Routine")
        constraints_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Specialist Preference
        ttk.Label(input_frame, text="Specialist:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.specialist_var = tk.StringVar(value="None")
        specialist_combo = ttk.Combobox(input_frame, textvariable=self.specialist_var, width=40)
        specialist_combo['values'] = ("None", "Cardiologist", "Neurologist", "General Practitioner", "Orthopedic")
        specialist_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.plan_button = ttk.Button(button_frame, text="🚀 Generate Plan", command=self.generate_plan)
        self.plan_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="🗑️ Clear", command=self.clear_form)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        self.export_button = ttk.Button(button_frame, text="💾 Export Plan", command=self.export_plan, state=tk.DISABLED)
        self.export_button.pack(side=tk.LEFT, padx=5)
        
        # Results Section
        results_frame = ttk.LabelFrame(main_frame, text="📊 Results", padding="10")
        results_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Plan Tab
        plan_tab = ttk.Frame(self.notebook)
        self.notebook.add(plan_tab, text="📋 Execution Plan")
        
        self.plan_text = scrolledtext.ScrolledText(plan_tab, height=20, width=80, wrap=tk.WORD)
        self.plan_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Progress Tab
        progress_tab = ttk.Frame(self.notebook)
        self.notebook.add(progress_tab, text="📈 Progress")
        
        self.progress_text = scrolledtext.ScrolledText(progress_tab, height=20, width=80, wrap=tk.WORD)
        self.progress_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Resources Tab
        resources_tab = ttk.Frame(self.notebook)
        self.notebook.add(resources_tab, text="🏥 Resources")
        
        self.resources_text = scrolledtext.ScrolledText(resources_tab, height=20, width=80, wrap=tk.WORD)
        self.resources_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready to assist with healthcare planning...")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def generate_plan(self):
        """Generate healthcare plan based on user input"""
        try:
            self.status_var.set("Generating healthcare plan...")
            self.plan_button.config(state=tk.DISABLED)
            self.root.update()
            
            # Get user input
            goal = self.goal_var.get()
            patient_info = {}
            constraints = []
            preferences = {}
            
            # Parse patient information
            if self.age_var.get().isdigit():
                patient_info["age"] = int(self.age_var.get())
            if self.condition_var.get():
                patient_info["condition"] = self.condition_var.get()
            
            # Parse constraints
            constraint = self.constraints_var.get()
            if constraint != "None":
                constraints.append(constraint.lower())
            
            # Parse preferences
            specialist = self.specialist_var.get()
            if specialist != "None":
                preferences["specialist"] = specialist.lower()
            
            # Generate plan using backend agent
            self.current_plan = self.agent.process_request(
                goal=goal,
                patient_info=patient_info,
                constraints=constraints,
                preferences=preferences
            )
            
            # Display results
            self.display_plan()
            self.display_progress()
            self.display_resources()
            
            # Enable export button
            self.export_button.config(state=tk.NORMAL)
            
            self.status_var.set(f"Plan generated successfully! {len(self.current_plan.tasks)} tasks created.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate plan: {str(e)}")
            self.status_var.set("Error occurred while generating plan")
        
        finally:
            self.plan_button.config(state=tk.NORMAL)
    
    def display_plan(self):
        """Display the execution plan"""
        self.plan_text.delete(1.0, tk.END)
        
        if not self.current_plan:
            return
        
        plan_text = f"🏥 HEALTHCARE EXECUTION PLAN\n"
        plan_text += f"{'='*60}\n\n"
        plan_text += f"Goal: {self.current_plan.goal}\n"
        plan_text += f"Total Duration: {self.current_plan.total_duration} minutes\n"
        plan_text += f"Number of Tasks: {len(self.current_plan.tasks)}\n\n"
        
        for i, task in enumerate(self.current_plan.tasks, 1):
            start_time = self.current_plan.schedule.get(task.id, datetime.now())
            end_time = start_time + timedelta(minutes=task.estimated_duration)
            
            plan_text += f"📋 TASK {i}: {task.title}\n"
            plan_text += f"   📝 Description: {task.description}\n"
            plan_text += f"   ⚡ Priority: {task.priority.value.upper()}\n"
            plan_text += f"   ⏱️  Duration: {task.estimated_duration} minutes\n"
            plan_text += f"   🕐 Start: {start_time.strftime('%H:%M')}\n"
            plan_text += f"   🕐 End: {end_time.strftime('%H:%M')}\n"
            plan_text += f"   👥 Resources: {', '.join(task.required_resources)}\n"
            if task.dependencies:
                plan_text += f"   🔗 Dependencies: {len(task.dependencies)} task(s)\n"
            plan_text += f"   📊 Status: {task.status.value}\n\n"
        
        self.plan_text.insert(tk.END, plan_text)
    
    def display_progress(self):
        """Display task progress information"""
        self.progress_text.delete(1.0, tk.END)
        
        if not self.current_plan:
            return
        
        progress = self.agent.get_task_progress()
        
        progress_text = f"📈 TASK PROGRESS TRACKING\n"
        progress_text += f"{'='*60}\n\n"
        progress_text += f"📊 Overall Progress: {progress['progress_percentage']:.1f}%\n"
        progress_text += f"📋 Total Tasks: {progress['total_tasks']}\n"
        progress_text += f"✅ Completed: {progress['completed_tasks']}\n"
        progress_text += f"🔄 In Progress: {progress['in_progress_tasks']}\n"
        progress_text += f"⏳ Remaining: {progress['remaining_tasks']}\n\n"
        
        # Task status breakdown
        progress_text += f"📋 TASK STATUS BREAKDOWN\n"
        progress_text += f"{'-'*40}\n"
        
        for i, task in enumerate(self.current_plan.tasks, 1):
            status_emoji = {
                "pending": "⏳",
                "in_progress": "🔄", 
                "completed": "✅",
                "blocked": "❌"
            }.get(task.status.value, "❓")
            
            progress_text += f"{status_emoji} {task.title} - {task.status.value.upper()}\n"
        
        self.progress_text.insert(tk.END, progress_text)
    
    def display_resources(self):
        """Display resource utilization information"""
        self.resources_text.delete(1.0, tk.END)
        
        utilization = self.agent.get_resource_utilization()
        
        resources_text = f"🏥 RESOURCE UTILIZATION\n"
        resources_text += f"{'='*60}\n\n"
        
        # Group resources by type
        resource_groups = {}
        for resource_id, info in utilization.items():
            resource_type = info['type']
            if resource_type not in resource_groups:
                resource_groups[resource_type] = []
            resource_groups[resource_type].append(info)
        
        for resource_type, resources in resource_groups.items():
            resources_text += f"🏷️ {resource_type.upper()}\n"
            resources_text += f"{'-'*40}\n"
            
            for resource in resources:
                utilization_bar = self.create_utilization_bar(resource['utilization_percentage'])
                status = "🟢 Available" if resource['available'] else "🔴 Busy"
                
                resources_text += f"📋 {resource['name']}\n"
                resources_text += f"   Utilization: {utilization_bar} {resource['utilization_percentage']:.0f}%\n"
                resources_text += f"   Load: {resource['current_load']}/{resource['capacity']}\n"
                resources_text += f"   Status: {status}\n\n"
        
        self.resources_text.insert(tk.END, resources_text)
    
    def create_utilization_bar(self, percentage, width=20):
        """Create a simple text-based utilization bar"""
        filled = int((percentage / 100) * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def clear_form(self):
        """Clear all input fields"""
        self.goal_var.set("Treatment Options")
        self.age_var.set("")
        self.condition_var.set("")
        self.constraints_var.set("None")
        self.specialist_var.set("None")
        
        # Clear results
        self.plan_text.delete(1.0, tk.END)
        self.progress_text.delete(1.0, tk.END)
        self.resources_text.delete(1.0, tk.END)
        
        # Reset
        self.current_plan = None
        self.export_button.config(state=tk.DISABLED)
        self.status_var.set("Form cleared. Ready for new planning request...")
    
    def export_plan(self):
        """Export the current plan to a file"""
        if not self.current_plan:
            messagebox.showwarning("Warning", "No plan to export")
            return
        
        try:
            filename = f"healthcare_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            result = self.agent.export_plan(filename)
            messagebox.showinfo("Success", result)
            self.status_var.set(f"Plan exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export plan: {str(e)}")

def main():
    root = tk.Tk()
    app = HealthcarePlanningGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
