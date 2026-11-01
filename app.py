from flask import Flask, render_template, jsonify, request
from stack import Stack
from linked_list import LinkedList
from my_queue import Queue
from sorting import SORTS, INFO, sort_steps

app = Flask(__name__)


@app.route('/')
def index():
    # Home: the welcome screen, then the Works page
    return render_template('index.html', welcome=True)


@app.route('/works')
def works():
    # Works page (list of programs), without the welcome screen
    return render_template('index.html', welcome=False)


# Each program has its own page, still part of the Works section
@app.route('/works/uppercase')
def uppercase():
    return render_template('uppercase.html')


@app.route('/works/linkedlist')
def linkedlist():
    return render_template('linkedlist.html')


@app.route('/works/area/circle')
def circle():
    return render_template('circle.html')


@app.route('/works/area/triangle')
def triangle():
    return render_template('triangle.html')


# ---------- Infix to Postfix ----------
def prec(c):
    if c == '^':
        return 3
    elif c == '/' or c == '*':
        return 2
    elif c == '+' or c == '-':
        return 1
    else:
        return -1


def isRightAssociative(c):
    return c == '^'


def stack_to_list(stack):
    """Read the linked stack from bottom to top (used only to draw the steps)."""
    items = []
    current = stack.top
    while current:
        items.append(current.data)
        current = current.next
    items.reverse()
    return items


def infixToPostfixSteps(s):
    """Same algorithm as before, using my own Stack class, and it records every step."""
    st = Stack()
    res = []
    steps = []

    def snap(pos, action):
        steps.append({"pos": pos, "action": action,
                      "stack": stack_to_list(st), "output": res[:]})

    snap(-1, "Start. The stack and the output are both empty.")

    pos = -1
    for c in s:
        if c.isspace():
            continue
        pos += 1

        # If operand, add to result
        if c.isascii() and c.isalnum():
            res.append(c)
            snap(pos, "Operand '" + c + "': add it straight to the output.")

        # If '(', push to stack
        elif c == '(':
            st.push('(')
            snap(pos, "'(' : push it onto the stack.")

        # If ')', pop until '('
        elif c == ')':
            popped = []
            while st.peek() is not None and st.peek() != '(':
                popped.append(st.peek())
                res.append(st.pop())
            if st.peek() is None:
                raise ValueError("Unbalanced parentheses: extra ')'.")
            st.pop()
            if popped:
                text = "')' : pop " + ", ".join("'" + x + "'" for x in popped) + \
                       " to the output until '(' is found, then discard '('."
            else:
                text = "')' : nothing to pop, discard the matching '('."
            snap(pos, text)

        # If operator
        elif c in '+-*/^':
            popped = []
            while st.peek() is not None and st.peek() != '(' and \
                    (prec(st.peek()) > prec(c) or
                     (prec(st.peek()) == prec(c) and not isRightAssociative(c))):
                popped.append(st.peek())
                res.append(st.pop())
            st.push(c)
            if popped:
                text = ("Operator '" + c + "': pop " +
                        ", ".join("'" + x + "'" for x in popped) +
                        " to the output (higher or equal precedence), then push '" + c + "'.")
            else:
                text = "Operator '" + c + "': push it onto the stack."
            snap(pos, text)

        else:
            raise ValueError("Invalid character: " + c)

    # Pop remaining operators
    while st.peek() is not None:
        top = st.pop()
        if top == '(':
            raise ValueError("Unbalanced parentheses: missing ')'.")
        res.append(top)
        snap(-1, "End of input: pop '" + top + "' from the stack to the output.")

    snap(-1, "Done. The output is the postfix expression.")

    return ''.join(res), steps


def infixToPostfix(s):
    return infixToPostfixSteps(s)[0]


@app.route('/works/infix-to-postfix')
def infixtopostfix():
    return render_template('infixtopostfix.html')


@app.route('/works/infix-to-postfix/convert', methods=['POST'])
def convert_infix():
    data = request.get_json(silent=True) or {}
    try:
        postfix, steps = infixToPostfixSteps(data.get('infix', ''))
        return jsonify(postfix=postfix, steps=steps)
    except ValueError as e:
        return jsonify(error=str(e)), 400


# ---------- Linked List (uses my LinkedList class from Lab_3_linklist.py) ----------
my_list = LinkedList()
for _v in ["10", "20", "30"]:
    my_list.insert_at_end(_v)


