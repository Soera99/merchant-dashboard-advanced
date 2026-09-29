import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "C:/Users/fazaa/Downloads/Advanced Dashboard.xlsx";
const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);

const summary = await workbook.inspect({
  kind: "workbook,sheet,table,drawing",
  maxChars: 16000,
  tableMaxRows: 12,
  tableMaxCols: 16,
  tableMaxCellChars: 120,
});
console.log(summary.ndjson);

const first = workbook.worksheets.getItemAt(0);
const used = first.getUsedRange();
console.log(JSON.stringify({ firstSheet: first.name, usedAddress: used?.address ?? null }));

const region = await workbook.inspect({
  kind: "region",
  sheetId: first.name,
  range: used?.address ?? "A1:Z100",
  maxChars: 30000,
  tableMaxRows: 100,
  tableMaxCols: 30,
  tableMaxCellChars: 160,
});
console.log(region.ndjson);

await fs.mkdir("workbook_inspection", { recursive: true });
const preview = await workbook.render({
  sheetName: first.name,
  autoCrop: "all",
  scale: 1,
  format: "png",
});
await fs.writeFile("workbook_inspection/sheet1.png", new Uint8Array(await preview.arrayBuffer()));
