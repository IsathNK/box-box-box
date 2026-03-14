#!/usr/bin/env python3
import json
import sys

# ---------------------------------------------------------
# CURRENT BEST PHYSICS PARAMETERS (37/100)
# ---------------------------------------------------------


PARAMS = {
      'SOFT':   {'offset': 2.959679, 'cliff': 10, 'deg': 0.393913},
      'MEDIUM': {'offset': 3.928766, 'cliff': 20, 'deg': 0.200049},
      'HARD':   {'offset': 4.726468, 'cliff': 30, 'deg': 0.101575},
      'temp_coef': 0.112732
  }

def calc_stint_time(tire_name, laps, base_time, temp):
    if laps <= 0: 
        return 0.0
        
    tire = PARAMS[tire_name]
    
    # Base speed for this tire compound
    lap_speed = base_time + tire["offset"]
    
    # Temperature impact on degradation
    actual_deg = tire["deg"] * (1.0 + temp * PARAMS["temp_coef"])
    
    # Base time for all laps in the stint
    total_stint_time = laps * lap_speed
    
    # Add degradation penalty only for laps beyond the cliff
    if laps > tire["cliff"]:
        n = laps - tire["cliff"]
        # Arithmetic progression: sum of 1 + 2 + 3 ... n
        total_stint_time += actual_deg * (n * (n + 1)) / 2.0
        
    return total_stint_time

def main():
    # Read STDIN
    input_data = sys.stdin.read()
    if not input_data.strip():
        return
        
    try: 
        test_case = json.loads(input_data)
    except Exception: 
        sys.exit(1)
        
    config = test_case['race_config']
    base = config['base_lap_time']
    temp = config['track_temp']
    pit_time = config['pit_lane_time']
    
    results = []
    
    for pos, strategy in test_case['strategies'].items():
        driver = strategy['driver_id']
        pit_stops = sorted(strategy.get('pit_stops', []), key=lambda x: x['lap'])
        
        total = 0.0
        curr_lap = 1
        curr_tire = strategy['starting_tire']
        
        # Calculate time for each stint between pit stops
        for stop in pit_stops:
            stint_laps = stop['lap'] - curr_lap + 1
            total += calc_stint_time(curr_tire, stint_laps, base, temp)
            total += pit_time
            curr_lap = stop['lap'] + 1
            curr_tire = stop['to_tire']
            
        # Calculate final stint to the end of the race
        final_laps = config['total_laps'] - curr_lap + 1
        total += calc_stint_time(curr_tire, final_laps, base, temp)
        
        results.append((total, driver))
    
    # Sort by lowest total time, using driver_id as a tie-breaker
    results.sort(key=lambda x: (round(x[0], 5), x[1]))
    
    output = {
        'race_id': test_case['race_id'], 
        'finishing_positions': [r[1] for r in results]
    }
    
    print(json.dumps(output))

if __name__ == '__main__':
    main()