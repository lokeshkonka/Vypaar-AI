// src/components/Navbar.tsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  SignedIn,
  SignedOut,
  UserButton,
} from "@clerk/clerk-react";

import {
  FiMenu,
  FiBell,
  FiUser,
  FiBarChart2,
  FiBox,
  FiTrendingUp,
  FiActivity,
  FiChevronLeft,
} from "react-icons/fi";

import NavLoader from "./NavLoader";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <>
      {/* TOP NAVBAR */}
      <header className="
       fixed top-0 z-30 w-full
  bg-[#0f1f1b]
  border-b border-[#1f3a33]
  shadow-sm

      ">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          {/* LEFT */}
          <div className="flex items-center gap-4">
            <button
              onClick={() => setOpen(true)}
              className="cursor-pointer text-gray-200 hover:text-white transition"
            >
              <FiMenu size={22} />
            </button>

            <Link to="/home" className="flex items-center gap-2 cursor-pointer">
              <img src="/icon.png" className="h-8 w-8" />
              <span className="font-semibold text-white tracking-wide">
                Vypaar AI
              </span>
            </Link>
          </div>

          {/* CENTER */}
          <nav className="hidden md:flex items-center gap-10 text-sm text-gray-300">
            <Link to="/blog" className="hover:text-white cursor-pointer transition">
              Blog
            </Link>
            <Link to="/pricing" className="hover:text-white cursor-pointer transition">
              Pricing
            </Link>
          </nav>

          {/* RIGHT */}
          <div className="flex items-center gap-5 text-white">
            <button className="relative cursor-pointer text-gray-200 hover:text-white transition">
              <FiBell size={20} />
              <span className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-emerald-400" />
            </button>

            <SignedIn>
              <UserButton appearance={{
                elements: {
                  avatarBox:
                    "h-8 w-8 border border-white/20 rounded-full",
                },
              }} />
            </SignedIn>

            <SignedOut>
              <FiUser size={20} />
            </SignedOut>
          </div>
        </div>
      </header>

      {/* SIDE NAVBAR */}
      <NavLoader open={open}>
        <div className="flex h-full flex-col px-5 py-6">
          {/* HEADER */}
          <div className="flex items-center justify-between">
            <Link
              to="/home"
              onClick={() => setOpen(false)}
              className="flex items-center gap-2 cursor-pointer"
            >
              <img src="/icon.png" className="h-8 w-8" />
              <span className="text-lg font-semibold text-white">
                Vypaar AI
              </span>
            </Link>

            <button
              onClick={() => setOpen(false)}
              className="cursor-pointer rounded-md p-1
                text-gray-300 hover:text-white hover:bg-white/10 transition"
            >
              <FiChevronLeft size={22} />
            </button>
          </div>

          <div className="my-5 h-px bg-white/10" />

          {/* DASHBOARD NAV */}
          <div className="space-y-1">
            <SideItem
              icon={<FiBarChart2 />}
              label="Product Analysis"
              onClick={() => navigate("/dashboard/product-analysis")}
            />
            <SideItem
              icon={<FiBox />}
              label="Inventory"
              onClick={() => navigate("/dashboard/inventory")}
            />
            <SideItem
              icon={<FiTrendingUp />}
              label="Insights"
              onClick={() => navigate("/dashboard/insights")}
            />
            <SideItem
              icon={<FiActivity />}
              label="Model Accuracy"
              onClick={() => navigate("/dashboard/model-accuracy")}
            />
          </div>

          <div className="my-5 h-px bg-white/10" />

          {/* MOBILE LINKS */}
          <div className="md:hidden space-y-2">
            <Link to="/blog" onClick={() => setOpen(false)} className="block text-sm text-gray-300 hover:text-white cursor-pointer">
              Blog
            </Link>
            <Link to="/pricing" onClick={() => setOpen(false)} className="block text-sm text-gray-300 hover:text-white cursor-pointer">
              Pricing
            </Link>
          </div>

          <div className="flex-1" />

          <span className="text-xs text-gray-400">
            © Vypaar AI
          </span>
        </div>
      </NavLoader>
    </>
  );
}

/* SIDE ITEM */
function SideItem({
  icon,
  label,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="
        cursor-pointer
        flex w-full items-center gap-3 rounded-lg
        px-4 py-2.5
        text-gray-300
        hover:bg-white/10 hover:text-white
        hover:scale-[1.02]
        transition-all duration-200
      "
    >
      <span className="text-lg">{icon}</span>
      <span className="text-sm font-medium">{label}</span>
    </button>
  );
}
