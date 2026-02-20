import streamlit as st
from datetime import datetime, timedelta
from production_params import ProductionParameters, BusinessCalendar
from resource_pool import ResourcePool
from simulator import AnimSimulator
import pandas as pd
import plotly.express as px

# Initialize session state
if 'simulator' not in st.session_state:
    st.session_state.simulator = None
    st.session_state.results = None

# App title and description
st.title("AnimTycoon Production Simulator")
st.markdown("""
This simulator helps optimize resource allocation for 3D animation production pipelines.
Adjust team sizes using the sliders below and run simulations to see their impact.
""")

# Resource allocation sliders
st.sidebar.header("Resource Allocation")
modelado_team = st.sidebar.slider("Modeling Team Size", 1, 10, 2)
layout_team = st.sidebar.slider("Layout Team Size", 1, 8, 2)
anim_team = st.sidebar.slider("Animation Team Size", 1, 12, 3)
support_team = st.sidebar.slider("Support Team Size", 0, 5, 1)

# Simulation controls
st.sidebar.header("Simulation")
project_duration = st.sidebar.slider("Project Duration (days)", 30, 365, 180)
run_simulation = st.sidebar.button("Run Simulation")

# Initialize parameters
params = ProductionParameters()

# Set up studio calendar
studio_cal = BusinessCalendar("Studio Calendar")
params.add_resource_calendar("studio", studio_cal)

# Add sample assets
params.add_creative_input("asset_caballo", datetime(2026, 3, 1))
params.add_creative_input("shot_sec1", datetime(2026, 3, 5))

# Define complexities
params.define_complexity("asset_caballo", "alta", {
    "modelado": 5,
    "layout": 3,
    "anim": 8
})
params.define_complexity("shot_sec1", "baja", {
    "modelado": 2,
    "layout": 1,
    "anim": 4
})

# Define workflow
params.create_workflow("asset_workflow", {
    "modelado": {"default": 3, "alta": 5, "baja": 2, "resource_type": "quota"},
    "layout": {"default": 2, "alta": 3, "baja": 1, "resource_type": "quota"},
    "anim": {"default": 4, "alta": 8, "baja": 4, "resource_type": "quota"}
})

# Run simulation when requested
if run_simulation:
    with st.spinner("Running simulation..."):
        # Create simulator with current parameters
        simulator = AnimSimulator(params)
        
        # Update resource counts based on sliders
        simulator.resource_pool = ResourcePool(studio_cal)
        
        # Add resources based on slider settings
        for i in range(modelado_team):
            simulator.resource_pool.add_resource(f"m{i+1}", "Modeling Artist", "quota")
        
        for i in range(layout_team):
            simulator.resource_pool.add_resource(f"l{i+1}", "Layout Artist", "quota")
            
        for i in range(anim_team):
            simulator.resource_pool.add_resource(f"a{i+1}", "Animation Artist", "quota")
            
        for i in range(support_team):
            simulator.resource_pool.add_resource(f"s{i+1}", "Support Technician", "support")
        
        # Schedule production
        simulator.schedule_production("proj_ep1", ["asset_caballo", "shot_sec1"])
        
        # Run simulation
        simulator.run(until=project_duration)
        
        # Store results
        st.session_state.simulator = simulator
        st.session_state.results = simulator.events

# Display results if available
if st.session_state.results:
    st.header("Simulation Results")
    
    # Convert events to DataFrame
    events_df = pd.DataFrame([{
        "Asset": e.item_id,
        "Stage": e.stage,
        "Start": e.start_time,
        "End": e.end_time,
        "Resource": e.resource,
        "Duration (hrs)": e.duration
    } for e in st.session_state.results])
    
    # Show KPIs
    st.subheader("Key Performance Indicators")
    col1, col2, col3 = st.columns(3)
    total_days = (events_df["End"].max() - events_df["Start"].min()).days
    col1.metric("Total Production Days", f"{total_days} days")
    col2.metric("Assets Completed", f"{events_df['Asset'].nunique()} assets")
    col3.metric("Resource Utilization", "85%")  # Placeholder
    
    # Show Gantt chart
    st.subheader("Production Timeline")
    fig = px.timeline(
        events_df, 
        x_start="Start", 
        x_end="End", 
        y="Asset", 
        color="Stage",
        title="Animation Production Timeline"
    )
    fig.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig)
    
    # Show raw data
    st.subheader("Event Details")
    st.dataframe(events_df)
    
    # Export to CSV
    if st.button("Export to CSV"):
        csv = events_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="production_simulation.csv",
            mime="text/csv"
        )

# Display placeholder if no results
elif run_simulation:
    st.warning("Simulation completed but no results to display")
else:
    st.info("Configure resources and click 'Run Simulation' to start")