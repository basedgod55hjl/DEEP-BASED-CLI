const consoleEl = document.getElementById('console');

function appendOutput(text) {
  const pre = document.createElement('pre');
  pre.textContent = text;
  consoleEl.appendChild(pre);
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

async function runCommand(cmd) {
  const res = await fetch(`/api/run?cmd=${encodeURIComponent(cmd)}`);
  const data = await res.json();
  if (data.error) {
    appendOutput(`Error: ${data.error}`);
  } else {
    appendOutput(data.output);
  }
}

document.getElementById('runBtn').addEventListener('click', () => {
  const cmd = document.getElementById('commandInput').value;
  if (cmd) {
    runCommand(cmd);
  }
});

document.querySelectorAll('#sidebar button').forEach((btn) => {
  btn.addEventListener('click', () => {
    runCommand(btn.dataset.cmd);
  });
});
