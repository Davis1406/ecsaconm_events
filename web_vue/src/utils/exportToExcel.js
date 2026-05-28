import * as XLSX from "xlsx";
import { saveAs } from "file-saver";
import Swal from "sweetalert2";

export function exportToExcel(data, filename) {
  if (!data || !data.length) {
    Swal.fire({
      icon: "error",
      title: "No Data",
      text: "No data provided for export.",
      confirmButtonText: "OK",
    });
    return;
  }

  const worksheet = XLSX.utils.json_to_sheet(data);
  const headers = Object.keys(data[0]);
  headers.forEach((header, index) => {
    const cellAddress = XLSX.utils.encode_cell({ r: 0, c: index });
    if (!worksheet[cellAddress]) {
      worksheet[cellAddress] = {
        v: header.toUpperCase(),
        s: { font: { bold: true } },
      };
    } else {
      worksheet[cellAddress].v = header.toUpperCase(); // Capitalize headers
      worksheet[cellAddress].s = { font: { bold: true } }; // Make headers bold
    }
  });

  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, "Participants");
  const wbout = XLSX.write(workbook, { bookType: "xlsx", type: "binary" });
  const buffer = new ArrayBuffer(wbout.length);
  const view = new Uint8Array(buffer);
  for (let i = 0; i < wbout.length; ++i) {
    view[i] = wbout.charCodeAt(i) & 0xff;
  }

  saveAs(
    new Blob([buffer], { type: "application/octet-stream" }),
    `${filename}.xlsx`
  );
}
