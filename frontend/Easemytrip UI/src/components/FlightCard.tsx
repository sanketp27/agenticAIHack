import { Plane, Clock } from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";

interface FlightCardProps {
  flight: {
    airline: string;
    flightNumber: string;
    from: string;
    to: string;
    departure: string;
    arrival: string;
    duration: string;
    price: number;
    date: string;
  };
}

export function FlightCard({ flight }: FlightCardProps) {
  return (
    <Card className="bg-white shadow-sm hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div>
            <p className="text-gray-900">{flight.airline}</p>
            <p className="text-sm text-gray-500">{flight.flightNumber}</p>
          </div>
          <div className="text-right">
            <p className="text-[#2196F3]">₹{flight.price.toLocaleString()}</p>
            <p className="text-xs text-gray-500">{flight.date}</p>
          </div>
        </div>

        <div className="flex items-center justify-between mb-3">
          <div>
            <p className="text-gray-900">{flight.departure}</p>
            <p className="text-sm text-gray-600">{flight.from}</p>
          </div>
          
          <div className="flex-1 mx-4 flex flex-col items-center">
            <div className="flex items-center gap-2 text-gray-500">
              <Clock className="w-4 h-4" />
              <span className="text-sm">{flight.duration}</span>
            </div>
            <div className="w-full h-px bg-gray-300 my-1 relative">
              <Plane className="w-4 h-4 text-[#2196F3] absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white" />
            </div>
          </div>
          
          <div className="text-right">
            <p className="text-gray-900">{flight.arrival}</p>
            <p className="text-sm text-gray-600">{flight.to}</p>
          </div>
        </div>

        <Button 
          size="sm" 
          className="w-full bg-[#FF6D00] hover:bg-[#F57C00] text-white"
          onClick={() => {
            // This will be handled by your backend integration
            console.log("Booking flight:", flight);
          }}
        >
          Select Flight
        </Button>
      </CardContent>
    </Card>
  );
}
