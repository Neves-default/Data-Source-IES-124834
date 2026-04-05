import enum
from typing import NamedTuple

class ZoneInfo(NamedTuple):
    lat: float
    lon: float
    zone_type: str

class AveiroZoneList(enum.Enum):
    # --- ZONA CENTRAL (Comércio e Serviços) ---
    CENTRO_AVENIDA = ZoneInfo(40.6435, -8.6488, "DOWNTOWN")
    CENTRO_FORUM = ZoneInfo(40.6412, -8.6535, "COMMERCIAL_DISTRICT")
    CENTRO_ESTACAO = ZoneInfo(40.6450, -8.6400, "DOWNTOWN")
    CENTRO_MERCADO = ZoneInfo(40.6442, -8.6560, "COMMERCIAL_DISTRICT")
    
    # --- ZONA INDUSTRIAL / LOGÍSTICA ---
    IND_TABOEIRA_N = ZoneInfo(40.6482, -8.6254, "INDUSTRIAL_PARK")
    IND_ESGUEIRA = ZoneInfo(40.6550, -8.6300, "INDUSTRIAL_PARK")
    PORTO_AVEIRO_1 = ZoneInfo(40.6402, -8.7005, "INDUSTRIAL_PARK")


    # --- ZONA RESIDENCIAL / ACADÉMICA ---
    RES_UNIVERSIDADE = ZoneInfo(40.6305, -8.6575, "RESIDENTIAL_NORTH")
    RES_LICEU = ZoneInfo(40.6330, -8.6500, "RESIDENTIAL_NORTH")
    RES_ALBOI = ZoneInfo(40.6380, -8.6580, "RESIDENTIAL_NORTH")
    
    # --- EIXOS RODOVIÁRIOS (Tráfego Intenso) ---
    ROAD_A25_SAIDA = ZoneInfo(40.6465, -8.6100, "INDUSTRIAL_PARK")
    ROAD_N109_SUL = ZoneInfo(40.6200, -8.6520, "RESIDENTIAL_NORTH")


class LisboaZoneList(enum.Enum):
    # --- ZONA CENTRAL / COMERCIAL (Baixa e Avenidas) ---
    BAIXA_CHIADO = ZoneInfo(38.7109, -9.1367, "DOWNTOWN")
    MARQUES_POMBAL = ZoneInfo(38.7253, -9.1500, "DOWNTOWN")
    AV_LIBERDADE = ZoneInfo(38.7200, -9.1460, "COMMERCIAL_DISTRICT")
    SALDANHA = ZoneInfo(38.7350, -9.1450, "COMMERCIAL_DISTRICT")
    
    # --- ZONA INDUSTRIAL / LOGÍSTICA (Zona Oriental) ---
    CABO_RUIVO = ZoneInfo(38.7483, -9.1021, "INDUSTRIAL_PARK")
    BEATO_CREATIVE = ZoneInfo(38.7350, -9.1050, "INDUSTRIAL_PARK")
    PORTO_LISBOA = ZoneInfo(38.7020, -9.1700, "INDUSTRIAL_PARK")
    
    # --- ZONA RESIDENCIAL / ACADÉMICA ---
    CIDADE_UNIVERSITARIA = ZoneInfo(38.7520, -9.1550, "RESIDENTIAL_NORTH")
    ALVALADE = ZoneInfo(38.7500, -9.1400, "RESIDENTIAL_NORTH")
    BELEM_TORRE = ZoneInfo(38.6916, -9.2160, "RESIDENTIAL_NORTH")
    BENFICA_ESTADIO = ZoneInfo(38.7527, -9.1847, "RESIDENTIAL_NORTH")

class AlgarveZoneList(enum.Enum):
    # --- TRANSPORTES E LOGÍSTICA ---
    FARO_AIRPORT = ZoneInfo(37.0176, -7.9697, "INDUSTRIAL_PARK")      # Aviões + Rent-a-car
    FARO_TRAIN_STATION = ZoneInfo(37.0195, -7.9390, "DOWNTOWN")       # Interface Comboio/Autocarro
    PORTIMAO_PORTO = ZoneInfo(37.1180, -8.5290, "INDUSTRIAL_PARK")    # Cruzeiros e Carga
    
    # --- CENTROS URBANOS E COMERCIAIS (Muito Movimentados) ---
    FARO_BAIXA = ZoneInfo(37.0155, -7.9345, "DOWNTOWN")              # Comércio e Turismo
    ALBUFEIRA_OLD_TOWN = ZoneInfo(37.0870, -8.2520, "DOWNTOWN")      # Densidade pedonal extrema
    GUIA_SHOPPING = ZoneInfo(37.1250, -8.2800, "COMMERCIAL_DISTRICT") # Algarve Shopping (Trânsito)
    
    # --- RESIDENCIAL / LAZER (Mais calmos mas com picos) ---
    QUARTEIRA_CALÇADA = ZoneInfo(37.0685, -8.1010, "RESIDENTIAL_NORTH") 
    LAGOS_MARINA = ZoneInfo(37.1080, -8.6740, "RESIDENTIAL_NORTH")
    TAVIRA_CENTRO = ZoneInfo(37.1260, -7.6500, "RESIDENTIAL_NORTH")
    
    # --- EIXOS RODOVIÁRIOS (Fluxo TomTom) ---
    ROAD_VILA_REAL_A22 = ZoneInfo(37.2000, -7.4300, "INDUSTRIAL_PARK") # Fronteira com Espanha
    ROAD_A2_ALGARVE = ZoneInfo(37.2500, -8.2000, "INDUSTRIAL_PARK")    # Ligação a Lisboa

#class newRegion:
#    __zones=[]
#    def __init__(self,region):
#        self.region=region
#    
#    def createNewZone(self,name,lon,lat,typeZone):
#        self.__zones.append({name: ZoneInfo(lon,lat,typeZone)})
#
#    def getRegionsZone(self):
#        return self.__zones
        