def ll_to_list():
    items = []
    current = my_list.head
    while current:
        items.append(current.data)
        current = current.next
    return items


@app.route('/works/linkedlist/state')
def linkedlist_state():
    return jsonify(list=ll_to_list())


@app.route('/works/linkedlist/action', methods=['POST'])
def linkedlist_action():
    data = request.get_json(silent=True) or {}
    action = data.get('action', '')
    value = str(data.get('value', '')).strip()
    after = str(data.get('after', '')).strip()
    msg = ""
    mark = None

    if action == "insert_at_beginning":
        my_list.insert_at_beginning(value)
        msg = "Inserted " + value + " at the beginning."
        mark = 0

    elif action == "insert_at_end":
        my_list.insert_at_end(value)
        msg = "Inserted " + value + " at the end."
        mark = len(ll_to_list()) - 1

    elif action == "insert_after":
        if my_list.search(after):
            my_list.insert_after(after, value)
            msg = "Inserted " + value + " after " + after + "."
            mark = ll_to_list().index(after) + 1
        else:
            msg = "No node holds " + after + ". The list is unchanged."

    elif action == "remove_beginning":
        removed = my_list.remove_beginning()
        msg = "The list is empty." if removed is None else "Removed " + removed + " from the beginning."

    elif action == "remove_at_end":
        removed = my_list.remove_at_end()
        msg = "The list is empty." if removed is None else "Removed " + removed + " from the end."

    elif action == "remove_at":
        removed = my_list.remove_at(value)
        msg = value + " is not in the list. The list is unchanged." if removed is None else "Removed " + removed + "."

    elif action == "search":
        if my_list.search(value):
            msg = "Found " + value + " in the list."
            mark = ll_to_list().index(value)
        else:
            msg = value + " is not in the list."

    else:
        return jsonify(error="Unknown action."), 400

    return jsonify(list=ll_to_list(), message=msg, mark=mark)


# ---------- Queue (uses my own Queue class in my_queue.py) ----------
my_queue = Queue()
for _v in ["10", "20", "30"]:
    my_queue.enqueue(_v)


def queue_to_list():
    items = []
    current = my_queue.front
    while current:
        items.append(current.data)
        current = current.next
    return items


@app.route('/works/queue')
def queue_page():
    return render_template('queue.html')


@app.route('/works/queue/state')
def queue_state():
    return jsonify(list=queue_to_list())


@app.route('/works/queue/action', methods=['POST'])
def queue_action():
    data = request.get_json(silent=True) or {}
    action = data.get('action', '')
    value = str(data.get('value', '')).strip()
    msg = ""
    mark = None

    if action == "enqueue":
        my_queue.enqueue(value)
        msg = "Enqueued " + value + " at the rear."
        mark = len(queue_to_list()) - 1

    elif action == "dequeue":
        removed = my_queue.dequeue()
        msg = "The queue is empty." if removed is None else "Dequeued " + removed + " from the front."

    elif action == "peek":
        front = my_queue.peek()
        if front is None:
            msg = "The queue is empty."
        else:
            msg = "The front of the queue is " + front + "."
            mark = 0

    else:
        return jsonify(error="Unknown action."), 400

    return jsonify(list=queue_to_list(), message=msg, mark=mark)


# ---------- Sorting visualizer (uses my sorting.py) ----------
MAX_BARS = 50


@app.route('/works/sorting')
def sorting_page():
    return render_template('sorting.html', info=INFO)


@app.route('/works/sorting/run', methods=['POST'])
def sorting_run():
    data = request.get_json(silent=True) or {}
    name = data.get('algorithm', '')
    arr = data.get('array')

    if name not in SORTS:
        return jsonify(error="Unknown sorting algorithm."), 400
    if not isinstance(arr, list) or not 2 <= len(arr) <= MAX_BARS:
        return jsonify(error="Use between 2 and " + str(MAX_BARS) + " numbers."), 400
    if not all(isinstance(x, int) and not isinstance(x, bool) and 1 <= x <= 99 for x in arr):
        return jsonify(error="Every number must be a whole number from 1 to 99."), 400

    result, steps = sort_steps(name, arr)
    return jsonify(sorted=result, steps=steps)


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == "__main__":
    app.run(debug=True)