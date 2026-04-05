"""
============================================================================================
        DATA SOURCE v.1.0
============================================================================================
"""
"""Main APIs(Noise_level)"""
# {
#   id: centro_avenida
#   Name: Esgueira    
#   Region: Aveiro 
#   Coords: {           #for tomtom
#       Lat: 40.648
#       Lon: -8.625
#   }# Traffic Density:
#   Zona Industrial (Norte/Esgueira):40.648, -8.625
#   Zona de Serviços/Comercial (Centro): 40.643, -8.648
#   Zona Académica/Residencial (Sul): 40.630, -8.655
# Air Qulity:
#   Sensor Industrial: @8379 (Aveiro-Esgueira)
#   Sensor Urbano/Centro: aveiro
# Documento a enviar para a Queue
#   ZoneType: INDUSTRIAL_PARK 
#   "timestamp": "2026-04-03T20:34:40.571913"
#   Data: {
#      "type": "NOISE",
#      "value": noise_level,
#      "unit": "dB",
#      "is_anomaly": spike, 
#   }
# }
"""Main APIs(Air quality)"""
# {
#   id: centro_avenida
#   Name: Esgueira    
#   Region: Aveiro 
#   Coords: {           #for tomtom
#       Lat: 40.648
#       Lon: -8.625
#   }
#   ZoneType: INDUSTRIAL_PARK 
#   "timestamp": "2026-04-03T20:34:40.571913"
#   {
#      "type": "AIR_QUALITY",
#      "value": 50,
#      "unit": "AQI-index",
#      "details": {
#          "pm25": 50,
#          "pm10": 30,
#          "no2": 4.2,
#          "so2": 0,
#          "t": 17,
#          "h": 63
#      },
#      "forecast": [],
#      "station_name": "Sobreiras-Lordelo do Ouro, Porto, Portugal"
#   }
# }
"""Main APIs(Traffic Jam)"""
# {
#   id: centro_avenida
#   Name: Esgueira    
#   Region: Aveiro 
#   Coords: {           #for tomtom
#       Lat: 40.648
#       Lon: -8.625
#   }
#   ZoneType: INDUSTRIAL_PARK 
#   "timestamp": "2026-04-03T20:34:40.571913"
#   {
#       "type": "TRAFFIC",
#       "current_speed": 46,
#       "free_flow_speed": 46,
#       "congestion_level": "0%",
#       "travel_delay_seconds": 0,
#       "data_confidence": 1,
#       "unit": "km/h",
#    }
# }

from datetime import datetime

import pika
import API_Requests
import json
import threading
import time
import ZonesManager
import ZoneList
# proxy for Simulation Agent is working too :)
# the complete main api is functional :)
# concorrencial part done :)))
# Tomorrow: 
#   -> Scalability: I will do it later...
#       -> put more zones
#       -> allow adding new zones or new APIs 
#   -> Activate RABBITMQ: done :)

"""GLOBAL DATA"""
CONTROL = threading.Lock()

WAQI_TOKEN = "e1efed23182aa81cccacb75b7369e8f61c49278a"
TOMTOM_KEY = "3JxP0zJl55ipLB0cQfqRfyuPnPZSaDDH"

RABBITMQ_HOST="localhost"
RABBITMQ_HEARTBEAT=600

TIME_NOISE_LEVEL=10#0.1#10
TIME_AIR_QUALITY=60*60#0.5#60*60
TIME_TRAFFIC_DENSITY=20*60#0.5#20*60

NUM_APIs=3
REQUESTS={
    "AirQuality":API_Requests.ForAirQuality(WAQI_TOKEN),
    "NoiseLevel":API_Requests.ForNoiseLevel(),
    "TrafficJam":API_Requests.ForTrafficDensity(TOMTOM_KEY)
}

REGIONS={
    "Aveiro":ZoneList.AveiroZoneList,
    "Lisboa":ZoneList.LisboaZoneList,
    "Algarve":ZoneList.AlgarveZoneList
}
#============================================================================================

"""REQUESTS TO THE APIs"""
def makeRequest(request,zone):
    with CONTROL:
        request.setZone(zone)
        data=request.getData()
    if (request.obtainResponse()!=200):
        print(f"An error occur during the APIs request:{request.obtainResponse()}")
        return None
    return data

def loadZones():
    manager=ZonesManager.ZonesManager()
    manager.updateNumRegions(REGIONS)
    return manager.getAllzones()

    
def requestAirQuality(zone):
    request=REQUESTS["AirQuality"]
    return makeRequest(request,zone)

def requestTrafficJam(zone):
    request=REQUESTS["TrafficJam"]
    return makeRequest(request,zone)

