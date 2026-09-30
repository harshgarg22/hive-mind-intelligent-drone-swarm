import streamlit as st
import os
import pandas as pd
from core.swarm_logic import SwarmAgent, ConsensusEngine, TaskAllocator

# ==========================================
# 1. PAGE CONFIG & INITIALIZATION
# ==========================================
st.set_page_config(page_title="Presight IntelliCity Command", layout="wide")

if 'threat_detected' not in st.session_state:
    st.session_state.threat_detected = False
if 'drone_1_lost' not in st.session_state:
    st.session_state.drone_1_lost = False

consensus_engine = ConsensusEngine(minimum_threshold=0.85)
allocator = TaskAllocator(critical_battery_level=20)

# ==========================================
# 2. SIDEBAR (OPERATOR CONTROLS)
# ==========================================
st.sidebar.title("Swarm Controls")
if st.sidebar.button("1. Simulate Threat Detection"):
    st.session_state.threat_detected = True
    st.session_state.drone_1_lost = False

if st.sidebar.button("2. Simulate MANET Loss (Drone 01)"):
    st.session_state.drone_1_lost = True

if st.sidebar.button("Reset Swarm"):
    st.session_state.threat_detected = False
    st.session_state.drone_1_lost = False

# ==========================================
# 3. EXPLAINABLE AI (XAI) TOP BANNER
# ==========================================
st.title("Hive Mind: Swarm Oversight Dashboard")
if not st.session_state.threat_detected:
    st.info("🟢 STATUS: Swarm Patrolling. No anomalies detected. Network stable.")
elif st.session_state.threat_detected and not st.session_state.drone_1_lost:
    st.error("🔴 STATUS: Threat Consensus Reached. Target locked. Assigning tracking roles.")
elif st.session_state.drone_1_lost:
    st.warning("🟠 STATUS: Drone 01 Network Lost. System Resilience Loop activated. Roles reassigned.")

# ==========================================
# 4. MULTI-MODAL VIDEO VIEWER (ALWAYS VISIBLE)
# ==========================================
st.markdown("### Edge Perception Feeds")
col1, col2 = st.columns(2)

current_dir = os.path.dirname(os.path.abspath(__file__))
color_vid = os.path.join(current_dir, "assets", "color_processed.mp4")
thermal_vid = os.path.join(current_dir, "assets", "thermal_processed.mp4")

with col1:
    st.markdown("**Drone 01 (Vanguard) - Optical EO**")
    if os.path.exists(color_vid):
        st.video(color_vid)
    else:
        st.error("Video asset missing. Check assets/ folder.")

with col2:
    st.markdown("**Drone 02 (Overwatch) - Thermal LWIR**")
    if os.path.exists(thermal_vid):
        st.video(thermal_vid)
    else:
        st.error("Video asset missing. Check assets/ folder.")

# ==========================================
# 5. DATA STATE DEFINITION (EXPANDED TO 4 DRONES)
# ==========================================
if not st.session_state.threat_detected:
    mock_detections = []
    d1_status = "Connected"
    swarm = [
        SwarmAgent("Drone 01", "optical", battery=86, distance_to_target=500, network_status=d1_status),
        SwarmAgent("Drone 02", "thermal", battery=76, distance_to_target=500, network_status="Connected"),
        SwarmAgent("Drone 03", "optical", battery=92, distance_to_target=500, network_status="Connected"),
        SwarmAgent("Drone 04", "thermal", battery=65, distance_to_target=500, network_status="Connected")
    ]
else:
    mock_detections = [
        {'agent_id': 'Drone_01', 'sensor': 'optical', 'conf': 0.88},
        {'agent_id': 'Drone_02', 'sensor': 'thermal', 'conf': 0.60}
    ]
    
    d1_status = "Disconnected" if st.session_state.drone_1_lost else "Connected"
    swarm = [
        SwarmAgent("Drone 01", "optical", battery=85, distance_to_target=50, network_status=d1_status),
        SwarmAgent("Drone 02", "thermal", battery=75, distance_to_target=60, network_status="Connected"),
        SwarmAgent("Drone 03", "optical", battery=91, distance_to_target=180, network_status="Connected"),
        SwarmAgent("Drone 04", "thermal", battery=64, distance_to_target=220, network_status="Connected")
    ]

consensus_score, is_confirmed = consensus_engine.calculate_consensus(mock_detections)
updated_swarm = allocator.run_micro_auction(swarm)

# ==========================================
# 6. DISTRIBUTED LOGIC UI RENDERING
# ==========================================
st.markdown("---")
st.markdown("### Distributed Logic & Task Allocation")

# Section A: Consensus & Live Ledger
st.markdown("#### 1. Collective Target Identification")
cons_col1, cons_col2 = st.columns([1, 2])
with cons_col1:
    if not mock_detections:
        st.write("Awaiting threat telemetry...")
    else:
        st.metric(label="Calculated Consensus", value=f"{consensus_score * 100:.1f}%", delta="Threat Confirmed" if is_confirmed else "Unconfirmed", delta_color="inverse")
with cons_col2:
    if mock_detections:
        st.markdown("**Live Telemetry JSON Payload**")
        st.json(mock_detections)

# Section B: Micro-Auction Visuals (EXPANDED TO 4 COLUMNS)
st.markdown("#### 2. Micro-Auction Status")
met_cols = st.columns(4)

for i, col in enumerate(met_cols):
    agent = updated_swarm[i]
    with col:
        delta_val = "-100% (Offline)" if agent.network_status == "Disconnected" else f"Bid: {agent.current_bid}"
        delta_color = "normal" if agent.network_status == "Connected" else "inverse"
        st.metric(label=f"{agent.agent_id} - {agent.current_task}", value=agent.network_status, delta=delta_val, delta_color=delta_color)

# Section C: Full Ledger Table
st.markdown("#### 3. Full Swarm Ledger")
ledger_data = []
for agent in updated_swarm:
    ledger_data.append({
        "Unit": agent.agent_id,
        "Network": agent.network_status,
        "Battery (%)": agent.battery,
        "Distance (m)": agent.distance,
        "Calculated Bid": agent.current_bid,
        "Assigned Role": agent.current_task
    })
st.dataframe(pd.DataFrame(ledger_data), use_container_width=True)