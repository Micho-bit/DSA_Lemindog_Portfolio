// Sorting visualizer. The sorting itself runs in Python (sorting.py). This page sends the bars
// to Flask, gets back every step of the chosen sort, and plays the steps back as bars.
var info = JSON.parse(document.getElementById("sv-info").textContent);

var algoSel = document.getElementById("sv-algo");
var sizeIn = document.getElementById("sv-size"), sizeOut = document.getElementById("sv-size-out");
var speedIn = document.getElementById("sv-speed");
var customIn = document.getElementById("sv-custom");
var barsEl = document.getElementById("sv-bars");
var msgEl = document.getElementById("sv-msg"), statsEl = document.getElementById("sv-stats");
var statusEl = document.getElementById("sv-status"), aboutEl = document.getElementById("sv-about");
var btnRestart = document.getElementById("sv-restart"), btnBack = document.getElementById("sv-back");
var btnPlay = document.getElementById("sv-play"), btnStep = document.getElementById("sv-step");
var btnEnd = document.getElementById("sv-end");

var DELAYS = [900, 550, 320, 180, 100, 50, 25, 10];   // milliseconds per step, slow to fast

var base = [];          // the bars before sorting
var steps = [];         // steps from Python for the current algorithm and bars
var pos = 0;            // which step is showing
var timer = null;       // set while playing
var maxVal = 1;
var barEls = [], valEls = [];

function randomBars(n){
  var a = [], i, j, t;
  for (i = 0; i < n; i++) a.push(Math.max(1, Math.round((i + 1) * 99 / n)));
  for (i = n - 1; i > 0; i--) {           // shuffle
    j = Math.floor(Math.random() * (i + 1));
    t = a[i]; a[i] = a[j]; a[j] = t;
  }
  return a;
}

function buildBars(arr){
  barsEl.innerHTML = "";
  barEls = []; valEls = [];
  maxVal = Math.max.apply(null, arr);
  barsEl.className = "sv-bars" + (arr.length <= 25 ? " show-vals" : "");
  arr.forEach(function(){
    var b = document.createElement("div"); b.className = "bar";
    var v = document.createElement("span"); v.className = "bar-val";
    b.appendChild(v); barsEl.appendChild(b);
    barEls.push(b); valEls.push(v);
  });
}

function paint(f){
  var inRange = f.range !== null && f.range !== undefined;
  for (var k = 0; k < barEls.length; k++) {
    var cls = "bar";
    if (f.done.indexOf(k) > -1) cls += " done";
    else if (inRange && (k < f.range[0] || k > f.range[1])) cls += " out";
    if (f.pivot === k) cls += " pivot";
    if (f.cmp.indexOf(k) > -1) cls += " cmp";
    if (f.moved.indexOf(k) > -1) cls += " moved";
    barEls[k].className = cls;
    barEls[k].style.height = (f.a[k] / maxVal * 100) + "%";
    valEls[k].textContent = f.a[k];
  }
  barsEl.setAttribute("aria-label", "Bars: " + f.a.join(", "));
}

function baseFrame(){
  return { a: base, cmp: [], moved: [], done: [], pivot: null, range: null,
           comparisons: 0, moves: 0, msg: "Press Play to start, or Step to go one move at a time." };
}

function showAbout(){
  var a = info[algoSel.value];
  aboutEl.innerHTML = "";
  var p1 = document.createElement("p"); p1.textContent = a.about; p1.style.margin = "0 0 8px";
  var p2 = document.createElement("p"); p2.style.margin = "0";
  p2.textContent = "Time: best " + a.best + ", average " + a.average + ", worst " + a.worst +
                   ". Extra space: " + a.space + ". " + (a.stable ? "Stable." : "Not stable.");
  aboutEl.appendChild(p1); aboutEl.appendChild(p2);
}

function updateControls(){
  var loaded = steps.length > 0, last = steps.length - 1;
  btnRestart.disabled = !loaded || pos === 0;
  btnBack.disabled = !loaded || pos === 0;
  btnStep.disabled = loaded && pos >= last;
  btnEnd.disabled = loaded && pos >= last;
  btnPlay.textContent = timer ? "Pause" : "Play";
}

