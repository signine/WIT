from hashlib import md5
from time import sleep
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import os, sys
import simplejson as json
import urllib2, urllib

sys.path.append(os.path.dirname(__file__))
import settings

DB_URL = "mysql://root@localhost:3306/WIT"
URL = "http://maps.googleapis.com/maps/api/streetview?%s"
FORMAT = ".jpg"
DEFAULTS = {'size': '800x600', 'fov': 80, 'key': settings.GOOGLE_API_KEY, 'userIP': settings.USER_IP}
# Seconds to sleep between api call
DELAY = 0.5

# Image positions per coordinate. Format: (heading, pitch)
IMG_POSITIONS = ((0, 0), (45, 0), (90, 0), (135, 0), (180, 0), (225, 0), (270, 0), (315, 0))
IDENTITY_POSITION = (0, 0)

INSERT_SQL = text("INSERT INTO images (lat, lng, street_name, step_id, heading, pitch) VALUES (:lat, :lng, :street_name, :step_id, :heading, :pitch);")

output_dir = ''
db = None 

def snap(lat, lng, heading, pitch, **kwargs):
  params = DEFAULTS.copy()
  params.update({'location': "%s,%s"%(lat, lng), 'heading': heading, 'pitch': pitch})
  params.update(kwargs)
  encoded = urllib.urlencode(params)
  try:
    return urllib2.urlopen(URL % encoded).read()
  except Exception as e:
    print(URL % encoded)
    raise e
  

def fetch_images(street_name, step_id, lat, lng):
  for heading, pitch in IMG_POSITIONS:
    img = snap(lat, lng, heading, pitch)
    save_image(img, lat, lng, street_name, step_id, heading, pitch)
    sleep(DELAY)

def get_db_connection():
  global db
  db = create_engine(DB_URL)
 
def save_image(img, lat, lng, street_name, step_id, heading, pitch):
  if not db:
    get_db_connection()

  result = db.execute(INSERT_SQL, lat=lat, lng=lng, street_name=street_name, step_id=step_id, heading=heading, pitch=pitch)

  name = "%i_%s_%s_%i_%i%s"%(result.lastrowid, street_name, step_id, heading, pitch, FORMAT)
  print("Saving image: ", name)
  with open(os.path.join(output_dir, name), 'wb') as file:
    file.write(img)
  

def main():
  global output_dir
  street_name = sys.argv[1]
  coordinates_file = sys.argv[2]
  output_dir = sys.argv[3]
  
  if not street_name or not coordinates_file or not output_dir:
    print("Usage: python streetview_crawler.py <street name> <coordinates file> <output dir>")
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
