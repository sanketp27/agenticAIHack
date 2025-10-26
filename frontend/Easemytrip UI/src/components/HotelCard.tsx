import { Star, MapPin, Wifi, Coffee } from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";

interface HotelCardProps {
  hotel: {
    name: string;
    location: string;
    rating: number;
    price: number;
    amenities: string[];
  };
}

export function HotelCard({ hotel }: HotelCardProps) {
  const getAmenityIcon = (amenity: string) => {
    if (amenity.toLowerCase().includes('wifi')) return <Wifi className="w-3 h-3" />;
    return <Coffee className="w-3 h-3" />;
  };

  return (
    <Card className="bg-white shadow-sm hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h4 className="text-gray-900 mb-1">{hotel.name}</h4>
            <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
              <MapPin className="w-4 h-4" />
              <span>{hotel.location}</span>
            </div>
            <div className="flex items-center gap-1">
              <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
              <span className="text-sm">{hotel.rating}</span>
            </div>
          </div>
          
          <div className="text-right">
            <p className="text-[#2196F3]">₹{hotel.price.toLocaleString()}</p>
            <p className="text-xs text-gray-500">per night</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-1 mb-3">
          {hotel.amenities.slice(0, 4).map((amenity, index) => (
            <Badge key={index} variant="secondary" className="text-xs">
              {amenity}
            </Badge>
          ))}
        </div>

        <Button 
          size="sm" 
          className="w-full bg-[#FF6D00] hover:bg-[#F57C00] text-white"
          onClick={() => {
            // This will be handled by your backend integration
            console.log("Booking hotel:", hotel);
          }}
        >
          Select Hotel
        </Button>
      </CardContent>
    </Card>
  );
}
