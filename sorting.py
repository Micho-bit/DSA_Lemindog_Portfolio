"""Bubble, selection, insertion, merge and quick sort.

Every sort works on a COPY of the list you give it and returns the sorted copy.
Each one can also record every step it takes (a Recorder). The Works page uses
those steps to draw the animated bars.

    bubble_sort([5, 2, 9, 1])                  -> [1, 2, 5, 9]
    sort_steps("bubble", [5, 2, 9, 1])         -> (sorted list, list of steps)
"""
import random


class Recorder:
    """Holds the list being sorted and, if record=True, a snapshot after each step."""

    def __init__(self, arr, record=True):
        self.a = list(arr)
        self.record = record
        self.steps = []
        self.comparisons = 0
        self.moves = 0
        self.done = set()      # positions that count as sorted (green)
        self.pivot = None      # pivot / current smallest / item being inserted (purple)
        self.range = None      # [low, high] part being worked on (merge and quick sort)
        self._snap("Start. The bars are in random order.")

    def _snap(self, msg, cmp=(), moved=()):
        if not self.record:
            return
        self.steps.append({
            "a": self.a[:],
            "cmp": list(cmp),
            "moved": list(moved),
            "done": sorted(self.done),
            "pivot": self.pivot,
            "range": self.range,
            "msg": msg,
            "comparisons": self.comparisons,
            "moves": self.moves,
        })

    def compare(self, i=None, j=None, msg=None):
        """Count one comparison. i and j are the positions to highlight (optional)."""
        self.comparisons += 1
        if msg is None:
            msg = "Compare " + str(self.a[i]) + " and " + str(self.a[j]) + "."
        cmp = [x for x in (i, j) if x is not None]
        self._snap(msg, cmp=cmp)

    def swap(self, i, j, msg=None):
        """Swap two positions and count one move."""
        if msg is None:
            msg = "Swap " + str(self.a[i]) + " and " + str(self.a[j]) + "."
        self.a[i], self.a[j] = self.a[j], self.a[i]
        self.moves += 1
        self._snap(msg, moved=(i, j))

    def write(self, k, value, msg):
        """Put a value at position k (used by merge sort) and count one move."""
        self.a[k] = value
        self.moves += 1
        self._snap(msg, moved=(k,))

    def note(self, msg):
        """A step that only explains something."""
        self._snap(msg)

    def mark(self, *positions):
        self.done.update(positions)

    def finish(self):
        self.done = set(range(len(self.a)))
        self.pivot = None
        self.range = None
        self._snap("Done. Every bar is in place.")


def bubble_sort(arr, rec=None):
    """Swap neighbours that are out of order. Stable, O(n^2), O(n) if already sorted."""
    rec = rec or Recorder(arr, record=False)
    a = rec.a
    n = len(a)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            rec.compare(j, j + 1)
            if a[j] > a[j + 1]:
                rec.swap(j, j + 1)
                swapped = True
        rec.mark(n - 1 - i)
        rec.note(str(a[n - 1 - i]) + " has bubbled to the end, so it is in its final place.")
        if not swapped:
            rec.note("No swaps in this pass, so the list is already sorted.")
            break
    rec.finish()
    return a


def selection_sort(arr, rec=None):
    """Move the smallest remaining item to the front. Not stable, always O(n^2)."""
    rec = rec or Recorder(arr, record=False)
    a = rec.a
    n = len(a)
    for i in range(n - 1):
        min_idx = i
        rec.pivot = min_idx
        rec.note("Look for the smallest item from here on. Start with " + str(a[i]) + ".")
        for j in range(i + 1, n):
            rec.compare(j, min_idx, "Compare " + str(a[j]) + " with the smallest so far, " +
                        str(a[min_idx]) + ".")
            if a[j] < a[min_idx]:
                min_idx = j
                rec.pivot = min_idx
                rec.note(str(a[min_idx]) + " is the new smallest.")
        if min_idx != i:
            rec.swap(i, min_idx, "Swap the smallest, " + str(a[min_idx]) +
                     ", to the front of the unsorted part.")
        else:
            rec.note(str(a[i]) + " is already the smallest, so it stays.")
        rec.pivot = None
        rec.mark(i)
    rec.finish()
    return a


def insertion_sort(arr, rec=None):
    """Slide each item left into the sorted part. Stable, O(n^2), O(n) if nearly sorted."""
    rec = rec or Recorder(arr, record=False)
    a = rec.a
    rec.mark(0)
    rec.note("The first item on its own is already sorted.")
    for i in range(1, len(a)):
        j = i
        rec.pivot = j
        rec.note("Take " + str(a[i]) + " and slide it left into the sorted part.")
        while j > 0:
            rec.compare(j - 1, j, "Compare " + str(a[j - 1]) + " with " + str(a[j]) + ".")
            if a[j - 1] > a[j]:
                rec.swap(j - 1, j, str(a[j - 1]) + " is bigger, so " + str(a[j]) + " moves left.")
                j -= 1
                rec.pivot = j
            else:
                break
        rec.mark(*range(i + 1))
        rec.pivot = None
        rec.note(str(a[j]) + " is in place. The first " + str(i + 1) + " items are sorted.")
    rec.finish()
    return a


