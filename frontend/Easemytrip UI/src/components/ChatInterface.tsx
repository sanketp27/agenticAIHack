import { useState, useRef, useEffect } from "react";
import { Send, Bot, User as UserIcon, Loader2 } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { ScrollArea } from "./ui/scroll-area";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { FlightCard } from "./FlightCard";
import { HotelCard } from "./HotelCard";
import { BookingConfirmation } from "./BookingConfirmation";

export interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  data?: any; // For structured data like flight options, hotel details, etc.
  dataType?: 'flights' | 'hotels' | 'booking-confirmation';
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ai',
      content: "Hello! 👋 I'm your EaseMyTrip AI assistant. I can help you book flights, hotels, trains, buses, and plan your perfect trip. How can I assist you today?",
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    // TODO: Replace this with your actual backend API call
    // This is a mock response for demonstration
    try {
      const response = await mockBackendCall(inputValue);
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: response.message,
        timestamp: new Date(),
        data: response.data,
        dataType: response.dataType
      };

      setTimeout(() => {
        setMessages(prev => [...prev, aiMessage]);
        setIsLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: "I'm sorry, I encountered an error connecting to the backend. Please make sure the backend API is running on http://localhost:5001",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="bg-gradient-to-b from-[#2196F3] to-[#1976D2] -mt-8 pt-8 pb-12">
      <div className="max-w-5xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-2xl overflow-hidden" style={{ height: '600px' }}>
          {/* Chat Header */}
          <div className="bg-[#2196F3] text-white p-4 flex items-center gap-3">
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
              <Bot className="w-6 h-6 text-[#2196F3]" />
            </div>
            <div>
              <h3 className="text-white">EaseMyTrip AI Assistant</h3>
              <p className="text-white/80 text-sm">Online • Ready to help</p>
            </div>
          </div>

          {/* Messages Area */}
          <ScrollArea className="h-[440px] p-4">
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                >
                  <Avatar className="w-8 h-8 flex-shrink-0">
                    <AvatarFallback className={message.type === 'user' ? 'bg-gray-200' : 'bg-blue-100'}>
                      {message.type === 'user' ? (
                        <UserIcon className="w-5 h-5 text-gray-600" />
                      ) : (
                        <Bot className="w-5 h-5 text-[#2196F3]" />
                      )}
                    </AvatarFallback>
                  </Avatar>

                  <div className={`flex-1 ${message.type === 'user' ? 'flex justify-end' : ''}`}>
                    <div
                      className={`rounded-lg p-3 max-w-[80%] ${
                        message.type === 'user'
                          ? 'bg-[#2196F3] text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{message.content}</p>
                      
                      {/* Render structured data */}
                      {message.dataType === 'flights' && message.data && (
                        <div className="mt-3 space-y-2">
                          {message.data.map((flight: any, index: number) => (
                            <FlightCard key={index} flight={flight} />
                          ))}
                        </div>
                      )}
                      
                      {message.dataType === 'hotels' && message.data && (
                        <div className="mt-3 space-y-2">
                          {message.data.map((hotel: any, index: number) => (
                            <HotelCard key={index} hotel={hotel} />
                          ))}
                        </div>
                      )}

                      {message.dataType === 'booking-confirmation' && message.data && (
                        <div className="mt-3">
                          <BookingConfirmation booking={message.data} />
                        </div>
                      )}
                    </div>
                    <p className={`text-xs text-gray-500 mt-1 ${message.type === 'user' ? 'text-right' : ''}`}>
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex gap-3">
                  <Avatar className="w-8 h-8">
                    <AvatarFallback className="bg-blue-100">
                      <Bot className="w-5 h-5 text-[#2196F3]" />
                    </AvatarFallback>
                  </Avatar>
                  <div className="bg-gray-100 rounded-lg p-3">
                    <Loader2 className="w-5 h-5 animate-spin text-[#2196F3]" />
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          {/* Input Area */}
          <div className="border-t p-4">
            <div className="flex gap-2">
              <Input
                placeholder="Type your travel request... (e.g., 'Book a flight from Delhi to Mumbai on Dec 25')"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isLoading}
                className="flex-1"
              />
              <Button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isLoading}
                className="bg-[#FF6D00] hover:bg-[#F57C00] text-white"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              💡 Try: "I want to book a flight from Delhi to Mumbai" or "Find hotels in Goa"
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';

// Backend API call - Connects to Flask backend
async function mockBackendCall(userMessage: string): Promise<{ message: string; data?: any; dataType?: string }> {
  try {
    // Call the actual backend API
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: userMessage })
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API call failed:', error);
    // Fallback to mock response if API is unavailable
    return getMockResponse(userMessage);
  }
}

function getMockResponse(userMessage: string): { message: string; data?: any; dataType?: string } {
  const lowerMessage = userMessage.toLowerCase();
  
  // Simulate API delay
  // await new Promise(resolve => setTimeout(resolve, 500));

  // Example: Flight search
  if (lowerMessage.includes('flight') || lowerMessage.includes('fly')) {
    return {
      message: "I found these flights for you. Which one would you like to book?",
      dataType: 'flights',
      data: [
        {
          airline: "IndiGo",
          flightNumber: "6E-2045",
          from: "Delhi (DEL)",
          to: "Mumbai (BOM)",
          departure: "08:30 AM",
          arrival: "10:45 AM",
          duration: "2h 15m",
          price: 4500,
          date: "Dec 25, 2025"
        },
        {
          airline: "Air India",
          flightNumber: "AI-860",
          from: "Delhi (DEL)",
          to: "Mumbai (BOM)",
          departure: "02:15 PM",
          arrival: "04:30 PM",
          duration: "2h 15m",
          price: 5200,
          date: "Dec 25, 2025"
        }
      ]
    };
  }

  // Example: Hotel search
  if (lowerMessage.includes('hotel')) {
    return {
      message: "Here are some great hotels I found for you:",
      dataType: 'hotels',
      data: [
        {
          name: "The Taj Mahal Palace",
          location: "Mumbai",
          rating: 4.8,
          price: 12000,
          amenities: ["WiFi", "Pool", "Spa", "Restaurant"]
        },
        {
          name: "ITC Grand Central",
          location: "Mumbai",
          rating: 4.6,
          price: 9500,
          amenities: ["WiFi", "Gym", "Restaurant", "Bar"]
        }
      ]
    };
  }

  // Example: Booking confirmation
  if (lowerMessage.includes('book') && (lowerMessage.includes('confirm') || lowerMessage.includes('yes'))) {
    return {
      message: "Great! Your booking has been confirmed! 🎉",
      dataType: 'booking-confirmation',
      data: {
        bookingId: "EMT" + Math.random().toString(36).substr(2, 9).toUpperCase(),
        type: "Flight",
        details: "Delhi to Mumbai on Dec 25, 2025",
        amount: 4500,
        status: "Confirmed"
      }
    };
  }

  // Default response
  return {
    message: "I can help you with:\n\n✈️ Flight bookings\n🏨 Hotel reservations\n🚂 Train tickets\n🚌 Bus bookings\n\nPlease tell me what you'd like to do!"
  };
}
