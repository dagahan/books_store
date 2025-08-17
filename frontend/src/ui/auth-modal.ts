import { AuthApi } from "@/api/auth";
import type { RegisterResponse } from "@/types/register";

const phoneDigits = (s: string) => (s ?? "").replace(/\D+/g, "");

export function initAuthModal() {
  const dialog = document.getElementById("authDialog") as HTMLDialogElement | null;
  const form   = document.getElementById("authForm") as HTMLFormElement | null;
  const open   = document.getElementById("openAuth") as HTMLButtonElement | null;
  const close  = dialog?.querySelector(".auth__close") as HTMLButtonElement | null;
  const title  = document.getElementById("authTitle") as HTMLHeadingElement | null;
  const errorP = form?.querySelector(".auth__error") as HTMLParagraphElement | null;
  const viewLogin    = form?.querySelector<HTMLElement>('.auth__view[data-view="login"]');
  const viewRegister = form?.querySelector<HTMLElement>('.auth__view[data-view="register"]');

  let view: "login" | "register" = "login";

  const setError = (msg?: string) => {
    if (!errorP) return;
    errorP.hidden = !msg;
    errorP.textContent = msg ?? "";
  };

  const switchView = (v: "login" | "register") => {
    view = v;
    title && (title.textContent = v === "register" ? "Регистрация" : "Войти");
    viewLogin?.classList.toggle("is-hidden", v !== "login");
    viewRegister?.classList.toggle("is-hidden", v !== "register");
    setError();
  };

  open?.addEventListener("click", () => { switchView("login"); dialog?.showModal(); });
  close?.addEventListener("click", () => dialog?.close());
  form?.querySelectorAll<HTMLButtonElement>(".auth__swap [data-go]").forEach(btn =>
    btn.addEventListener("click", () => switchView((btn.dataset.go as any) || "login"))
  );

  form?.addEventListener("submit", async (e) => {
    e.preventDefault();
    setError();

    if (view !== "register") {
      setError("Вход пока не реализован. Переключитесь на «Регистрация».");
      return;
    }

    // берём поля только из view=register
    const scope = viewRegister!;
    const get = (name: string) =>
      scope.querySelector<HTMLInputElement>(`[name="${name}"]`)?.value.trim() ?? "";

    const payload = {
      user_name:   get("user_name"),
      password:    get("password"),
      first_name:  get("first_name"),
      last_name:   get("last_name"),
      middle_name: get("middle_name"),
      phone:       phoneDigits(get("phone")),
      dsh:         get("dsh") || "true test dsh is in backend."
    };

    try {
      const data: RegisterResponse = await AuthApi.register(payload);
      console.log("Registered", data);
      alert("Регистрация успешна!");
      dialog?.close();
    } catch (err: any) {
      const msg =
        err?.body?.detail?.length
          ? `Validation failed: ${err.body.detail.map((d: any) => `${d.loc?.join(".")}: ${d.msg}`).join("; ")}`
          : err?.message || "Не удалось отправить форму";
      setError(msg);
      console.error(err);
    }
  });
}
