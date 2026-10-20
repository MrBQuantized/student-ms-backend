const searchInput = document.querySelector("#studentSearch");
const studentsTable = document.querySelector("#studentsTable");
const noSearchResults = document.querySelector("#noSearchResults");

if (searchInput && studentsTable && noSearchResults) {
  const studentRows = studentsTable.querySelectorAll("tbody tr");

  searchInput.addEventListener("input", () => {
    const query = searchInput.value.trim().toLowerCase();
    let visibleCount = 0;

    studentRows.forEach((row) => {
      // ignore the initial "no students" placeholder row.
      if (row.querySelectorAll("td").lenght === 1) {
        return;
      }

      const matches = row.textContent.toLowerCase().includes(query);

      row.hidden = !matches;

      if (matches) {
        visibleCount++;
      }
    });

    noSearchResults.hidden = visibleCount > 0 || query === "";
  });
}
