class BusinessCalendar:
    """Manages business calendar with holidays and vacations"""
    def __init__(self, name, work_days=(0, 1, 2, 3, 4), # Mon-Fri
                 holidays=None, vacations=None):
        self.name = name
        self.work_days = work_days  # Weekdays considered work days (0=Mon, 6=Sun)
        self.holidays = set(holidays) if holidays else set()
        self.vacations = vacations if vacations else {}
    
    def is_workday(self, date):
        """Check if a date is a work day"""
        return (
            date.weekday() in self.work_days and
            date not in self.holidays and
            not any(start <= date <= end for start, end in self.vacations)
        )
    
    def next_workday(self, date):
        """Get the next business day"""
        next_day = date + timedelta(days=1)
        while not self.is_workday(next_day):
            next_day += timedelta(days=1)
        return next_day

class ProductionParameters:
    """Central repository for production parameters"""
    def __init__(self):
        self.creative_calendar = {}  # {asset_id: datetime}
        self.delivery_calendar = {}  # {project_id: datetime}
        self.complexity_matrix = {}  # {item_id: {"level": "alta/baja", "values": {...}}}
        self.workflow_definitions = {}  # {workflow_type: WorkflowDefinition}
        self.resource_calendars = {}  # {resource_type: BusinessCalendar}
    
    def add_resource_calendar(self, name, calendar):
        """Add a new resource calendar"""
        self.resource_calendars[name] = calendar
    
    def add_creative_input(self, asset_id, date):
        """Register creative input date"""
        self.creative_calendar[asset_id] = date
    
    def set_delivery_deadline(self, project_id, date):
        """Set project delivery deadline"""
        self.delivery_calendar[project_id] = date
    
    def define_complexity(self, item_id, level, details):
        """Define complexity for an asset/shot"""
        self.complexity_matrix[item_id] = {
            "level": level,
            "details": details
        }
    
    def create_workflow(self, workflow_type, stages):
        """Define a new workflow type"""
        self.workflow_definitions[workflow_type] = WorkflowDefinition(stages)
        
    def get_stage_bid(self, workflow_type, stage, complexity):
        """Get bid time for a stage based on complexity"""
        wf = self.workflow_definitions.get(workflow_type)
        if wf and stage in wf.stages:
            return wf.stages[stage].get(complexity, wf.stages[stage]["default"])
        return 0

class WorkflowDefinition:
    """Detailed workflow definition with stage information"""
    def __init__(self, stages):
        """
        stages: dict of stage definitions
        Example:
        {
            "modelado": {
                "default": 3,
                "alta": 5,
                "baja": 2,
                "resource_type": "quota",
                "review": False
            },
            "layout_review": {
                "default": 1,
                "resource_type": "review",
                "review": True,
                "approval_required": True
            }
        }
        """
        self.stages = stages
        self.stage_order = list(stages.keys())
        
    def get_next_stage(self, current_stage):
        """Get the next stage in the workflow"""
        idx = self.stage_order.index(current_stage)
        if idx < len(self.stage_order) - 1:
            return self.stage_order[idx + 1]
        return None

# Example usage
if __name__ == "__main__":
    from datetime import datetime, timedelta
    
    # Create studio calendar (Mon-Fri with holiday)
    studio_cal = BusinessCalendar(
        "Studio Calendar",
        holidays=[datetime(2026, 12, 25)],  # Christmas
        vacations=[
            (datetime(2026, 8, 1), datetime(2026, 8, 15))  # Summer break
        ]
    )
    
    params = ProductionParameters()
    params.add_resource_calendar("studio", studio_cal)
    
    # Add sample creative input
    params.add_creative_input("asset_caballo", datetime(2026, 3, 1))
    
    # Define complexity
    params.define_complexity("asset_caballo", "alta", {
        "modelado": 5,
        "layout": 3,
        "anim": 8
    })
    
    # Define workflow
    params.create_workflow("asset_workflow", [
        "modelado",
        "layout_review",
        "anim",
        "final_review"
    ])
    
    print("Production Parameters initialized successfully")