def requestNoiseLevel(zone):
    request=REQUESTS["NoiseLevel"]
    traffic_api = REQUESTS["TrafficJam"]
    air_api = REQUESTS["AirQuality"]
    with CONTROL:
        request.setZone(zone)

        #getting the right data    
        t_cache = traffic_api.getCache().get(zone["id"])
        a_cache = air_api.getCache().get(zone["region"])
        
        data=request.getData(traffic_data=t_cache,weather_data=a_cache)
    
    if (request.obtainResponse()!=200):
        print(f"An error occur during the APIs request:{request.obtainResponse()}")
        return None
    return data
#============================================================================================

"""BUILD THE APIs"""

def formGenericMainAPI(zone):
    api=zone.copy()
    #register date time
    api["timestamp"]=datetime.now().isoformat()
    return api

def formNoiseLevelAPI(zone):
    api=formGenericMainAPI(zone)
    api["data"]=requestNoiseLevel(zone)
    return api

def formAirQualityAPI(zone):
    api=formGenericMainAPI(zone)
    api["data"]=requestAirQuality(zone)
    return api

def formTrafficJamAPI(zone):
    api=formGenericMainAPI(zone)
    api["data"]=requestTrafficJam(zone)
    return api
#============================================================================================

"""CONNECTIONS TO RABBITMQ"""

def create_channel():
    """Creates a exclusive connection for a thread."""
    conn = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, heartbeat=RABBITMQ_HEARTBEAT)
    )
    ch = conn.channel()
    ch.queue_declare(queue='city_data_queue', durable=True)

    ch.confirm_delivery()

    return conn, ch
def publish_message(channel_info, message, thread_name):
    """
    Publishes a message using auto-reconnection 
    channel_info: a list [connection, channel] used to allow reference updating
    """
    published = False
    while not published:
        try:
            channel_info[1].basic_publish(
                exchange='',
                routing_key='city_data_queue',
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            published = True
        except (pika.exceptions.AMQPConnectionError, pika.exceptions.AMQPChannelError):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Reconnecting {thread_name}...")
            time.sleep(2)
            try:
                # Closes the old connection and creates a new one
                new_conn, new_ch = create_channel()
                channel_info[0] = new_conn
                channel_info[1] = new_ch
            except Exception as e:
                print(f"Failed to reconnect {thread_name}: {e}")
#============================================================================================

"""TASKs FOR EACH THREAT"""

def task_traffic_priority(zones,ch_info):
    """Updates the traffic each 20 minutes"""
    while True:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] --- UPDATE: Traffic (20 min) ---")
        for zo in zones:
            data=formTrafficJamAPI(zo)
            message = json.dumps(data, ensure_ascii=False)
            publish_message(ch_info,message,"TrafficThread")
        time.sleep(TIME_TRAFFIC_DENSITY)
        REQUESTS["TrafficJam"].resetCache()

def task_air_quality(zones,ch_info):
    """Updates the air quality each 1 hour"""
    while True:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] --- UPDATE: Air (1 hora) ---")
        for zo in zones:
            data=formAirQualityAPI(zo)
            message = json.dumps(data, ensure_ascii=False)
            publish_message(ch_info,message, "AirThread")
        time.sleep(TIME_AIR_QUALITY)
        REQUESTS["AirQuality"].resetCache()

def task_noise_trigger(zones,ch_info):
    """Just manages the 10 seconds cycle and triggers the process"""
    while True:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] --- UPDATE: Noise (10 segundos) ---")
        for zo in zones:
            data=formNoiseLevelAPI(zo)
            if data.get("data"):
                message = json.dumps(data, ensure_ascii=False)
                publish_message(ch_info, message, "NoiseThread")
                
        time.sleep(TIME_NOISE_LEVEL)
#============================================================================================

"""MAIN CODE"""

def main():
    """===================================Main code====================================="""
    try: 

        # Request(time):
        # Noise Level: 10-10 seconds
        # Air Quality: 1-1 hour
        # Traffic Density: 20-20 min(prioritary)
        zones=loadZones()

        # Creating a channel structure that can be updated by the threads
        info_t = list(create_channel()) # [conn, channel]
        info_a = list(create_channel())
        info_n = list(create_channel())
        
        
        # Creating independent threads
        t_traffic = threading.Thread(target=task_traffic_priority, args=(zones,info_t), daemon=True)
        t_air = threading.Thread(target=task_air_quality, args=(zones,info_a), daemon=True)
        t_noise = threading.Thread(target=task_noise_trigger, args=(zones,info_n), daemon=True)

        # Iniciate the parallel process
        t_traffic.start()
        t_air.start()
        t_noise.start()

        try:
            while True: 
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nProcess interrupted by the User. Clossing...")

        # Closes  the connections
        for info in [info_t, info_a, info_n]:
            try:
                info[1].close()
                info[0].close()
            except: pass
        return 0

    except Exception as e:
        print(f"!!! Critical error on the RAbbitMQ: {e}")
        return 1


if __name__=="__main__":
    main()