// Binary tree UI. The tree itself lives in Python (my BinaryTree class in binary_tree.py),
// and the buttons talk to it through the Flask routes in app.py.
var NS = "http://www.w3.org/2000/svg";
var svg = document.getElementById("bt-svg");
var btVal = document.getElementById("bt-value");
var btMsg = document.getElementById("bt-msg");
var orderEl = document.getElementById("bt-order");
var btnList = document.querySelectorAll("[data-bt]");

var STEP = 550;          // milliseconds between highlighted nodes
var nodeEls = {};        // value -> the <g> element drawn for it
var timers = [];

function callTree(action, value){
  return fetch("/works/binary-tree/action", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: action, value: value })
  }).then(function(res){
    return res.json().then(function(d){ d.ok = res.ok; return d; });
  });
}

function make(tag, attrs){
  var el = document.createElementNS(NS, tag);
  for (var k in attrs) el.setAttribute(k, attrs[k]);
  return el;
}

// Draw the tree. Each node's x position is its place in the in-order walk, so nothing overlaps.
function drawTree(tree){
  svg.innerHTML = "";
  nodeEls = {};
  var X_GAP = 46, Y_GAP = 70, R = 20, PAD = 30;

  if (!tree) {
    svg.setAttribute("viewBox", "0 0 300 90");
    var t = make("text", { x: 150, y: 50, "text-anchor": "middle", "class": "bt-empty" });
    t.textContent = "The tree is empty. Insert a value to start.";
    svg.appendChild(t);
    svg.setAttribute("aria-label", "Empty binary tree");
    return;
  }

  var items = [], counter = 0, maxDepth = 0, pre = [];
  function walk(n, depth, parent){
    if (!n) return;
    var it = { v: n.data, depth: depth, parent: parent, x: 0 };
    pre.push(n.data);
    if (depth > maxDepth) maxDepth = depth;
    walk(n.left, depth + 1, it);
    it.x = counter++;
    items.push(it);
    walk(n.right, depth + 1, it);
  }
  walk(tree, 0, null);

  var innerW = (counter - 1) * X_GAP;
  var width = Math.max(innerW + PAD * 2, 300);
  var height = maxDepth * Y_GAP + PAD * 2;
  var offset = (width - innerW) / 2;
  svg.setAttribute("viewBox", "0 0 " + width + " " + height);

  items.forEach(function(it){
    it.cx = offset + it.x * X_GAP;
    it.cy = PAD + it.depth * Y_GAP;
  });
  items.forEach(function(it){
    if (it.parent) svg.appendChild(make("line", { x1: it.parent.cx, y1: it.parent.cy, x2: it.cx, y2: it.cy, "class": "bt-edge" }));
  });
  items.forEach(function(it){
    var g = make("g", { "class": "bt-node" });
    g.appendChild(make("circle", { cx: it.cx, cy: it.cy, r: R }));
    var txt = make("text", { x: it.cx, y: it.cy, "text-anchor": "middle", "dominant-baseline": "central" });
    txt.textContent = it.v;
    g.appendChild(txt);
    svg.appendChild(g);
    nodeEls[it.v] = g;
  });
  svg.setAttribute("aria-label", "Binary tree with " + items.length + " node" +
                   (items.length === 1 ? "" : "s") + ". Root " + pre[0] + ". Pre-order: " + pre.join(", ") + ".");
}

function setClass(v, cls){
  if (nodeEls[v]) nodeEls[v].setAttribute("class", "bt-node" + (cls ? " " + cls : ""));
}

function addOrderBox(v, first){
  if (first) orderEl.innerHTML = "";
  else {
    var a = document.createElement("span"); a.className = "arrow"; a.textContent = "\u2192";
    a.setAttribute("aria-hidden", "true"); orderEl.appendChild(a);
  }
  var n = document.createElement("div"); n.className = "node"; n.textContent = v;
  orderEl.appendChild(n);
}

function setBusy(on){
  for (var i = 0; i < btnList.length; i++) btnList[i].disabled = on;
}

// Light up the values one at a time, then show the message
function animate(values, mark, message){
  if (!values.length) {
    btMsg.textContent = message;
    if (mark !== null && mark !== undefined) setClass(mark, "found");
    return;
  }
  setBusy(true);
  var i = 0;
  function next(){
    if (i > 0) setClass(values[i - 1], "seen");
    if (i < values.length) {
      setClass(values[i], "cur");
      addOrderBox(values[i], i === 0);
      i++;
      timers.push(setTimeout(next, STEP));
    } else {
      if (mark !== null && mark !== undefined) setClass(mark, "found");
      btMsg.textContent = message;
      setBusy(false);
    }
  }
  next();
}

function run(action){
  var v = btVal.value.trim();
  var needsValue = ["insert", "search", "delete"].indexOf(action) > -1;
  if (needsValue && (!/^\d+$/.test(v) || +v < 1 || +v > 999)) {
    btMsg.textContent = "Enter a whole number from 1 to 999 first.";
    btVal.focus();
    return;
  }
  callTree(action, v).then(function(r){
    if (!r.ok) { btMsg.textContent = r.error || "Something went wrong."; return; }
    drawTree(r.tree);
    if (action === "reset") orderEl.textContent = "Run a search or a traversal to see the order here.";
    var values = r.order.length ? r.order : r.path;
    if (values.length) btMsg.textContent = "...";
    animate(values, r.mark, r.message);
    if (action === "insert") { btVal.value = ""; btVal.focus(); }
  }).catch(function(){
    btMsg.textContent = "Could not reach the server.";
    setBusy(false);
  });
}

for (var i = 0; i < btnList.length; i++) {
  (function(btn){
    btn.addEventListener("click", function(){ run(btn.getAttribute("data-bt")); });
  })(btnList[i]);
}
btVal.addEventListener("keydown", function(e){ if (e.key === "Enter") run("insert"); });

fetch("/works/binary-tree/state")
  .then(function(res){ return res.json(); })
  .then(function(r){ drawTree(r.tree); })
  .catch(function(){ btMsg.textContent = "Could not reach the server."; });
