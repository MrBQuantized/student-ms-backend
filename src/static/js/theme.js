const themeToggle = document.getElementById("themeToggle");
const themeMenu = document.getElementById("themeMenu");
const systemTheme = window.matchMedia("(prefers-color-scheme: dark)");
const root = document.documentElement;

// ---------- Theme Toggle ----------
function applyTheme(preference) {
  // Decide which theme to apply
  if (preference === "auto") {
    root.removeAttribute("data-theme"); // remove "data-theme" when preference is "auto"
  } else {
    root.dataset.theme = preference; // otherwise, set attribute to preference
  }

  // Appearance is "dark" is user selects "dark" explicitly or
  // if the user selected "auto" and their system prefers dark mode
  const isDark =
    preference === "dark" || (preference === "auto" && systemTheme.matches);

  // Switch icons — the "moon" icon is displayed when theme is "dark",
  // otherwise, "sun" icon is displayed
  themeToggle.querySelector(".sun").style.display = isDark ? "none" : "block";
  themeToggle.querySelector(".moon").style.display = isDark ? "block" : "none";

  // Update the accessible label
  themeToggle.setAttribute(
    "aria-label",
    `Theme settings. Current mode: ${preference}`,
  );
}

// Load the saved preference
// Retrieve the saved theme. if no saved value exists, use "auto".
let savedTheme = localStorage.getItem("theme") || "auto";

// Validate the saved value — If saved value isn't one of the permitted themes
// fall back to auto
if (!["light", "dark", "auto"].includes(savedTheme)) {
  savedTheme = "auto";
}
applyTheme(savedTheme); // apply the preference when the page loads

// Open and close the theme menu
themeToggle.addEventListener("click", () => {
  const isOpen = !themeMenu.hidden;

  // If themeMenu is visible (open), it becomes hidden.
  // If it was closed, it becomes visible
  themeMenu.hidden = isOpen;

  // update the accessible state to reflect whether the menu is open
  // String() converts the Boolean into strings "true" or "false"
  themeToggle.setAttribute("aria-expanded", String(!isOpen));
});

// Handle the user's theme selection
// We listen on the parent menu instead of having a click listener for each option
themeMenu.addEventListener("click", (event) => {
  const button = event.target.closest("[data-theme-choice]");

  // If no option was clicked, stop the function.
  if (!button) return;

  // set the savedTheme to the option clicked by user.
  savedTheme = button.dataset.themeChoice;

  // save and apply the choice/option
  localStorage.setItem("theme", savedTheme);
  applyTheme(savedTheme);

  //  Close the menu after a user makes a selection
  themeMenu.hidden = true;
  themeToggle.setAttribute("aria-expanded", "false");
});

// Detect changes to the operating system's theme
systemTheme.addEventListener("change", () => {
  if (savedTheme === "auto") {
    applyTheme("auto");
  }
});

// Close the menu when clicking outside it
document.addEventListener("click", (event) => {
  // If the click happened outside .theme-control, the menu stays open
  // otherwise, menu closes
  if (!event.target.closest(".theme-control")) {
    themeMenu.hidden = true;

    themeToggle.setAttribute("aria-expanded", "false");
  }
});
