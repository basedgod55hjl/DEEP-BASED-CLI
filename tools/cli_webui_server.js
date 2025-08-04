import { createServer } from 'http';
import { execFile } from 'child_process';
import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';
import { URL } from 'url';

const PORT = process.env.PORT || 3002;
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function sendFile(res, filePath, contentType = 'text/html') {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end('Not found');
      return;
    }
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(data);
  });
}

const server = createServer((req, res) => {
  const reqUrl = new URL(req.url, `http://localhost:${PORT}`);
  if (reqUrl.pathname === '/api/run') {
    const cmd = reqUrl.searchParams.get('cmd');
    if (!cmd) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'cmd parameter required' }));
      return;
    }
    const args = cmd.split(' ');
    const binary = path.join(__dirname, 'cli_bridge');
    execFile(binary, args, { cwd: path.join(__dirname, '..') }, (err, stdout, stderr) => {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      if (err) {
        res.end(JSON.stringify({ error: stderr.toString() || err.message }));
        return;
      }
      res.end(JSON.stringify({ output: stdout }));
    });
    return;
  }

  const filePath = path.join(
    __dirname,
    'webui',
    reqUrl.pathname === '/' ? 'index.html' : reqUrl.pathname
  );
  const ext = path.extname(filePath);
  const contentType =
    ext === '.html'
      ? 'text/html'
      : ext === '.js'
      ? 'application/javascript'
      : ext === '.css'
      ? 'text/css'
      : 'text/plain';
  sendFile(res, filePath, contentType);
});

server.listen(PORT, () => {
  console.log(`CLI WebUI running at http://localhost:${PORT}`);
});
