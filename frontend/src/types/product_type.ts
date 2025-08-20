import type { ProductCategory } from "@/types/categories";  


export interface ProductType {
    id: string;
    name: string;
    category: ProductCategory;
}