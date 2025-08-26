import { CategoriesApi } from "@/api/categories";
import { labelizeCategory } from "@/core/utils";

export function initNav() {
  const burger = document.getElementById("mobile-menu");
  const menu   = document.querySelector(".nav__menu");
  if (!burger || !menu) return;

  burger.addEventListener("click", () => {
    const open = !menu.classList.contains("active");
    menu.classList.toggle("active", open);
    burger.classList.toggle("is-active", open);
    burger.setAttribute("aria-expanded", String(open));
  });

  document.addEventListener("click", (e) => {
    const inside = (e.target as Element | null)?.closest(".nav__menu, #mobile-menu");
    if (!inside && menu.classList.contains("active")) {
      menu.classList.remove("active");
      burger.classList.remove("is-active");
      burger.setAttribute("aria-expanded", "false");
    }
  });

  // раскрывашка "Catalog" (нужна кнопка с data-toggle="submenu" в HTML — см. ниже)
  document.querySelectorAll<HTMLButtonElement>("[data-toggle='submenu']").forEach((btn) => {
    btn.addEventListener("click", () => {
      const expanded = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", String(!expanded));
      btn.closest(".nav__item")?.querySelector(".nav__submenu")?.classList.toggle("open", !expanded);
    });
  });
}

/** тянем категории с бэка и рисуем их в меню и чипсах */
export async function renderCategoriesEverywhere() {
  const all = await CategoriesApi.getCategories();             // ["fiction", ...]
  const labels = all.map(k => ({ key: k, label: labelizeCategory(k) }));

  // ВЫПАДАЮЩЕЕ МЕНЮ (все категории)
  const submenu = document.querySelector(".nav__submenu");
  if (submenu) {
    submenu.innerHTML = labels
      .map(
        ({ key, label }) =>
          `<a href="/catalog?category=${encodeURIComponent(key)}" role="menuitem">${label}</a>`
      )
      .join("");
  }

  // ЧИПСЫ НА ГЛАВНОЙ (первые 8)
  const chipsRow = document.querySelector(".chips__row");
  if (chipsRow) {
    chipsRow.innerHTML = labels.slice(0, 8)
      .map(
        ({ key, label }) =>
          `<a class="chip" role="listitem" href="/catalog?category=${encodeURIComponent(key)}">${label}</a>`
      )
      .join("");
  }
}