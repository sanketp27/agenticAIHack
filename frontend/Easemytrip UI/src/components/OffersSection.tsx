import { Badge } from "./ui/badge";
import { Card, CardContent } from "./ui/card";
import { ImageWithFallback } from "./figma/ImageWithFallback";

const offers = [
  {
    id: 1,
    title: "Flat 15% Off on Domestic Flights",
    code: "EMTDC",
    description: "Get flat 15% discount on domestic flight bookings",
    color: "bg-gradient-to-r from-blue-500 to-blue-600"
  },
  {
    id: 2,
    title: "Save Up to 20% on Hotels",
    code: "EMTHOTEL",
    description: "Book hotels and save up to 20% on your stay",
    color: "bg-gradient-to-r from-purple-500 to-purple-600"
  },
  {
    id: 3,
    title: "Train Booking Offers",
    code: "EMTTRAIN",
    description: "Flat ₹150 off on train ticket bookings",
    color: "bg-gradient-to-r from-green-500 to-green-600"
  },
  {
    id: 4,
    title: "Bus Booking Special",
    code: "EMTBUS",
    description: "Get 10% cashback on bus bookings",
    color: "bg-gradient-to-r from-orange-500 to-orange-600"
  }
];

export function OffersSection() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-12 -mt-20">
      <div className="mb-8">
        <h2 className="mb-2">Exclusive Offers For You</h2>
        <p className="text-gray-600">Save big on your next trip with our special deals</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {offers.map((offer) => (
          <Card key={offer.id} className="overflow-hidden border-0 shadow-lg hover:shadow-xl transition-shadow">
            <div className={`${offer.color} h-32 p-4 text-white flex flex-col justify-between`}>
              <Badge className="bg-white/20 text-white w-fit backdrop-blur-sm">
                Code: {offer.code}
              </Badge>
              <h3 className="text-white">{offer.title}</h3>
            </div>
            <CardContent className="p-4">
              <p className="text-gray-600">{offer.description}</p>
              <button className="mt-3 text-[#2196F3] hover:underline">
                View Details →
              </button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
