import ZoneList
import Zones
class ZoneFactory:
    @staticmethod
    def getList(region):
        manager=ZonesManager()
        match region:
            case "Aveiro":
                return ZoneList.AveiroZoneList
            case "Lisboa":
                return ZoneList.LisboaZoneList
            case "Algarve":
                return ZoneList.AlgarveZoneList
            case _:
                print(f"Zone not implemented yet({region})!")
                return None

        
class ZonesManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.__regions=[]
        self.zones=Zones.Zones("Aveiro")    
    
    def getAllzones(self):
        allZones=[]
        for region in self.__regions:
            self.zones.setRegion(region)
            allZones.extend(self.zones.getAllZonesFromRegion())
        return allZones
      
    def updateNumRegions(self,newRegions):
        self.__regions.extend(newRegions)
    
    def getRegions(self):
        return self.__regions
