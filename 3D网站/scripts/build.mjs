import { mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';

const html = readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const output = new URL('../dist/server/index.js', import.meta.url);

rmSync(new URL('../dist', import.meta.url), { recursive: true, force: true });
mkdirSync(new URL('../dist/server', import.meta.url), { recursive: true });
writeFileSync(output, `const page = ${JSON.stringify(html)};

export default {
  async fetch() {
    return new Response(page, {
      headers: {
        'content-type': 'text/html; charset=UTF-8',
        'cache-control': 'public, max-age=300'
      }
    });
  }
};
`);
