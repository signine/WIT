from geopy.distance import vincenty
from location_match import LocationMatch

DISTANCE_LIMIT = 20

def group_by_location(matches):
  locations = []
  
  while len(matches) > 0:
    loc = matches.pop()
    loc_group = [loc]
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

def score_img_match(img_match, total_features):
  return 100 * ((img_match.count * 1.0) / total_features)


def score(matches):
  total_features = 0
  for m in matches: total_features += m.count

  locations = group_by_location(matches)
  location_scores = []

  for l in locations:
    loc = LocationMatch(l[0].location)
    for img in l:
      loc.imgs.append(img)
      loc.score += score_img_match(img, total_features)
    location_scores.append(loc)

  location_scores = sorted(location_scores, key=lambda x: x.score)
  return location_scores

