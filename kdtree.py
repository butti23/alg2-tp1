import csv
import re
from typing import List, Optional, Dict, Any
import numpy as np
from pyproj import Transformer

transformer = Transformer.from_crs('EPSG:32723', 'EPSG:4326', always_xy=True)

class Info:
    def __init__(
        self,
        date: str,
        address: str,
        name: str,
        ficname: Optional[str],
        has_license: Optional[bool],
        id_ativ_econ_estabelecimento: Optional[str] = None
    ):
        self.date = date
        self.address = address
        self.name = name
        self.ficname = ficname
        self.has_license = has_license
        self.id_ativ_econ_estabelecimento = id_ativ_econ_estabelecimento

class Point:
    def __init__(self, data: Any, x: float = 0.0, y: float = 0.0):
        self.data = data
        self.point = np.array([x, y], dtype=np.float64)

    @property
    def x(self) -> float:
        return self.point[0]

    @property
    def y(self) -> float:
        return self.point[1]

    def __repr__(self) -> str:
        return f'(x = {self.x:.2f}, y = {self.y:.2f})'

class Rectangle:
    def __init__(self, p1: Point, p2: Point):
        self.ll = np.array([min(p1.x, p2.x), min(p1.y, p2.y)], dtype=np.float64)
        self.ur = np.array([max(p1.x, p2.x), max(p1.y, p2.y)], dtype=np.float64)

    def contains(self, p: Point) -> bool:
        return self.ll[0] <= p.x <= self.ur[0] and self.ll[1] <= p.y <= self.ur[1]

    def intersect_axis(self, value: float, axis: int):
        return self.ll[axis] <= value, self.ur[axis] >= value

class Node:
    def __init__(
        self,
        point: Point,
        axis: int,
        left: Optional['Node'] = None,
        right: Optional['Node'] = None
    ):
        self.point = point
        self.axis = axis
        self.left = left
        self.right = right
        self.split = point.point[axis]

class KdTree:
    def __init__(self, points: List[Point], depth: int = 0):
        self.root, self.len = self._build_tree(points, depth)

    def __len__(self) -> int:
        return self.len

    def _build_tree(self, points: List[Point], depth: int):
        if not points:
            return None, 0

        axis = depth % 2
        coords = np.array([p.point[axis] for p in points])
        median_idx = len(points) // 2
        partition_idxs = np.argpartition(coords, median_idx)
        points = [points[i] for i in partition_idxs]
        median = points[median_idx]

        left_node, left_len = self._build_tree(points[:median_idx], depth + 1)
        right_node, right_len = self._build_tree(points[median_idx + 1:], depth + 1)
        node = Node(median, axis, left=left_node, right=right_node)

        return node, left_len + right_len + 1

    def search(self, search_area: Rectangle) -> List[Point]:
        in_range = []

        def _search_recursive(node: Optional[Node]):
            if node is None:
                return

            if search_area.contains(node.point):
                in_range.append(node.point)

            left_intersect, right_intersect = search_area.intersect_axis(node.split, node.axis)
            if left_intersect:
                _search_recursive(node.left)
            if right_intersect:
                _search_recursive(node.right)

        _search_recursive(self.root)
        return in_range

def read_csv(path: str) -> List[List[str]]:
    with open(path, 'r', encoding='UTF-8') as file:
        return list(csv.reader(file, delimiter=';'))

def parse_csv(path: str) -> List[Point]:
    file = read_csv(path)
    columns = file[0]
    rows = file[1:]

    idx = {col: columns.index(col) for col in [
        'NOME', 'NOME_FANTASIA', 'IND_POSSUI_ALVARA', 'DATA_INICIO_ATIVIDADE',
        'DESC_LOGRADOURO', 'NOME_LOGRADOURO', 'NUMERO_IMOVEL', 'COMPLEMENTO',
        'NOME_BAIRRO', 'ID_ATIV_ECON_ESTABELECIMENTO'
    ]}

    points = []
    for row in rows:
        match = re.search(r'\((.*?)\)', row[-1])
        if not match:
            continue
        coords = match.group(1).split(' ')
        x, y = transformer.transform(float(coords[0]), float(coords[1]))

        address = (
            f"{row[idx['DESC_LOGRADOURO']]} {row[idx['NOME_LOGRADOURO']]}, {row[idx['NUMERO_IMOVEL']]},"
            f"{' ' + row[idx['COMPLEMENTO']] + ',' if row[idx['COMPLEMENTO']] else ''} {row[idx['NOME_BAIRRO']]}"
        )
        ficname = row[idx['NOME_FANTASIA']] or None
        has_license = {'SIM': True, 'NÃO': False}.get(row[idx['IND_POSSUI_ALVARA']], None)
        id_ativ = row[idx['ID_ATIV_ECON_ESTABELECIMENTO']]

        info = Info(
            date=row[idx['DATA_INICIO_ATIVIDADE']],
            address=address,
            name=row[idx['NOME']],
            ficname=ficname,
            has_license=has_license,
            id_ativ_econ_estabelecimento=id_ativ
        )
        points.append(Point(info, x, y))

    return points

def parse_bares_completos_csv(path: str) -> Dict[str, Dict[str, str]]:
    bares_info = {}
    with open(path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            bares_info[row['ID']] = row
    return bares_info