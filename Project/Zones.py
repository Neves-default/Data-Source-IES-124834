from ZoneList import AveiroZoneList
from ZonesManager import ZoneFactory
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
class Zones:
    
    region=""
    def __init__(self,region):
        self.region=region
    
    def getAllZonesFromRegion(self):
        zones_ListJSON=[]
        for zone in ZoneFactory.getList(self.region):
            # Creating a document for each zone
            zone_doc = self.__convertIntoJSON(zone)
            zones_ListJSON.append(zone_doc)
        return zones_ListJSON
    
    def getZone(self,zone):
        return self.__convertIntoJSON(zone)
    
    def setRegion(self,region):
        self.region=region
    
    def __convertIntoJSON(self,zone):
        return {
            "id": zone.name.lower(),
            "name": zone.name.replace("_", " ").title(),
            "radius": self.__getRadius(zone.value.zone_type),
            "region": self.region,
            "coords": {
                "lat": zone.value.lat,
                "lon": zone.value.lon
            },
            "zoneType": zone.value.zone_type
        }
    def __getRadius(self,zoneType):
        match (zoneType):
            case "DOWNTOWN":
                return 400
            case "COMMERCIAL_DISTRICT":
                return 300
            case "INDUSTRIAL_PARK":
                return 800
            case "RESIDENTIAL_NORTH":
                return 300
            case _:
                return 500
    

