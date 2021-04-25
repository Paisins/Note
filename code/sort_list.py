import random


def bubble_sort(data: list):
    flag = True
    while flag:
        flag = False
        for index in range(len(data) - 1):
            if data[index] <= data[index + 1]:
                continue
            else:
                data[index], data[index + 1] = data[index + 1], data[index]
                flag = True
    return data


def insert_sort(data: list):
    if not data:
        return list()
    new_data = [data[0]]
    for i in data[1:]:
        for index in range(len(new_data)):
            if i <= new_data[index]:
                new_data.insert(index, i)
                break
        else:
            new_data.append(i)
    return new_data


def merge_sort(data: list):
    length = len(data)
    mid = length // 2

    part_1 = data[:mid]
    part_2 = data[mid:]

    if len(part_1) > 1:
        part_1 = merge_sort(part_1)
    if len(part_2) > 1:
        part_2 = merge_sort(part_2)

    if not part_1 or not part_2:
        return part_1 + part_2

    part = list()
    i = j = 0
    part_1_len = len(part_1)
    part_2_len = len(part_2)
    while i < part_1_len and j < part_2_len:
        if part_1[i] < part_2[j]:
            part.append(part_1[i])
            i += 1
        else:
            part.append(part_2[j])
            j += 1
    part += part_1[i:] + part_2[j:]
    return part


def quick_sort(data: list):
    if not data:
        return data

    random_one = random.choice(data)
    part_1 = [i for i in data if i < random_one]
    part_2 = [i for i in data if i >= random_one]

    # 因为是根据大小切分，所以要保证至少有两个不一样大小的数字
    if len(set(part_1)) > 1:
        part_1 = quick_sort(part_1)
    if len(set(part_2)) > 1:
        part_2 = quick_sort(part_2)

    return part_1 + part_2


def shell_sort(data: list):
    n = len(data)
    gap = int(n/2)

    while gap > 0:
        for i in range(gap,n):
            value = data[i]
            index = i
            while index >= gap and data[index-gap] > value:
                data[index] = data[index-gap]
                index -= gap
            data[index] = value
        gap = int(gap/2)
        print(data)
    return data


def select_sort(data: list):
    length = len(data)
    i = 0
    while i < length:
        min_index = i
        for j in range(i, length):
            if data[j] < data[min_index]:
                min_index = j
        data[i], data[min_index] = data[min_index], data[i]
        i += 1
    return data


def main():
    example = [1, 3, 2, 0, 9, 5, 4, 7, 8, 6, 4]
    # 冒泡排序
    # print(bubble_sort(example))
    # 插入排序
    # print(insert_sort(example))
    # 归并排序
    # print(merge_sort(example))
    # 快速排序
    # print(quick_sort(example))
    # 希尔排序
    # print(shell_sort(example))
    # 选择排序
    print(select_sort(example))


if __name__ == '__main__':
    main()