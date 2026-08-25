import * as pdfjs from 'pdfjs-dist/legacy/build/pdf.mjs'
import { readFile } from 'node:fs/promises'

class DOMMatrix {
  constructor(init) {
    if (init) {
      this.a = init[0]; this.b = init[1]; this.c = init[2]
      this.d = init[3]; this.e = init[4]; this.f = init[5]
    } else { this.a = 1; this.b = 0; this.c = 0; this.d = 1; this.e = 0; this.f = 0 }
  }
  static fromMatrix() { return new DOMMatrix() }
  static fromFloat32Array() { return new DOMMatrix() }
}
globalThis.DOMMatrix = DOMMatrix

const file = process.argv[2]
const data = new Uint8Array(await readFile(file))
try {
  const doc = await pdfjs.getDocument({
    data,
    disableWorker: true,
    isEvalSupported: false,
  }).promise
  console.log('OK pages:', doc.numPages)
  const page = await doc.getPage(1)
  console.log('page1 viewport size ok:', page.view.length === 4)
  await doc.destroy()
  console.log('RESULT: SUCCESS')
} catch (e) {
  console.log('FAIL:', e?.name, '|', e?.message)
  console.log((e?.stack || '').split('\n').slice(0, 4).join('\n'))
  console.log('RESULT: FAIL')
}
