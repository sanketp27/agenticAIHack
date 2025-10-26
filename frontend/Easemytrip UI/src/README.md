# EaseMyTrip AI Chat Booking System

An AI-powered travel booking interface with the EaseMyTrip design theme. Users can book flights, hotels, trains, and buses through a conversational chat interface.

## Features

- 💬 Conversational AI chat interface
- ✈️ Flight booking with real-time options
- 🏨 Hotel reservations
- 🚂 Train ticket booking
- 🚌 Bus bookings
- 🎨 EaseMyTrip branded design
- 📱 Responsive layout

## Running Locally After Download

### Prerequisites

Make sure you have [Node.js](https://nodejs.org/) installed (version 16 or higher recommended).

### Setup Instructions

1. **Extract the downloaded files** to a folder on your computer

2. **Open Terminal/Command Prompt** and navigate to the project folder:
   ```bash
   cd path/to/your/project-folder
   ```

3. **Install dependencies**:
   ```bash
   npm install
   ```

4. **Start the development server**:
   ```bash
   npm run dev
   ```

5. **Open your browser** and go to:
   ```
   http://localhost:5173
   ```

The application should now be running locally!

## Backend Integration

The chat interface is ready to integrate with your AI agents backend. Here's how:

### 1. Update the API Call

In `/components/ChatInterface.tsx`, replace the `mockBackendCall` function with your actual API endpoint:

```typescript
async function mockBackendCall(userMessage: string): Promise<{ message: string; data?: any; dataType?: string }> {
  // Replace this with your actual backend API call
  const response = await fetch('YOUR_BACKEND_API_URL', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: userMessage,
      // Add any other context your AI needs
    }),
  });

  const data = await response.json();
  return data;
}
```

### 2. Expected Backend Response Format

Your backend should return responses in this format:

```typescript
{
  message: string;        // The AI's text response
  dataType?: string;      // Optional: 'flights' | 'hotels' | 'booking-confirmation'
  data?: any;            // Optional: Structured data for cards
}
```

### 3. Example Response Formats

**Flight Search Response:**
```json
{
  "message": "I found these flights for you:",
  "dataType": "flights",
  "data": [
    {
      "airline": "IndiGo",
      "flightNumber": "6E-2045",
      "from": "Delhi (DEL)",
      "to": "Mumbai (BOM)",
      "departure": "08:30 AM",
      "arrival": "10:45 AM",
      "duration": "2h 15m",
      "price": 4500,
      "date": "Dec 25, 2025"
    }
  ]
}
```

**Hotel Search Response:**
```json
{
  "message": "Here are some hotels:",
  "dataType": "hotels",
  "data": [
    {
      "name": "The Taj Mahal Palace",
      "location": "Mumbai",
      "rating": 4.8,
      "price": 12000,
      "amenities": ["WiFi", "Pool", "Spa"]
    }
  ]
}
```

**Booking Confirmation Response:**
```json
{
  "message": "Booking confirmed!",
  "dataType": "booking-confirmation",
  "data": {
    "bookingId": "EMTABC123",
    "type": "Flight",
    "details": "Delhi to Mumbai",
    "amount": 4500,
    "status": "Confirmed"
  }
}
```

### 4. Handling Button Clicks

When users click "Select Flight" or "Select Hotel" buttons, you can capture that in the respective component files:

- `/components/FlightCard.tsx` - Update the `onClick` handler
- `/components/HotelCard.tsx` - Update the `onClick` handler

Example:
```typescript
onClick={() => {
  // Send selection to your backend
  fetch('YOUR_BACKEND_API_URL/select', {
    method: 'POST',
    body: JSON.stringify({ flightId: flight.flightNumber }),
  });
}}
```

## Project Structure

```
├── App.tsx                          # Main app component
├── components/
│   ├── ChatInterface.tsx            # Main chat interface (INTEGRATE HERE)
│   ├── FlightCard.tsx               # Flight display card
│   ├── HotelCard.tsx                # Hotel display card
│   ├── BookingConfirmation.tsx      # Booking confirmation card
│   ├── Header.tsx                   # Top navigation
│   ├── Footer.tsx                   # Footer
│   ├── OffersSection.tsx            # Offers display
│   └── WhyChooseUs.tsx              # Features section
```

## Customization

- **Colors**: The theme uses EaseMyTrip's blue (`#2196F3`) and orange (`#FF6D00`)
- **Branding**: Update the logo text in `/components/Header.tsx`
- **Chat Height**: Adjust the chat window height in `/components/ChatInterface.tsx` (currently 600px)

## Environment Variables

Create a `.env` file in the root directory for your API endpoint:

```env
VITE_API_URL=https://your-backend-api.com
```

Then use it in your code:
```typescript
const API_URL = import.meta.env.VITE_API_URL;
```

## Troubleshooting

**Port already in use?**
```bash
npm run dev -- --port 3000
```

**Dependencies not installing?**
```bash
npm cache clean --force
npm install
```

## Support

For questions about integration, check the inline comments in `/components/ChatInterface.tsx` where the mock backend call is located.

Happy coding! 🚀
