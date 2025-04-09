export interface ApiRecipe {
  recipe_id: string;
  title: string;
  image_url: string;
  instructions: string;
  dietary_tags?: string[];
  isFavorite: boolean;
}

export interface ApiIngredient {
  ingredient_id: string;
  name: string;
  category: string;
  image_url?: string;
  isTracked: boolean;
}

export interface ApiResponse<T> {
  data: T[];
}