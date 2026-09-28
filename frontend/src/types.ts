export interface SizeStock {
  size: string;
  quantity: number;
  in_stock: boolean;
  low_stock: boolean;
}

export interface Product {
  product_id: string;
  name: string;
  garment_type: string;
  description: string;
  colors: string[];
  search_tags?: string[];
  image_file_path: string;
  image_url: string;
  price: number;
  inventory: SizeStock[];
  total_stock: number;
}

export interface Shopper {
  id: number;
  first_name: string;
  last_name: string;
  name: string;
  email: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  products?: Product[];
}
