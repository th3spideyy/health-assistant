"""
Simple launcher for Healthcare Planning Assistant GUI
"""

import subprocess
import sys
import os

def main():
    """Launch the Healthcare Planning Assistant GUI"""
    print("🏥 Starting Healthcare Planning Assistant GUI...")
    
    try:
        # Check if we're in the right directory
        if not os.path.exists("gui_app.py"):
            print("❌ Error: gui_app.py not found. Please run from the project directory.")
            return
        
        # Launch the GUI
        subprocess.run([sys.executable, "gui_app.py"])
        
    except KeyboardInterrupt:
        print("\n👋 GUI closed by user")
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")

if __name__ == "__main__":
    main()
