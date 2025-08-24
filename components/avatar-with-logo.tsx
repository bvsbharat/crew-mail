"use client";

import { useState } from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import type { EmailSender } from "@/types/email";
import SenderProfile from "@/components/sender-profile";

// Generate vibrant colors based on user name/email
const generateAvatarColors = (name: string, email: string) => {
  const text = (name + email).toLowerCase();
  let hash = 0;
  for (let i = 0; i < text.length; i++) {
    hash = text.charCodeAt(i) + ((hash << 5) - hash);
  }

  const colorPairs = [
    ["from-pink-500", "to-rose-500"],
    ["from-purple-500", "to-indigo-500"],
    ["from-blue-500", "to-cyan-500"],
    ["from-green-500", "to-emerald-500"],
    ["from-yellow-500", "to-orange-500"],
    ["from-red-500", "to-pink-500"],
    ["from-indigo-500", "to-purple-500"],
    ["from-cyan-500", "to-blue-500"],
    ["from-emerald-500", "to-teal-500"],
    ["from-orange-500", "to-red-500"],
    ["from-violet-500", "to-purple-500"],
    ["from-teal-500", "to-cyan-500"],
  ];

  const index = Math.abs(hash) % colorPairs.length;
  return colorPairs[index];
};

interface AvatarWithLogoProps {
  sender: EmailSender;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function AvatarWithLogo({
  sender,
  size = "md",
  className = "",
}: AvatarWithLogoProps) {
  const [showProfile, setShowProfile] = useState(false);

  // Generate dynamic colors for this user
  const [fromColor, toColor] = generateAvatarColors(sender.name, sender.email);

  // Determine avatar size
  const avatarSizeClasses = {
    sm: "h-8 w-8",
    md: "h-10 w-10",
    lg: "h-12 w-12",
  };

  // Determine logo size
  const logoSizeClasses = {
    sm: "h-3.5 w-3.5",
    md: "h-4.5 w-4.5",
    lg: "h-5.5 w-5.5",
  };

  return (
    <>
      <div
        className={`relative ${className} cursor-pointer hover:scale-105 hover:shadow-lg transition-all duration-200`}
        onClick={(e) => {
          e.stopPropagation();
          setShowProfile(true);
        }}
      >
        <Avatar
          className={`${avatarSizeClasses[size]} ring-2 ring-white/20 shadow-md`}
        >
          <AvatarFallback className="text-white font-semibold bg-gradient-to-br from-blue-500 to-purple-600">
            {(sender.name || sender.email).charAt(0).toUpperCase()}
          </AvatarFallback>
        </Avatar>

        {sender.organization && (
          <div className="absolute -bottom-1 -right-1 rounded-full border-2 border-background shadow-lg">
            <div
              className={`${logoSizeClasses[size]} rounded-full bg-gradient-to-br from-slate-100 to-slate-200 overflow-hidden ring-2 ring-white/50 flex items-center justify-center shadow-inner`}
            >
              {sender.organization.logo ? (
                <img
                  src={sender.organization.logo}
                  alt={sender.organization.name}
                  className="h-full w-full object-cover"
                />
              ) : (
                <div className="h-full w-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-xs font-bold text-white">
                  {sender.organization.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")
                    .toUpperCase()
                    .substring(0, 2)}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <SenderProfile
        sender={sender}
        open={showProfile}
        onClose={() => setShowProfile(false)}
      />
    </>
  );
}
