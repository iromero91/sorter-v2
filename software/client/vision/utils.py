import cv2
import numpy as np


def masksOverlap(mask1: np.ndarray, mask2: np.ndarray) -> bool:
    overlap = np.logical_and(mask1, mask2)
    return bool(np.any(overlap))


def masksWithinDistance(
    mask1: np.ndarray, mask2: np.ndarray, threshold_px: int
) -> bool:
    kernel = np.ones((threshold_px * 2 + 1, threshold_px * 2 + 1), np.uint8)
    dilated = cv2.dilate(mask2.astype(np.uint8), kernel, iterations=1)
    return masksOverlap(mask1, dilated.astype(bool))


def maskEdgeProximity(
    object_mask: np.ndarray, target_mask: np.ndarray, proximity_px: int = 3
) -> float:
    mask_uint8 = object_mask.astype(np.uint8)
    eroded = cv2.erode(mask_uint8, np.ones((3, 3), np.uint8), iterations=1)
    edge = mask_uint8 - eroded

    # dilate target to create "near target" zone
    kernel = np.ones((proximity_px * 2 + 1, proximity_px * 2 + 1), np.uint8)
    dilated_target = cv2.dilate(target_mask.astype(np.uint8), kernel, iterations=1)

    # what percentage of object edge is near the target
    edge_near_target = np.logical_and(edge, dilated_target)
    edge_pixels = np.sum(edge)
    if edge_pixels == 0:
        return 0.0
    return float(np.sum(edge_near_target) / edge_pixels)
