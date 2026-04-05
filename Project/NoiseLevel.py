from datetime import datetime
import random
import Zones

#{
#   "city": "Aveiro",
#   "zone": INDUSTRIAL_PARK,
#   "type": "NOISE",
#   "value": 40,
#   "unit": "dB",
#   "timestamp": "2026-04-03T16:01:06.598235"
#}
class NoiseLevel:

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NoiseLevel, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
    
    def generateData(self,zone,traffic_data=None, weather_data=None):
        atual_Hour=datetime.now().hour
        
        base=self.__base(zone["zoneType"])
        
        variation=-1
        if 8 <= atual_Hour <= 9 or 17 <= atual_Hour <= 19:
            variation = random.uniform(15, 25) 
        else:
            variation = random.uniform(0, 10)
        
        # 2. Congestion bonus (Based on TomTom's real traffic)
        traffic_bonus = 0
        if traffic_data and "congestion_level" in traffic_data:
            # Converts "45.5%" in 45.5
            c_level = float(traffic_data["congestion_level"].replace("%", ""))
            traffic_bonus = c_level * 0.1 
        
        # 3. Raining/wet streets factor(Based on Waqi)
        weather_bonus = 0
        if weather_data and weather_data.get("details", {}).get("h", 0) > 80:
            weather_bonus = random.uniform(3, 5)

        # 4. Random Events (Sirens/big trucks)
        # 2% probability of a sound peak.
        spike = 20 if random.random() < 0.02 else 0

        noise_level = round(base + variation + traffic_bonus + weather_bonus + spike, 2)

        return {
            #"city": zone["region"],
            #"zone": zone["zoneType"],
            "type": "NOISE",
            "value": noise_level,
            "unit": "dB",
            "is_anomaly": spike > 0, 
            #"timestamp": datetime.now().isoformat()
        }
    
    def __base(self, zone_type):
        bases = {
            'INDUSTRIAL_PARK': 60,
            'DOWNTOWN': 55,
            'COMMERCIAL_DISTRICT': 55,
            'RESIDENTIAL_NORTH': 40
        }
        return bases.get(zone_type, 40) # 40 is the default value
    
        