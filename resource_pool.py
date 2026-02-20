from datetime import datetime, timedelta
from production_params import BusinessCalendar

class Resource:
    """Represents an individual resource (artist/team)"""
    def __init__(self, name, resource_type, calendar):
        self.name = name
        self.resource_type = resource_type  # "quota", "support", etc.
        self.calendar = calendar
        self.assigned_hours = {}  # {date: assigned_hours}
        self.vacations = []  # List of (start, end) tuples
    
    def add_vacation(self, start_date, end_date):
        """Schedule vacation for this resource"""
        self.vacations.append((start_date, end_date))
    
    def is_available(self, date, required_hours=8):
        """Check resource availability on a date"""
        if not self.calendar.is_workday(date):
            return False
        
        # Check vacation conflicts
        if any(start <= date <= end for start, end in self.vacations):
            return False
        
        # Check current workload
        current_load = self.assigned_hours.get(date, 0)
        return (current_load + required_hours) <= 8
    
    def assign_work(self, date, hours):
        """Assign work to resource on specific date"""
        if not self.is_available(date, hours):
            raise ValueError(f"Resource {self.name} not available on {date}")
        
        self.assigned_hours[date] = self.assigned_hours.get(date, 0) + hours

class ResourcePool:
    """Manages a pool of resources"""
    def __init__(self, calendar):
        self.calendar = calendar
        self.resources = {}  # {resource_id: Resource}
        self.resources_by_type = {}  # {type: [resources]}
    
    def add_resource(self, resource_id, name, resource_type):
        """Add new resource to pool"""
        resource = Resource(name, resource_type, self.calendar)
        self.resources[resource_id] = resource
        
        if resource_type not in self.resources_by_type:
            self.resources_by_type[resource_type] = []
        self.resources_by_type[resource_type].append(resource)
        return resource
    
    def allocate_resource(self, resource_type, date, hours=8):
        """Allocate an available resource of given type"""
        for resource in self.resources_by_type.get(resource_type, []):
            if resource.is_available(date, hours):
                resource.assign_work(date, hours)
                return resource
        return None  # No available resource
    
    def get_utilization(self, start_date, end_date):
        """Calculate utilization rate over date range"""
        total_capacity = 0
        total_assigned = 0
        
        current = start_date
        while current <= end_date:
            if self.calendar.is_workday(current):
                # Calculate daily capacity
                daily_capacity = len(self.resources_by_type.get("quota", [])) * 8
                total_capacity += daily_capacity
                
                # Calculate daily assigned hours
                daily_assigned = 0
                for resource in self.resources.values():
                    daily_assigned += resource.assigned_hours.get(current, 0)
                total_assigned += daily_assigned
            
            current += timedelta(days=1)
        
        return total_assigned / total_capacity if total_capacity else 0

# Example usage
if __name__ == "__main__":
    from datetime import datetime
    
    # Create calendar
    studio_cal = BusinessCalendar("Studio Calendar")
    
    # Create resource pool
    pool = ResourcePool(studio_cal)
    
    # Add resources
    pool.add_resource("m1", "Modeling Artist", "quota")
    pool.add_resource("m2", "Modeling Artist", "quota")
    pool.add_resource("l1", "Layout Artist", "quota")
    pool.add_resource("s1", "Support Technician", "support")
    
    # Allocate work
    work_date = datetime(2026, 3, 10)
    resource = pool.allocate_resource("quota", work_date)
    if resource:
        print(f"Allocated {resource.name} for modeling on {work_date}")
    else:
        print("No available resources")
    
    # Check utilization
    util = pool.get_utilization(work_date, work_date)
    print(f"Utilization rate: {util:.2%}")