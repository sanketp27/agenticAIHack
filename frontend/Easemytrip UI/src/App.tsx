import { Header } from "./components/Header";
import { ChatInterface } from "./components/ChatInterface";
import { OffersSection } from "./components/OffersSection";
import { WhyChooseUs } from "./components/WhyChooseUs";
import { Footer } from "./components/Footer";

export default function App() {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      <ChatInterface />
      <OffersSection />
      <WhyChooseUs />
      <Footer />
    </div>
  );
}
