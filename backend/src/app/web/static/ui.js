/**
 * UI components
 * Handles UI state management and interactions (theme mode + snackbar).
 */

document.addEventListener("alpine:init", () => {
  Alpine.store("settings", {
    currentMode: localStorage.getItem("mode") || "light",
    currentTheme: localStorage.getItem("theme") || "",

    async toggleMode() {
      this.currentMode = this.currentMode === "light" ? "dark" : "light";
      localStorage.setItem("mode", this.currentMode);
      await ui("mode", this.currentMode);
    },

    async toggleTheme(theme) {
      await ui("theme", theme);
      localStorage.setItem("theme", theme);
    },

    toggleNavbar() {
      this.showNavbar = !this.showNavbar;
    },

    async init() {
      // apply persisted mode on load
      await ui("mode", this.currentMode);
    },
  });

  Alpine.data("snackbar", () => ({
    snackbarVisible: false,
    snackbarMessage: "",
    snackbarType: "success",
    snackbarTimeout: null, // Store the timeout ID

    displaySnackbar(message, type = "primary") {
      // if no message is defined
      if (!message) {
        message = "Unknown error";
      }

      // Clear any existing timeout to reset the timer
      if (this.snackbarTimeout) {
        clearTimeout(this.snackbarTimeout);
      }

      this.snackbarVisible = true;
      this.snackbarMessage = message;
      this.snackbarType = type;
      this.snackbarTimeout = setTimeout(() => {
        this.clearSnackbar();
      }, 3000);
    },

    clearSnackbar() {
      this.snackbarVisible = false;
      this.snackbarMessage = "";
    },
  }));
});
