import csv
import re

# classe pra guardar as informaçoes de cada estabelecimento
class Info:
  def __init__(self, date, address, name) -> None:
    self.date = date
    self.address = address
    self.name = name

class Point:
  def __init__(self, data, x = 0.0, y = 0.0) -> None:
    self.data = data
    self.x = x
    self.y = y

  def __repr__(self):
    return f"(x = {self.x}, y = {self.y})"

class Rectangle:
  def __init__(self, p1, p2) -> None:
    self.ll = Point(None, min(p1.x, p2.x), min(p1.y, p2.y))
    self.ur = Point(None, max(p1.x, p2.x), max(p1.y, p2.y))
    self.w = abs(p2.x - p1.x)
    self.h = abs(p2.y - p1.y)

  def contains(self, p) -> bool:
    return self.ll.x <= p.x <= self.ur.x and self.ll.y <= p.y <= self.ur.y

class Node:
  def __init__(self, point, axis, left = None, right = None) -> None:
    self.point = point
    self.axis = axis
    self.left = left
    self.right = right

class KdTree:
  def __init__(self, points, depth = 0) -> None:
    self.root = self.build_tree(list(points), depth)
     
  def build_tree(self, points, depth) -> Node | None:
    if not points:
      return None

    k = 2
    axis = depth % k
     
    if axis == 0:
      points.sort(key = lambda p : p.x)
    else:
      points.sort(key = lambda p : p.y)

    median_index = len(points) // 2
    median = points[median_index]
     
    return Node(
      median,
      axis,
      left = self.build_tree(points[ : median_index], depth + 1),
      right = self.build_tree(points[median_index + 1 : ], depth + 1),
    )

  def search(self, search_area) -> list[Point]:
    in_range = []

    def search_recursive(node):
      if node is None:
        return

      if search_area.contains(node.point):
        in_range.append(node.point)

      if node.axis == 0:
        if search_area.ll.x <= node.point.x:
          search_recursive(node.left)
        if search_area.ur.x >= node.point.x:
          search_recursive(node.right)
      else:
        if search_area.ll.y <= node.point.y:
          search_recursive(node.left)
        if search_area.ur.y >= node.point.y:
          search_recursive(node.right)

    search_recursive(self.root)
    return in_range

def read_csv(path):
  with open(path, 'r') as file:
    return list(csv.reader(file, delimiter = ';'))

def parse_csv(path):
  file = read_csv(path)

  columns = file[0]
  rows = file[1 : ]

  idx_cnae = columns.index('CNAE_PRINCIPAL')
  idx_desc = columns.index('DESCRICAO_CNAE_PRINCIPAL')

  descs = set()

  for row in rows:
    if len(row) > max(idx_cnae, idx_desc):
      descs.add(row[idx_desc].strip())

  descs = sorted(descs)

  keywords = re.compile(r'\b(RESTAURANTE|RESTAURANTES|BAR|BARES|BEBIDA|BEBIDAS)\b', re.IGNORECASE)

  filtered_desc = [desc for desc in descs if keywords.search(desc)]
  filtered_desc = [filtered_desc[0], filtered_desc[1], filtered_desc[11]]

  filtered_rows = [row for row in rows if row[idx_desc] in filtered_desc]
  
  points = []

  for row in filtered_rows:
    match = re.search(r'\((.*?)\)', row[-1])
    coords = match.group(1)
    point = coords.split(' ')
    x, y = float(point[0]), float(point[1])
    points.append(Point(row[ : -1], x, y))

  return points
    
def main():
  points = parse_csv('dados.csv')
  tree = KdTree(points)

  center_x, center_y = 604468, 7792708
  delta = 250  # search within ±50 meters

  p1 = Point(None, center_x - delta, center_y - delta)
  p2 = Point(None, center_x + delta, center_y + delta)
  area = Rectangle(p1, p2)
  print(tree.search(area))

if __name__ == "__main__":
    main()