def merge_sort(arr, rec=None):
    """Split in half, sort each half, merge them. Stable, always O(n log n), O(n) extra space."""
    rec = rec or Recorder(arr, record=False)
    a = rec.a

    def merge(lo, mid, hi):
        rec.range = [lo, hi]
        left = a[lo:mid + 1]
        right = a[mid + 1:hi + 1]
        rec.note("Merge " + str(left) + " and " + str(right) + ".")
        i = j = 0
        k = lo
        while i < len(left) and j < len(right):
            rec.compare(msg="Compare " + str(left[i]) + " (left) with " + str(right[j]) + " (right).")
            if left[i] <= right[j]:      # <= keeps equal items in their original order
                rec.write(k, left[i], "Take " + str(left[i]) + " from the left half.")
                i += 1
            else:
                rec.write(k, right[j], "Take " + str(right[j]) + " from the right half.")
                j += 1
            k += 1
        while i < len(left):
            rec.write(k, left[i], "Copy the leftover " + str(left[i]) + " from the left half.")
            i += 1
            k += 1
        while j < len(right):
            rec.write(k, right[j], "Copy the leftover " + str(right[j]) + " from the right half.")
            j += 1
            k += 1
        rec.note("Merged into " + str(a[lo:hi + 1]) + ".")

    def sort(lo, hi):
        if lo >= hi:
            return
        mid = (lo + hi) // 2
        rec.range = [lo, hi]
        rec.note("Split positions " + str(lo + 1) + " to " + str(hi + 1) + " in half.")
        sort(lo, mid)
        sort(mid + 1, hi)
        merge(lo, mid, hi)

    sort(0, len(a) - 1)
    rec.finish()
    return a


def quick_sort(arr, rec=None):
    """Partition around a random pivot, then sort each side. Not stable, O(n log n) on average."""
    rec = rec or Recorder(arr, record=False)
    a = rec.a

    def sort(lo, hi):
        if lo > hi:
            return
        rec.range = [lo, hi]
        if lo == hi:
            rec.mark(lo)
            rec.note(str(a[lo]) + " is alone, so it is in its final place.")
            return

        p = random.randint(lo, hi)       # random pivot avoids the O(n^2) case on sorted input
        pivot = a[p]
        if p != hi:
            rec.swap(p, hi, "Pick " + str(pivot) + " as the pivot and move it to the end.")
        else:
            rec.note("Pick " + str(pivot) + " as the pivot.")
        rec.pivot = hi

        i = lo                            # a[lo..i-1] holds everything smaller than the pivot
        for j in range(lo, hi):
            rec.compare(j, hi, "Compare " + str(a[j]) + " with the pivot " + str(pivot) + ".")
            if a[j] < pivot:
                if i != j:
                    rec.swap(i, j, str(a[j]) + " is smaller than the pivot, so it goes to the left side.")
                i += 1

        if i != hi:
            rec.swap(i, hi, "Put the pivot " + str(pivot) + " between the smaller and the larger items.")
        else:
            rec.note("The pivot " + str(pivot) + " is already between the smaller and larger items.")
        rec.pivot = None
        rec.mark(i)
        sort(lo, i - 1)
        sort(i + 1, hi)

    sort(0, len(a) - 1)
    rec.finish()
    return a


# ---------- Used by the Works page ----------
SORTS = {
    "bubble": bubble_sort,
    "selection": selection_sort,
    "insertion": insertion_sort,
    "merge": merge_sort,
    "quick": quick_sort,
}

INFO = {
    "bubble": {
        "name": "Bubble Sort", "best": "O(n)", "average": "O(n²)", "worst": "O(n²)",
        "space": "O(1)", "stable": True,
        "about": "Compares neighbours and swaps them when they are out of order. After each pass "
                 "the biggest remaining bar has bubbled to the end."},
    "selection": {
        "name": "Selection Sort", "best": "O(n²)", "average": "O(n²)", "worst": "O(n²)",
        "space": "O(1)", "stable": False,
        "about": "Finds the smallest bar in the unsorted part and swaps it to the front. "
                 "It makes very few swaps but always checks every pair."},
    "insertion": {
        "name": "Insertion Sort", "best": "O(n)", "average": "O(n²)", "worst": "O(n²)",
        "space": "O(1)", "stable": True,
        "about": "Takes the next bar and slides it left until it sits in the right place "
                 "among the bars already sorted. Fast when the list is nearly sorted."},
    "merge": {
        "name": "Merge Sort", "best": "O(n log n)", "average": "O(n log n)", "worst": "O(n log n)",
        "space": "O(n)", "stable": True,
        "about": "Splits the list in half, sorts each half, then merges the two sorted halves. "
                 "The faded bars are outside the part being merged."},
    "quick": {
        "name": "Quick Sort", "best": "O(n log n)", "average": "O(n log n)", "worst": "O(n²)",
        "space": "O(log n)", "stable": False,
        "about": "Picks a pivot, moves smaller bars to its left and larger bars to its right, "
                 "then repeats on each side. The faded bars are outside the part being partitioned."},
}


def sort_steps(name, arr):
    """Run one sort and return (sorted list, list of recorded steps)."""
    rec = Recorder(arr)
    SORTS[name](arr, rec)
    return rec.a, rec.steps


if __name__ == "__main__":
    data = [5, 2, 9, 1, 5, 6]
    for key, func in SORTS.items():
        print(INFO[key]["name"] + ":", func(data))
    print("Original is untouched:", data)

    # Quick self-check against Python's own sorted()
    for func in SORTS.values():
        for case in ([], [1], [2, 1], [3, 3, 3], list(range(20, 0, -1)),
                     [random.randint(-50, 50) for _ in range(100)]):
            assert func(case) == sorted(case), func.__name__
    print("All sorts match sorted().")
