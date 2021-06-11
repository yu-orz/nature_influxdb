from datetime import datetime,timedelta,timezone
import json
import requests
import influxdb
import time
import settings

headers = {
  'accept': 'application/json',
  'Authorization': 'Bearer ' + settings.nature_api_token,
}

while True: 

  response = requests.get("https://api.nature.global/1/appliances", headers=headers)
  data = response.json()

  Value = {}

  for appliance in data:
    if appliance['type'] == 'EL_SMART_METER':
      for meterValue in appliance['smart_meter']['echonetlite_properties']:
        if meterValue['name'] == 'normal_direction_cumulative_electric_energy':
            Value['CumulativeEnergy'] = float(meterValue['val'])/100
        elif meterValue['name'] == 'measured_instantaneous':
            Value['Watt'] = int(meterValue['val'])

  client = influxdb.InfluxDBClient(host=settings.influx_db_host,database=settings.influx_db_name)
  datestr = datetime.now(timezone(timedelta(hours=+0), 'UTC')).strftime('%Y-%m-%dT%H:%M:%SZ')
  points = [
    {
      "measurement": settings.influx_db_measurement,
      "time": datestr,
      "fields": {
        "Watt": float(Value['Watt']), 
        "CumulativeEnergy": float(Value['CumulativeEnergy'])
        }
      }
    ]
  #print(points)
  client.write_points(points)

  time.sleep(15)
