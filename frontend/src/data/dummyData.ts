/* =========================
   TYPES
   ========================= */

export type MarketType = "Wholesale" | "Retail" | "Local Mandi";

export type Market = {
  id: string;
  name: string;
  city: string;
  state: string;
  type: MarketType;
};

export type ProductCategory =
  | "Vegetables"
  | "Fruits"
  | "Grains"
  | "Pulses";

export type Product = {
  id: string;
  name: string;
  category: ProductCategory;
};

/* =========================
   MARKETS (UNCHANGED)
   ========================= */

export const markets: Market[] = [
  {
    id: "m1",
    name: "APMC Vashi",
    city: "Mumbai",
    state: "Maharashtra",
    type: "Wholesale",
  },
  {
    id: "m2",
    name: "Dadar Market",
    city: "Mumbai",
    state: "Maharashtra",
    type: "Retail",
  },
  {
    id: "m3",
    name: "Pune Mandi",
    city: "Pune",
    state: "Maharashtra",
    type: "Local Mandi",
  },
  {
    id: "m4",
    name: "Azadpur Mandi",
    city: "Delhi",
    state: "Delhi",
    type: "Wholesale",
  },
];

/* =========================
   PRODUCTS (EXTENDED)
   ========================= */

export const products: Product[] = [
  // Vegetables
  { id: "p1", name: "Tomato", category: "Vegetables" },
  { id: "p2", name: "Onion", category: "Vegetables" },
  { id: "p3", name: "Potato", category: "Vegetables" },
  { id: "p4", name: "Cauliflower", category: "Vegetables" },

  // Fruits
  { id: "p5", name: "Apple", category: "Fruits" },
  { id: "p6", name: "Banana", category: "Fruits" },
  { id: "p7", name: "Orange", category: "Fruits" },

  // Grains
  { id: "p8", name: "Rice", category: "Grains" },
  { id: "p9", name: "Wheat", category: "Grains" },

  // Pulses
  { id: "p10", name: "Toor Dal", category: "Pulses" },
  { id: "p11", name: "Chana Dal", category: "Pulses" },
];

/* =========================
   FESTIVALS (UNCHANGED)
   ========================= */

export const festivals = [
  { name: "Ganesh Chaturthi", daysAway: 6 },
  { name: "Navratri", daysAway: 18 },
];

/* =========================
   WEATHER CONTEXT (UNCHANGED)
   ========================= */

export const weatherContext = {
  summary: "Moderate rainfall expected",
  impact: "High",
};
