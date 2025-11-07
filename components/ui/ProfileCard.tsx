
"use client";
import React from "react";
import { motion } from "framer-motion";

interface ProfileCardProps {
  name: string;
  title: string;
  avatarUrl: string;
  location?: string;
  contactText?: string;
  onContactClick?: () => void;
  showGlow?: boolean;
}

const ProfileCard: React.FC<ProfileCardProps> = ({
  name,
  title,
  avatarUrl,
  location,
  contactText = "Contact",
  onContactClick,
  showGlow = true,
}) => {
  return (
    <motion.div
      whileHover={{ scale: 1.05, rotateX: 5, rotateY: -5 }}
      transition={{ type: "spring", stiffness: 200, damping: 15 }}
      className="relative bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white 
                 rounded-2xl p-6 w-80 h-[380px] shadow-xl overflow-hidden border border-gray-700"
    >
      {/* Hover glow */}
      {showGlow && (
        <div className="absolute inset-0 bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500 opacity-30 blur-3xl"></div>
      )}

      {/* Card Content */}
      <div className="relative flex flex-col items-center z-10">
        <img
          src={avatarUrl}
          alt={name}
          className="w-24 h-24 rounded-full object-cover border-4 border-gray-700 shadow-md mb-4"
        />
        <h2 className="text-xl font-semibold">{name}</h2>
        <p className="text-gray-400">{title}</p>
        {location && <p className="text-sm text-gray-500 mt-1">{location}</p>}

        <button
          onClick={onContactClick}
          className="mt-6 px-4 py-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-purple-500 hover:to-pink-500 transition-all duration-300 shadow-md"
        >
          {contactText}
        </button>
      </div>
    </motion.div>
  );
};

export default ProfileCard;