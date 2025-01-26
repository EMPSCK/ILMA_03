#Сортировка хоара
import random
def hoar_sort(a):
    if len(a) <= 1:
        return a
    q = random.choise(a)
    l, r, m = [], [], []
    for num in a:
        if num == q:
            m.append(q)
        elif num > q:
            r.append(num)
        else:
            l.append(num)
    return hoar_sort(l) + m + hoar_sort(r)



def hoar_sort_01(a):
    if len(a) <= 1:
        return a
    mid = random.choice(a)
    l, r, m = [], [], []
    for i in range(len(a)):
        if a[i] > mid:
            r.append(a[i])
        elif a[i] < mid:
            l.append(a[i])
        else:
            m.append(a[i])

    return hoar_sort(l) + m + hoar_sort(r)


def merge_sort_01(a):
    if len(a) <= 1:
        return a

    mid = len(a)//2
    left = a[:mid]
    right = a[mid:]
    merge_sort_01(left)
    merge_sort_01(right)

    l, r, c = 0, 0, 0
    k = [0]*len(a)
    while l != len(left) and r != len(right):
        if left[l] <= right[r]:
            k[c] = left[l]
            l += 1
            c += 1
        else:
            k[c] = right[r]
            r += 1
            c += 1

    while l != len(left):
        k[c] = left[l]
        l += 1
        c += 1

    while r != len(right):
        k[c] = right[r]
        r += 1
        c += 1

    return k


def bubble_sort_01(a):
    for i in range(len(a)):
        for j in range(len(a) - 1 - i):
            if a[j] > a[j + 1]:
                a[j + 1], a[j] = a[j], a[j + 1]
    return a


def merge_sort(arr):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left_half = merge_sort(arr[:mid])
    right_half = merge_sort(arr[mid:])

    return merge(left_half, right_half)


def merge(left, right):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    while i < len(left):
        result.append(left[i])
        i += 1

    while j < len(right):
        result.append(right[j])
        j += 1

    return result


def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

firstList = [[3,10]]
secondList = [[5,10]]
ans = []
i, j = 0, 0
while i != len(firstList) and j != len(secondList):
    ff, fl = firstList[i]
    sf, sl = secondList[j]

    if ff > sl:
        j += 1
    elif sf > fl:
        i += 1
    else:
        if ff == sf and fl == sl:
            ans.append([ff, fl])
            i += 1
            j += 1

        elif fl >= sl:
            ans.append([max(ff, sf), sl])
            j += 1
        elif sl > fl:
            ans.append([max(ff, sf), fl])
            i += 1



s = "abc"
t = "ahbgdc"

i, j = 0, 0
if len(s) > len(t):
    print(False)

while i != len(s) and j != len(t):
    if s[i] == t[j]:
        i += 1
    j += 1

