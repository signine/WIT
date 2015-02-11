class ImgMatch():
  def __init__(self, img_data, features):
    self.img_data = img_data
    self.location = (img_data[1], img_data[2])
    self.img_id = img_data[0]
    self.street = img_data[3]
    self.weight = img_data[8]
    self.count = features  # Number of features that matched this img

  def __str__(self):
    print self.img_data, self.count
