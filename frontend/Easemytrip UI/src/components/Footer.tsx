import { Facebook, Twitter, Instagram, Linkedin, Youtube } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
          <div>
            <h3 className="text-white mb-4">Company</h3>
            <ul className="space-y-2">
              <li><a href="#" className="hover:text-white">About Us</a></li>
              <li><a href="#" className="hover:text-white">Careers</a></li>
              <li><a href="#" className="hover:text-white">Our Team</a></li>
              <li><a href="#" className="hover:text-white">Investor Relations</a></li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-white mb-4">Support</h3>
            <ul className="space-y-2">
              <li><a href="#" className="hover:text-white">Help Center</a></li>
              <li><a href="#" className="hover:text-white">Contact Us</a></li>
              <li><a href="#" className="hover:text-white">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-white">Terms & Conditions</a></li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-white mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li><a href="#" className="hover:text-white">Flight Status</a></li>
              <li><a href="#" className="hover:text-white">PNR Status</a></li>
              <li><a href="#" className="hover:text-white">Offers</a></li>
              <li><a href="#" className="hover:text-white">Travel Blog</a></li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-white mb-4">Follow Us</h3>
            <div className="flex gap-4">
              <a href="#" className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-gray-700">
                <Facebook className="w-5 h-5" />
              </a>
              <a href="#" className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-gray-700">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="#" className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-gray-700">
                <Instagram className="w-5 h-5" />
              </a>
              <a href="#" className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-gray-700">
                <Linkedin className="w-5 h-5" />
              </a>
              <a href="#" className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-gray-700">
                <Youtube className="w-5 h-5" />
              </a>
            </div>
            <div className="mt-6">
              <p className="mb-2">Download Our App</p>
              <div className="flex gap-2">
                <div className="bg-gray-800 px-3 py-2 rounded hover:bg-gray-700 cursor-pointer">
                  <p className="text-xs">Google Play</p>
                </div>
                <div className="bg-gray-800 px-3 py-2 rounded hover:bg-gray-700 cursor-pointer">
                  <p className="text-xs">App Store</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="border-t border-gray-800 pt-8 text-center">
          <p>&copy; 2025 EaseMyTrip. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
