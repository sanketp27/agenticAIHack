import { useState } from "react";
import { Plane, Hotel, Train, Bus, Calendar, MapPin, Users, Search } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Calendar as CalendarComponent } from "./ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover";
import { RadioGroup, RadioGroupItem } from "./ui/radio-group";
import { Label } from "./ui/label";
import { format } from "date-fns";

export function BookingSearch() {
  const [tripType, setTripType] = useState("oneway");
  const [departDate, setDepartDate] = useState<Date>();
  const [returnDate, setReturnDate] = useState<Date>();
  const [travelers, setTravelers] = useState(1);

  return (
    <div className="bg-gradient-to-b from-[#2196F3] to-[#1976D2] -mt-8 pt-8 pb-32">
      <div className="max-w-6xl mx-auto px-4">
        <Tabs defaultValue="flights" className="w-full">
          <TabsList className="bg-white/10 border-b border-white/20 h-auto p-0 mb-6">
            <TabsTrigger 
              value="flights" 
              className="data-[state=active]:bg-white data-[state=active]:text-[#2196F3] text-white gap-2 px-6 py-3 rounded-t"
            >
              <Plane className="w-4 h-4" />
              Flights
            </TabsTrigger>
            <TabsTrigger 
              value="hotels" 
              className="data-[state=active]:bg-white data-[state=active]:text-[#2196F3] text-white gap-2 px-6 py-3 rounded-t"
            >
              <Hotel className="w-4 h-4" />
              Hotels
            </TabsTrigger>
            <TabsTrigger 
              value="trains" 
              className="data-[state=active]:bg-white data-[state=active]:text-[#2196F3] text-white gap-2 px-6 py-3 rounded-t"
            >
              <Train className="w-4 h-4" />
              Trains
            </TabsTrigger>
            <TabsTrigger 
              value="bus" 
              className="data-[state=active]:bg-white data-[state=active]:text-[#2196F3] text-white gap-2 px-6 py-3 rounded-t"
            >
              <Bus className="w-4 h-4" />
              Bus
            </TabsTrigger>
          </TabsList>

          <TabsContent value="flights" className="mt-0">
            <div className="bg-white rounded-lg shadow-xl p-6">
              <RadioGroup value={tripType} onValueChange={setTripType} className="flex gap-6 mb-6">
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="oneway" id="oneway" />
                  <Label htmlFor="oneway">One Way</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="roundtrip" id="roundtrip" />
                  <Label htmlFor="roundtrip">Round Trip</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="multicity" id="multicity" />
                  <Label htmlFor="multicity">Multi City</Label>
                </div>
              </RadioGroup>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                <div className="relative">
                  <Label className="mb-2 block">From</Label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <Input 
                      placeholder="Delhi (DEL)" 
                      className="pl-10"
                    />
                  </div>
                </div>

                <div className="relative">
                  <Label className="mb-2 block">To</Label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <Input 
                      placeholder="Mumbai (BOM)" 
                      className="pl-10"
                    />
                  </div>
                </div>

                <div className="relative">
                  <Label className="mb-2 block">Departure</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="outline" className="w-full justify-start text-left">
                        <Calendar className="mr-2 h-4 w-4" />
                        {departDate ? format(departDate, "PPP") : <span>Pick a date</span>}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <CalendarComponent
                        mode="single"
                        selected={departDate}
                        onSelect={setDepartDate}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>

                {tripType === "roundtrip" && (
                  <div className="relative">
                    <Label className="mb-2 block">Return</Label>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button variant="outline" className="w-full justify-start text-left">
                          <Calendar className="mr-2 h-4 w-4" />
                          {returnDate ? format(returnDate, "PPP") : <span>Pick a date</span>}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0">
                        <CalendarComponent
                          mode="single"
                          selected={returnDate}
                          onSelect={setReturnDate}
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                  </div>
                )}

                <div className="relative">
                  <Label className="mb-2 block">Travelers</Label>
                  <div className="relative">
                    <Users className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <Input 
                      type="number" 
                      value={travelers}
                      onChange={(e) => setTravelers(parseInt(e.target.value) || 1)}
                      className="pl-10"
                      min="1"
                    />
                  </div>
                </div>
              </div>

              <Button className="w-full bg-[#FF6D00] hover:bg-[#F57C00] text-white h-12">
                <Search className="mr-2 h-5 w-5" />
                Search Flights
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="hotels" className="mt-0">
            <div className="bg-white rounded-lg shadow-xl p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div className="relative">
                  <Label className="mb-2 block">City/Hotel/Area</Label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <Input 
                      placeholder="Enter city or hotel name" 
                      className="pl-10"
                    />
                  </div>
                </div>

                <div className="relative">
                  <Label className="mb-2 block">Check-in</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="outline" className="w-full justify-start text-left">
                        <Calendar className="mr-2 h-4 w-4" />
                        {departDate ? format(departDate, "PPP") : <span>Pick a date</span>}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <CalendarComponent
                        mode="single"
                        selected={departDate}
                        onSelect={setDepartDate}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>

                <div className="relative">
                  <Label className="mb-2 block">Check-out</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="outline" className="w-full justify-start text-left">
                        <Calendar className="mr-2 h-4 w-4" />
                        {returnDate ? format(returnDate, "PPP") : <span>Pick a date</span>}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <CalendarComponent
                        mode="single"
                        selected={returnDate}
                        onSelect={setReturnDate}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>
              </div>

              <Button className="w-full bg-[#FF6D00] hover:bg-[#F57C00] text-white h-12">
                <Search className="mr-2 h-5 w-5" />
                Search Hotels
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="trains" className="mt-0">
            <div className="bg-white rounded-lg shadow-xl p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div className="relative">
                  <Label className="mb-2 block">From</Label>
                  <Input placeholder="Enter source station" />
                </div>

                <div className="relative">
                  <Label className="mb-2 block">To</Label>
                  <Input placeholder="Enter destination station" />
                </div>

                <div className="relative">
                  <Label className="mb-2 block">Journey Date</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="outline" className="w-full justify-start text-left">
                        <Calendar className="mr-2 h-4 w-4" />
                        {departDate ? format(departDate, "PPP") : <span>Pick a date</span>}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <CalendarComponent
                        mode="single"
                        selected={departDate}
                        onSelect={setDepartDate}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>
              </div>

              <Button className="w-full bg-[#FF6D00] hover:bg-[#F57C00] text-white h-12">
                <Search className="mr-2 h-5 w-5" />
                Search Trains
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="bus" className="mt-0">
            <div className="bg-white rounded-lg shadow-xl p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div className="relative">
                  <Label className="mb-2 block">From</Label>
                  <Input placeholder="Enter source city" />
                </div>

                <div className="relative">
                  <Label className="mb-2 block">To</Label>
                  <Input placeholder="Enter destination city" />
                </div>

                <div className="relative">
                  <Label className="mb-2 block">Journey Date</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="outline" className="w-full justify-start text-left">
                        <Calendar className="mr-2 h-4 w-4" />
                        {departDate ? format(departDate, "PPP") : <span>Pick a date</span>}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <CalendarComponent
                        mode="single"
                        selected={departDate}
                        onSelect={setDepartDate}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>
              </div>

              <Button className="w-full bg-[#FF6D00] hover:bg-[#F57C00] text-white h-12">
                <Search className="mr-2 h-5 w-5" />
                Search Buses
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
