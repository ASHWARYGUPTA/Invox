export default function ReverseTriangleGradient() {
  return (
    <div className="h-screen w-full bg-black flex items-center justify-center">
      <div
        className="relative w-[500px] h-[500px] animate-glow"
        style={{
          background: `
            radial-gradient(
              circle at 50% 20%,
              #00BFFF 0%,
              #00AEEF 30%,
              #0077FF 60%,
              #001133 100%
            )
          `,
          clipPath: "polygon(0% 0%, 100% 0%, 50% 100%)",
          filter: "drop-shadow(0 0 25px #00BFFF)",
        }}
      ></div>

      <style>{`
        @keyframes glowPulse {
          0%, 100% {
            filter: drop-shadow(0 0 20px #00BFFF) drop-shadow(0 0 40px #0077FF);
            transform: scale(1);
          }
          50% {
            filter: drop-shadow(0 0 35px #00BFFF) drop-shadow(0 0 60px #0077FF);
            transform: scale(1.05);
          }
        }
        .animate-glow {
          animation: glowPulse 4s ease-in-out infinite;
          transition: all 0.3s ease;
        }
      `}</style>
    </div>
  );
}
