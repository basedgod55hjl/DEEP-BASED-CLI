document.getElementById('runBtn').addEventListener('click', runCommand);
document.getElementById('commandInput').addEventListener('keyup', (e) => {
    if (e.key === 'Enter') runCommand();
});

async function runCommand() {
    const input = document.getElementById('commandInput');
    const cmd = input.value.trim();
    if (!cmd) return;

    const res = await fetch('/cli/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: cmd })
    });

    const data = await res.json();
    const output = document.getElementById('output');
    const prefix = `\n$ ${cmd}\n`;
    if (data.error) {
        output.textContent += prefix + data.error;
    } else {
        output.textContent += prefix + data.output;
    }
    output.scrollTop = output.scrollHeight;
    input.value = '';
}
