"""
Mock Resource Manager for Healthcare Planning Assistant
Simulates resource availability and validation
"""

from typing import List, Dict, Optional
from .models import Resource, ResourceType
import random

class MockResourceManager:
    """Mock resource manager that simulates healthcare resources"""
    
    def __init__(self):
        self.resources = self._initialize_mock_resources()
    
    def _initialize_mock_resources(self) -> Dict[str, Resource]:
        """Initialize mock healthcare resources"""
        resources = {}
        
        # Doctors
        resources["dr_smith"] = Resource("dr_smith", "Dr. Smith - Cardiologist", ResourceType.DOCTOR, True, 1, 0)
        resources["dr_jones"] = Resource("dr_jones", "Dr. Jones - General Practitioner", ResourceType.DOCTOR, True, 1, 0)
        resources["dr_wilson"] = Resource("dr_wilson", "Dr. Wilson - Neurologist", ResourceType.DOCTOR, True, 1, 0)
        
        # Nurses
        resources["nurse_1"] = Resource("nurse_1", "Nurse Sarah", ResourceType.NURSE, True, 1, 0)
        resources["nurse_2"] = Resource("nurse_2", "Nurse Mike", ResourceType.NURSE, True, 1, 0)
        
        # Equipment
        resources["mri_machine"] = Resource("mri_machine", "MRI Machine", ResourceType.EQUIPMENT, True, 1, 0)
        resources["xray_machine"] = Resource("xray_machine", "X-Ray Machine", ResourceType.EQUIPMENT, True, 2, 0)
        resources["ultrasound"] = Resource("ultrasound", "Ultrasound Device", ResourceType.EQUIPMENT, True, 1, 0)
        
        # Rooms
        resources["room_101"] = Resource("room_101", "Examination Room 101", ResourceType.ROOM, True, 1, 0)
        resources["room_102"] = Resource("room_102", "Examination Room 102", ResourceType.ROOM, True, 1, 0)
        resources["or_1"] = Resource("or_1", "Operating Room 1", ResourceType.ROOM, True, 1, 0)
        
        # Lab
        resources["blood_lab"] = Resource("blood_lab", "Blood Laboratory", ResourceType.LAB, True, 5, 0)
        resources["pathology_lab"] = Resource("pathology_lab", "Pathology Lab", ResourceType.LAB, True, 3, 0)
        
        return resources
    
    def add_doctor(self, doctor_id: str, name: str, specialization: str, available: bool = True):
        """Add a doctor as a schedulable healthcare resource."""
        self.resources[doctor_id] = Resource(
            doctor_id, f"{name} - {specialization}", ResourceType.DOCTOR, available, 1, 0
        )

    def remove_doctor(self, doctor_id: str):
        """Remove a dynamically added doctor resource."""
        if doctor_id in self.resources and self.resources[doctor_id].type == ResourceType.DOCTOR:
            del self.resources[doctor_id]

    def check_availability(self, resource_id: str) -> bool:
        """Check if a resource is available"""
        if resource_id not in self.resources:
            return False
        
        # Simulate random availability for demo purposes
        resource = self.resources[resource_id]
        if random.random() > 0.8:  # 20% chance resource is busy
            return False
        
        return resource.is_available()
    
    def get_available_resources(self, resource_type: ResourceType) -> List[Resource]:
        """Get all available resources of a specific type"""
        available = []
        for resource in self.resources.values():
            if resource.type == resource_type and self.check_availability(resource.id):
                available.append(resource)
        return available
    
    def validate_resource_requirements(self, required_resources: List[str]) -> Dict[str, bool]:
        """Validate if all required resources are available"""
        validation = {}
        for resource_id in required_resources:
            validation[resource_id] = self.check_availability(resource_id)
        return validation
    
    def reserve_resource(self, resource_id: str) -> bool:
        """Reserve a resource if available"""
        if self.check_availability(resource_id):
            self.resources[resource_id].current_load += 1
            return True
        return False
    
    def release_resource(self, resource_id: str):
        """Release a previously reserved resource"""
        if resource_id in self.resources:
            self.resources[resource_id].current_load = max(0, self.resources[resource_id].current_load - 1)
    
    def get_resource_info(self, resource_id: str) -> Optional[Resource]:
        """Get information about a specific resource"""
        return self.resources.get(resource_id)
    
    def list_all_resources(self) -> Dict[str, Resource]:
        """List all resources in the system"""
        return self.resources.copy()
