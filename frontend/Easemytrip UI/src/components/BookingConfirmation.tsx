import { CheckCircle2, Download, Share2 } from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";

interface BookingConfirmationProps {
  booking: {
    bookingId: string;
    type: string;
    details: string;
    amount: number;
    status: string;
  };
}

export function BookingConfirmation({ booking }: BookingConfirmationProps) {
  return (
    <Card className="bg-green-50 border-green-200 shadow-sm">
      <CardContent className="p-4">
        <div className="flex items-start gap-3 mb-3">
          <CheckCircle2 className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
          <div className="flex-1">
            <h4 className="text-green-900 mb-1">Booking Confirmed!</h4>
            <p className="text-sm text-green-700">Booking ID: <span className="font-mono">{booking.bookingId}</span></p>
          </div>
        </div>

        <div className="bg-white rounded p-3 mb-3">
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>
              <p className="text-gray-500">Type</p>
              <p className="text-gray-900">{booking.type}</p>
            </div>
            <div>
              <p className="text-gray-500">Amount Paid</p>
              <p className="text-gray-900">₹{booking.amount.toLocaleString()}</p>
            </div>
            <div className="col-span-2">
              <p className="text-gray-500">Details</p>
              <p className="text-gray-900">{booking.details}</p>
            </div>
          </div>
        </div>

        <div className="flex gap-2">
          <Button size="sm" variant="outline" className="flex-1">
            <Download className="w-4 h-4 mr-2" />
            Download
          </Button>
          <Button size="sm" variant="outline" className="flex-1">
            <Share2 className="w-4 h-4 mr-2" />
            Share
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
