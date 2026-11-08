class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None


class BinaryTree:
    """Binary search tree: smaller values go to the left, bigger values go to the right."""

    def __init__(self):
        self.root = None
        self.delete_note = ""     # says which delete case happened (used by the Works page)

    # ---------- Insert ----------
    def insert(self, key):
        """Add a value. Returns False if it is already in the tree."""
        if self.search(self.root, key) is not None:
            return False
        self.root = self._insert(self.root, key)
        return True

    def _insert(self, root, key):
        if root is None:
            return Node(key)
        if key < root.data:
            root.left = self._insert(root.left, key)
        else:
            root.right = self._insert(root.right, key)
        return root

    # ---------- Search ----------
    def search(self, root, key, path=None):
        """Return the node that holds key, or None if it is not in the tree.

        path is optional. Give it an empty list and it will be filled with every
        value visited on the way down (the Works page uses it to draw the search).
        """
        if root is None:
            return None
        if path is not None:
            path.append(root.data)
        if key == root.data:
            return root
        if key < root.data:
            return self.search(root.left, key, path)
        return self.search(root.right, key, path)

    # ---------- Traversals ----------
    def post_traversal(self, start, traversal):
        """Post-order: left, then right, then the node itself.

        Start with traversal = [] and the values are added in post-order.
        """
        if start:
            traversal = self.post_traversal(start.left, traversal)
            traversal = self.post_traversal(start.right, traversal)
            traversal.append(start.data)
        return traversal

    def in_traversal(self, start, traversal):
        """In-order: left, node, right. On a search tree this gives sorted order."""
        if start:
            traversal = self.in_traversal(start.left, traversal)
            traversal.append(start.data)
            traversal = self.in_traversal(start.right, traversal)
        return traversal

    def pre_traversal(self, start, traversal):
        """Pre-order: node, left, right."""
        if start:
            traversal.append(start.data)
            traversal = self.pre_traversal(start.left, traversal)
            traversal = self.pre_traversal(start.right, traversal)
        return traversal

    # ---------- Delete ----------
    def min_node(self, root):
        """The smallest node under root is the one furthest to the left."""
        current = root
        while current.left is not None:
            current = current.left
        return current

    def delete_node(self, root, key):
        """Delete key from the tree under root and return the new root of that part.

        Three cases once the node is found:
          1. no children    -> just remove it
          2. one child      -> the child takes its place
          3. two children   -> copy the inorder successor (smallest value in the
                               right side) into this node, then delete the successor
        """
        if root is None:
            self.delete_note = str(key) + " is not in the tree."
            return None

        if key < root.data:
            root.left = self.delete_node(root.left, key)
        elif key > root.data:
            root.right = self.delete_node(root.right, key)
        else:
            if root.left is None and root.right is None:
                self.delete_note = str(key) + " had no children, so it was simply removed."
                return None
            if root.left is None:
                self.delete_note = str(key) + " had one child (" + str(root.right.data) + \
                                   "), so that child took its place."
                return root.right
            if root.right is None:
                self.delete_note = str(key) + " had one child (" + str(root.left.data) + \
                                   "), so that child took its place."
                return root.left

            successor = self.min_node(root.right)
            note = (str(key) + " had two children. The inorder successor " + str(successor.data) +
                    " (smallest value on the right) took its place.")
            root.data = successor.data
            root.right = self.delete_node(root.right, successor.data)
            self.delete_note = note
        return root

    def remove(self, key):
        """Delete a value from the whole tree. Returns False if it was not there."""
        if self.search(self.root, key) is None:
            self.delete_note = str(key) + " is not in the tree."
            return False
        self.root = self.delete_node(self.root, key)
        return True

    # ---------- Helpers ----------
    def size(self, root="start"):
        if root == "start":
            root = self.root
        if root is None:
            return 0
        return 1 + self.size(root.left) + self.size(root.right)

    def to_dict(self, root="start"):
        """The tree as nested dictionaries (the Works page sends this to the browser)."""
        if root == "start":
            root = self.root
        if root is None:
            return None
        return {"data": root.data, "left": self.to_dict(root.left), "right": self.to_dict(root.right)}


if __name__ == "__main__":
    tree = BinaryTree()
    for v in [50, 30, 70, 20, 40, 60, 80]:
        tree.insert(v)

    print("In-order  :", tree.in_traversal(tree.root, []))
    print("Pre-order :", tree.pre_traversal(tree.root, []))
    print("Post-order:", tree.post_traversal(tree.root, []))

    print("Search 60 :", tree.search(tree.root, 60) is not None)
    print("Search 65 :", tree.search(tree.root, 65) is not None)

    tree.remove(20)                       # leaf
    print(tree.delete_note, tree.in_traversal(tree.root, []))
    tree.remove(30)                       # one child
    print(tree.delete_note, tree.in_traversal(tree.root, []))
    tree.remove(50)                       # two children (the root)
    print(tree.delete_note, tree.in_traversal(tree.root, []))
    print("Post-order:", tree.post_traversal(tree.root, []))
