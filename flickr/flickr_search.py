from time import time
import flickr as flkr
import simplejson as json
import sys

STORAGE_DIR = "flickr_photos/"
# Min 250 per page. Should be multiple of 250.
OBJS_PER_FILE = 1000
DELIMITER = "\n"

PAGES = { 'start': int(sys.argv[1]), 'finish': int(sys.argv[2]) }

API = flkr.Photo()

# Not meant to be thread-safe
class Processor:
  def __init__(self):
    self.obj_count = 0
    self.file = None

  def write_to_file(self, data):
    data = json.dumps(data)
    file = self.get_file()
    file.write(data + DELIMITER)
    self.obj_count += 1
    
  def get_file(self):
    if not self.file:
      self.set_new_file()
    elif self.obj_count == OBJS_PER_FILE:
      self.close_file()
      self.set_new_file()
    return self.file
  
  def close_file(self):
    self.file.flush()
    self.file.close()
    
  def set_new_file(self):
    filename = "%s/%s.txt" % (STORAGE_DIR, str(self.current_page))
    print("Opening file: " + filename)
    self.file = open(filename, 'w')
    self.obj_count = 0
  
  def set_current_page(self, page_id):
    self.current_page = page_id
    
  def ingest(self, data):
    start = time()
    self.set_current_page(data['photos']['page'])
    print(self.current_page)
    
    for p in data['photos']['photo']:
      try:
        info = API.get_info({'photo_id' : p['id']})
      except Exception as e:
        print("ERROR retrieving photo", p)
        print(e)
        continue
      new_photo = [p['id'], p['owner'], info['photo']['location']['latitude'], info['photo']['location']['longitude']]
      self.write_to_file(new_photo)
    
    finish = time()
    print("Time: ", finish - start)
    
    
def main():
  params = { 'bbox' : '-79.396590,43.634020,-79.361485,43.675503', 'page' : PAGES['start'] }
  data = API.search(params)
  
  pages = data['photos']['pages']
  print("Total pages: ", pages)
  
  processor = Processor()
  processor.ingest(data)
  for p in range(PAGES['start'] + 1, PAGES['finish'] + 1):
    params.update({ 'page' : p })
    try:
      data = API.search(params)
      processor.ingest(data)
    except Exception as e:
      print("ERROR retrieving page: ", p)
      print(e)
      continue
  processor.close_file()
    
  
    
if __name__ == '__main__':
  main()
  
