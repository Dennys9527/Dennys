const modeLabel = document.getElementById('modeLabel');
const timeDisplay = document.getElementById('timeDisplay');
const statusText = document.getElementById('statusText');

const startBtn = document.getElementById('startBtn');
const pauseBtn = document.getElementById('pauseBtn');
const resetBtn = document.getElementById('resetBtn');
const applyBtn = document.getElementById('applyBtn');

const workInput = document.getElementById('workInput');
const breakInput = document.getElementById('breakInput');

let workMinutes = 25;
let breakMinutes = 5;
let isWorkMode = true;
let remainingSeconds = workMinutes * 60;
let timerId = null;

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60)
    .toString()
    .padStart(2, '0');
  const secs = (seconds % 60).toString().padStart(2, '0');
  return `${mins}:${secs}`;
}

function render() {
  modeLabel.textContent = isWorkMode ? '專注時間' : '休息時間';
  timeDisplay.textContent = formatTime(remainingSeconds);
}

function syncButtons(isRunning) {
  startBtn.disabled = isRunning;
  pauseBtn.disabled = !isRunning;
}

function switchMode() {
  isWorkMode = !isWorkMode;
  remainingSeconds = (isWorkMode ? workMinutes : breakMinutes) * 60;
  statusText.textContent = isWorkMode ? '休息結束，回到專注！' : '做得好，休息一下吧！';
}

function tick() {
  if (remainingSeconds > 0) {
    remainingSeconds -= 1;
    render();
    return;
  }

  switchMode();
  render();
}

function startTimer() {
  if (timerId) return;
  timerId = window.setInterval(tick, 1000);
  syncButtons(true);
  statusText.textContent = '計時中...保持專注！';
}

function pauseTimer() {
  if (!timerId) return;
  clearInterval(timerId);
  timerId = null;
  syncButtons(false);
  statusText.textContent = '已暫停。準備好再繼續！';
}

function resetTimer() {
  pauseTimer();
  isWorkMode = true;
  remainingSeconds = workMinutes * 60;
  render();
  statusText.textContent = '已重設為專注時間。';
}

function applySettings() {
  const nextWork = Number(workInput.value);
  const nextBreak = Number(breakInput.value);

  if (!Number.isInteger(nextWork) || !Number.isInteger(nextBreak) || nextWork <= 0 || nextBreak <= 0) {
    statusText.textContent = '請輸入有效的分鐘數（正整數）。';
    return;
  }

  workMinutes = nextWork;
  breakMinutes = nextBreak;
  resetTimer();
  statusText.textContent = `已套用：專注 ${workMinutes} 分鐘、休息 ${breakMinutes} 分鐘。`;
}

startBtn.addEventListener('click', startTimer);
pauseBtn.addEventListener('click', pauseTimer);
resetBtn.addEventListener('click', resetTimer);
applyBtn.addEventListener('click', applySettings);

render();
