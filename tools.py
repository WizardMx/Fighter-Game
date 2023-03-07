def is_box_intersect(RecA, RecB):

    # 获取交集区域的[xmin,ymin,xmax,ymax]
    x_A_and_B_min = max(RecA[0], RecB[0])
    y_A_and_B_min = max(RecA[1], RecB[1])
    x_A_and_B_max = min(RecA[2], RecB[2])
    y_A_and_B_max = min(RecA[3], RecB[3])
    # 计算交集部分面积, 当(xmax - xmin)为负时，说明A与B框无交集，直接置为0。 (ymax - ymin)同理。
    interArea = max(0, x_A_and_B_max - x_A_and_B_min) * max(0, y_A_and_B_max - y_A_and_B_min)
    # 计算A和B的面积
    RecA_Area = (RecA[2] - RecA[0]) * (RecA[3] - RecA[1])  # (xmax - xmin) * (ymax - ymin)
    RecB_Area = (RecB[2] - RecB[0]) * (RecB[3] - RecB[1])  # (xmax - xmin) * (ymax - ymin)
    # 计算IOU
    iou = interArea / (RecA_Area + RecB_Area - interArea)
    return iou > 0

def get_box(centre, size0):
    size = size0[1], size0[0]
    return [centre[0] - size[0] // 2, centre[1], centre[0] + size[0] // 2, centre[1] + size[1]]

