import {
    log
} from "@/analytics/logger";


export function initNav() {
  const burger = document.getElementById("mobile-menu");
  const menu   = document.querySelector(".nav__menu");
  if (!burger || !menu) return;


  burger.addEventListener("click", () => {
    const open = !menu.classList.contains("active");
    menu.classList.toggle("active", open);
    burger.classList.toggle("is-active", open);
    burger.setAttribute("aria-expanded", String(open));
    log(open ? "nav_menu_open" : "nav_menu_close");
  });


  document.addEventListener("click", (e) => {
    const inside = (e.target as Element | null)?.closest(".nav__menu, #mobile-menu");
    if (!inside && menu.classList.contains("active")) {
      menu.classList.remove("active");
      burger.classList.remove("is-active");
      burger.setAttribute("aria-expanded", "false");
    }
  });


  document.querySelectorAll<HTMLButtonElement>("[data-toggle='submenu']").forEach((btn) => {
    btn.addEventListener("click", () => {
      const expanded = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", String(!expanded));
      btn.closest(".nav__item")?.querySelector(".nav__submenu")?.classList.toggle("open", !expanded);
    });
  });
}
