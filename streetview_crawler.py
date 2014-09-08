from urllib import request, parse
from os import path
from sys import argv
from hashlib import md5
from time import sleep
from capstone import settings
import simplejson as json

URL = "http://maps.googleapis.com/maps/api/streetview?%s"
OUTPUT_DIR = "C:\/Users\/shamil\/Desktop\/capstone\/crawler"
FORMAT = ".jpg"
DEFAULTS = {'size': '800x600', 'fov': 80, 'key': settings.GOOGLE_API_KEY, 'userIP': settings.USER_IP}
# Seconds to sleep between api call
DELAY = 0.5

# Image positions per coordinate. Format: (heading, pitch)
IMG_POSITIONS = ((0, 0), (45, 0), (90, 0), (135, 0), (180, 0), (225, 0), (270, 0), (315, 0), (0, 40), (90, 40), (180, 40), (270, 40))
IDENTITY_POSITION = (0, 0)

def snap(lat, lng, heading, pitch, **kwargs):
  params = DEFAULTS.copy()
  params.update({'location': "%s,%s"%(lat, lng), 'heading': heading, 'pitch': pitch})
  params.update(kwargs)
  encoded = parse.urlencode(params)
  try:
    return request.urlopen(URL % encoded).read()
  except Exception as e:
    print(URL % encoded)
    raise e
  

def fetch_images(streetname, coordinate_id, lat, lng):
  for heading, pitch in IMG_POSITIONS:
    name = "%s_%s_%i_%i"%(streetname, coordinate_id, heading, pitch)
    img = snap(lat, lng, heading, pitch)
    save_image(img, name)
    sleep(DELAY)
 
 
def save_image(img, name):
  name = name + FORMAT
  print("Saving image: ", name)
  with open(path.join(OUTPUT_DIR, name), 'wb') as file:
    file.write(img)
  
  

def main():
  street_name = argv[1]
  coordinates_file = argv[2]
  
  if not street_name or not coordinates_file:
    print("Usage: python streetview_crawler.py <street name> <coordinates file>")
    return
  
  with open(coordinates_file, 'r') as file:
    coordinates = [ (lat, lng) for lat, lng in json.loads(file.read()) ]
  
  print("Coordinates count: ", len(coordinates))
  
  img_ident_hash = {}
  id_counter = 1
  
  for lat, lng in coordinates:
    img = snap(lat, lng, IDENTITY_POSITION[0], IDENTITY_POSITION[1])
    _hash = md5(img).hexdigest()
    if _hash not in img_ident_hash:
      print(lat, lng)
      img_ident_hash[_hash] = ''
      fetch_images(street_name, id_counter, lat, lng)
      id_counter += 1
    else:
      print("duplicate")
  
    
    
if __name__ == '__main__':
  main()