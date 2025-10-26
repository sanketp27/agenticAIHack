import { Phone, User, Menu } from "lucide-react";
import { Button } from "./ui/button";

export function Header() {
  return (
    <header className="bg-[#2196F3] text-white">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between py-3">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-2">
              <div className="w-40 h-10 bg-white rounded flex items-center justify-center px-3">
                <span className="text-[#2196F3]" style={{ fontWeight: 700, fontSize: "24px" }}>EaseMyTrip</span>
              </div>
            </div>
            <nav className="hidden md:flex items-center gap-6">
              <a href="#" className="hover:text-white/90">Flights</a>
              <a href="#" className="hover:text-white/90">Hotels</a>
              <a href="#" className="hover:text-white/90">Trains</a>
              <a href="#" className="hover:text-white/90">Bus</a>
              <a href="#" className="hover:text-white/90">Holidays</a>
              <a href="#" className="hover:text-white/90">Cabs</a>
            </nav>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center gap-2">
              <Phone className="w-4 h-4" />
              <span>+91-9555-555-555</span>
            </div>
            <Button variant="ghost" className="text-white hover:bg-white/10">
              <User className="w-4 h-4 mr-2" />
              Login or Signup
            </Button>
            <Button variant="ghost" className="md:hidden text-white hover:bg-white/10">
              <Menu className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
