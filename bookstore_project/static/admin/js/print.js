function exportReportToExcel() {
    // Get the table element
    const table = document.querySelector("#orderTable table");

    if (table) {
        // Convert the table to a workbook
        const workbook = XLSX.utils.table_to_book(table);

        // Convert the workbook to a binary Excel file
        const excelBinary = XLSX.write(workbook, { bookType: "xlsx", type: "binary" });

        // Create a Blob object and download the file
        const blob = new Blob([s2ab(excelBinary)], { type: "application/octet-stream" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "salesReport.xlsx";
        link.click();
    } else {
        console.log("Table element not found.");
    }

    // Utility function to convert a string to an ArrayBuffer
    function s2ab(s) {
        const buf = new ArrayBuffer(s.length);
        const view = new Uint8Array(buf);
        for (let i = 0; i < s.length; i++) {
            view[i] = s.charCodeAt(i) & 0xff;
        }
        return buf;
    }
}


function printTable() {
    // Get the table element
    var table = document.querySelector("#orderTable table");

    if (table) {
        // Create a new window for printing
        var newWin = window.open('', 'Print-Window');
        newWin.document.open();

        // Add necessary CSS styles for the table
        newWin.document.write('<html><head><style>');
        newWin.document.write('table { border-collapse: collapse; width: 100%; }');
        newWin.document.write('table, th, td { border: 1px solid black; }');
        newWin.document.write('</style></head><body onload="window.print()">');

        // Write the table HTML
        newWin.document.write(table.outerHTML);

        newWin.document.write('</body></html>');
        newWin.document.close();

        setTimeout(function () { newWin.close(); }, 10);
    } else {
        console.log("Table element not found.");
    }
}

// sort table

function exportSortReportToExcel() {
    // Get the table element
    const table = document.querySelector("#sortTable");

    if (table) {
        // Convert the table to a workbook
        const workbook = XLSX.utils.table_to_book(table);

        // Convert the workbook to a binary Excel file
        const excelBinary = XLSX.write(workbook, { bookType: "xlsx", type: "binary" });

        // Create a Blob object and download the file
        const blob = new Blob([s2ab(excelBinary)], { type: "application/octet-stream" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "salesReport.xlsx";
        link.click();
    } else {
        console.log("Table element not found.");
    }

    // Utility function to convert a string to an ArrayBuffer
    function s2ab(s) {
        const buf = new ArrayBuffer(s.length);
        const view = new Uint8Array(buf);
        for (let i = 0; i < s.length; i++) {
            view[i] = s.charCodeAt(i) & 0xff;
        }
        return buf;
    }
}

function printsortTable() {
    // Get the table element
    var table = document.querySelector("#sortTable");

    if (table) {
        // Create a new window for printing
        var newWin = window.open('', 'Print-Window');
        newWin.document.open();

        // Add necessary CSS styles for the table
        newWin.document.write('<html><head><style>');
        newWin.document.write('table { border-collapse: collapse; width: 100%; }');
        newWin.document.write('table, th, td { border: 1px solid black; }');
        newWin.document.write('</style></head><body onload="window.print()">');

        // Write the table HTML
        newWin.document.write(table.outerHTML);

        newWin.document.write('</body></html>');
        newWin.document.close();

        setTimeout(function () { newWin.close(); }, 10);
    } else {
        console.log("Table element not found.");
    }
}


//cancel table

function exportCancelTable() {
    // Get the table element
    const table = document.querySelector("#customTable");

    if (table) {
        // Convert the table to a workbook
        const workbook = XLSX.utils.table_to_book(table);

        // Convert the workbook to a binary Excel file
        const excelBinary = XLSX.write(workbook, { bookType: "xlsx", type: "binary" });

        // Create a Blob object and download the file
        const blob = new Blob([s2ab(excelBinary)], { type: "application/octet-stream" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "salesReport.xlsx";
        link.click();
    } else {
        console.log("Table element not found.");
    }

    // Utility function to convert a string to an ArrayBuffer
    function s2ab(s) {
        const buf = new ArrayBuffer(s.length);
        const view = new Uint8Array(buf);
        for (let i = 0; i < s.length; i++) {
            view[i] = s.charCodeAt(i) & 0xff;
        }
        return buf;
    }
}

function printcancelTable() {
    // Get the table element
    var table = document.querySelector("#customTable");

    if (table) {
        // Create a new window for printing
        var newWin = window.open('', 'Print-Window');
        newWin.document.open();

        // Add necessary CSS styles for the table
        newWin.document.write('<html><head><style>');
        newWin.document.write('table { border-collapse: collapse; width: 100%; }');
        newWin.document.write('table, th, td { border: 1px solid black; }');
        newWin.document.write('</style></head><body onload="window.print()">');

        // Write the table HTML
        newWin.document.write(table.outerHTML);

        newWin.document.write('</body></html>');
        newWin.document.close();

        setTimeout(function () { newWin.close(); }, 10);
    } else {
        console.log("Table element not found.");
    }
}