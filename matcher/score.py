from geopy.distance import vincenty

DISTANCE_LIMIT = 20

def group_by_location(matches):
  locations = []
  
  while len(matches) > 0:
    loc = matches.pop()
    loc_group = [loc]
    print loc.location
    i = 0
    while i < len(matches):
      m = matches[i]
      dis = vincenty(loc.location, m.location)
      if dis.meters <= DISTANCE_LIMIT:
        loc_group.append(m)
        matches.remove(m)
      else:
        i += 1
    locations.append(loc_group)

  return locations    
