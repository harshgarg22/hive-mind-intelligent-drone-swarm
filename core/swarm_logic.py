class SwarmAgent:
    def __init__(self, agent_id, sensor_type, battery, distance_to_target, network_status="Connected", within_geofence=True):
        self.agent_id = agent_id
        self.sensor_type = sensor_type
        self.battery = battery
        self.distance = distance_to_target
        self.network_status = network_status
        self.within_geofence = within_geofence
        self.current_task = "Patrol"
        self.current_bid = 0.0

class ConsensusEngine:
    def __init__(self, minimum_threshold=0.85):
        self.minimum_threshold = minimum_threshold
        self.sensor_weights = {'optical': 1.0, 'thermal': 1.2}

    def calculate_consensus(self, detections):
        if not detections:
            return 0.0, False

        total_score = 0.0
        total_weight = 0.0

        for d in detections:
            weight = self.sensor_weights.get(d['sensor'], 1.0)
            total_score += (d['conf'] * weight)
            total_weight += weight

        consensus_score = total_score / total_weight
        is_confirmed = consensus_score >= self.minimum_threshold
        return round(consensus_score, 3), is_confirmed

class TaskAllocator:
    def __init__(self, critical_battery_level=20):
        self.critical_battery = critical_battery_level

    def run_micro_auction(self, agents):
        highest_bid = -float('inf')
        winning_agent = None

        for agent in agents:
            if agent.network_status != "Connected":
                agent.current_task = "Network Lost"
                agent.current_bid = 0.0
                continue
                
            if not agent.within_geofence:
                agent.current_task = "Return to Bounds"
                agent.current_bid = 0.0
                continue
                
            if agent.battery < self.critical_battery:
                agent.current_task = "Return to Base"
                agent.current_bid = 0.0
                continue

            # Normalized Bid Formula (0-100 scale)
            # 50% weight to battery, 50% weight to proximity (assuming 500m max range)
            battery_score = (agent.battery / 100) * 50
            proximity_score = max(0, ((500 - agent.distance) / 500) * 50)
            
            bid = round(battery_score + proximity_score, 1)
            agent.current_bid = bid

            if bid > highest_bid:
                highest_bid = bid
                winning_agent = agent

        if winning_agent:
            winning_agent.current_task = "Close-Range Tracking"
            for agent in agents:
                if agent != winning_agent and agent.network_status == "Connected":
                    agent.current_task = "Comms Relay / Overwatch"

        return agents

# ==========================================
# TEST BLOCK: Verify logic before Phase 3
# ==========================================
if __name__ == "__main__":
    print("--- TESTING CONSENSUS ENGINE ---")
    consensus_engine = ConsensusEngine(minimum_threshold=0.80)
    
    # Scenario: Optical sees something (0.85), Thermal is obscured (0.40)
    mock_detections = [
        {'agent_id': 'Drone_01', 'sensor': 'optical', 'conf': 0.85},
        {'agent_id': 'Drone_02', 'sensor': 'thermal', 'conf': 0.40}
    ]
    score, confirmed = consensus_engine.calculate_consensus(mock_detections)
    print(f"Detections: {mock_detections}")
    print(f"Calculated Consensus: {score} | Threat Confirmed: {confirmed}")
    print("Notice how the low thermal score pulls the consensus down, preventing a false positive.\n")

    print("--- TESTING TASK ALLOCATOR & GUARDRAILS ---")
    allocator = TaskAllocator(critical_battery_level=20)
    
    swarm = [
        SwarmAgent("Drone_01", "optical", battery=85, distance_to_target=50),
        SwarmAgent("Drone_02", "thermal", battery=15, distance_to_target=10), # Should trigger battery guardrail
        SwarmAgent("Drone_03", "optical", battery=90, distance_to_target=200, network_status="Disconnected") # Should trigger network guardrail
    ]

    updated_swarm = allocator.run_micro_auction(swarm)
    for agent in updated_swarm:
        print(f"[{agent.agent_id}] Bid: {agent.current_bid} | Task Assigned: {agent.current_task}")