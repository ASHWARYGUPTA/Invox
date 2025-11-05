export default function Navbar() {
  return (
    <div>
      <nav className="fixed top-6 left-1/2 -translate-x-1/2 w-1/2 min-w-[300px] z-50">
        <div className="flex justify-between bg-background/10 backdrop-blur-xl border border-white/20 rounded-full shadow-lg shadow-black/5 px-6 py-3">
          <div className=" w-[60px]">
            <div className="text-3xl font-bold">Invox</div>
          </div>
          <div className="w-2/3">
            <ul className="flex items-center justify-around">
              <li>
                <a
                  href="#"
                  className="flex items-center justify-center w-10 h-10 rounded-full transition-all duration-300 hover:bg-primary/10 hover:scale-110 text-foreground/70 hover:text-primary"
                  aria-label="Home"
                >
                  <img className="w-5 h-5" />
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="flex items-center justify-center w-10 h-10 rounded-full transition-all duration-300 hover:bg-primary/10 hover:scale-110 text-foreground/70 hover:text-primary"
                  aria-label="Explore"
                >
                  <img className="w-5 h-5" />
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="flex items-center justify-center w-10 h-10 rounded-full transition-all duration-300 hover:bg-primary/10 hover:scale-110 text-foreground/70 hover:text-primary"
                  aria-label="Profile"
                >
                  <img className="w-5 h-5" />
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="flex items-center justify-center w-10 h-10 rounded-full transition-all duration-300 hover:bg-primary/10 hover:scale-110 text-foreground/70 hover:text-primary"
                  aria-label="Settings"
                >
                  <img className="w-5 h-5" />
                </a>
              </li>
            </ul>
          </div>
        </div>
      </nav>
    </div>
  );
}
