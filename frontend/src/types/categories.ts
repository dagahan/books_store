export type ProductCategory =
  | "fiction"
  | "nonfiction"
  | "business_economics"
  | "science_technology"
  | "self_help"
  | "psychology"
  | "history"
  | "biography_memoir"
  | "children"
  | "young_adult"
  | "fantasy"
  | "science_fiction"
  | "mystery_thriller"
  | "romance"
  | "comics_manga"
  | "art_photography"
  | "cookbooks_food"
  | "health_fitness"
  | "education_teaching"
  | "travel";


export const PRODUCT_CATEGORIES: { key: ProductCategory; label: string }[] = [
  { key: "fiction", label: "Fiction" },
  { key: "nonfiction", label: "Non-fiction" },
  { key: "business_economics", label: "Business & Economics" },
  { key: "science_technology", label: "Science & Technology" },
  { key: "self_help", label: "Self-Help" },
  { key: "psychology", label: "Psychology" },
  { key: "history", label: "History" },
  { key: "biography_memoir", label: "Biography & Memoir" },
  { key: "children", label: "Children" },
  { key: "young_adult", label: "Young Adult" },
  { key: "fantasy", label: "Fantasy" },
  { key: "science_fiction", label: "Science Fiction" },
  { key: "mystery_thriller", label: "Mystery & Thriller" },
  { key: "romance", label: "Romance" },
  { key: "comics_manga", label: "Comics & Manga" },
  { key: "art_photography", label: "Art & Photography" },
  { key: "cookbooks_food", label: "Cookbooks & Food" },
  { key: "health_fitness", label: "Health & Fitness" },
  { key: "education_teaching", label: "Education & Teaching" },
  { key: "travel", label: "Travel" },
];


export const CATEGORY_LABELS: Record<ProductCategory, string> =
  Object.fromEntries(PRODUCT_CATEGORIES.map(c => [c.key, c.label])) as Record<ProductCategory, string>;

