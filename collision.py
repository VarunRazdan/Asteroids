"""Collision detection: SAT for triangle-vs-circle, circle-vs-circle for everything else."""
import pygame


def sat_triangle_circle(triangle_points, circle_pos, circle_radius):
    """Separating Axis Theorem: test if a triangle collides with a circle.

    Args:
        triangle_points: list of 3 pygame.Vector2 (world-space vertices)
        circle_pos: pygame.Vector2 center of circle
        circle_radius: float radius

    Returns:
        True if the shapes overlap.
    """
    # Axes to test: 3 edge normals + 1 axis from nearest vertex to circle center
    axes = []

    # Edge normals
    for i in range(3):
        edge = triangle_points[(i + 1) % 3] - triangle_points[i]
        # Perpendicular (normal)
        normal = pygame.Vector2(-edge.y, edge.x)
        if normal.length_squared() > 0:
            normal.normalize_ip()
            axes.append(normal)

    # Axis from circle center to nearest triangle vertex
    nearest_dist_sq = float('inf')
    nearest_vertex = triangle_points[0]
    for v in triangle_points:
        d = (v - circle_pos).length_squared()
        if d < nearest_dist_sq:
            nearest_dist_sq = d
            nearest_vertex = v

    axis_to_nearest = nearest_vertex - circle_pos
    if axis_to_nearest.length_squared() > 0:
        axis_to_nearest.normalize_ip()
        axes.append(axis_to_nearest)

    # Test each axis for separation
    for axis in axes:
        # Project triangle
        tri_min = float('inf')
        tri_max = float('-inf')
        for v in triangle_points:
            proj = v.dot(axis)
            tri_min = min(tri_min, proj)
            tri_max = max(tri_max, proj)

        # Project circle
        center_proj = circle_pos.dot(axis)
        circle_min = center_proj - circle_radius
        circle_max = center_proj + circle_radius

        # Check for gap
        if tri_max < circle_min or circle_max < tri_min:
            return False  # Separating axis found — no collision

    return True  # No separating axis — collision!


def circles_collide(pos1, radius1, pos2, radius2):
    """Fast circle-vs-circle collision check."""
    dx = pos1.x - pos2.x
    dy = pos1.y - pos2.y
    dist_sq = dx * dx + dy * dy
    radii_sum = radius1 + radius2
    return dist_sq < radii_sum * radii_sum