function show(i){
  pos = Math.max(0, Math.min(i, steps.length - 1));
  var f = steps[pos];
  paint(f);
  msgEl.textContent = f.msg;
  statsEl.textContent = "Comparisons: " + f.comparisons + " \u00b7 Moves: " + f.moves +
                        " \u00b7 Step " + pos + " of " + (steps.length - 1);
  updateControls();
}

function pause(){
  if (timer) { clearTimeout(timer); timer = null; }
  updateControls();
}

function resetRun(){
  pause();
  steps = []; pos = 0;
  paint(baseFrame());
  msgEl.textContent = baseFrame().msg;
  statsEl.textContent = "Comparisons: 0 \u00b7 Moves: 0";
  statusEl.textContent = "";
  updateControls();
}

function setBars(arr){
  base = arr;
  buildBars(arr);
  resetRun();
}

// Ask Python for the steps (only once per algorithm and bars)
function load(){
  if (steps.length) return Promise.resolve(true);
  msgEl.textContent = "Getting the steps from Python...";
  return fetch("/works/sorting/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ algorithm: algoSel.value, array: base })
  }).then(function(res){
    return res.json().then(function(d){ return { ok: res.ok, d: d }; });
  }).then(function(r){
    if (!r.ok) { msgEl.textContent = r.d.error || "Something went wrong."; return false; }
    steps = r.d.steps; pos = 0;
    return true;
  }).catch(function(){
    msgEl.textContent = "Could not reach the server.";
    return false;
  });
}

function announceDone(){
  var f = steps[steps.length - 1];
  statusEl.textContent = info[algoSel.value].name + " finished with " + f.comparisons +
                         " comparisons and " + f.moves + " moves.";
}

function tick(){
  show(pos + 1);
  if (pos >= steps.length - 1) { pause(); announceDone(); return; }
  timer = setTimeout(tick, DELAYS[speedIn.value - 1]);
}

function play(){
  if (timer) { pause(); return; }
  load().then(function(ok){
    if (!ok) return;
    if (pos >= steps.length - 1) show(0);
    timer = setTimeout(tick, DELAYS[speedIn.value - 1]);
    updateControls();
  });
}

btnPlay.addEventListener("click", play);
btnStep.addEventListener("click", function(){
  pause();
  load().then(function(ok){
    if (!ok) return;
    show(pos + 1);
    if (pos >= steps.length - 1) announceDone();
  });
});
btnBack.addEventListener("click", function(){ pause(); show(pos - 1); });
btnRestart.addEventListener("click", function(){ pause(); show(0); });
btnEnd.addEventListener("click", function(){
  pause();
  load().then(function(ok){ if (ok) { show(steps.length - 1); announceDone(); } });
});

algoSel.addEventListener("change", function(){ showAbout(); resetRun(); });
speedIn.addEventListener("input", function(){ /* the next step uses the new speed */ });

sizeIn.addEventListener("input", function(){
  sizeOut.textContent = sizeIn.value;
  setBars(randomBars(parseInt(sizeIn.value, 10)));
});
document.getElementById("sv-shuffle").addEventListener("click", function(){
  setBars(randomBars(parseInt(sizeIn.value, 10)));
});

function useCustom(){
  var parts = customIn.value.split(/[\s,]+/).filter(function(s){ return s !== ""; });
  var nums = parts.map(Number);
  var bad = nums.some(function(n){ return !isFinite(n) || n % 1 !== 0 || n < 1 || n > 99; });
  if (nums.length < 2 || nums.length > 50 || bad) {
    msgEl.textContent = "Enter 2 to 50 whole numbers from 1 to 99, like 5, 3, 8, 1.";
    customIn.focus();
    return;
  }
  sizeIn.value = Math.max(5, nums.length); sizeOut.textContent = nums.length;
  setBars(nums);
}
document.getElementById("sv-use").addEventListener("click", useCustom);
customIn.addEventListener("keydown", function(e){ if (e.key === "Enter") useCustom(); });

showAbout();
setBars(randomBars(parseInt(sizeIn.value, 10)));
