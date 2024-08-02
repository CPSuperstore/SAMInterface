import math
import typing

import PIL.Image
import PIL.ImageDraw
import matplotlib.pyplot as plt
import numpy as np
import shapely
import shapely.affinity
import svgwrite
import svgwrite.shapes
import tqdm

import vector_node.base_node as base_node

POLYGON_TYPE = typing.Union[np.ndarray, 'vector_node', shapely.Polygon]


class VectorNode(base_node.BaseNode):
    def __init__(
            self, exterior: np.ndarray, category: int = None, color: np.ndarray = None, level: int = 0
    ):
        super().__init__(level)
        if isinstance(exterior, list):
            exterior = np.array(exterior)

        self.exterior = exterior
        self.category = category
        self.color = color
        self.synthetic: bool = False

    @classmethod
    def from_rectangle(cls, size: tuple, category: int = None, color: np.ndarray = None) -> 'VectorNode':
        size = size[::-1]
        return cls([(0, 0), (size[0], 0), (size[0], size[1]), (0, size[1])], category, color)

    def get_children_by_category(self) -> dict:
        result = {}

        for child in self.children:
            if child.category not in result:
                result[child.category] = []

            result[child.category].append(child)

        return result

    def as_shapely(self) -> shapely.Polygon:
        return shapely.Polygon(self.exterior)

    def from_shapely(self, polygon: shapely.Polygon):
        self.exterior = np.array(polygon.exterior.coords).astype(float)

    def get_centroid(self, yx: bool = False) -> np.ndarray:
        centroid = np.array(self.as_shapely().centroid.coords)[0]

        if yx:
            centroid = centroid[::-1]

        return centroid

    def set_centroid(self, centroid: np.ndarray):
        self.move_centroid(centroid - self.get_centroid())

    def move_centroid(self, delta: np.ndarray):
        self.exterior = self.exterior.astype(float) + delta

        for child in self.children:
            child.move_centroid(delta)

    def get_polygon_coordinate_pairs(self, yx: bool = False, normalized: bool = False) -> np.ndarray:
        coords = self.exterior.copy()

        if normalized:
            coords = self.exterior - self.get_centroid()

        if yx:
            coords = np.flip(coords, axis=1)

        return coords

    def get_polygon_split_coordinates(self, yx: bool = False, normalized: bool = False) -> np.ndarray:
        coords = self.get_polygon_coordinate_pairs(yx, normalized)
        return np.array([coords[:, 0], coords[:, 1]])

    def draw(self, color: np.ndarray = None, fill: bool = True):
        if color is None:
            color = self.color

        if fill:
            plt.fill(*self.get_polygon_split_coordinates(yx=True), c=color)

        else:
            plt.plot(*self.get_polygon_split_coordinates(yx=True), c=color)

    def draw_centroids(self, surface_only: bool = False, include_self: bool = True, color: np.ndarray = None):
        generator = [self] + self.children if surface_only else self.level_order_traversal()
        for child in generator:
            if include_self:
                plt.scatter(*child.get_centroid(yx=True), s=1, color=color)

            elif child != self:
                plt.scatter(*child.get_centroid(yx=True), s=1, color=color)

    def draw_pyramid(
            self, surface_only: bool = False, include_self: bool = True
    ):
        generator = [self] + self.children if surface_only else self.level_order_traversal()
        for child in generator:
            if include_self:
                child.draw()

            elif child != self:
                child.draw()

    def draw_categorical_children(self):
        categories = self.get_unique_child_categories()
        colors = np.random.random((len(categories), 3))

        for child in self.children:
            category_index = np.where(categories == child.category)[0][0]
            child.draw(color=colors[category_index])

    def get_unique_child_categories(self):
        return np.unique([c.category for c in self.children])

    def get_area(self) -> float:
        return self.as_shapely().area

    def get_perimeter(self) -> float:
        return self.as_shapely().length

    def get_polsby_popper_compactness(self) -> float:
        return 4 * math.pi * (self.get_area() / self.get_perimeter() ** 2)

    def get_schwartzberg_compactness(self) -> float:
        return 1 / (self.get_perimeter() / (2 * math.pi * math.sqrt(self.get_area() / math.pi)))

    def get_length_width_ratio(self) -> float:
        return self.get_bounding_width() / self.get_bounding_height()

    def get_reock_score(self) -> float:
        return self.as_shapely().area / self.get_bounding_circle_area()

    def get_convex_hull_score(self) -> float:
        return self.as_shapely().area / self.get_convex_hull().area

    def get_elongation(self) -> float:
        """
        Defined in "Appearance-guided Synthesis of Element Arrangements by Example"
        Hurtut et al., 2009
        :return:
        """
        area = self.get_area()
        perimeter = self.get_perimeter()

        return min(area, perimeter) / max(area, perimeter)

    def get_convex_hull(self) -> shapely.Polygon:
        return self.as_shapely().convex_hull

    def get_bounding_box(self) -> np.ndarray:
        min_x, min_y, max_x, max_y = self.as_shapely().bounds

        return np.array([
            (min_x, min_y),
            (min_x, max_y),
            (max_x, max_y),
            (max_x, min_y),
        ])

    def get_bounding_width(self) -> float:
        min_x, min_y, max_x, max_y = self.as_shapely().bounds
        return max_x - min_x

    def get_bounding_height(self) -> float:
        min_x, min_y, max_x, max_y = self.as_shapely().bounds
        return max_y - min_y

    def distance_to_point(self, point: np.ndarray) -> float:
        return np.linalg.norm(point - self.get_centroid())

    @staticmethod
    def _convert_to_shapely(polygon) -> shapely.Polygon:
        if isinstance(polygon, VectorNode):
            polygon = polygon.as_shapely()

        elif not isinstance(polygon, shapely.Polygon):
            polygon = shapely.Polygon(polygon)

        return polygon

    def get_bounding_circle(self) -> shapely.Polygon:
        return shapely.minimum_bounding_circle(self.as_shapely())

    def get_bounding_circle_radius(self) -> float:
        return shapely.minimum_bounding_radius(self.as_shapely())

    def get_bounding_circle_area(self) -> float:
        return math.pi * self.get_bounding_circle_radius() ** 2

    def distance_to_polygon(self, polygon: POLYGON_TYPE) -> float:
        polygon = self._convert_to_shapely(polygon)
        return self.distance_to_point(np.array(polygon.centroid.coords)[0])

    def angle_to_point(self, point: np.ndarray) -> float:
        return math.atan2(*(point - self.get_centroid())[::-1])

    def angle_to_polygon(self, polygon: POLYGON_TYPE) -> float:
        polygon = self._convert_to_shapely(polygon)
        return self.angle_to_point(np.array(polygon.centroid.coords)[0])

    def get_overlap_percent(self, polygon: POLYGON_TYPE) -> float:
        polygon = self._convert_to_shapely(polygon)
        self_polygon = self.as_shapely()

        return polygon.intersection(self_polygon).area / min(polygon.area, self_polygon.area)

    def is_fully_contained(self, polygon: POLYGON_TYPE) -> bool:
        polygon = self._convert_to_shapely(polygon)
        self_polygon = self.as_shapely()

        return polygon.intersection(self_polygon).area == polygon.area

    def is_touching(self, polygon: POLYGON_TYPE, border_touching: bool = True) -> bool:
        polygon = self._convert_to_shapely(polygon)
        self_polygon = self.as_shapely()

        if border_touching:
            return polygon.intersects(self_polygon)

        return polygon.intersection(self_polygon).area > 0

    def contains_point(self, point) -> bool:
        return self.as_shapely().contains(shapely.Point(point))

    def refit_to_parent(self, recursive: bool = True):
        s = self.as_shapely()

        for child in self.children[:]:
            try:
                polygon = s.intersection(child.as_shapely())
            except shapely.GEOSException:
                polygon = s.buffer(0).intersection(child.as_shapely().buffer(0))

            if isinstance(
                    polygon, (shapely.LineString, shapely.Point, shapely.MultiPoint, shapely.MultiLineString)
            ) or polygon.is_empty:

                self.children.remove(child)

            elif isinstance(polygon, (shapely.MultiPolygon, shapely.GeometryCollection)):
                self.children.remove(child)

                for p in polygon.geoms:
                    if isinstance(p, shapely.Polygon):
                        node = child.copy()
                        node.from_shapely(p)
                        self.add_child(node)

                        if recursive:
                            node.refit_to_parent()

            else:
                child.from_shapely(polygon)

                if recursive:
                    child.refit_to_parent()

    def to_svg(self, filename: str):
        dwg = svgwrite.Drawing(filename, profile='tiny', size=(self.get_bounding_height(), self.get_bounding_width()))

        for node in self.level_order_traversal():
            dwg.add(
                svgwrite.shapes.Polygon(
                    node.get_polygon_coordinate_pairs(yx=True).tolist(),
                    fill=svgwrite.rgb(*node.color * 100, '%')
                )
            )

        dwg.save()

    def color_to_int(self, scale: float = 255) -> np.ndarray:
        return (self.color * scale).astype(int)

    def to_raster(self, filename: str):
        surface = PIL.Image.new(
            "RGB", (int(self.get_bounding_height()), int(self.get_bounding_width())),
            color=tuple([0, 0, 0] if self.color is None else self.color_to_int())
        )

        draw = PIL.ImageDraw.Draw(surface)

        for child in self.level_order_traversal(include_self=False):
            draw.polygon(
                [tuple(c) for c in child.get_polygon_coordinate_pairs(yx=True).astype(int)],
                fill=tuple(child.color_to_int())
            )

        surface.save(filename)

    def rotate(self, angle: float):
        centroid = tuple(self.get_centroid())

        for child in self.level_order_traversal():
            rotated = shapely.affinity.rotate(child.as_shapely(), angle, centroid, use_radians=True)
            child.from_shapely(rotated)

    def scale(self, x_scale: float = 1, y_scale: float = 1):
        centroid = tuple(self.get_centroid())

        for child in self.level_order_traversal():
            scaled = shapely.affinity.scale(child.as_shapely(), x_scale, y_scale, origin=centroid)
            child.from_shapely(scaled)

    def synthesize_children(
            self, quantity: float, top: float = 0.25,
            rotation_range: tuple = (-math.pi / 4, math.pi / 4),
            scale_range: tuple = (8/9, 9/8)
    ):
        if scale_range is None and rotation_range is None:
            return

        total_candidates = int(len(self.children) * top)

        if quantity < 1:
            quantity = len(self.children) * quantity

        quantity = int(quantity)

        areas = np.array([c.get_area() for c in self.children])
        compactness = np.array([c.get_polsby_popper_compactness() for c in self.children])

        areas -= areas.min()
        areas /= areas.max()

        compactness -= compactness.min()
        compactness /= compactness.max()

        coordinates = np.column_stack((areas, compactness))
        distances = np.linalg.norm(coordinates - [1, 1], axis=1)

        candidate_indices = np.argpartition(distances, total_candidates)[-total_candidates:]

        children = []
        for _ in tqdm.tqdm(range(quantity), total=quantity):
            parent_index = np.random.choice(candidate_indices)
            new_child = self.children[parent_index].copy()

            if scale_range is not None:
                scale_x = np.random.uniform(*scale_range)
                scale_y = np.random.uniform(*scale_range)
                new_child.scale(scale_x, scale_y)

            if rotation_range is not None:
                angle = np.random.uniform(*rotation_range)
                new_child.rotate(angle)

            new_child.synthetic = True
            self.add_child(new_child)
            children.append(new_child)

        return children

    def get_category_density(self, normalize: bool = True) -> tuple:
        categories = [c.category for c in self.children if not c.synthetic]
        unique, counts = np.unique(categories, return_counts=True)

        if normalize:
            counts = counts.astype(np.float32) / len(self.children)

        return unique, counts
