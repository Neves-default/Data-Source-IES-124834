from abc import ABC, abstractmethod
import NoiseLevel
import requests
import threading
import time
from datetime import datetime
# Document Zone
# {
#   id: @8379  #for WAQI
#   Name: Esgueira    
#   Region: Aveiro 
#   Coords: {           #for tomtom
#       Lat: 40.648
#       Lon: -8.625
#   }
#   ZoneType: INDUSTRIAL 
# }
dicionary_lock = threading.Lock()
class API_Requests(ABC):
    response=100
    def __init__(self):
        self.zone=None
        self._historical_request={}

    def setZone(self,zone):
        self.zone=zone
    
    def obtainResponse(self):
        return self.response
    
    def resetCache(self):
        with dicionary_lock:
            self._historical_request={}

    def getCache(self):
        return self._historical_request

    @abstractmethod
    def getData(self):
        pass

    @abstractmethod
    def _format_output(self,api_data):
        pass

    
    

class ForNoiseLevel(API_Requests):
    def __init__(self):
        super().__init__()
        self.noiseLevel = NoiseLevel.NoiseLevel()

    def getData(self,traffic_data=None, weather_data=None):
        if self.zone is None:
            self.response = 400 # Bad Request
            return None
        result=None
        try:
            # Generateing noise
            result = self.noiseLevel.generateData(self.zone,traffic_data=traffic_data,weather_data=weather_data)
            self.response=200
        except Exception as e:
            print(f"An error as occur on the noiseAPI: {e}")
            result=None
            self.response=500
        return result
    def _format_output(self, api_data):
        return None


class ForAirQuality(API_Requests):
    def __init__(self,token):
        super().__init__()
        self.token = token
        self.base_url = "https://api.waqi.info/feed/geo:{lat};{lon}/?token={token}"
    
    def getData(self):
        if self.zone is None:
            self.response = 400
            return None 
        with dicionary_lock: 
            if self.zone["region"] in self._historical_request:
                return self._historical_request[self.zone["region"]]
        try:
            lat = self.zone["coords"]["lat"]
            lon = self.zone["coords"]["lon"]
            # Build the URL with the zone's coordinates
            url = self.base_url.format(lat=lat, lon=lon, token=self.token)
            
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if data["status"] == "ok":
                    self.response = 200
                    data=self._format_output(data["data"])
                    with dicionary_lock:
                        self._historical_request[self.zone["region"]]=data
                    return data
            
            self.response = res.status_code
            return None
        except Exception as e:
            print(f"An error as occur on the WAQI API: {e}")
            self.response = 500
            return None
    
    def _format_output(self, api_data):
        # Individual pollutants extration (IAQI)
        iaqi = api_data.get("iaqi", {})
    
        # Creating a dictionary with the values, using 0 as default if it doesn't exist
        detailed_pollutants = {
            "pm25": iaqi.get("pm25", {}).get("v", 0),
            "pm10": iaqi.get("pm10", {}).get("v", 0),
            "no2": iaqi.get("no2", {}).get("v", 0),
            "so2": iaqi.get("so2", {}).get("v", 0),
            "t": iaqi.get("t", {}).get("v", 0), # Temperature
            "h": iaqi.get("h", {}).get("v", 0)  # Humity
        }

        # Forecast extration - next days
        # Get the PM25 prevision for tomorow
        forecast_list = api_data.get("forecast", {}).get("daily", {}).get("pm25", [])
        next_days_forecast = []
    
        for day in forecast_list[:3]: # We take just the next 3 days
            next_days_forecast.append({
                "day": day.get("day"),
                "avg": day.get("avg"),
                "max": day.get("max")
            })

        return {
            #"city": self.zone["region"],
            #"zone": self.zone["zoneType"],
            "type": "AIR_QUALITY",
            "value": api_data["aqi"],
            "unit": "AQI-index",
            #"timestamp": api_data["time"]["s"],
            "details": detailed_pollutants,      # more detail
            "forecast": next_days_forecast,      # previsions
            "station_name": api_data["city"]["name"]
        }

class ForTrafficDensity(API_Requests):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        # Endpoint to the absolut data flux
        self.base_url = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
    
    def getData(self):
        if self.zone is None:
            self.response = 400
            return None
        with dicionary_lock:
            if self.zone["id"] in self._historical_request:
                return self._historical_request[self.zone["id"]]
        try:
            lat = self.zone["coords"]["lat"]
            lon = self.zone["coords"]["lon"]
            
            # params: key and geografic point
            params = {
                "key": self.api_key,
                "point": f"{lat},{lon}"
            }
            
            res = requests.get(self.base_url, params=params, timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                self.response = 200
                data=self._format_output(data.get("flowSegmentData", {}))
                with dicionary_lock:
                    self._historical_request[self.zone["id"]]=data
                return data
            
            self.response = res.status_code
            return None
            
        except Exception as e:
            print(f"An error has occur in TomTom API: {e}")
            self.response = 500
            return None

    def _format_output(self, api_data):

        curr_speed = api_data.get("currentSpeed", 0)
        free_speed = api_data.get("freeFlowSpeed", 0)
        
        # Time and delayed data(seconds)
        travel_time = api_data.get("currentTravelTime", 0)
        free_travel_time = api_data.get("freeFlowTravelTime", 0)
        
        # Delay is the real diference that the driver feels
        delay = max(0, travel_time - free_travel_time)
        
        # Data's Confidence (0.0-1.0)
        # Indicates if TomTom has real data(close to 1) or estimates(close to 0)
        confidence = api_data.get("confidence", 0)

        # Percentual congestion calculation
        congestion = 0
        if free_speed > 0:
            # The more far away is the real velocity compared to the ideal, bigger is the congestion
            congestion = max(0, round((1 - (curr_speed / free_speed)) * 100, 2))

        return {
            #"city": self.zone["region"],
            #"zone": self.zone["zoneType"],
            "type": "TRAFFIC",
            "current_speed": curr_speed,
            "free_flow_speed": free_speed,
            "congestion_level": f"{congestion}%",
            "travel_delay_seconds": delay,      
            "data_confidence": confidence,      
            "unit": "km/h",
            #"timestamp": datetime.now().isoformat()
        }