import { apiFetch } from "@/api/client";


export interface CatalogCategoriesResponse {
  categories: string[]
}


export const CategoriesApi = {
  async getCategories(): Promise<string[]> {
    const res = await apiFetch<CatalogCategoriesResponse>("catalog/categories");
    return res.categories ?? [];
  },
};

