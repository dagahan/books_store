import { initNav } from "@/ui/nav";
import { initAuthModal } from "@/ui/auth-modal";
import { Logger, log } from "@/analytics/logger";
import { API_BASE } from "@/api/client";


document.addEventListener("DOMContentLoaded", () => {
    Logger.i.init({
        getAccessToken: () => localStorage.getItem("bs_access"),
    });

    log("page_view", {
        message: "Vite dev boot",
        mode: import.meta.env.MODE,
        api_base: API_BASE,
    })

    initNav();
    initAuthModal();
});
