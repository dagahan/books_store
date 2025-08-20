import { apiFetch } from "@/api/client";
import type { ProductCategory } from "@/types/categories";
import type { ProductType } from "@/types/product_type";


export const ProductTypesApi = {
    list(params? : { categories?: ProductCategory[]; limit?: number; offset?: number}) {
        const qs = new URLSearchParams();
        params?.categories?.forEach((c) => qs.append("categories", c));
        
        if (params?.limit) qs.set("limit", String(params.limit));
        if (params?.offset) qs.set("offset", String(params.offset));
        const suffix = qs.toString() ? '?${qs}' : "";

        return apiFetch<ProductType[]>('product-types${suffix}');
    }
}

