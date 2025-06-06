import csv
import numpy as np
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
    self.point = np.array([x, y], dtype = np.float64)

  @property
  def x(self) -> float:
    return self.point[0]
  
  @property
  def y(self) -> float:
    return self.point[1]

  def __repr__(self) -> str:
    return f"(x = {self.x:.2f}, y = {self.y:.2f})"

class Rectangle:
  def __init__(self, p1, p2) -> None:
    self.ll = np.array([min(p1.x, p2.x), min(p1.y, p2.y)], dtype = np.float64)
    self.ur = np.array([max(p1.x, p2.x), max(p1.y, p2.y)], dtype = np.float64)

  def contains(self, p) -> bool:
    return self.ll[0] <= p.x <= self.ur[0] and self.ll[1] <= p.y <= self.ur[1]

  def intersect_axis(self, p, axis) -> tuple[bool, bool]:
    return self.ll[axis] <= p, self.ur[axis] >= p

class Node:
  def __init__(self, point, axis, left = None, right = None) -> None:
    self.point = point
    self.axis = axis
    self.left = left
    self.right = right
    self.split = point.point[axis]

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
     
    coords = np.array([p.point[axis] for p in points])
    median_idx = len(points) // 2

    partition_idxs = np.argpartition(coords, median_idx)
    points = [points[i] for i in partition_idxs]
    median = points[median_idx]

    left_node, left_len = self.build_tree(points[ : median_idx], depth + 1)
    right_node, right_len = self.build_tree(points[median_idx + 1 : ], depth + 1)
    node = Node(median, axis, left = left_node, right = right_node)

    return node, left_len + right_len + 1

  def search(self, search_area) -> list[Point]:
    in_range = []

    def search_recursive(node) -> None:
      if node is None:
        return

      if search_area.contains(node.point):
        in_range.append(node.point)

      left_intersect, right_intersect = search_area.intersect_axis(node.split, node.axis)

      if left_intersect:
        search_recursive(node.left)

      if right_intersect:
        search_recursive(node.right)

    search_recursive(self.root)
    return in_range

def read_csv(path) -> list[list[str]]:
  with open(path, 'r') as file:
    return list(csv.reader(file, delimiter = ';'))

def parse_csv(path) -> list[Point]:
  file = read_csv(path)
  
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
  points = np.array(parse_csv('dados.csv'))
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
