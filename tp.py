import csv

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
    self.root, self.len = self.build_tree(list(points), depth)

  def __len__(self) -> int:
    return self.len
     
  def build_tree(self, points, depth) -> tuple[Node | None, int]:
    if not points:
      return None, 0

    k = 2
    axis = depth % k
     
    if axis == 0:
      points.sort(key = lambda p : p.x)

    else:
      points.sort(key = lambda p : p.y)

    median_index = len(points) // 2
    median = points[median_index]

    left_node, left_len = self.build_tree(points[ : median_index], depth + 1)
    right_node, right_len = self.build_tree(points[median_index + 1 : ], depth + 1)
     
    node = Node(
      median,
      axis,
      left = left_node,
      right = right_node,
    )

    return node, left_len + right_len + 1

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

  points = []

  for row in rows:
    match = re.search(r'\((.*?)\)', row[-1])
    coords = match.group(1)
    point = coords.split(' ')
    x, y = float(point[0]), float(point[1])
    points.append(Point(row[ : -1], x, y))

  return points
    
def main():
  points = parse_csv('dados.csv')
  tree = KdTree(points)

  # teste
  center_x, center_y = 604468.0, 7792708.0
  delta = 250 

  p1 = Point(None, center_x - delta, center_y - delta)
  p2 = Point(None, center_x + delta, center_y + delta)
  area = Rectangle(p1, p2)
  print(tree.search(area))
  print(len(tree))

if __name__ == "__main__":
    main()
