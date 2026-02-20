from datetime import datetime, timedelta
from production_params import ProductionParameters, BusinessCalendar, WorkflowDefinition
from resource_pool import ResourcePool
import simpy

class ProductionEvent:
    """Represents a production event in the simulation"""
    def __init__(self, item_id, stage, start_time, end_time, resource):
        self.item_id = item_id
        self.stage = stage
        self.start_time = start_time
        self.end_time = end_time
        self.resource = resource
        self.duration = (end_time - start_time).total_seconds() / 3600  # Hours

class AnimSimulator:
    """Core animation production simulator"""
    def __init__(self, params):
        self.params = params
        self.env = simpy.Environment()
        self.resource_pool = ResourcePool(params.resource_calendars["studio"])
        self.events = []  # Track all production events
        self.current_date = datetime.now()
        
        # Register resources from parameters
        self._register_resources()
    
    def _register_resources(self):
        """Register resources based on typical studio setup"""
        # Modelado team
        self.resource_pool.add_resource("m1", "Modeling Artist", "quota")
        self.resource_pool.add_resource("m2", "Modeling Artist", "quota")
        
        # Layout team
        self.resource_pool.add_resource("l1", "Layout Artist", "quota")
        self.resource_pool.add_resource("l2", "Layout Artist", "quota")
        
        # Animation team
        self.resource_pool.add_resource("a1", "Animation Artist", "quota")
        self.resource_pool.add_resource("a2", "Animation Artist", "quota")
        self.resource_pool.add_resource("a3", "Animation Artist", "quota")
        
        # Support team
        self.resource_pool.add_resource("s1", "Support Technician", "support")
    
    def schedule_production(self, project_id, assets):
        """Schedule production for a project's assets"""
        for asset_id in assets:
            workflow = self.params.workflow_definitions["asset_workflow"]
            complexity = self.params.complexity_matrix[asset_id]["level"]
            
            # Create production process for this asset
            self.env.process(self.process_asset(asset_id, workflow, complexity))
    
    def process_asset(self, asset_id, workflow, complexity):
        """Process an asset through its workflow"""
        current_stage = workflow.stage_order[0]
        
        while current_stage:
            stage_def = workflow.stages[current_stage]
            bid_hours = stage_def.get(complexity, stage_def["default"])
            
            # Wait until creative input date if first stage
            if current_stage == workflow.stage_order[0]:
                input_date = self.params.creative_calendar[asset_id]
                yield self.env.timeout((input_date - self.current_date).total_seconds())
            
            # Find available resource
            resource_type = stage_def["resource_type"]
            start_time = self.current_date + timedelta(days=self.env.now)
            resource = self.resource_pool.allocate_resource(resource_type, start_time, bid_hours)
            
            if resource:
                # Process the stage
                start = self.current_date + timedelta(days=self.env.now)
                yield self.env.timeout(bid_hours * 24)  # Convert hours to days
                end = self.current_date + timedelta(days=self.env.now)
                
                # Record event
                self.events.append(ProductionEvent(
                    asset_id, current_stage, start, end, resource.name
                ))
            else:
                # Resource conflict - apply conflict resolution
                resolved = self.resolve_conflict(asset_id, current_stage)
                if not resolved:
                    print(f"Warning: {asset_id} stalled at {current_stage}")
                    yield self.env.timeout(1)  # Wait a day and retry
                    continue
            
            # Move to next stage
            current_stage = workflow.get_next_stage(current_stage)
    
    def resolve_conflict(self, asset_id, stage):
        """Resolve resource conflicts using min-cost flow algorithm"""
        # Get all pending tasks for this resource type
        pending_tasks = self._get_pending_tasks(stage)
        if not pending_tasks:
            return False
            
        # Create flow network
        flow_graph = self._create_flow_network(pending_tasks)
        
        # Solve min-cost flow
        assigned = self._solve_min_cost_flow(flow_graph)
        
        # Apply assignments
        for task, resource in assigned.items():
            # Actual assignment would happen here
            print(f"Assigned {task} to {resource}")
            
        return True
    
    def _get_pending_tasks(self, stage):
        """Get all pending tasks for a given stage"""
        # In a real implementation, this would query the simulation state
        # For now, return sample data
        return [
            {"asset_id": "asset1", "priority": 1, "stage": stage},
            {"asset_id": "asset2", "priority": 2, "stage": stage},
            {"asset_id": "asset3", "priority": 3, "stage": stage}
        ]
    
    def _create_flow_network(self, tasks):
        """Create flow network for min-cost flow algorithm"""
        # Simplified representation:
        # Nodes: source, tasks, resources, sink
        # Edges: source->tasks, tasks->resources, resources->sink
        return {
            "tasks": tasks,
            "resources": ["m1", "m2", "l1", "l2", "a1", "a2", "a3"],
            "edges": [
                # Format: (from, to, capacity, cost)
                # Source to tasks
                ("source", "asset1", 1, 1),
                ("source", "asset2", 1, 2),
                ("source", "asset3", 1, 3),
                
                # Tasks to resources
                ("asset1", "m1", 1, 0),
                ("asset1", "m2", 1, 0),
                ("asset2", "l1", 1, 0),
                ("asset2", "l2", 1, 0),
                ("asset3", "a1", 1, 0),
                ("asset3", "a2", 1, 0),
                ("asset3", "a3", 1, 0),
                
                # Resources to sink
                ("m1", "sink", 1, 0),
                ("m2", "sink", 1, 0),
                ("l1", "sink", 1, 0),
                ("l2", "sink", 1, 0),
                ("a1", "sink", 1, 0),
                ("a2", "sink", 1, 0),
                ("a3", "sink", 1, 0)
            ]
        }
    
    def _solve_min_cost_flow(self, graph):
        """Solve min-cost flow problem (simplified Edmonds-Karp)"""
        # In a full implementation, this would be a proper algorithm
        # For demo purposes, return a simple assignment
        return {
            "asset1": "m1",
            "asset2": "l1",
            "asset3": "a1"
        }
    
    def run(self, until=365):
        """Run the simulation"""
        self.env.run(until=until)
        
        # Print simulation summary
        print(f"Simulation completed in {self.env.now} days")
        print(f"Total production events: {len(self.events)}")

# Example usage
if __name__ == "__main__":
    # Create parameters (reuse from production_params example)
    params = ProductionParameters()
    
    # Create simulator
    simulator = AnimSimulator(params)
    
    # Schedule production
    simulator.schedule_production("proj_ep1", ["asset_caballo"])
    
    # Run simulation
    simulator.run()