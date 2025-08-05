document.getElementById('runBtn').addEventListener('click', runCommand);
document.getElementById('clearBtn').addEventListener('click', () => {
    document.getElementById('output').textContent = '';
});
document.getElementById('stopBtn').addEventListener('click', async () => {
    await fetch('/cli/stop', { method: 'POST' });
    const output = document.getElementById('output');
    output.textContent += '\n[Process terminated]\n';
    output.scrollTop = output.scrollHeight;
});
document.getElementById('commandInput').addEventListener('keyup', (e) => {
    if (e.key === 'Enter') runCommand();
});

async function runCommand() {
    const input = document.getElementById('commandInput');
    const cmd = input.value.trim();
    if (!cmd) return;
    const output = document.getElementById('output');
    const prefix = `\n$ ${cmd}\n`;

    try {
        const res = await fetch('/cli/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: cmd })
        });

        const data = await res.json();
        if (data.error) {
            output.textContent += prefix + data.error;
        } else {
            output.textContent += prefix + data.output;
        }
    } catch (err) {
        output.textContent += prefix + err.message;
    }

    output.scrollTop = output.scrollHeight;
    input.value = '';
}
