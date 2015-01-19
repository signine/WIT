CREATE TABLE kmeans_tree (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  parent_id INT,
  descriptor TEXT,
  children VARCHAR(1000),
  images VARCHAR(500)
) ENGINE = InnoDB;
