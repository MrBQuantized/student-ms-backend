// ---------- Wrap everything in DOMContentLoaded ----------
document.addEventListener("DOMContentLoaded", () => {
  // ---------- Elements ----------
  const sidebar = document.getElementById("sidebar");
  const sidebarToggle = document.getElementById("sidebarToggle");
  const menuBtn = document.getElementById("menuBtn");

  // ---------- Sidebar: restore saved state ----------
  const savedCollapsed = localStorage.getItem("sideCollapsed") === "true";
  if (savedCollapsed && window.innerWidth > 768) {
    sidebar.classList.add("collapsed");
  }

  // ---------- Sidebar toggle (Mobile & Desktop) ----------
  function toggleSidebar() {
    // ON mobile → slide in/out
    if (window.innerWidth <= 768) {
      sidebar.classList.toggle("open");
    } else {
      // On desktop → collapse/expand
      sidebar.classList.toggle("collapsed");
      localStorage.setItem(
        "sidebarCollapsed",
        sidebar.classList.contains("collapsed"),
      );
    }
  }

  // ---------- Wire up Both buttons ----------
  sidebarToggle.addEventListener("click", toggleSidebar);
  menuBtn.addEventListener("click", toggleSidebar);

  // ---------- Nav routing (hash-based) ----------
  const navItems = document.querySelectorAll(".nav-item");
  const sections = document.querySelectorAll(".page-section");
  const pageTitle = document.getElementById("pageTitle");

  /* Map id → pretty title */
  const TITLES = {
    home: "Home",
    dashboard: "Dashboard",
    students: "Students",
    courses: "Courses",
    departments: "Departments",
    grades: "Grades",
    enrollments: "Enrollments",
    reports: "Reports",
  };

  /* ---- Core: show only one section ---- */
  function showSection(id) {
    // If id is invalid fallback to home
    if (!TITLES[id]) id = "home";

    // Toggle section visibility
    sections.forEach((sec) => {
      sec.classList.toggle("active", sec.id === id);
    });

    // Toggle active nav state
    navItems.forEach((item) => {
      const href = item.getAttribute("href")?.replace("/", "");
      item.classList.toggle("active", href === id);
    });

    // Update topbar title
    if (pageTitle) pageTitle.textContent = TITLES[id];

    // Update URL hash without jumping
    if (location.hash !== `#${id}`) {
      history.replaceState(null, "", `#${id}`);
    }
  }

  /* ---- Click handler ---- */
  navItems.forEach((item) => {
    item.addEventListener("click", (e) => {
      e.preventDefault(); // ← stops browser default hash jump
      const id = item.getAttribute("href").replace("/", "");
      showSection(id);

      // Close sidebar on mobile after click
      document.getElementById("sidebar")?.classList.remove("open");
    });
  });

  /* ---- On page load: read hash and show correct section ---- */
  window.addEventListener("DOMContentLoaded", () => {
    const initial = location.hash.replace("#", "") || "home";
    showSection(initial);
  });

  /* ---- On back/forward buttons ---- */
  window.addEventListener("hashchange", () => {
    const id = location.hash.replace("#", "") || "home";
    showSection(id);
  });
});
