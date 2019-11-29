# -*- coding:utf-8 -*-
import numpy as np

class TextConnector(object):

    def __init__(self):
        self.MIN_SIZE_SIM = 0.6
        self.MIN_V_OVERLAPS = 0.6

    def __get_successions(self, index):
            box=self.textLocs[index]
            results=[]
            for left in range(int(box[0]) + 1, min(int(box[0]) + self.MAX_HORIZONTAL_GAP + 1, self.im_size[0])):
                adj_box_indices = self.boxes_table[left]
                for adj_box_index in adj_box_indices:
                    if self.__meet_v_iou(adj_box_index, index):
                        results.append(adj_box_index)
                if len(results) != 0:
                    return results
            return results

    def __get_precursors(self, index):
        box=self.textLocs[index]
        results=[]
        for left in range(int(box[0]) - 1, max(int(box[0] - self.MAX_HORIZONTAL_GAP), 0) -1, -1):
            adj_box_indices = self.boxes_table[left]
            for adj_box_index in adj_box_indices:
                if self.__meet_v_iou(adj_box_index, index):
                    results.append(adj_box_index)
            if len(results)!=0:
                return results
        return results

    def __meet_v_iou(self, index1, index2):
        def overlaps_v(index1, index2):
            h1=self.textLocs[index1][3]
            h2=self.textLocs[index2][3]
            y0=max(self.textLocs[index2][1], self.textLocs[index1][1])
            y1=min(self.textLocs[index2][1] + h2, self.textLocs[index1][1] + h1)
            return max(0, y1 - y0 + 1) / min(h1, h2)

        def size_similarity(index1, index2):
            h1=self.textLocs[index1][3]
            h2=self.textLocs[index2][3]
            return min(h1, h2) / max(h1, h2)

        return overlaps_v(index1, index2) >= self.MIN_V_OVERLAPS and \
               size_similarity(index1, index2) >= self.MIN_SIZE_SIM

    def connect_text(self, textBoxes, im_size, MAX_HORIZONTAL_GAP=60):
        self.MAX_HORIZONTAL_GAP = MAX_HORIZONTAL_GAP
        # Box layout should be [[x, y, width, height], ...]
        self.textBoxes = textBoxes
        self.textLocs = np.array(np.array(self.textBoxes)[:, 0:4], dtype=int)

        # Image size (width, height)
        self.im_size = im_size

        # Build a box table by X axis
        boxes_table = [[] for _ in range(self.im_size[0])]
        for index, box in enumerate(self.textLocs):
            boxes_table[int(box[0])].append(index)
        self.boxes_table = boxes_table

        graph = np.zeros((len(self.textLocs), len(self.textLocs)), np.bool)

        for index, box in enumerate(self.textLocs):
            successions = self.__get_successions(index)
            # print(index, successions)

            if len(successions) == 0:
                continue

            succession_index = np.max(successions)
            graph[index, succession_index] = True

        # for index, box in enumerate(self.textLocs):
        #     precursors = self.__get_precursors(index)
        #     print(index, precursors)
        #
        #     if len(precursors) == 0:
        #         continue
        #
        #     precursor_index = np.min(precursors)
        #     graph[precursor_index, index] = True

        tp_groups=[]
        tp_indices = []
        for index in range(graph.shape[0]):
            if not graph[:, index].any() and graph[index, :].any():
                v=index
                tp_groups.append([v])
                tp_indices.append(v)
                while graph[v, :].any():
                    v=np.where(graph[v, :])[0][0]
                    tp_groups[-1].append(v)
                    tp_indices.append(v)

        # Output the connected boxes
        newBoxes = []
        for index, box in enumerate(self.textBoxes):
            if index in tp_indices:
                continue
            else:
                newBoxes.append(box)

        for index, tp_indices in enumerate(tp_groups):
            text_line_boxes=self.textLocs[list(tp_indices)]
            text_values = np.array(self.textBoxes)[list(tp_indices)][:, 4]

            x0 = np.min(text_line_boxes[:, 0])
            x1 = np.max(text_line_boxes[:, 0] + text_line_boxes[:, 2])
            y0 = np.min(text_line_boxes[:, 1])
            y1 = np.max(text_line_boxes[:, 1] + text_line_boxes[:, 3])

            newBoxes.append([x0, y0, x1 - x0, y1 - y0, ' '.join(text_values.tolist())])

        return newBoxes


if __name__ == '__main__':
    text_box = [[0, 3, 316, 31, "abc"], [0, 50, 136, 28, "112114255"], [116, 99, 79, 27, "1970"], [12, 100, 110, 27, "18MAR"], [20, 143, 169, 27, "22JUL2015"]]

    textConnect = TextConnector()
    new_box = textConnect.connect_text(text_box, (200, 200))
    print(new_box)
