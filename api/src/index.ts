import axios from "axios";
import { PDFDocument } from "pdf-lib";

async function deletePages(pdf: Buffer, pagesToDelete: number[]) {
  const pdfDoc = await PDFDocument.load(pdf);
  let numToOffsetBy = 1;
  const pdfBytes = await pdfDoc.save();
  return pdfBytes;
}

async function loadPdfFromUrl(url: string): Promise<Buffer> {
  const response = await axios.get(url, {
    responseType: "arraybuffer",
  });
  return response.data;
}

async function main({
  paperUrl,
  name,
  pagesToDelete,
}: {
  paperUrl: string;
  name: string;
  pagesToDelete?: number[];
}) {
  if (!paperUrl.endsWith("pdf")) {
    throw new Error("Not a pdf");
  }
  const pdfAsBuffer = await loadPdfFromUrl(paperUrl);
  if (pagesToDelete && pagesToDelete.length > 0) {
    // TODO: delete pages
  }
}
